"""Two's-complement (binary {0,1}) signed multiplier with Dadda + Kogge-Stone (Baugh–Wooley partial products),
to compare against the signed-digit (two-rail) multiplier of sd_tree.py at equal numeric range."""
import sys, os, random; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *
from rep_sweep import ColBuilder, timing_any
def signed_multiplier(n, final='ks', cells=('and2','xor+and','xor2x2+a21o')):
    """n-bit two's complement a, b (inputs 0..n-1 = a, n..2n-1 = b) -> 2n-bit two's complement product."""
    net=Net(n); pp,ha,fa=cells; W=2*n
    A=list(range(n)); B=list(range(n,2*n))
    INV=lambda x: net.add('inv_1',{'A':x})['Y']; AND=lambda x,y: net.add('and2_1',{'A':x,'B':y})['X']
    cb=ColBuilder(net,W,pp,ha,fa)
    # Baugh–Wooley: a_i b_j for i,j<n-1 positive; a_{n-1} b_j and a_i b_{n-1} negative -> use complemented terms + constants
    for i in range(n):
        for j in range(n):
            t=AND(A[i],B[j])
            if (i==n-1) != (j==n-1): t=INV(t)          # exactly one sign bit: negative weight -> complement
            cb.cols[i+j].append(t)
    # correction constants: +2^(n) ... standard BW: add 1 at weight n and at weight 2n-1 (mod 2^2n)
    one=net.add('conb_1',{})['HI']
    cb.cols[n].append(one); cb.cols[2*n-1].append(one)
    sched_dadda(cb)
    for k in list(cb.cols):
        if k>=W: del cb.cols[k]
    net.outputs=cb.resolve(final); net.signed_n=n; return net
def check_signed(net, nvec=2048, seed=5):
    import fullcell as F
    rng=random.Random(seed); n=net.signed_n
    F.ROWS=nvec; F.MASK=(1<<nvec)-1
    A=[rng.randrange(-(1<<(n-1)),1<<(n-1)) for _ in range(nvec)]; B=[rng.randrange(-(1<<(n-1)),1<<(n-1)) for _ in range(nvec)]
    def bits(v): return v & ((1<<n)-1)
    prim=[F.TT(sum(((bits(A[r])>>k)&1)<<r for r in range(nvec))) for k in range(n)]+[F.TT(sum(((bits(B[r])>>k)&1)<<r for r in range(nvec))) for k in range(n)]
    vals=[None]*net.nnets
    for i in range(2*n): vals[i]=prim[i]
    for ii in topo(net):
        inst=net.insts[ii]; pv={p:vals[x] for p,x in inst['pins'].items()}
        for op,x in inst['outs'].items(): vals[x]=cell_func(inst['cell'],op,pv)
    W=2*n
    for r in range(nvec):
        got=sum((((vals[o].v>>r)&1) if o is not None else 0)<<k for k,o in enumerate(net.outputs))
        if got>=1<<(W-1): got-=1<<W
        if got!=A[r]*B[r]: raise AssertionError(f"{A[r]}*{B[r]}: got {got}")
    F.set_width(4); return True
if __name__=="__main__":
    print(f"{'design':50s} {'cells':>6s} {'area':>7s} {'delay':>7s}")
    for n,final in ((11,'ks'),(11,'ripple'),(10,'ks')):
        net=signed_multiplier(n,final); check_signed(net); d,a=timing_any(net)
        print(f"{f'binary two-complement {n}x{n} (range ±{1<<(n-1)}), Dadda+{final}':50s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps")
    # tree-only (carry-save output) for the 11-bit case
    net=Net(11); n=11; cb=ColBuilder(net,22,'and2','xor+and','xor2x2+a21o'); A=list(range(n)); B=list(range(n,2*n))
    for i in range(n):
        for j in range(n):
            t=net.add('and2_1',{'A':A[i],'B':B[j]})['X']
            if (i==n-1)!=(j==n-1): t=net.add('inv_1',{'A':t})['Y']
            cb.cols[i+j].append(t)
    one=net.add('conb_1',{})['HI']; cb.cols[n].append(one); cb.cols[2*n-1].append(one); sched_dadda(cb)
    net.outputs=[cb.cols[k][0] if cb.cols[k] else None for k in range(22)]+[cb.cols[k][1] if len(cb.cols[k])>1 else None for k in range(22)]
    d,a=timing_any(net); print(f"{'binary 11x11, tree only (two rows out)':50s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps")
