#!/bin/sh
# Full sky130_fd_sc_hd Liberty (tt, 25C, 1.80V) as packaged by OpenROAD-flow-scripts (Apache-2.0, ~13 MB). Not committed.
set -e
cd "$(dirname "$0")"
curl -sSfL -o sky130_fd_sc_hd__tt_025C_1v80.lib \
  https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/sky130hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib
ls -la sky130_fd_sc_hd__tt_025C_1v80.lib
