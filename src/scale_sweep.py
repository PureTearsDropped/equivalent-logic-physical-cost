"""Scaling sweep: n x n multipliers, array vs Wallace vs Dadda vs arrival-greedy, cell-only NLDM timing.
Reports cells, area, model delay, the share of delay spent in the final ripple adder, timing-eval cost, and check time."""
import sys, os, time; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *
ns=[int(x) for x in sys.argv[1:]] or [4,8,16]
print(f"{'n':>3s} {'sched':12s} {'FA':16s} {'cells':>6s} {'area':>7s} {'delay':>7s} {'tree':>6s} {'CPA':>6s} {'t_eval':>7s} {'t_check':>8s}")
for n in ns:
    for fa,pp,ha in (('nand9','nand+inv','nand5'),('xor2x2+a21o','and2','xor+and')):
        for name,s in (("array",sched_array),("wallace",sched_wallace),("dadda",sched_dadda),("greedy_time",sched_greedy_time)):
            if n>=32 and name=="greedy_time": continue
            t0=time.time(); b=Builder(pp=pp,ha=ha,fa=fa,n=n,late_to_cin=False); s(b); net=b.ripple(); t_build=time.time()-t0
            t0=time.time(); d,a,_,_=timing(net); t_eval=time.time()-t0
            t0=time.time(); (verify(net) if n<=8 else verify_random(net,4096)); t_chk=time.time()-t0
            print(f"{n:3d} {name:12s} {fa:16s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps {b.tree_delay*1000:5.0f}ps {(d-b.tree_delay)*1000:5.0f}ps {t_eval:6.2f}s {t_chk:7.2f}s{'*' if n>8 else ''}",flush=True)
            if name in ("array","dadda"):
                os.makedirs("out",exist_ok=True); nm=f"as{n}_{name}_{'nand9' if fa=='nand9' else 'xa'}"; open(f"out/{nm}.v","w").write(to_verilog(net,nm))
print("* = 4096 random vectors (exhaustive infeasible); correctness of the schedule itself is the Lean theorem")
