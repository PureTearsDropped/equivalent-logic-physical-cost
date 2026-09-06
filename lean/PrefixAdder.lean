/-!
# Parallel-prefix (Kogge-Stone) carry computation is the ripple carry (core Lean 4, no Mathlib)

Bits are LSB first. For operand bits `x y : List Bool` define generate `g = x ∧ y` and propagate `p = x ⊕ y`.
The ripple carry is `c₀ = false`, `cᵢ₊₁ = gᵢ ∨ (pᵢ ∧ cᵢ)`. Group (G,P) pairs compose associatively, the
composition over a prefix `[0..i]` gives the carry into `i+1`, and the Kogge-Stone network — which at level
`L` holds, at position `i`, the composition over the last `2^L` positions — therefore holds the exact carry
once `2^L ≥ i+1`. Finally `sumᵢ = pᵢ ⊕ cᵢ` and the sum bits plus the carry-out value the addition.
-/

namespace PrefixAdder

abbrev GP := Bool × Bool   -- (generate, propagate)

/-- `comp hi lo`: the group (G,P) of the concatenation with `hi` above `lo` -/
def comp (hi lo : GP) : GP := (hi.1 || (hi.2 && lo.1), hi.2 && lo.2)

theorem comp_assoc (a b c : GP) : comp (comp a b) c = comp a (comp b c) := by
  cases a with | mk a1 a2 => cases b with | mk b1 b2 => cases c with | mk c1 c2 =>
  cases a1 <;> cases a2 <;> cases b1 <;> cases b2 <;> cases c1 <;> cases c2 <;> decide

/-- identity element (no bits): generates nothing, propagates everything -/
def idGP : GP := (false, true)
theorem comp_id_left (a : GP) : comp idGP a = a := by cases a with | mk a1 a2 => cases a1 <;> cases a2 <;> decide
theorem comp_id_right (a : GP) : comp a idGP = a := by cases a with | mk a1 a2 => cases a1 <;> cases a2 <;> decide

/-- group of a segment given LSB first: the head is the lowest bit -/
def grp : List GP → GP
  | [] => idGP
  | l :: t => comp (grp t) l

theorem grp_append (l₁ l₂ : List GP) : grp (l₁ ++ l₂) = comp (grp l₂) (grp l₁) := by
  induction l₁ with
  | nil => simp [grp, comp_id_right]
  | cons h t ih => simp [grp, ih, comp_assoc]

/-- ripple carry out of a segment (LSB first) given carry-in `c` -/
def cout : List GP → Bool → Bool
  | [], c => c
  | (g, p) :: t, c => cout t (g || (p && c))

/-- **the algebraic core**: the ripple carry equals the group composition applied to the carry-in -/
theorem cout_eq_grp (l : List GP) (c : Bool) : cout l c = ((grp l).1 || ((grp l).2 && c)) := by
  induction l generalizing c with
  | nil => cases c <;> simp [cout, grp, idGP]
  | cons h t ih =>
    cases h with | mk g p =>
    simp only [cout, grp, comp]
    rw [ih]
    cases g <;> cases p <;> cases c <;> simp

/-! ## The Kogge-Stone network -/

/-- one level with span `s`: position `i ≥ s` composes with position `i - s` -/
def level (s : Nat) (st : List GP) : List GP :=
  (List.range st.length).map fun i =>
    if i < s then st.getD i idGP else comp (st.getD i idGP) (st.getD (i - s) idGP)

/-- levels with spans 1, 2, 4, …, 2^(L-1) -/
def ks : Nat → List GP → List GP
  | 0, st => st
  | L + 1, st => level (2 ^ L) (ks L st)

/-- segment of `gp` covering positions `lo … i` (inclusive), clipped at 0 -/
def seg (gp : List GP) (lo i : Nat) : List GP := (gp.drop lo).take (i + 1 - lo)

theorem level_length (s : Nat) (st : List GP) : (level s st).length = st.length := by
  simp [level]
theorem ks_length (L : Nat) (st : List GP) : (ks L st).length = st.length := by
  induction L with
  | zero => rfl
  | succ L ih => simp [ks, level_length, ih]

theorem level_getD (s : Nat) (st : List GP) (i : Nat) (hi : i < st.length) :
    (level s st).getD i idGP = if i < s then st.getD i idGP else comp (st.getD i idGP) (st.getD (i - s) idGP) := by
  simp [level, List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_range, hi]

/-- splitting a segment at `i - s`: lower part `lo … i-s`, upper part `i-s+1 … i` -/
theorem seg_split (gp : List GP) (lo i s : Nat) (h1 : lo + s ≤ i + 1) (h2 : 1 ≤ s) :
    seg gp lo i = seg gp lo (i - s) ++ seg gp (i - s + 1) i := by
  unfold seg
  have hdrop : gp.drop (i - s + 1) = (gp.drop lo).drop (i - s + 1 - lo) := by
    rw [List.drop_drop]; congr 1; omega
  rw [hdrop]
  have : i + 1 - lo = (i - s + 1 - lo) + (i + 1 - (i - s + 1)) := by omega
  rw [this, List.take_add]

theorem take_one_drop (l : List GP) (i : Nat) (hi : i < l.length) : (l.drop i).take 1 = [l.getD i idGP] := by
  induction l generalizing i with
  | nil => simp at hi
  | cons h t ih =>
    cases i with
    | zero => simp
    | succ i => simp only [List.drop_succ_cons, List.getD_cons_succ]; exact ih i (by simpa using hi)

/-- **invariant**: after `L` levels, position `i` holds the group of the last `2^L` positions -/
theorem ks_invariant (gp : List GP) (L : Nat) (i : Nat) (hi : i < gp.length) :
    (ks L gp).getD i idGP = grp (seg gp (i + 1 - 2 ^ L) i) := by
  induction L generalizing i with
  | zero =>
    simp only [ks, seg, Nat.pow_zero]
    have e : i + 1 - 1 = i := by omega
    rw [e]
    have e2 : i + 1 - i = 1 := by omega
    rw [e2, take_one_drop gp i hi]; simp [grp, comp_id_left]
  | succ L ih =>
    have hlen : i < (ks L gp).length := by rw [ks_length]; exact hi
    have hs : 1 ≤ 2 ^ L := Nat.one_le_two_pow
    simp only [ks]
    rw [level_getD _ _ _ hlen, Nat.pow_succ]
    by_cases h : i < 2 ^ L
    · rw [if_pos h, ih i hi]
      have e1 : i + 1 - 2 ^ L = 0 := by omega
      have e2 : i + 1 - 2 ^ L * 2 = 0 := by omega
      rw [e1, e2]
    · rw [if_neg h, ih i hi, ih (i - 2 ^ L) (Nat.lt_of_le_of_lt (Nat.sub_le _ _) hi)]
      rw [← grp_append]
      congr 1
      by_cases hb : i + 1 < 2 ^ L * 2
      · have e2 : i + 1 - 2 ^ L * 2 = 0 := by omega
        rw [e2, seg_split gp 0 i (2 ^ L) (by omega) hs]
        have e3 : i - 2 ^ L + 1 - 2 ^ L = 0 := by omega
        have e4 : i - 2 ^ L + 1 = i + 1 - 2 ^ L := by omega
        rw [e3, e4]
      · rw [seg_split gp (i + 1 - 2 ^ L * 2) i (2 ^ L) (by omega) hs]
        have e3 : i - 2 ^ L + 1 - 2 ^ L = i + 1 - 2 ^ L * 2 := by omega
        have e4 : i - 2 ^ L + 1 = i + 1 - 2 ^ L := by omega
        rw [e3, e4]

/-- once the span covers the whole prefix, position `i` holds the group of `0 … i` -/
theorem ks_prefix (gp : List GP) (L i : Nat) (hi : i < gp.length) (hL : i + 1 ≤ 2 ^ L) :
    (ks L gp).getD i idGP = grp (gp.take (i + 1)) := by
  rw [ks_invariant gp L i hi]
  have : i + 1 - 2 ^ L = 0 := by omega
  simp [seg, this]

/-- and that group's G is the ripple carry into position `i+1` (carry-in 0) -/
theorem ks_carry (gp : List GP) (L i : Nat) (hi : i < gp.length) (hL : i + 1 ≤ 2 ^ L) :
    ((ks L gp).getD i idGP).1 = cout (gp.take (i + 1)) false := by
  rw [ks_prefix gp L i hi hL, cout_eq_grp]; simp

/-! ## From carries to the sum -/

/-- generate/propagate of two operand rows -/
def gpOf : List Bool → List Bool → List GP
  | x :: xs, y :: ys => (x && y, xor x y) :: gpOf xs ys
  | _, _ => []

/-- ripple-carry sum bits, LSB first, with carry-in `c` -/
def sumBits : List GP → Bool → List Bool
  | [], _ => []
  | (g, p) :: t, c => xor p c :: sumBits t (g || (p && c))

def bval : List Bool → Nat
  | [] => 0
  | b :: t => b.toNat + 2 * bval t

theorem fa_id (a b c : Bool) :
    (xor (xor a b) c).toNat + 2 * ((a && b) || (xor a b && c)).toNat = a.toNat + b.toNat + c.toNat := by
  cases a <;> cases b <;> cases c <;> decide

/-- the ripple adder adds: sum bits plus carry-out at the top weight -/
theorem ripple_adds (x y : List Bool) (c : Bool) (hl : x.length = y.length) :
    bval (sumBits (gpOf x y) c) + 2 ^ x.length * (cout (gpOf x y) c).toNat = bval x + bval y + c.toNat := by
  induction x generalizing y c with
  | nil => cases y with
    | nil => cases c <;> simp [gpOf, sumBits, cout, bval]
    | cons _ _ => simp at hl
  | cons xb xs ih =>
    cases y with
    | nil => simp at hl
    | cons yb ys =>
      simp only [List.length_cons] at hl
      have ih' := ih ys ((xb && yb) || (xor xb yb && c)) (by omega)
      have hfa := fa_id xb yb c
      simp only [gpOf, sumBits, cout, bval, List.length_cons]
      rw [Nat.pow_succ, Nat.mul_right_comm]
      omega

/-! ## Sum bits from Kogge-Stone carries equal the ripple sum bits -/

theorem sumBits_length (l : List GP) (c : Bool) : (sumBits l c).length = l.length := by
  induction l generalizing c with
  | nil => rfl
  | cons h t ih => cases h; simp [sumBits, ih]

/-- bit `i` of the ripple sum is `pᵢ ⊕ (carry out of the bits below i)` -/
theorem sumBits_getD (l : List GP) (c : Bool) (i : Nat) (hi : i < l.length) :
    (sumBits l c).getD i false = xor (l.getD i idGP).2 (cout (l.take i) c) := by
  induction l generalizing c i with
  | nil => simp at hi
  | cons h t ih =>
    cases h with | mk g p =>
    cases i with
    | zero => simp [sumBits, cout, idGP]
    | succ i =>
      simp only [sumBits, List.getD_cons_succ, List.take_succ_cons, cout]
      exact ih _ i (by simpa using hi)

/-- the carry into position `i` taken from the Kogge-Stone network (position `i-1`; `false` at `i = 0`) -/
def ksCarry (gp : List GP) (L i : Nat) : Bool :=
  match i with
  | 0 => false
  | j + 1 => ((ks L gp).getD j idGP).1

/-- **Kogge-Stone adder = ripple adder, bit for bit**, once `2^L ≥ length` -/
theorem ks_sum_bit (gp : List GP) (L i : Nat) (hi : i < gp.length) (hL : gp.length ≤ 2 ^ L) :
    xor (gp.getD i idGP).2 (ksCarry gp L i) = (sumBits gp false).getD i false := by
  rw [sumBits_getD gp false i hi]
  cases i with
  | zero => simp [ksCarry, cout]
  | succ j => simp only [ksCarry]; rw [ks_carry gp L j (by omega) (by omega)]

end PrefixAdder
