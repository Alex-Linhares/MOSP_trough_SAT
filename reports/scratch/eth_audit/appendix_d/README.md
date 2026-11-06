# Appendix D of "The Exponential Time Hypothesis is False": three adversarial audits (2026-11-06)

Appendix D (pp. 53–64, "A sharper bound for exact counting") is the only proof of the
manuscript's two sharper exponents (Theorem 1.1) and is not covered by the Lean
formalisation. Three agents audited it with different angles, read-only on the clone,
scripts run with `python3 -I` under this directory:

- `audit_theorem_D1.md` — the proof of Theorem D.1 (Section D.4), with eight check scripts.
- `audit_encodings_and_bounds.md` — D.2, D.3 and the derivation of Theorem 1.1 from D.1.
- `audit_numerics.md` — every identity instantiable at small size, tested with exact arithmetic
  (`numerics/`; rendered pages 58, 60, 62 under `numerics/pdfpages/`).

## Consolidated verdict

**No error found.** Every exact identity that can be instantiated held on every instance:
the D.2 encoding against brute-force model counts (1,800 + 300 formulas), Lemma D.2's
encoding against common-zero counts (127 systems), Lemma D.4's integrality, Lemma D.5's
tapered Hermite recovery (exact in 117 random cases, precision loss far inside the budget),
the mode divisibility (tight), the recursion identity (D.16) with children built literally
(408 of 408 cases, with a working negative control), the packing inequality of Lemma D.3,
and the exponent arithmetic (own derivations in two reports agree with the text, including
the additive-per-call polynomial factor the text notes).

**One apparent error was an extraction artifact.** `audit_theorem_D1.md` Finding 1 reports
`D_arr = r·2^a` in display (D.4) and shows the packing inequality fails under it. The PDF
(p. 58, rendered in `numerics/pdfpages/` and re-rendered by the coordinator) typesets
`D_arr = r^{2a}`; `pdftotext` dropped the superscript. Under `r^{2a}` everything closes, as that
report's own "repair" paragraph shows. The finding is withdrawn as an error.

**Gaps, all presentational**: the inductive statement of the recursion is never written
(children are not instances of Theorem D.1 as stated; every invariant checks); "for all
sufficiently large n" in D.3 hides thresholds of n ≥ 2^380–2^670 at k = 3; one symbol
overloaded; log bases switch between statement and proof.

**The finding that matters for paper 3 (constants, not correctness).** With the appendix's
fixed ε = 1/131072, the recursion's first parameter u_0 = ⌊ελ⌋ is 0 for every network of
fewer than 2^131071 wires, so "the fixed finite range of smaller sizes handled by direct
summation" is every input anyone can write down; the text's own child-count estimate (D.15)
exceeds direct summation unless u_0 > 1,973 (s ≥ 2^(2.6·10^8)); summed over depth with the
explicit constants the proved exponent is ≤ 19,530·C·s/√λ bits, below n for 3-CNF only when
λ ≳ 1.5·10^12 (s ≳ 2^(1.5·10^12)). Nothing contradicts the asymptotic theorem; the sharper,
unverified bound has no content at any representable size and the manuscript states no
crossover — the same observation the paper's title makes about the verified bound, now
for the sharper route, with a far larger threshold.

Cost: about 650,000 tokens across the three agents, ~25 core-minutes of scripts.
