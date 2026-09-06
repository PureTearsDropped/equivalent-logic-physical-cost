# Spec v3 (Julia, for the exhaustive MPFR sweep) — must match exp_f32_spec_v3.py integer for integer.
using Base.Threads
const F=60; const TB=6; const D=6; const GG=68; const NT=1<<TB; const LF=F+12+8; const X0S=13; const CF=40
setprecision(BigFloat, 300)
R(v)=round(Int128, v)
const L  = R(BigFloat(2)^LF * log(BigFloat(2)) / NT)
const X0 = (L << X0S) >> (LF - F)
const C  = R(BigFloat(2)^CF * NT / log(BigFloat(2)))
const TBL= [R(BigFloat(2)^F * BigFloat(2)^(j/BigFloat(NT))) for j in 0:NT-1]
const CFAC=[R(BigFloat(2)^F / factorial(BigFloat(m))) for m in 1:D]
const K0 = (X0*C) >> (F+CF-20)
const CS = C >> (CF-20)
const c1=CFAC[1]<<8; const c2=CFAC[2]<<8; const c3=CFAC[3]<<8; const c4=CFAC[4]<<8; const c5=CFAC[5]<<8; const c6=CFAC[6]<<8
const NEG = mod((Int128(1)<<35) - cld(C, Int128(1)<<12), Int128(1)<<35)
function rowprod(a::Int128, fa::Int, b::Int128, fb::Int)
    s=Int128(0); sh=fa+fb-GG; i=0
    while a>0
        if (a&1)==1; s += (i<=sh ? b>>(sh-i) : b<<(i-sh)); end
        a>>=1; i+=1
    end
    s
end
trunc68(v::Int128, keep::Int) = (v >> (GG-keep)) << (GG-keep)
function _limits()
    xhi = 88.72283905206835f0; while !isinf(Float32(exp(BigFloat(xhi)))); xhi = nextfloat(xhi); end; xhi = prevfloat(xhi)
    xlo = -87.33654475055310f0; while Float32(exp(BigFloat(xlo))) < 2f0^-126; xlo = nextfloat(xlo); end
    (xlo, xhi)
end
const XLO, XHI = _limits()
function exp_spec(x::Float32; B0::Int128=Int128(40))
    if x > XHI; return (0x7f7fffff, true, Int128(0)); end
    if x < XLO; return (0x00800000, true, Int128(0)); end
    ax=abs(x); if ax < 2f0^-25; return (reinterpret(UInt32,1f0), true, Int128(0)); end
    bits=reinterpret(UInt32,x); s=Int((bits>>31)&1); e=Int((bits>>23)&0xff); m=Int128(bits&0x7fffff|0x800000)
    xf = m << (e-150+GG)
    A = xf ⊻ (s==1 ? (Int128(1)<<76)-1 : Int128(0))
    u = K0 + (s==1 ? NEG : Int128(0)); c=C; i=0
    while c>0
        if (c&1)==1; u += (A<<i)>>(GG+CF-20); end
        c>>=1; i+=1
    end
    u = mod(u, Int128(1)<<35)
    n = Int(u>>20); k=(n>>TB)-(1<<(X0S-TB)); j=n&(NT-1)
    nl=Int128(0); l=L; i=0
    while l>0
        if (l&1)==1; nl += (Int128(n)<<i)>>(LF-GG); end
        l>>=1; i+=1
    end
    r = mod(A + (X0<<8) + s - nl, Int128(1)<<62)
    q  = rowprod(r,GG,r,GG)
    cr1= rowprod(c1,GG,r,GG); cr3=rowprod(c3,GG,r,GG); cr5=rowprod(c5,GG,r,GG)
    Bq = c2+cr3; qB=rowprod(q,GG,Bq,GG); qc6=rowprod(c6,GG,q,GG); Cq=c4+cr5+qc6
    q4 = rowprod(trunc68(q,56),GG,trunc68(q,56),GG)
    q4C= rowprod(trunc68(q4,56),GG,trunc68(Cq,30),GG)
    p  = (Int128(1)<<GG) + cr1 + qB + q4C
    y  = rowprod(TBL[j+1],F,p,GG)
    B=B0
    if y >= (Int128(2)<<GG); y>>=1; k+=1; B=(B>>1)+1; end
    if y < (Int128(1)<<GG); y<<=1; k-=1; B<<=1; end
    y8=y>>8; B+=1
    tailbits=F-23; mant=Int64(y8>>tailbits); tail=y8&((Int128(1)<<tailbits)-1); half=Int128(1)<<(tailbits-1)
    dist=abs(tail-half); decided=dist>B
    up = tail>half || (tail==half && isodd(mant))
    if up; mant+=1; if mant==(1<<24); mant>>=1; k+=1; end; end
    ((UInt32(k+127)<<23) | (UInt32(mant)&0x007fffff), decided, dist)
end
reference(x::Float32)=Float32(exp(BigFloat(x)))
function sweep()
    nt=nthreads(); mism=zeros(Int,nt); undec=zeros(Int,nt); cnt=zeros(Int,nt); mind=fill(typemax(Int128),nt); minx=zeros(Float32,nt)
    @threads for t in 1:nt
        for b in UInt32(t-1):UInt32(nt):UInt32(0xffffffff)
            x=reinterpret(Float32,b); (isnan(x)||isinf(x)) && continue
            (x>XHI || x<XLO || abs(x)<2f0^-25) && continue
            bits,dec,dist=exp_spec(x); cnt[t]+=1
            if dist<mind[t]; mind[t]=dist; minx[t]=x; end
            if !dec; undec[t]+=1; continue; end
            bits!=reinterpret(UInt32,reference(x)) && (mism[t]+=1)
        end
    end
    i=argmin(mind); println("checked=",sum(cnt)," mismatches=",sum(mism)," undecided=",sum(undec)," min_midpoint_distance=",mind[i]," units of 2^-",F," at x=",minx[i])
end
function dump_vectors(n::Int, path::String)
    rng=Base.require(Main,:Random).MersenneTwister(7)
    open(path,"w") do io
        while n>0
            b=rand(rng,UInt32); x=reinterpret(Float32,b)
            (isnan(x)||x>XHI||x<XLO||abs(x)<2f0^-25) && continue
            bits,dec,dist=exp_spec(x); println(io,string(b,base=16)," ",string(bits,base=16)," ",dec ? 1 : 0); n-=1
        end
    end
end
if length(ARGS)>0 && ARGS[1]=="sweep"; @time sweep()
elseif length(ARGS)>0 && ARGS[1]=="vectors"; dump_vectors(parse(Int,ARGS[2]),ARGS[3])
else
    for x in Float32[1,-1,0.5,88.0,-87.0,2f0^-24,-2f0^-24,3.14159f0,1f-3,42.42f0,-0.1f0,10.5f0]
        bits,dec,dist=exp_spec(x); println(x," -> ",reinterpret(Float32,bits)," ref=",reference(x)," ",bits==reinterpret(UInt32,reference(x)) ? "OK" : "MISMATCH"," dist=",dist)
    end
end
function dump_all(path::String)
    open(path, "w") do io
        n = 0
        for b in UInt32(0):UInt32(0xffffffff)
            x = reinterpret(Float32, b); (isnan(x) || isinf(x)) && continue
            (x > XHI || x < XLO || abs(x) < 2f0^-25) && continue
            bits, dec, dist = exp_spec(x); write(io, b); write(io, bits); n += 1
        end
        println("wrote ", n, " pairs")
    end
end
if length(ARGS) > 0 && ARGS[1] == "dumpall"; @time dump_all(ARGS[2]); end
