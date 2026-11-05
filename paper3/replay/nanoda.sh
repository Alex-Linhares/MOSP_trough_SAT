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
