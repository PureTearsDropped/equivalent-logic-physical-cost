import sys, subprocess, re, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pa4x4 import *
YS=sys.argv[1]
def generic_verilog(net,outs,name):
    L=[f"module {name}(input [3:0] a, input [3:0] b, output [7:0] p);"]
    n=len(net.nodes); L.append("  wire "+", ".join(f"n{i}" for i in range(n))+";")
    for i in range(4): L.append(f"  assign n{i} = a[{i}];")
    for i in range(4): L.append(f"  assign n{4+i} = b[{i}];")
    for i,nd in enumerate(net.nodes):
        if nd.op=="IN": continue
        op="&" if nd.op=="NAND" else "|"
        L.append(f"  assign n{i} = ~(n{nd.a} {op} n{nd.b});")
    for k,o in enumerate(outs): L.append(f"  assign p[{k}] = n{o};")
    L.append("endmodule"); return "\n".join(L)
open('behav.v','w').write("module behav(input [3:0] a, input [3:0] b, output [7:0] p); assign p = a*b; endmodule\n")
srcs=[('behav','behav.v')]
for name,fa in [("gco",GATE_COUNT_ONLY_FA),("aa",ARRIVAL_AWARE_MIXED_FA),("allnand",ALL_NAND_FA)]:
    net,outs=build_array4(fa); open(f"{name}_g.v","w").write(generic_verilog(net,outs,name)); srcs.append((name,f"{name}_g.v"))
print(f"{'design':8s} {'LUTs':>5s} {'LUT-depth':>9s}   (yosys synth_xilinx xc7, abc default)  | flatten-only: cells depth")
for name,f in srcs:
    scr=f"read_verilog {f}; synth_xilinx -family xc7 -noclkbuf -nodsp -nobram -nocarry; stat; ltp -noff"
    r=subprocess.run([YS,"-p",scr],capture_output=True,text=True)
    o=r.stdout+r.stderr
    luts=sum(int(m.group(2)) for m in re.finditer(r"(LUT\d)\s+(\d+)",o))
    dep=re.search(r"length=(\d+)",o)
    # also raw gate count/depth via simple opt (no abc)
    scr2=f"read_verilog {f}; proc; flatten; opt -fast; techmap; opt -fast; stat; ltp -noff"
    r2=subprocess.run([YS,"-p",scr2],capture_output=True,text=True); o2=r2.stdout+r2.stderr
    cells=re.search(r"Number of cells:\s*(\d+)",o2); dep2=re.search(r"length=(\d+)",o2)
    print(f"{name:8s} {luts:5d} {dep.group(1) if dep else '?':>9s}   | {cells.group(1) if cells else '?':>5s} {dep2.group(1) if dep2 else '?':>5s}")
    if not dep: print(o[-800:])
