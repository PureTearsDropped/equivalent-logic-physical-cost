import ArithEquiv
/-!
# Signed-digit (borrow-save) arithmetic on two rails (core Lean 4, no Mathlib)

A signed digit d ∈ {−1,0,+1} is encoded as a pair of bits (p, n) with value `p − n`
(total-arith-hardware's `(p,n)` encoding; `(1,1)` is the redundant zero of borrow-save form).
A number is two rails of weighted bits: value = wval P − wval N (as an integer).
Because each rail is an ordinary unsigned bit set, **any** FA/HA compression schedule applied to a rail
preserves the value (ArithEquiv.schedule_preserves), so the two-rail value is preserved by any pair of
schedules — no per-step canonicalisation is needed for exactness. The canonical 3:2 compressor of
`sd2_gates.py` (two full adders + rail subtraction) is also proved value-preserving and canonical.
-/
namespace SignedDigit
open ArithEquiv

/-- value of a two-rail (borrow-save) number -/
def sdval (P N : List (Nat × Bool)) : Int := (wval P : Int) - (wval N : Int)

/-- two schedules, one per rail, preserve the signed value -/
theorem two_rail_preserves {P₀ P₁ N₀ N₁ : List (Nat × Bool)}
    (sp : Schedule P₀ P₁) (sn : Schedule N₀ N₁) : sdval P₀ N₀ = sdval P₁ N₁ := by
  unfold sdval; rw [schedule_preserves sp, schedule_preserves sn]

/-- digit product on rails: (xp − xn)(yp − yn) = (xp·yp + xn·yn) − (xp·yn + xn·yp) -/
theorem digit_product (xp xn yp yn : Bool) :
    ((xp.toNat : Int) - xn.toNat) * ((yp.toNat : Int) - yn.toNat)
      = ((xp && yp).toNat + (xn && yn).toNat : Int) - ((xp && yn).toNat + (xn && yp).toNat) := by
  cases xp <;> cases xn <;> cases yp <;> cases yn <;> decide

/-- signed value of a (p,n) digit list, LSB first -/
def dval : List (Bool × Bool) → Int
  | [] => 0
  | (p, n) :: t => ((p.toNat : Int) - n.toNat) + 2 * dval t

/-- the two rails of a digit list -/
def railP : List (Bool × Bool) → List Bool
  | [] => []
  | (p, _) :: t => p :: railP t
def railN : List (Bool × Bool) → List Bool
  | [] => []
  | (_, n) :: t => n :: railN t

theorem dval_rails (d : List (Bool × Bool)) : dval d = (bval (railP d) : Int) - bval (railN d) := by
  induction d with
  | nil => simp [dval, railP, railN, bval]
  | cons h t ih => cases h; simp [dval, railP, railN, bval, ih]; omega

/-- **product of two signed-digit numbers as four unsigned partial-product sets**:
    P-rail gets xP·yP and xN·yN, N-rail gets xP·yN and xN·yP. -/
theorem sd_product (x y : List (Bool × Bool)) :
    dval x * dval y
      = ((bval (railP x) * bval (railP y) + bval (railN x) * bval (railN y) : Nat) : Int)
        - ((bval (railP x) * bval (railN y) + bval (railN x) * bval (railP y) : Nat) : Int) := by
  rw [dval_rails, dval_rails]
  simp only [Int.natCast_add, Int.natCast_mul]
  rw [Int.sub_mul, Int.mul_sub, Int.mul_sub]; omega

/-! ## The canonical 3:2 compressor of sd2_gates.py -/

def faS (a b c : Bool) : Bool := xor (xor a b) c
def faC (a b c : Bool) : Bool := (a && b) || (c && xor a b)
/-- low/high digits (p,n) of `sd2_compress3_gates`: FA per rail, then rail subtraction -/
def compress3 (xp xn yp yn cp cn : Bool) : (Bool × Bool) × (Bool × Bool) :=
  let ps := faS xp yp cp; let pc := faC xp yp cp
  let ns := faS xn yn cn; let nc := faC xn yn cn
  ((ps && !ns, ns && !ps), (pc && !nc, nc && !pc))

def dv (d : Bool × Bool) : Int := (d.1.toNat : Int) - d.2.toNat
/-- canonical: never (1,1) -/
def canon (d : Bool × Bool) : Prop := !(d.1 && d.2)

/-- for canonical inputs: x + y + c = low + 2·high, and low, high are canonical -/
theorem compress3_spec (xp xn yp yn cp cn : Bool)
    (hx : canon (xp, xn)) (hy : canon (yp, yn)) (hc : canon (cp, cn)) :
    dv (xp, xn) + dv (yp, yn) + dv (cp, cn)
      = dv (compress3 xp xn yp yn cp cn).1 + 2 * dv (compress3 xp xn yp yn cp cn).2
    ∧ canon (compress3 xp xn yp yn cp cn).1 ∧ canon (compress3 xp xn yp yn cp cn).2 := by
  cases xp <;> cases xn <;> cases yp <;> cases yn <;> cases cp <;> cases cn <;> simp_all [canon] <;> decide

end SignedDigit
