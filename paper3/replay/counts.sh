#!/bin/bash
# Regenerates every count the paper quotes from the replay logs.
# Usage: bash paper3/replay/counts.sh [path to the full build_main.log]
# (default: the sandbox's ~/dev/untrusted/replay/logs/build_main.log; the
# committed copy under logs/run2/ holds its SHA-256 and last 200 lines).
L=${1:-/home/al/dev/untrusted/replay/logs/build_main.log}
R=$(dirname "$0")/logs/run2
echo "build_main.log: $L"
echo "sha256:            $(sha256sum "$L" | cut -c1-64)   (committed: $(cut -c1-64 $R/build_main_sha256.txt))"
echo "total lines:       $(wc -l < "$L")"
echo "modules built:     $(grep -c '^✔.*Built OAI' "$L")   (lines '✔ [i/N] Built OAI...')"
echo "distinct modules:  $(grep -o 'Built OAI[^ ]*' "$L" | sort -u | wc -l)"
echo "job total:         $(grep -o 'Build completed successfully ([0-9]* jobs)' "$L")"
echo "error lines:       $(grep -c -i 'error' "$L")"
echo "sorry warnings:    $(grep -c 'sorry' "$L")"
echo "warning lines:     $(grep -c -i 'warning' "$L")   of which 'has local changes' (the lakefile's compatibility patches): $(grep -c 'has local changes' "$L")"
echo "build start/end:   $(grep -o '^\[[^]]*\] === lake build' $R/sandbox_run2.txt | cut -c2-20)  ->  $(grep -o '^\[[^]]*\] lake build exit code [0-9]*' $R/sandbox_run2.txt | cut -c2-20)  (exit $(grep -o 'lake build exit code [0-9]*' $R/sandbox_run2.txt | grep -o '[0-9]*$'))"
echo "axioms:            $(grep -A2 'depends on axioms' $R/axioms.txt | tr -d '\n' | tr -s ' ')"
echo "lean:              $(grep -o 'Lean (version [^)]*)' $R/sandbox_run2.txt)"
echo "mathlib rev:       $(grep -o 'mathlib rev:.*' $R/sandbox_run2.txt | grep -o '[0-9a-f]\{40\}')"
echo "DONE:              $(cat $R/DONE)"
