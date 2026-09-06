"""Arithmetic-level search: partial-product matrix -> column-compression schedule (FA/HA steps) -> ripple final adder.
Every schedule is correct by the Lean theorem ArithEquiv.multiplier_correct (lean/ArithEquiv.lean); the emitted
netlist is still verified exhaustively. Physical cost = NLDM model (fullcell.timing), then OpenSTA / LibreLane."""
import sys, os, random, copy, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fullcell import *

class Builder:
    def __init__(self, pp='nand+inv', ha='nand5', fa='nand9', size=1, late_to_cin=True):
        self.net=Net(); self.ppf=PP_MENU[pp]; self.haf=HA_MENU[ha]; self.faf=FA_MENU[fa]; self.s=size; self.late=late_to_cin
        self.cols={k:[] for k in range(8)}; self.steps=[]
        A=list(range(4)); B=list(range(4,8))
        for i in range(4):
            for j in range(4): self.cols[i+j].append(self.ppf(self.net,A[i],B[j],size))
        self._arr=None
    def arrivals(self):
        if self._arr is None: self._arr=timing_detail(self.net)['arrival']
        return self._arr
    def order_by_arrival(self,bits):
        a=self.arrivals(); return sorted(bits,key=lambda n:a[n])
    def fa(self,k,bits):
        assert len(bits)==3 and all(b in self.cols[k] for b in bits)
        for b in bits: self.cols[k].remove(b)
        if self.late: bits=self.order_by_arrival(bits)      # latest -> cin
        s,c=self.faf(self.net,bits[0],bits[1],bits[2],self.s)
        self.cols[k].append(s); self.cols.setdefault(k+1,[]).append(c); self._arr=None; self.steps.append(('fa',k)); return s,c
    def ha(self,k,bits):
        assert len(bits)==2
        for b in bits: self.cols[k].remove(b)
        s,c=self.haf(self.net,bits[0],bits[1],self.s)
        self.cols[k].append(s); self.cols.setdefault(k+1,[]).append(c); self._arr=None; self.steps.append(('ha',k)); return s,c
    def height(self): return max(len(v) for v in self.cols.values())
    def ripple(self):
        """final carry-propagate: column by column, FA on 3 bits, HA on 2, pass 1."""
        P=[None]*8
        for k in range(8):
            while len(self.cols[k])>3: self.fa(k,self.order_by_arrival(self.cols[k])[:3])
            b=self.cols[k]
            if len(b)==3: s,_=self.fa(k,list(b)); P[k]=s
            elif len(b)==2: s,_=self.ha(k,list(b)); P[k]=s
            elif len(b)==1: P[k]=b[0]
            else: raise RuntimeError(f"empty column {k}")
            self.cols[k]=[P[k]]
        self.net.outputs=P; return self.net

def sched_array(b):
    """row-by-row accumulation (the classic array multiplier): reproduces pa4x4.build_array4"""
    # rows: row i occupies columns i..i+3; accumulate rows 1..3 into the running sum with a ripple per row
    rows={i:{} for i in range(4)}
    bits={k:list(v) for k,v in b.cols.items()}
    # identify pp bits by construction order: pp (i,j) was appended in i-major order
    idx=0; ppn={}
    for i in range(4):
        for j in range(4): ppn[i,j]=bits[i+j][ (i if True else 0) ] if False else None
    # simpler: rebuild mapping from net ids: pp nets were created in order i*4+j
    order=[n for k in range(8) for n in b.cols[k]]
    ids=sorted(order)  # net ids increase with creation order
    for i in range(4):
        for j in range(4): ppn[i,j]=ids[i*4+j] if b.ppf is PP_and2 else ids[i*4+j]
    # with nand+inv each pp creates 2 nets; the pp output is the inv output (the larger id). handle generically:
    outs=set(n for k in b.cols for n in b.cols[k]); ids=sorted(outs)
    for i in range(4):
        for j in range(4): ppn[i,j]=ids[i*4+j]
    acc={j:ppn[0,j] for j in range(4)}  # column -> net
    for i in range(1,4):
        carry=None; new={}
        for k in range(i, i+4+1):
            got=[]
            if k in acc: got.append(acc[k])
            if k-i in range(4): got.append(ppn[i,k-i])
            if carry is not None: got.append(carry)
            if len(got)==3: s,c=b.fa(k,got); new[k]=s; carry=c
            elif len(got)==2: s,c=b.ha(k,got); new[k]=s; carry=c
            elif len(got)==1: new[k]=got[0]; carry=None
            else: carry=None
        for k in range(i): new[k]=acc[k]
        acc=new
    for k in range(8): b.cols[k]=[acc[k]] if k in acc else b.cols[k]
    return b

def sched_wallace(b):
    while b.height()>2:
        for k in sorted(b.cols):
            bits=b.order_by_arrival(b.cols[k]); groups=[bits[i:i+3] for i in range(0,len(bits)-2,3)]
            for g in groups: b.fa(k,g)
    return b

def sched_dadda(b):
    targets=[3,2]
    for t in targets:
        for k in sorted(b.cols):
            while len(b.cols[k])>t:
                bits=b.order_by_arrival(b.cols[k])
                if len(b.cols[k])-t>=2: b.fa(k,bits[:3])
                else: b.ha(k,bits[:2])
    return b

def sched_greedy_time(b):
    """always compress the column that currently limits: pick the tallest column, earliest three bits"""
    while b.height()>2:
        k=max(b.cols,key=lambda k:(len(b.cols[k]),-k)); b.fa(k,b.order_by_arrival(b.cols[k])[:3])
    return b

def sched_random(b,rng,p_ha=0.15):
    while b.height()>2:
        ks=[k for k in b.cols if len(b.cols[k])>=3]; k=rng.choice(ks)
        b.fa(k,rng.sample(b.cols[k],3))
        if rng.random()<p_ha:
            ks2=[k for k in b.cols if len(b.cols[k])>=2]
            if ks2: k=rng.choice(ks2); b.ha(k,rng.sample(b.cols[k],2))
    return b

def build(sched,rng=None,**kw):
    b=Builder(**kw)
    (sched(b,rng) if sched is sched_random else sched(b)); net=b.ripple(); verify(net)
    d,a,_,_=timing(net); return net,d,a,b.steps

if __name__=="__main__":
    out={}
    print("named schedules (nand+inv / nand5 / nand9, size 1):")
    for name,s in (("array",sched_array),("wallace",sched_wallace),("dadda",sched_dadda),("greedy_time",sched_greedy_time)):
        for late in (False,True):
            net,d,a,steps=build(s,late_to_cin=late)
            nfa=sum(1 for t,_ in steps if t=='fa'); nha=len(steps)-nfa
            print(f"  {name:12s} late_to_cin={late!s:5s} cells={len(net.insts):3d} FA={nfa:2d} HA={nha:2d} area={a:6.1f} model={d*1000:6.0f}ps")
            out[f"{name}_{'late' if late else 'plain'}"]=(d,a,net)
    print("\nnamed schedules with FA=xor2x2+a21o, HA=xor+and, PP=and2:")
    for name,s in (("array",sched_array),("wallace",sched_wallace),("dadda",sched_dadda),("greedy_time",sched_greedy_time)):
        net,d,a,steps=build(s,pp='and2',ha='xor+and',fa='xor2x2+a21o')
        print(f"  {name:12s} cells={len(net.insts):3d} area={a:6.1f} model={d*1000:6.0f}ps"); out[f"{name}_xa"]=(d,a,net)
    rng=random.Random(1); samples=[]
    N=int(sys.argv[1]) if len(sys.argv)>1 else 400
    for i in range(N):
        fa=rng.choice(['nand9','xor2x2+a21o']); pp=rng.choice(['nand+inv','and2']); ha=rng.choice(['nand5','xor+and'])
        try: net,d,a,steps=build(sched_random,rng,pp=pp,ha=ha,fa=fa)
        except RuntimeError: continue
        samples.append((d,a,fa,pp,ha,net))
    samples.sort(key=lambda x:x[0])
    print(f"\nrandom schedules: {len(samples)} valid; best delay:")
    for d,a,fa,pp,ha,net in samples[:5]: print(f"  {d*1000:6.0f}ps area={a:6.1f} cells={len(net.insts):3d} fa={fa} pp={pp} ha={ha}")
    # Pareto of everything
    allpts=[(d,a,k) for k,(d,a,_) in out.items()]+[(d,a,f"rand{i}") for i,(d,a,*_) in enumerate(samples)]
    allpts.sort(); pareto=[]; best_a=1e9
    for d,a,k in allpts:
        if a<best_a: pareto.append((d,a,k)); best_a=a
    print("\nPareto (delay, area):"); [print(f"  {d*1000:6.0f}ps {a:6.1f}  {k}") for d,a,k in pareto]
    # OpenSTA on the best few + export
    os.makedirs("out",exist_ok=True)
    best={k:v for k,v in out.items()}
    for i,(d,a,fa,pp,ha,net) in enumerate(samples[:3]): best[f"rand{i}"]=(d,a,net)
    print("\nOpenSTA check of the best named + random:")
    chk=sorted(best.items(),key=lambda kv:kv[1][0])[:6]
    for k,(d,a,net) in chk:
        nm="as_"+k.replace('+','_'); v=f"out/{nm}.v"; open(v,"w").write(to_verilog(net,nm)); s=sta_delay(v,nm)
        print(f"  {k:22s} model={d*1000:6.0f}ps OpenSTA={s*1000 if s else float('nan'):6.0f}ps area={a:6.1f} cells={len(net.insts)}")
