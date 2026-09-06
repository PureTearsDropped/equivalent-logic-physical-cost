"""Whole-DAG timing-driven optimizer over the full sky130_fd_sc_hd cell vocabulary.
Netlist = instances of Liberty cells; timing = NLDM lookup (arrival+slew) generalized to N-input, unate/non-unate, multi-output cells."""
import json, copy, re, glob, os, subprocess, sys
import numpy as np
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from paths import CELLS_DIR, LIB_PATH, run_sta as _run_sta

# ---------------- Liberty cells ----------------
CELLS={}
for f in sorted(glob.glob(str(CELLS_DIR/'*_[124].json'))):
    name=os.path.basename(f)[:-5]; d=json.load(open(f))
    base,size=name.rsplit('_',1)
    c={'name':name,'base':base,'size':int(size),'area':d['area'],'in':{},'out':{}}
    for k,v in d.items():
        if not k.startswith('pin,'): continue
        p=k[4:]
        if v['direction']=='input': c['in'][p]=v['capacitance']
        else:
            tl=v['timing']; tl=[tl] if isinstance(tl,dict) else tl
            arcs=[]
            for t in tl:
                a={'pin':t['related_pin'],'sense':t.get('timing_sense')}
                for key in ('cell_rise','cell_fall','rise_transition','fall_transition'):
                    tb=[x for kk,x in t.items() if kk.startswith(key)][0]
                    a[key]=(np.array(tb['index_1'],float),np.array(tb['index_2'],float),np.array(tb['values'],float).reshape(len(tb['index_1']),-1))
                arcs.append(a)
            c['out'][p]={'func':v['function'],'arcs':arcs}
    CELLS[name]=c

def interp2(tab,s,cl):
    i1,i2,v=tab; s=min(max(s,i1[0]),i1[-1]); cl=min(max(cl,i2[0]),i2[-1])
    col=[np.interp(s,i1,v[:,j]) for j in range(len(i2))]
    return float(np.interp(cl,i2,col))

# ---------------- truth tables (256 rows) ----------------
ROWS=256; MASK=(1<<ROWS)-1
class TT:
    __slots__=('v',)
    def __init__(s,v): s.v=v&MASK
    def __and__(s,o): return TT(s.v&o.v)
    def __or__(s,o): return TT(s.v|o.v)
    def __xor__(s,o): return TT(s.v^o.v)
    def __invert__(s): return TT(MASK^s.v)
def cell_func(cell,outpin,pinvals):
    expr=CELLS[cell]['out'][outpin]['func'].replace('!','~')
    expr=re.sub(r'\b([A-Z][A-Z0-9_]*)\b',r'P["\1"]',expr)
    return eval(expr,{'P':pinvals})
def var_tt(bit):
    v=0
    for r in range(ROWS):
        if (r>>bit)&1: v|=1<<r
    return TT(v)
PRIM=[var_tt(i) for i in range(8)]   # a0..a3, b0..b3

# ---------------- netlist ----------------
class Net:
    def __init__(s):
        s.insts=[]          # {'cell':name,'pins':{inpin:net},'outs':{outpin:net}}
        s.nnets=8           # nets 0..7 primary inputs
        s.outputs=[None]*8  # net ids for p0..p7
    def add(s,cell,pins):
        c=CELLS[cell]; assert set(pins)==set(c['in']),(cell,pins)
        outs={}
        for op in c['out']: outs[op]=s.nnets; s.nnets+=1
        s.insts.append({'cell':cell,'pins':dict(pins),'outs':outs})
        return outs
    def renumber(s):
        """compact net ids; returns self"""
        return s

def eval_tt(net):
    vals=[None]*net.nnets
    for i in range(8): vals[i]=PRIM[i]
    pending=list(range(len(net.insts))); guard=0
    while pending:
        rest=[]
        for ii in pending:
            inst=net.insts[ii]
            if all(vals[n] is not None for n in inst['pins'].values()):
                pv={p:vals[n] for p,n in inst['pins'].items()}
                for op,n in inst['outs'].items(): vals[n]=cell_func(inst['cell'],op,pv)
            else: rest.append(ii)
        assert len(rest)<len(pending),"cycle / undriven net"
        pending=rest
    return vals
def verify(net):
    vals=eval_tt(net)
    for r in range(ROWS):
        a,b=r&15,r>>4
        got=sum(((vals[net.outputs[k]].v>>r)&1)<<k for k in range(8))
        if got!=a*b: raise AssertionError(f"a={a} b={b} got {got}")
    return True

def topo(net):
    known=set(range(8)); order=[]; pending=list(range(len(net.insts)))
    while pending:
        rest=[]
        for ii in pending:
            inst=net.insts[ii]
            if all(n in known for n in inst['pins'].values()):
                order.append(ii); known.update(inst['outs'].values())
            else: rest.append(ii)
        assert len(rest)<len(pending); pending=rest
    return order

def timing_detail(net,out_load=0.010,in_slew=0.05):
    loads=[0.0]*net.nnets; sinks=[[] for _ in range(net.nnets)]
    for ii,inst in enumerate(net.insts):
        c=CELLS[inst['cell']]
        for p,n in inst['pins'].items(): loads[n]+=c['in'][p]; sinks[n].append((ii,p))
    for n in net.outputs:
        if n is not None: loads[n]+=out_load
    rise=[0.0]*net.nnets; fall=[0.0]*net.nnets; sr=[in_slew]*net.nnets; sf=[in_slew]*net.nnets
    for ii in topo(net):
        inst=net.insts[ii]; c=CELLS[inst['cell']]
        for op,on in inst['outs'].items():
            br=(-1.0,0.0); bf=(-1.0,0.0); L=loads[on]
            for a in c['out'][op]['arcs']:
                src=inst['pins'][a['pin']]; sense=a['sense']
                if sense in ('positive_unate','non_unate'):
                    t=rise[src]+interp2(a['cell_rise'],sr[src],L)
                    if t>br[0]: br=(t,interp2(a['rise_transition'],sr[src],L))
                    t=fall[src]+interp2(a['cell_fall'],sf[src],L)
                    if t>bf[0]: bf=(t,interp2(a['fall_transition'],sf[src],L))
                if sense in ('negative_unate','non_unate'):
                    t=fall[src]+interp2(a['cell_rise'],sf[src],L)
                    if t>br[0]: br=(t,interp2(a['rise_transition'],sf[src],L))
                    t=rise[src]+interp2(a['cell_fall'],sr[src],L)
                    if t>bf[0]: bf=(t,interp2(a['fall_transition'],sr[src],L))
            rise[on],sr[on]=br; fall[on],sf[on]=bf
    area=sum(CELLS[i['cell']]['area'] for i in net.insts)
    arr=[max(rise[o],fall[o]) for o in net.outputs if o is not None]
    return dict(delay=max(arr) if arr else 0.0,area=area,sinks=sinks,loads=loads,arrival=[max(r,f) for r,f in zip(rise,fall)])

def timing(net,out_load=0.010,in_slew=0.05):
    d=timing_detail(net,out_load,in_slew); return d['delay'],d['area'],d['sinks'],d['loads']

# ---------------- building blocks (each returns (sum_net, carry_net)) ----------------
def sz(base,size): return f"{base}_{size}"
def PP_and2(net,a,b,s=1): return net.add(sz('and2',s),{'A':a,'B':b})['X']
def PP_nand_inv(net,a,b,s=1):
    t=net.add(sz('nand2',s),{'A':a,'B':b})['Y']; return net.add(sz('inv',s),{'A':t})['Y']
PP_MENU={'and2':PP_and2,'nand+inv':PP_nand_inv}

def HA_nand5(net,a,b,s=1):
    n1=net.add(sz('nand2',s),{'A':a,'B':b})['Y']; n2=net.add(sz('nand2',s),{'A':a,'B':n1})['Y']; n3=net.add(sz('nand2',s),{'A':b,'B':n1})['Y']
    return net.add(sz('nand2',s),{'A':n2,'B':n3})['Y'], net.add(sz('inv',s),{'A':n1})['Y']
def HA_xor_and(net,a,b,s=1): return net.add(sz('xor2',s),{'A':a,'B':b})['X'], net.add(sz('and2',s),{'A':a,'B':b})['X']
def HA_cell(net,a,b,s=1): o=net.add(sz('ha',s),{'A':a,'B':b}); return o['SUM'],o['COUT']
HA_MENU={'nand5':HA_nand5,'xor+and':HA_xor_and,'ha':HA_cell}

def FA_nand9(net,a,b,c,s=1):
    N=lambda x,y: net.add(sz('nand2',s),{'A':x,'B':y})['Y']
    g1=N(a,b); g2=N(a,g1); g3=N(b,g1); x=N(g2,g3); g5=N(x,c); g6=N(x,g5); g7=N(c,g5)
    return N(g6,g7), N(g1,g5)
def FA_xor3_maj3(net,a,b,c,s=1): return net.add(sz('xor3',s),{'A':a,'B':b,'C':c})['X'], net.add(sz('maj3',s),{'A':a,'B':b,'C':c})['X']
def FA_cell(net,a,b,c,s=1): o=net.add(sz('fa',s),{'A':a,'B':b,'CIN':c}); return o['SUM'],o['COUT']
def FA_xor2_maj3(net,a,b,c,s=1):
    x=net.add(sz('xor2',s),{'A':a,'B':b})['X']; return net.add(sz('xor2',s),{'A':x,'B':c})['X'], net.add(sz('maj3',s),{'A':a,'B':b,'C':c})['X']
def FA_xor2_a21o(net,a,b,c,s=1):
    x=net.add(sz('xor2',s),{'A':a,'B':b})['X']; ab=net.add(sz('and2',s),{'A':a,'B':b})['X']
    return net.add(sz('xor2',s),{'A':x,'B':c})['X'], net.add(sz('a21o',s),{'A1':x,'A2':c,'B1':ab})['X']
FA_MENU={'nand9':FA_nand9,'xor3+maj3':FA_xor3_maj3,'fa':FA_cell,'xor2x2+maj3':FA_xor2_maj3,'xor2x2+a21o':FA_xor2_a21o}

# position ids: pp0..15, ha0..3, fa0..7 (same array topology as pa4x4.build_array4)
def build(choice):
    """choice: dict pos -> (variant, size)"""
    net=Net(); A=list(range(4)); B=list(range(4,8))
    def ch(pos,menu): v,s=choice.get(pos,(list(menu)[0],1)); return menu[v],s
    pp={}
    for i in range(4):
        for j in range(4):
            f,s=ch(f'pp{i*4+j}',PP_MENU); pp[i,j]=f(net,A[i],B[j],s)
    def HA(k,a,b): f,s=ch(f'ha{k}',HA_MENU); return f(net,a,b,s)
    def FA(k,a,b,c): f,s=ch(f'fa{k}',FA_MENU); return f(net,a,b,c,s)
    P=[None]*8; P[0]=pp[0,0]
    P[1],x1=HA(0,pp[1,0],pp[0,1]); x2,x3=FA(0,pp[1,1],pp[0,2],x1); x4,x5=FA(1,pp[1,2],pp[0,3],x3); x6,x7=HA(1,pp[1,3],x5)
    P[2],x15=HA(2,x2,pp[2,0]); x14,x16=FA(2,x4,pp[2,1],x15); x13,x17=FA(3,x6,pp[2,2],x16); x9,x8=FA(4,x7,pp[2,3],x17)
    P[3],x12=HA(3,x14,pp[3,0]); P[4],x11=FA(5,x13,pp[3,1],x12); P[5],x10=FA(6,x9,pp[3,2],x11); P[6],P[7]=FA(7,x8,pp[3,3],x10)
    net.outputs=P; return net
POSITIONS=[f'pp{i}' for i in range(16)]+[f'ha{i}' for i in range(4)]+[f'fa{i}' for i in range(8)]
MENUS={**{f'pp{i}':PP_MENU for i in range(16)},**{f'ha{i}':HA_MENU for i in range(4)},**{f'fa{i}':FA_MENU for i in range(8)}}

# ---------------- moves on a built netlist: resize instance, duplicate instance ----------------
def resize(net,ii,newsize):
    n=copy.deepcopy(net); base=CELLS[n.insts[ii]['cell']]['base']
    nm=f"{base}_{newsize}"
    if nm not in CELLS: return None
    n.insts[ii]['cell']=nm; return n
def duplicate(net,ii,sink_subset):
    """clone single-output instance ii; move given (inst,pin) sinks to clone"""
    n=copy.deepcopy(net); inst=n.insts[ii]
    if len(inst['outs'])!=1: return None
    op=list(inst['outs'])[0]; newnet=n.nnets; n.nnets+=1
    n.insts.append({'cell':inst['cell'],'pins':dict(inst['pins']),'outs':{op:newnet}})
    for (si,sp) in sink_subset: n.insts[si]['pins'][sp]=newnet
    return n

# ---------------- Verilog export ----------------
def to_verilog(net,name):
    L=[f"module {name}(input [3:0] a, input [3:0] b, output [7:0] p);"]
    nm={i:f"a[{i}]" for i in range(4)}; nm.update({4+i:f"b[{i}]" for i in range(4)})
    for k,o in enumerate(net.outputs): nm[o]=f"p[{k}]"
    wires=[f"n{i}" for i in range(8,net.nnets) if i not in nm]
    for i in range(8,net.nnets): nm.setdefault(i,f"n{i}")
    if wires: L.append("  wire "+", ".join(wires)+";")
    for ii,inst in enumerate(net.insts):
        conns=[f".{p}({nm[n]})" for p,n in inst['pins'].items()]+[f".{p}({nm[n]})" for p,n in inst['outs'].items()]
        L.append(f"  sky130_fd_sc_hd__{inst['cell']} g{ii} ({', '.join(conns)});")
    L.append("endmodule"); return "\n".join(L)+"\n"

def sta_delay(vfile,top):
    tcl=f"read_liberty {LIB_PATH}\nread_verilog {vfile}\nlink_design {top}\nset_input_transition 0.05 [all_inputs]\nset_load 0.010 [all_outputs]\nset_input_delay 0 [all_inputs]\nreport_checks -unconstrained -path_delay max -digits 4\nexit\n"
    m=re.search(r"([-\d.]+)\s+data arrival time",_run_sta(tcl))
    return float(m.group(1)) if m else None

if __name__=="__main__":
    print(f"{len(CELLS)} cells loaded")
    # uniform variants
    print("\nUniform variants (size 1), model vs OpenSTA:")
    rows=[]
    for ppv in PP_MENU:
        for hav in HA_MENU:
            for fav in FA_MENU:
                ch={**{f'pp{i}':(ppv,1) for i in range(16)},**{f'ha{i}':(hav,1) for i in range(4)},**{f'fa{i}':(fav,1) for i in range(8)}}
                net=build(ch); verify(net); d,a,_,_=timing(net)
                rows.append((d,a,ppv,hav,fav,net))
    rows.sort()
    for d,a,ppv,hav,fav,net in rows:
        nm=f"u_{ppv}_{hav}_{fav}".replace('+','_')
        open(f"{nm}.v","w").write(to_verilog(net,nm)); s=sta_delay(f"{nm}.v",nm)
        print(f"  pp={ppv:9s} ha={hav:8s} fa={fav:12s} cells={len(net.insts):3d} area={a:6.1f}  model={d*1000:6.0f}ps  STA={s*1000 if s else float('nan'):6.0f}ps")
