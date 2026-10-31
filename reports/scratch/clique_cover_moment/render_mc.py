"""Render mc_empty_pairs.log as a markdown table: per (cell, generator) the ratio P(empty)/prod q at each t with its 95% CI."""
import re, collections
rows = collections.OrderedDict()
pat = re.compile(r"\((\d+),(\d+),(\d+)\) (\S+)\s+t=\s*(\d+) p_emp=(\S+) prod_q=(\S+) ratio=(\S+) \[(\S+), (\S+)\] low/high-ones (\S+)/(\S+) hits=(\d+)")
for line in open("mc_empty_pairs.log"):
    m = pat.match(line)
    if not m: continue
    n, mm, d, g, t, pe, q, r, lo, hi, rl, rh, hits = m.groups()
    rows.setdefault((int(n), int(d), g), []).append((int(t), float(r), float(lo), float(hi), int(hits), float(pe)))
names = {"bern_padC1_padP2_conn": "best fit (Bernoulli, pad C≥1, pad P≥2, connected)", "paper_bern_conn": "paper as written (Bernoulli, connected)",
         "i_fixed_padC2": "(i) fixed d, customers padded to ≥2", "ii_bern_padC2": "(ii) Bernoulli, customers padded to ≥2", "uniform:bern_padC1_padP2_conn": "control: best-fit sizes, uniform sets"}
print("| cell | generator | ratio P(empty) / E[∏q] at t = 2, 3, 4, … (95% CI half-width; hits) |")
print("|---|---|---|")
for (n, d, g), L in sorted(rows.items(), key=lambda kv: (kv[0][0], kv[0][1], list(names).index(kv[0][2]))):
    cells = []
    for t, r, lo, hi, hits, pe in sorted(L):
        if hits < 20: cells.append(f"t={t}: ({hits} hits)"); continue
        cells.append(f"t={t}: **{r:.3f}** ±{(hi-lo)/2:.3f}")
    print(f"| ({n},{n},{d}) | {names.get(g, g)} | " + "; ".join(cells) + " |")
