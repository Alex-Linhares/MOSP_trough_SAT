# Ralph Loop Setup Guide

The **Fresh Context Pattern** (aka "Ralph Loop") prevents context window degradation by spawning fresh agent sessions for each task while maintaining state through file-based persistence.

## Why Ralph Loops?

As sessions progress, context accumulates and performance degrades:

| Context Usage | Performance Impact | Symptoms |
|--------------|-------------------|----------|
| 0-50% | Baseline | Fast, accurate |
| 50-70% | 10-15% degradation | Slower, occasional repetition |
| 70-85% | 20-30% degradation | Confused about prior decisions |
| 85%+ | 40-50% degradation | Tool hallucination, missed requirements |

Ralph Loops solve this by resetting to 0% context at each iteration while preserving state in files.

---

## Folder Structure

```
Ralph_Loops/
├── Ralph_Loop_Guide.md    # This file
└── loop0001/              # First loop instance
    ├── TASK.md            # Immutable goal definition (read-only)
    ├── PROGRESS.md        # Mutable state (updated each iteration)
    ├── iterations.md      # Ordered work items (replaces near_misses.md)
    ├── loop.py            # The driver (one copy per loop)
    ├── knobs.json         # Run-time controls, re-read before every session
    ├── status.json        # What is running now, since when, which phase
    ├── loop.log, session_itNN.log/.jsonl, nohup.out   # written by the driver
    └── [optional files]   # e.g. gate.py, allowed_sorries.txt (loop0005)
```

*(Corrected 2026-09-30: this tree read `RalphLoops/` and `RALPH_LOOP_GUIDE.md`;
the folder in this repository is `Ralph_Loops/`. Loops 0001–0005 exist, all
finished; see "As practised here" at the end.)*

> **Naming convention**: The work-item list is called `iterations.md` (not `near_misses.md`).
> This makes loops general — they can track architectural tasks, problem-solving runs, or anything else.
> `loop.py` falls back to `near_misses.md` for backward compatibility with older loops.

Each new loop gets its own folder: `loop0001`, `loop0002`, etc.

---

## File Templates

### TASK.md (Immutable)

```markdown
# TASK: [Brief Title]

## Philosophy
[Key principles for this work - guide agent behavior]

## Current Focus
[What we're trying to achieve]

## Target Problems (in order)
[List of specific items to complete]

## Acceptance Criteria (per item)
- [ ] Criterion 1
- [ ] Criterion 2
- [ ] No regressions

## Completion Conditions
An item is DONE when either:
1. **Solved**: Meets all criteria, OR
2. **Blocked**: Documented with specific blockers

## Context
- **Key files**: [relevant files]
- **Testing**: [how to verify]
- **Constraints**: [what must not break]

## Important Notes
[Any critical guidance]
```

### PROGRESS.md (Mutable)

```markdown
# Progress Log

## Ralph Loop [NNNN] Status
- **Started**: YYYY-MM-DD
- **Target**: [N] items
- **Current**: 0/[N] SOLVED

---

## Iteration 1 — YYYY-MM-DD HH:MM
### Completed
- [What was done]

### Blockers
- [Any issues encountered]

### Next
- [What the next iteration should do]

---
```

Each iteration appends a new section. When all tasks complete:

```markdown
## Iteration N — YYYY-MM-DD HH:MM
### Completed
- All tasks verified

LOOP_COMPLETE
```

---

## Running a Ralph Loop

### Option 1: Manual (Recommended for Complex Work)

1. **Create the loop folder:**
   ```bash
   mkdir -p RalphLoops/loop0001
   ```

2. **Create TASK.md** with your goals

3. **Create empty PROGRESS.md:**
   ```markdown
   # Progress Log
   
   ## Ralph Loop 0001 Status
   - **Started**: 2026-02-09
   - **Current**: 0/N SOLVED
   
   ---
   ```

4. **Run iterations manually:**
   - Start fresh agent session
   - Agent reads TASK.md + PROGRESS.md
   - Agent works on ONE item
   - Agent updates PROGRESS.md
   - Agent commits changes
   - Repeat until LOOP_COMPLETE

### Option 2: Automated Script (`loop.py`)

Each loop folder contains a `loop.py` script that handles the full iteration cycle: spawning a fresh Claude session, running regression tests, auto-fixing regressions (up to 3 attempts), and committing results.

```bash
# Run from the loop folder:
cd RalphLoops/loop0007

# Run 10 iterations (default), resuming from current PROGRESS.md
python3 loop.py

# Run 60 iterations
python3 loop.py 60

# Run 60 iterations with a fresh start (resets PROGRESS.md)
python3 loop.py 60 --fresh

# Custom TASK.md and PROGRESS.md paths
python3 loop.py 20 /path/to/TASK.md /path/to/PROGRESS.md
```

*(Note 2026-09-30: the drivers in `Ralph_Loops/loop0001`–`loop0005` take only
`[N]`, `--fresh` and `--dry-run`; they read TASK.md and PROGRESS.md from their
own folder and ignore further positional arguments. With no `N` they run up to
`knobs.json`'s `max_iterations`.)*

**What `loop.py` does each iteration:**
1. Reads `TASK.md` + `PROGRESS.md` and finds the next task from `iterations.md` (falls back to `near_misses.md`)
2. Spawns a fresh `claude -p` session with the combined prompt
3. Runs regression tests after Claude finishes
4. If tests pass: commits all changes
5. If tests fail: asks Claude to fix (up to 3 attempts), then reverts code but keeps PROGRESS.md findings
6. Checks for `LOOP_COMPLETE` sentinel and exits if found

---

## Key Principles

### 1. ONE Task Per Iteration
Each iteration tackles exactly ONE item. This:
- Keeps iterations short (5-15 min)
- Prevents scope creep
- Makes progress visible

### 2. File-Based State
All state lives in files, not memory:
- **TASK.md**: Immutable goals
- **PROGRESS.md**: Accumulated results
- **Git commits**: Audit trail + rollback

### 3. Fresh Context Every Time
Each iteration starts with 0% context:
- No session continuation (`-c` flag)
- State injected via file reading
- No accumulated confusion

### 4. Completion Sentinel
The exact string `LOOP_COMPLETE` signals done:
- Must be added by agent, not script
- Agent verifies completion before adding
- Script checks and exits

---

## As practised here (added 2026-09-30)

How loops 0001–0005 were actually run in this repository. The procedure above
is the general pattern; this is what to do here.

**Launch** detached from the repository root, with the API key in the
environment, read from `~/.config/anthropic/api_key` (never typed on a command
line), so unattended sessions do not draw on the interactive login:

```bash
export ANTHROPIC_API_KEY="$(tr -d '\n' < ~/.config/anthropic/api_key)"
setsid nohup python Ralph_Loops/loopNNNN/loop.py >> Ralph_Loops/loopNNNN/nohup.out 2>&1 < /dev/null & disown
```

The driver refuses to start if the code directories have uncommitted changes,
and it commits each item with `git add -A`, so commit unrelated work first.
Never start a second driver on the same folder; it would corrupt its state.

**Check by PID, never by command text.** A `pgrep -f` or `pkill -f` on the
command line also matches the shell running the check (one session killed its
own shell that way). Use

```bash
pgrep -x -f "python Ralph_Loops/loopNNNN/loop.py"                  # the PID
tr '\0' '\n' < /proc/<pid>/environ | grep -c ANTHROPIC_API_KEY     # the key is set
cat Ralph_Loops/loopNNNN/status.json; tail Ralph_Loops/loopNNNN/loop.log
```

**Steer with `knobs.json`**, which is re-read before every session and every
fix attempt: `stop` (finish the current item, commit, exit), `pause`,
`iteration_cap_hours`, `fix_cap_hours`, `max_fix_attempts`, `max_iterations`,
`model`, `sleep_between_s`, `run_tests`. A session that died is marked `- [!]`
in `iterations.md`; flip it back to `- [ ]` to redo it, and relaunch if the
driver has exited.

**The gate.** Loops 0001–0004 gate on `python -m pytest tests/ -q -x`.
loop0005, whose items are Lean proofs, uses its own script,
`Ralph_Loops/loop0005/gate.py`: `lake build` passes, every file under
`lean/MOSPFormalization/Complex/` is imported, the count of `sorry` in Lean
code does not exceed the baseline plus `allowed_sorries.txt`, no new `axiom`,
and pytest passes. A loop whose correctness criterion is not the test suite
should write a gate like it and point `TEST_CMD` at it.

**Working beside a running loop**: use a separate git worktree and commit only
your own paths; never commit a file the loop's session has modified.

| loop | subject | items | ran |
|---|---|---|---|
| loop0001 | ML and the nature of MOSP, phase 1 | 8 | finished 2026-09-25 |
| loop0002 | the generated-ensemble campaign | 6 | 2026-09-26, 2 h 11 min |
| loop0003 | objects (`reports/ml_nature_plan_2.md`) | 14 | 2026-09-26, 16 sessions |
| loop0004 | the seven questions (`reports/ml_nature_plan_3.md`) | 13 | 2026-09-27 to 09-28 |
| loop0005 | Table 1 of Linhares & Yanasse (2002) in Lean (`lean/MOSPFormalization/Complex/`) | 14 | 2026-09-30, $37 |
