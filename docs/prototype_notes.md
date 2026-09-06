Physical-Aware Exact 4×4 Multiplier Optimizer
1. Purpose
This prototype extends the earlier exact Boolean superoptimization work from a pure logic-depth model to a simplified physical timing model.
The central change is:
[ \text{logical depth} \quad\longrightarrow\quad \text{gate-specific load-aware delay} ]
Instead of assuming:
[ delay(NAND2)=delay(NOR2)=1 ]
the optimizer now computes a delay for every gate from:
	●	gate type
	●	rise/fall direction
	●	intrinsic delay
	●	output load
	●	input capacitance of fanout gates
	●	primary-output load
The resulting whole-circuit arrival times are propagated through the DAG and the actual optimization target becomes:
[ T_{critical} ]
rather than logic level count.
￼
2. Important limitation
The default cell values in the code are normalized illustrative numbers.
They are not:
	●	a foundry PDK
	●	a Liberty .lib
	●	SPICE characterization
	●	a real standard-cell timing signoff model
The purpose is to verify that the algorithmic machinery works.
For physical use, replace the normalized cell model with real library timing data.
￼
3. Simplified cell model
Each gate has:
[ ( C_{in}, p_{rise}, r_{rise}, p_{fall}, r_{fall}, Area ) ]
The output load is:
[ C_{load}
\sum C_{sink\ pin} + C_{primary\ output} ]
For an inverting gate such as NAND2 or NOR2:
[ t_{rise}
\max(t_{fall,input}) + p_{rise} + r_{rise}C_{load} ]
[ t_{fall}
\max(t_{rise,input}) + p_{fall} + r_{fall}C_{load} ]
The model therefore captures, at least qualitatively:
	●	NAND2 and NOR2 are not equivalent
	●	high fanout increases delay
	●	NAND/NOR rise/fall behavior can differ
	●	duplicating a gate reduces downstream load
	●	duplicating a gate also increases upstream input load
That last point is particularly important.
￼
4. Why gate duplication cannot be evaluated locally
Suppose:
```text           ┌──> A x -> g ───┼──> B           ├──> C           └──> D ```
Duplicating g gives:
```text           ┌-> g1 -> A,B inputs ---|           └-> g2 -> C,D ```
The benefit is that each output sees less fanout.
However, the inputs of g1 and g2 are now both connected to the upstream logic.
Therefore:
[ C_{upstream} ]
increases.
So the decision cannot be made from the output fanout alone.
This prototype evaluates a duplication by rebuilding the candidate DAG and recomputing the entire circuit timing.
A duplication is accepted only if:
[ T_{critical,new} < T_{critical,old} ]
This automatically includes both:
	●	downstream load reduction
	●	upstream load increase
￼
5. Exact 4×4 multiplier
The experiment uses an unsigned 4×4 multiplier.
Every final circuit is exhaustively checked over:
[ 16\times16=256 ]
input pairs.
Thus the optimization criterion is:
[ \boxed{\text{exact functionality is a hard constraint}} ]
There is no approximate arithmetic in this experiment.
￼
6. Full-adder variants compared
Three exact 9-gate full-adder implementations are inserted into the same multiplier topology.
A. Gate-count-only mixed NAND/NOR
This is the earlier 9-gate solution found without timing-aware selection.
B. Arrival-aware mixed NAND/NOR
This is the earlier 9-gate solution found with late-carry arrival in the local score.
C. All-NAND 9-gate full adder
This is a standard exact 9-NAND implementation.
The simplified physical model deliberately makes NOR2 somewhat less favorable than NAND2.
This tests the question:
> If NOR is physically more expensive, will an all-NAND realization actually become better?
￼
7. Reproduced result
Using the default normalized library:
|Circuit              |Gates  |Logical depth|Normalized area|Estimated delay| |---------------------|------:|------------:|--------------:|--------------:| |Gate-count-only mixed|124    |37           |138.4          |88.110         | |Arrival-aware mixed  |124    |28           |131.2          |67.885         | |All-NAND 9-gate FA   |**124**|**28**       |**124.0**      |**63.000**     |
All circuits pass all 256 multiplier input pairs exactly.
In this model, the all-NAND version wins.
This does not prove that NAND-only is always physically best.
It shows that once NAND and NOR have different physical costs, the optimizer must use the real cost model rather than treating them as identical unit gates.
￼
8. Fanout-aware gate duplication result
Starting from the all-NAND 124-gate multiplier, the optimizer greedily tries exact logic-preserving gate duplication.
A candidate move:
	1.	chooses a shared gate
	2.	clones the same Boolean gate
	3.	moves some sink pins to the clone
	4.	recomputes all loads
	5.	recomputes all rise/fall arrival times
	6.	accepts the move only if global critical delay improves
One reproduced run gives:
|Duplications|Gates|Area |Critical delay| |-----------:|----:|----:|-------------:| |0           |124  |124.0|63.00         | |1           |125  |125.0|62.15         | |2           |126  |126.0|61.45         | |3           |127  |127.0|60.95         | |4           |128  |128.0|**60.20**     |
After four accepted duplications:
[ 124\rightarrow128 ]
gates, while:
[ 63.0\rightarrow60.2 ]
delay units.
That is approximately:
[ 4.44% ]
critical-delay reduction for roughly:
[ 3.23% ]
normalized area increase.
The final circuit remains exact for all 256 input pairs.
￼
9. Why this is more useful than a simple fanout penalty
A simple prototype rule could be:
[ penalty=\alpha\max(0,fanout-2) ]
This can be useful as a heuristic.
However, it cannot properly model the tradeoff caused by duplication.
The current method is stronger:
[ \boxed{\text{actually modify the DAG and recompute timing}} ]
Therefore no manually chosen rule such as:
> fanout ≥ 3 means +0.2 delay
is required for the duplication decision.
The physical model itself determines whether the move is beneficial.
￼
10. Logical depth is no longer the final objective
A major consequence is:
[ \boxed{ \text{minimum depth} \neq \text{minimum physical delay} } ]
Two circuits can both have depth 28 while having different:
	●	NAND/NOR composition
	●	fanout
	●	input capacitance
	●	output load
	●	transition direction
and therefore different delay.
In the experiment:
[ depth=28 ]
remains unchanged while the delay is improved by gate duplication.
Thus depth should become a secondary diagnostic metric.
The optimization target should instead be a Pareto set such as:
[ ( T_{critical}, Area, Power ) ]
￼
11. Next useful extensions
Drive-strength choices
Add cell variants such as:
```text NAND2_X1 NAND2_X2 NAND2_X4 NOR2_X1 NOR2_X2 INV_X1 INV_X2 BUF_X2 BUF_X4 ```
Then the optimizer can choose between:
	●	sharing
	●	duplication
	●	buffering
	●	sizing up a gate
	●	changing polarity
	●	changing gate type
Real Liberty timing
Replace:
[ p+rC_{load} ]
with timing lookup tables from a real .lib:
[ delay
f( input\ slew, output\ capacitance, input\ pin, rise/fall ) ]
and propagate output slew as well as arrival time.
Wire parasitics
Eventually include:
[ C_{wire},R_{wire} ]
from placement/routing estimates.
Pareto optimization
Instead of greedily accepting only the best delay move, preserve candidates such as:
```text fast / larger balanced small / slower ```
Then the result is a real area-delay Pareto front.
￼
12. Relation to the earlier Boolean-expression optimizer
The full intended pipeline is now:
```text existing exact circuit         |         v local cut / cone extraction         |         v exact Boolean function         |         v equivalent expression generation   - reassociation   - De Morgan   - polarity   - NAND/NOR restructuring         |         v DAG realization choices   - share   - duplicate   - buffer   - cell size         |         v physical-aware timing propagation         |         v (area, delay, power) Pareto selection         |         v exact equivalence verification         |         v replace cone and repeat ```
This combines the earlier exact logical search with physical timing awareness.
￼
13. Running the code
Default:
```bash python physical_aware_4x4_multiplier_optimizer.py ```
Limit duplication search:
```bash python physical_aware_4x4_multiplier_optimizer.py --max-duplications 4 ```
The script prints:
	●	exact verification status
	●	gate count
	●	logical depth
	●	normalized area
	●	load-aware critical delay
	●	each accepted gate-duplication move
￼
14. Current interpretation
The current experiment supports three conclusions:
	1.	NAND/NOR must not be modeled as identical unit-delay gates.
	2.	Fanout should affect timing explicitly.
	3.	Sharing versus duplication should itself be an optimization variable.
The most important conceptual shift is:
[ \boxed{ \text{optimize the actual modeled delay of the whole DAG} } ]
rather than optimizing gate count or logic depth first and trying to repair physical problems afterward.