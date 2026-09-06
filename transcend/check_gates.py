"""Simulate the gate-level exp netlist on the spec model's random vectors (bit-parallel) and compare bit-exactly."""
import sys, os, time
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import fullcell as F
from fullcell import *
def check(net, vec_path, limit=None):
    rows=[l.split() for l in open(vec_path)][:limit]
    xs=[int(r[0],16) for r in rows]; want=[int(r[1],16) for r in rows]; wdec=[int(r[2]) for r in rows]
    n=len(rows); F.ROWS=n; F.MASK=(1<<n)-1
    vals=[None]*net.nnets
    for b in range(32): vals[b]=F.TT(sum(((x>>b)&1)<<i for i,x in enumerate(xs)))
    t0=time.time()
    for ii in topo(net):
        inst=net.insts[ii]; pv={p:vals[x] for p,x in inst['pins'].items()}
        for op,x in inst['outs'].items(): vals[x]=cell_func(inst['cell'],op,pv)
    outs=net.outputs   # 23 mant bits, 8 exponent bits, sign(None), decided
    bad=0; baddec=0; ex=[]
    for i in range(n):
        got=0
        for b in range(31):
            o=outs[b]
            if o is not None and (vals[o].v>>i)&1: got|=1<<b
        dec=(vals[outs[32]].v>>i)&1 if outs[32] is not None else 1
        if got!=want[i]: bad+=1; len(ex)<5 and ex.append((hex(xs[i]),hex(got),hex(want[i])))
        if dec!=wdec[i]: baddec+=1
    print(f"vectors={n} mismatches={bad} decided-mismatches={baddec} sim {time.time()-t0:.1f}s"); [print("  ",e) for e in ex]
    return bad==0 and baddec==0
if __name__=="__main__":
    import pickle
    net=pickle.load(open(sys.argv[1],'rb')); check(net, sys.argv[2], int(sys.argv[3]) if len(sys.argv)>3 else None)
