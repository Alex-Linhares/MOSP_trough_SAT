# Refuter's report — loop0014 item 06 (the crossover), 2026-11-04

Scope: `Crossover.lean` (with `Frame.lean`, `PrimitiveMachine.lean`),
`learning/subexp_crossover.py` (read twice: the `oct_cnf` encoding was added
while I was reading), `check_atlas7.log` (empty at 23:12 because the run
was in progress; filled by 23:14, 129,761 evaluations, 0 failures),
`check.json`, `README.md`, `eth.txt` lines 50–70, 95–120, 185–195, 225–240,
1155–1165, 1405–1420. Own brute force in `/tmp/refute/` (networkx atlas to
6 vertices, 209 graphs, own enumerators, pysat only as an extension counter
with the inputs fixed by assumptions; the module's `count_models` and
`run_checks` were not used).

## Findings

**1. WRONG — `oct_cnf` docstring's count formula.** `learning/subexp_crossover.py`
lines 37–39 and 280: "the count is `Σ_D 2^{cc(G − D)}`". The side bits of the
deleted vertices are unconstrained, so the count is
`Σ_{|D| ≤ t, G − D bipartite} 2^{|D|} · 2^{cc(G − D)}`. Exhaustive enumeration
over every variable (no SAT solver, `/tmp/refute/oct2.py`): `P_3`, `t = 1`:
18 models, docstring 10, corrected 18; `K_3`, `t = 2`: 36, 12, 36; `C_4`,
`t = 4`: 162, 35, 162. The *decision* is right (283 cases to 5 vertices, 0
mismatches), and the module says "decision only", so nothing downstream
breaks; but the sentence as written is false. Fix the formula or drop it.

**2. GAP — the crossover table's `n` is the vertex count, but the exponent
is in the number of *variables*, and only the two counts of Cor. 1.3 have
`n` variables.** `crossover_table` puts `E(n) / log₂ c` with `n` the graph's
vertex count. For every other encoding of §6 the variable count is a
constant multiple: measured in `check.json`, `indep_atleast` 6.6 (n+m),
`maxcut` 5.9 (n+m), `domset_tseitin` 1.75 (n+m), `ham` 16.5 (n+m); `q`-colouring
`q n`. With the paper form at constant 1 (`/tmp/refute/arith.py`):

| problem (DP base) | variables `N` | paper `pw*/n` at `n = 10²` | at `10⁶` |
|---|---|---|---|
| #independent sets (2) | `n` | 0.466 (table) | 0.269 (table) |
| maximum independent set via `Σ x ≥ t` (2) | `≈ 8 n` | **3.09** | **2.01** |
| 3-colouring (3) | `3 n` | 0.79 | 0.49 |
| 4-colouring (4) | `4 n` | 0.82 | 0.51 |
| Max-Cut ≥ t, `m = n` (2) | `≈ 13 n` | **4.8** | **3.2** |
| Hamiltonian cycle, `m = n` (2+√2) | `≈ 33 n` | **≈ 6** | **≈ 4** |

So under the table's own convention (constant 1), *maximum* independent
set, Max-Cut and Hamiltonian cycle have **no crossover at any `n` in the
table** (`pw* > n ≥ pw`); only the two counting problems and the colourings
do. The asymptotic statement (`ρ(N) = o(n)` when `N = O(n)`) is untouched;
the table is not. State what `n` is, and either tabulate per encoding or
label the rows "per variable of the formula".

**3. GAP — which paper exponent.** The table calls `n / √ln n` "the paper
form". Theorem 1.1 (eth.txt 56–66) gives `2^{O_{k,D}(n/√log n)}` **only at
fixed density `m ≤ D n`** and `2^{O_k(n log log n/√log n)}` otherwise. The
Tseitin encodings have `O(N)` clauses (fixed density, fine); `indepCNF` has
`m` clauses on `n` variables, so on dense graphs (`m = Θ(n²)`) the
applicable paper exponent carries the extra `log log n` (×1.5 at `10²`,
×2.6 at `10⁶`: the `c = 2` row at `10⁶` becomes 0.71, not 0.27, still
below 1). Also the paper's `log` is presumably base 2; `√ln 2 = 0.83`
shifts every "constant 1" entry — harmless since `O_{k,D}` is unknown, but
say so. The constants are `O_{k,D}`, so no entry of the table is a claim.

**4. WRONG (as quoted in the brief) — "`ρ(n)/n` with constant 1 is above 1
for all `n` below about `e^{4000}`".** `ρ(n)/n = (ln ln(n+16))² / √ln(n+16)`
is **below 1 for `n ≤ 49`** (0.77 at 10, 0.92 at 30, 0.9856 at 45, 1.0027
at 50), peaks at `16/e² = 2.165` at `ln(n+16) = e⁴` (`n ≈ 10^{23.7}`), and
crosses 1 again at `ln(n+16) = 5504`, i.e. `n ≈ e^{5504} ≈ 10^{2390}`, not
`e^{4000}` (at `y = 4000` the ratio is still 1.088). Correct form: "above 1
for `50 ≤ n ≲ e^{5500}`". The consequence claimed — the verified form's
`c = 2` crossover `pw* = ρ(n) > n − 1 ≥ pw` at every `n` in the table — is
right (the table starts at `10²`). For `c = 3, 4` the verified column shows
`pw*/n = 0.70, 0.56` at `10²`, which would be a crossover, but with the
right variable count (finding 2) `ρ(3n)/(n log₂ 3) = 2.4` at `n = 100`: no
crossover there either.

**5. OK — the arithmetic of the table, three entries by hand.**
`n = 10², c = 2`: `ln 100 = 4.60517`, `√ = 2.14597`, `100/2.14597 = 46.60` ✓;
verified `ln 116 = 4.75359`, `ln ln = 1.55890`, squared 2.43017,
`√ = 2.18027`, `ρ = 111.46` ✓. `n = 10⁴, c = 4`: `ln = 9.21034`,
`√ = 3.03485`, `3295.05 / 2 = 1647.5` ✓; `ρ = 16245.2`, `/2 = 8122.6` ✓.
`n = 10⁶, c = 3`: `269039.8 / 1.58496 = 169745` ✓; `ρ = 1854972`,
`/1.58496 = 1170357` ✓. `log₂ c` is the right divisor
(`c^{pw} = 2^{pw log₂ c}`).

**6. OK — `indepCount_subexp` says what its docstring says.** Checked by
`#check` on the built olean (`/tmp/refute/scratch.lean`): the machine and
`countTape` are quantified before `n` and `G`; the input is
`machine.init (encodeCNF (indepCNF G))`; the count tape holds
`countWord (indepCount G)`; the halting state is `decide (0 < indepCount G)`;
the time bound is `C (L+1)^d 2^{A ρ(n)}` with `L = formulaBitLength (indepCNF G)`
and `n` the `Fin n` of the graph, i.e. the vertex count (the formula's
variable count equals it). Axioms `[propext, Classical.choice, Quot.sound]`.
Not vacuous in any way I can see: `SubexpCount 2` is #2-SAT in `2^{o(n)}`,
non-trivial and not obviously inconsistent (the `n + 1`-bit count word fits
`2^n`; the encoding `cnfNumbers` is injective). Not circular. Minor
EDITORIAL: the docstring calls it "Corollary 1.3's first sentence", which
also covers `q`-colourings; only independent sets are formalised.

**7. OK / EDITORIAL — `IsSubexpExponent` and `counting_beats_dp_eventually`.**
`f =o[atTop] n` is the standard meaning of `2^{o(n)}`. The crossover theorem
is a one-line corollary of `runtimeScale_isLittleO`; it holds with
`pathwidth G` replaced by any real `≥ β n` (I proved that variant in the
scratch file in two lines), as intended. It is the inequality one would
want *for the exponential factors*, with three things outside it that the
report should name: (i) the DP is not modelled — `c^{pw}` is a number, not
a machine; (ii) `A` is universally quantified, not the `A` of
`indepCount_subexp`; the combined statement "∃ machine, C, d, ∀ᶠ n, ∀ G with
`pw G ≥ β n`, time ≤ `C (L+1)^d c^{pw G}`" is what "beats" means and is a
two-line corollary not stated; (iii) `L = Θ(m · n)` for `indepCNF` because
`encodeNat` is unary, so the polynomial factor is in `n³` on dense graphs —
still polynomial, but larger than the DP's `poly(n)`.

**8. OK — the encodings, by my own brute force to 6 vertices
(`/tmp/refute/bf.py`, 0 failures).** Independent-set count by evaluating
the CNF on all `2^n` assignments (no solver): 209/209. Threshold
`indep_atleast_cnf(g, t)`, every `t ∈ [0, n+1]`, every input assignment
(88,744): exactly one extension to the auxiliaries iff the set is
independent and `|S| ≥ t`, else zero — count-preservation in its strong
form; width ≤ 3. 3-colouring counts 209/209. Max-Cut to 5 vertices: exactly
one extension iff `cut ≥ t` (316 formulas). Cut & Count (205 graphs,
`n ≥ 3`): every model projects to a distinct `(X, sides)` (auxiliaries are
functions), `X` is a 2-factor, sides constant on its components, `side 0 =
0`, total `= Σ_X 2^{cc(X)−1}` from my own 2-factor enumeration, parity `=`
my own Hamiltonian-cycle count by permutations, and the 2-factors with
`cc = 1` are exactly the Hamiltonian cycles. Weighted decision, own
arithmetic with weights in `[1, 2m]`, 615 trials: never "yes" without a
cycle; whenever the minimum-weight cycle was unique (172 trials) the
coefficient at that weight was odd.

**9. OK — the paper proofs (b)(i)–(iv).** (i) `add_numbers` on two `b`-bit
numbers uses `b` adders of 5 auxiliaries (2 for the first); level `j` of the
tree has `n/2^{j+1}` adders on `(j+1)`-bit inputs (the brief says `n/2^j`;
same `O(n)`), total `≈ 10 n` bounded by `Σ (j+1)/2^{j+1} = 2`, measured 6.98;
comparator `O(log n)`; all Tseitin clauses width ≤ 3; every auxiliary is
the value of a gate on the inputs, and `TRUE` is a fresh variable pinned by
a unit clause, so count-preserving. (ii) `q n` variables, width `max(q, 2)`,
one-hot is a bijection — but the hypothesis needed is `SubexpCount q`, with
its own `A_q`, and the variable count is `q n` (finding 2). (iii) Direct form
width `Δ + 1` needs `SubexpCount (Δ+1)`, whose constants are `O_{Δ+1}`: a
single machine only on **bounded-degree** graphs (say so; there `m ≤ Δn/2`
anyway). Tseitin form: `or_many` spends `deg(v)` auxiliaries, `n + 2m`
variables, width 3, `2^{o(n)}` iff `m = O(n)` ✓. (iv) `n + m + ≈ 7m`
variables, width 3, count `= #{sides : cut ≥ t}` (both sides of each cut
counted) ✓, `2^{o(n)}` iff `m = O(n)` — the same caveat as (iii), to be
stated.

**10. GAP — the Hamiltonian-cycle decision rests on a one-sentence remark of
the paper, outside the hypothesis.** The parity `count ≡ #HC (mod 2)` is
exact and under `SubexpCount 3` (the thresholds and the side clauses are
width 3). The *decision* needs the weighted count `Σ_X 2^{cc−1} y^{w(X)}` in
`Q[y]/(y^ℓ)`, `ℓ = 2mn + 1`. `SubexpCount` does not provide it, and it cannot
be simulated by plain counting within budget: a weighted adder over `m`
weights of `log 2m` bits is `Θ(m log m)` gates, and `ρ(m log m)` and
`m log m / √log m` are both `≫ m`. What provides it is eth.txt 1161–1163
("The proof also works with coefficients in any commutative Q-algebra A")
and Proposition 3.4 — the counting *routine* over `A`; whether the full
pipeline of §6 / Appendix D (sparsification, branching, interpolation) is
`A`-valued throughout is the paper's assertion, not something checked here
or in the item. The module docstring says "paper form only"; the report
must say explicitly that this decision depends on the `Q`-algebra extension,
that no Lean statement covers it, and that the degree bound (3.2) is met
(each weight factor `1 + (y^{w_e} − 1) Y_e` has degree 1). Isolation lemma:
weights uniform in `{1, …, 2m}` on the family of Hamiltonian cycles as edge
sets gives a unique minimum with probability `≥ 1 − m/2m = 1/2`
(Mulmuley–Vazirani–Vazirani 1987; Cygan et al. 2011 state it with
`N = 2|U|`); at the unique minimum weight `w₀` the coefficient is
`Σ_{X: w(X)=w₀} 2^{cc(X)−1} ≡ #{HC of weight w₀} = 1 (mod 2)` ✓; any odd
coefficient implies a cycle, so the algorithm is sound always ✓. No off-by-one:
a connected 2-regular spanning subgraph of a simple graph on `n ≥ 3`
vertices is a Hamiltonian cycle; for `n ≤ 2` both sides are 0 (the module
guards `n ≥ 3`; `n = 0` would give `2^{−1}`, irrelevant). Randomised
`2^{o(n+m)} · poly`, so `2^{o(n)}` iff `m = O(n)` ✓.

**11. OK, with a required qualification — the framing (d).** An algorithm
in `2^{o(n)} · poly` is not one in `(2 − ε)^{pw} · poly(n)`: the LMS and
Cygan et al. hard instances come from SAT on `N` variables with `pw ≈ N`
and `n = poly(N, M) ≫ pw`, where `2^{o(n)}` says nothing. The combination
"DP when `pw` is small, counting when large" runs in
`min(2^{pw}, 2^{o(n)}) · poly`, which is `2^{pw}` and not `(2 − ε)^{pw}`
whenever `pw ≤ A ρ(n)`; so **no SETH-tight parameterised bound is
refuted**, including Lampis's bounded-width `pw`-SETH (a `(2−ε)^{pw}`
algorithm would have to work at every `pw`, and the counting machine is
`(2−ε)^{pw}` only at `pw = Ω(n)`). eth.txt 225–236 says what the brief
says: the treewidth-dependence bounds for Independent Set and Dominating
Set "also follow from the hypothesis that unrestricted CNF-SAT admits no
`2^{(1−δ)n} poly(n, m)`-time algorithm", which Theorem 1.1's per-`k`
constants do not touch. **The qualification**: line 187 says "Theorem 1.1
refutes ETH, SETH, Gap-ETH, and NSETH". So the *premise* of every
SETH-conditional bound is refuted under the theorem; what is "not refuted"
is the *conclusion* (no `(c − ε)^{pw}` algorithm), which now rests on the
unrestricted-CNF-SAT hypothesis (or `pw`-SETH) and on nothing else. The
report must not write "the lower bounds still hold" but "the lower bounds
are not contradicted, and their SETH premise is gone". The same applies to
ETH-conditional "no `2^{o(pw)} poly(n)`" statements: the crossover does not
supply `2^{o(pw)}` on all graphs either, because at `pw = o(n)` the
machine's `2^{o(n)}` is not `2^{o(pw)}`.

**12. EDITORIAL — stale and inconsistent records.** `README.md` says
"110,307 evaluations, zero failures, 27 s" and lists no `oct` checks;
`check_atlas7.log` (23:14) says 129,761 evaluations, 119.3 s, with
`oct_sat`/`oct_width` 9,727 each; `check.json` at 23:07 predates the `oct`
addition (no `oct` keys). Regenerate both together. The 119 s against 27 s
is load (my runs and the main agent's were concurrent), not a change.
The module docstring (line 12) mentions `THRESHOLD_AUX_PER_INPUT` as if it
were a named constant; no such name exists (the value is
`threshold_aux_ratio()['max_aux_per_input']`).

## What I could not check

The `Q`-algebra claim of eth.txt §3.1 beyond the sentence quoted — that
every step of Theorem 1.1's proof (§6, Appendix D) is valid with
`A`-valued factors — I took from the paper; nothing in the item or here
verifies it, and the Lean hypothesis does not express it. The exact lemma
numbers in Cygan et al. 2011 and in LMS 2011/2018 (neither held in
`literature/`; I cite the statements, not the numbering). The paper's
constants `O_{k,D}` and `O_k` are unknown, so no entry of the crossover
table and no finite-`n` statement about any crossover is checkable; I
checked the arithmetic of the table's convention only. I did not run
`lake build` (the oleans were present and `lake env lean` sufficed); I did
not check `Frame.lean`'s proofs beyond reading them (they are the item 02
deliverable). The atlas to 7 vertices was the main agent's run; mine stops
at 6 (209 graphs), and the Max-Cut extension check at 5.
