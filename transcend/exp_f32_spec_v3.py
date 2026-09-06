"""Spec v3 (Python reference, integers): Estrin evaluation, x' kept as rows, same truncation rule (drop grid index < 0)."""
from exp_f32_gates import F, TB, D, GG, NT, LF, X0S, CF, L, X0, C, TBL, CFAC
def rowprod(a, fa, b, fb):      # Σ a_i · b · 2^(i-fa) truncated at 2^-GG, result at GG fraction bits
    s=0; sh=fa+fb-GG; i=0
    while a>0:
        if a&1: s += (b>>(sh-i)) if i<=sh else (b<<(i-sh))
        a>>=1; i+=1
    return s
K0 = (X0*C) >> (F+CF-20)                          # X0·C at 20 fraction bits
NEG = ((1<<35) - (-(-C >> 12))) % (1<<35)   # -(2^8·C) in 2^-20 units, rounded up in magnitude: cancels the complement row's 2^76 (s=1); u never exceeds the truth
CS = C >> (CF-20)                                  # C at 20 fraction bits (for the s·C row)
c1,c2,c3,c4,c5,c6 = [c<<8 for c in CFAC]           # 1/k! at GG=68 fraction bits
def trunc(v, keep): return (v >> (GG-keep)) << (GG-keep)   # keep `keep` fraction bits (as a 68-grid integer)
def exp_spec(xbits, B0=40):
    s=(xbits>>31)&1; e=(xbits>>23)&0xff; m=(xbits&0x7fffff)|0x800000
    xf=m<<(e-150+GG)                               # |x| at 68-grid (exact)
    A=xf ^ ((1<<76)-1 if s else 0)                 # field XOR s
    # u = A·C + K0 + s·C, rows truncated at 20 fraction bits (C bit i <-> 2^(i-40): (A<<i)>>(68+40-20))
    u=K0 + (NEG if s else 0); c=C; i=0          # (the complement's +1 LSB is 2^-68: negligible in u)
    while c>0:
        if c&1: u += (A<<i)>>(GG+CF-20)
        c>>=1; i+=1
    u%=1<<(8+20+7)                                 # the u tree keeps 35 columns (indices 48..82)
    n=u>>20; k=(n>>TB)-(1<<(X0S-TB)); j=n&(NT-1)
    # r = A + X0 + s − n·L  mod 2^62 (68-grid, 62 columns); L bit i <-> 2^(i-80), n bit b: index b+i-12
    nl=0; l=L; i=0
    while l>0:
        if l&1: nl += (n<<i)>>(LF-GG)
        l>>=1; i+=1
    r=(A + (X0<<8) + s - nl) % (1<<62)
    # Estrin: q=r², q4=q², B=c2+c3 r, Cq=(c4+c5 r)+q·c6, p = (1 + c1 r) + q·B + q4·Cq
    q  = rowprod(r, GG, r, GG)
    cr1= rowprod(c1, GG, r, GG); cr3=rowprod(c3, GG, r, GG); cr5=rowprod(c5, GG, r, GG)
    Bq = c2 + cr3
    qB = rowprod(q, GG, Bq, GG)
    qc6= rowprod(c6, GG, q, GG)
    Cq = c4 + cr5 + qc6
    q4 = rowprod(trunc(q,56), GG, trunc(q,56), GG)
    q4C= rowprod(trunc(q4,56), GG, trunc(Cq,30), GG)
    p  = (1<<GG) + cr1 + qB + q4C
    y  = rowprod(TBL[j], F, p, GG)
    B=B0
    if y >= (2<<GG): y>>=1; k+=1; B=(B>>1)+1
    if y < (1<<GG): y<<=1; k-=1; B<<=1
    y8=y>>8; B+=1
    tailbits=F-23; mant=y8>>tailbits; tail=y8&((1<<tailbits)-1); half=1<<(tailbits-1)
    dist=abs(tail-half); decided=dist>B
    up = tail>half or (tail==half and (mant&1))
    if up:
        mant+=1
        if mant==(1<<24): mant>>=1; k+=1
    return dict(bits=((k+127)<<23)|(mant&0x7fffff), decided=decided, dist=dist, k=k, j=j, n=n, r=r, q=q, p=p, y=y, A=A, u=u)
