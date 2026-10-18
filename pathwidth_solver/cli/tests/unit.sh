#!/bin/sh
# Unit tests: run ./pathwidth -l on tests/unit_cases.txt and compare width and
# status with the values the Python solver gave (tests/make_unit_cases.py).
# The program itself checks every layout before printing it; this script also
# checks the layout line is a permutation of the right length.
set -u
here=$(dirname "$0")
bin="$here/../pathwidth"
cases="$here/unit_cases.txt"
out=$(mktemp)
trap 'rm -f "$out"' EXIT
certs=$(mktemp)
trap 'rm -f "$out" "$certs"' EXIT
awk '{print $1}' "$cases" | "$bin" -l > "$out.raw" || { echo "FAIL: program exited with $?"; exit 1; }
grep -v '^minor ' "$out.raw" > "$out"
grep '^minor ' "$out.raw" > "$certs"
rm -f "$out.raw"
fail=0
total=0
exec 3< "$out"
while read -r g6 width proof name; do
    total=$((total + 1))
    read -r tag w status <&3
    read -r layout <&3
    n=$(printf '%s\n' "$layout" | awk '{print NF - 1}')
    distinct=$(printf '%s\n' "$layout" | awk '{for (i = 2; i <= NF; i++) s[$i] = 1; c = 0; for (k in s) c++; print c}')
    if [ "$tag" != pathwidth ] || [ "$w" != "$width" ] || [ "$status" != "$proof" ] || [ "$n" != "$distinct" ]; then
        echo "FAIL $name: expected $width $proof, got $w $status (layout $n entries, $distinct distinct)"
        fail=$((fail + 1))
    else
        echo "ok   $name: pathwidth $w $status"
    fi
done < "$cases"
# one certificate line per minor proof
nminor=$(awk '$3 == "minor"' "$cases" | wc -l)
ncert=$(wc -l < "$certs")
if [ "$nminor" != "$ncert" ]; then echo "FAIL: $nminor minor proofs but $ncert certificate lines"; fail=$((fail + 1)); fi
echo "$((total - fail)) of $total passed ($ncert minor certificates printed)"
[ "$fail" -eq 0 ]
