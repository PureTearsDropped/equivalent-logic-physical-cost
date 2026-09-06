"""Exhaustive gate-level check: simulate the exp netlist on every in-range binary32 input (65536 inputs per
bit-parallel pass) and compare with the spec dump (input,output UInt32 pairs from exp_f32_spec_v3.jl dumpall)."""
import sys, os, time, struct, numpy as np
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
import fullcell as F
from fullcell import *
from exp_f32_gates import build_exp
from fullcell import buffer_high_fanout
def run(path, chunk=65536, limit=None):
    net=build_exp(); buffer_high_fanout(net)
    order=topo(net); outs=net.outputs
    data=np.fromfile(path,dtype=np.uint32).reshape(-1,2)
    if limit: data=data[:limit]
    N=len(data); bad=0; baddec=0; t0=time.time(); done=0
    F.ROWS=chunk; F.MASK=(1<<chunk)-1
    for s in range(0,N,chunk):
        xs=data[s:s+chunk,0]; want=data[s:s+chunk,1]; n=len(xs)
        if n!=chunk: F.ROWS=n; F.MASK=(1<<n)-1
        # pack input bit b over rows: column b of the (n x 32) bit matrix
        bitsm=((xs[:,None]>>np.arange(32,dtype=np.uint32))&1).astype(np.uint8)   # n x 32
        vals=[None]*net.nnets
        for b in range(32):
            col=np.packbits(bitsm[:,b],bitorder='little').tobytes(); vals[b]=F.TT(int.from_bytes(col,'little'))
        for ii in order:
            inst=net.insts[ii]; pv={p:vals[x] for p,x in inst['pins'].items()}
            for op,x in inst['outs'].items(): vals[x]=cell_func(inst['cell'],op,pv)
        # unpack outputs: 31 value bits
        got=np.zeros(n,dtype=np.uint32)
        for b in range(31):
            o=outs[b]
            if o is None: continue
            arr=np.frombuffer(vals[o].v.to_bytes((n+7)//8,'little'),dtype=np.uint8)
            got|=(np.unpackbits(arr,bitorder='little')[:n].astype(np.uint32)<<b)
        dec=np.unpackbits(np.frombuffer(vals[outs[32]].v.to_bytes((n+7)//8,'little'),dtype=np.uint8),bitorder='little')[:n]
        bad+=int((got!=want).sum()); baddec+=int((dec==0).sum()); done+=n
        if (s//chunk)%200==0: print(f"  {done}/{N} mismatches={bad} undecided={baddec} {time.time()-t0:.0f}s",flush=True)
    print(f"EXHAUSTIVE: inputs={N} mismatches={bad} undecided={baddec} time={time.time()-t0:.0f}s")
if __name__=="__main__": run(sys.argv[1], limit=int(sys.argv[2]) if len(sys.argv)>2 else None)
