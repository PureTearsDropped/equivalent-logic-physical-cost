import sys, copy, time, json, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from fullcell import *

def phase1(choice,rank='gain',steps=60,max_area=None):
    """greedy over per-position (variant,size) choices"""
    net=build(choice); d,a,_,_=timing(net); hist=[(d,a,'start')]
    for _ in range(steps):
        best=None
        for pos in POSITIONS:
            for v in MENUS[pos]:
                for s in (1,2,4):
                    if choice.get(pos,(list(MENUS[pos])[0],1))==(v,s): continue
                    c2=dict(choice); c2[pos]=(v,s)
                    try: n2=build(c2)
                    except (AssertionError,KeyError): continue
                    d2,a2,_,_=timing(n2); g=d-d2
                    if g<=1e-9: continue
                    if max_area and a2>max_area: continue
                    key=g if rank=='gain' else g/max(a2-a,1e-6) if a2>a else g*1e6
                    if best is None or key>best[0]: best=(key,c2,d2,a2,f'{pos}->{v}_{s}')
        if best is None: break
        _,choice,d,a,mv=best; hist.append((d,a,mv))
    return choice,hist

def phase2(net,rank='gain',steps=60,max_area=None):
    cur=copy.deepcopy(net); d,a,sinks,_=timing(cur); hist=[(d,a,'start')]
    for _ in range(steps):
        best=None
        for ii,inst in enumerate(cur.insts):
            s0=CELLS[inst['cell']]['size']
            for s in (1,2,4):
                if s==s0: continue
                n2=resize(cur,ii,s)
                if n2 is None: continue
                d2,a2,_,_=timing(n2); g=d-d2
                if g<=1e-9 or (max_area and a2>max_area): continue
                key=g if rank=='gain' else g/max(a2-a,1e-6) if a2>a else g*1e6
                if best is None or key>best[0]: best=(key,n2,d2,a2,f'size g{ii} {inst["cell"]}->{s}')
            if len(inst['outs'])==1:
                on=list(inst['outs'].values())[0]; sk=sinks[on]; m=len(sk)
                if 2<=m<=6:
                    for mask in range(1,(1<<m)-1):
                        sub=[sk[k] for k in range(m) if (mask>>k)&1]
                        if len(sub)>m-len(sub) or (len(sub)==m-len(sub) and not mask&1): continue
                        n2=duplicate(cur,ii,sub); d2,a2,_,_=timing(n2); g=d-d2
                        if g<=1e-9 or (max_area and a2>max_area): continue
                        key=g if rank=='gain' else g/max(a2-a,1e-6) if a2>a else g*1e6
                        if best is None or key>best[0]: best=(key,n2,d2,a2,f'dup g{ii} {inst["cell"]} ({len(sub)} sinks)')
        if best is None: break
        _,cur,d,a,mv=best; _,_,sinks,_=timing(cur); hist.append((d,a,mv))
    verify(cur)
    return cur,hist

if __name__=='__main__':
    t0=time.time()
    start={**{f'pp{i}':('nand+inv',1) for i in range(16)},**{f'ha{i}':('nand5',1) for i in range(4)},**{f'fa{i}':('nand9',1) for i in range(8)}}
    results={}
    for rank in ('gain','eff'):
        ch,h1=phase1(dict(start),rank=rank)
        net=build(ch); verify(net)
        print(f"\n[{rank}] phase1: {len(h1)-1} moves  {h1[0][0]*1000:.0f}->{h1[-1][0]*1000:.0f}ps  area {h1[0][1]:.0f}->{h1[-1][1]:.0f}   ({time.time()-t0:.0f}s)")
        print("   choices:", {k:v for k,v in ch.items() if v!=start[k]})
        net2,h2=phase2(net,rank=rank)
        print(f"[{rank}] phase2: {len(h2)-1} moves  {h2[0][0]*1000:.0f}->{h2[-1][0]*1000:.0f}ps  area {h2[0][1]:.0f}->{h2[-1][1]:.0f}   ({time.time()-t0:.0f}s)")
        print("   moves:", ", ".join(m for _,_,m in h2[1:10]),"...")
        # Pareto trace of combined history
        hist=h1+h2[1:]
        for tgt in (450,500,550,600,700,800,1000):
            pts=[h for h in hist if h[1]<=tgt]
            if pts: print(f"   area<={tgt}: {min(p[0] for p in pts)*1000:.0f}ps")
        results[rank]=(net2,hist,ch)
        nm=f"full_{rank}"; open(f"{nm}.v","w").write(to_verilog(net2,nm)); s=sta_delay(f"{nm}.v",nm)
        print(f"   final: cells={len(net2.insts)} area={h2[-1][1]:.0f} model={h2[-1][0]*1000:.0f}ps OpenSTA={s*1000:.0f}ps")
        # also export the point at area<=600 and <=550 for P&R
        json.dump([(d,a,m) for d,a,m in hist],open(f"{nm}_hist.json","w"))
    print("done",time.time()-t0)
