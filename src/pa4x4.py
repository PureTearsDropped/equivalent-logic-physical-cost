#!/usr/bin/env python3
"""
physical_aware_4x4_multiplier_optimizer.py

Self-contained research prototype for exact 4x4 multiplier optimization.

What this script demonstrates
-----------------------------
1. Build an exact 4x4 unsigned multiplier.
2. Compare several exact 9-gate full-adder implementations:
   - gate-count-only mixed NAND/NOR
   - arrival-aware mixed NAND/NOR
   - all-NAND 9-gate FA
3. Use a gate-specific, load/fanout-aware timing model instead of pure logic depth.
4. Propagate rise/fall arrival times through the whole DAG.
5. Greedily duplicate shared gates when whole-circuit critical delay improves.
6. Exhaustively verify the multiplier for all 256 input pairs after every final result.

Important
---------
The default cell numbers below are NORMALIZED ILLUSTRATIVE VALUES.
They are NOT a foundry PDK and NOT a standard-cell Liberty characterization.

The point is to demonstrate the optimization machinery:
    gate type -> input capacitance -> output load -> gate delay
    -> circuit arrival propagation -> critical delay
    -> topology optimization

To obtain physically meaningful timing numbers, replace DEFAULT_LIB with
values derived from a real .lib / timing characterization.
"""

from __future__ import annotations

import argparse
import copy
from collections import defaultdict, deque
from dataclasses import dataclass
from typing import Dict, List, Optional, Sequence, Tuple


# =============================================================================
# Exact truth-table representation for a 3-input full adder
# =============================================================================

N_FA_ROWS = 8
FA_MASK = (1 << N_FA_ROWS) - 1


def var_signature(bit: int) -> int:
    s = 0
    for row in range(N_FA_ROWS):
        if (row >> bit) & 1:
            s |= 1 << row
    return s


A_SIG, B_SIG, CIN_SIG = [var_signature(i) for i in range(3)]
SUM_SIG = A_SIG ^ B_SIG ^ CIN_SIG
CARRY_SIG = (A_SIG & B_SIG) | (A_SIG & CIN_SIG) | (B_SIG & CIN_SIG)


@dataclass(frozen=True)
class SearchGate:
    op: str
    a: int
    b: int


# Earlier gate-count-only 9-gate mixed NAND/NOR FA.
GATE_COUNT_ONLY_FA: Tuple[SearchGate, ...] = (
    SearchGate("NAND", 0, 1),
    SearchGate("NAND", 2, 3),
    SearchGate("NAND", 4, 3),
    SearchGate("NOR", 0, 1),
    SearchGate("NOR", 6, 5),
    SearchGate("NOR", 7, 6),   # carry
    SearchGate("NOR", 4, 6),
    SearchGate("NOR", 7, 2),
    SearchGate("NOR", 9, 10),  # sum
)

# Arrival-aware mixed 9-gate FA discovered earlier with input arrivals (0,0,4).
ARRIVAL_AWARE_MIXED_FA: Tuple[SearchGate, ...] = (
    SearchGate("NOR", 0, 1),
    SearchGate("NAND", 0, 1),
    SearchGate("NAND", 3, 3),
    SearchGate("NAND", 4, 5),
    SearchGate("NOR", 2, 6),
    SearchGate("NOR", 3, 7),    # carry
    SearchGate("NAND", 2, 6),
    SearchGate("NAND", 4, 7),
    SearchGate("NAND", 9, 10),  # sum
)

# Standard exact 9-NAND full adder.
ALL_NAND_FA: Tuple[SearchGate, ...] = (
    SearchGate("NAND", 0, 1),   # g1 = ~(ab)
    SearchGate("NAND", 0, 3),
    SearchGate("NAND", 1, 3),
    SearchGate("NAND", 4, 5),   # g4 = a xor b
    SearchGate("NAND", 6, 2),
    SearchGate("NAND", 6, 7),
    SearchGate("NAND", 2, 7),
    SearchGate("NAND", 8, 9),   # sum
    SearchGate("NAND", 3, 7),   # carry
)


def evaluate_fa_signature(gates: Sequence[SearchGate]) -> Tuple[int, int]:
    sigs = [A_SIG, B_SIG, CIN_SIG]
    found_sum = None
    found_carry = None

    for g in gates:
        a, b = sigs[g.a], sigs[g.b]
        if g.op == "NAND":
            f = FA_MASK ^ (a & b)
        elif g.op == "NOR":
            f = FA_MASK ^ (a | b)
        else:
            raise ValueError(g.op)
        sigs.append(f)
        if f == SUM_SIG:
            found_sum = len(sigs) - 1
        if f == CARRY_SIG:
            found_carry = len(sigs) - 1

    if found_sum is None or found_carry is None:
        raise ValueError("FA implementation does not produce exact SUM/CARRY")

    return found_sum, found_carry


for _fa in (GATE_COUNT_ONLY_FA, ARRIVAL_AWARE_MIXED_FA, ALL_NAND_FA):
    evaluate_fa_signature(_fa)


# =============================================================================
# Gate-level DAG
# =============================================================================

@dataclass
class Node:
    op: str  # IN / NAND / NOR
    a: Optional[int] = None
    b: Optional[int] = None


class GateNet:
    def __init__(self) -> None:
        self.nodes: List[Node] = []

    def inp(self) -> int:
        i = len(self.nodes)
        self.nodes.append(Node("IN"))
        return i

    def nand(self, a: int, b: int) -> int:
        i = len(self.nodes)
        self.nodes.append(Node("NAND", a, b))
        return i

    def nor(self, a: int, b: int) -> int:
        i = len(self.nodes)
        self.nodes.append(Node("NOR", a, b))
        return i


def and2(net: GateNet, a: int, b: int) -> int:
    t = net.nand(a, b)
    return net.nand(t, t)


def half_adder(net: GateNet, a: int, b: int) -> Tuple[int, int]:
    # Exact 5-NAND HA.
    n1 = net.nand(a, b)
    n2 = net.nand(a, n1)
    n3 = net.nand(b, n1)
    s = net.nand(n2, n3)
    c = net.nand(n1, n1)
    return s, c


def instantiate_fa(
    net: GateNet,
    a: int,
    b: int,
    cin: int,
    gates: Sequence[SearchGate],
) -> Tuple[int, int]:
    ids = [a, b, cin]
    sigs = [A_SIG, B_SIG, CIN_SIG]
    sum_id = None
    carry_id = None

    for g in gates:
        if g.op == "NAND":
            nid = net.nand(ids[g.a], ids[g.b])
            f = FA_MASK ^ (sigs[g.a] & sigs[g.b])
        elif g.op == "NOR":
            nid = net.nor(ids[g.a], ids[g.b])
            f = FA_MASK ^ (sigs[g.a] | sigs[g.b])
        else:
            raise ValueError(g.op)

        ids.append(nid)
        sigs.append(f)

        if f == SUM_SIG:
            sum_id = nid
        if f == CARRY_SIG:
            carry_id = nid

    if sum_id is None or carry_id is None:
        raise ValueError("FA does not expose exact SUM/CARRY")

    return sum_id, carry_id


def build_array4(fa: Sequence[SearchGate]) -> Tuple[GateNet, List[int]]:
    """
    Same exact 4x4 unsigned array topology for all FA variants.
    Only the internal FA factorization changes.
    """
    net = GateNet()
    A = [net.inp() for _ in range(4)]
    B = [net.inp() for _ in range(4)]

    pp = {
        (i, j): and2(net, A[i], B[j])
        for i in range(4)
        for j in range(4)
    }

    P: List[Optional[int]] = [None] * 8
    P[0] = pp[0, 0]

    P[1], x1 = half_adder(net, pp[1, 0], pp[0, 1])
    x2, x3 = instantiate_fa(net, pp[1, 1], pp[0, 2], x1, fa)
    x4, x5 = instantiate_fa(net, pp[1, 2], pp[0, 3], x3, fa)
    x6, x7 = half_adder(net, pp[1, 3], x5)

    P[2], x15 = half_adder(net, x2, pp[2, 0])
    x14, x16 = instantiate_fa(net, x4, pp[2, 1], x15, fa)
    x13, x17 = instantiate_fa(net, x6, pp[2, 2], x16, fa)
    x9, x8 = instantiate_fa(net, x7, pp[2, 3], x17, fa)

    P[3], x12 = half_adder(net, x14, pp[3, 0])
    P[4], x11 = instantiate_fa(net, x13, pp[3, 1], x12, fa)
    P[5], x10 = instantiate_fa(net, x9, pp[3, 2], x11, fa)
    P[6], P[7] = instantiate_fa(net, x8, pp[3, 3], x10, fa)

    assert all(x is not None for x in P)
    return net, [int(x) for x in P]


# =============================================================================
# Exact verification
# =============================================================================

def topo_order(net: GateNet) -> List[int]:
    n = len(net.nodes)
    indeg = [0] * n
    succ = [[] for _ in range(n)]

    for i, node in enumerate(net.nodes):
        if node.op == "IN":
            continue
        for src in (node.a, node.b):
            indeg[i] += 1
            succ[src].append(i)

    q = deque(i for i in range(n) if indeg[i] == 0)
    order: List[int] = []

    while q:
        u = q.popleft()
        order.append(u)
        for v in succ[u]:
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)

    if len(order) != n:
        raise RuntimeError("Cycle detected")

    return order


def eval_dag(net: GateNet, input_values: Sequence[int]) -> List[int]:
    order = topo_order(net)
    vals: List[Optional[int]] = [None] * len(net.nodes)

    input_ids = [i for i, n in enumerate(net.nodes) if n.op == "IN"]
    if len(input_ids) != len(input_values):
        raise ValueError("Wrong number of primary input values")

    for i, v in zip(input_ids, input_values):
        vals[i] = int(v)

    for i in order:
        node = net.nodes[i]
        if node.op == "IN":
            continue

        va = vals[node.a]
        vb = vals[node.b]
        assert va is not None and vb is not None

        if node.op == "NAND":
            vals[i] = 1 - (va & vb)
        elif node.op == "NOR":
            vals[i] = 1 - (va | vb)
        else:
            raise ValueError(node.op)

    return [int(v) for v in vals]


def verify_array4(net: GateNet, outputs: Sequence[int]) -> None:
    for a in range(16):
        for b in range(16):
            ins = (
                [(a >> i) & 1 for i in range(4)]
                + [(b >> i) & 1 for i in range(4)]
            )
            vals = eval_dag(net, ins)
            got = sum(vals[o] << i for i, o in enumerate(outputs))
            expected = a * b
            if got != expected:
                raise AssertionError(
                    f"Mismatch a={a}, b={b}: got {got}, expected {expected}"
                )


# =============================================================================
# Gate-specific, fanout/load-aware timing model
# =============================================================================

@dataclass(frozen=True)
class Cell:
    cin: float
    p_rise: float
    r_rise: float
    p_fall: float
    r_fall: float
    area: float


# Illustrative normalized values only.
DEFAULT_LIB: Dict[str, Cell] = {
    "NAND": Cell(
        cin=1.00,
        p_rise=0.80,
        r_rise=0.55,
        p_fall=0.95,
        r_fall=0.70,
        area=1.00,
    ),
    "NOR": Cell(
        cin=1.30,
        p_rise=1.10,
        r_rise=0.90,
        p_fall=0.80,
        r_fall=0.55,
        area=1.30,
    ),
}


@dataclass
class TimingResult:
    critical_delay: float
    output_arrivals: List[float]
    rise: List[float]
    fall: List[float]
    loads: List[float]
    area: float
    sinks: Dict[int, List[Tuple[object, object]]]


def fanout_pin_lists(
    net: GateNet,
    outputs: Sequence[int],
) -> Dict[int, List[Tuple[object, object]]]:
    sinks: Dict[int, List[Tuple[object, object]]] = defaultdict(list)

    for i, node in enumerate(net.nodes):
        if node.op == "IN":
            continue
        sinks[node.a].append((i, "a"))
        sinks[node.b].append((i, "b"))

    for k, o in enumerate(outputs):
        sinks[o].append(("OUT", k))

    return sinks


def physical_timing(
    net: GateNet,
    outputs: Sequence[int],
    lib: Dict[str, Cell] = DEFAULT_LIB,
    out_load: float = 2.0,
) -> TimingResult:
    """
    Simplified static timing analysis.

    For NAND/NOR, output rise is driven from falling input arrival,
    output fall from rising input arrival.

    delay = intrinsic + resistance_factor * output_load

    output_load = sum(sink input capacitances) + primary-output load

    This captures:
      - NAND/NOR non-equivalence
      - fanout/load cost
      - rise/fall asymmetry
      - upstream penalty caused by gate duplication

    It does NOT capture real slew tables, routing parasitics, placement,
    coupling, voltage/temperature corners, etc.
    """
    order = topo_order(net)
    sinks = fanout_pin_lists(net, outputs)

    rise = [0.0] * len(net.nodes)
    fall = [0.0] * len(net.nodes)
    loads = [0.0] * len(net.nodes)

    for src in range(len(net.nodes)):
        c = 0.0
        for consumer, _pin in sinks[src]:
            if consumer == "OUT":
                c += out_load
            else:
                c += lib[net.nodes[consumer].op].cin
        loads[src] = c

    for i in order:
        node = net.nodes[i]

        if node.op == "IN":
            rise[i] = 0.0
            fall[i] = 0.0
            continue

        cell = lib[node.op]

        in_fall = max(fall[node.a], fall[node.b])
        in_rise = max(rise[node.a], rise[node.b])

        rise[i] = (
            in_fall
            + cell.p_rise
            + cell.r_rise * loads[i]
        )
        fall[i] = (
            in_rise
            + cell.p_fall
            + cell.r_fall * loads[i]
        )

    output_arrivals = [max(rise[o], fall[o]) for o in outputs]
    area = sum(
        lib[n.op].area
        for n in net.nodes
        if n.op != "IN"
    )

    return TimingResult(
        critical_delay=max(output_arrivals),
        output_arrivals=output_arrivals,
        rise=rise,
        fall=fall,
        loads=loads,
        area=area,
        sinks=sinks,
    )


def logical_depth(net: GateNet, outputs: Sequence[int]) -> int:
    order = topo_order(net)
    depth = [0] * len(net.nodes)

    for i in order:
        node = net.nodes[i]
        if node.op != "IN":
            depth[i] = max(depth[node.a], depth[node.b]) + 1

    return max(depth[o] for o in outputs)


# =============================================================================
# Logic-preserving gate duplication
# =============================================================================

def duplicate_and_rewire(
    net: GateNet,
    node_id: int,
    moved_sinks: Sequence[Tuple[int, str]],
) -> GateNet:
    """
    Clone one logic gate with exactly the same inputs, then move selected
    sink pins from the original gate to the clone.

    Functional equivalence is preserved by construction.

    The clone's inputs create extra upstream capacitance, which is naturally
    included when the full-circuit timing is recomputed.
    """
    newnet = copy.deepcopy(net)
    src = newnet.nodes[node_id]

    if src.op == "IN":
        raise ValueError("Primary input duplication is not handled here")

    clone_id = len(newnet.nodes)
    newnet.nodes.append(Node(src.op, src.a, src.b))

    for consumer, pin in moved_sinks:
        c = newnet.nodes[consumer]
        if pin == "a":
            c.a = clone_id
        elif pin == "b":
            c.b = clone_id
        else:
            raise ValueError(pin)

    return newnet


def best_one_duplication(
    net: GateNet,
    outputs: Sequence[int],
    lib: Dict[str, Cell] = DEFAULT_LIB,
    out_load: float = 2.0,
    max_fanout_to_enumerate: int = 6,
):
    """
    Enumerate nontrivial sink partitions for moderate-fanout gates.
    Accept only a duplication that reduces WHOLE-CIRCUIT critical delay.
    """
    before = physical_timing(net, outputs, lib, out_load)
    best = None

    for node_id, node in enumerate(net.nodes):
        if node.op == "IN":
            continue

        internal_sinks = [
            x for x in before.sinks[node_id]
            if x[0] != "OUT"
        ]
        m = len(internal_sinks)

        if m < 2 or m > max_fanout_to_enumerate:
            continue

        for mask in range(1, (1 << m) - 1):
            subset = [
                internal_sinks[k]
                for k in range(m)
                if (mask >> k) & 1
            ]

            # Symmetry breaking: partition S and complement(S) are equivalent.
            if len(subset) > m - len(subset):
                continue
            if len(subset) == m - len(subset) and not (mask & 1):
                continue

            candidate = duplicate_and_rewire(
                net,
                node_id,
                subset,
            )
            tm = physical_timing(
                candidate,
                outputs,
                lib,
                out_load,
            )

            gain = before.critical_delay - tm.critical_delay
            if gain <= 1e-12:
                continue

            rank = (
                gain,      # first: greatest delay reduction
                -tm.area,  # second: smaller area
            )

            if best is None or rank > best["rank"]:
                best = {
                    "rank": rank,
                    "gain": gain,
                    "node": node_id,
                    "subset": subset,
                    "net": candidate,
                    "timing": tm,
                }

    return best


def greedy_duplicate(
    net: GateNet,
    outputs: Sequence[int],
    max_steps: int = 8,
    lib: Dict[str, Cell] = DEFAULT_LIB,
    out_load: float = 2.0,
):
    current = copy.deepcopy(net)
    history = []

    tm = physical_timing(current, outputs, lib, out_load)
    history.append(
        {
            "duplications": 0,
            "gates": len(current.nodes) - 8,
            "area": tm.area,
            "critical_delay": tm.critical_delay,
            "gain_this_step": 0.0,
            "move": "start",
        }
    )

    for step in range(1, max_steps + 1):
        best = best_one_duplication(
            current,
            outputs,
            lib,
            out_load,
        )

        if best is None:
            break

        current = best["net"]
        tm = best["timing"]

        history.append(
            {
                "duplications": step,
                "gates": len(current.nodes) - 8,
                "area": tm.area,
                "critical_delay": tm.critical_delay,
                "gain_this_step": best["gain"],
                "move": (
                    f"duplicate node {best['node']}; "
                    f"move {len(best['subset'])} sink pin(s)"
                ),
            }
        )

    return current, history


# =============================================================================
# Experiment
# =============================================================================

def run_experiment(max_duplications: int = 8) -> None:
    variants = {
        "gate-count-only mixed": GATE_COUNT_ONLY_FA,
        "arrival-aware mixed": ARRIVAL_AWARE_MIXED_FA,
        "all-NAND 9-gate FA": ALL_NAND_FA,
    }

    built = {}
    rows = []

    for name, fa in variants.items():
        net, outputs = build_array4(fa)
        verify_array4(net, outputs)
        tm = physical_timing(net, outputs)

        built[name] = (net, outputs)

        rows.append(
            {
                "circuit": name,
                "gates": len(net.nodes) - 8,
                "logical_depth": logical_depth(net, outputs),
                "normalized_area": tm.area,
                "physical_delay": tm.critical_delay,
                "max_pin_fanout": max(
                    len(v) for v in tm.sinks.values()
                ),
            }
        )

    print("=== Exact 4x4 multiplier comparison ===")
    print("All variants passed exhaustive 256/256 verification.\n")

    headers = (
        "circuit",
        "gates",
        "depth",
        "area",
        "delay",
        "max_fanout",
    )

    print(
        f"{headers[0]:24s} "
        f"{headers[1]:>7s} "
        f"{headers[2]:>7s} "
        f"{headers[3]:>10s} "
        f"{headers[4]:>10s} "
        f"{headers[5]:>11s}"
    )
    print("-" * 78)

    for r in sorted(rows, key=lambda x: x["physical_delay"]):
        print(
            f"{r['circuit']:24s} "
            f"{r['gates']:7d} "
            f"{r['logical_depth']:7d} "
            f"{r['normalized_area']:10.2f} "
            f"{r['physical_delay']:10.3f} "
            f"{r['max_pin_fanout']:11d}"
        )

    nand_net, nand_outputs = built["all-NAND 9-gate FA"]
    start_tm = physical_timing(nand_net, nand_outputs)

    optimized, history = greedy_duplicate(
        nand_net,
        nand_outputs,
        max_steps=max_duplications,
    )

    verify_array4(optimized, nand_outputs)
    final_tm = physical_timing(optimized, nand_outputs)

    print("\n=== Greedy exact gate duplication on all-NAND multiplier ===")
    print(
        f"{'dup':>4s} {'gates':>7s} {'area':>9s} "
        f"{'delay':>10s} {'gain':>9s}  move"
    )
    print("-" * 90)

    for h in history:
        print(
            f"{h['duplications']:4d} "
            f"{h['gates']:7d} "
            f"{h['area']:9.2f} "
            f"{h['critical_delay']:10.3f} "
            f"{h['gain_this_step']:9.3f}  "
            f"{h['move']}"
        )

    reduction = (
        start_tm.critical_delay - final_tm.critical_delay
    ) / start_tm.critical_delay * 100.0

    area_increase = (
        final_tm.area - start_tm.area
    ) / start_tm.area * 100.0

    print("\nFinal exact result:")
    print("  verification : 256/256")
    print(
        f"  gates        : "
        f"{len(nand_net.nodes)-8} -> {len(optimized.nodes)-8}"
    )
    print(
        f"  area         : "
        f"{start_tm.area:.2f} -> {final_tm.area:.2f} "
        f"({area_increase:+.2f}%)"
    )
    print(
        f"  delay        : "
        f"{start_tm.critical_delay:.3f} -> "
        f"{final_tm.critical_delay:.3f} "
        f"({reduction:.2f}% reduction)"
    )

    print(
        "\nReminder: delay/area values are normalized research-model values, "
        "not PDK timing."
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-duplications",
        type=int,
        default=8,
        help="Maximum greedy gate-duplication steps.",
    )
    args = parser.parse_args()

    run_experiment(
        max_duplications=args.max_duplications,
    )


if __name__ == "__main__":
    main()
