`RepDemo.lean` needs Mathlib (`import Mathlib.Tactic`); run it inside any Lake project that depends on Mathlib
(`lake env lean RepDemo.lean`). It shows Lean *producing* the representation-independent identity: the array
accumulation order and the Dadda column grouping are both rewritten by `ring_nf` to one canonical
polynomial (`a0*b0 + a0*b1*2 + … + b3*a3*64`), and `ring` proves array = Dadda and carry-save rows = product.
The core-only theorems in `../ArithEquiv.lean` do the bit-level part (bits → ℕ, any FA/HA schedule preserves the value).
