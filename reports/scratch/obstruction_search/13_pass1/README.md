# Pass 1 over the open classes of the pathwidth dataset (owner, 2026-11-03)

`pass1.py`: every open class with a recorded layout (the dataset's jsonl, 336 open records, 24 in `SKIP`),
ten minutes of minor search each on 24 niced workers, minors at 40–90% of n and never above 1,000 vertices.
**312 classes, no error rows, 4 closed** (`results_pass1.csv`, `run_unlimited.py`'s format): `pwc-17702`
(jgiraldezlevy…gaifman_2, 111 vertices) = 34 by a 56-vertex minor, `pwc-17681` (Promedus_14_9, 173) = 13 by
a 69-vertex minor, `pwc-17406` (ex165, 222) = 16 by a 123-vertex minor, `pwc-17393` (ex152, 770) = 15 by a
308-vertex minor in 5.4 s. Its class list has no blank-component hole: every open jsonl record carries a
measured `max_component`, the largest is 1,024 (he027). Its 59 GB peak was 24 workers on graphs to 1,024
vertices, nothing larger. Flaw in `pass1.csv`: the four closed rows carry an unlabelled 21st column
(`minor`), so `pandas.read_csv` rejects the file; read it with `csv.reader`, or use `results_pass1.csv`.

`pass1b.py`: the open classes with *no* recorded layout (742), 60 s of the C program on the whole graph for
a layout, then the same search. Of the 742: 54 have a component above the engine's 1,024 limit; **78 have a
blank `max_component`** (the dataset's never-measured `big` graphs, PACE 2017 heuristic and PACE 2016,
6,040 to 24.6 M vertices) and the original filter's `int(x or 0)` let every one of them through — one worker
reached 74 GB and the run was killed at 18:10; the filter now treats blank as over the limit
(`pass1b.py.bak-20261103` is the original); and the 610 within the limit are all Frinhani 2018 "large"
(400–1,000 vertices), of which **96 ran** (all 1,000 vertices, `pass1b.csv`, no error rows, **none closed**:
floors at 35–843 against greedy widths of 172–982) before the owner excluded the rest. So pass 1b is
complete under two exclusions: the owner's Frinhani skip (514 classes) and the blank-component patch (78).

`check_pass1.py`: every certificate of both passes through `paper1/obstruction_check.py check-minor`
(own replay, quotient hash, C re-run at the search's 20 s cap; rule-free `vsmemo` + `checkF` where the
minor has ≤ 80 vertices), 2026-11-03 18:35–18:38, 21 CPU-minutes. **100 of 100 verified, zero rejected,
zero contradictions** (`check_pass1.csv`, `check_pass1.jsonl`): the four pass 1 closures (the two minors
under 80 vertices also rule-free verified), and the 96 pass 1b floors, on 72 of which the C program refutes
`floor − 2` outright so the floor is the minor's exact pathwidth, the other 24 resting on the printed `lower`.
The pass 1b certificates live in `certificates_1b/` (git-ignored, 279 MB; hashes and verdicts in `check_pass1.jsonl`);
pass 1's are in `certificates/` (17 MB, committed).

**Folded** (owner, 2026-11-03 evening): `paper1/dataset.py`'s `OPEN_RUNS` now reads the obstruction evidence rows
(07_open, 12_tenmin/open, this directory's `results_pass1.csv`), so NY_13, ex139 and the four closures above enter
the dataset as `certified:minor` with their contraction certificates; the BalancedTree_3_5 theorem row still folds as
`solution` at the recorded width (a `certified:theorem` row needs `dataset_check.py` to know the branch-lemma case).

`pass2.py` (owner, same evening): one hour of search each on 12 niced workers over the 95 open classes nearest to
closing — the 66 one stack short (pass 1's 46 and the unlimited run's 20), 15 two short, 14 three short — seed 13,
a 10 GB address-space limit per worker and a systemd scope at 80 GB. Outputs `pass2.csv`, `certificates_2/`,
`results_pass2.csv`, `pass2.log`.
