"""Post-layout summary over flow/results/<design>/ (arrival from OpenSTA max.rpt, logic-only cell area, wirelength)."""
import sys, re, json, collections, glob, os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from paths import FLOW_RESULTS, CELLS_DIR
AREAS = json.load(open(CELLS_DIR / "areas.json"))
DESIGNS = ["all_nand_inv","all_nand_dup12_inv","opt_ds","u_xor2a21o","full_gain","full_eff",
           "all_nand_rsz_2ns","dup12_rsz_2ns","behav_area","behav_delay","behav_delay_2ns"]
def load(d):
    R = FLOW_RESULTS / d
    m = json.load(open(R / "metrics.json"))
    t = open(R / "max.rpt").read()
    arr = max(float(x) for x in re.findall(r"([-\d.]+)\s+data arrival time", t))
    nl = glob.glob(str(R / "*.nl.v"))[0]
    cells = collections.Counter(re.findall(r"sky130_fd_sc_hd__([a-z0-9_]+)", open(nl).read()))
    logic = {k: v for k, v in cells.items() if not k.startswith(("decap", "tap", "fill"))}
    return dict(design=d, arrival_ps=arr * 1000, logic_cells=sum(logic.values()),
                logic_area=sum(AREAS.get(k, 0) * v for k, v in logic.items()),
                wirelength=m["route__wirelength"], cells=logic)
if __name__ == "__main__":
    print(f"{'design':18s} {'arrival':>8s} {'logic':>6s} {'logicA':>7s} {'wire':>6s}  top cells")
    for d in (sys.argv[1:] or DESIGNS):
        r = load(d)
        top = ", ".join(f"{k}:{v}" for k, v in sorted(r["cells"].items(), key=lambda x: -x[1])[:5])
        print(f"{d:18s} {r['arrival_ps']:7.0f}ps {r['logic_cells']:6d} {r['logic_area']:7.0f} {r['wirelength']:6.0f}  {top}")
