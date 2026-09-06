# equivalent-logic-physical-cost

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
