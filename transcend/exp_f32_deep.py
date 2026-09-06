"""Deeply pipelined variant of exp_f32_gates.build_exp: every 60-bit product is split into a compression-tree
stage and a Kogge-Stone stage (13 stages). Same spec (v3), same cells; only registers are added."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp_f32_gates import *          # Fx, constants, ColBuilder, Net, ...
from rep_sweep import ColBuilder

class FxD(Fx):
    def tree_rows(self, bits, W):
        """compress to two rows (no carry-propagate): returns (row0, row1) as {index: net}"""
        cb=ColBuilder(self.net,W,'and2','xor+and','xor2x2+a21o'); cb.no_arrival=True
        for idx,n in bits:
            if n is not None and 0<=idx<W: cb.cols[idx].append(n)
        cb.reduce_to_2()
        r0={}; r1={}
        for k in range(W):
            b=cb.cols.get(k,[])
            if len(b)>0: r0[k]=b[0]
            if len(b)>1: r1[k]=b[1]
        return r0,r1
    def rows_ks(self, rows, W):
        cb=ColBuilder(self.net,W,'and2','xor+and','xor2x2+a21o'); cb.no_arrival=True
        for r in rows:
            for k,n in r.items():
                if n is not None: cb.cols[k].append(n)
        out=cb.resolve('ks'); return {w:n for w,n in enumerate(out) if n is not None}

def build_exp_deep():
    net=Net(17); fx=FxD(net,True,clk=32); X=list(range(32)); s=X[31]; e=X[23:31]; m=X[0:23]; ONE=fx.one()
    # ---- S1a: shift amount, barrel, x' rows, u tree rows
    sa=fx.tree([(i,e[i]) for i in range(8)]+fx.const_bits(154),8)[:5]
    bus=m+[ONE]+[None]*31
    for t in range(5):
        step=1<<t; nb=[None]*55
        for q in range(55): nb[q]=fx.MUX(bus[q], bus[q-step] if q-step>=0 else None, sa[t])
        bus=nb
    xf={q+20:bus[q] for q in range(55) if bus[q] is not None}
    A=[(w, fx.XOR(xf.get(w),s) if w in xf else s) for w in range(76)]
    ubits=[(w+i-40-48,n) for i in range(C.bit_length()) if (C>>i)&1 for w,n in A if w+i-40>=48]
    ubits+= [(b,ONE) for b in range(35) if (K0>>b)&1] + [(b,s) for b in range(35) if (NEG>>b)&1]
    u0,u1=fx.tree_rows(ubits,35)
    fx.cut(); u0=fx.regd(u0); u1=fx.regd(u1); xf=fx.regd(xf); s=fx.reg(s)
    # ---- S1b: u KS -> n
    u=fx.rows_ks([u0,u1],35); nbits={b:u.get(20+b) for b in range(14) if u.get(20+b) is not None}
    fx.cut(); nbits=fx.regd(nbits); xf=fx.regd(xf); s=fx.reg(s)
    A=[(w, fx.XOR(xf.get(w),s) if w in xf else s) for w in range(76)]
    j=[nbits.get(b) for b in range(6)]; kn=[nbits.get(6+b) for b in range(8)]
    # ---- S2: r tree + KS
    rows=[]; K1=0; NR=0
    for i in range(L.bit_length()):
        if not (L>>i)&1: continue
        NR+=1; mask=0
        for b in range(14):
            w=b+i-(LF-(F+8))
            if 0<=w<62: mask|=1<<w; rows.append((w, fx.INV(nbits[b]) if b in nbits else ONE))
        K1+=((1<<62)-1)^mask
    K1=(K1+NR+(X0<<8))%(1<<62)
    rows+= [(w,n) for w,n in A if w<62] + [(0,s)] + fx.const_bits(K1)
    r0,r1=fx.tree_rows(rows,62)
    fx.cut(); r0=fx.regd(r0); r1=fx.regd(r1); j=fx.regl(j); kn=fx.regl(kn)
    rb=fx.rows_ks([r0,r1],62)
    fx.cut(); rb=fx.regd(rb); j=fx.regl(j); kn=fx.regl(kn)
    def cbits(v): return {w:ONE for w in range(v.bit_length()) if (v>>w)&1}
    def cprod(cv,xb): return [(i+w-GG,n) for i in range(cv.bit_length()) if (cv>>i)&1 for w,n in xb.items() if i+w-GG>=0]
    def keep(bits,k): return {w:n for w,n in bits.items() if w>=GG-k}
    def full(bits,W=70): t=fx.tree(bits,W); return {w:n for w,n in enumerate(t) if n is not None}
    # ---- S3a: q tree rows, constant products (resolved)
    q0,q1=fx.tree_rows(fx.rowprod(rb,rb,70),70)
    cr1=full(cprod(c1,rb)); cr5=full(cprod(c5,rb)); Bq=full(cprod(c3,rb)+fx.const_bits(c2))
    fx.cut(); q0=fx.regd(q0); q1=fx.regd(q1); cr1=fx.regd(cr1); cr5=fx.regd(cr5); Bq=fx.regd(Bq); j=fx.regl(j); kn=fx.regl(kn)
    # ---- S3b: q KS
    q=fx.rows_ks([q0,q1],70)
    fx.cut(); q=fx.regd(q); cr1=fx.regd(cr1); cr5=fx.regd(cr5); Bq=fx.regd(Bq); j=fx.regl(j); kn=fx.regl(kn)
    # ---- S4a: qB tree, q4 tree, Cq (resolved)
    qB0,qB1=fx.tree_rows(fx.rowprod(q,Bq,70),70)
    q40,q41=fx.tree_rows(fx.rowprod(keep(q,56),keep(q,56),70),70)
    Cq=full([(w,n) for w,n in cr5.items()]+cprod(c6,q)+fx.const_bits(c4))
    fx.cut(); qB0=fx.regd(qB0); qB1=fx.regd(qB1); q40=fx.regd(q40); q41=fx.regd(q41); Cq=fx.regd(keep(Cq,30)); cr1=fx.regd(cr1); j=fx.regl(j); kn=fx.regl(kn)
    # ---- S4b: qB KS, q4 KS
    qB=fx.rows_ks([qB0,qB1],70); q4=keep(fx.rows_ks([q40,q41],70),56)
    fx.cut(); qB=fx.regd(qB); q4=fx.regd(q4); Cq=fx.regd(Cq); cr1=fx.regd(cr1); j=fx.regl(j); kn=fx.regl(kn)
    # ---- S5a: q4C tree
    qc0,qc1=fx.tree_rows(fx.rowprod(q4,Cq,70),70)
    fx.cut(); qc0=fx.regd(qc0); qc1=fx.regd(qc1); qB=fx.regd(qB); cr1=fx.regd(cr1); j=fx.regl(j); kn=fx.regl(kn)
    # ---- S5b: p tree from (cr1 + qB + q4C rows + 1)  [q4C rows fed directly, no KS needed]
    p0,p1=fx.tree_rows([(w,n) for w,n in cr1.items()]+[(w,n) for w,n in qB.items()]+[(w,n) for w,n in qc0.items()]+[(w,n) for w,n in qc1.items()]+[(68,ONE)],70)
    # table T[j] in parallel
    tb={}
    for bit in range(61):
        vals=[(TBL[jj]>>bit)&1 for jj in range(NT)]
        if all(v==1 for v in vals): tb[bit+8]=ONE; continue
        if all(v==0 for v in vals): continue
        level=[ONE if v else None for v in vals]
        for t in range(TB): level=[fx.MUX(level[2*qq],level[2*qq+1],j[t]) for qq in range(len(level)//2)]
        tb[bit+8]=level[0]
    fx.cut(); p0=fx.regd(p0); p1=fx.regd(p1); tb=fx.regd(tb); kn=fx.regl(kn)
    # ---- S5c: p KS
    pb=fx.rows_ks([p0,p1],70)
    fx.cut(); pb=fx.regd(pb); tb=fx.regd(tb); kn=fx.regl(kn)
    # ---- S6a: y tree
    y0,y1=fx.tree_rows(fx.rowprod(tb,pb,70),70)
    fx.cut(); y0=fx.regd(y0); y1=fx.regd(y1); kn=fx.regl(kn)
    # ---- S6b: y KS
    y=fx.rows_ks([y0,y1],70); yb=[y.get(w) for w in range(70)]
    fx.cut(); yb=fx.regl(yb); kn=fx.regl(kn)
    # ---- S7: normalize, round, decide (as in build_exp)
    hi=yb[69]; lo=fx.AND(fx.INV(yb[69]),fx.INV(yb[68]))
    yn=[fx.MUX(fx.MUX(yb[w], yb[w-1] if w>=1 else None, lo), yb[w+1] if w+1<70 else None, hi) for w in range(69)]
    mant=yn[45:69]; tail=yn[8:45]; tmsb=tail[36]; rest=tail[:36]
    lvl=[b for b in rest if b is not None]
    while len(lvl)>1: lvl=[fx.OR(lvl[i],lvl[i+1]) if i+1<len(lvl) else lvl[i] for i in range(0,len(lvl),2)]
    rest_nz=lvl[0] if lvl else None
    gt=fx.AND(tmsb,rest_nz); eq=fx.AND(tmsb,fx.INV(rest_nz)); up=fx.OR(gt,fx.AND(eq,mant[0]))
    def ge_const(bits,c,W):
        t=fx.tree([(w,bits[w]) for w in range(W)]+fx.const_bits((1<<W)-c),W+1); return t[W]
    half=1<<36
    d41=fx.INV(fx.AND(ge_const(tail,half-41,37), fx.INV(ge_const(tail,half+42,37))))
    d81=fx.INV(fx.AND(ge_const(tail,half-81,37), fx.INV(ge_const(tail,half+82,37))))
    d21=fx.INV(fx.AND(ge_const(tail,half-21,37), fx.INV(ge_const(tail,half+22,37))))
    decided=fx.MUX(fx.MUX(d41,d81,lo),d21,hi)
    # ---- S7b: increment + exponent
    fx.cut(); mant=fx.regl(mant); up=fx.reg(up); decided=fx.reg(decided); hi=fx.reg(hi); lo=fx.reg(lo); kn=fx.regl(kn)
    mi=fx.tree([(b,mant[b]) for b in range(24)]+[(0,up)],25); co=mi[24]
    mant2=[fx.MUX(mi[b], ONE if b==23 else None, co) for b in range(24)]
    ex=fx.tree([(b,kn[b]) for b in range(8)]+fx.const_bits(255)+[(0,hi),(0,co)]+[(w,lo) for w in range(8)],8)
    net.outputs=mant2[:23]+ex+[None]+[decided]
    return net

if __name__=="__main__":
    import json
    from check_gates import check
    from fullcell import buffer_high_fanout
    net=build_exp_deep(); n0=len(net.insts); buffer_high_fanout(net)
    print("deep pipeline cells",n0,"-> with buffers",len(net.insts),"flops",sum(1 for i in net.insts if i['cell'].startswith('dfxtp')),"stages",max(net.stage_regs)+0)
    check(net,'/tmp/claude-1001/exp_vectors_v3.txt')
    stage_report(net)
    d="../flow/designs/exp_f32_deep"; os.makedirs(d,exist_ok=True)
    open(f"{d}/exp_f32_deep.v","w").write(to_verilog_exp(net,"exp_f32_deep"))
    c=json.load(open("../flow/designs/exp_f32_pipe_pl/config.json")); c.update({"DESIGN_NAME":"exp_f32_deep","VERILOG_FILES":["dir::exp_f32_deep.v"],"CLOCK_PERIOD":6.0})
    json.dump(c,open(f"{d}/config.json","w"),indent=1); print("staged exp_f32_deep (6 ns clock, timing-driven placement, util 60)")

OPS={'and2':'({A} & {B})','or2':'({A} | {B})','xor2':'({A} ^ {B})','xnor2':'~({A} ^ {B})','inv':'~{A}','nand2':'~({A} & {B})','nor2':'~({A} | {B})',
     'a21o':'(({A1} & {A2}) | {B1})','a21oi':'~(({A1} & {A2}) | {B1})','mux2':"({S} ? {A1} : {A0})",'buf':'{A}'}
def to_generic_verilog(net, name):
    """technology-independent Verilog (assign / always @posedge clk) for the standard synthesis flow."""
    nm={i:f"x[{i}]" for i in range(32)}; nm[32]="clk"
    for i in range(34,net.nnets): nm[i]=f"n{i}"
    regs=[]; L=[]
    for inst in net.insts:
        base=inst['cell'].rsplit('_',1)[0]; o=list(inst['outs'].values())[0]
        if base=='dfxtp': regs.append(o); L.append(f"  always @(posedge clk) {nm[o]} <= {nm[inst['pins']['D']]};")
        elif base=='conb': L.append(f"  assign {nm[o]} = 1'b1;")
        else: L.append(f"  assign {nm[o]} = {OPS[base].format(**{p:nm[x] for p,x in inst['pins'].items()})};")
    outs=net.outputs
    for k in range(31):
        rhs = nm[outs[k]] if outs[k] is not None else "1'b0"
        L.append(f"  assign y[{k}] = {rhs};")
    L.append("  assign y[31] = 1'b0;"); dec = nm[outs[32]] if outs[32] is not None else "1'b1"; L.append(f"  assign decided = {dec};")
    hdr=[f"module {name}(input [31:0] x, input clk, output [31:0] y, output decided);"]
    wires=[nm[i] for i in range(34,net.nnets) if i not in regs]; regd=[nm[i] for i in regs]
    if wires: hdr.append("  wire "+", ".join(wires)+";")
    if regd: hdr.append("  reg "+", ".join(regd)+";")
    return "\n".join(hdr+L+["endmodule"])+"\n"
