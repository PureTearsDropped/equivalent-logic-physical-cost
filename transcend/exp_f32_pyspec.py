"""Python mirror of exp_f32_spec.jl (integers), returning intermediates for debugging the gate model."""
from exp_f32_gates import F, TB, D, GG, NT, LF, X0S, CF, L, X0, C, TBL, CFAC, WP
def rowprod(a, fa, b, fb):
    s=0; sh=fa+fb-GG; i=0
    while a>0:
        if a&1: s += (b>>(sh-i)) if i<=sh else (b<<(i-sh))
        a>>=1; i+=1
    return s
def exp_spec(xbits):
    s=(xbits>>31)&1; e=(xbits>>23)&0xff; m=(xbits&0x7fffff)|0x800000
    ee=e-150; xf=m<<(ee+F)
    xp=(X0 - xf) if s else (X0 + xf)
    u=0; c=C; i=0
    while c>0:
        if c&1: u += (xp<<i)>>(F+CF-20)
        c>>=1; i+=1
    n=u>>20; k=(n>>TB)-(1<<(X0S-TB)); j=n&(NT-1)
    nl=0; l=L; i=0
    while l>0:
        if l&1: nl += (n<<i)>>(LF-(F+8))
        l>>=1; i+=1
    r=(xp<<8)-nl
    p=CFAC[D-1]<<8; ps=[]
    for lvl in range(D-1,0,-1):
        wp=WP[lvl]; pt=p>>(F+8-wp); rt=r>>(F+8-wp)
        p=(CFAC[lvl-1]<<8)+rowprod(rt,wp,pt,wp); ps.append(p)
    p=(1<<(F+8))+rowprod(r,F+8,p,F+8)
    y=rowprod(TBL[j],F,p,F+8)
    return dict(xf=xf,xp=xp,u=u,n=n,k=k,j=j,r=r,ps=ps,p=p,y=y)
