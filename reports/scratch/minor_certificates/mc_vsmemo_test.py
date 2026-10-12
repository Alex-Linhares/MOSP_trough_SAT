"""Self-test of vsmemo against the brute-force DP of mc_sat.vs_brute, and an
edge-list converter: python mc_vsmemo_test.py [CLAIM ...] writes CLAIM_edges.txt."""
import json, random, subprocess, sys, tempfile, os
from mc_sat import vs_brute
HERE = os.path.dirname(os.path.abspath(__file__))

def write_txt(n, E, path):
    with open(path, "w") as f:
        f.write(f"{n} {len(E)}\n" + "".join(f"{a} {b}\n" for a, b in E))

if len(sys.argv) > 1:
    for c in sys.argv[1:]:
        E = json.load(open(f"{HERE}/{c}_edges.json")); n = 1 + max(max(e) for e in E)
        write_txt(n, E, f"{HERE}/{c}_edges.txt"); print("wrote", c)
    sys.exit()
rng = random.Random(7)
for t in range(1500):
    n = rng.randint(1, 13); p = rng.choice([0.15, 0.3, 0.5, 0.8])
    E = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p]
    adj = {v: set() for v in range(n)}
    for a, b in E: adj[a].add(b); adj[b].add(a)
    pw = vs_brute(n, adj)
    with tempfile.NamedTemporaryFile("w", delete=False) as fh: path = fh.name
    write_txt(n, E, path)
    for flag in ([], ["-f"], ["-o"], ["-o", "-f"]):
        for w in range(max(0, pw - 2), pw + 1):
            r = subprocess.run([f"{HERE}/vsmemo", path, str(w)] + flag, capture_output=True, text=True)
            assert r.returncode == (10 if w >= pw else 20), (n, E, w, pw, flag, r.stdout)
    os.unlink(path)
print("vsmemo agrees with brute force on 1500 random graphs (n <= 13), plain, -f, -o and -o -f")
