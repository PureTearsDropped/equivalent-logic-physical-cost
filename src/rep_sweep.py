"""Representation sweep: dot product sum_k a_k*b_k (n-bit operands, K pairs) in three representations,
measured in delay (NLDM) and cells/area. binary = each product resolved to binary then added with CPAs;
carrysave = all partial products in one compression tree, one CPA at the end; redundant = tree only (no CPA)."""
import sys, os, random, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *

class ColBuilder(Builder):
    """Builder over an arbitrary set of primary inputs / preloaded columns."""
    def __init__(self, net, W, pp='and2', ha='xor+and', fa='xor2x2+a21o', size=1):
        self.n=W//2; self.W=W; self.net=net; self.ppf=PP_MENU[pp]; self.haf=HA_MENU[ha]; self.faf=FA_MENU[fa]; self.s=size; self.late=False
        self.cols={k:[] for k in range(W)}; self.steps=[]; self._arr=None
    def add_pp(self, A, B):
        for i,ai in enumerate(A):
            for j,bj in enumerate(B): self.cols[i+j].append(self.ppf(self.net,ai,bj,self.s))
    def add_number(self, bits):
        for k,x in enumerate(bits):
            if x is not None: self.cols[k].append(x)
    def reduce_to_2(self):
        sched_dadda(self); return self
    def resolve(self, final):
        self.net.outputs=[None]*self.W
        net = self.kogge_stone() if final=='ks' else self.ripple()
        return list(net.outputs)

def dot_product(n, K, rep, final, cells=('and2','xor+and','xor2x2+a21o')):
    net=Net(n*K); W=2*n+math.ceil(math.log2(K)) if K>1 else 2*n
    A=[[k*n+j for j in range(n)] for k in range(K)]; B=[[n*K+k*n+j for j in range(n)] for k in range(K)]
    pp,ha,fa=cells
    if rep=='binary':
        nums=[]
        for k in range(K):
            cb=ColBuilder(net,2*n,pp,ha,fa); cb.add_pp(A[k],B[k]); cb.reduce_to_2(); nums.append(cb.resolve(final))
        while len(nums)>1:               # balanced tree of binary adders
            nxt=[]
            for i in range(0,len(nums)-1,2):
                w=max(len(nums[i]),len(nums[i+1]))+1
                cb=ColBuilder(net,w,pp,ha,fa); cb.add_number(nums[i]); cb.add_number(nums[i+1]); cb.reduce_to_2(); nxt.append(cb.resolve(final))
            if len(nums)%2: nxt.append(nums[-1])
            nums=nxt
        out=nums[0][:W]+[None]*(W-len(nums[0]))
        net.outputs=out; return net
    cb=ColBuilder(net,W,pp,ha,fa)
    for k in range(K): cb.add_pp(A[k],B[k])
    cb.reduce_to_2()
    if rep=='carrysave':
        net.outputs=cb.resolve(final); return net
    # redundant: two rows out, no CPA. outputs = row0 bits then row1 bits (None where a column has one bit)
    rows=[[],[]]
    for k in range(W):
        b=cb.cols[k]; rows[0].append(b[0] if b else None); rows[1].append(b[1] if len(b)>1 else None)
    net.outputs=rows[0]+rows[1]; net.redundant=True; return net

def check(net, n, K, nvec=2048, seed=1):
    """random bit-parallel check of sum_k a_k b_k; handles redundant (two-row) outputs"""
    import fullcell as F
    rng=random.Random(seed); F.set_width(1)  # placeholder; we build PRIM manually
    F.ROWS=nvec; F.MASK=(1<<nvec)-1
    As=[[rng.getrandbits(n) for _ in range(K)] for _ in range(nvec)]; Bs=[[rng.getrandbits(n) for _ in range(K)] for _ in range(nvec)]
    prim=[None]*(2*n*K)
    for k in range(K):
        for j in range(n):
            prim[k*n+j]=F.TT(sum(((As[r][k]>>j)&1)<<r for r in range(nvec)))
            prim[n*K+k*n+j]=F.TT(sum(((Bs[r][k]>>j)&1)<<r for r in range(nvec)))
    vals=[None]*net.nnets
    for i in range(2*n*K): vals[i]=prim[i]
    for ii in topo(net):
        inst=net.insts[ii]; pv={p:vals[x] for p,x in inst['pins'].items()}
        for op,x in inst['outs'].items(): vals[x]=cell_func(inst['cell'],op,pv)
    W=len(net.outputs)//2 if getattr(net,'redundant',False) else len(net.outputs)
    for r in range(nvec):
        want=sum(As[r][k]*Bs[r][k] for k in range(K))
        if getattr(net,'redundant',False):
            got=sum((((vals[o].v>>r)&1) if o is not None else 0)<<(i%W) for i,o in enumerate(net.outputs))
        else:
            got=sum((((vals[o].v>>r)&1) if o is not None else 0)<<i for i,o in enumerate(net.outputs))
        if got!=want: raise AssertionError(f"row {r}: got {got} want {want}")
    F.set_width(4); return True

def timing_any(net):
    """timing over defined outputs only"""
    saved=net.outputs; net.outputs=[o for o in saved if o is not None]
    d,a,_,_=timing(net); net.outputs=saved; return d,a

if __name__=="__main__":
    n=int(sys.argv[1]) if len(sys.argv)>1 else 8
    print(f"dot product of K pairs of {n}-bit operands; cells and2/xor+and/xor2x2+a21o, size 1")
    print(f"{'K':>2s} {'rep':10s} {'final':7s} {'cells':>6s} {'area':>7s} {'delay':>7s}")
    os.makedirs("out",exist_ok=True)
    for K in (1,2,4,8):
        for rep,final in (('binary','ripple'),('binary','ks'),('carrysave','ripple'),('carrysave','ks'),('redundant','-')):
            net=dot_product(n,K,rep,final); check(net,n,K); d,a=timing_any(net)
            print(f"{K:2d} {rep:10s} {final:7s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps",flush=True)
            if K==4 and rep!='redundant':
                outs=[o for o in net.outputs if o is not None]; saved=net.outputs; net.outputs=outs
                open(f"out/dot{n}_K{K}_{rep}_{final}.v","w").write(to_verilog(net,f"dot{n}_K{K}_{rep}_{final}")); net.outputs=saved
