# exp_f32_spec.jl — bit-exact *specification model* of the fixed-point exp datapath (what the gates compute).
# Every product is a sum of partial-product rows truncated per row at a column G (drop bits of weight < 2^-G),
# exactly as a compression tree that omits those columns; every operand truncation is a right shift.
# Parameters: F fraction bits, table of 2^TB entries, Taylor degree D, per-level operand widths.
using Base.Threads
const F  = 60                 # fraction bits of the main grid
const TB = 6                  # 64-entry table 2^(j/64): |r| < ln2/128 ≈ 2^-7.5
const D  = 6                  # Taylor degree: r^7/7! < 2^-65
const G  = F + 8              # partial-product rows truncated at 2^-G (8 guard bits)
setprecision(BigFloat, 200)
const NT = 1 << TB
const X0_SHIFT = 12           # X0 = 2^X0_SHIFT · L, L = ln2/NT rounded to F+X0_SHIFT+8 fraction bits (so X0 exact at F+8)
const LF = F + X0_SHIFT + 8
const L  = round(Int128, BigFloat(2)^LF * log(BigFloat(2)) / NT)          # ln2/64 at LF bits
const X0 = L << X0_SHIFT                                                    # = 4096·L (exact), 2^X0_SHIFT·NT/… >> covers |x| ≤ 87.34: X0 ≈ 44.36? see below
# bias must exceed |x|max = 87.34: X0 = 4096·ln2/64 = 64·ln2 = 44.36 — too small; use X0 = 8192·L = 88.72
const X0S = 13
const X0b = L << X0S                                                        # 8192·L = 128·ln2 ≈ 88.72 > 87.34 ✓ (LF fraction bits)
const CF = 40
const C  = round(Int128, BigFloat(2)^CF * NT / log(BigFloat(2)))            # 64/ln2 at CF bits
# exact binary32 range limits: largest x with RNE(exp x) finite, smallest x with a normal result
function _limits()
    xhi = 88.72283905206835f0; while !isinf(Float32(exp(BigFloat(xhi)))); xhi = nextfloat(xhi); end; xhi = prevfloat(xhi)
    xlo = -87.33654475055310f0; while Float32(exp(BigFloat(xlo))) < 2f0^-126; xlo = nextfloat(xlo); end
    (xlo, xhi)
end
const XLO, XHI = _limits()
const TBL = [round(Int128, BigFloat(2)^F * BigFloat(2)^(j/BigFloat(NT))) for j in 0:NT-1]
const CFAC = [round(Int128, BigFloat(2)^F / factorial(BigFloat(m))) for m in 1:D]
# operand widths per Horner level: r·p_k needs absolute 2^-F·2^{7.5(k-1)}; keep some margin (+6 bits)
const WP = [min(F, F - round(Int, 7.5*(k-1)) + 6) for k in 1:D]            # fraction bits kept of p_k (k = level)

# product of a binary operand (bits of `a`, lowest weight 2^-fa) with a value b (fraction bits fb), rows truncated at G:
# result has fraction bits G.  Model: Σ_i a_i · ((b << i) >> (fa + fb - G))  — per-row truncation.
function rowprod(a::Int128, fa::Int, b::Int128, fb::Int)
    s = Int128(0); sh = fa + fb - G
    i = 0
    while a > 0
        if (a & 1) == 1; s += (i <= sh ? b >> (sh - i) : b << (i - sh)); end   # = (b<<i)>>sh without overflow
        a >>= 1; i += 1
    end
    s
end

"""(bits32, decided, kind, dist): dist = distance to nearest midpoint in units of 2^-F (for margin statistics)"""
function exp_spec(x::Float32)
    if isnan(x); return (reinterpret(UInt32, x), true, :nan, Int128(0)); end
    if x > XHI; return (0x7f7fffff, true, :ovf, Int128(0)); end
    if x < XLO; return (0x00800000, true, :unf, Int128(0)); end
    ax = abs(x)
    if ax < 2f0^-25; return (reinterpret(UInt32, 1f0), true, :one, Int128(0)); end
    s = x < 0
    m = Int128(reinterpret(UInt32, ax) & 0x007fffff | 0x00800000); e = Int((reinterpret(UInt32, ax) >> 23) & 0xff) - 150
    # |x| at F fraction bits (exact): shift = e + F ∈ [35, 66] → barrel
    xf = m << (e + F)
    # x' = X0 ± |x|  (mod 2^W) built from rows: (xf XOR s-mask), constant X0, +s.  Here as an exact integer:
    W = F + 8   # x' < 2^8 (177): integer bits 8
    xp = s ? (X0b >> (LF - F)) - xf : (X0b >> (LF - F)) + xf      # X0 at F bits: X0b has LF fraction bits, exact truncation
    @assert xp > 0
    # u = x'·C, rows truncated at 2^-20 (only floor needed, error < 3 rows·2^-20)
    u = Int128(0); c = C; i = 0
    while c > 0
        if (c & 1) == 1; u += (xp << i) >> (F + CF - 20); end
        c >>= 1; i += 1
    end
    n = Int(u >> 20)                                  # floor(x'·C) ≥ 0
    haskey(ENV,"DBG") && println("xp=", Float64(xp)/2.0^F, " u=", Float64(u)/2.0^20, " n=", n)
    k = (n >> TB) - (1 << (X0S - TB))                 # n' = n - 8192·… : X0 = 8192·L = 2^(13-6)=128 table periods
    j = n & (NT - 1)
    # r = x' − n·L  at F+8 bits: rows (n << i) for 1-bits of L, truncated at 2^-(F+8); L has LF fraction bits
    nl = Int128(0); l = L; i = 0
    while l > 0
        if (l & 1) == 1; nl += (Int128(n) << i) >> (LF - (F + 8)); end
        l >>= 1; i += 1
    end
    r = (xp << 8) - nl                                # F+8 fraction bits; expect 0 ≤ r < L(1+tiny)
    haskey(ENV,"DBG") && println("k=", k, " j=", j, " r=", Float64(r)/2.0^(F+8), " L=", Float64(L)/2.0^LF)
    @assert r >= 0
    # Horner with per-level operand widths; p_k kept at F+8 fraction bits, operands truncated to WP[k] fraction bits
    p = CFAC[D] << 8
    for lvl in D-1:-1:1
        wp = WP[lvl+1]                                # width of the multiplicand p_{lvl+1}
        pt = p >> (F + 8 - wp)                        # p_{lvl+1} truncated to wp fraction bits
        rt = r >> (F + 8 - wp)                        # r truncated to the same width
        prod = rowprod(rt, wp, pt, wp)                # fraction bits G = F+8
        p = (CFAC[lvl] << 8) + prod
    end
    prod = rowprod(r, F + 8, p, F + 8)                # full-width final term r·p_1 (rows truncated at G)
    p = (Int128(1) << (F + 8)) + prod                 # e^r at F+8 bits
    # y = T[j]·p : T at F bits (binary), p at F+8 → rows truncated at G → y at F+8 fraction bits
    y = rowprod(TBL[j+1], F, p, F + 8)
    # error bound in units of 2^-F (conservative, see notes): 
    B = Int128(40)
    haskey(ENV,"DBG") && println("p=", Float64(p)/2.0^(F+8), " y=", Float64(y)/2.0^(F+8), " T=", Float64(TBL[j+1])/2.0^F)
    # normalize
    if y >= (Int128(2) << (F + 8)); y >>= 1; k += 1; B = (B >> 1) + 1; end
    if y < (Int128(1) << (F + 8)); y <<= 1; k -= 1; B <<= 1; end
    if k > 127; return (0x7f7fffff, true, :ovf, Int128(0)); end
    if k < -126; return (0x00800000, true, :unf, Int128(0)); end
    y8 = y >> 8                                       # back to F fraction bits (drop guard bits: error ≤ 1 unit)
    B += 1
    tailbits = F - 23
    mant = Int64(y8 >> tailbits); tail = y8 & ((Int128(1) << tailbits) - 1); half = Int128(1) << (tailbits - 1)
    dist = abs(tail - half)
    decided = dist > B
    up = tail > half || (tail == half && isodd(mant))
    if up; mant += 1; if mant == (1 << 24); mant >>= 1; k += 1; end; end
    ((UInt32(k + 127) << 23) | (UInt32(mant) & 0x007fffff), decided, :normal, dist)
end
reference(x::Float32) = Float32(exp(BigFloat(x)))

function sweep()
    nt = nthreads(); mism = zeros(Int, nt); undec = zeros(Int, nt); cnt = zeros(Int, nt); mind = fill(typemax(Int128), nt); minx = zeros(Float32, nt)
    @threads for t in 1:nt
        for b in UInt32(t-1):UInt32(nt):UInt32(0xffffffff)
            x = reinterpret(Float32, b)
            (isnan(x) || isinf(x)) && continue
            (x > XHI || x < XLO || abs(x) < 2f0^-25) && continue
            bits, decided, kind, dist = exp_spec(x); cnt[t] += 1
            if dist < mind[t]; mind[t] = dist; minx[t] = x; end
            if !decided; undec[t] += 1; continue; end
            bits != reinterpret(UInt32, reference(x)) && (mism[t] += 1)
        end
    end
    i = argmin(mind)
    println("checked=", sum(cnt), " mismatches=", sum(mism), " undecided=", sum(undec), " min_midpoint_distance=", mind[i], " units of 2^-", F, " at x=", minx[i])
end
function dump_vectors(n::Int, path::String)
    import_random = Base.require(Main, :Random); rng = import_random.MersenneTwister(7)
    open(path, "w") do io
        while n > 0
            b = rand(rng, UInt32); x = reinterpret(Float32, b)
            (isnan(x) || x > XHI || x < XLO || abs(x) < 2f0^-25) && continue
            bits, dec, kind, dist = exp_spec(x); println(io, string(b, base=16), " ", string(bits, base=16), " ", dec ? 1 : 0); n -= 1
        end
    end
end
if length(ARGS) > 0 && ARGS[1] == "vectors"      # dump random test vectors for the gate model: hex(x) hex(result) decided
    dump_vectors(parse(Int, ARGS[2]), ARGS[3])
elseif length(ARGS) > 0 && ARGS[1] == "sweep"
    @time sweep()
else
    for x in Float32[1, -1, 0.5, 88.0, -87.0, 2f0^-24, -2f0^-24, 3.14159f0, 1f-3, 42.42f0, -0.1f0, 10.5f0]
        bits, dec, kind, dist = exp_spec(x)
        println(x, " -> ", reinterpret(Float32, bits), " ref=", reference(x), " decided=", dec, " dist=", dist, " ", bits == reinterpret(UInt32, reference(x)) ? "OK" : "MISMATCH")
    end
    println("WP = ", WP)
end
