"""Item 03 (c): the candidates against the exact values, and the kill criterion.

Reads ct_values.csv (the item's grid, <= 400 vertices), ct_ext_values.csv (the extension beyond it, if
present), caterpillar_values.csv, random_block_trees.csv and record_forests.csv; prints markdown tables:

  1. CT(s, h, b): the exact pathwidth, one table per b (rows s, columns h), with the status;
  2. the kill criterion: every alpha (omega - 1) + beta h + gamma with alpha, beta in 0..4 and gamma in
     -6..6, on the item's grid, exact or not; the best such fit; the same per b;
  3. the conjectured exact form C(s, h, b) = ceil((h + 2)(s - 2) / 2) + pw(CT(2, h, b)), checked on
     every clique tree solved (grid and extension), with pw(CT(2, h, b)) read from the s = 2 row;
  4. per candidate and per family: violations (candidate below the exact pathwidth), exact share, mean
     slack, max slack -- the candidate as a would-be upper bound;
  5. the caterpillar of cliques: exact against the additive and the multiplicative forms.

    cd /home/al/dev/MOSP && python3 reports/scratch/forest_regime/fit.py > reports/scratch/forest_regime/fit.log
"""
import math, sys
from itertools import product
from pathlib import Path
import pandas as pd
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[2]))
from learning.block_trees import CANDIDATES

pd.set_option("display.width", 200)


def md(frame: pd.DataFrame, floatfmt=".3g") -> str:
    return frame.to_markdown(index=False, floatfmt=floatfmt)


ct = pd.read_csv(HERE / "ct_values.csv")
ct["grid"] = "item"
ext_path = HERE / "ct_ext_values.csv"
if ext_path.exists():
    ext = pd.read_csv(ext_path)
    ext["grid"] = "extension"
    ct = pd.concat([ct, ext], ignore_index=True)
ct = ct.sort_values(["b", "s", "h"]).reset_index(drop=True)
# a censored incidence tree is exact when its upper bound meets the complete-ternary-subtree lower bound
from learning.block_trees import clique_tree, incidence_graph, ternary_subtree_height
ct["ternary_lb_B"] = [ternary_subtree_height(incidence_graph(clique_tree(int(r.s), int(r.h), int(r.b))[0])) for r in ct.itertuples()]
resolved = (ct.status_B == "upper") & (ct.ternary_lb_B == ct.pw_B)
ct.loc[resolved, "status_B"] = "upper = ternary subtree lower bound"
print(f"incidence trees censored: {int((ct.status_B == 'upper').sum())} left after the ternary-subtree bound resolved {int(resolved.sum())}\n")
exact = ct[ct["status"] != "upper"]
print(f"# Clique trees: {len(ct)} solved ({(ct.grid == 'item').sum()} in the item's grid, "
      f"{(ct.grid == 'extension').sum()} in the extension), {(ct.status == 'upper').sum()} censored\n")

# 1. the table per b
for b, g in ct.groupby("b"):
    piv = g.pivot(index="s", columns="h", values="pw")
    cens = g[g.status == "upper"]
    print(f"## CT(s, h, b = {b}): exact pathwidth (rows s, columns h)\n")
    rows = []
    for s in sorted(g.s.unique()):
        row = {"s": s}
        for h in sorted(g.h.unique()):
            sub = g[(g.s == s) & (g.h == h)]
            if len(sub) == 0:
                row[f"h={h}"] = ""
            else:
                r = sub.iloc[0]
                row[f"h={h}"] = f"{r.pw}" + ("" if r.status != "upper" else f" (censored: in [{r.lower}, {r.pw}])") + \
                    (f" [n={r.n}]")
        rows.append(row)
    print(md(pd.DataFrame(rows)) + "\n")
print("## Every clique tree solved\n")
cols = ["grid", "s", "h", "b", "n", "m", "pw", "status", "nodes", "seconds", "pw_B", "status_B", "ternary_lb_B", *CANDIDATES]
print(md(ct[cols]) + "\n")

# 2. the kill criterion
item = ct[(ct.grid == "item") & (ct.status != "upper")]
fits = []
for alpha, beta, gamma in product(range(0, 5), range(0, 5), range(-6, 7)):
    pred = alpha * (item.omega - 1) + beta * item.h + gamma
    misses = int((pred != item.pw).sum())
    fits.append({"alpha": alpha, "beta": beta, "gamma": gamma, "misses": misses, "max |err|": int((pred - item.pw).abs().max())})
fits = pd.DataFrame(fits).sort_values(["misses", "max |err|"]).reset_index(drop=True)
print("## Kill criterion: alpha (omega - 1) + beta h + gamma on the item's grid\n")
print(f"forms tried: {len(fits)}; forms exact on every value: {int((fits.misses == 0).sum())} of {len(fits)}; "
      f"best form misses {fits.iloc[0].misses} of {len(item)} values\n")
print(md(fits.head(8)) + "\n")
print("### The same per b (an alpha, beta, gamma of its own for each b)\n")
rows = []
for b, g in item.groupby("b"):
    best = None
    for alpha, beta, gamma in product(range(0, 5), range(0, 5), range(-6, 7)):
        pred = alpha * (g.omega - 1) + beta * g.h + gamma
        misses = int((pred != g.pw).sum())
        if best is None or misses < best[3]:
            best = (alpha, beta, gamma, misses)
    rows.append({"b": b, "values": len(g), "best alpha": best[0], "best beta": best[1], "best gamma": best[2], "misses": best[3]})
print(md(pd.DataFrame(rows)) + "\n")
print("### Growth in s at fixed (h, b), and in h at fixed (s, b)\n")
rows = []
for (h, b), g in item.groupby(["h", "b"]):
    g = g.sort_values("s")
    rows.append({"h": h, "b": b, "s values": " ".join(map(str, g.s)), "pw": " ".join(map(str, g.pw)),
                 "differences in s": " ".join(str(d) for d in g.pw.diff().dropna().astype(int))})
print(md(pd.DataFrame(rows)) + "\n")
rows = []
for (s, b), g in item.groupby(["s", "b"]):
    g = g.sort_values("h")
    rows.append({"s": s, "b": b, "h values": " ".join(map(str, g.h)), "pw": " ".join(map(str, g.pw)),
                 "differences in h": " ".join(str(d) for d in g.pw.diff().dropna().astype(int))})
print(md(pd.DataFrame(rows)) + "\n")

# 3. monotone lower bounds, then the conjectured forms
# CT(s-1, h, b), CT(s, h-1, b) and CT(s, h, b-1) are induced subgraphs of CT(s, h, b), so their exact
# pathwidths are lower bounds; a censored cell whose best such bound meets its upper bound is exact.
value = {(int(r.s), int(r.h), int(r.b)): int(r.pw) for r in ct.itertuples() if r.status != "upper"}
lower_all = {}
for r in ct.itertuples():
    s_, h_, b_ = int(r.s), int(r.h), int(r.b)
    lb = int(r.lower) if pd.notna(r.lower) else 0
    for key in ((s_ - 1, h_, b_), (s_, h_ - 1, b_), (s_, h_, b_ - 1)):
        if key in value:
            lb = max(lb, value[key])
    lower_all[(s_, h_, b_)] = lb
ct["monotone_lb"] = [lower_all[(int(r.s), int(r.h), int(r.b))] for r in ct.itertuples()]
settled = (ct.status == "upper") & (ct.monotone_lb == ct.pw)
ct.loc[settled, "status"] = "upper = induced-subgraph lower bound"
print(f"## Censored clique trees settled by induced-subgraph monotonicity: {int(settled.sum())}\n")
print(md(ct[settled][["grid", "s", "h", "b", "n", "lower", "monotone_lb", "pw", "status"]]) + "\n")
exact = ct[ct["status"] != "upper"].copy()
tree_pw = {(int(r.h), int(r.b)): int(r.pw) for r in exact[exact.s == 2].itertuples()}


def conj1(s, h, b):
    t = tree_pw.get((h, b))
    return None if t is None else math.ceil((h + 2) * (s - 2) / 2) + t


def conj2(s, h, b):
    return math.ceil((h + 2) * (s - 2) / 2) + 1 + (1 if (b >= 2 and h >= 2) else 0)


exact["C1"] = [conj1(int(r.s), int(r.h), int(r.b)) for r in exact.itertuples()]
exact["C2"] = [conj2(int(r.s), int(r.h), int(r.b)) for r in exact.itertuples()]
exact["tree_lb"] = [tree_pw.get((int(r.h), int(r.b))) for r in exact.itertuples()]
print("## Two closed forms against every exact clique tree (grid and extension)\n")
print("C1(s, h, b) = ceil((h + 2)(s - 2) / 2) + pw(CT(2, h, b)), stated after the grid; "
      "C2(s, h, b) = ceil((h + 2)(s - 2) / 2) + 1 + [b >= 2][h >= 2], stated after the extension.\n")
print(f"pw(CT(2, h, b)) from the s = 2 row: {dict(sorted(tree_pw.items()))}\n")
have = exact[exact.C1.notna()]
print(f"C1: checked on {len(have)} exact values: {int((have.C1 == have.pw).sum())} exact, "
      f"{int((have.C1 != have.pw).sum())} misses; C2: checked on {len(exact)}: {int((exact.C2 == exact.pw).sum())} exact, "
      f"{int((exact.C2 != exact.pw).sum())} misses, of which {int(((exact.C2 != exact.pw) & (exact.s >= 3)).sum())} with s >= 3\n")
print(md(exact[["grid", "s", "h", "b", "n", "pw", "status", "C1", "C2", "tree_lb"]]) + "\n")
cens = ct[ct.status == "upper"].copy()
if len(cens):
    cens["C1"] = [conj1(int(r.s), int(r.h), int(r.b)) for r in cens.itertuples()]
    cens["C2"] = [conj2(int(r.s), int(r.h), int(r.b)) for r in cens.itertuples()]
    print("### Censored clique trees: the interval [monotone lower bound, upper bound] against the forms\n")
    print(md(cens[["grid", "s", "h", "b", "n", "lower", "monotone_lb", "pw", "C1", "C2", "nodes", "seconds"]]) + "\n")

# 4. candidates as would-be upper bounds
cat = pd.read_csv(HERE / "caterpillar_values.csv")
rbt = pd.read_csv(HERE / "random_block_trees.csv") if (HERE / "random_block_trees.csv").exists() else None
rec = pd.read_csv(HERE / "record_forests.csv") if (HERE / "record_forests.csv").exists() else None
# rows whose incidence tree is censored carry an upper bound on pw(B), so their candidates are overestimates: excluded here
usable = (ct.status != "upper") & (ct.status_B != "upper")
print(f"## Candidates: clique-tree rows excluded because pw(B) is censored: {int(((ct.status != 'upper') & (ct.status_B == 'upper')).sum())}\n")
families = [("clique trees (item grid)", ct[(ct.grid == "item") & usable]),
            ("clique trees (extension)", ct[(ct.grid == "extension") & usable]),
            ("caterpillars of cliques", cat[cat.status != "upper"])]
if rbt is not None:
    families.append(("random block trees", rbt[rbt.status != "upper"]))
    for d, g in rbt[rbt.status != "upper"].groupby("d"):
        families.append((f"random block trees d = {d}", g))
if rec is not None:
    families.append(("forests on record (certified optima)", rec))
print("## Candidates as would-be upper bounds: violations (candidate < exact), exact share, slack\n")
rows = []
for name, g in families:
    if len(g) == 0:
        continue
    for c in CANDIDATES:
        diff = g[c] - g["pw"]
        rows.append({"family": name, "count": len(g), "candidate": c, "violations": int((diff < 0).sum()),
                     "worst violation": int(-diff.min()) if (diff < 0).any() else 0,
                     "exact": float((diff == 0).mean()), "mean slack": float(diff.mean()), "max slack": int(diff.max())})
print(md(pd.DataFrame(rows)) + "\n")
if rbt is not None:
    print("## Random block trees: by (d, n)\n")
    g = rbt.groupby(["d", "n"]).agg(count=("pw", "size"), censored=("status", lambda s: int((s == "upper").sum())),
                                    omega_mean=("omega", "mean"), h_mean=("h", "mean"), pwB_mean=("pw_B", "mean"),
                                    pw_mean=("pw", "mean"), pw_min=("pw", "min"), pw_max=("pw", "max"),
                                    nodes_max=("nodes", "max"), seconds_max=("seconds", "max")).reset_index()
    print(md(g) + "\n")
    print("### pw - (omega - 1) against pw(B) and h on the random block trees\n")
    rbt2 = rbt[rbt.status != "upper"].copy()
    rbt2["pw - (omega-1)"] = rbt2.pw - (rbt2.omega - 1)
    print(md(rbt2.groupby("pw_B").agg(count=("pw", "size"), mean_excess=("pw - (omega-1)", "mean"),
                                       max_excess=("pw - (omega-1)", "max"), omega_mean=("omega", "mean")).reset_index()) + "\n")
if rec is not None:
    print("## Forests on record: by n\n")
    g = rec.groupby("n").agg(count=("pw", "size"), omega_mean=("omega", "mean"), h_mean=("h", "mean"),
                             pwB_mean=("pw_B", "mean"), pw_mean=("pw", "mean"), pw_max=("pw", "max")).reset_index()
    print(md(g) + "\n")

# 5. the caterpillar
print("## The caterpillar of cliques: exact against the forms\n")
cat2 = cat.copy()
cat2["ceil(3s/2)-2"] = [math.ceil(3 * s / 2) - 2 for s in cat2.s]
print(md(cat2[["s", "length", "n", "m", "h", "pw", "status", "pw_B", "omega-1+pw(B)", "omega-2+pw(B)", "omega-1+h",
               "omega(pw(B)+1)-1", "omega(tb+1)-1", "ceil(3s/2)-2"]]) + "\n")
