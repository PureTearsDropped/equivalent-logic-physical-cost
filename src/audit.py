import sys, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pa4x4 import *
import itertools

# ---- (1) FA-internal depths: cin->carry, cin->sum, a->carry, a->sum
def fa_depths(fa):
    d=[0,0,0]; ids=[0,1,2]
    sigs=[A_SIG,B_SIG,CIN_SIG]
    # depth from each input separately
    res={}
    for src in range(3):
        dep=[None]*3; dep[src]=0
        sg=list(sigs)
        for g in fa:
            f = FA_MASK ^ (sg[g.a]&sg[g.b]) if g.op=="NAND" else FA_MASK ^ (sg[g.a]|sg[g.b])
            sg.append(f)
            cand=[dep[g.a],dep[g.b]]; cand=[c for c in cand if c is not None]
            dep.append(max(cand)+1 if cand else None)
        s=[i for i,f in enumerate(sg) if f==SUM_SIG][-1]; c=[i for i,f in enumerate(sg) if f==CARRY_SIG][-1]
        res[src]=(dep[s],dep[c])
    return res
print("FA internal depths {input:(to_sum,to_carry)}  0=a 1=b 2=cin")
for n,fa in [("gate-count-only",GATE_COUNT_ONLY_FA),("arrival-aware",ARRIVAL_AWARE_MIXED_FA),("all-NAND",ALL_NAND_FA)]:
    nn=sum(1 for g in fa if g.op=="NAND"); nr=len(fa)-nn
    print(f"  {n:16s} NAND={nn} NOR={nr}  {fa_depths(fa)}")

# ---- (2) independent bit-parallel verification (256 rows packed in one int)
def bitpar_verify(net,outs):
    order=topo_order(net); M=(1<<256)-1
    vals=[0]*len(net.nodes)
    ins=[i for i,n in enumerate(net.nodes) if n.op=="IN"]
    for k,i in enumerate(ins):
        s=0
        for row in range(256):
            a,b=row&15,row>>4
            bit=(a>>k)&1 if k<4 else (b>>(k-4))&1
            s|=bit<<row
        vals[i]=s
    for i in order:
        nd=net.nodes[i]
        if nd.op=="IN": continue
        vals[i]= M^(vals[nd.a]&vals[nd.b]) if nd.op=="NAND" else M^(vals[nd.a]|vals[nd.b])
    for row in range(256):
        a,b=row&15,row>>4
        got=sum(((vals[o]>>row)&1)<<k for k,o in enumerate(outs))
        assert got==a*b,(a,b,got)
    return True

# ---- (3) run sweep over libs
def run(lib,out_load=2.0,steps=8,quiet=False):
    res={}
    for name,fa in [("gate-count-only",GATE_COUNT_ONLY_FA),("arrival-aware",ARRIVAL_AWARE_MIXED_FA),("all-NAND",ALL_NAND_FA)]:
        net,outs=build_array4(fa); tm=physical_timing(net,outs,lib,out_load)
        res[name]=(tm.critical_delay,tm.area,net,outs)
    best=min(res,key=lambda k:res[k][0])
    net,outs=res[best][2],res[best][3]
    opt,hist=greedy_duplicate(net,outs,steps,lib,out_load)
    bitpar_verify(opt,outs)
    return res,best,hist,opt,outs

libs={
 "default":DEFAULT_LIB,
 "NOR==NAND":{"NAND":DEFAULT_LIB["NAND"],"NOR":DEFAULT_LIB["NAND"]},
 "unit(p=1,r=0,cin=1)":{k:Cell(1,1,0,1,0,1) for k in ("NAND","NOR")},
 "NAND expensive(swap)":{"NAND":DEFAULT_LIB["NOR"],"NOR":DEFAULT_LIB["NAND"]},
 "NOR fall-fast only":{"NAND":DEFAULT_LIB["NAND"],"NOR":Cell(1.0,0.8,0.55,0.6,0.4,1.0)},
}
print("\nlib sweep: delay per variant | winner | dup history (delay after each accepted dup)")
for ln,lib in libs.items():
    res,best,hist,opt,outs=run(lib)
    ds=" ".join(f"{k}={v[0]:.3f}" for k,v in res.items())
    print(f"  {ln:22s} {ds} | win={best:15s} | {' -> '.join(f'{h['critical_delay']:.3f}' for h in hist)}  (+{len(hist)-1} gates)")

# out_load sensitivity, default lib
print("\nout_load sweep (default lib, all-NAND start):")
for ol in (0.0,1.0,2.0,4.0,8.0):
    res,best,hist,opt,outs=run(DEFAULT_LIB,ol)
    print(f"  out_load={ol:4.1f} start={hist[0]['critical_delay']:.3f} end={hist[-1]['critical_delay']:.3f} dups={len(hist)-1} red={(1-hist[-1]['critical_delay']/hist[0]['critical_delay'])*100:.2f}%")

# ---- (4) identify duplicated nodes & critical path in default run
net,outs=build_array4(ALL_NAND_FA)
tm=physical_timing(net,outs)
def crit_path(net,outs,tm):
    o=max(outs,key=lambda o:max(tm.rise[o],tm.fall[o])); path=[]
    i=o; ph='rise' if tm.rise[o]>=tm.fall[o] else 'fall'
    while net.nodes[i].op!="IN":
        path.append((i,ph,round(tm.rise[i] if ph=='rise' else tm.fall[i],3),round(tm.loads[i],2)))
        nd=net.nodes[i]
        if ph=='rise': i=max((nd.a,nd.b),key=lambda x:tm.fall[x]); ph='fall'
        else: i=max((nd.a,nd.b),key=lambda x:tm.rise[x]); ph='rise'
    return o,path
o,path=crit_path(net,outs,tm)
print(f"\ncritical output P{outs.index(o)}; path length {len(path)} (depth {logical_depth(net,outs)})")
print("  first 6 (from output):",path[:6])
for nid in (48,49,58,118):
    nd=net.nodes[nid]; print(f"  node {nid}: {nd.op}({nd.a},{nd.b}) sinks={tm.sinks[nid]} load={tm.loads[nid]}")
# how many nodes have tied inputs (inverter-as-NAND)?
tied=sum(1 for n in net.nodes if n.op!="IN" and n.a==n.b)
print(f"  tied-input NAND (inverters) = {tied} of {len(net.nodes)-8} gates; each counts load 2*cin")
