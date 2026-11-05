# The sandboxed replay of family 378 (`OAI.Algorithms.SubexponentialSAT`)

Paper 3, item 01 (Ralph loop0015, 2026-11-05). Everything here is text
copied out of the sandbox at `~/dev/untrusted/replay/`; nothing produced
inside the sandbox is executed outside it. The pristine clone
`~/dev/untrusted/openai-math` (commit `4eaee875`) is never touched; the
replay builds a **fresh copy** of it at `~/dev/untrusted/replay/openai-math/`.

## What is replayed

`lake build OAI.Algorithms.SubexponentialSAT.Main` — the 3,091-module
import closure of the family's solution (never the default target, which
builds the whole collection: its `README.md` line 16 counts 721 manuscripts in 373 families) — followed by
`#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat`,
the one theorem the comparator JSON names
(`lean/ComparatorChallenges/SubexponentialSAT.json`, `theorem_names`),
at the toolchain the clone pins (`lean-toolchain`: `leanprover/lean4:v4.34.1`)
with upstream Mathlib at the manifest's revision, whose oleans come from
`lake exe cache get`.

## Isolation

`run_sandbox.sh` (below) runs `bwrap` under `taskset -c 0-7 nice -n 19`
with `/usr /lib /lib64 /bin /sbin /etc` bound read-only, `/proc`, `/dev`,
a `tmpfs` on `/tmp`, `/var` and `/home`, the private directory
`replay/home` bound at `/home/al` (so the repository `/home/al/dev/MOSP`
and the real home are invisible), `replay/` bound at `/replay`,
`--unshare-pid --unshare-ipc --unshare-uts --die-with-parent`; the
network is on (the lakefile's dependency clones, the `elan` and toolchain
downloads, the Mathlib cache). `replay.sh` runs inside with
`HOME=/home/al` = `replay/home` outside, installs `elan` there
(`ELAN_HOME=/home/al/.elan`), and `elan` fetches the pinned toolchain
from `lean-toolchain`.

## Timeline

| when (host clock, WET) | what |
|---|---|
| 2026-11-05 01:03:36 | **run 1** started by the coordinator (`sandbox.out` first line); `elan` installed; toolchain `v4.34.1` downloaded (01:03:40–01:05:39) |
| 01:05:39–01:13:40 | `lake exe cache get`: the lakefile's dependency clones (42 packages under `.lake/packages`, Mathlib included (item 10 recounted: an earlier count said 41)), then 8,908 Mathlib cache files downloaded and decompressed (`Decompressed 8908 file(s)`) |
| 01:13:40 | `lake build OAI.Algorithms.SubexponentialSAT.Main -j 8` **failed at once**: `error: unknown short option '-j'` (the whole of `build_main.log`, run 1); Lake `v4.34.1` has no `-j`/`--jobs` option (`lake --help`, `lake help build`) |
| 01:13:47 | `#print axioms` failed for want of a build (`unknown module prefix 'OAI'`); `DONE` = `1` |
| 01:16:17 | **run 2** (the one relaunch item 01 is allowed): `replay.sh` edited to drop `-j 8` and to read the Mathlib `rev` from the manifest correctly (`grep -B3`; the run-1 line was empty because `"rev"` precedes `"name"` in `lake-manifest.json`); `run_sandbox.sh` edited to prefix `taskset -c 0-7`, which is the core cap `-j 8` was meant to be; both run-1 originals kept under `logs/run1/` |
| 01:16:25 | run 2: `lake exe cache get` finds nothing to download (`Already decompressed 8908 file(s)`); `lake build` starts, 12,014 jobs of which the first ~8,900 are the cached Mathlib modules |
| 01:49:31 | run 2: `lake build exit code 0`, `Build completed successfully (12014 jobs)`; **33 min 6 s** of wall clock on eight cores for the family's 3,091 modules |
| 01:49:31–01:49:40 | `#print axioms … exact_count_and_sat` → `[propext, Classical.choice, Quot.sound]`; `lean --version` and the Mathlib `rev` logged; `DONE` = `0` |
| 01:50:55 | the second-kernel script launched (`run_sandbox_nanoda.sh`, below) |

Run 1's failure was a command-line error, not a failure of the proof or
of the toolchain: nothing of the family was compiled in run 1.

### The core cap

Lake sizes its worker pool from the hardware concurrency (32 here) and
has no option to lower it in `v4.34.1`, so `taskset -c 0-7` on the
`bwrap` line confines the whole sandbox to eight cores; `lake` then
spawns up to ~30 `lean` processes that share those eight cores. That is
the owner's "at most 8 workers" in CPU, not in process count, and it
drives the one-minute load average above 24 while the build runs (the
load counts runnable threads, the cores in use are eight).

## The scripts, verbatim (as run in run 2)

### `run_sandbox.sh`

```bash
#!/bin/bash
R=/home/al/dev/untrusted/replay
exec taskset -c 0-7 nice -n 19 bwrap \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /bin /bin --ro-bind /sbin /sbin \
  --ro-bind /etc /etc --ro-bind /run/systemd/resolve /run/systemd/resolve --proc /proc --dev /dev --tmpfs /tmp --tmpfs /var \
  --tmpfs /home --bind $R/home /home/al --bind $R /replay \
  --unshare-pid --unshare-ipc --unshare-uts --die-with-parent \
  --setenv HOME /home/al --setenv USER al --setenv TERM dumb \
  --chdir /replay -- /bin/bash /replay/replay.sh
```

### `replay.sh`

```bash
#!/bin/bash
# Runs INSIDE the bwrap sandbox: HOME=/home/al is the private replay home.
set -o pipefail
log() { echo "[$(date '+%F %T')] $*"; }
export ELAN_HOME=$HOME/.elan PATH=$HOME/.elan/bin:/usr/local/bin:/usr/bin:/bin
log "sandbox start; nproc $(nproc); home $HOME; whoami $(whoami)"
if [ ! -x $ELAN_HOME/bin/elan ]; then
  log "installing elan into $ELAN_HOME"
  curl -sSf https://elan.lean-lang.org/elan-init.sh -o /tmp/elan-init.sh && sh /tmp/elan-init.sh -y --default-toolchain none --no-modify-path 2>&1 | tail -3
fi
cd /replay/openai-math/lean || exit 2
log "toolchain file: $(cat lean-toolchain)"
log "lake version: $(lake --version 2>&1 | head -1)"
log "=== lake exe cache get (Mathlib oleans)"
lake exe cache get 2>&1 | tail -5
log "=== lake build OAI.Algorithms.SubexponentialSAT.Main (no -j: this Lake has no such option; the core cap is taskset in run_sandbox.sh)"
lake build OAI.Algorithms.SubexponentialSAT.Main 2>&1 | tee /replay/logs/build_main.log | grep -E --line-buffered 'error|Error|warning: .*sorry|Build completed|built|✔|✖' | tail -2000 > /replay/logs/build_filtered.log
rc=${PIPESTATUS[0]}
log "lake build exit code $rc"
cat > /tmp/Axioms.lean <<'EOL'
import OAI.Algorithms.SubexponentialSAT.Main
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat
EOL
log "=== #print axioms"
lake env lean /tmp/Axioms.lean 2>&1 | tee /replay/logs/axioms.log
log "lean: $(lake env lean --version 2>&1)"
log "mathlib rev: $(grep -B3 '"name": "mathlib"' lake-manifest.json | grep '"rev"' | head -1)"
log "DONE rc=$rc"
echo $rc > /replay/logs/DONE
```

### Run 1's originals (differ only as the timeline says)

`run_sandbox.sh`, run 1:

```bash
#!/bin/bash
R=/home/al/dev/untrusted/replay
exec nice -n 19 bwrap \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /bin /bin --ro-bind /sbin /sbin \
  --ro-bind /etc /etc --ro-bind /run/systemd/resolve /run/systemd/resolve --proc /proc --dev /dev --tmpfs /tmp --tmpfs /var \
  --tmpfs /home --bind $R/home /home/al --bind $R /replay \
  --unshare-pid --unshare-ipc --unshare-uts --die-with-parent \
  --setenv HOME /home/al --setenv USER al --setenv TERM dumb \
  --chdir /replay -- /bin/bash /replay/replay.sh
```

`replay.sh`, run 1:

```bash
#!/bin/bash
# Runs INSIDE the bwrap sandbox: HOME=/home/al is the private replay home.
set -o pipefail
log() { echo "[$(date '+%F %T')] $*"; }
export ELAN_HOME=$HOME/.elan PATH=$HOME/.elan/bin:/usr/local/bin:/usr/bin:/bin
log "sandbox start; nproc $(nproc); home $HOME; whoami $(whoami)"
if [ ! -x $ELAN_HOME/bin/elan ]; then
  log "installing elan into $ELAN_HOME"
  curl -sSf https://elan.lean-lang.org/elan-init.sh -o /tmp/elan-init.sh && sh /tmp/elan-init.sh -y --default-toolchain none --no-modify-path 2>&1 | tail -3
fi
cd /replay/openai-math/lean || exit 2
log "toolchain file: $(cat lean-toolchain)"
log "lake version: $(lake --version 2>&1 | head -1)"
log "=== lake exe cache get (Mathlib oleans)"
lake exe cache get 2>&1 | tail -5
log "=== lake build OAI.Algorithms.SubexponentialSAT.Main -j 8"
lake build OAI.Algorithms.SubexponentialSAT.Main -j 8 2>&1 | tee /replay/logs/build_main.log | grep -E --line-buffered 'error|Error|warning: .*sorry|Build completed|built|✔|✖' | tail -2000 > /replay/logs/build_filtered.log
rc=${PIPESTATUS[0]}
log "lake build exit code $rc"
cat > /tmp/Axioms.lean <<'EOL'
import OAI.Algorithms.SubexponentialSAT.Main
#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat
EOL
log "=== #print axioms"
lake env lean /tmp/Axioms.lean 2>&1 | tee /replay/logs/axioms.log
log "lean: $(lake env lean --version 2>&1)"
log "mathlib rev: $(grep -A3 '"name": "mathlib"' lake-manifest.json | grep rev | head -1)"
log "DONE rc=$rc"
echo $rc > /replay/logs/DONE
```

Run 2 was launched from the host as

```bash
cd ~/dev/untrusted/replay && rm -f logs/DONE && setsid nohup bash -c 'bash /home/al/dev/untrusted/replay/run_sandbox.sh; echo "wrapper: run_sandbox.sh exited $? at $(date "+%F %T")" >> /home/al/dev/untrusted/replay/logs/wrapper.out' > logs/sandbox.out 2>&1 < /dev/null &
```

(the `bash -c` wrapper stays alive as the parent of `bwrap`, which
`--die-with-parent` requires; the launching shell may exit).

## Result of run 2

**Exit code 0** (`logs/run2/DONE`). From `build_main.log` (SHA-256
`d313f594daa3cd3713f872bde8b4d33138820eeec5a335a21a276846aa54e21e`,
3,160 lines; regenerate every number with `bash paper3/replay/counts.sh`,
output in `logs/run2/counts.txt`):

| quantity | value |
|---|---|
| `Build completed successfully` | `(12014 jobs)` — the job total counts the cached Mathlib and dependency modules; none of them was compiled |
| family modules compiled (`Built OAI.Algorithms.SubexponentialSAT.…` lines) | **3,091 distinct**, exactly the audit's closure (`reports/scratch/eth_audit/closure_modules.json`: same 3,091 names, set difference empty both ways); 3,083 lines carry `✔` and 8 carry `ℹ` because those eight files print information while compiling (see the next row) |
| lines containing `error` | **0** |
| lines containing `sorry` | **0** |
| lines containing `warning` | 11, all `<package>: repository '…' has local changes` — the lakefile's own compatibility patches to eleven dependencies (`lean/lakefile.lean` lines 188–191, applied by its `run_cmd` hook; none of them is Mathlib) |
| `depends on axioms` lines inside the build | 19, from the 8 source files of the closure that contain a `#print axioms` command (17 files of the family directory carry one, 9 of them outside the closure; item 04 counted, item 10 corrected this cell), every one `[propext, Classical.choice, Quot.sound]` (`logs/run2/axioms_in_build.txt`); among them `SqrtLogSpace/Final.lean` lines 197–201 print the axioms of `compiled_exact_count_and_sat`, `exact_count_and_sat`, `exact_count_eth`, `sat_polynomial_space` and `original_sat_main` |
| wall clock of the build | 01:16:25 → 01:49:31, **33 min 6 s**, eight cores, `nice -n 19`, ~30 `lean` processes sharing them |
| `#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat` (a separate `lake env lean` run after the build) | `[propext, Classical.choice, Quot.sound]` (`logs/run2/axioms.txt`) |
| Lean | `Lean (version 4.34.1, x86_64-unknown-linux-gnu, commit 5045d0056413266e57c625dcd7c365b10e377c52, Release)`; `Lake version 5.0.0-src+5045d00 (Lean version 4.34.1)` |
| Mathlib | `"rev": "d13f23b723b8a846827a245b89c10fc7d3f11612"` from `lake-manifest.json`, upstream `leanprover-community/mathlib4`, oleans from `cache.mathlib.org` (8,908 cache files) |
| the replay copy | `git rev-parse HEAD` = `4eaee87548250b2682affda7d05d947c05554bae`, the same as the pristine clone; the comparator file and the solution files hash the same in both (`logs/run2/hashes.txt`) |

Hashes (`logs/run2/hashes.txt`, `sha256sum`): the comparator statement
`lean/ComparatorChallenges/SubexponentialSAT.lean`
`4183b2057cff350d66848215ff7167196dfc20e1891b598fdddea59077a76685`;
`OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean`
`040360a8465957622d934e5f1bb4f2cce8dab950e78f52033fbf70da493184f5`;
`OAI/Algorithms/SubexponentialSAT/Main.lean`
`cbd4cebf71f1d3239c21241f946d05e8de802dbb9c138713f8e7182d868b2d1c`;
`build_main.log` as above.

What the log does not contain: any module compiled from outside the
family (Mathlib and the 40 other dependencies came from the cache or
were never needed), any `native_decide`, `sorry` or `error` line, and
any rebuild of a module already built (run 1 compiled nothing).

## The second kernel (nanoda)

**Ran, and passed.** `run_sandbox_nanoda.sh` launched at 01:50:55
(host clock) after run 2's `DONE`; `logs/nanoda/nanoda_sandbox.txt` is
its timeline. Inside the sandbox:

| step | when | result |
|---|---|---|
| `lake build` of `lean4export` (tag `v4.34.0`, commit `076e8e57…`, its `lean-toolchain` overridden to `leanprover/lean4:v4.34.1`) | 01:50:55–01:50:58 | `Build completed successfully (6 jobs)` (`logs/nanoda/lean4export_build.txt`) |
| `lake env lean4export OAI.Algorithms.SubexponentialSAT.Main -- OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat > export.ndjson`, from `/replay/openai-math/lean` | 01:50:58–01:52:06 (68 s) | exit 0; **2,355,666,449 bytes, 43,633,742 lines**; header `{"meta":{"exporter":{"name":"lean4export","version":"3.1.0"},"format":{"version":"3.1.0"},"lean":{"githash":"5045d0056413266e57c625dcd7c365b10e377c52","version":"4.34.1"}}}` (`logs/nanoda/export_meta.txt`); SHA-256 `bdbc9afe336fea99b01bc4eced6e4232153afdefe13a1095cdc5ca9499e3f573` (`export_sha256.txt`); the file stays in the sandbox directory (git-ignored) |
| `cargo build --release` of `nanoda_lib` (commit `8de7e0c4…`, crate version 0.4.31; `rustc 1.99.1 (58cf8f9c3 2026-10-13)`, `cargo 1.99.1`, the host's stable toolchain bound read-only) | 01:52:06–01:52:17 | `Finished release profile` in 10.68 s (`logs/nanoda/nanoda_build.txt`) |
| `nanoda_bin nanoda_config.json` (`logs/nanoda/nanoda_config.json`: the export path, 8 threads, 1 GB stack per worker, `permitted_axioms = [propext, Classical.choice, Quot.sound]`, `unpermitted_axiom_hard_error = false`, `nat_extension` and `string_extension` on, `pp_declars = [exact_count_and_sat]`) | 01:52:17–01:54:07 (110 s) | exit 0; **`Checked 95176 declarations with no errors`**; the pretty-printer printed back the theorem's full statement and the three axioms as nanoda parsed them (`logs/nanoda/nanoda_check.txt`, 104 lines) |

`grep -c '"axiom"' export.ndjson` = **3**: the export carries exactly three
axiom declarations, so the permitted list could not have been exceeded
by an axiom the hard-error setting skipped. `NANODA_DONE` = `0`.
Peak memory was not measured; `free` showed 11 GB used on the host after
the run.

What this adds to the single-kernel replay: the same theorem, with its
transitive dependencies as the built environment holds them, type-checks
under a checker that shares no code with the Lean kernel, under the same
three axioms. What it does not add: trust in `lean4export` (that the
export is faithful to the environment) and in `nanoda_lib` itself; and it
is still not the comparator run (no statement-level match through
`lean4export` against the challenge file — that match is item 04's,
textual).

### `run_sandbox_nanoda.sh` (recorded before it ran)

Identical to `run_sandbox.sh` except that it runs `nanoda.sh` and binds
the host's Rust toolchain directory read-only at its own path
(`/home/al/.rustup/toolchains/stable-x86_64-unknown-linux-gnu`, binaries
only; `cargo` writes to a private `CARGO_HOME` inside the sandbox home):

```bash
#!/bin/bash
# Same bwrap line as run_sandbox.sh (same isolation, same core cap), running
# nanoda.sh instead of replay.sh; the host's Rust toolchain is bound READ-ONLY
# at its own path (binaries only), cargo writes to a private CARGO_HOME.
R=/home/al/dev/untrusted/replay
RT=/home/al/.rustup/toolchains/stable-x86_64-unknown-linux-gnu
exec taskset -c 0-7 nice -n 19 bwrap \
  --ro-bind /usr /usr --ro-bind /lib /lib --ro-bind /lib64 /lib64 --ro-bind /bin /bin --ro-bind /sbin /sbin \
  --ro-bind /etc /etc --ro-bind /run/systemd/resolve /run/systemd/resolve --proc /proc --dev /dev --tmpfs /tmp --tmpfs /var \
  --tmpfs /home --bind $R/home /home/al --bind $R /replay --ro-bind $RT $RT \
  --unshare-pid --unshare-ipc --unshare-uts --die-with-parent \
  --setenv HOME /home/al --setenv USER al --setenv TERM dumb \
  --chdir /replay -- /bin/bash /replay/nanoda.sh
```

### `nanoda.sh` (recorded before it ran)

```bash
#!/bin/bash
# Runs INSIDE the bwrap sandbox (run_sandbox_nanoda.sh): second-kernel replay.
# 1. build lean4export (tag v4.34.0, lean-toolchain overridden to the pinned
#    v4.34.1 so that it reads the oleans the replay produced);
# 2. export exact_count_and_sat and its transitive dependencies from the
#    built OAI.Algorithms.SubexponentialSAT.Main environment (NDJSON);
# 3. build nanoda_lib (Rust) and check the export with the three axioms permitted.
set -o pipefail
log() { echo "[$(date '+%F %T')] $*"; }
RT=/home/al/.rustup/toolchains/stable-x86_64-unknown-linux-gnu
export ELAN_HOME=$HOME/.elan PATH=$HOME/.elan/bin:$RT/bin:/usr/local/bin:/usr/bin:/bin
export CARGO_HOME=$HOME/cargo_home
L=/replay/logs
log "nanoda.sh start; nproc $(nproc); rustc $(rustc --version); cargo $(cargo --version)"
cd $HOME/src/lean4export || exit 2
log "lean4export commit $(git rev-parse HEAD); toolchain file was: $(cat lean-toolchain)"
echo "leanprover/lean4:v4.34.1" > lean-toolchain
log "=== lake build lean4export (toolchain $(cat lean-toolchain))"
lake build 2>&1 | tail -5 | tee $L/lean4export_build.log
rc=${PIPESTATUS[0]}; log "lean4export build exit $rc"; [ $rc -ne 0 ] && { echo $rc > $L/NANODA_DONE; exit $rc; }
EXP=$HOME/src/lean4export/.lake/build/bin/lean4export
cd /replay/openai-math/lean || exit 2
log "=== export: lake env lean4export OAI.Algorithms.SubexponentialSAT.Main -- OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"
lake env $EXP OAI.Algorithms.SubexponentialSAT.Main -- OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat > $L/export.ndjson 2> $L/export.err
rc=$?; log "export exit $rc; size $(stat -c %s $L/export.ndjson) bytes; lines $(wc -l < $L/export.ndjson)"
head -c 600 $L/export.ndjson | head -1 > $L/export_meta.txt
[ $rc -ne 0 ] && { echo $rc > $L/NANODA_DONE; exit $rc; }
cd $HOME/src/nanoda_lib || exit 2
log "nanoda_lib commit $(git rev-parse HEAD)"
log "=== cargo build --release (nanoda_lib)"
cargo build --release 2>&1 | tail -5 | tee $L/nanoda_build.log
rc=${PIPESTATUS[0]}; log "nanoda build exit $rc"; [ $rc -ne 0 ] && { echo $rc > $L/NANODA_DONE; exit $rc; }
cat > /tmp/nanoda_config.json <<EOL
{
    "export_file_path": "$L/export.ndjson",
    "use_stdin": false,
    "num_threads": 8,
    "stack_size_bytes": 1073741824,
    "permitted_axioms": ["propext", "Classical.choice", "Quot.sound"],
    "unpermitted_axiom_hard_error": false,
    "nat_extension": true,
    "string_extension": true,
    "pp_declars": ["OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"],
    "pp_to_stdout": true,
    "print_success_message": true
}
EOL
cp /tmp/nanoda_config.json $L/nanoda_config.json
log "=== nanoda check"
./target/release/nanoda_bin /tmp/nanoda_config.json > $L/nanoda_check.log 2>&1
rc=$?; log "nanoda exit $rc"; tail -5 $L/nanoda_check.log
log "NANODA_DONE rc=$rc"
echo $rc > $L/NANODA_DONE
```

Sources, cloned from the host into the sandbox home before the run
(`git clone`, nothing executed): `leanprover/lean4export` at tag
`v4.34.0` (commit `076e8e57707e813375e8f9da8bf989799ace9680`,
2026-09-14; no `v4.34.1` tag exists, and its `lean-toolchain` is
overridden to `v4.34.1` inside the sandbox because an exporter must be
built with the same Lean that produced the oleans it reads);
`ammkrn/nanoda_lib` at `master`, commit
`8de7e0c4ed3052745a7f8725164efd9e76d84c56` (2026-10-29), whose README
says it consumes `lean4export`'s NDJSON export format (3.1.0,
`format_ndjson.md`).

## Files in `logs/`

| file | what |
|---|---|
| `run1/sandbox_run1.txt` | run 1's `sandbox.out` (timeline, the cache download progress lines) |
| `run1/build_main_run1.txt` | run 1's whole `build_main.log`: the `-j` error |
| `run1/axioms_run1.txt` | run 1's `axioms.log` (the `unknown module prefix 'OAI'` error after the 41 "has local changes" warnings, which are the lakefile's compatibility patches, see `lean/lakefile.lean` lines 188–191 and 290–371) |
| `run1/DONE_run1` | `1` |
| `run1/*.run1` | the two scripts as run 1 ran them |
| `run2/` | run 2's `sandbox_run2.txt`, `build_filtered.txt`, `axioms.txt`, `DONE`, `build_main_sha256.txt`, `build_main_tail200.txt`, `versions.txt`, `hashes.txt` (filled when run 2 ends) |
| `nanoda/` | the second-kernel run: `nanoda_sandbox.txt` (timeline), `lean4export_build.txt`, `export_meta.txt`, `export_sha256.txt` (hash, size, line count of the git-ignored export), `export_err.txt` (empty after dropping the `local changes` warnings), `nanoda_build.txt`, `nanoda_config.json`, `nanoda_check.txt`, `NANODA_DONE`, `nanoda_launched_at.txt` |

The full `build_main.log` of run 2 stays in the sandbox directory
(git-ignored here by `paper3/.gitignore`); its SHA-256 is committed.
