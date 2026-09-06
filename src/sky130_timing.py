import sys, json, copy, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from paths import CELLS_DIR
from pa4x4 import *
import numpy as np

def load_cell(path, inpins):
    d=json.load(open(path))
    cell={'area':d['area'],'cin':{p:d[f'pin,{p}']['capacitance'] for p in inpins},'arcs':{}}
    tl=d['pin,Y']['timing']
    if isinstance(tl,dict): tl=[tl]
    for t in tl:
        rp=t['related_pin']
        arc={}
        for key in ('cell_rise','cell_fall','rise_transition','fall_transition'):
            tb=[v for k,v in t.items() if k.startswith(key)][0]
            arc[key]=(np.array(tb['index_1'],float),np.array(tb['index_2'],float),np.array(tb['values'],float).reshape(len(tb['index_1']),len(tb['index_2'])))
        cell['arcs'][rp]=arc
    return cell
NAND=load_cell(CELLS_DIR/'nand2_1.json',['A','B']); NOR=load_cell(CELLS_DIR/'nor2_1.json',['A','B']); INV=load_cell(CELLS_DIR/'inv_1.json',['A'])
if __name__=="__main__": print("sky130_fd_sc_hd tt_025C_1v80 (units ns, pF):")
for n,c in (('nand2_1',NAND),('nor2_1',NOR),('inv_1',INV)) if __name__=='__main__' else ():
    a=c['arcs'][list(c['arcs'])[0]]
    # report delay at slew index ~0.05ns, cap ~ 3 nand inputs (0.007pF) via interpolation
    def lk(tab,s,cl): 
        i1,i2,v=tab; return float(np.interp(cl,i2,[np.interp(s,i1,v[:,j]) for j in range(len(i2))]))
    print(f"  {n:8s} area={c['area']:.2f} cin={list(c['cin'].values())[0]*1000:.2f}fF  @slew50ps,load7fF: rise={lk(a['cell_rise'],0.05,0.007)*1000:.0f}ps fall={lk(a['cell_fall'],0.05,0.007)*1000:.0f}ps  slope d(delay)/dC: rise={(lk(a['cell_rise'],0.05,0.02)-lk(a['cell_rise'],0.05,0.005))/0.015:.2f} fall={(lk(a['cell_fall'],0.05,0.02)-lk(a['cell_fall'],0.05,0.005))/0.015:.2f} ns/pF")

def interp2(tab,s,cl):
    i1,i2,v=tab
    s=min(max(s,i1[0]),i1[-1]); cl=min(max(cl,i2[0]),i2[-1])
    col=[np.interp(s,i1,v[:,j]) for j in range(len(i2))]
    return float(np.interp(cl,i2,col))

def nldm_timing(net,outputs,out_load=0.010,in_slew=0.05,use_inv=False):
    """Arrival+slew propagation with sky130 NLDM tables. Tied-input NAND -> inv_1 if use_inv."""
    order=topo_order(net); sinks=fanout_pin_lists(net,outputs)
    def cellof(nd):
        if nd.op=="IN": return None
        if use_inv and nd.a==nd.b: return INV
        return NAND if nd.op=="NAND" else NOR
    n=len(net.nodes)
    loads=[0.0]*n
    for src in range(n):
        c=0.0; seen=set()
        for cons,pin in sinks[src]:
            if cons=="OUT": c+=out_load; continue
            cell=cellof(net.nodes[cons])
            if cell is INV:
                if cons in seen: continue   # inverter has one pin
                seen.add(cons); c+=cell['cin']['A']
            else: c+=cell['cin']['A' if pin=='a' else 'B']
        loads[src]=c
    rise=[0.0]*n; fall=[0.0]*n; srise=[in_slew]*n; sfall=[in_slew]*n
    for i in order:
        nd=net.nodes[i]
        if nd.op=="IN": continue
        cell=cellof(nd)
        best_r=(-1,0); best_f=(-1,0)
        pins=[('A',nd.a)] if cell is INV else [('A',nd.a),('B',nd.b)]
        for pn,src in pins:
            arc=cell['arcs'][pn]
            # output rise from input fall
            t=fall[src]+interp2(arc['cell_rise'],sfall[src],loads[i]); tr=interp2(arc['rise_transition'],sfall[src],loads[i])
            if t>best_r[0]: best_r=(t,tr)
            t=rise[src]+interp2(arc['cell_fall'],srise[src],loads[i]); tf=interp2(arc['fall_transition'],srise[src],loads[i])
            if t>best_f[0]: best_f=(t,tf)
        rise[i],srise[i]=best_r; fall[i],sfall[i]=best_f
    area=sum(cellof(nd)['area'] for nd in net.nodes if nd.op!="IN")
    arr=[max(rise[o],fall[o]) for o in outputs]
    return max(arr),area,loads,sinks

def greedy(net,outputs,steps=12,**kw):
    cur=copy.deepcopy(net); d0,a0,_,_=nldm_timing(cur,outputs,**kw); hist=[(d0,a0)]
    for _ in range(steps):
        d,a,loads,sinks=nldm_timing(cur,outputs,**kw); best=None
        for nid,nd in enumerate(cur.nodes):
            if nd.op=="IN": continue
            s=[x for x in sinks[nid] if x[0]!="OUT"]; m=len(s)
            if m<2 or m>6: continue
            for mask in range(1,(1<<m)-1):
                sub=[s[k] for k in range(m) if (mask>>k)&1]
                if len(sub)>m-len(sub) or (len(sub)==m-len(sub) and not mask&1): continue
                c=duplicate_and_rewire(cur,nid,sub); dc,ac,_,_=nldm_timing(c,outputs,**kw)
                g=d-dc
                if g>1e-9 and (best is None or (g,-ac)>best[0]): best=((g,-ac),c,dc,ac)
        if best is None: break
        cur=best[1]; hist.append((best[2],best[3]))
    verify_array4(cur,outputs)
    return hist

for use_inv in ((False,True) if __name__=='__main__' else ()):
    print(f"\n=== sky130 NLDM, tied-NAND as {'inv_1' if use_inv else 'nand2_1'} , out_load=10fF, in_slew=50ps ===")
    res={}
    for name,fa in [("gate-count-only",GATE_COUNT_ONLY_FA),("arrival-aware",ARRIVAL_AWARE_MIXED_FA),("all-NAND",ALL_NAND_FA)]:
        net,outs=build_array4(fa); d,a,_,_=nldm_timing(net,outs,use_inv=use_inv); res[name]=(d,a,net,outs)
        print(f"  {name:16s} delay={d*1000:7.1f} ps  area={a:7.2f} um^2")
    for name in ("all-NAND","arrival-aware"):
        d,a,net,outs=res[name]
        h=greedy(net,outs,use_inv=use_inv)
        print(f"  greedy dup on {name}: "+" -> ".join(f"{x[0]*1000:.1f}" for x in h)+f"  ps  ({len(h)-1} dups, area {h[0][1]:.1f}->{h[-1][1]:.1f}, {(1-h[-1][0]/h[0][0])*100:.2f}% faster)")
