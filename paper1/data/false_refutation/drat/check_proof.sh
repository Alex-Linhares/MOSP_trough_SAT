#!/bin/bash
# Check the DRAT refutation of k = 5 for the 34-customer instance (paper1/data/false_refutation).
# 1. rebuild the CNF exactly from the instance and confirm its SHA-256 against the certificate record;
# 2. decompress the trimmed proof (the lemmas drat-trim kept as the core of the refutation);
# 3. check it with drat-trim (tools/drat-trim). Expect "s VERIFIED".
#     bash paper1/data/false_refutation/drat/check_proof.sh      (from the repository root)
set -euo pipefail
cd "$(dirname "$0")/../../../.."
D=paper1/data/false_refutation/drat
T=$(mktemp -d)
python3 - "$T" <<'PY'
import hashlib, json, sys
from learning.proofs import rebuild_cnf
from paper1.false_refutation_figure import load, instance
d, masks, n, edges = load()
cert = json.load(open("paper1/data/false_refutation/drat/false_refutation_34__k5.json"))
cnf = rebuild_cnf(cert, instance(n, edges))
assert hashlib.sha256(cnf).hexdigest() == cert["cnf_sha256"], "rebuilt CNF does not match the record"
open(sys.argv[1] + "/f.cnf", "wb").write(cnf)
print("CNF rebuilt, SHA-256 matches the certificate record")
PY
(cd $D && sha256sum -c false_refutation_34__k5.core.drat.xz.sha256)
xz -dc $D/false_refutation_34__k5.core.drat.xz > $T/core.drat
tools/drat-trim/drat-trim $T/f.cnf $T/core.drat | grep -E "VERIFIED|verification time"
rm -rf "$T"
