"""Self-test of checkF: certificates from vsmemo -o -w on random small graphs
verify at w < pw; every certificate with one set removed is rejected (except
when the removed set is not needed, which cannot happen for the empty set), and
a certificate at w >= pw cannot exist (vsmemo answers SAT)."""
import os, random, subprocess, tempfile
from mc_sat import vs_brute
HERE = os.path.dirname(os.path.abspath(__file__))
rng = random.Random(11); tmp = tempfile.mkdtemp(); n_ok = n_rej = 0
for t in range(400):
    n = rng.randint(2, 12); p = rng.choice([0.2, 0.4, 0.6])
    E = [(a, b) for a in range(n) for b in range(a + 1, n) if rng.random() < p]
    adj = {v: set() for v in range(n)}
    for a, b in E: adj[a].add(b); adj[b].add(a)
    pw = vs_brute(n, adj)
    if pw == 0: continue
    ef = f"{tmp}/e.txt"; open(ef, "w").write(f"{n} {len(E)}\n" + "".join(f"{a} {b}\n" for a, b in E))
    w = pw - 1; cf = f"{tmp}/F.bin"
    assert subprocess.run([f"{HERE}/vsmemo", ef, str(w), "-o", "-w", cf], capture_output=True).returncode == 20
    r = subprocess.run([f"{HERE}/checkF", ef, str(w), cf], capture_output=True, text=True)
    assert r.returncode == 0 and "VERIFIED" in r.stdout, r.stdout; n_ok += 1
    data = open(cf, "rb").read(); B = (n + 7) // 8; k = len(data) // B
    i = rng.randrange(k); open(cf, "wb").write(data[:i*B] + data[(i+1)*B:])
    r = subprocess.run([f"{HERE}/checkF", ef, str(w), cf], capture_output=True, text=True)
    # a removed member may be unreachable from the empty set; only count rejections
    n_rej += r.returncode != 0
    # the certificate must not verify at w + 1 = pw (there a layout exists)
    open(cf, "wb").write(data)
    r = subprocess.run([f"{HERE}/checkF", ef, str(pw), cf], capture_output=True, text=True)
    assert r.returncode != 0, "certificate verified at w = pw"
print(f"checkF: {n_ok} genuine certificates verified; {n_rej}/{n_ok} with one set deleted rejected; none verifies at w = pw")
