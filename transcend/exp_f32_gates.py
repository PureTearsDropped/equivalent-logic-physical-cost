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

class Fx:
    """helper around a Net: nets with None = constant 0, ONE = constant 1 (a real net)"""
    def __init__(self, net): self.net=net; self._one=None
    def one(self):
        if self._one is None: a=self.net.add('inv_1',{'A':0})['Y']; self._one=self.net.add('or2_1',{'A':0,'B':a})['X']
        return self._one
    def AND(self,a,b):
        if a is None or b is None: return None
        if a==self._one: return b
        if b==self._one: return a
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
        cb=ColBuilder(self.net,W,'and2','xor+and','xor2x2+a21o')
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
    # (c) x' = X0 ± |x| mod 2^76: row A = field XOR s (field indices 0..75), + X0 (at F bits -> index+8), + s at index 68
    A=[(w, fx.XOR(xf.get(w),s) if w in xf else s) for w in range(76)]
    xp=fx.tree(A+fx.const_bits(X0,8)+[(68,s)],76)                          # binary x' (76 bits)
    xpb={w:n for w,n in enumerate(xp) if n is not None}
    _log('xp',net)
    # u = x'·C rows truncated at index 48 (2^-20); C bit i <-> 2^(i-40): index = w + i - 40
    ubits=[(w+i-40,n) for i in range(C.bit_length()) if (C>>i)&1 for w,n in xpb.items() if w+i-40>=48]
    u=fx.tree([(w-48,n) for w,n in ubits],35)                              # indices 48..82 -> local 0..34
    nbits={b:u[20+b] for b in range(14) if u[20+b] is not None}            # n = floor(u): local 20.. (index 68..81)
    j=[nbits.get(b) for b in range(6)]                                     # table index
    kn=[nbits.get(6+b) for b in range(8)]                                  # n >> 6 (8 bits); k = kn - 128
    _log('u/n',net)
    # (d) r = x'·2^8 − n·L mod 2^76, low 62 columns only. L bit i <-> 2^(i-81); n bit b at index 68+b: index b+i-13
    rows=[]; K1=0; NR=0
    for i in range(L.bit_length()):
        if not (L>>i)&1: continue
        NR+=1; mask=0
        for b in range(14):
            w=b+i-13
            if 0<=w<62:
                mask|=1<<w
                if b in nbits: rows.append((w,fx.INV(nbits[b])))
                else: rows.append((w,ONE))                                  # ~0 = 1 for absent (constant-0) n bits
        K1+=((1<<62)-1)^mask                                                # ones outside the window
    K1=(K1+NR)%(1<<62)
    rows+= [(w,n) for w,n in xpb.items() if w<62] + fx.const_bits(K1)
    r=fx.tree(rows,62); rb={w:n for w,n in enumerate(r) if n is not None}   # r binary, indices 0..61
    _log('r',net)
    # (e) Horner
    def trunc(bits,wp): return {w:n for w,n in bits.items() if w>=GG-wp}
    p=fx.const_bits(CFAC[D-1],8); p=fx.tree(p,70); pb={w:n for w,n in enumerate(p) if n is not None}
    for lvl in range(D-1,0,-1):
        wp=WP[lvl]                                                         # WP[lvl] = width for p_{lvl+1} (0-based list)
        prod=fx.rowprod(trunc(rb,wp),trunc(pb,wp),70)
        p=fx.tree(prod+fx.const_bits(CFAC[lvl-1],8),70); pb={w:n for w,n in enumerate(p) if n is not None}
        _log(f'horner lvl {lvl}',net)
    prod=fx.rowprod(rb,pb,70)
    p=fx.tree(prod+[(68,ONE)],70); pb={w:n for w,n in enumerate(p) if n is not None}
    # (f) table T[j] (61 bits at F=60 -> index+8) via mux2 trees on j
    tb={}
    for bit in range(61):
        vals=[(TBL[jj]>>bit)&1 for jj in range(NT)]
        if all(v==1 for v in vals): tb[bit+8]=ONE; continue
        if all(v==0 for v in vals): continue
        level=[ONE if v else None for v in vals]
        for t in range(TB):
            level=[fx.MUX(level[2*q],level[2*q+1],j[t]) for q in range(len(level)//2)]
        tb[bit+8]=level[0]
    _log('table',net)
    y=fx.tree(fx.rowprod(tb,pb,70),70); yb=y
    _log('y',net)
    # (g) normalize: hi = y[69], lo = ~y[69] & ~y[68]
    hi=yb[69]; lo=fx.AND(fx.INV(yb[69]),fx.INV(yb[68]))
    yn=[fx.MUX(fx.MUX(yb[w], yb[w-1] if w>=1 else None, lo), yb[w+1] if w+1<70 else None, hi) for w in range(69)]
    # (h) rounding: mant = indices 45..68, tail = 8..44 (37 bits), half = bit 44
    mant=yn[45:69]; tail=yn[8:45]; tmsb=tail[36]; rest=tail[:36]
    rest_nz=None
    for b in rest: rest_nz=fx.OR(rest_nz,b)
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
    ex=fx.tree([(b,kn[b]) for b in range(8)]+fx.const_bits(255)+[(0,hi),(0,co)]+[(w,ONE) for w in range(8)]+[(0,lo)],8)
    # note: −lo = +(~lo)+... handled as: add 255·lo? simpler: two's complement of lo = 2^8 - lo -> add (2^8-1) + (1 - lo) = 255 + ~lo ... see below
    net.outputs=mant2[:23]+ex+[None]+[decided]
    return net

if __name__=="__main__":
    import time; t0=time.time(); net=build_exp()
    print("cells:",len(net.insts),"build time %.0fs"%(time.time()-t0))
