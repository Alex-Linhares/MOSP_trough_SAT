# Audit of Appendix D, the encodings and the bounds (D.2, D.3, and the use of Theorem D.1)

Manuscript: OpenAI, *The Exponential Time Hypothesis is False*, 17 Oct 2026, rev. 25 Oct 2026.
Text audited: `paper_flow.txt` lines 4273–4598 (pp. 53–57) and every lemma they cite
(Lemmas 5.1, 5.2, 6.1, 6.2, 6.3, equation (6.1), Section 6.4). Theorem D.1 (lines 4291–4304) is
*assumed true exactly as stated*; its proof (D.4) is audited separately. Scripts in this directory,
run with `python3 -I`: `d2_network.py`, `lemma_d2_encoding.py`, `exponents.py`.

## Verdict

Assuming Theorem D.1 as stated, Sections D.2 and D.3 do deliver both sharper bounds of Theorem 1.1,
deterministically and in polynomial space. I found **no ERROR**: every hypothesis of Theorem D.1 is
met by both networks, the two encodings compute exactly `#F` (modulo `2^{n+1}`, which suffices since
`#F ≤ 2^n`), each cited lemma is used in the form it is stated, the exponent arithmetic closes, and the
appendix does not contradict Section 6.4. I verified both encodings computationally against brute
force (the clause network on 300 random k-CNFs; a faithful implementation of Lemma D.2's
incidence-monomial network on 115 random systems, including runs where the truncation bound `K`
of (D.1) actually bites and runs with the high-incidence branching forced). The most serious item is
not a flaw in the logic but a **GAP of presentation** (Finding 1): the "for all sufficiently large n"
provisos hide thresholds around `n ≥ 2^{380}`–`2^{670}` for k = 3 (the degree hypothesis
`n^{3/4} λ^{O(1)} ≤ ⌈(nν)^{9/10}⌉` with the constants Section 6 actually supplies), below which the
algorithm of Theorem 1.1 is exhaustive search; this is legitimate for an asymptotic `O_k` statement
and I checked that exhaustive search fits inside the claimed bound with constant ≈ 3.5, but the
Theorem-1.1 proof on p. 57 never says so, and a reader should know that the "n ≥ 20" statement is
true only with constants of that size.

## Findings (most serious first)

**1. GAP (presentational; trivially fillable). Small `n` in the arbitrary-density proof is not
handled explicitly, and the hidden threshold is astronomical.**
Lines 4575–4578 (p. 57): "A single constant c = c(k) bounds both the ratio of equations to variables
and the exponent of λ in the monomial bound for all sufficiently large n." Line 4536–4538:
"For all sufficiently large n its maximum degree is at most ⌈s^{9/10}⌉". Lemma D.2 (line 4559) and
D.2 (line 4342) say "direct enumeration for bounded exceptional sizes", but the proof of the
arbitrary-density bound of Theorem 1.1 (lines 4562–4589) does not: for `20 ≤ n < n_0(k)` the
hypotheses of Lemma D.2 (monomials `≤ λ^c`) may fail and the proof says nothing. What is needed:
one sentence, "for n below the threshold enumerate the 2^n assignments", plus the observation that
`2^n ≤ 2^{C n log log n/√log n}` for all `20 ≤ n ≤ n_0` with `C = √log n_0 / log log n_0`.
I computed the thresholds (`exponents.py`): with `a ≤ 6n` and scopes `≤ k λ^c`, the variable-group
degree bound `⌈n/J⌉·D*` is below `⌈(nν)^{9/10}⌉` for all `n ≥ 2^{54}` (k=3, c=1), `n ≥ 2^{381}`
(k=3, c=6) and `n ≥ 2^{671}` (k=3, c=10); `c(k) ≥ 6` is forced by the 6n equations, and
`2^k·max(D0, P) ≤ λ^c` with `D0 = 320000 B² μ³` and `B = O_k((√λ log λ)^{k−1})` needs `c` near 10
for k = 3 unless `λ` is itself enormous. So for every `n` below roughly `2^{600}` the algorithm of
Theorem 1.1 is exhaustive search. Exhaustive search needs `C ≥ 2.96` at `n = 2^{400}` and `4.02` at
`n = 2^{1000}` in the exponent `C n log log n/√log n`: finite, so the theorem's `O_k` constants
absorb it and **the statement remains correct**. Severity: GAP in exposition only; the fixed-density
route (D.2) has a tiny threshold (`max{k,3} ≤ ⌈s^{9/10}⌉` holds for `s ≥ 3` when `k ≤ 3`, `s ≥ 21`
when `k = 16`).

**2. Checked, no fault: every hypothesis of Theorem D.1 against the D.2 clause network
(lines 4328–4349, p. 54).**
| Hypothesis (lines 4291–4304) | D.2 network | Status |
|---|---|---|
| bipartite multigraph, distinct ports | every edge subdivided once; old vs new vertices; no parallel edges | proved in text; verified (`d2_network.py`) |
| at most `Cs` edges, `s = n+m` | `≤ km` clause ports; a variable with `d` ports costs `≤ 2d−3` edges; after subdivision `≤ 4km ≤ 4k·s` | text says `O_k(n+m)`; measured 3.7–11.6 `s` for k = 3, 4 |
| max degree `≤ ⌈s^{9/10}⌉` | clause `≤ k`, trivalent equality trees `≤ 3`, subdivision vertices 2: `max{k,3}` *independent of occurrence count* | verified: a variable in all 10^5 clauses still gives max degree 3 |
| vertices `≤ poly(s)` | `≤ m + 2km + 4km` | yes |
| entries in `B_{P0,ℓ}`, `1 ≤ P0, ℓ ≤ Cs` | `Z/2^{n+1}`, `P0 = n+1 ≤ 2s`, `ℓ = 1` (permitted, line 4304) | yes for all `s ≥ 1`, not only "sufficiently large" |
| entry time `(s+L)^b 2^{As^{9/10}}`, space `(s+L)^b` | tables of size `≤ 2^k` | yes |
| contraction = `#F` | consistent edge assignments ↔ assignments of occurring variables; `×2^u` for unused; `#F ≤ 2^n < 2^{n+1}` | verified: 300 random instances (n ≤ 6, m ≤ 7, k ∈ {2,3,4}), 0 mismatches |
The brief's question "does the text handle variables of occurrence `> s^{9/10}`" is answered by the
equality trees (lines 4331–4334): the high-occurrence variable becomes a tree of degree-3 vertices,
so no vertex degree depends on occurrence. The tree bookkeeping (`d−2` internal vertices, unique
extension of a common port value) is correct.

**3. Checked, no fault: Lemma D.2's hypotheses, proof, and its use of Section 5
(lines 4354–4560, pp. 54–57).** Items confirmed by reading and by `lemma_d2_encoding.py`:
- High-incidence branching (line 4364): with `D* = max{1,⌈N0/n⌉}⌈√λ⌉`, fewer than `N0/D* ≤ n/√λ`
  variables exceed `D*` (both cases `N0 ≥ n`, `N0 < n`); the remaining variables lie in
  `≤ D* = λ^{O(1)}` scopes. Correct.
- `B̄_i`, `F`, and the degree bound (D.1), line 4418: coefficient of `V^j` has degree `≤ k(1+2j)`
  because `deg e_j ≤ 1`, `deg h = 2`, `deg L̃_i ≤ k`; terms with `Σ j_i ≥ ℓ` vanish in `B`; hence
  every surviving monomial has degree `≤ K = k(a + 2(ℓ−1))`. Verified: with `ℓ = p ∈ {1,2,3}`
  (so `K` is below the incidence count), the full product `F` had no nonzero coefficient of degree
  `> K` in 44 systems, and the maximum nonzero degree reached `K` exactly when `ℓ = 1`.
- Lemma 5.2 is used only in its integer-argument form (`S_ℓ(Π B_i) ≡ Π 1{2|y_i} mod 2^ℓ`) with
  `p = ℓ = n+1`, exactly as stated at lines 2998–3010; the degree clause of Lemma 5.2 is not
  invoked, (D.1) re-derives it inline. Lemma 5.1 is used as stated (`deg e_j ≤ 1`, poly-time
  construction; Lemma B.1 gives `|a_j|,|b_j| ≤ 2^{Cℓ²}`, so `L = poly(n)`). I re-derived `e_j` by
  successive division of `(1−Y)^ℓ Σ_{j<ℓ} C(ℓ+j−1,j) Y^j` by `Y²−Y` and confirmed both lemmas
  numerically for `ℓ ≤ 9`.
- Indexing (lines 4437–4492): arrays `(K+1)^{J²} = 2^{O(√n log n)}` (`J² ≤ 4√n`); each monomial of
  `F` lies in exactly one array and has one valid index per pair; `Π C_gh ≤ C(N, Σd) ≤ C(N+K, K)`
  gives (D.3) `M ≤ J² + K log2(e(N+K)/K) = O(nν)` since `(N+K)/K = O(λ^c)`; `⌈log2 C_gh⌉ ≤ N_gh`
  so vertex degree `≤ n^{3/4} λ^{O(1)}`. Verified on every array of every test run: (D.3) held and
  degree `≤` incidences; the lexicographic encode/decode by binomial counting round-trips.
- Entries (lines 4494–4530): the Möbius formula `[z_{S}] B̄_i = Σ_{T⊆S} (−1)^{|S−T|} B_i(1_T, V)` was
  checked against direct symbolic multilinear expansion on every test of 44 systems; variable-group
  entry `2^{#{v: b_v = 0}}` is right and covers variables outside all scopes; cost `2^{kλ^c}·poly`
  per test, `≤ 2^{λ^{O(1)}}` per vertex, far below the permitted `2^{A s^{9/10}}`.
- Whole identity: `Σ_branches S_ℓ(Σ_arrays contraction) ≡ #common zeros (mod 2^{n+1})`: 0 mismatches
  on 40 systems at `p = ℓ = n+1` (n = 4..6), 40 at small `ℓ`, 15 with branching forced (`D* = 1`),
  and 10 denser systems (N up to 19, up to 1,050 arrays, 15 wires).
- Application at line 4536: `s = nν`, `p = ℓ = n+1 ≤ Cs`, wires `O_{k,c}(s)`, `2J ≤ s` vertices,
  degree `n^{3/4}λ^{O(1)} ≤ ⌈s^{9/10}⌉` for large `n` (Finding 1 quantifies "large"), entry time
  `2^{λ^{O(1)}} ≤ 2^{s^{9/10}}`. Constants of Theorem D.1 depend only on `C, A, b` and the vertex
  polynomial, so they are uniform over the `2^{n/√λ + O(√n log n)}` sequential applications; total
  exponent `O(nν/√λ)`. Space: counters for branches and arrays, polynomial per contraction. Correct.

**4. Checked, no fault: the greedy steps (lines 4562–4589, p. 57).** Lemma 6.3 with
`σ = 1/⌈√λ⌉` (a rational in `(0,1]`, `L_σ = O(log λ)`): `n^{O_k(1)} 2^{n/⌈√λ⌉}` nodes, leaf
occurrence bound `B = O_k((√λ log λ)^{k−1}) = λ^{O_k(1)}`, `≤ Bn` clauses. Per leaf, Lemma 6.2 as
stated: `≤ 3n(2m_G)^P` counts (the "+1 final call" at line 4580 is redundant, since the last
round's minimum already is `N(A)`, but harmless), each a system of `≤ 6n` equations with
`≤ 2^k max(D0,P) = λ^{O_k(1)}` monomials of degree `≤ k` by (6.1) — exactly Lemma D.2's input with
`c = c(k)` for large `n`. Invocations per leaf `2^{λ^{O_k(1)}}`, leaves `2^{n/√λ} n^{O(1)}`, each
invocation `n^{O(1)} 2^{O(nν/√λ)}` (which already contains its own `2^{n/√λ}` branching): total
`(n+m)^{O_k(1)} 2^{O_k(nν/√λ)}`. Leaves are disjoint (Lemma 6.3, Appendix A), so an `(n+1)`-bit
accumulator suffices; depth-first traversal with polynomial depth gives polynomial space. Lemma D.2
is applied to each leaf on the original `n ≥ 20` declared variables, as its statement requires.

**5. AMBIGUITY (harmless): "fixed polynomial in s" and "for all sufficiently large s".** Theorem
D.1's vertex bound is "a fixed polynomial in s"; D.2 supplies `≤ 7k·s`, D.3 `2⌈n^{1/4}⌉`, with
coefficients depending on `k` (and `c`). The proof needs the reading "a polynomial whose degree and
coefficients are among the fixed bounds", which is how line 4303 ("Constants depend only on the
fixed bounds in the hypotheses") must be read for the `O_k` constants to be legitimate. Likewise
"the degree and precision bounds hold for all sufficiently large s" (line 4341): the precision bound
holds for all `s ≥ 1` with `C ≥ 2`; only the degree bound needs `s ≥ max{k,3}^{10/9}`.

**6. AMBIGUITY (outside the appendix but about what it delivers): the sign convention of
`o(1)`.** The abstract (line 7) and the definition of `ρ(n)` (lines 80–84) write
`n/(log n)^{1/2+o(1)}`, whereas `n log log n/√log n = n/(log n)^{1/2 − log log log n/log log n}`,
i.e. `(log n)^{1/2 − o(1)}`. Consistent only under the convention that `o(1)` may be negative
(standard, but the display suggests the exponent is at least 1/2). Not an error.

**7. AMBIGUITY (harmless): base of the logarithm.** The paper's convention is natural log (line
58); D.4 (line 4599) switches to base 2 for its proof; Theorem D.1's `2^{O(s/√log s)}` is
base-independent up to the constant. Lemma D.2's `λ = ⌈log2 n⌉`, `ν = ⌈log2 λ⌉` are explicit.

**8. Consistency with Sections 3–6 and with 6.4 (brief item 5).** Appendix D uses: Lemma 5.1
(as stated), Lemma 5.2 (integer form, as stated), (6.1) (as stated), Lemma 6.1 (support `≤ D0`,
`≤ 3n` rows), Lemma 6.2 (`3n(2m)^P` counts, `≤ 6n` equations, `≤ 2^k max(D0,P)` monomials, final
`N(A) = #F`), Lemma 6.3 (as stated, with a smaller `σ` than 6.4's). None is used in a stronger
form. Lemma D.2 is the contraction analogue of Theorem 2.2 (lines 1504–1510), same input class,
better exponent; nothing in D.3 contradicts the interpolation route of 6.4, which only needs its own
`σ = 1/s` with `s = ⌊√λ/ν²⌋`. The single-algorithm paragraph (lines 4594–4598) correctly makes
Theorem 1.1's "its running time" refer to one algorithm: clause network when `m ≤ nν`, else parity
queries; for fixed `D`, inputs with `m ≤ Dn` take the clause branch once `n > 2^{2^{D−1}}`, and the
finitely many smaller `n` cost `O_D(1)` more in the exponent.

**9. The introduction's sentence (line 87, brief item 6).** "Appendix D proves both bounds in
Theorem 1.1 by tensor contraction" is accurate given Theorem D.1: both bounds, deterministic (every
component — Lemma 6.1's construction, Lemma 6.2's derandomised greedy, Lemma 6.3's tree,
branch/array enumeration, Theorem D.1 — is deterministic), polynomial space.

## The exponent arithmetic (my own)

*Fixed density.* `s = n+m ≤ (1+D)n`, `log s ≥ log n`, so `s/√log s ≤ (1+D) n/√log n`: exponent
`O_{k,D}(n/√log n)`, polynomial factor `s^{O_k(1)} = (n+m)^{O_k(1)}`.

*Arbitrary density, inside Lemma D.2.* `s = nν` with `ν = ⌈log2⌈log2 n⌉⌉ ≤ log2 log2 n + 2 ≤
1.45 log log n + 2`, and `log s = log n + log ν ≥ log n`, so
`s/√log s ≤ nν/√log n ≤ (1.45 + o(1))·n log log n/√log n`. Numerically the ratio
`(s/√log s)/(n log log n/√log n)` is 1.55–1.92 for `n` from `10^2` to `10^{10000}` (`exponents.py`),
so `2^{O(s/√log s)} = 2^{O(n log log n/√log n)}` as claimed. The other exponents: branches
`n/√λ ≤ nν/√λ`; arrays `J² log2(K+1) ≤ 4√n·O(log n) = o(nν/√λ)` (ratio `10^{-2}` at `n = 10^5`,
`10^{-23}` at `10^{50}`); leaves `n/⌈√λ⌉ ≤ nν/√λ`; evaluations per leaf `λ^{O_k(1)} = o(nν/√λ)`.
Sum: `O_k(nν/√λ) = O_k(n log log n/√log n)`. The clause-network branch of the single algorithm,
`m ≤ nν`: `s ≤ n(1+ν)`, ratio to `n log log n/√log n` between 1.68 and 2.30 over the same range.

*Polynomial factor and "n ≥ 20".* `(n+m)^{O_k(1)}` collects normalisation `poly(n,m)`, tree nodes
`poly(n, log(2/σ))`, Lemma D.2's `n^{O(1)}`, and Theorem D.1's `(s+L)^{O(1)}` with `L = poly(n)`
(the `e_j` have `O(ℓ²)` bits each by Lemma B.1). For `20 ≤ n < n_0(k)` exhaustive search costs
`2^n poly(n,m) ≤ (n+m)^{O(1)} 2^{C_k n log log n/√log n}` with `C_k = max_{20≤n≤n_0} √log n/log log n`
(≈ 1.4 at `2^{20}`, 3.0 at `2^{400}`, 4.0 at `2^{1000}`), so the "n ≥ 20" statement is consistent
with the "sufficiently large n" provisos — at the price in Finding 1.

## What this audit does not establish

- The truth of Theorem D.1 (Section D.4), including whether its proof actually needs only the
  hypotheses listed in its statement (e.g. that the entry oracle's `2^{A s^{9/10}}` cost and the
  `⌈s^{9/10}⌉` degree are compatible with its leaf evaluation at `M ≤ s/⌊√λ⌋` edges — plausible,
  since `s^{9/10} = o(s/√log s)`, but not checked here).
- The lemmas of Sections 5–6 and Appendix A themselves (Lemma 6.1's expander construction and
  its `m/P` distance bound, Lemma 6.2's averaging argument, Lemma 6.3's disjointness); I checked
  only that Appendix D uses them as stated. One point worth a glance by whoever audits Section 6:
  Lemma 6.2's argument when a leaf has `m_G < P` clauses (then `m/P < 1` and the miss probability
  bound still holds because `|supp| ≥ 1 > m/P`), which the proof does not spell out.
- Computational verification was at `n ≤ 6` for both encodings; it certifies the algebra of the
  constructions (Möbius inversion, truncation bound, variable-group entries, index decoding,
  bipartite subdivision), not the asymptotic parameter inequalities, which were checked by
  calculation in `exponents.py` with the constants the text supplies and a parametric `c`.
- The practical content of Theorem 1.1: with the constants Section 6 supplies, the algorithm is
  exhaustive search for every `n` below roughly `2^{600}` (Finding 1). This does not affect the
  asymptotic claim.
