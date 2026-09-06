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
| behav_booth_2ns (standard flow + `SYNTH_MUL_BOOTH`, 2 ns target) | 2150 | 210 | 2281 | 4051 | 5335 | 488 | 32 % |

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
| 32 | Dadda | nand9 | 10848 | 40719 | 10153 ps | 2706 | 7448 | 0.42 s | 0.11 s |

The search cost is not the problem: one timing evaluation of a 32×32 multiplier (10.8k cells) is 0.4 s in
pure Python, and the random functional check is 0.1 s. What changes with width is *where the delay is*:
the ripple CPA is 56 % of the Dadda delay at 4 bits, 61 % at 16 and 73 % at 32, so the final adder becomes the
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
| m8_behav_booth_3ns (standard flow + `SYNTH_MUL_BOOTH`, 3 ns target) | 3408 ps | 663 | 6838 | 15378 | 10670 fJ | 30 % |

At 8 bits the picture is the same as at 4: re-wiring the same 600 cells from array to Dadda order is 38 %
faster and 36 % lower energy at zero area cost; the standard flow is slower than Dadda+ripple while using
3.7× the area and 6.3× the energy. The flow's Booth option (radix-4 recoding) helps it at 8 bits (3408 ps, 6838 µm²) but it
still loses to Dadda + Kogge-Stone on delay at 2.3× the area, and its recoding logic toggles so much (999 toggles/op)
that it uses 14× the energy; at 4 bits Booth is worse than the plain flow on every axis. OpenSTA's probabilistic power estimate is 14–33× above simulation at this
size (it was 1.3–2.2× at 4 bits) — it is unusable as a ranking signal for deep reconvergent logic.

## 7. Representation sweep: dot products Σₖ aₖ·bₖ (research branch)

`src/rep_sweep.py`, 8-bit operands, K pairs, cells and2 / xor+and / xor2,xor2,a21o (size 1), cell-only NLDM STA.
*binary*: every product is resolved to binary (compression tree + CPA), then the K numbers are added with a tree of
CPAs. *carrysave*: all K partial-product sets go into one compression tree, one CPA at the end. *redundant*: the tree
only — the result stays as two rows (no CPA), which is the form the total-arith signed-digit / carry-save datapaths keep.
Every netlist checked on 2048 random vectors; the schedule is covered by `dot_product_correct` / `dot_product_redundant`
in `lean/ArithEquiv.lean` (Kogge-Stone excepted).

| K | representation | final adder | cells | area µm² | delay |
|--:|---|---|--:|--:|--:|
| 1 | binary = carrysave | ripple | 272 | 2022 | 3027 ps |
| 1 | binary = carrysave | Kogge-Stone | 386 | 2770 | 2494 ps |
| 1 | redundant | – | 218 | 1600 | 1440 ps |
| 2 | binary | Kogge-Stone | 966 | 6893 | 3551 ps |
| 2 | carrysave | Kogge-Stone | 724 | 5291 | 3195 ps |
| 2 | redundant | – | 530 | 3939 | 2138 ps |
| 4 | binary | ripple | 1278 | 9572 | 4229 ps |
| 4 | binary | Kogge-Stone | 2144 | 15262 | 4609 ps |
| 4 | carrysave | ripple | 1236 | 9256 | 4418 ps |
| 4 | carrysave | Kogge-Stone | 1382 | 10217 | 3696 ps |
| 4 | redundant | – | 1170 | 8741 | 2639 ps |
| 8 | binary | ripple | 2626 | 19690 | 4831 ps |
| 8 | binary | Kogge-Stone | 4518 | 32125 | 5787 ps |
| 8 | carrysave | ripple | 2522 | 18909 | 5086 ps |
| 8 | carrysave | Kogge-Stone | 2682 | 19963 | 4499 ps |
| 8 | redundant | – | 2452 | 18363 | 3306 ps |

Same function, three representations, measured in time and gates: at K = 4 the carry-save representation is 20 % faster
and 33 % smaller than binary (both with Kogge-Stone), and keeping the result redundant is 43 % faster and 43 % smaller.
A tree of Kogge-Stone adders (binary, K = 8) is *slower* than ripple — the prefix networks' fan-out compounds — while one
Kogge-Stone at the end of a carry-save tree is the best resolved form. The representation, not the gate-level structure,
is the first-order variable.

### What Lean produces

- `lean/ArithEquiv.lean` (core Lean 4): the bit-level identity for any width — every FA/HA schedule preserves the weighted
  sum (`schedule_preserves`), partial products are the product (`ppAll_value`), merged partial products are the dot
  product (`ppDot_value`), and the two-row redundant output is exact (`dot_product_redundant`).
- `lean/mathlib/RepDemo.lean` (Mathlib): `ring_nf` rewrites the array order and the Dadda grouping to one canonical
  polynomial, i.e. Lean itself *outputs* the representation-independent form and decides equality of any two arithmetic
  decompositions automatically — at any width, where truth tables are unavailable.

## 8. Signed-digit (total-arith) multiplier, 10 digits (research branch)

`src/sd_tree.py`. Digits are (p,n) pairs with value p − n (total-arith-hardware's encoding). `sd10_tah` is
total-arith-hardware's `sd_mult10.sv` (generic gates, auto-emitted) imported, constant-folded (≈2 100 of its
11 670 assigns were `x & 1'b0`, `x ^ 1'b0`, …) and mapped 1:1 onto sky130 and2/or2/xor2/inv. Ours keeps two
rails (P: xP·yP + xN·yN, N: xP·yN + xN·yP, merged with or2 — exact for canonical inputs), compresses each
rail with a Dadda schedule, and then either stops (borrow-save, redundant), resolves each rail (Kogge-Stone)
or canonicalises (their ripple compressor; or two borrow-lookahead subtractors P−N / N−P sharing the
propagate signals, selected by the sign). Lean: `lean/SignedDigit.lean` — any pair of rail schedules
preserves the signed value, the digit-product identity, and their canonical 3:2 compressor is exact and
canonical (64-case decide). The borrow-lookahead canonicaliser is not yet in Lean (random-checked only).
All designs checked on 1024 random canonical digit vectors.

Cell-only (NLDM):

| design | output contract | cells | area µm² | delay |
|---|---|--:|--:|--:|
| sd_mult10 (total-arith, folded) | canonical (zP,zN) | 4742 | 27659 | 7320 ps |
| ours, canonical ripple | canonical (zP,zN) | 1432 | 9819 | 6594 ps |
| ours, borrow-lookahead + select | canonical (zP,zN) | 2085 | 14420 | 4769 ps |
| ours, Kogge-Stone per rail | borrow-save (zP,zN), may contain (1,1) | 1610 | 11228 | 3141 ps |
| ours, tree only | four rows (two per rail) | 1140 | 7965 | 1946 ps |

Placed and routed (LibreLane, SPEF) with glitch-inclusive energy (8192 random canonical vectors, 200 MHz):

| design | arrival | cells | logic area µm² | wire µm | E_vcd / op | glitch |
|---|--:|--:|--:|--:|--:|--:|
| sd10_tah (total-arith sd_mult10) | 8659 ps | 4769 | 27757 | 53635 | 32.3 pJ | 41 % |
| sd10_canon (ours, canonical ripple) | 7989 ps | 1436 | 9834 | 26254 | 13.1 pJ | 32 % |
| sd10_canon_ks (ours, canonical, borrow-lookahead) | 6915 ps | 2086 | 14423 | 43504 | 24.2 pJ | 31 % |
| **sd10_bs_ks** (ours, borrow-save, Kogge-Stone per rail) | **4166 ps** | 1614 | 11241 | 30630 | **13.8 pJ** | 27 % |

Same contract as sd_mult10 (canonical digits out): 8 % faster at 2.8× less area and 2.5× less energy with the
ripple canonicaliser, or 20 % faster at 1.9× less area and 1.3× less energy with the parallel one. Relaxing the
contract to borrow-save (the consumer tolerates the redundant zero (1,1)) gives 2.1× the speed at 2.5× less
area and 2.3× less energy. The canonical-per-step compressor (18 gates, 8 of them the rail subtraction) is
the signed-digit analogue of resolving carries at every step; moving canonicalisation to the boundary is the
same lesson as carry-save. Wires hurt the prefix networks most (canon_ks: 4769 → 6915 ps).

FPGA cross-check (yosys 0.62 `synth_xilinx` xc7, abc default; LUT count and LUT depth only — no place and route):

| design | LUTs | LUT depth |
|---|--:|--:|
| sd_mult10 (total-arith, as emitted) | 4182 | 25 |
| ours, canonical ripple | 2014 | 31 |
| ours, canonical borrow-lookahead | 3482 | 24 |
| ours, borrow-save Kogge-Stone | 2727 | 19 |
| ours, tree only (four rows) | 2230 | 11 |

On the FPGA target the gain is smaller and contract-dependent: same contract, either half the LUTs at 6 more
levels (ripple canonicaliser) or 17 % fewer LUTs at one level less (borrow-lookahead); borrow-save output gives
35 % fewer LUTs and 24 % fewer levels. abc cannot collapse a 40-input function, so structure survives here,
unlike the 4×4 case.

## 9. Binary {0,1} vs signed-digit {−1,0,+1} at equal numeric range (research branch)

`src/signed_binary.py`: two's-complement multiplier (Baugh–Wooley partial products, Dadda tree, Kogge-Stone), 11 bits
(range ±1024 ≥ the 10-digit signed-digit range ±1023), cell-only NLDM STA, checked on 2048 random signed vectors.

| design | output | cells | area µm² | delay |
|---|---|--:|--:|--:|
| binary 11×11, Dadda + Kogge-Stone | two's complement | 770 | 5485 | 2997 ps |
| binary 11×11, Dadda + ripple | two's complement | 564 | 4129 | 4368 ps |
| binary 11×11, tree only | carry-save (two rows) | 484 | 3505 | 1789 ps |
| signed-digit 10 digits, two rails, Kogge-Stone per rail (§8) | borrow-save (zP,zN) | 1610 | 11228 | 3141 ps |
| signed-digit 10 digits, canonical ripple (§8) | canonical digits | 1432 | 9819 | 6594 ps |
| signed-digit 10 digits, tree only (§8) | four rows | 1140 | 7965 | 1946 ps |
| total-arith sd_mult10 (§8) | canonical digits | 4742 | 27659 | 7320 ps |

At equal range the binary multiplier costs about half the cells and area of the two-rail signed-digit one at the same
delay (2997 vs 3141 ps), and 2.2× less delay than the canonical-output signed-digit design at 1.8× less area. Binary
carry-save (tree only) gives the same carry-free accumulation as signed-digit borrow-save at 0.44× the area. What the
signed-digit form buys is representational: negation by wiring, symmetric digits, and total-arith's flag semantics
(sign-unknown, structural zero) — not speed or area.

## 10. Correctly rounded binary32 exp as hardware (research branch, `transcend/`)

Spec: 64-entry table 2^(j/64), |r| < ln2/128, degree-6 Taylor evaluated by Estrin in 60-bit fixed point (+8 guard
bits), every product = partial-product rows truncated at grid index < 0, Ziv decision at the exit (midpoint distance
> 40 units of 2^-60), **no fallback stage**. `exp_f32_spec_v3.jl` sweeps every in-range binary32 input against MPFR:
526,392,936 inputs, 0 mismatches, 0 undecided, minimum midpoint distance 298 units (7.5× the error bound).
`exp_f32_gates.py` builds the sky130 netlist from the same integer spec; the netlist was simulated on all
526,392,936 inputs against the spec's outputs: 0 mismatches (`exp_f32_gates_exhaustive_part{1,2}.log`).

Placed and routed (LibreLane, sky130, tt corner, my STA on the routed netlist + SPEF):

| design | stages | flops | cells | logic area µm² | wire m | clock / latency |
|---|--:|--:|--:|--:|--:|---|
| combinational, 1× cells | – | 0 | 61,647 | 447k | 1.57 | 64.4 ns (cell-only 37.3) |
| 7-stage, standard placement | 7 | 786 | 62,903 | 470k | 1.70 | 10.6 ns (94 MHz) |
| 7-stage, timing-driven placement, 60 % util, pins ordered | 7 | 786 | 63,241 | 470k | 1.63 | 9.6 ns (104 MHz) |
| 7-stage + OpenROAD resizer (8 ns target) | 7 | 786 | 66,031 | 498k | 1.84 | 9.6 ns; hold fixed with 1,641 delay buffers; 1,137 gates upsized, "unable to repair" |
| **15-stage (tree / Kogge-Stone split, exit split)** | 15 | 2,207 | 60,929 | 482k | 1.68 | **6.46 ns (155 MHz)** |
| everything left to the standard flow (generic Verilog of the 15-stage design → abc DELAY + resizer + CTS, 6 ns target) | 15 | 2,142 | 82,996 | 710k | 2.74 | 6.99 ns (143 MHz); 27,444 buffers |

Per-stage post-layout times of the 15-stage design: compression-tree stages 6.1–6.5 ns, Kogge-Stone stages 2.4–3.8 ns,
exit 4.2 + 5.9 ns. Placement alone bought 10 %; the resizer nothing; splitting the multiplies bought 33 %. Handing the
whole design to the standard flow gives a design 8 % slower and 47 % larger than the hand-structured 1× netlist.
Existing gate-level exp in total-arith-hardware (not correctly rounded): 270k gates, depth 791.
