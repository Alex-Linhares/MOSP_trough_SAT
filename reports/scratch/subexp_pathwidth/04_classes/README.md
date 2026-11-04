# loop0014 item 04 — classes with `O(n)`-bit layouts? (2026-11-04)

Report section: `reports/subexp_pathwidth.md` §4. Code:
`learning/subexp_classes.py`, tests `tests/test_subexp_classes.py` (9).

Files:

- `check_atlas7.log`, `check.json` — the brute-force check of every
  statement of §4 (the cobipartite normal form on every cobipartition of
  every atlas graph to 7 vertices and on every `A × B` edge set with
  `a + b ≤ 8`; the split dichotomy and criterion on every split partition
  and on 300 random split graphs on 11 vertices; the twin lemma and the
  unit DP on every atlas graph; the orientation measurement on every
  subcubic atlas graph; the gap lemma's arithmetic). §4.8 tabulates it.
  Zero failures. Committed.
- No encoding is claimed to fit, so there is no encoding to check beyond
  the structural statements above; the one `O(n)`-bit object examined
  (the acyclic orientation, §4.3) is measured, not claimed.
- Nothing was downloaded, run on an instance, or written to `solutions/`.
  The Gustedt extract used for §4.2 and §4.5 is
  `../03_reductions/1993-Gustedt-Pathwidth-Chordal-Graphs-DAM.txt`
  (git-ignored; regenerate as in that directory's README).

Regenerate:

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/04_classes
    nice -n 19 python3 -m learning.subexp_classes --nmax 7 --patterns-max 8 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_classes.py -q
