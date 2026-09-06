"""Glitch-inclusive energy per operation: SDF-annotated gate-level simulation (iverilog) -> VCD -> OpenSTA read_power_activities.
Requires: iverilog, OpenSTA ($STA), and $PDK_VERILOG pointing at the sky130_fd_sc_hd verilog dir (sky130_fd_sc_hd.v, primitives.v).
Gotchas found the hard way: iverilog needs -gspecify or SDF is silently ignored; the power-pin-less cell models fail to
elaborate under -gspecify (lpflow_bleeder references VPWR), so the powered netlist (*.pnl.v) + -DUSE_POWER_PINS is used."""
import sys, re, glob, os, subprocess
from collections import Counter
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from paths import FLOW_RESULTS, PDK_VERILOG, run_sta
from summary import DESIGNS, load
from power import power_tcl, parse_power, PERIOD
def toggles(vcd_path):
    vcd = open(vcd_path).read(); ids = {}
    for m in re.finditer(r"\$var\s+\w+\s+\d+\s+(\S+)\s+(\S+)", vcd): ids.setdefault(m.group(1), m.group(2))
    cnt = Counter(re.findall(r"^[01xz](\S+)$", vcd.split("$enddefinitions")[1], re.M))
    return sum(c for i, c in cnt.items() if not ids.get(i, "").startswith(("a", "b")))
def simulate(d, nvec, timed, outdir):
    R = FLOW_RESULTS / d
    pnl = glob.glob(str(R / "*.pnl.v"))[0]; sdf = glob.glob(str(R / "*.sdf"))[0]
    top = re.search(r"module\s+(\w+)", open(pnl).read()).group(1)
    tag = "timed" if timed else "zerodelay"; vcd = f"{outdir}/{d}_{tag}.vcd"
    annotate = f'$sdf_annotate("{sdf}", dut);' if timed else ""
    tb = f"""`timescale 1ns/1ps
module tb;
  reg [3:0] a,b; wire [7:0] p; integer i, seed; supply1 vpwr; supply0 vgnd;
  {top} dut(.a(a),.b(b),.p(p),.VPWR(vpwr),.VGND(vgnd));
  initial begin
    {annotate}
    $dumpfile("{vcd}"); $dumpvars(0, dut);
    seed=12345; a=0; b=0; #{PERIOD};
    for (i=0;i<{nvec};i=i+1) begin a=$random(seed); b=$random(seed); #{PERIOD}; end
    $finish;
  end
endmodule
"""
    tbf = f"{outdir}/{d}_{tag}_tb.v"; open(tbf, "w").write(tb)
    flags = ["-gspecify"] if timed else ["-DFUNCTIONAL"]
    subprocess.run(["iverilog", "-g2012", *flags, "-DUSE_POWER_PINS", "-o", f"{outdir}/{d}_{tag}.vvp", tbf, pnl,
                    f"{PDK_VERILOG}/primitives.v", f"{PDK_VERILOG}/sky130_fd_sc_hd.v"], check=True, capture_output=True, text=True)
    subprocess.run(["vvp", f"{outdir}/{d}_{tag}.vvp"], check=True, capture_output=True, text=True)
    return vcd
if __name__ == "__main__":
    nvec = int(sys.argv[1]) if len(sys.argv) > 1 else 32768
    outdir = os.environ.get("SIM_OUT", "sim_out"); os.makedirs(outdir, exist_ok=True)
    assert PDK_VERILOG, "set PDK_VERILOG to the sky130_fd_sc_hd verilog directory"
    print(f"{'design':18s} {'delay':>7s} {'E_prob':>8s} {'E_vcd':>8s} {'ratio':>6s} {'toggles/op':>10s} {'glitch%':>8s}")
    for d in (sys.argv[2:] or DESIGNS):
        r = load(d)
        vcd = simulate(d, nvec, True, outdir); tg = toggles(vcd)
        tz = toggles(simulate(d, nvec, False, outdir))
        ep, _ = parse_power(run_sta(power_tcl(d, "set_power_activity -input -activity 0.5 -duty 0.5")))
        ev, _ = parse_power(run_sta(power_tcl(d, f"read_power_activities -scope tb/dut -vcd {vcd}")))
        print(f"{d:18s} {r['arrival_ps']:6.0f}ps {ep*1e15:7.1f}fJ {ev*1e15:7.1f}fJ {ev/ep:6.2f} {tg/nvec:10.1f} {(1-tz/tg)*100:7.0f}%", flush=True)
