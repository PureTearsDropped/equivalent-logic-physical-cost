"""Phase 2 on the Dadda netlist: instance-level resize + duplicate moves (whole-DAG timing)."""
import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *
from optimize_full import phase2
for fa,pp,ha,tag in (('nand9','nand+inv','nand5','dadda_nand9'),('xor2x2+a21o','and2','xor+and','dadda_xa')):
    net,d,a,_=build(sched_dadda,pp=pp,ha=ha,fa=fa)
    for rank in ('gain','eff'):
        n2,h=phase2(net,rank=rank,steps=40)
        nm=f"out/as_{tag}_p2_{rank}.v"; open(nm,"w").write(to_verilog(n2,f"{tag}_p2_{rank}")); s=sta_delay(nm,f"{tag}_p2_{rank}")
        print(f"{tag} phase2[{rank}]: {len(h)-1} moves {d*1000:.0f}->{h[-1][0]*1000:.0f}ps area {a:.0f}->{h[-1][1]:.0f} cells={len(n2.insts)} OpenSTA={s*1000:.0f}ps")
        for tgt in (1.02,1.05,1.10):
            pts=[x for x in h if x[1]<=a*tgt]; print(f"   area<=+{(tgt-1)*100:.0f}%: {min(p[0] for p in pts)*1000:.0f}ps")
