"""Dadda tree + ripple vs Dadda tree + Kogge-Stone final adder, n = 4, 8, 16."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *
ns=[int(x) for x in sys.argv[1:]] or [4,8,16]
print(f"{'n':>3s} {'FA':16s} {'final':7s} {'cells':>6s} {'area':>7s} {'delay':>7s} {'tree':>6s} {'CPA':>6s}")
for n in ns:
    for fa,pp,ha in (('nand9','nand+inv','nand5'),('xor2x2+a21o','and2','xor+and')):
        for final in ('ripple','ks'):
            net,d,a,extra=build(sched_dadda,n=n,pp=pp,ha=ha,fa=fa,late_to_cin=False,final=final)
            tree=extra[1]
            print(f"{n:3d} {fa:16s} {final:7s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps {tree*1000:5.0f}ps {(d-tree)*1000:5.0f}ps",flush=True)
            os.makedirs("out",exist_ok=True); nm=f"fs{n}_dadda_{'nand9' if fa=='nand9' else 'xa'}_{final}"; open(f"out/{nm}.v","w").write(to_verilog(net,nm))
