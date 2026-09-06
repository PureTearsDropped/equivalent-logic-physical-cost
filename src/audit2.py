import sys, os; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from pa4x4 import *
net,outs=build_array4(ALL_NAND_FA)
opt,hist=greedy_duplicate(net,outs,8)
tm=physical_timing(opt,outs)
print("final delay",tm.critical_delay)
print("output arrivals:",[round(x,2) for x in tm.output_arrivals])
# enumerate all single moves at the final net, classify gains
gains=[]
for nid,nd in enumerate(opt.nodes):
    if nd.op=="IN": continue
    s=[x for x in tm.sinks[nid] if x[0]!="OUT"]; m=len(s)
    if m<2 or m>6: continue
    for mask in range(1,(1<<m)-1):
        sub=[s[k] for k in range(m) if (mask>>k)&1]
        c=duplicate_and_rewire(opt,nid,sub); t=physical_timing(c,outs)
        gains.append(tm.critical_delay-t.critical_delay)
import collections
print("moves:",len(gains),"gain>0:",sum(g>1e-12 for g in gains),"gain==0:",sum(abs(g)<=1e-12 for g in gains),"gain<0:",sum(g<-1e-12 for g in gains))
# how many near-critical paths? nodes whose worst arrival + downstream slack... simpler: outputs within 0.5 of critical
crit=tm.critical_delay
print("outputs within 1.0 of critical:",sum(1 for x in tm.output_arrivals if crit-x<1.0))
# 2-step lookahead: plateau move then improving?
best2=0
for nid,nd in enumerate(opt.nodes):
    if nd.op=="IN": continue
    s=[x for x in tm.sinks[nid] if x[0]!="OUT"]; m=len(s)
    if m<2 or m>6: continue
    for mask in range(1,(1<<m)-1):
        sub=[s[k] for k in range(m) if (mask>>k)&1]
        c=duplicate_and_rewire(opt,nid,sub); t=physical_timing(c,outs)
        if t.critical_delay-crit>0.3: continue   # only near-plateau first moves
        b=best_one_duplication(c,outs)
        if b and crit-b["timing"].critical_delay>best2: best2=crit-b["timing"].critical_delay
print("best 2-step total gain from final:",round(best2,3))
