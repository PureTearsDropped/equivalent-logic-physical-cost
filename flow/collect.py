"""Copy the artifacts summary.py/power.py/sim_power.py need from a LibreLane run dir into flow/results/<design>/."""
import sys, glob, os, shutil
here=os.path.dirname(os.path.abspath(__file__))
for d in sys.argv[1:]:
    runs=sorted(glob.glob(f"{here}/designs/{d}/runs/RUN_*")); R=runs[-1]
    out=f"{here}/results/{d}"; os.makedirs(out,exist_ok=True)
    S=sorted(glob.glob(f"{R}/*stapostpnr*"))[-1]+"/nom_tt_025C_1v80"
    files=[f"{R}/final/metrics.json",f"{S}/max.rpt",f"{S}/power.rpt"]+glob.glob(f"{S}/*.sdf")+glob.glob(f"{R}/final/nl/*.nl.v")+glob.glob(f"{R}/final/pnl/*.pnl.v")+glob.glob(f"{R}/final/spef/nom/*.spef")
    for f in files: shutil.copy(f,out)
    print(d,"->",out,len(files),"files")
