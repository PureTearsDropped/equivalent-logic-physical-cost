import Mathlib.Tactic

/-! Two arithmetic decompositions of the same 4×4 product, as ℕ-polynomials in the bits.
`ring_nf` rewrites each to the canonical polynomial normal form: that normal form *is* the
representation-independent identity. -/

-- partial products at weight 2^(i+j)
def pp (ai bj : ℕ) (i j : ℕ) : ℕ := ai * bj * 2 ^ (i + j)

-- array multiplier: rows accumulated one after another (left fold)
def array4 (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) : ℕ :=
  (((pp a0 b0 0 0 + pp a0 b1 0 1 + pp a0 b2 0 2 + pp a0 b3 0 3)
    + (pp a1 b0 1 0 + pp a1 b1 1 1 + pp a1 b2 1 2 + pp a1 b3 1 3))
    + (pp a2 b0 2 0 + pp a2 b1 2 1 + pp a2 b2 2 2 + pp a2 b3 2 3))
    + (pp a3 b0 3 0 + pp a3 b1 3 1 + pp a3 b2 3 2 + pp a3 b3 3 3)

-- Dadda: columns grouped by weight, compressed in a different association
def dadda4 (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) : ℕ :=
  pp a0 b0 0 0
  + (pp a0 b1 0 1 + pp a1 b0 1 0)
  + ((pp a0 b2 0 2 + pp a1 b1 1 1) + pp a2 b0 2 0)
  + ((pp a0 b3 0 3 + pp a1 b2 1 2 + pp a2 b1 2 1) + pp a3 b0 3 0)
  + ((pp a1 b3 1 3 + pp a2 b2 2 2) + pp a3 b1 3 1)
  + (pp a2 b3 2 3 + pp a3 b2 3 2)
  + pp a3 b3 3 3

-- carry-save: the same value held as two rows r0 + r1 (here: even rows / odd rows)
def carrysave4 (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) : ℕ × ℕ :=
  ( pp a0 b0 0 0 + pp a0 b1 0 1 + pp a0 b2 0 2 + pp a0 b3 0 3 + pp a2 b0 2 0 + pp a2 b1 2 1 + pp a2 b2 2 2 + pp a2 b3 2 3,
    pp a1 b0 1 0 + pp a1 b1 1 1 + pp a1 b2 1 2 + pp a1 b3 1 3 + pp a3 b0 3 0 + pp a3 b1 3 1 + pp a3 b2 3 2 + pp a3 b3 3 3 )

theorem array_eq_dadda (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) :
    array4 a0 a1 a2 a3 b0 b1 b2 b3 = dadda4 a0 a1 a2 a3 b0 b1 b2 b3 := by
  unfold array4 dadda4 pp; ring

theorem carrysave_eq (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) :
    (carrysave4 a0 a1 a2 a3 b0 b1 b2 b3).1 + (carrysave4 a0 a1 a2 a3 b0 b1 b2 b3).2
      = (a0 + 2*a1 + 4*a2 + 8*a3) * (b0 + 2*b1 + 4*b2 + 8*b3) := by
  unfold carrysave4 pp; ring

-- print the canonical normal form Lean produces for both sides
example (a0 a1 a2 a3 b0 b1 b2 b3 : ℕ) :
    array4 a0 a1 a2 a3 b0 b1 b2 b3 = dadda4 a0 a1 a2 a3 b0 b1 b2 b3 := by
  unfold array4 dadda4 pp
  conv_lhs => ring_nf
  trace_state
  conv_rhs => ring_nf
  trace_state
  ring
