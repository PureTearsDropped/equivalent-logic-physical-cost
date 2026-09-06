"""Signed-digit (borrow-save, (p,n) encoding) multiplier on two rails, built with the same schedule machinery,
compared against total-arith-hardware's sd_mult10 (generic-gate SystemVerilog imported and mapped to sky130 cells).
Correctness: lean/SignedDigit.lean (two-rail schedules preserve the signed value; digit product identity);
every netlist is also checked on random canonical digit vectors."""
import sys, os, re, random, math; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from arith_search import *
from rep_sweep import ColBuilder, timing_any

# ------------------------------------------------------------------ import generic-gate SV (assign w = a op b)
def import_generic_sv(path, n_in, n_out):
    """inputs xP,xN,yP,yN [n_in-1:0] -> Net inputs 0..4n-1 (xP,xN,yP,yN); outputs zP,zN [n_out-1:0]."""
    net=Net(2*n_in)                      # Net(nbits) allocates 2*nbits inputs; we need 4*n_in
    net.nnets=4*n_in; net.nbits=2*n_in
    names={}
    for k in range(n_in):
        names[f"xP[{k}]"]=k; names[f"xN[{k}]"]=n_in+k; names[f"yP[{k}]"]=2*n_in+k; names[f"yN[{k}]"]=3*n_in+k
    const={}                       # wire name -> 0/1 for constant-folded wires
    def val(s):
        s=s.strip()
        if s=="1'b0": return ('c',0)
        if s=="1'b1": return ('c',1)
        if s in const: return ('c',const[s])
        if s not in names: names[s]=net.nnets; net.nnets+=1
        return ('n',names[s])
    INV=lambda a: net.add('inv_1',{'A':a})['Y']
    for m in re.finditer(r"assign\s+(\S+)\s*=\s*(.+?);",open(path).read()):
        lhs,rhs=m.group(1),m.group(2).strip()
        mm=re.match(r"(\S+)\s*([&|^])\s*(\S+)$",rhs)
        if mm:
            a,op,b=mm.groups(); va,vb=val(a),val(b)
            if va[0]=='c' and vb[0]=='c':
                x,y=va[1],vb[1]; const[lhs]={'&':x&y,'|':x|y,'^':x^y}[op]; continue
            if va[0]=='c': va,vb=vb,va          # constant on the right
            if vb[0]=='c':
                c=vb[1]
                if op=='&': 
                    if c==0: const[lhs]=0
                    else: names[lhs]=va[1]
                elif op=='|':
                    if c==1: const[lhs]=1
                    else: names[lhs]=va[1]
                else:
                    names[lhs]=va[1] if c==0 else INV(va[1])
                continue
            cell={'&':'and2_1','|':'or2_1','^':'xor2_1'}[op]
            names[lhs]=net.add(cell,{'A':va[1],'B':vb[1]})['X']
        else:
            v=val(rhs)
            if v[0]=='c': const[lhs]=v[1]
            else: names[lhs]=v[1]
    zP=[names.get(f"zP[{k}]",None) for k in range(n_out)]; zN=[names.get(f"zN[{k}]",None) for k in range(n_out)]
    assert all(const.get(f"z{r}[{k}]",0)==0 for r in "PN" for k in range(n_out)), "constant-1 output"
    net.outputs=zP+zN; net.n_in=n_in; net.n_out=n_out; net.sd=True; return net

# ------------------------------------------------------------------ our two-rail generator
def sd_multiplier(n, pp_mode='merged', final='none', cells=('and2','xor+and','xor2x2+a21o'), sched=sched_dadda):
    """inputs xP,xN,yP,yN (n digits, canonical). P rail collects xP·yP and xN·yN, N rail xP·yN and xN·yP.
    pp_mode 'split': 2 bits per rail per (i,j); 'merged': or2 of the two (exact for canonical inputs).
    final: 'none' (two rows per rail), 'ripple'/'ks' (one row per rail -> borrow-save (zP,zN)),
           'canon' (their canonical ripple: FA per rail + rail subtraction; canonical (zP,zN))."""
    net=Net(2*n); net.nnets=4*n; net.nbits=2*n
    xP=list(range(n)); xN=list(range(n,2*n)); yP=list(range(2*n,3*n)); yN=list(range(3*n,4*n))
    W=2*n+1; pp,ha,fa=cells
    P=ColBuilder(net,W,pp,ha,fa); N=ColBuilder(net,W,pp,ha,fa)
    AND=lambda a,b: net.add('and2_1',{'A':a,'B':b})['X']; OR=lambda a,b: net.add('or2_1',{'A':a,'B':b})['X']
    for i in range(n):
        for j in range(n):
            pp1,pp2=AND(xP[i],yP[j]),AND(xN[i],yN[j]); nn1,nn2=AND(xP[i],yN[j]),AND(xN[i],yP[j])
            if pp_mode=='merged': P.cols[i+j].append(OR(pp1,pp2)); N.cols[i+j].append(OR(nn1,nn2))
            else: P.cols[i+j]+= [pp1,pp2]; N.cols[i+j]+=[nn1,nn2]
    sched(P); sched(N)
    if final in ('ripple','ks'):
        zP=P.resolve(final); zN=N.resolve(final)
    elif final=='none':
        rows=[]
        for B in (P,N):
            r0=[];r1=[]
            for k in range(W): b=B.cols[k]; r0.append(b[0] if b else None); r1.append(b[1] if len(b)>1 else None)
            rows+= [r0,r1]
        net.outputs=rows[0]+rows[1]+rows[2]+rows[3]; net.sd4=True; net.n_in=n; net.n_out=W; return net
    elif final=='canon':
        # canonical ripple (sd2_gates.py): per column, FA on each rail with carry digit, then rail subtraction
        INV=lambda a: net.add('inv_1',{'A':a})['Y']
        def FA3(bits):  # 3 bits (some None) -> (sum, carry) using the chosen FA cell; fold Nones
            bits=[b for b in bits if b is not None]
            if len(bits)==3: return FA_MENU[fa](net,bits[0],bits[1],bits[2],1)
            if len(bits)==2: return HA_MENU[ha](net,bits[0],bits[1],1)
            if len(bits)==1: return bits[0],None
            return None,None
        cp=cn=None; zP=[]; zN=[]
        for k in range(W):
            for B in (P,N):
                while len(B.cols[k])>2: B.fa(k,B.order_by_arrival(B.cols[k])[:3])
            ps,pc=FA3(P.cols[k]+[cp]); ns,nc=FA3(N.cols[k]+[cn])
            def sub(p,q):  # p AND NOT q, folding None
                if p is None: return None
                if q is None: return p
                return AND(p,INV(q))
            zP.append(sub(ps,ns)); zN.append(sub(ns,ps)); cp,cn=sub(pc,nc),sub(nc,pc)
        zP.append(cp); zN.append(cn); W=W+1
    elif final=='canon_ks':
        INV=lambda a: net.add('inv_1',{'A':a})['Y']
        XNOR=lambda a,b: (INV(a) if b is None else INV(b) if a is None else net.add('xnor2_1',{'A':a,'B':b})['Y'])
        A21O=lambda p,gp,g: (g if (p is None or gp is None) else (AND(p,gp) if g is None else net.add('a21o_1',{'A1':p,'A2':gp,'B1':g})['X']))
        ANDn=lambda a,b: None if (a is None or b is None) else AND(a,b)
        for B in (P,N):
            for k in range(W):
                while len(B.cols[k])>2: B.fa(k,B.order_by_arrival(B.cols[k])[:3])
        # each rail to one row first (Kogge-Stone), then borrow-lookahead subtract
        rp=P.resolve('ks'); rn=N.resolve('ks')
        T=[None]*W; Gpn=[None]*W; Gnp=[None]*W   # T: p==n (borrow propagates); G: borrow generate for P-N / N-P
        for k in range(W):
            p_,n_=rp[k],rn[k]
            if p_ is None and n_ is None: T[k]=None; Gpn[k]=None; Gnp[k]=None   # both 0: T=1 constant -> treat as propagate-true
            elif p_ is None: T[k]=INV(n_); Gpn[k]=n_; Gnp[k]=None
            elif n_ is None: T[k]=INV(p_); Gpn[k]=None; Gnp[k]=p_
            else: T[k]=XNOR(p_,n_); Gpn[k]=AND(n_,INV(p_)); Gnp[k]=AND(p_,INV(n_))
        # T None means constant 1 (propagate). prefix with spans 1,2,4,...
        def prefix(G):
            Gc=list(G); Tc=list(T); d=1
            TRUE=None  # constant-true propagate encoded as None in Tc
            while d<W:
                Gn=list(Gc); Tn=list(Tc)
                for k in range(d,W):
                    # comp: G = Gk | (Tk & G[k-d]); T = Tk & T[k-d]   with None-T = true, None-G = false
                    tk,gk,gl,tl=Tc[k],Gc[k],Gc[k-d],Tc[k-d]
                    if tk is None: Gn[k]= gl if gk is None else (gk if gl is None else net.add('or2_1',{'A':gk,'B':gl})['X'])
                    else: Gn[k]=A21O(tk,gl,gk)
                    Tn[k]= tl if tk is None else (tk if tl is None else AND(tk,tl))
                Gc,Tc=Gn,Tn; d*=2
            return Gc
        Bpn=prefix(Gpn); Bnp=prefix(Gnp)                  # Bpn[k] = borrow out of columns 0..k for P-N
        sign=Bpn[W-1]                                       # P < N
        zP=[];zN=[]
        def diff(t,b):   # d = (p xor n) xor b = (not T) xor b ; T None = constant true, b None = constant 0
            if t is None: return b                       # T true: d = b
            if b is None: return INV(t)                  # b = 0: d = not T
            return XNOR(t,b)
        nsign=None if sign is None else INV(sign)
        for k in range(W):
            dk=diff(T[k],Bpn[k-1] if k>0 else None); dk2=diff(T[k],Bnp[k-1] if k>0 else None)
            zP.append(dk if sign is None else ANDn(dk,nsign)); zN.append(ANDn(dk2,sign))
        net.outputs=zP+zN; net.sd=True; net.n_in=n; net.n_out=W; return net
    net.outputs=zP+zN; net.sd=True; net.n_in=n; net.n_out=W; return net

# ------------------------------------------------------------------ random check with canonical digits
def check_sd(net, nvec=1024, seed=3):
    import fullcell as F
    rng=random.Random(seed); n=net.n_in
    F.ROWS=nvec; F.MASK=(1<<nvec)-1
    X=[[rng.choice((-1,0,1)) for _ in range(n)] for _ in range(nvec)]; Y=[[rng.choice((-1,0,1)) for _ in range(n)] for _ in range(nvec)]
    def rail(D,sign): return [F.TT(sum((1 if D[r][k]==sign else 0)<<r for r in range(nvec))) for k in range(n)]
    prim=rail(X,1)+rail(X,-1)+rail(Y,1)+rail(Y,-1)
    vals=[None]*net.nnets
    for i in range(4*n): vals[i]=prim[i]
    for ii in topo(net):
        inst=net.insts[ii]; pv={p:vals[x] for p,x in inst['pins'].items()}
        for op,x in inst['outs'].items(): vals[x]=cell_func(inst['cell'],op,pv)
    W=net.n_out; outs=net.outputs
    for r in range(nvec):
        want=sum(d<<k for k,d in enumerate(X[r]))*sum(d<<k for k,d in enumerate(Y[r]))
        bit=lambda o:(((vals[o].v>>r)&1) if o is not None else 0)
        if getattr(net,'sd4',False):
            got=sum((bit(outs[k])+bit(outs[W+k])-bit(outs[2*W+k])-bit(outs[3*W+k]))<<k for k in range(W))
        else:
            got=sum((bit(outs[k])-bit(outs[W+k]))<<k for k in range(W))
        if got!=want: raise AssertionError(f"row {r}: got {got} want {want}")
    F.set_width(4); return True

if __name__=="__main__":
    n=10
    print(f"{'design':44s} {'cells':>6s} {'area':>7s} {'delay':>7s}  output")
    R="/home/claude/seedcradle/publish/total-arith-hardware/rtl/generated/sd_mult10.sv"
    if os.path.exists(R):
        net=import_generic_sv(R,10,33); check_sd(net); d,a=timing_any(net)
        print(f"{'total-arith sd_mult10 (imported, 1x cells)':44s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps  canonical (zP,zN)")
        os.makedirs("out",exist_ok=True); saved=net.outputs; net.outputs=[o for o in saved if o is not None]
        # to_verilog assumes a/b/p ports; emit with generic names for STA
    for pp_mode in ('merged','split'):
        for final,desc in (('none','4 rows (2 per rail), no CPA'),('ripple','borrow-save (zP,zN), ripple per rail'),('ks','borrow-save (zP,zN), Kogge-Stone per rail'),('canon','canonical (zP,zN), canonical ripple'),('canon_ks','canonical (zP,zN), borrow-lookahead + select')):
            net=sd_multiplier(n,pp_mode,final); check_sd(net); d,a=timing_any(net)
            print(f"{'ours '+pp_mode+' / '+final:44s} {len(net.insts):6d} {a:7.0f} {d*1000:6.0f}ps  {desc}",flush=True)

# ------------------------------------------------------------------ Verilog export for SD nets (xP,xN,yP,yN -> zP,zN)
def to_verilog_sd(net, name):
    n=net.n_in; W=net.n_out
    L=[f"module {name}(input [{n-1}:0] xP, input [{n-1}:0] xN, input [{n-1}:0] yP, input [{n-1}:0] yN, output [{W-1}:0] zP, output [{W-1}:0] zN);"]
    nm={}
    for k in range(n): nm[k]=f"xP[{k}]"; nm[n+k]=f"xN[{k}]"; nm[2*n+k]=f"yP[{k}]"; nm[3*n+k]=f"yN[{k}]"
    outs=net.outputs; ties=[]
    for k in range(W):
        for r,o in (("zP",outs[k]),("zN",outs[W+k])):
            if o is None: ties.append(f"{r}[{k}]")
            elif o in nm: L.append(f"  // {r}[{k}] shares net {nm[o]}"); ties.append((f"{r}[{k}]",nm[o]))
            else: nm[o]=f"{r}[{k}]"
    wires=[f"n{i}" for i in range(4*n,net.nnets) if i not in nm]
    for i in range(4*n,net.nnets): nm.setdefault(i,f"n{i}")
    if wires: L.append("  wire "+", ".join(wires)+";")
    for ii,inst in enumerate(net.insts):
        conns=[f".{p}({nm[x]})" for p,x in inst['pins'].items()]+[f".{p}({nm[x]})" for p,x in inst['outs'].items()]
        L.append(f"  sky130_fd_sc_hd__{inst['cell']} g{ii} ({', '.join(conns)});")
    for j,t in enumerate(ties):
        if isinstance(t,tuple): L.append(f"  sky130_fd_sc_hd__buf_1 tb{j} (.A({t[1]}), .X({t[0]}));")
        else: L.append(f"  sky130_fd_sc_hd__conb_1 tc{j} (.LO({t}), .HI());")
    L.append("endmodule"); return "\n".join(L)+"\n"
