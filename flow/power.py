"""Probabilistic (OpenSTA activity propagation) power on the post-layout netlist + SPEF, identical conditions for all designs.
NOTE: this over-estimates by 1.3-2.2x versus glitch-inclusive simulation and mis-ranks designs; see sim_power.py."""
import sys, re, glob, os, json
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from paths import FLOW_RESULTS, LIB_PATH, run_sta
from summary import DESIGNS, load
PERIOD = 5.0  # ns (200 MHz virtual clock); energy/op = dynamic power * period
def power_tcl(d, activity):
    R = FLOW_RESULTS / d
    nl = glob.glob(str(R / "*.nl.v"))[0]; spef = glob.glob(str(R / "*.spef"))[0]
    top = re.search(r"module\s+(\w+)", open(nl).read()).group(1)
    return f"""read_liberty {LIB_PATH}
read_verilog {nl}
link_design {top}
read_spef {spef}
create_clock -name vclk -period {PERIOD}
set_input_delay 0 -clock vclk [all_inputs]
set_output_delay 0 -clock vclk [all_outputs]
set_input_transition 0.05 [all_inputs]
set_load 0.010 [all_outputs]
{activity}
report_power
exit
"""
def parse_power(out):
    m = re.search(r"Total\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)\s+([\d.e+-]+)", out)
    if not m: raise RuntimeError(out[-800:])
    internal, switching, leak, total = map(float, m.groups())
    return (internal + switching) * PERIOD * 1e-9, leak   # J per op, W
if __name__ == "__main__":
    print(f"{'design':18s} {'delay':>7s} {'logicA':>7s} {'Edyn/op':>9s} {'Pleak':>8s} {'E*delay':>9s}")
    for d in (sys.argv[1:] or DESIGNS):
        r = load(d)
        e, leak = parse_power(run_sta(power_tcl(d, "set_power_activity -input -activity 0.5 -duty 0.5")))
        print(f"{d:18s} {r['arrival_ps']:6.0f}ps {r['logic_area']:7.0f} {e*1e15:8.1f}fJ {leak*1e9:7.2f}nW {e*1e15*r['arrival_ps']/1000:8.0f}")
