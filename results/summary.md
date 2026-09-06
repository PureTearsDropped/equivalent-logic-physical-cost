# Results (sky130_fd_sc_hd, tt 25°C 1.80 V)

All circuits compute the exact unsigned 4×4 product (256/256 input pairs verified) on the same
array-multiplier topology (16 partial products, 4 half adders, 8 full adders). Design names refer to
`flow/designs/<name>/`.

| name | what it is |
|---|---|
| all_nand_inv | 9-NAND full adders, 5-NAND half adders, NAND+INV partial products; tied-input NANDs mapped to inv_1 (124 cells) |
| all_nand_dup12_inv | all_nand_inv after 12 whole-DAG-timing-driven gate duplications (136 cells) |
| opt_ds | all_nand_inv after greedy duplication + drive-strength moves (134 cells) |
| u_xor2a21o | full adder = xor2, xor2, a21o; half adder = xor2 + and2; partial product = and2 (72 cells) |
| full_gain / full_eff | two-phase greedy over the full cell vocabulary (variant+size per position, then resize/duplicate), ranked by gain / gain-per-area |
| all_nand_rsz_2ns / dup12_rsz_2ns | all_nand_inv / all_nand_dup12_inv with OpenROAD's own resizer enabled, 2 ns target |
| behav_area / behav_delay / behav_delay_2ns | `assign p = a*b` through the standard LibreLane flow: yosys/abc AREA strategy, DELAY strategy (10 ns), DELAY strategy with a 2 ns target |

## 1. Cell-delay STA (no wires): uniform full-adder choices, size-1 cells

Model = the NLDM lookup in `src/fullcell.py`; STA = OpenSTA on the exported netlist. Output load 10 fF, input slew 50 ps.

| pp | HA | FA | cells | area µm² | model ps | OpenSTA ps |
|---|---|---|---:|---:|---:|---:|
| nand+inv | nand5 | nand9 | 124 | 465 | 1920 | 1940 |
| nand+inv | xor+and | nand9 | 112 | 450 | 1933 | 1946 |
| nand+inv | xor+and | xor2x2+a21o | 72 | 430 | 1968 | 1990 |
| and2 | nand5 | nand9 | 108 | 445 | 1981 | 1981 |
| and2 | ha | xor2x2+a21o | 52 | 400 | 2167 | 2180 |
| nand+inv | nand5 | xor2x2+maj3 | 76 | 415 | 2675 | 2686 |
| nand+inv | nand5 | xor3+maj3 | 68 | 465 | 2790 | 2795 |
| nand+inv | nand5 | fa (dedicated cell) | 60 | 355 | 3325 | 3323 |

(30 combinations in `results/`-reproducible run of `src/fullcell.py`; model vs OpenSTA within ~1.5 % in all of them.)

## 2. Post-layout (LibreLane 3.0.11 / OpenROAD, placed & routed, SPEF-annotated OpenSTA)

| design | arrival ps | logic cells | logic area µm² | wirelength µm |
|---|---:|---:|---:|---:|
| u_xor2a21o | 2290 | 72 | 430 | 746 |
| all_nand_inv | 2319 | 124 | 465 | 957 |
| full_gain | 2189 | 122 | 507 | 981 |
| all_nand_dup12_inv | 2207 | 136 | 510 | 1070 |
| full_eff | 2190 | 122 | 514 | 1018 |
| opt_ds | 2216 | 134 | 563 | 1068 |
| behav_area | 3387 | 77 | 724 | 987 |
| all_nand_rsz_2ns | 2252 | 149 | 807 | 1303 |
| dup12_rsz_2ns | 2294 | 160 | 957 | 1854 |
| behav_delay | 3043 | 126 | 1235 | 2504 |
| behav_delay_2ns | 1998 | 167 | 1775 | 3645 |

Pareto front on (area, delay): u_xor2a21o, all_nand_inv, full_gain, behav_delay_2ns. Everything in between is dominated.

## 3. Energy per operation (post-layout netlist + SPEF, 200 MHz virtual clock, random inputs)

`E_prob` = OpenSTA probabilistic activity propagation (input toggle rate 0.5).
`E_vcd` = SDF-annotated gate-level simulation of 32768 random vectors (iverilog), VCD read back into OpenSTA.
Glitch share = 1 − (toggles in a zero-delay simulation) / (toggles in the SDF simulation). Leakage is < 1 nW everywhere.

| design | delay ps | area µm² | E_prob fJ | E_vcd fJ | ratio | toggles/op | glitch |
|---|---:|---:|---:|---:|---:|---:|---:|
| u_xor2a21o | 2290 | 430 | 1281 | 589 | 0.46 | 142 | 30 % |
| all_nand_inv | 2319 | 465 | 1075 | 749 | 0.70 | 259 | 39 % |
| full_gain | 2189 | 507 | 1223 | 777 | 0.64 | 244 | 37 % |
| all_nand_dup12_inv | 2207 | 510 | 1157 | 819 | 0.71 | 282 | 40 % |
| full_eff | 2190 | 514 | 1246 | 825 | 0.66 | 251 | 39 % |
| opt_ds | 2216 | 563 | 1305 | 898 | 0.69 | 283 | 41 % |
| behav_area | 3387 | 724 | 2275 | 1175 | 0.52 | 133 | 29 % |
| all_nand_rsz_2ns | 2252 | 807 | 2105 | 1585 | 0.75 | 321 | 48 % |
| dup12_rsz_2ns | 2294 | 957 | 2660 | 1960 | 0.74 | 334 | 47 % |
| behav_delay | 3043 | 1235 | 3310 | 2365 | 0.71 | 259 | 38 % |
| behav_delay_2ns | 1998 | 1775 | 5065 | 3505 | 0.69 | 303 | 30 % |

## 4. LUT mapping (yosys 0.62 `synth_xilinx`, xc7)

`assign p = a*b` and all three gate-level variants map to exactly 80 LUTs, depth 5. abc re-synthesizes the 8-input function from scratch; no input structure survives.

## 5. Arithmetic-level schedules (research branch)

Same cells, same partial products; only the *order in which columns are compressed* changes.
`src/arith_search.py`; correctness of every schedule is the Lean theorem `ArithEquiv.multiplier_correct`
(`lean/ArithEquiv.lean`, core Lean 4, no Mathlib, axioms `propext` + `Quot.sound` only), and every emitted
netlist is still checked on 256/256 inputs.

Cell-only STA (size-1 cells, output load 10 fF):

| schedule | pp / HA / FA | cells | area µm² | model ps | OpenSTA ps |
|---|---|---:|---:|---:|---:|
| array (row-by-row ripple, = `all_nand_inv`) | nand+inv / nand5 / nand9 | 124 | 465 | 1920 | 1940 |
| Wallace | nand+inv / nand5 / nand9 | 124 | 465 | 1528 | – |
| arrival-greedy (tallest column, earliest bits) | nand+inv / nand5 / nand9 | 124 | 465 | 1524 | – |
| **Dadda** | nand+inv / nand5 / nand9 | 124 | 465 | **1379** | 1393 |
| best of 400 random schedules | nand+inv / xor+and / nand9 | 112 | 450 | 1393 | 1409 |
| array | and2 / xor+and / xor2x2+a21o | 56 | 410 | 2048 | – |
| **Dadda** | and2 / xor+and / xor2x2+a21o | 56 | 410 | **1463** | 1472 |

Assigning the latest-arriving bit to the carry-in pin ("late_to_cin") changed nothing (±10 ps).

Post-layout (LibreLane, SPEF) and glitch-inclusive energy (SDF simulation, 32768 random vectors, 200 MHz):

| design | arrival ps | cells | logic area µm² | wire µm | E_vcd fJ | toggles/op | glitch |
|---|---:|---:|---:|---:|---:|---:|---:|
| **dadda_xa** (Dadda, and2 / xor+and / xor2x2+a21o) | **1662** | 56 | **410** | 713 | **440** | 92 | 25 % |
| dadda_nand9 (Dadda, 9-NAND) | 1688 | 124 | 465 | 975 | 598 | 214 | 31 % |
| rand0_nand9 (best random) | 1704 | 112 | 450 | 931 | 607 | 208 | 32 % |
| all_nand_inv (array, 9-NAND) | 2319 | 124 | 465 | 957 | 749 | 259 | 39 % |
| u_xor2a21o (array, xor2x2+a21o) | 2290 | 72 | 430 | 746 | 589 | 142 | 30 % |
| behav_delay_2ns (standard flow, 2 ns target) | 1998 | 167 | 1775 | 3645 | 3505 | 303 | 30 % |

`dadda_xa` dominates every other design on all three axes: versus the standard flow's fastest result it is
17 % faster, 4.3× smaller and uses 8× less energy per operation; versus the array with the same cells it is
27 % faster and 25 % lower energy at equal area.

Phase 2 (instance-level resize + duplicate, cell-only STA) on top of Dadda buys another 5–7 % for 6–17 % area
(dadda_nand9: 1379 → 1284 ps at +6 %; dadda_xa: 1463 → 1402 ps at +17 %) — the same modest ratio as before.
The schedule is where the big lever is; sizing and duplication remain second-order.

## 6. Scaling: 4 → 32 bits (research branch)

`src/scale_sweep.py` and `src/final_adder_sweep.py`. Cell-only NLDM STA; "tree" = arrival of the last bit
leaving the compression tree, "CPA" = the rest (final carry-propagate adder). Checks: exhaustive for n ≤ 8,
4096 random vectors (bit-parallel) for n ≥ 16; the schedule itself is covered for every width by
`ArithEquiv.multiplier_correct_general`.

| n | schedule | FA | cells | area µm² | delay | tree | CPA | timing eval | check |
|--:|---|---|--:|--:|--:|--:|--:|--:|--:|
| 4 | array | nand9 | 124 | 465 | 1920 ps | 1863 | 57 | 0.01 s | 0.00 s |
| 4 | Dadda | nand9 | 124 | 465 | 1379 ps | 604 | 775 | 0.00 s | 0.00 s |
| 8 | array | nand9 | 600 | 2252 | 4720 ps | 4660 | 60 | 0.02 s | 0.10 s |
| 8 | Wallace | nand9 | 600 | 2252 | 2906 ps | 1727 | 1179 | 0.02 s | 0.09 s |
| 8 | Dadda | nand9 | 600 | 2252 | 2708 ps | 1267 | 1442 | 0.02 s | 0.09 s |
| 16 | array | nand9 | 2608 | 9789 | 10318 ps | 10259 | 60 | 0.10 s | 0.04 s |
| 16 | Wallace | nand9 | 2608 | 9789 | 5375 ps | 2959 | 2416 | 0.10 s | 0.04 s |
| 16 | Dadda | nand9 | 2608 | 9789 | 5190 ps | 2008 | 3182 | 0.10 s | 0.04 s |
| 32 | array | nand9 | 10848 | 40719 | 21515 ps | 21456 | 60 | 0.40 s | 0.11 s |
| 32 | Wallace | nand9 | 10848 | 40719 | 10312 ps | 5441 | 4871 | 0.46 s | 0.12 s |

The search cost is not the problem: one timing evaluation of a 32×32 multiplier (10.8k cells) is 0.4 s in
pure Python, and the random functional check is 0.1 s. What changes with width is *where the delay is*:
the ripple CPA is 56 % of the Dadda delay at 4 bits and 61 % at 16 bits, so the final adder becomes the
lever. Adding a Kogge-Stone final adder (`Builder.kogge_stone`; and2/xor2/a21o prefix network, **not**
covered by the Lean schedule theorem — checked exhaustively / randomly):

| n | FA | final adder | cells | area µm² | delay | CPA |
|--:|---|---|--:|--:|--:|--:|
| 4 | nand9 | ripple | 124 | 465 | 1379 ps | 775 |
| 4 | nand9 | Kogge-Stone | 127 | 651 | 1559 ps | 954 |
| 8 | nand9 | ripple | 600 | 2252 | 2708 ps | 1442 |
| 8 | nand9 | Kogge-Stone | 646 | 2964 | 2377 ps | 1111 |
| 16 | nand9 | ripple | 2608 | 9789 | 5190 ps | 3182 |
| 16 | nand9 | Kogge-Stone | 2793 | 11909 | 3284 ps | 1276 |
| 16 | xor2x2+a21o | ripple | 1184 | 8848 | 6103 ps | 4036 |
| 16 | xor2x2+a21o | Kogge-Stone | 1517 | 11044 | 3409 ps | 1342 |

Kogge-Stone loses at 4 bits (its fan-out costs more than the 3-level ripple it replaces), gains 12 % at 8
bits and 37 % at 16 bits for +22 % area. The right final adder is width-dependent, i.e. one more thing the
search must choose rather than the designer.

### 8×8 placed and routed (LibreLane, SPEF; energy from SDF simulation, 16384 random vectors, 200 MHz)

| design | arrival | cells | logic area µm² | wire µm | E_vcd / op | glitch |
|---|--:|--:|--:|--:|--:|--:|
| m8_array_nand9 (array, 9-NAND) | 5692 ps | 600 | 2252 | 4322 | 1072 fJ | 43 % |
| m8_dadda_nand9 (Dadda + ripple, 9-NAND) | 3505 ps | 600 | 2252 | 5046 | 686 fJ | 28 % |
| **m8_dadda_nand9_ks** (Dadda + Kogge-Stone, 9-NAND) | **3120 ps** | 646 | 2964 | 7223 | 737 fJ | 21 % |
| m8_dadda_xa_ks (Dadda + Kogge-Stone, xor2/a21o) | 3150 ps | 386 | 2770 | 5930 | 714 fJ | 21 % |
| m8_behav_delay_3ns (standard flow, DELAY, 3 ns target) | 3620 ps | 716 | 8288 | 16591 | 4320 fJ | 23 % |

At 8 bits the picture is the same as at 4: re-wiring the same 600 cells from array to Dadda order is 38 %
faster and 36 % lower energy at zero area cost; the standard flow is slower than Dadda+ripple while using
3.7× the area and 6.3× the energy. OpenSTA's probabilistic power estimate is 14–33× above simulation at this
size (it was 1.3–2.2× at 4 bits) — it is unusable as a ranking signal for deep reconvergent logic.
