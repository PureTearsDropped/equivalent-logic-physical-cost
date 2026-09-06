/-!
# Arithmetic-level equivalence for column-compression multipliers (core Lean 4, no Mathlib)

A multiplier is: partial-product bits at weights 2^(i+j), then a sequence of *compression steps*
(full adder on three bits of one weight, half adder on two), ending with at most one bit per weight,
which is the output number. This file proves that **every** such schedule computes `a * b`,
so an external search over schedules needs no per-candidate proof — only the exhaustive check
that the emitted gates implement the chosen FA/HA steps (done in Python).

The Boolean full/half adders are the ones used in the netlists, and the 9-NAND realization used in
`src/` is proved to compute them (`fa_nand9`).
-/

namespace ArithEquiv

/-- full-adder sum and carry -/
def faSum (a b c : Bool) : Bool := xor (xor a b) c
def faCarry (a b c : Bool) : Bool := (a && b) || (a && c) || (b && c)
def haSum (a b : Bool) : Bool := xor a b
def haCarry (a b : Bool) : Bool := a && b

theorem fa_spec (a b c : Bool) :
    a.toNat + b.toNat + c.toNat = (faSum a b c).toNat + 2 * (faCarry a b c).toNat := by
  cases a <;> cases b <;> cases c <;> decide

theorem ha_spec (a b : Bool) :
    a.toNat + b.toNat = (haSum a b).toNat + 2 * (haCarry a b).toNat := by
  cases a <;> cases b <;> decide

/-- The 9-NAND full adder of `src/pa4x4.py` (ALL_NAND_FA) computes faSum/faCarry. -/
def nand (x y : Bool) : Bool := !(x && y)
def fa9_sum (a b c : Bool) : Bool :=
  let g1 := nand a b; let g2 := nand a g1; let g3 := nand b g1; let x := nand g2 g3
  let g5 := nand x c; let g6 := nand x g5; let g7 := nand c g5
  nand g6 g7
def fa9_carry (a b c : Bool) : Bool :=
  let g1 := nand a b; let g2 := nand a g1; let g3 := nand b g1; let x := nand g2 g3
  let g5 := nand x c
  nand g1 g5
theorem fa_nand9 (a b c : Bool) : fa9_sum a b c = faSum a b c ∧ fa9_carry a b c = faCarry a b c := by
  cases a <;> cases b <;> cases c <;> decide

/-- The xor2/xor2/a21o full adder (`FA_xor2_a21o` in `src/fullcell.py`): carry = (x ∧ c) ∨ (a ∧ b). -/
theorem fa_xor2_a21o (a b c : Bool) :
    xor (xor a b) c = faSum a b c ∧ ((xor a b && c) || (a && b)) = faCarry a b c := by
  cases a <;> cases b <;> cases c <;> decide

/-- weighted bits: `(k, b)` contributes `2^k` when `b` is set -/
def wval : List (Nat × Bool) → Nat
  | [] => 0
  | (k, b) :: t => (if b then 2 ^ k else 0) + wval t

theorem wval_append (l₁ l₂ : List (Nat × Bool)) : wval (l₁ ++ l₂) = wval l₁ + wval l₂ := by
  induction l₁ with
  | nil => simp [wval]
  | cons h t ih => cases h; simp [wval, ih]; omega

/-- `wval` does not depend on the order of the bits -/
theorem wval_perm {l₁ l₂ : List (Nat × Bool)} (h : l₁.Perm l₂) : wval l₁ = wval l₂ := by
  induction h with
  | nil => rfl
  | cons x _ ih => cases x; simp [wval, ih]
  | swap x y l => cases x; cases y; simp [wval]; omega
  | trans _ _ ih₁ ih₂ => omega

/-- a full-adder step on three bits of weight `k` (at the front of the list) -/
theorem fa_step (k : Nat) (x y z : Bool) (rest : List (Nat × Bool)) :
    wval ((k, x) :: (k, y) :: (k, z) :: rest)
      = wval ((k, faSum x y z) :: (k + 1, faCarry x y z) :: rest) := by
  cases x <;> cases y <;> cases z <;> simp [wval, faSum, faCarry, Nat.pow_succ] <;> omega

/-- a half-adder step on two bits of weight `k` -/
theorem ha_step (k : Nat) (x y : Bool) (rest : List (Nat × Bool)) :
    wval ((k, x) :: (k, y) :: rest)
      = wval ((k, haSum x y) :: (k + 1, haCarry x y) :: rest) := by
  cases x <;> cases y <;> simp [wval, haSum, haCarry, Nat.pow_succ] <;> omega

/-- A compression step: reorder the bits (any permutation), then apply FA or HA at the front. -/
inductive Step
  | fa (perm : List (Nat × Bool)) (k : Nat) (x y z : Bool) (rest : List (Nat × Bool))
  | ha (perm : List (Nat × Bool)) (k : Nat) (x y : Bool) (rest : List (Nat × Bool))

/-- The state a step starts from and the state it produces. -/
def Step.src : Step → List (Nat × Bool)
  | .fa p _ _ _ _ _ => p
  | .ha p _ _ _ _ => p
def Step.dst : Step → List (Nat × Bool)
  | .fa _ k x y z r => (k, faSum x y z) :: (k + 1, faCarry x y z) :: r
  | .ha _ k x y r => (k, haSum x y) :: (k + 1, haCarry x y) :: r
/-- well-formed: the chosen bits are a reordering of the source state -/
def Step.wf : Step → Prop
  | .fa p k x y z r => p.Perm ((k, x) :: (k, y) :: (k, z) :: r)
  | .ha p k x y r => p.Perm ((k, x) :: (k, y) :: r)

theorem step_preserves (s : Step) (h : s.wf) : wval s.src = wval s.dst := by
  cases s with
  | fa p k x y z r => simp [Step.src, Step.dst]; rw [wval_perm h]; exact fa_step k x y z r
  | ha p k x y r => simp [Step.src, Step.dst]; rw [wval_perm h]; exact ha_step k x y r

/-- A schedule is a chain of well-formed steps, each starting where the previous one ended. -/
inductive Schedule : List (Nat × Bool) → List (Nat × Bool) → Prop
  | refl (l) : Schedule l l
  | step (s : Step) (h : s.wf) {l} (rest : Schedule s.dst l) : Schedule s.src l

/-- **Any** compression schedule preserves the weighted sum. -/
theorem schedule_preserves {l₀ l₁ : List (Nat × Bool)} (sch : Schedule l₀ l₁) : wval l₀ = wval l₁ := by
  induction sch with
  | refl _ => rfl
  | step s h _ ih => rw [step_preserves s h]; exact ih

/-! ## Partial products of a 4×4 unsigned multiplier -/

def val4 (x0 x1 x2 x3 : Bool) : Nat := x0.toNat + 2 * x1.toNat + 4 * x2.toNat + 8 * x3.toNat

def pp4 (a0 a1 a2 a3 b0 b1 b2 b3 : Bool) : List (Nat × Bool) :=
  [(0, a0 && b0), (1, a0 && b1), (2, a0 && b2), (3, a0 && b3),
   (1, a1 && b0), (2, a1 && b1), (3, a1 && b2), (4, a1 && b3),
   (2, a2 && b0), (3, a2 && b1), (4, a2 && b2), (5, a2 && b3),
   (3, a3 && b0), (4, a3 && b1), (5, a3 && b2), (6, a3 && b3)]

theorem pp4_value (a0 a1 a2 a3 b0 b1 b2 b3 : Bool) :
    wval (pp4 a0 a1 a2 a3 b0 b1 b2 b3) = val4 a0 a1 a2 a3 * val4 b0 b1 b2 b3 := by
  cases a0 <;> cases a1 <;> cases a2 <;> cases a3 <;> cases b0 <;> cases b1 <;> cases b2 <;> cases b3 <;> decide

/-- The output of a schedule that ends with one bit per weight 0..7 is the product. -/
theorem multiplier_correct (a0 a1 a2 a3 b0 b1 b2 b3 p0 p1 p2 p3 p4 p5 p6 p7 : Bool)
    (sch : Schedule (pp4 a0 a1 a2 a3 b0 b1 b2 b3)
                    [(0, p0), (1, p1), (2, p2), (3, p3), (4, p4), (5, p5), (6, p6), (7, p7)]) :
    p0.toNat + 2 * p1.toNat + 4 * p2.toNat + 8 * p3.toNat + 16 * p4.toNat + 32 * p5.toNat
      + 64 * p6.toNat + 128 * p7.toNat = val4 a0 a1 a2 a3 * val4 b0 b1 b2 b3 := by
  have h := schedule_preserves sch
  rw [pp4_value] at h
  rw [h]
  cases p0 <;> cases p1 <;> cases p2 <;> cases p3 <;> cases p4 <;> cases p5 <;> cases p6 <;> cases p7 <;> decide

/-! ## General width: partial products of n×m bit lists (LSB first) -/

/-- value of a bit list, least-significant bit first -/
def bval : List Bool → Nat
  | [] => 0
  | b :: t => b.toNat + 2 * bval t

/-- one partial-product row: `ai ∧ bj` at weight `w + j` -/
def ppRow (w : Nat) (ai : Bool) : List Bool → List (Nat × Bool)
  | [] => []
  | bj :: t => (w, ai && bj) :: ppRow (w + 1) ai t

/-- all rows: row `i` of `a` starts at weight `w + i` -/
def ppAll (w : Nat) : List Bool → List Bool → List (Nat × Bool)
  | [], _ => []
  | ai :: t, b => ppRow w ai b ++ ppAll (w + 1) t b

/-- the output bits `p` laid out at weights `w, w+1, …` -/
def outList (w : Nat) : List Bool → List (Nat × Bool)
  | [] => []
  | p :: t => (w, p) :: outList (w + 1) t

theorem ppRow_value (w : Nat) (ai : Bool) (b : List Bool) :
    wval (ppRow w ai b) = (if ai then 2 ^ w * bval b else 0) := by
  induction b generalizing w with
  | nil => cases ai <;> simp [ppRow, wval, bval]
  | cons bj t ih =>
    cases ai <;> cases bj <;> simp [ppRow, wval, bval, ih, Nat.pow_succ, Nat.mul_add, Nat.mul_assoc, Nat.mul_comm 2]

theorem ppAll_value (w : Nat) (a b : List Bool) :
    wval (ppAll w a b) = 2 ^ w * (bval a * bval b) := by
  induction a generalizing w with
  | nil => simp [ppAll, wval, bval]
  | cons ai t ih =>
    cases ai <;> simp [ppAll, wval_append, ppRow_value, ih, bval, Nat.pow_succ, Nat.mul_add, Nat.add_mul,
                       Nat.mul_assoc, Nat.mul_comm 2, Nat.mul_left_comm]

theorem outList_value (w : Nat) (p : List Bool) : wval (outList w p) = 2 ^ w * bval p := by
  induction p generalizing w with
  | nil => simp [outList, wval, bval]
  | cons x t ih => cases x <;> simp [outList, wval, bval, ih, Nat.pow_succ, Nat.mul_add, Nat.mul_assoc, Nat.mul_comm 2]

/-- **General width.** Any compression schedule from the partial products of `a` and `b`
    to one bit per weight computes the product. -/
theorem multiplier_correct_general (a b p : List Bool)
    (sch : Schedule (ppAll 0 a b) (outList 0 p)) : bval p = bval a * bval b := by
  have h := schedule_preserves sch
  rw [ppAll_value, outList_value] at h
  simpa using h.symm

end ArithEquiv
