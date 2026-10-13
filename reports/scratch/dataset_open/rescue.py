# Injected into the running run_quick.py (PID 2808586) by rescue.gdb, 2026-10-13.
# Finds the finished-but-unwritten results (done futures still held by the
# executor's ordered map) and writes them to rescued_quick.jsonl. Reads only.
import gc, json
from concurrent.futures import Future
_rows = []
for _f in gc.get_objects():
    try:
        if isinstance(_f, Future) and _f.done() and not _f.cancelled() and _f.exception() is None:
            _r = _f.result()
            if isinstance(_r, dict) and "status" in _r and "id" in _r:
                _rows.append(_r)
    except Exception:
        pass
with open("/home/al/dev/MOSP/reports/scratch/dataset_open/rescued_quick.jsonl", "w") as _out:
    for _r in _rows:
        _out.write(json.dumps(_r) + "\n")
del _rows, _f, _out
