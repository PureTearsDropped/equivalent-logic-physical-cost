"""Gate-level (sky130 cells) correctly-rounded binary32 exp, bit-exact with exp_f32_spec.jl.
Fixed point on a 68-bit fraction grid (F=60 + 8 guard): weight index w <-> 2^(w-68). All products are
partial-product rows truncated to indices >= 0 (the spec's per-row truncation); every intermediate that the
spec holds as an integer is resolved to binary with a Kogge-Stone adder (ColBuilder.resolve('ks'))."""
import sys, os, math
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'src'))
from fullcell import *
from arith_search import *
from rep_sweep import ColBuilder
from mpmath import mp, mpf, log, factorial
mp.prec = 300
F, TB, D, GG = 60, 6, 6, 68
NT = 1 << TB; LF = F + 12 + 8; X0S = 13; CF = 40
def R(v): return int(mp.nint(v))
L   = R(mpf(2)**LF * log(2) / NT)           # ln2/64 at LF=80 fraction bits
X0  = (L << X0S) >> (LF - F)                # 128·ln2 at F fraction bits (exact truncation, as the spec)
C   = R(mpf(2)**CF * NT / log(2))           # 64/ln2 at 40 fraction bits
TBL = [R(mpf(2)**F * mpf(2)**(mpf(j)/NT)) for j in range(NT)]
CFAC= [R(mpf(2)**F / factorial(m)) for m in range(1, D+1)]
WP  = [min(F, F - round(7.5*(k-1)) + 6) for k in range(1, D+1)]
B0  = 40
K0  = (X0*C) >> (F+CF-20)
NEG = ((1<<35) - (-(-C >> 12))) % (1<<35)
c1,c2,c3,c4,c5,c6 = [c<<8 for c in CFAC]

class Fx:
    """helper around a Net: nets with None = constant 0, ONE = constant 1 (a real net)"""
    def __init__(self, net): self.net=net; self._one=None; self._uses=0; self._ones=set()
    def one(self):
        if self._one is None or self._uses>=32:
            self._one=self.net.add('conb_1',{})['HI']; self._uses=0; self._ones=getattr(self,'_ones',set()); self._ones.add(self._one)
        self._uses+=1; return self._one
    def AND(self,a,b):
        if a is None or b is None: return None
        if a in self._ones: return b
        if b in self._ones: return a
        return self.net.add('and2_1',{'A':a,'B':b})['X']
    def OR(self,a,b):
        if a is None: return b
        if b is None: return a
        return self.net.add('or2_1',{'A':a,'B':b})['X']
    def XOR(self,a,b):
        if a is None: return b
        if b is None: return a
        return self.net.add('xor2_1',{'A':a,'B':b})['X']
    def INV(self,a):
        if a is None: return self.one()
        return self.net.add('inv_1',{'A':a})['Y']
    def MUX(self,a0,a1,s):   # s ? a1 : a0
        if s is None: return a0
        if a0 is None and a1 is None: return None
        if a0 is None: return self.AND(a1,s)
        if a1 is None: return self.AND(a0,self.INV(s))
        if a0==a1: return a0
        return self.net.add('mux2_1',{'A0':a0,'A1':a1,'S':s})['X']
    def const_bits(self,value,shift=0):
        """[(index, ONE)] for the 1-bits of an integer placed at index+shift"""
        return [(i+shift,self.one()) for i in range(value.bit_length()) if (value>>i)&1]
    def tree(self,bits,W):
        """sum of weighted bits (index,net) mod 2^W, resolved to binary: returns list of W nets"""
        cb=ColBuilder(self.net,W,'and2','xor+and','xor2x2+a21o'); cb.no_arrival=True
        for idx,n in bits:
            if n is not None and 0<=idx<W: cb.cols[idx].append(n)
        cb.reduce_to_2()
        for k in list(cb.cols):
            if k>=W: del cb.cols[k]
        return cb.resolve('ks')
    def rowprod(self,abits,bbits,W):
        """Σ a_i b_j at index i+j-68 (>=0), for binary operands given as {index:net}; returns tree bits (unresolved)"""
        out=[]
        for ia,na in abits.items():
            for ib,nb in bbits.items():
                w=ia+ib-GG
                if 0<=w<W: out.append((w,self.AND(na,nb)))
        return out

import time
_T0=time.time()
def _log(msg,net): print(f"[{time.time()-_T0:6.1f}s] {msg}: cells={len(net.insts)}",flush=True)
def build_exp():
    net=Net(16)                      # 32 primary inputs = bits of x
    fx=Fx(net); X=list(range(32)); s=X[31]; e=X[23:31]; m=X[0:23]
    ONE=fx.one()
    # (b) shift amount sh' = e - 102 (5 bits) : e + 154 mod 256
    sa=fx.tree([(i,e[i]) for i in range(8)]+fx.const_bits(154),8)[:5]
    # mantissa with hidden one; barrel left by sh' over a 55-bit bus; bus bit q sits at index q+20
    bus=m+[ONE]+[None]*31
    for t in range(5):
        step=1<<t; nb=[None]*55
        for q in range(55): nb[q]=fx.MUX(bus[q], bus[q-step] if q-step>=0 else None, sa[t])
        bus=nb
    xf={q+20:bus[q] for q in range(55) if bus[q] is not None}          # |x| at 68-grid (bits ≥ 2^-48)
    _log('barrel',net)
    # (c) x' rows: A = field XOR s (indices 0..75), constant X0 (index+8), +s at the field LSB (index 0)
    A=[(w, fx.XOR(xf.get(w),s) if w in xf else s) for w in range(76)]
    net.probes={'xf':xf}
    # u = A·C + K0 + s·NEG  (rows truncated at index 48 = 2^-20; 35 columns 48..82 -> local 0..34)
    ubits=[(w+i-40-48,n) for i in range(C.bit_length()) if (C>>i)&1 for w,n in A if w+i-40>=48]
    ubits+= [(b,ONE) for b in range(35) if (K0>>b)&1] + [(b,s) for b in range(35) if (NEG>>b)&1]
    u=fx.tree(ubits,35)
    nbits={b:u[20+b] for b in range(14) if u[20+b] is not None}            # n = floor(u)
    net.probes['u']={w:n for w,n in enumerate(u) if n is not None}; net.probes['n']=nbits
    j=[nbits.get(b) for b in range(6)]; kn=[nbits.get(6+b) for b in range(8)]
    _log('u/n',net)
    # (d) r = A + X0 + s − n·L mod 2^62 (68-grid, 62 columns). L bit i <-> 2^(i-80); n bit b: index b+i-12
    rows=[]; K1=0; NR=0
    for i in range(L.bit_length()):
        if not (L>>i)&1: continue
        NR+=1; mask=0
        for b in range(14):
            w=b+i-(LF-(F+8))
            if 0<=w<62:
                mask|=1<<w
                rows.append((w, fx.INV(nbits[b]) if b in nbits else ONE))
        K1+=((1<<62)-1)^mask
    K1=(K1+NR+(X0<<8))%(1<<62)
    rows+= [(w,n) for w,n in A if w<62] + [(0,s)] + fx.const_bits(K1)
    r=fx.tree(rows,62); rb={w:n for w,n in enumerate(r) if n is not None}
    net.probes['r']=rb
    _log('r',net)
    # (e) Estrin: q=r², cr_k = c_k·r, B=c2+cr3, Cq=(c4+cr5)+q·c6, q4=q², p = (1+cr1) + q·B + q4·Cq
    def resolve(bits,W=70):
        t=fx.tree(bits,W); return {w:n for w,n in enumerate(t) if n is not None}
    def cbits(v): return {w:ONE for w in range(v.bit_length()) if (v>>w)&1}      # constant as {index:ONE}
    def cprod(cv,xb):  # constant × signal: rows only for the constant's 1-bits
        return [(i+w-GG,n) for i in range(cv.bit_length()) if (cv>>i)&1 for w,n in xb.items() if i+w-GG>=0]
    def keep(bits,k): return {w:n for w,n in bits.items() if w>=GG-k}
    q=resolve(fx.rowprod(rb,rb,70));                       net.probes['q']=q; _log('q',net)
    cr1=resolve(cprod(c1,rb)); cr3=resolve(cprod(c3,rb)); cr5=resolve(cprod(c5,rb))
    Bq=resolve([(w,n) for w,n in cr3.items()]+fx.const_bits(c2))
    qB=resolve(fx.rowprod(q,Bq,70))
    qc6=resolve(cprod(c6,q))
    Cq=resolve([(w,n) for w,n in cr5.items()]+[(w,n) for w,n in qc6.items()]+fx.const_bits(c4))
    q4=resolve(fx.rowprod(keep(q,56),keep(q,56),70));      _log('q4',net)
    q4C=resolve(fx.rowprod(keep(q4,56),keep(Cq,30),70))
    p=resolve([(w,n) for w,n in cr1.items()]+[(w,n) for w,n in qB.items()]+[(w,n) for w,n in q4C.items()]+[(68,ONE)])
    pb=p; net.probes['p']=pb; _log('p',net)
    # (f) table T[j] (61 bits at F=60 -> index+8) via mux2 trees on j
    tb={}
    for bit in range(61):
        vals=[(TBL[jj]>>bit)&1 for jj in range(NT)]
        if all(v==1 for v in vals): tb[bit+8]=ONE; continue
        if all(v==0 for v in vals): continue
        level=[ONE if v else None for v in vals]
        for t in range(TB):
            level=[fx.MUX(level[2*qq],level[2*qq+1],j[t]) for qq in range(len(level)//2)]
        tb[bit+8]=level[0]
    _log('table',net)
    y=fx.tree(fx.rowprod(tb,pb,70),70); yb=y
    net.probes['T']=tb; net.probes['y']={w:n for w,n in enumerate(y) if n is not None}
    _log('y',net)
    # (g) normalize: hi = y[69], lo = ~y[69] & ~y[68]
    hi=yb[69]; lo=fx.AND(fx.INV(yb[69]),fx.INV(yb[68]))
    yn=[fx.MUX(fx.MUX(yb[w], yb[w-1] if w>=1 else None, lo), yb[w+1] if w+1<70 else None, hi) for w in range(69)]
    # (h) rounding: mant = indices 45..68, tail = 8..44 (37 bits), half = bit 44
    mant=yn[45:69]; tail=yn[8:45]; tmsb=tail[36]; rest=tail[:36]
    lvl=[b for b in rest if b is not None]
    while len(lvl)>1: lvl=[fx.OR(lvl[i],lvl[i+1]) if i+1<len(lvl) else lvl[i] for i in range(0,len(lvl),2)]
    rest_nz=lvl[0] if lvl else None
    gt=fx.AND(tmsb,rest_nz); eq=fx.AND(tmsb,fx.INV(rest_nz)); up=fx.OR(gt,fx.AND(eq,mant[0]))
    # decided: tail outside [half-B, half+B] with B = {hi:21, lo:81, else:41} (+1 for the guard-bit drop)
    def ge_const(bits,c,W):   # bits (list, LSB first, W wide) >= c  : carry out of bits + (2^W - c)
        t=fx.tree([(w,bits[w]) for w in range(W)]+fx.const_bits((1<<W)-c),W+1); return t[W]
    half=1<<36; dec=None
    for cond,Bv in ((hi,21),(lo,81),(None,41)):
        inside=fx.AND(ge_const(tail,half-Bv,37), fx.INV(ge_const(tail,half+Bv+1,37)))
        d=fx.INV(inside)
        dec = d if cond is None else fx.MUX(dec,d,cond) if dec is not None else d
    # order: default 41 first then override by lo/hi
    d41=fx.INV(fx.AND(ge_const(tail,half-41,37), fx.INV(ge_const(tail,half+42,37))))
    d81=fx.INV(fx.AND(ge_const(tail,half-81,37), fx.INV(ge_const(tail,half+82,37))))
    d21=fx.INV(fx.AND(ge_const(tail,half-21,37), fx.INV(ge_const(tail,half+22,37))))
    decided=fx.MUX(fx.MUX(d41,d81,lo),d21,hi)
    # mant + up (24 bits) -> carry out means mant became 2^24
    mi=fx.tree([(b,mant[b]) for b in range(24)]+[(0,up)],25); co=mi[24]
    mant2=[fx.MUX(mi[b], ONE if b==23 else None, co) for b in range(24)]   # on carry-out: 1000…0
    # exponent field = kn - 128 + 127 + hi - lo + co = kn - 1 + hi - lo + co  (mod 256)
    ex=fx.tree([(b,kn[b]) for b in range(8)]+fx.const_bits(255)+[(0,hi),(0,co)]+[(w,lo) for w in range(8)],8)   # kn - 1 + hi + co - lo (mod 256)
    net.outputs=mant2[:23]+ex+[None]+[decided]
    return net

if __name__=="__main__":
    import time, pickle; t0=time.time(); net=build_exp(); buffer_high_fanout(net)
    print("cells:",len(net.insts),"build time %.0fs"%(time.time()-t0),flush=True)
    pickle.dump(net,open('/tmp/claude-1001/exp_net.pkl','wb'))
    from check_gates import check
    check(net,'/tmp/claude-1001/exp_vectors_v3.txt',4000)

def to_verilog_exp(net, name):
    """ports: input [31:0] x; output [31:0] y (sign bit 0); output decided"""
    nm={i:f"x[{i}]" for i in range(32)}
    outs=net.outputs
    for k in range(31):
        if outs[k] is not None: nm[outs[k]]=f"y[{k}]"
    if outs[32] is not None: nm[outs[32]]="decided"
    wires=[f"n{i}" for i in range(32,net.nnets) if i not in nm]
    for i in range(32,net.nnets): nm.setdefault(i,f"n{i}")
    L=[f"module {name}(input [31:0] x, output [31:0] y, output decided);","  wire "+", ".join(wires)+";"]
    for ii,inst in enumerate(net.insts):
        conns=[f".{p}({nm[q]})" for p,q in inst['pins'].items()]+[f".{p}({nm[q]})" for p,q in inst['outs'].items()]
        L.append(f"  sky130_fd_sc_hd__{inst['cell']} g{ii} ({', '.join(conns)});")
    ties=[f"y[{k}]" for k in range(32) if k==31 or outs[k] is None]
    for j,t in enumerate(ties): L.append(f"  sky130_fd_sc_hd__conb_1 tc{j} (.LO({t}), .HI());")
    L.append("endmodule"); return "\n".join(L)+"\n"
