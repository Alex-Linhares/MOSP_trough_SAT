# Refuter report: Theorem 7.1, its two proofs, Algorithm 7.2 (2026-11-05)

Scope read: `reports/subexp_pathwidth.md` lines 2564-2700 (the §7.0 conventions paragraph and §7.1 only). Brute force written from scratch (`refuter_check.py`, `refuter_alg72.py`, `refuter_uncapped.py`, `refuter_n7.py` in this directory; nothing imported from `learning/` or `paper1/` until the final code comparison). All runs under `nice -n 19`.

## Coverage

- All 209 graphs on ≤ 6 vertices (`networkx.graph_atlas_g`, including the null graph); `cw(G)` and `vs(L(G))` exact by subset DP over prefix sets (the value of a layout depends only on its prefix sets, so this is the minimum over permutations). 19 of the 209 have a single-edge component; 85 are subcubic without one; 4 are stars `K_{1,Δ}`, `Δ = 2..5`.
- Bonus: 1,025 of the 1,044 graphs on 7 vertices (all with `m ≤ 16`; 19 skipped), the four inequalities only.
- Proof (i) map, with the rule exactly as stated and under **both** labellings of `e_q = uw` (`u` = either endpoint): every L-layout for `m ≤ 7` (164,425 layouts × 2 labellings), and for `m ≥ 8` every optimal L-layout up to a cap of 20,000 per graph plus 300 random layouts per graph (1,237,872 layouts × 2 labellings); 2,804,594 map checks in all. The cap was hit on 54 of the `m ≥ 8` graphs, so for those "every optimal layout" is not yet exhaustive; an uncapped run (`refuter_uncapped.py`, cap 3,000,000) is **not finished** at the time of writing.
- Proof (ii) map from **every** vertex layout (not only optimal ones): 115,820 layouts, 21,428 of them optimal for cutwidth.
- Algorithm 7.2 end to end (set aside, `L`, DP witness, map, append) with my own DP as the vs oracle on all 104 graphs with `Δ ≤ 3` to 6 vertices: value equals exact `cw` and the witness attains it on 104 of 104.

## Findings

1. **No violation found of (i), (ii), the general `cw ≤ max(1, vs(L))`, or the equality at `Δ ≤ 3` without a single-edge component**, on all 209 graphs to 6 vertices and the 1,025 7-vertex graphs with `m ≤ 16`. The star values `cw(K_{1,Δ}) = ⌈Δ/2⌉`, `vs(L) = Δ − 1` check for `Δ = 2..5`; the stated excess `⌊Δ/2⌋ − 1` is attained at `Δ = 4, 5` and is 0 (trivially attained) at `Δ = 2, 3`.

2. **Proof (i) holds per layout, not only at the optimum**: on every L-layout tested (optimal or not), the mapped vertex order has cutwidth ≤ the layout's vertex separation, for both labellings of `uw`, on every graph without a single-edge component. The rule is labelling-dependent in *which* endpoint goes first (if `u` is renamed `w` the choice can flip) but both choices satisfy the cut bound, as the proof's symmetric sentence says. Editorial: the proof could say in one clause that the rule is applied with either naming of the endpoints.

3. **Sentence-by-sentence check of proof (i)**: no gap found. Claim A (an edge `xz`, `x ∈ P_q`, `z ∉ P_q`, is placed and `z`'s last edge is unplaced and distinct from it) is correct; Claim B is correct; the identity `|∂(P ∪ {u})| = |∂P| − a_u + 1 + b_u` is correct (`deg u = a_u + 1 + b_u`); the extra `b_u + b_w` edges counted at L-cut `q − 1` are placed (position `< q`), have an unplaced neighbour (`ℓ(y) > q`), avoid `P` (so are disjoint from Claim A's edges) and are pairwise distinct (`uy = wy'` would force `y = w`); the arithmetic `vs_L(q−1) + 1 − a_u − b_w ≤ k` iff `a_u + b_w ≥ 1` is right; the "both fail" case is exactly `N(u) = {w}`, `N(w) = {u}`. The boundary case `q = 1` (`P = ∅`, `vs_L(0) = 0`) is covered: then `uw` is the only edge of both and is excluded.

4. **Sentence-by-sentence check of proof (ii)**: no gap found. `c_i − a_i + b_i` is the gap after `v_i`; the L-cuts `(i, j)` are as described (cut `(i, b_i)` coincides with `(i+1, 0)`, harmless); "a placed edge `xy` with `x` before `v_i` has all edges at `x` placed" holds whether or not `x` is the earlier endpoint; the `a_i` edges `x v_i` are counted iff `j < b_i`; the two bounds `c_i + j ≤ k + b_i − 1` and `c_i + j ≤ k + a_i − 1` are right (the second from `c_i − a_i + b_i ≤ k`); `min(a_i, b_i) ≤ ⌊Δ/2⌋` from `a_i + b_i ≤ Δ`; `b_i = 0` has no such cut; `max(0, ·)` is needed only for `Δ ≤ 1` and is right. The order of the `b_i` edges among themselves (by later endpoint) is never used by the proof — editorial, not a gap.

5. **The map of (i) is not valid on graphs *with* a single-edge component, and the text says nothing false about that but does not say it either.** Concrete: `G` = path `0—1—2` plus edge `3—4`, L-layout `(0,1), (3,4), (1,2)` has `vs = 1`; the completion order is `0, 4, 3, 1, 2` (or `0, 3, 4, 1, 2`) with cutwidth 2, so the mapped order is *not* within `max(1, vs(L(G)))`. 1,924 such (graph, layout, labelling) triples among the 19 graphs with a single-edge component. The theorem's "in general `cw(G) ≤ max(1, vs(L(G)))`" is still true (by components) and Algorithm 7.2 sets the single edges aside before mapping, so nothing claimed is wrong; editorial suggestion: say that the *map* requires the exclusion, not only the inequality.

6. **Algorithm 7.2 correctness argument**: correct as written. Step (1) guarantees `G'` has no single-edge component, so (i) gives the mapped order cutwidth ≤ `vs(L(G'))` and (ii) at `Δ ≤ 3` gives `vs(L(G')) ≤ cw(G')`; the appended single edges contribute a cut of 1 each and nothing else; the output is `max` over components. Verified on all 104 subcubic graphs to 6 vertices, both with my own pipeline and with the repo's `cutwidth_subcubic` (0 wrong values, every witness attains the value). Editorial: `O(m²)` for the maps is a safe over-statement (they are `O(m log m)`).

7. **First-draft remark** (path `0—4—3—2`, L-layout `(3,4), (2,3), (0,4)`): checked by hand — `vs(L) = 1`, the degree-tie order `3, 2, 4, 0` has cutwidth 2, and the stated rule gives `2, 3, 4, 0` with cutwidth 1. Correct.

8. **Base table arithmetic**: `log 2 / log 1.89 = 1.08887`; `1.89^{1.2} = 2.147`, `1.89^{1.25} = 2.216`, `1.89^{1.5} = 2.598`, `1.89^3 = 6.751`; `m < 1.0888 n ⟺` cyclomatic number `< 0.0888 n + 1` for connected graphs. All correct.

9. **Not checked (outside the lines I was told to read)**: the remark that `L(G)` is `G°` with the matching edges contracted (§3.4.3), and the attribution of the undirected special case to Kitsunai et al. 2016 §1 and of a witness to their DP's feasible-set bookkeeping.

## Code (`learning/subexp_algorithms.py`, read only after the above)

- `vertex_layout_from_line_layout`: implements the proof's rule exactly, with `u` the lower-indexed endpoint (stable sort by `lastpos` then index), `P` = vertices completed strictly earlier, "u first iff `adj[u] & P` or `adj[w] & ~(P ∪ {u, w})`", isolated vertices last. Compared with my implementation (labelling `u` = lower index) on all 164,425 L-layouts for `m ≤ 7`: **0 mismatches**.
- `line_layout_from_vertex_layout`: sorts edges by (earlier position, later position, edge index) — the proof's order. **0 mismatches** against mine on all 115,820 vertex layouts.
- `cutwidth_subcubic`: sets aside `K_2` components and isolated vertices, maps `L(G')`, returns `max(vs, 1 if K_2)`, appends each single edge consecutively — Algorithm 7.2 as stated. Exact on all 104 subcubic graphs to 6 vertices. Docstring nit: "for `Δ ≥ 4` the returned value is `vs(L(G))`" is off by the `max(·, 1)` when `G'` is empty and a single edge exists (then `vs(L(G)) = 0`, returned 1); the "upper bound within `⌊Δ/2⌋ − 1`" claim is right either way.
- `vs_layout`: the prefix-set DP with argmin pointers; the witness it returns was checked to attain the DP value on every graph above.

verdict: no wrong statement found
