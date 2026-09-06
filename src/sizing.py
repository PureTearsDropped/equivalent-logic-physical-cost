import sys, copy, subprocess, re, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from paths import CELLS_DIR
from pa4x4 import *
import sky130_timing as ST
from sky130_timing import load_cell, interp2
from export_sta import sta_delay, to_verilog
CELLS={}
for base,pins in (('nand2',['A','B']),('nor2',['A','B']),('inv',['A'])):
    for d in (1,2,4): CELLS[(base,d)]=load_cell(CELLS_DIR/f'{base}_{d}.json',pins)

def timing(net,outs,size,out_load=0.010,in_slew=0.05):
    order=topo_order(net); sinks=fanout_pin_lists(net,outs); n=len(net.nodes)
    def cellof(i):
        nd=net.nodes[i]
        if nd.op=="IN": return None
        base='inv' if nd.a==nd.b else ('nand2' if nd.op=="NAND" else 'nor2')
        return CELLS[(base,size.get(i,1))]
    loads=[0.0]*n
    for src in range(n):
        c=0.0; seen=set()
        for cons,pin in sinks[src]:
            if cons=="OUT": c+=out_load; continue
            cell=cellof(cons)
            if len(cell['cin'])==1:
                if cons in seen: continue
                seen.add(cons); c+=cell['cin']['A']
            else: c+=cell['cin']['A' if pin=='a' else 'B']
        loads[src]=c
    rise=[0.0]*n; fall=[0.0]*n; sr=[in_slew]*n; sf=[in_slew]*n
    for i in order:
        nd=net.nodes[i]
        if nd.op=="IN": continue
        cell=cellof(i); pins=[('A',nd.a)] if len(cell['cin'])==1 else [('A',nd.a),('B',nd.b)]
        br=(-1,0); bf=(-1,0)
        for pn,src in pins:
            arc=cell['arcs'][pn]
            t=fall[src]+interp2(arc['cell_rise'],sf[src],loads[i]); 
            if t>br[0]: br=(t,interp2(arc['rise_transition'],sf[src],loads[i]))
            t=rise[src]+interp2(arc['cell_fall'],sr[src],loads[i])
            if t>bf[0]: bf=(t,interp2(arc['fall_transition'],sr[src],loads[i]))
        rise[i],sr[i]=br; fall[i],sf[i]=bf
    area=sum(cellof(i)['area'] for i in range(n) if net.nodes[i].op!="IN")
    return max(max(rise[o],fall[o]) for o in outs),area,sinks

def optimize(net,outs,allow_dup=True,allow_size=True,steps=40,rank='gain'):
    cur=copy.deepcopy(net); size={}
    d,a,sinks=timing(cur,outs,size); hist=[(d,a,'start')]
    for _ in range(steps):
        best=None
        if allow_dup:
            for nid,nd in enumerate(cur.nodes):
                if nd.op=="IN": continue
                s=[x for x in sinks[nid] if x[0]!="OUT"]; m=len(s)
                if m<2 or m>6: continue
                for mask in range(1,(1<<m)-1):
                    sub=[s[k] for k in range(m) if (mask>>k)&1]
                    if len(sub)>m-len(sub) or (len(sub)==m-len(sub) and not mask&1): continue
                    c=duplicate_and_rewire(cur,nid,sub); sz=dict(size); sz[len(c.nodes)-1]=size.get(nid,1)
                    dc,ac,_=timing(c,outs,sz); g=d-dc
                    if g<=1e-9: continue
                    key=g if rank=='gain' else g/max(ac-a,1e-9)
                    if best is None or key>best[0]: best=(key,c,sz,dc,ac,f'dup {nid}')
        if allow_size:
            for nid,nd in enumerate(cur.nodes):
                if nd.op=="IN": continue
                s0=size.get(nid,1)
                if s0>=4: continue
                sz=dict(size); sz[nid]=s0*2
                dc,ac,_=timing(cur,outs,sz); g=d-dc
                if g<=1e-9: continue
                key=g if rank=='gain' else g/max(ac-a,1e-9)
                if best is None or key>best[0]: best=(key,copy.deepcopy(cur),sz,dc,ac,f'size {nid}->{s0*2}')
        if best is None: break
        _,cur,size,d,a,mv=best; _,_,sinks=timing(cur,outs,size); hist.append((d,a,mv))
    verify_array4(cur,outs)
    return cur,size,hist

net,outs=build_array4(ALL_NAND_FA)
d0,a0,_=timing(net,outs,{})
print(f"start: {d0*1000:.1f} ps, {a0:.1f} um^2 (all-NAND, tied->inv_1)")
results={}
for label,kw in [("dup only",dict(allow_size=False)),("size only",dict(allow_dup=False)),("dup+size",{}),("dup+size, rank=gain/area",dict(rank='eff'))]:
    cur,size,hist=optimize(net,outs,**kw)
    results[label]=(cur,size,hist)
    nd=sum(1 for h in hist if h[2].startswith('dup')); ns=sum(1 for h in hist if h[2].startswith('size'))
    print(f"\n{label}: {len(hist)-1} moves (dup {nd}, size {ns})  {d0*1000:.1f} -> {hist[-1][0]*1000:.1f} ps ({(1-hist[-1][0]/d0)*100:.2f}% faster), area {a0:.1f} -> {hist[-1][1]:.1f} (+{(hist[-1][1]/a0-1)*100:.1f}%)")
    # Pareto trace: delay at area budgets
    for tgt in (0.02,0.05,0.10):
        pts=[h for h in hist if h[1]<=a0*(1+tgt)]
        print(f"   within +{tgt*100:.0f}% area: {pts[-1][0]*1000:.1f} ps ({(1-pts[-1][0]/d0)*100:.2f}%)")
    print("   moves:", ", ".join(h[2] for h in hist[1:13]), "..." if len(hist)>13 else "")
# STA check of dup+size result
cur,size,hist=results["dup+size"]
open('opt_ds.v','w').write(to_verilog(cur,outs,'opt_ds',use_inv=True,size=size))
sta,out=sta_delay('opt_ds.v','opt_ds')
print(f"\nOpenSTA on dup+size result: {sta*1000:.1f} ps  (model {hist[-1][0]*1000:.1f} ps)")
cur,size,hist=results["size only"]
open('opt_s.v','w').write(to_verilog(cur,outs,'opt_s',use_inv=True,size=size))
sta,out=sta_delay('opt_s.v','opt_s')
print(f"OpenSTA on size-only result: {sta*1000:.1f} ps  (model {hist[-1][0]*1000:.1f} ps)")
