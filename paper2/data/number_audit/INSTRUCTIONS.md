# Number audit: shared instructions for every auditor (loop0008 item 07, 2026-10-03)

You audit EVERY quantitative claim in your assigned document(s) in /home/al/dev/MOSP/paper2/.
A quantitative claim = any number stated as a fact (counts, percentages, times, node counts,
core-hours, page/section/theorem numbers of citations, sizes, dates of measurement, Lean theorem
names cited as the source of a fact, "all N", "k of N"). Skip pure numbering of our own sections
and pure arithmetic examples inside proofs unless they state a result (e.g. "close = 3" in a
counterexample IS a claim: check it against the Lean theorem or a script).

For each claim, record ONE table row:
| line | claim (short, with the value) | source (regenerate command / CSV / JSON / Lean theorem / held PDF+page) | check done | status |

Status is one of:
- REPRODUCED: you re-ran the command or recomputed from raw data now and got the same value.
- MATCHES-RECORD: matches the recorded data file / tables.md / log / Lean theorem statement (grep), not rerun.
- DRIFT: does not match; give the correct value and the evidence.
- STALE: was true when written but superseded by later events (e.g. a run that has since finished).
- UNSOURCED: no source found in the repository; say what you searched.
- UNCHECKED: checkable only by a run beyond the budget; say why.

Group repeated mentions of the same number in a row ("lines 12, 340, 902").

RULES
- Compute budget: at most ONE core for you, and no single command longer than ~10 minutes.
  Prefix any Python run with `nice -n 10`. The machine is shared with a 20-core run
  (`paper2.solver_fix_split`, PID in paper2/data/solver_fix_split.pid): never stop, restart or
  edit it, `paper2/solver_fix_split.py`, or `paper2/data/solver_fix_split_*`. Do NOT run
  `python -m paper2.solver_fix_split --tables` (it writes a file); `--summary` is read-only and fine.
- Never write to solutions/. Never run benchmarks.csearch / recertify / overnight. Never commit.
  Never edit CLAUDE.md. Never edit any .lean file. Do not run `lake build` (the gate does that);
  for Lean, grep the theorem name and read its statement.
- Prefer checking against recorded data (CSVs, *_tables.md, JSON, logs). Rerun a script only if
  it is cheap (read its docstring/argparse first; make sure it does not overwrite recorded data
  files with different parameters — if it writes, either use a --out option to a scratch path
  under /tmp, or do not run it). Python is `python3`; run from /home/al/dev/MOSP with `-m`.
- Literature citations: check page/section numbers against the held PDF in literature/
  (`pdftotext -layout file.pdf - | grep -n ...`). Do not fetch from the web.
- FIX every DRIFT in the source document you were assigned (only those documents), with the
  Edit tool, minimal change, keeping the author's style (short plain sentences). For a STALE
  claim, add a short dated note "*(2026-10-03, number audit: ...)*" rather than rewriting history,
  unless the text is a present-tense status line, in which case update it and say so.
  Do not touch other documents; if a drift is in another document, report it instead.
- Output: write your full report to /home/al/dev/MOSP/paper2/data/number_audit/<NAME>.md with
  (1) a header: document(s), line count, number of claims, counts per status;
  (2) the table;
  (3) "Fixes made": file:line, old -> new, evidence;
  (4) "Drifts in other documents" if any.
  Your final reply to me: the status counts, the list of fixes, and anything alarming
  (especially any sign a certified value or a theorem claim is wrong). Keep the reply under 400 words.
