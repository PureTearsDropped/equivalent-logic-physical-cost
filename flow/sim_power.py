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
def toggles(vcd_path, input_names=("a", "b")):
    """count value changes on non-input nets, streaming (VCDs of large designs are gigabytes)"""
    ids = {}; skip = set(); total = 0; in_defs = True
    with open(vcd_path) as f:
        for line in f:
            if in_defs:
                if line.startswith("$var"):
                    parts = line.split(); ids[parts[3]] = parts[4]
                    if parts[4].split("[")[0] in input_names: skip.add(parts[3])
                elif line.startswith("$enddefinitions"): in_defs = False
                continue
            c = line[0]
            if c in "01xz":
                if line[1:].strip() not in skip: total += 1
            elif c == "b":
                if line.split()[1] not in skip: total += 1
    return total

def ports_of(pnl):
    """(inputs, outputs) as [(name, width)] from the powered netlist header (VPWR/VGND excluded)."""
    src = open(pnl).read(); hdr = re.search(r"module\s+\w+\s*\((.*?)\);", src, re.S).group(1)
    body = src[:src.find("endmodule")]
    ins, outs = [], []
    for d, w, nm in re.findall(r"^\s*(input|output)\s+(?:\[(\d+):0\]\s+)?(\w+)\s*;", body, re.M):
        (ins if d == "input" else outs).append((nm, int(w) + 1 if w else 1))
    return ins, outs

def simulate(d, nvec, timed, outdir):
    R = FLOW_RESULTS / d
    pnl = glob.glob(str(R / "*.pnl.v"))[0]; sdf = glob.glob(str(R / "*.sdf"))[0]
    top = re.search(r"module\s+(\w+)", open(pnl).read()).group(1)
    ins, outs = ports_of(pnl)
    tag = "timed" if timed else "zerodelay"; vcd = f"{outdir}/{d}_{tag}.vcd"
    annotate = f'$sdf_annotate("{sdf}", dut);' if timed else ""
    decl = "".join(f"  reg [{w-1}:0] {nm};\n" for nm, w in ins) + "".join(f"  wire [{w-1}:0] {nm};\n" for nm, w in outs)
    conn = ", ".join(f".{nm}({nm})" for nm, _ in ins + outs)
    init = "".join(f"{nm}=0; " for nm, _ in ins)
    # signed-digit pairs (xP,xN): keep digits canonical (never both 1)
    names = {nm for nm, _ in ins}; stim = []
    has_clk = "clk" in names
    for nm, w in ins:
        if nm == "clk": continue
        if nm.endswith("N") and nm[:-1] + "P" in names: continue
        if os.environ.get(f"STIM_{nm}"):                      # custom stimulus expression; `t` is a fresh $random
            stim.append(f"t=$random(seed); {nm}={os.environ[f'STIM_{nm}']};")
        elif nm.endswith("P") and nm[:-1] + "N" in names:
            stim.append(f"{nm}=$random(seed); t=$random(seed); {nm[:-1]}N=t & ~{nm};")
        else: stim.append(f"{nm}=$random(seed);")
    tb = f"""`timescale 1ns/1ps
module tb;
{decl}  integer i, seed; reg [63:0] t; supply1 vpwr; supply0 vgnd;
  {top} dut({conn},.VPWR(vpwr),.VGND(vgnd));
  {"always #(" + str(PERIOD/2) + ") clk = ~clk;" if has_clk else ""}
  initial begin
    {annotate}
    $dumpfile("{vcd}"); $dumpvars(0, dut);
    seed=12345; {init}{"clk=0; " if has_clk else ""}#{PERIOD};
    for (i=0;i<{nvec};i=i+1) begin {" ".join(stim)} #{PERIOD}; end
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
        pnl = glob.glob(str(FLOW_RESULTS / d / "*.pnl.v"))[0]; innames = tuple(nm for nm, _ in ports_of(pnl)[0])
        vcd = simulate(d, nvec, True, outdir); tg = toggles(vcd, innames)
        tz = toggles(simulate(d, nvec, False, outdir), innames)
        ep, _ = parse_power(run_sta(power_tcl(d, "set_power_activity -input -activity 0.5 -duty 0.5")))
        ev, _ = parse_power(run_sta(power_tcl(d, f"read_power_activities -scope tb/dut -vcd {vcd}")))
        print(f"{d:18s} {r['arrival_ps']:6.0f}ps {ep*1e15:7.1f}fJ {ev*1e15:7.1f}fJ {ev/ep:6.2f} {tg/nvec:10.1f} {(1-tz/tg)*100:7.0f}%", flush=True)
