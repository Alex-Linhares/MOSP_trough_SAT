import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

# The MOSP project, for the identity tests. Override with PATHWIDTH_MOSP_DIR.
# Since 2026-09-30 this package lives inside the MOSP repository, so the
# default is the parent directory; before that it was ~/dev/MOSP.
MOSP_DIR = Path(os.environ.get("PATHWIDTH_MOSP_DIR", ROOT.parent))
if MOSP_DIR.is_dir():
    sys.path.insert(0, str(MOSP_DIR))
