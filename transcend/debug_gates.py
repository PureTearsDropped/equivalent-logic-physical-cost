import sys, os; sys.path.insert(0,'.'); sys.path.insert(0,'../src')
import fullcell as F
from fullcell import *
from exp_f32_gates import build_exp
from exp_f32_pyspec import exp_spec
x=int(sys.argv[1],16); net=build_exp(); sp=exp_spec(x)
F.ROWS=1; F.MASK=1; vals=[None]*net.nnets
for b in range(32): vals[b]=F.TT((x>>b)&1)
for ii in topo(net):
    inst=net.insts[ii]; pv={p:vals[q] for p,q in inst['pins'].items()}
    for op,q in inst['outs'].items(): vals[q]=cell_func(inst['cell'],op,pv)
def val(bits, off=0):   # dict index->net at 68-grid; returns integer in units of 2^-68 (or local index)
    return sum((vals[n].v&1)<<w for w,n in bits.items() if n is not None)
print("xf   gates",val(net.probes['xf'])>>8,"spec",sp['xf'])
print("xp   gates",val(net.probes['xp'])>>8,"spec",sp['xp'])
print("u    gates",val(net.probes['u']),"spec",sp['u'], " (local units 2^-20)")
print("n    gates",val(net.probes['n']),"spec",sp['n'])
print("r    gates",val(net.probes['r']),"spec",sp['r'])
print("p    gates",val(net.probes['p']),"spec",sp['p'])
print("T    gates",val(net.probes['T'])>>8,"spec",__import__('exp_f32_gates').TBL[sp['j']])
print("y    gates",val(net.probes['y']),"spec",sp['y'])
