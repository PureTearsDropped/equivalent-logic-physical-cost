# equivalent-logic-physical-cost

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.22486589.svg)](https://doi.org/10.5281/zenodo.22486589)

**Functionally equivalent logic implementations compared under real physical cost.**
The subject is an exact unsigned 4×4 multiplier. Netlists that compute exactly the same function
(verified on all 256 input pairs) are compared on the SkyWater SKY130 standard-cell library with
real Liberty timing tables, OpenSTA, OpenROAD/LibreLane placement and routing, and SDF-annotated
gate-level simulation, to measure how far a whole-DAG timing-driven optimizer actually gets.

[日本語 README](README.md) · full tables in [results/summary.md](results/summary.md)

## Contents

- **Timing model** (`src/`): NLDM table lookup (input slew × output load) with slew propagation,
  from two-input inverting cells (`sky130_timing.py`) to N-input, non-unate, multi-output cells
  (`fullcell.py`). Agrees with OpenSTA within 1.5 % on 30 uniform variants.
- **Optimizer**: greedy; every candidate rebuilds the DAG, recomputes whole-circuit timing, and is
  accepted only if the critical delay drops. Moves: gate duplication (enumerated sink partitions),
  drive strength (×1/×2/×4), and per-position full/half-adder/partial-product variant selection.
  All moves preserve function by construction; the result is verified exhaustively.
- **Physical flow** (`flow/`): LibreLane 3.0.11 configs, netlists and results (metrics, STA reports,
  SPEF, SDF) for 11 designs; probabilistic power (`power.py`) and glitch-inclusive power (`sim_power.py`).
- **Prototype** (`src/pa4x4.py`, `docs/prototype_notes.md`): the starting point, an optimizer with
  illustrative normalized cell values. This repository began as a re-test of its claims on real cells.

## Main results

Post-layout (SKY130, tt 25 °C 1.80 V, parasitics included). Energy: 200 MHz random inputs, SDF simulation.

| design | delay | logic area µm² | energy / op |
|---|---:|---:|---:|
| FA = xor2, xor2, a21o (72 cells) | 2290 ps | 430 | **589 fJ** |
| 9-NAND FA, original (124 cells) | 2319 ps | 465 | 749 fJ |
| full-vocabulary optimizer (122 cells) | 2189 ps | 507 | 777 fJ |
| 9-NAND + 12 duplications (136 cells) | 2207 ps | 510 | 819 fJ |
| original + OpenROAD resizer (2 ns target) | 2252 ps | 807 | 1585 fJ |
| standard flow from `a*b`, DELAY strategy, 2 ns target | 1998 ps | 1775 | 3505 fJ |

Findings:

1. **The 9-NAND full adder is the fastest on SKY130.** The dedicated fa cell (3323 ps) and xor3+maj3 (2795 ps) are far slower; maj3 and xor3 are weak cells.
2. **Whole-DAG duplication survives routing** (5.9 % cell-only, 4.8 % post-layout). OpenROAD's own resizer on the same netlist gives 2252 ps / 807 µm², worse on both axes, and makes the already-duplicated netlist slower.
3. **The standard flow buys 10 % delay with 3.5× area and 6× energy per operation.** Below 600 µm² the hand netlists dominate the Pareto front; four of them fit in the standard result's area.
4. **OpenSTA's probabilistic power estimate mis-ranks designs**: 1.3–2.2× above simulation, with a design-dependent factor. Glitches are 29–48 % of all toggles.
5. **A larger cell vocabulary does not change the picture.** The two-phase greedy over 66 cells lands where NAND-only duplication does (2189 ps / 507 µm²).
6. **None of this matters on an FPGA.** yosys/abc maps `a*b` and all three gate-level variants to the same 80 LUTs, depth 5.

## research branch: arithmetic-level equivalence (compression schedules)

Instead of rewriting gates, change **the order in which partial-product columns are compressed**
(array, Wallace, Dadda, arrival-greedy, random). Same cells, same partial products; only the adder wiring
differs. Correctness of every schedule is one Lean theorem, `multiplier_correct` in `lean/ArithEquiv.lean`
(core Lean 4, no Mathlib, axioms propext and Quot.sound only), so the search carries no per-candidate proof;
emitted netlists are still checked on 256/256 inputs.

| design (post-layout) | delay | area µm² | energy / op |
|---|---:|---:|---:|
| **Dadda, xor2/xor2/a21o (56 cells)** | **1662 ps** | **410** | **440 fJ** |
| Dadda, 9-NAND (124 cells) | 1688 ps | 465 | 598 fJ |
| array, 9-NAND (124 cells, = original) | 2319 ps | 465 | 749 fJ |
| standard flow, 2 ns target | 1998 ps | 1775 | 3505 fJ |

Re-wiring the same 124 cells from array to Dadda order is 27 % faster at zero area cost, an order of
magnitude more than gate duplication bought (5 % for 10 % area). Dadda with xor2/a21o adders beats the
standard flow's fastest result by 17 % in delay, 4.3× in area and 8× in energy per operation, and dominates
every other design on all three axes. Keeping the arithmetic structure and rewriting *at the arithmetic level*
worked where discarding structure and re-synthesizing from the function (abc) did not.
Details in `results/summary.md` §5; reproduce with `python3 src/arith_search.py 400`.

### Scaling (4 → 32 bits)

The builder and checks are generalized to n bits (`src/scale_sweep.py`) and the Lean theorem to any width
(`multiplier_correct_general`). Search cost is not the issue: one timing evaluation of a 32×32 multiplier
(over 10k cells) takes 0.4 s in pure Python and the random check 0.1 s. What changes with width is where the
delay lives: the final adder is 56 % of the Dadda delay at 4 bits and 61 % at 16. A Kogge-Stone final adder
loses at 4 bits (fan-out), gains 12 % at 8 and 37 % at 16. Placed and routed at 8×8: array 5692 ps → Dadda
3505 ps (same 600 cells, −36 % energy) → Dadda + Kogge-Stone 3120 ps; the standard flow (3 ns target) is
3620 ps at 3.7× the area and 6.3× the energy; with the flow's Booth option it reaches 3408 ps / 6838 µm² / 10670 fJ, still behind Dadda + Kogge-Stone on delay at 2.3× area and 14× energy (at 4 bits Booth is worse than the plain flow on every axis). Tables in `results/summary.md` §6.

### Plugging into total-arith's signed-digit multiplier

total-arith-hardware's `sd_mult10` ((p,n) digit encoding) was imported (4742 cells after constant folding) and
compared on sky130 with a two-rail borrow-save multiplier built by the same generator (`src/sd_tree.py`, proofs in
`lean/SignedDigit.lean`). Placed and routed, glitch-inclusive: under the same contract (canonical digits out) 8 %
faster at 2.8× less area and 2.5× less energy; allowing borrow-save output, 2.1× faster at 2.5× less area
(4166 ps / 11241 µm² / 13.8 pJ vs 8659 ps / 27757 µm² / 32.3 pJ). Canonicalising every step (8 of the compressor's
18 gates) costs what resolving carries every step costs; moving it to the boundary is the carry-save lesson again.
Tables in `results/summary.md` §8.

### Correctly rounded float32 exp in hardware (2026-09-06)

The Ziv-style correct rounding of the cuda library ported to hardware: 64-entry table, degree-6 Estrin in 60-bit fixed
point, Ziv exit, no fallback. The spec model is correct on all 526,392,936 in-range float32 inputs against MPFR
(0 undecided); the gate netlist matches it on all of them. Routed: combinational 64.4 ns / 447k µm², 7 stages 9.6 ns,
**15 stages 6.46 ns (155 MHz) / 482k µm²**, everything-to-the-standard-flow 6.99 ns / 710k µm². OpenROAD's resizer
achieved nothing (1,137 gates upsized, then gave up); placement bought 10 %, splitting the multiplies 33 %.
**Energy: 4,952 pJ per operation combinational (80 % glitches) vs 318 pJ pipelined (15× less)** — at this depth
pipelining is first of all an energy measure. Details in `results/summary.md` §10, code in `transcend/`.

## Retractions

Intermediate claims that were withdrawn are kept here rather than deleted.

- The prototype's "NOR is physically expensive, so all-NAND wins" was, with its illustrative cell values, decided **by the values alone** (with NOR = NAND another variant wins). Real cells confirm the direction (nor2_1 rise 150 ps vs nand2_1 82 ps).
- The prototype's gate-count-only variant loses because of **topology** (its cin→carry path is 4 levels instead of 2), not NOR cost; it loses under unit delay too.
- "xor2-based adders cost 19 % more energy" came from probabilistic activity propagation; SDF simulation shows **21 % less**. Withdrawn.
- "Duplication + sizing is best" held only before routing; after routing duplication alone wins.

## Reproduction

```
pip install -r requirements.txt          # numpy only
python3 src/audit.py                     # re-test of the prototype (no external tools)
python3 src/sky130_timing.py             # NLDM on real cells, three variants + greedy duplication
sh lib/fetch_lib.sh                      # full Liberty (13 MB, Apache-2.0)
export STA=/path/to/sta                  # OpenSTA binary
python3 src/fullcell.py                  # 30 uniform variants, model vs OpenSTA
python3 src/optimize_full.py             # full-vocabulary two-phase greedy
python3 src/sizing.py                    # duplication vs drive strength
python3 flow/summary.py                  # post-layout table from the bundled results
python3 flow/power.py                    # probabilistic power
export PDK_VERILOG=/path/to/sky130A/libs.ref/sky130_fd_sc_hd/verilog
python3 flow/sim_power.py 32768          # SDF simulation + VCD power (needs iverilog)
```

To re-run placement and routing install LibreLane (`nix shell github:librelane/librelane`) and run
`librelane config.json` inside `flow/designs/<name>/`.

Pitfalls when pushing a structural netlist through LibreLane (all of them were hit):

- `SYNTH_ELABORATE_ONLY` to skip logic mapping; disable every resizer (`RUN_POST_*_REPAIR`, `*_RESIZER_*`).
- Declare every wire; no `assign` — connect ports directly to cell pins.
- A combinational block gets a dummy clock. Set `CLOCK_UNCERTAINTY_CONSTRAINT` to 0, otherwise hold checks fail and the baseline flow inserts hold-fix buffers that inflate its area.
- Read delay from the data arrival time in `stapostpnr/.../max.rpt` (worst slack includes the uncertainty).
- Close stdin when running OpenSTA as a subprocess or it waits for a prompt.
- iverilog silently ignores SDF without `-gspecify` (every transition lands on the clock grid). The cell models without power pins fail to elaborate under `-gspecify` (an unused lpflow_bleeder references VPWR), so use the powered netlist (`*.pnl.v`) with `-DUSE_POWER_PINS`.

## Limitations

- One 4×4 array topology. The array wiring is fixed; the search covers adder internals, duplication and sizing only.
- Single-move greedy with no plateau moves, look-ahead, or buffer insertion. The gap to the standard flow on the "spend area for speed" side is a limitation of this search.
- tt corner only; one input driving cell; 10 fF output load.
- Energy is the random-input average. Nothing has been measured on silicon.
- No novelty is claimed. Whole-DAG timing-driven optimization and NLDM are textbook; this is a record of measuring them with real cells and a real flow.

## Layout

```
src/        timing models, optimizers, audit scripts
cells/      per-cell SKY130 Liberty tables (JSON, Apache-2.0) and the area table
flow/       LibreLane configs and netlists (designs/), post-layout results (results/), power scripts
results/    result tables (summary.md) and search logs
docs/       prototype notes
lib/        fetch script for the full Liberty (file not committed)
```

## License

Code and text: 0BSD. Liberty-derived data in `cells/`: Apache-2.0 from the SkyWater PDK (`cells/NOTICE`).
