# Ten minutes of minor search each (owner's request, 2026-11-03)

`run.py`: (a) the 11 dense-shoulder instances loop0013 left open, 600 s ladder + 600 s search each,
seed 7, C cap 10 s (`eleven.csv`, `eleven.log`); (b) the 22 open dataset classes one stack short,
600 s each, minors at 40–90% of n, seed 7, C cap 20 s (`open/`, `open.log`). Six workers each, nice 19.

**Result.** (a) No closure: search floors one below the optimum on 100-100-4-1 (45/46), 125-125-2-2 (24/25),
125-125-6-2 (76/77), 125-125-6-3 (79/80), two to four below on the other seven; minors at 69–112 vertices.
(b) **One class closed: `pwc-17381` (ex139, PACE 2017, 334 vertices): a 134-vertex contraction minor of
pathwidth 10 (refutation of 9 in 1.05 s), verified by `paper1/obstruction_check.py check-minor` (replay,
hashes, C re-run; rule-free check skipped above 80 vertices), so pathwidth(ex139) = 10 = the recorded layout's
width.** The evidence row is `open/results_obstruction.csv` in `run_unlimited.py`'s format (with the
branch-lemma tree row copied from item 07); folding it into the dataset is the OPEN_RUNS change loop0013 proposed
(`07_open/open_runs_proposal.diff`) and a dataset rebuild — the owner's call. The other 21 classes: floor
width − 1 again (width − 2 on `494_bus`), minors 86–285 vertices; `open/lower_bounds.csv` lists the four whose floor
rose above the record. With NY_13 (loop0013) and the ternary tree, three of the 24 open classes are closed.
