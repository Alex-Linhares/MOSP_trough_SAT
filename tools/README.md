# tools/

Third-party binaries built from source for this repository. Nothing here is
imported by Python; the modules that need a tool look for its binary by path.

## drat-trim

Marijn Heule's DRAT proof checker, used by `learning/proofs.py` (loop0003
item 03, `reports/ml_nature.md` §17) to check the refutation proofs CaDiCaL
emits through pysat.

- Source: https://github.com/marijnheule/drat-trim, commit
  `2e3b2dc0ecf938addbd779d42877b6ed69d9a985` (2024-11-25), cloned 2026-09-26.
  The `.git` directory was removed; the sources are vendored as they were.
- Build (the upstream Makefile's `-std=c99` fails on glibc 2.39+ because
  `getc_unlocked` is POSIX, not C99; `gnu99` exposes it):

      cd tools/drat-trim && gcc drat-trim.c -std=gnu99 -O2 -o drat-trim

- The binary `tools/drat-trim/drat-trim` is git-ignored; `learning.proofs`
  refuses to run without it and prints the build line.
- Self-test: `./drat-trim examples/example-4-vars.cnf examples/example-4-vars.drat`
  ends in `s VERIFIED`.
- The upstream `examples/R_4_4_18.*` files (7 MB of proofs) were dropped from the vendored copy.
