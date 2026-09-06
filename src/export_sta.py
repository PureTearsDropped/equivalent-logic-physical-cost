import sys, copy, subprocess, re, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from paths import LIB_PATH, run_sta as _run_sta
from pa4x4 import *
from sky130_timing import nldm_timing, greedy, NAND, NOR, INV
import sky130_timing as ST

def to_verilog(net,outs,name,use_inv=False,size=None):
    """size: optional dict node->drive (1,2,4)"""
    L=[f"module {name}(input [3:0] a, input [3:0] b, output [7:0] p);"]
    n=len(net.nodes)
    wires=[f"n{i}" for i in range(n)]
    L.append("  wire "+", ".join(wires[8:])+";")
    for i in range(4): L.append(f"  assign n{i} = a[{i}];")
    for i in range(4): L.append(f"  assign n{4+i} = b[{i}];")
    for i,nd in enumerate(net.nodes):
        if nd.op=="IN": continue
        d=(size or {}).get(i,1)
        if use_inv and nd.a==nd.b:
            L.append(f"  sky130_fd_sc_hd__inv_{d} g{i} (.A(n{nd.a}), .Y(n{i}));")
        else:
            cell="nand2" if nd.op=="NAND" else "nor2"
            L.append(f"  sky130_fd_sc_hd__{cell}_{d} g{i} (.A(n{nd.a}), .B(n{nd.b}), .Y(n{i}));")
    for k,o in enumerate(outs): L.append(f"  assign p[{k}] = n{o};")
    L.append("endmodule")
    return "\n".join(L)

def sta_delay(vfile,top):
    tcl=f"""
read_liberty {LIB_PATH}
read_verilog {vfile}
link_design {top}
set_input_transition 0.05 [all_inputs]
set_load 0.010 [all_outputs]
set_input_delay 0 [all_inputs]
report_checks -unconstrained -path_delay max -digits 4
exit
"""
    out=_run_sta(tcl)
    m=re.search(r"([-\d.]+)\s+data arrival time",out)
    return (float(m.group(1)) if m else None), out

if __name__=="__main__":
    for use_inv in (False,True):
        print(f"\n### tied-NAND as {'inv_1' if use_inv else 'nand2_1'}")
        for name,fa in [("gate_count_only",GATE_COUNT_ONLY_FA),("arrival_aware",ARRIVAL_AWARE_MIXED_FA),("all_nand",ALL_NAND_FA)]:
            net,outs=build_array4(fa)
            mine,_,_,_=nldm_timing(net,outs,use_inv=use_inv)
            nm=name+("_inv" if use_inv else ""); v=to_verilog(net,outs,nm,use_inv); open(f"{nm}.v","w").write(v)
            sta,out=sta_delay(f"{nm}.v",nm)
            print(f"  {name:16s} mine={mine*1000:7.1f}ps  OpenSTA={sta*1000 if sta else float('nan'):7.1f}ps  diff={(sta-mine)*1000 if sta else float('nan'):+.1f}ps")
            if sta is None: print(out[-1500:])
        # duplicated all-NAND via my greedy (rebuild net by re-running greedy that returns net)
    # greedy returning final net
    def greedy_net(net,outputs,steps=12,**kw):
        cur=copy.deepcopy(net)
        for _ in range(steps):
            d,a,loads,sinks=nldm_timing(cur,outputs,**kw); best=None
            for nid,nd in enumerate(cur.nodes):
                if nd.op=="IN": continue
                s=[x for x in sinks[nid] if x[0]!="OUT"]; m=len(s)
                if m<2 or m>6: continue
                for mask in range(1,(1<<m)-1):
                    sub=[s[k] for k in range(m) if (mask>>k)&1]
                    if len(sub)>m-len(sub) or (len(sub)==m-len(sub) and not mask&1): continue
                    c=duplicate_and_rewire(cur,nid,sub); dc,ac,_,_=nldm_timing(c,outputs,**kw)
                    g=d-dc
                    if g>1e-9 and (best is None or (g,-ac)>best[0]): best=((g,-ac),c,dc,ac)
            if best is None: break
            cur=best[1]
        return cur
    net,outs=build_array4(ALL_NAND_FA)
    for use_inv in (False,True):
        dup=greedy_net(net,outs,12,use_inv=use_inv); verify_array4(dup,outs)
        mine,_,_,_=nldm_timing(dup,outs,use_inv=use_inv)
        nm=f"all_nand_dup12{'_inv' if use_inv else ''}"; open(f"{nm}.v","w").write(to_verilog(dup,outs,nm,use_inv))
        sta,out=sta_delay(f"{nm}.v",nm)
        print(f"  {nm:20s} gates={len(dup.nodes)-8} mine={mine*1000:7.1f}ps  OpenSTA={sta*1000:7.1f}ps  diff={(sta-mine)*1000:+.1f}ps")
