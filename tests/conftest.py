"""Keep the test process single-threaded, so that the tests which fork worker
processes fork from a single-threaded parent.

CPython 3.12 warns at every `os.fork()` from a multi-threaded process that it
"may lead to deadlocks in the child": the child gets one thread and a copy of
every lock, including those some other parent thread held at that instant, and
a copy of each native library's thread pool whose threads do not exist in the
child. Thirteen test files fork workers (`benchmarks.csearch`,
`satisfiability.race`, `benchmarks.ratchet`, `benchmarks.solve_parallel`,
`paper1.search_check`, `learning.sat_story`'s raw fork, ...). Measured on
2026-11-02 with `-W always::DeprecationWarning:multiprocessing.popen_fork`: 170
forks from a multi-threaded parent in one run of `tests/`, every fork the suite
makes. The hazard is intermittent by nature, and it is what hung the loop0012
gate for 13 h and the loop0013 item 01 gate for 40 min (its timeout): a
one-worker forked child asleep on a futex after 5 s of work, the same suite
passing in under 5 min on either side of those runs.

Where the threads come from, measured on this 32-core machine: numpy's OpenBLAS
starts one thread per core when it loads (every test module imports numpy at
collection); LightGBM and scikit-learn add libgomp pools on first use; after
`import numpy, lightgbm` the process has 81 threads. With the three `*_THREADS`
limits it has 2: the background threads of the two jemalloc instances that
pyarrow's libraries carry (`jemalloc_bg_thd`, started when pandas imports
pyarrow), which `JE_ARROW_MALLOC_CONF=background_thread:false` removes. With
all four in place the process has one thread at every fork and the warning
count is 0.

The variables must be in the environment before the libraries load. pytest
loads this file at collection, ahead of every test module, and nothing in
pytest's own start-up imports numpy or pandas (checked). `setdefault`: a
caller who sets a value on purpose keeps it, at their own risk.
"""
import os

for _var in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_var, "1")
os.environ.setdefault("JE_ARROW_MALLOC_CONF", "background_thread:false")
