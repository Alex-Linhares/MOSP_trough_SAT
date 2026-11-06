> **Coordinator's note (2026-11-06, after the numerics audit):** Finding 1 below rests on the
> text extraction, which renders display (D.4) as `Darr = r2a`. The PDF itself (p. 58) typesets
> `D_arr = r^{2a}`, the reading under which this report's own "repair" closes every inequality.
> Finding 1 is therefore **withdrawn as an error**; the analysis of what `r^{2a}` must satisfy stands.

# Audit of Theorem D.1 (Boolean tensor contraction), Section D.4

Manuscript: "The Exponential Time Hypothesis is False" (OpenAI, 17 Oct 2026, rev. 25 Oct 2026).
Scope: Section D.4, `paper_flow.txt` lines 4599–5151 (PDF pp. 57–64). Reference: hostile, independent;
every displayed inequality that is concrete was recomputed, and the two structural identities
(Lemma D.5's recovery, the recursion identity (D.16)) were executed end to end on small instances.
Scripts: `check_lemma_D4.py`, `check_lemma_D5.py`, `check_D12.py`, `check_D16.py` (+ `debug_D16.py`),
`check_packing.py`, `check_modes.py`, `check_params.py`, `check_recurrence.py`, all run with `python3 -I`.

## Verdict

Section D.4 proves Theorem D.1 as stated, up to one bookkeeping error that is repairable without
changing any other parameter. The error (Finding 1) is in D.4.2/Lemma D.3: the number of ordered
pair labels is written `D_arr = r·2^a`, but with vertex labels in `[r]^a` it is `r^{2a}`, and the
displayed variance inequality in Lemma D.3's proof is false as written (numerically it fails for every
`M ≥ 5` at `a = 1`, every `M ≥ 1` at `a ≥ 2`). With `D_arr := r^{2a}` the proof of Lemma D.3 goes
through verbatim and every consequence used later ((D.5), (D.6), "3M/L packets", "3M/r ports per
symbol", "6M/r child edges") still holds, because `ε` was chosen so small that `r^{2a} ≤ s^{48ε}`
with `48ε = 3/8192 < 1/1000`. The heart of the argument — Lemma D.5 — is correct: (D.10) is an exact
identity, the taper gives `v2(E_t(0)) ≥ −6D_t h`, the recovery of `F(0) mod 2^p` from the jets modulo
`2^{p_t}` is *exact*, so no precision is lost that could compound over the recursion; only the
*required* precision grows, and (D.11) bounds it correctly. The recursion identity (D.16) is an exact
identity, verified on 192 random configurations. The running-time recurrence yields
`(s+L)^{O(1)} exp(O(s/√λ))` with the polynomial factor additive per call, not compounded with depth; the
space argument is sound because children are enumerated with polynomial delay and consumed one at a
time. Nothing in D.4 contradicts the Lean-checked part; the sharper bounds rest on D.4 and D.4 holds.

## Findings (most serious first)

### 1. ERROR (repairable): `D_arr = r·2^a` is not the number of pair labels; Lemma D.3's displayed inequality is false as written
Location: (D.4), line 4644 (p. 58); Lemma D.3 proof, lines 4676–4692 (pp. 58–59).
Quote: "label the vertices on each side of the network by elements of `[r]^a`" … "For each pair of
labels let `X_γ` be the number of edges with that pair. Independent uniform vertex labels give
`E Σ_γ (X_γ − M/D_arr)^2 ≤ 2MΔ`. … Pairs with disjoint endpoints contribute zero."
What it needs: the number of ordered (row label, column label) pairs must equal `D_arr`, so that a
pair of edges with disjoint endpoints contributes `P(agree) − 1/D_arr = r^{−2a} − 1/D_arr = 0`.
What fails: with labels in `[r]^a` on each side the count is `N = r^{2a}`, not `r·2^a` (these agree
for no `a ≥ 1`). Exact closed form for a matching (`Δ = 1`):
`E Σ_γ (X_γ − M/D)^2 = M − M/N + M^2 (N − D)^2/(N D^2)`; with `D = N` this is `< M ≤ 2MΔ`, with the
paper's `D = r·2^a` and `r = 64` it is `M − M/N + 0.2346 M^2` at `a = 1` (exceeds `2M` for `M ≥ 5`),
`+256 M^2` at `a = 2`, `+262144 M^2` at `a = 3` (`check_packing.py`). Since the proof needs `M > H ≫ Δ`,
the display is false in the regime where it is applied. Consequences if read literally: the load bound
`M/D_arr + √(2MΔ)` is still an (over)estimate of each load, but the packet count would become
`H_pad·N/L`, not `≤ 3M/L`, so properties (1) and (3) of Lemma D.3 would not follow.
Repair: set `D_arr = r^{2a}`. Then `H_pad ≤ M/N + √(2MΔ) + L ≤ 3M/N` needs `M ≥ 2N^2 Δ` and `M ≥ LN`,
i.e. (D.6) with the corrected `D_arr`; `log_s(2N^2Δ) ≤ 0.9 + 96ε + o(1) = 0.90073…`, `log_s(LN) ≤ 13·4ε`,
both `< 1 − o(1) = log_s H`. (D.5)'s `D_arr ≤ s^{1/1000}` becomes `r^{2a} ≤ s^{48ε}·2^{48ε}`, `48ε ≈ 0.00037`,
still true (`check_params.py`). All later uses (3M/L packets, 3M/r ports per symbol per side, hence
6M/r = 3M/32 < M/8 child edges) are unchanged. Severity: an error in a displayed parameter and a false
displayed inequality, but the proof is restored by a one-token change with no other effect.

### 2. GAP (minor, filled by the audit): the inductive statement of the recursion is never written down
Location: D.4.6 line 5050 ("Thus the invariants used in (D.5) hold inductively"), D.4.7 lines
5077–5078 ("Lemma D.4, the recursion identity, and the recovery lemma prove correctness by induction
from the leaves"), pp. 63–64.
What it needs: the children are not instances of Theorem D.1. Their entries lie in `A_{p_t} =
(O[V]/(V^ℓ))/(2^{p_t})`, not in `B_{P0,ℓ}`; `p_t` grows to `sλ^{O(1)}2^{a_{d−1}} = s^{1+4ε+o(1)}`; the new
packet tensors have entry cost `exp(O(L log s))` rather than `(s+L)^b 2^{As^{9/10}}`; and the bipartition
is re-drawn (group-`g` vertices from *both* sides go on one side, packets on the other). The theorem's
hypotheses are therefore not what the recursion preserves; what it preserves is the invariant list
behind (D.5): `M_{d+1} ≤ 3M_d/32 < M_d/8` (from Lemma D.3(3), both sides), maximum degree `≤ Δ` (old
vertices unchanged; packet vertex `≤ 2L ≤ Δ`), vertex count `≤ poly(s) + d·3Cs`, bipartite, entry time
`≤ 2^{O(s^{9/10})}`, precision `p ≤ sλ^{O(1)}2^{a_{d−1}}`. I checked each; they hold. The proof would be
complete with one sentence stating "a call `(network, p, d)` satisfying these invariants returns its
contraction modulo `2^p`". Severity: presentational; no mathematical hole found.

### 3. AMBIGUITY: `L` is overloaded (description length vs packet size `2^a`)
Location: Theorem D.1 (line 4296) and D.4.7 lines 5094–5096 use `L` for the description length;
(D.4) line 4645 onward uses `L = 2^a`. Lemma D.3 ("polynomial time and space in `s + L`", line 4675),
Lemma D.5 ("polynomial … in `M, L, ℓ, e`", line 4839) and D.4.7 ("Since the branching bound is
independent of `L`", line 5095) can be read either way. The proof needs: packet size in Lemmas D.3/D.5,
description length in D.4.7. Both readings make the statements true, so this is harmless, but the
"(s+L)^{O(1)}" factor in the theorem is the description-length `L` and must not be confused with
`2^a ≤ s^{1/1000}`.

### 4. AMBIGUITY/REMARK: "sufficiently large `s`" is astronomically large
Location: D.4.2 line 4639 ("All estimates below hold for sufficiently large s … A fixed finite range
of smaller sizes is handled by direct summation"), (D.5) line 4661.
With `ε = 1/131072`: `u_0 = ⌊ελ⌋ ≥ 1` needs `λ ≥ 131072`, i.e. `s ≥ 2^{131072}`; the stated `u ≥ λ^{4/5}`
needs `λ ≥ (1/ε)^5 = 3.9·10^{25}`, i.e. `s ≥ 2^{3.9·10^{25}}` (`check_params.py`). (What the proof actually
uses from `u ≥ λ^{4/5}` is `2^u ≫ λ^{O(1)}u`, which holds from `λ ≈ 2^{24}` on, `s ≥ 2^{2^{24}}`.) The
theorem is an asymptotic `O`-statement and the direct-summation constant is legally absorbed in
`(s+L)^{O(1)}`, so this is not an error; but the proof establishes nothing about any input of
imaginable size, and the hidden constants (branching `exp(≳ 10^4·C·s/√λ)` at the root, cf. the
exponent arithmetic below) should be stated if the result is to be read as an algorithm.

### 5. Checked and correct (no finding), with the numbers
- Lemma D.4 (integrality of `W(t+αz)`): true for all `x, y ∈ [0, L)`, `t ∈ S`, `a ≤ 4` (`check_lemma_D4.py`);
  `W(0) = I` verified.
- Lemma D.5: on 27 random cases (`a ≤ 4`, `u ≤ a`, `M ≤ 6`, both random integer `F` and `F` built from
  products of `W` entries as in (D.8)) with each jet coefficient perturbed by a random multiple of
  `2^{p_t}`: `F(0) mod 2^p` recovered exactly every time; identity (D.10) exact for every node; actual
  worst loss `−min_j v2(E_t(0)(−t/α)^j)` at most 0.58 of the budget `6D_t h + 4M(a+1)` (`check_lemma_D5.py`).
  The "mode of weight `j` has coefficient divisible by `2^j`" claim is (D.12)'s
  `v2(base) + b·v2(ratio) ≥ (a+1−i) + b ≥ b+1`; verified, and **tight** (`min(v2(coef) − w) = 0`).
- (D.12) truncation: for all crossing pairs, `a ≤ 4`, four values of `ζ`, `P = 12`: the truncated series
  equals `W_{xy}(T)` modulo `2^P` (`check_D12.py`); `v2(t − y_0 + x) ≤ i` holds in every case.
- (D.15): exact tuple counts versus the bound `exp((1+π^2)√(MP/D))` from the generating-function
  argument: bound holds with large margin on five parameter sets (`check_modes.py`); the sum
  `Σ_j −ln(1−e^{−θj}) ≤ π^2/(6θ)` is right.
- (D.16): on tiny packet-form networks (`r = 2`, `a = 2`, `L = 4`, `α = 8`, `u = 2`, `M = 6`, two packets),
  `F(t+αζ)` computed from (D.8) by brute force agrees modulo `2^P` with `Σ_β Π_g Z_{g,β}` with the
  children built literally as in D.4.6 (coefficient extraction at the target, `L_Z^{β_Z}` at the source,
  equal-symbol packets fully local), for all nodes of valuation `0` and `1`, `ζ ∈ {0, ±1, 2}`,
  `P ∈ {3, 4}`, six seeds: 192 of 192 (`check_D16.py`). One point the text states correctly and an
  implementer can get wrong: a child's wires are *ports*, so an original edge's row bit `Y_e` and column
  bit `X_e` are two different child wires, generally in different children.
- (D.11): the increment `8hD_t + 8M(a+1)` with `h ≤ 4M/u`, `D_t ≤ 2^{a_d}` summed over `O(log λ)` depths
  gives `p ≤ sλ^{O(1)}2^{a_{d−1}}`; with `D_t ≥ 2^{a_{d−1}+u+1}` for `i < u` and `M > s/√λ`,
  `p/(MD_t/u) ≤ λ^{O(1)}u/2^{u}` → 0. Correct.
- (D.5)/(D.6): `a_d < 4ελ`, `L ≤ s^{4ε}`, `d_max ≤ log_2(λ)/6 + O(1)` from `Cs8^{−d} > s/√λ`; correct.
- Hermite setup: `Σ_{t≠0} q_t ≥ Lhu ≥ 3ML > M(2L−1) = deg F`; `q_t ≤ 4M` needs `M ≥ u` (hypothesis). Correct.
- Lemma D.3's property (3) and the child edge count `≤ 3M/r` per side: follow with `D_arr = r^{2a}`.

## The exponent arithmetic

Per active call at depth `d`: children `N_d ≤ (#t)·(#ζ)·(#β)·r ≤ 2L · s^4 · exp(c_2 √(M p_t/D_t)) · 64
= s^{c_1} exp(c_2' M_d/√u_d)`, using `p_t ≤ c_3 M D_t/u` from (D.11). With `M_d ≤ Cs8^{−d}` and
`u_d ≥ ελ/2^{d+1}`:
`M_d/√u_d ≤ C√(2/ε) · (s/√λ) · (√2/8)^d`, and `Σ_d (√2/8)^d = 1.2147`, so
`Σ_d M_d/√u_d ≤ 622·C·s/√λ` (`check_recurrence.py`).
Calls: `#calls ≤ Σ_{d ≤ d_max} Π_{d'<d} N_{d'} ≤ (d_max+1) s^{c_1 d_max} exp(c_2' Σ_d M_d/√u_d)
= exp(O(s/√λ) + O(log s · log λ))`, matching the paper's `exp(O_C(s/√λ) + O_C(λ log λ))`.
Time recurrence: `T(d) ≤ poly(s+L)·N_d + N_d·T(d+1)` (local work — packing, Lagrange interpolation at
`< s^4` points, Lemma D.5's rational combination, child descriptions — is polynomial per call and is
*added*, not multiplied, per level). Unrolled:
`T(0) ≤ poly(s+L)·Σ_d Π_{d'<d} N_{d'} + Π_d N_d · T_leaf`, `T_leaf ≤ 2^H · poly(s) · max{(s+L)^b 2^{As^{9/10}}, e^{O(L log s)}}`
with `H = ⌊s/⌊√λ⌋⌋`, `s^{9/10} = o(s/√λ)`, `L log s = O(s^{1/1000} log s)`. Hence
`T(0) = (s+L)^{O(1)} exp(O(s/√λ)) = (s+L)^{O(1)} 2^{O(s/√log s)}`. The polynomial factor over a path,
`s^{O(d_max)} = 2^{O(λ log λ)}`, is `2^{26}`–`2^{40}` bits for `log_2 s = 10^6`–`10^{10}` against `2^{10^6}`–`2^{10^{10}}`
bits in the main term: negligible. The naive recurrence `T(d) ≤ poly·N_d·T(d+1)` would give
`poly^{d_max} = (s+L)^{O(log λ)}`, which is *not* `(s+L)^{O(1)}` for superpolynomial `L`; the paper's
sentence "the branching bound is independent of `L`" (line 5095) is exactly the observation that the
correct recurrence is the additive one, and it is right.
Space: a call stores `F(t+αζ_j) mod 2^{p_t}` for `≤ 2L` nodes and `< s^4` values, each `eℓp_t` bits;
`β` is a vector over `≤ (3M/L)2^{u}p_t` modes with entries `< p_t`; children for one `(t, ζ, β)` are run
sequentially for `g = 1..r` keeping one product, and `β` is enumerated with polynomial delay keeping one
running sum; stack depth `O(log λ)`. Polynomial. The claim "reusing space" is justified because nothing
from a finished child is retained except its single ring element.

## What this audit does not establish

- It does not check Sections D.2–D.3 (the encodings) beyond noting they supply `P_0, ℓ ≤ Cs`,
  degree `≤ ⌈s^{9/10}⌉` and entry time `2^{λ^{O(1)}}`; whether `Lemma D.2`'s wire count (D.3) is right is
  outside this angle.
- Numerical checks are at `a ≤ 4`, `r = 2`, `M ≤ 6`, `e = 1` (so `O = Z_{(2)}`, `ℓ = 1`). The extension
  to `O = Z_{(2)}[U]/(f)` rests on the paper's `v2` being coordinatewise and multiplicative, which I
  verified by reading, not by computation; the `V`-truncation plays no role in any inequality.
- The derandomised packing (conditional expectations) was not executed; its polynomiality and the
  load bound were checked by reading, the variance identity by closed form.
- I did not attempt to find the true threshold `s_0` of "sufficiently large" for every inequality in
  (D.5)/(D.6); only the two governing ones (`u ≥ 1`, `2^u ≫ λ^{O(1)}`).
- "Exact" above means modulo `2^p` at each call as the paper claims; I did not implement the full
  recursion (Lagrange interpolation over `A_{p_t}` plus Lemma D.5 plus (D.16)) as one program, only
  each link separately on instances satisfying that link's hypotheses.
