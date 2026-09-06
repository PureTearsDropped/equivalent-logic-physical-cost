"""Per-stage post-layout setup slack of a pipelined exp design (flow/results/<design>): OpenSTA on netlist+SPEF."""
import sys, os, re, glob, collections; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','src'))
from paths import run_sta, LIB_PATH, FLOW_RESULTS
from exp_f32_gates import build_exp
from exp_f32_deep import build_exp_deep
from fullcell import buffer_high_fanout
def stage_slack(design, period):
    net=(build_exp_deep() if 'deep' in design else build_exp(pipe=True)); buffer_high_fanout(net)
    stage_of={f"g{ii}":inst['stage'] for ii,inst in enumerate(net.insts) if inst['cell'].startswith('dfxtp')}
    last=max(stage_of.values())+1
    R=FLOW_RESULTS/design; nl=glob.glob(str(R/'*.nl.v'))[0]; spef=glob.glob(str(R/'*.spef'))[0]
    top=re.search(r"module\s+(\w+)",open(nl).read()).group(1)
    tcl=f"""read_liberty {LIB_PATH}
read_verilog {nl}
link_design {top}
read_spef {spef}
create_clock -name clk -period {period} [get_ports clk]
set_input_delay 0 -clock clk [delete_from_list [all_inputs] [get_ports clk]]
set_output_delay 0 -clock clk [all_outputs]
set_input_transition 0.05 [delete_from_list [all_inputs] [get_ports clk]]
set_load 0.010 [all_outputs]
report_checks -path_delay max -group_count 3000 -endpoint_count 1 -format end
exit
"""
    out=run_sta(tcl,timeout=900); worst=collections.defaultdict(lambda:99.0)
    for l in out.splitlines():
        m=re.match(r"\s*(\S+?)(?:/D)?\s+\(.*?\)\s+([-\d.]+)\s+([-\d.]+)\s+([-\d.]+)\s+\((MET|VIOLATED)\)",l)
        if not m: continue
        ep=m.group(1); slack=float(m.group(4)); inst=ep.split('/')[0]
        st=stage_of.get(inst, last if (ep.startswith('y[') or ep=='decided') else None)
        if st is None: continue
        worst[st-1]=min(worst[st-1],slack)
    print(f"{design}: post-layout stage times at {period} ns clock (tt):")
    for st in sorted(worst): print(f"  stage {st}: needs {period-worst[st]:5.2f} ns")
    print(f"  => min period {max(period-w for w in worst.values()):.2f} ns ({1000/max(period-w for w in worst.values()):.0f} MHz)")
if __name__=="__main__": stage_slack(sys.argv[1], float(sys.argv[2]) if len(sys.argv)>2 else 8.0)
