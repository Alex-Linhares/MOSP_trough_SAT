# Second reading of the ETH paper (one subagent, blind to §1.3 of the report)

Produced 2026-11-04 by a general-purpose subagent given only
`reports/scratch/subexp_pathwidth/01_audit/eth.txt` and seven questions
(the brief is quoted in the session transcript). Compared against
`reports/subexp_pathwidth.md` §1.3: **no disagreement**. Two precisions it
adds that §1.3 now carries: at general density the clause network of
Appendix D has `s = n + m` wires (l. 3052), so the exponent is
`O_k((n + m)/√log(n + m))` and the `n`-only bound needs `m ≤ Dn`; and the
`(log log n)²` of the interpolation route comes from `r = ⌊√λ/ν²⌋`, forced
by `D = r^{2Q} ≤ (2n)^{1/128}` (ll. 968–973).

## 1. The quantity the exponent is measured in

- **Theorem 1.1** (ll. 56–62): both bounds are in `n`, the number of *declared variables*; `m` (clauses) appears only in the polynomial factor `(n+m)^{O_k(1)}`. The fixed-density bound `2^{O_{k,D}(n/√log n)}` requires `m ≤ Dn` (l. 60–61). Appendix D explains why: "The two running times reflect the number of wires in the networks. A formula with m ≤ Dn clauses gives a network with O_{k,D}(n) wires" (ll. 3003–3005); in general the clause network has `s = n+m` wires (l. 3052) and the exponent is `O_k(s/√log s)` (l. 3058).
- **Theorem 2.2** (ll. 1137–1143): `n`, the number of Boolean variables of the polynomial system; the system has `m_test ≤ cn` equations of at most `(log n)^c` monomials each.
- **Theorem D.1** (ll. 3016–3028): `s`, a size parameter with the network having at most `Cs` edges; "We measure the size of the network by its number of edges" (l. 3014). A *wire* is an edge of the bipartite multigraph, carrying "a single bit" (ll. 3008–3009); each vertex has a tensor indexed by Boolean assignments to its incident edges.
- **Lemma D.2** (ll. 3069–3072): `n`, the declared variables of the polynomial system (`a ≤ cn` equations); internally it applies D.1 with `s = nν = n⌈log₂ log₂ n⌉` wires (ll. 3203, 3163–3165), which is where the extra `log log n` comes from.

## 2. What the method needs

**(a)** The sum is always over the full Boolean cube `{0,1}^n` of the *variables* (ll. 1157–1159, (3.1)); in D.1 it is over `{0,1}^{E(G)}`, one bit per wire (ll. 3010–3012). Restrictions `x_i = 1` on a prefix set are allowed and local (ll. 1232–1234).

**(b)** Summand: a product of factors `Φ_f`, each "any rational polynomial" (l. 1152) or with coefficients in any commutative Q-algebra (ll. 1161–1163), reading a scope `I_f ⊆ [n]`. Hypotheses:
- degree bound (3.2) (ll. 1166–1170): the product, with each incidence `(f,v)` given its own indeterminate, has total degree `≤ d`, and "Our application will have d = O(n)" (ll. 1180–1181); the Taylor cost is `q = ⌊dR/Q⌋` (l. 1446), so `d` super-linear in `n` breaks the bound.
- scope width `w` and incidence `b` (Lemma 4.7, ll. 1897–1900; (4.1), ll. 1467–1472): `|I_f| ≤ w`, each variable in at most `b` factors, `n ≤ M ≤ bn`; the parameter choice of Lemma 4.8 needs `b, w ≤ λ^β`, i.e. a fixed power of `log n` (ll. 1921–1923, 1934). "The scope bound w need not bound the degree of the factor polynomial" (l. 1472). Section 5 branches on the `≤ n/√λ` variables of incidence above `b₀` (ll. 2177–2186) to make `b` polylogarithmic.
- factor evaluation must be polynomial in bit cost (ll. 2140–2145) and must not enumerate the whole scope (l. 2151).

**(c)** Theorem D.1 (ll. 3016–3028), verbatim hypotheses: "Fix positive constants C, A, b. Let s ≥ 2 be an integer ... bipartite tensor network with at most Cs edges and maximum degree at most ⌈s^{9/10}⌉. Suppose that the number of vertices is bounded by a fixed polynomial in s, and that the entries belong to B_{P₀,ℓ} = (Z/2^{P₀}Z)[V]/(V^ℓ), 1 ≤ P₀, ℓ ≤ Cs. Suppose, uniformly for every vertex and Boolean choice of its ports, that its entry can be computed from the description in time (s+L)^b 2^{As^{9/10}} and space (s+L)^b." The ring is a truncated polynomial ring over integers modulo a power of two; `ℓ = 1` is permitted (l. 3029). Counts are recovered as residues mod `2^{n+1}` (ll. 3052–3056).

## 3. Where `2^{n/√log n}` comes from

Three costs ((2.11), ll. 663–669; (3.16), ll. 1430–1437; l. 1923–1931): Taylor data `O(n (R/Q) log(2Q/R))`, measurement tuples `τ log(2D+1) · n`, and one-group enumeration `2^{2n/r}`. Under (2.10)/(4.17) with `r = ⌊√λ/ν²⌋`, `Q = ⌊λ/(128ν)⌋`, `R = Θ(√λ)`, `τ = 1/(rλ)`: Taylor is `O(n ν²/√λ)`, measurements `O(n/r) = O(nν²/√λ)`, one group `O(nν²/√λ)` (ll. 693–705, 1967–1969). All three are of the same order; none dominates, and the `(log log n)²` is from `r` being `√λ/ν²`, because `D = r^{2Q}` must stay `≤ (2n)^{1/128}` (ll. 968–973). The cleaner `n/√log n` of Theorem 1.1 is obtained only via the tensor recursion of Appendix D, where exponents "sum geometrically to O(s/√log s)" (ll. 3041–3043).

## 4. `k` growing with `n`

`k` enters: sparsification `B = O_k((σ⁻¹ log(2/σ))^{k−1})` (ll. 1072–1073, 2473–2474), so with `σ = 1/s`, `B = (log n)^{O_k(1)}` only for fixed `k` (l. 2500); the degree bound `d = k(m_test + 2(ℓ−1))` (l. 2127, (D.1) l. 3113); the monomial count `2^k max(D₀, P)` (ll. 2436–2438) and the "single fixed c = c(k)" of Theorem 2.2 (ll. 2452–2455, 3231–3233); test-side entry cost `2^{|S_i|} ≤ 2^{kλ^c}` (ll. 3194–3196) which must fit `2^{As^{9/10}}`; the clause network's degree `max{k,3}` and "local tables have bounded size for fixed k" (ll. 3047, 3054). Section 1 says explicitly: "Theorem 1.1 gives a running-time guarantee for each fixed clause width k, while this hypothesis allows the width to grow with n" (ll. 235–236). No bound uniform in `k` is stated.

## 5. One constraint reading many bits in D.1

D.1 permits a vertex of degree up to `⌈s^{9/10}⌉` with entry computation `2^{As^{9/10}}` (ll. 3019, 3022–3024), so a vertex whose entry is a threshold "at most t of its d ports" is formally within scope for `d ≤ s^{9/10}` (its entry is computable in polynomial time). The text does not discuss threshold or other non-local constraints explicitly; the hypotheses are the only statement. Internally the degree cap is used in (D.6) `M ≥ 2D_arr ∆`, `2L ≤ ∆` (ll. 3313–3316, 3586) and the entry budget in the leaf cost `exp(O_C(H) + O_{C,A}(s^{9/10}))` (l. 3627).

## 6. Counting vs. decision, witnesses, weights

Counting is primary; "Testing #F > 0 also decides satisfiability" (l. 48). Witnesses by self-reduction, "fixing one variable at a time and checking that the remaining count is positive", and uniform sampling with `poly_k(n,m)` overhead (ll. 68–71). Weighted sums: Section 3.1 allows factors "any rational polynomials" with coefficients in any commutative Q-algebra `A` (ll. 1152, 1161–1163), subject to the degree, scope and incidence bounds above; D.1 works over `(Z/2^{P₀}Z)[V]/(V^ℓ)`.

## 7. Encodings with more variables than the natural parameter

Lines 95–99: "runtime bounds of the form 2^{o(n)} do not transfer under general polynomial-time reductions (2^{n^{o(1)}} would be needed for this), so our result does not imply that general NP problems admit subexponential time algorithms." Lines 237–243: "we need a reduction in the other direction, from that problem to fixed-width SAT, that controls the number of variables", with Set Splitting as the example having one variable per element. Corollary 1.3 (ll. 100–120) gives `2^{o(v)}` for colourings only via `qv` variables with `q` fixed, and perfect matchings only `2^{o(v+e)}`, one variable per edge. Nothing is said about permutation problems or `Θ(n²)`-variable encodings beyond these.
