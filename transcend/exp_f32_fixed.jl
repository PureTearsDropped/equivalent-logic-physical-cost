# exp_f32_fixed.jl — correctly rounded binary32 exp as a *fixed-point, single-pass* datapath (hardware model)
# with Ziv's decision at the exit, checked exhaustively against MPFR.
#
#   x = 2^k · 2^(j/32) · e^r,   n = round(x·32/ln2), k = n ÷ 32, j = n mod 32, r = x − n·(ln2/32), |r| ≤ ln2/64 (+slack)
#   e^r ≈ 1 + r + r²/2 + … + r^6/720   (fixed point, F fraction bits, truncations counted)
#   y = T[j]·p(r) ∈ [1, 2.03),  T[j] = 2^(j/32) at F bits
#   result = RNE(y·2^k) to 24 bits, decided iff the working value is farther than the error bound B from the
#   nearest rounding midpoint (Ziv). No fallback stage: for binary32 the exhaustive sweep shows whether any
#   input is left undecided at this F.
using Base.Threads
const F = 60                      # fraction bits of the fixed-point grid (products must fit Int128)
const N_TERMS = 6                 # Taylor degree
const ONE = Int128(1) << F
setprecision(BigFloat, 160)
const LN2_32 = round(Int128, BigFloat(2)^(F+16) * log(BigFloat(2)) / 32)      # ln2/32 at F+16 bits
const CF = 40                     # fraction bits of 32/ln2 (only the integer n = round(x·32/ln2) is used)
const INV_LN2_32 = round(Int128, BigFloat(2)^CF * 32 / log(BigFloat(2)))       # 32/ln2 at CF bits
const TBL = [round(Int128, BigFloat(2)^F * BigFloat(2)^(j/BigFloat(32))) for j in 0:31]   # 2^(j/32) at F bits
const INV_FACT = [round(Int128, BigFloat(2)^F / factorial(BigFloat(n))) for n in 1:N_TERMS]

# fixed-point helpers (truncating): (a·b) >> F, exact in Int128 for |a|,|b| < 2^63
fmul(a::Int128, b::Int128) = (a * b) >> F          # arithmetic shift = floor

"""returns (bits32, decided, kind) — kind: :normal, :one (|x| tiny), :ovf, :unf"""
function exp_fixed(x::Float32)
    if isnan(x); return (reinterpret(UInt32, x), true, :nan); end
    if x > 88.72283905206835f0; return (0x7f7fffff, true, :ovf); end      # > MAX: saturate (⟦≥⟧ in total-arith)
    if x < -87.33654475055310f0; return (0x00800000, true, :unf); end     # result subnormal: out of scope here
    ax = abs(x)
    if ax < 2f0^-25; return (reinterpret(UInt32, 1f0), true, :one); end   # exp(x) rounds to 1 (proved separately)
    # x as fixed point (exact: 24-bit mantissa, exponent ≥ −25 ⇒ ≤ 48 fraction bits)
    xm = Int128(reinterpret(UInt32, ax) & 0x007fffff | 0x00800000); xe = Int((reinterpret(UInt32, ax) >> 23) & 0xff) - 127 - 23
    xf = xe >= 0 ? xm << xe : xm << (F + xe)            # if xe<0: xm·2^xe·2^F = xm << (F+xe)  (F+xe ≥ 16)
    if xe >= 0; xf <<= F; end
    if x < 0; xf = -xf; end
    # n = round(x·32/ln2)
    u = (xf * INV_LN2_32) >> CF                           # x·32/ln2 at F bits (trunc; x·2^F·C·2^CF < 2^127)
    n = Int((u + (ONE >> 1)) >> F)                        # round half up (any consistent rounding is fine)
    k = fld(n, 32); j = mod(n, 32)
    # r = x − n·ln2/32  (n·LN2_32 has F+16 bits; align)
    r = xf - ((Int128(n) * LN2_32) >> 16)                 # truncation ≤ 1 unit of 2^-F, plus LN2_32 rounding n·2^-(F+16)
    # Horner: p = 1 + r(1 + r(1/2 + r(1/6 + …)))
    p = INV_FACT[N_TERMS]
    for m in N_TERMS-1:-1:1
        p = INV_FACT[m] + fmul(r, p)
    end
    p = ONE + fmul(r, p)                                  # e^r at F bits
    y = fmul(TBL[j+1], p)                                 # ∈ [2^F, ~2.03·2^F)
    # error bound in units of 2^-F (conservative, counted): see below
    B = Int128(32)                                        # counted: r 2 + Horner 6 + Taylor tail 4 + table 1 + product 1, ×TBL<2, margin
    # normalize to [1,2): y ≥ 2·2^F ⇒ shift right 1, k += 1
    if y >= (ONE << 1); y >>= 1; k += 1; B = (B >> 1) + 1; end
    if y < ONE; y <<= 1; k -= 1; B <<= 1; end                 # j = 0, r < 0 ⇒ y ∈ [e^{-ln2/64}, 1)
    e = k                                                 # result exponent (value = y·2^-F · 2^k)
    if e > 127; return (0x7f7fffff, true, :ovf); end
    if e < -126; return (0x00800000, true, :unf); end
    # RNE to 24 bits: keep top 24 bits of y (bit F is the leading 1), tail = lower F-23 bits
    tailbits = F - 23
    mant = Int64(y >> tailbits)                           # 24-bit integer with leading 1 (2^23 ≤ mant < 2^24)
    tail = y & ((ONE >> 23) - 1)                          # F-23 = 41 bits
    half = Int128(1) << (tailbits - 1)
    decided = abs(tail - half) > B                        # farther than B from the midpoint
    up = tail > half || (tail == half && isodd(mant))
    if up; mant += 1; if mant == (1 << 24); mant >>= 1; e += 1; end; end
    bits = (UInt32(e + 127) << 23) | (UInt32(mant) & 0x007fffff)
    return (bits, decided, :normal)
end

function reference(x::Float32)
    Float32(exp(BigFloat(x)))     # MPFR at 160 bits, then RNE to binary32
end

function sweep()
    lo = reinterpret(UInt32, -87.33654f0); hi = reinterpret(UInt32, 88.72283f0)
    # enumerate all binary32 bit patterns whose value lies in the normal-output range, excluding tiny |x|
    nt = nthreads(); mism = zeros(Int, nt); undec = zeros(Int, nt); cnt = zeros(Int, nt); examples = [Float32[] for _ in 1:nt]
    @threads for t in 1:nt
        for b in UInt32(t-1):UInt32(nt):UInt32(0xffffffff)
            x = reinterpret(Float32, b)
            (isnan(x) || isinf(x)) && continue
            (x > 88.72283905206835f0 || x < -87.33654475055310f0) && continue
            abs(x) < 2f0^-25 && continue
            bits, decided, kind = exp_fixed(x)
            cnt[t] += 1
            if !decided; undec[t] += 1; length(examples[t]) < 5 && push!(examples[t], x); continue; end
            if bits != reinterpret(UInt32, reference(x)); mism[t] += 1; length(examples[t]) < 5 && push!(examples[t], x); end
        end
    end
    println("checked=", sum(cnt), " mismatches=", sum(mism), " undecided=", sum(undec))
    for ex in examples; for x in ex; println("  example x=", x, " ours=", reinterpret(Float32, exp_fixed(x)[1]), " ref=", reference(x)); end; end
end

# quick spot checks
for x in Float32[1, -1, 0.5, 88.0, -87.0, 2f0^-24, -2f0^-24, 3.14159f0, 1f-3, 42.42f0]
    bits, dec, kind = exp_fixed(x)
    println(x, " -> ", reinterpret(Float32, bits), " ref=", reference(x), " decided=", dec, " ", kind, " ", bits == reinterpret(UInt32, reference(x)) ? "OK" : "MISMATCH")
end
if length(ARGS) > 0 && ARGS[1] == "sweep"; @time sweep(); end
