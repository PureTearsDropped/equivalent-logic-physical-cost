#!/bin/sh
# Per-cell Liberty tables (JSON form) from google/skywater-pdk-libs-sky130_fd_sc_hd (Apache-2.0). The committed copies were fetched 2026-09-06.
set -e
cd "$(dirname "$0")"
for c in and2 and3 or2 xor2 xnor2 xor3 xnor3 maj3 fa ha a21o a21oi o21ai o21a nand3 nor3 a22o a22oi buf nand2 nor2 inv; do
  for d in 1 2 4; do
    curl -sSfL -o ${c}_${d}.json "https://raw.githubusercontent.com/google/skywater-pdk-libs-sky130_fd_sc_hd/main/cells/${c}/sky130_fd_sc_hd__${c}_${d}__tt_025C_1v80.lib.json"
  done
done
