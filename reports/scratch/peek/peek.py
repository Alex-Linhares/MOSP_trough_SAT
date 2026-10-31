# Read-only peek, injected by peek.gdb (2026-10-14): writes each thread's Python stack with the
# small locals that say where the search is (minor size, rule, k, n, budgets) to peek_<pid>.json.
def _peek():
    import sys, os, json
    keys = {"n", "k", "w", "size", "rule", "budget", "lower", "upper", "target", "m", "nodes",
            "max_nodes", "cap", "refuted", "best", "at", "sizes", "deadline", "self"}
    out = []
    for tid, fr in sys._current_frames().items():
        stack, f = [], fr
        while f is not None:
            loc = {}
            for k, v in f.f_locals.items():
                if k in keys:
                    loc[k] = v if isinstance(v, (int, float, str, bool, type(None))) else (
                        v[:12] if isinstance(v, list) and len(v) < 50 and all(isinstance(x, int) for x in v) else type(v).__name__)
            stack.append([f.f_code.co_filename.rsplit("/", 1)[-1], f.f_code.co_name, f.f_lineno, loc])
            f = f.f_back
        out.append({"thread": tid, "stack": stack})
    with open(f"/home/al/dev/MOSP/reports/scratch/peek/peek_{os.getpid()}.json", "w") as fh:
        json.dump(out, fh, indent=1, default=str)
_peek()
del _peek
