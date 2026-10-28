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

## p17 (PACE 2017 exact treewidth, Larisch & Salfelder)

The exact-track winner of PACE 2017, used for the treewidth of random graphs
that `learning/treewidth.py` cannot settle (`reports/random_graph_pathwidth_survey.md`
§7(d); driver `reports/scratch/gnp_pilot/p17_censored.py`). Reads a PACE `.gr`
on stdin, prints a `.td` whose `s td <bags> <bagsize> <n>` line gives
treewidth = bagsize − 1.

- Source: https://github.com/freetdi/p17, commit
  `552341da2ae36cb2e64ef9e39add2fab27c6d879` (2017-05-25), cloned 2026-10-28;
  `.git`, the Python bindings (`tdlib/pytdlib`) and the autotools tests dropped.
  Needs the header-only STX B+ tree: https://github.com/bingmann/stx-btree,
  commit `eff5e36975b62327755b2e05fd19c882ea6b4b0c` (2019-03-25), vendored as
  `tools/stx-btree/include` with its licence.
- Build: `sh tools/p17/build.sh` (no autotools; `inc/config.h` is a hand-written
  stand-in for configure's, and `inc/tdlib` maps the `tdlib/` include prefix
  onto `tdlib/src`). The upstream submission is the wrapper `tw-exact`, which
  runs `build/grtd/grtd -m 64`; here that is `grtd.bin -m 64`. `tw-exact.bin`
  is the older Tamaki port, kept for comparison: much weaker on dense graphs.
- The binaries are git-ignored. The build script ends with a self-test on the
  bundled Hoffman graph (treewidth 6).
- Trust: a `.td` is checked by `reports/scratch/gnp_pilot/check_td.py` (a valid
  decomposition is a proof of the upper bound); the lower half is grtd's
  iterative deepening over the bag size, cross-checked on 120 pilot graphs with
  an independently proved treewidth, 120 agreements, 0 disagreements.
