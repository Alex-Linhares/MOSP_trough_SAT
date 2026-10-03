# Number audit: `paper2/problem_transformations.md` (2026-10-03, loop0008 item 07)

- Document: `paper2/problem_transformations.md`, 827 lines before this audit, 833 after.
  Line numbers below are those **before** the fixes.
- Claims audited: 44 rows (repeated mentions grouped). Two rows carry two statuses, one per source (Wing, EST).
- Status counts: REPRODUCED 18, MATCHES-RECORD 23, DRIFT 4 (all fixed), STALE 0, UNSOURCED 1, UNCHECKED 0.

Method. Every Lean name in the document was grepped in `lean/MOSPFormalization/`
and its statement read; all of them exist, with the hypotheses the text gives.
Page, section and theorem numbers were checked with `pdftotext -layout` against
the held PDFs (`literature/`, `paper2/literature/`), using the printed page numbers.
Numerical values were checked against `paper2/data/complex_check.json` (seed
20260930, 146.6 s). The checker was **not** rerun, because it rewrites that JSON.
No Lean build was run.

| line | claim (short, with the value) | source | check done | status |
|---|---|---|---|---|
| 30, 36 | pw and vs definitions, Kinnersley 1992 p. 346 | `13_kinnersley_1992.pdf` | both definitions and Thm 3.1 are on printed p. 346 | REPRODUCED |
| 43 | MOSP value, L&Y 2002 eqs. (1)-(2) | L&Y 2002 PDF | eqs. (1), (2) on pdf p. 2 | REPRODUCED |
| 51-52 | gate matrix layout, Möhring 1990 p. 18; Wing, Huang & Wang 1985 Problem 1 | `06_mohring_1990.pdf`; `08_wing_huang_wang_1985.pdf` | MPP defined on printed p. 18. Wing is a scan with text on p. 1 only; `equivalences.md` l. 224 quotes Problem 1 from p. 222 | Möhring REPRODUCED; Wing MATCHES-RECORD |
| 62, 191, 477 | Ohtsuki et al. 1979 §II-III, §IV, Thm 3 | `07_ohtsuki_et_al_1979.pdf` | §II "Problem formulation", §III "Gate sequencing and track assignment", §IV "Minimal augmentation" (boundary gates), Theorem 3 in §III | REPRODUCED |
| 69-70 | PLA folding, Möhring p. 25; path partitions p. 36 | Möhring | PLAMPP on p. 25; "path partition (or multiple folding)" and Thm 3.14 on p. 36 | REPRODUCED |
| 76-77 | interval thickness, KP 1985 p. 182; Möhring p. 31 | `09_kirousis_papadimitriou_1985.pdf`, Möhring | definition on KP p. 182; "interval thickness" defined on Möhring p. 31 | REPRODUCED |
| 87 | node search, KP 1985 p. 181; KP 1986 §2 | KP 1985, KP 1986 | game defined on p. 181; KP 1986 §2 "Two versions of searching" | REPRODUCED |
| 96-97 | edge search, KP 1986 p. 208; EST 1994 p. 53 | KP 1986; `ellis_sudborough_turner_1994_*.pdf` | sliding and progressive version on KP p. 208. The EST PDF has no text layer; `equivalences.md` l. 393 and l. 1155 cite p. 53 | KP REPRODUCED; EST MATCHES-RECORD |
| 105, 197, 495 | narrowness, Kornai & Tuza §2; Prop. 3.1 (at least one vertex) | `11_kornai_tuza_1992.pdf` | §2 "Narrowness of graphs"; Prop. 3.1 "with at least one vertex, ν = π + 1" | REPRODUCED |
| 113 | split bandwidth, Fomin 1998 §3.2 | `12_fomin_1998.pdf` | §3.2 "Split bandwidth" | REPRODUCED |
| 122, 125, 129, 301 | cutwidth on Lengauer p. 468, Definition 6, VSG on p. 467 | `14_lengauer_1981.pdf` (pp. 465-475) | min-cut on p. 468, Def. 6 on p. 473, VSG on p. 467 | REPRODUCED |
| 139-150 | BWP on Lengauer pp. 466-467; KP 1986 p. 206 and pp. 205-206; Lengauer Def. 1a, 1b | Lengauer, KP 1986 | BWP rules on pp. 466-467; pb/pbw on KP p. 206; Def. 1 a), b) on p. 468 | REPRODUCED |
| 156, 245 | minimum progressive pebbling and directives, KP 1986 p. 213, Thm 3.1 | KP 1986 | "directive" and Thm 3.1 `mpb = ns = mpbw` on p. 213 | REPRODUCED |
| 6 | "Every statement is proved in Lean unless it says otherwise" | this audit | true after the four fixes below | MATCHES-RECORD |
| 169, 381 | (E1) Kinnersley Thm 3.1; `vertexSeparation_eq_pathwidth` | PDF; `VSEquivPW.lean:49` | Thm 3.1 on p. 346; theorem exists | MATCHES-RECORD |
| 173-174 | (E2) Yanasse 1997a Prop. 5; F&L 1989 Thm 7; L&Y Prop. 2; `mospValue_eq_pathwidth_add_one`, needs one 1 | PDFs; `MOSPGraph.lean:464` | Prop. 5 in `yanasse_1997a`; Thm 7 in F&L 1989; Prop. 2 in L&Y p. 1763. Lean has the hypothesis `∃ c p, M.requires c p` | REPRODUCED |
| 180-181 | (E3) left edge, Möhring p. 31, Prop. 3.5; `NetGateMatrix.tracks_eq_mospValue`, `tracks_eq_pathwidth_add_one` | Möhring; `GateMatrix.lean:305, 323` | left-edge algorithm on p. 31. Prop. 3.5 (pw is equivalent to IGA) is on p. 32, so read "p. 31" as the left edge. Both Lean theorems need `hreq` | MATCHES-RECORD |
| 185-186 | (E4) Möhring Prop. 3.5; Kashiwabara & Fujisawa not held; `intervalThickness_eq_pathwidth_add_one` | Möhring p. 32; `paper2/literature/MANIFEST.md` (11 of 12 held); `IntervalThickness.lean:255` `[Nonempty V]` | checked | MATCHES-RECORD |
| 191-192 | (E5) `LogicArray.tracks_eq_intervalThickness` (every net on a gate), `tracks_eq_pathwidth_add_one` (some gate connects a net) | `OneDimLogic.lean:396, 218` | hypotheses are `hgate`, `hreq` as stated | MATCHES-RECORD |
| 197 | (E6) `narrowness_eq_pathwidth_add_one`, `V ≠ ∅` | `Narrowness.lean:363` | `[Nonempty V]` | MATCHES-RECORD |
| 202-207 | (E7) KP 1985 Thm; KP 1986 Thm 2.3, Thm 4.1; `nodeSearchMonotonicity`, `nodeSearch_eq_vertexSeparation_add_one`, `nodeSearch_chain`; `proof_reductions.md` §1 | KP PDFs; `NodeMonotonicity.lean:674, 659, 691`; `proof_reductions.md` l. 9 | Thm 2.3 on p. 209, Thm 4.1 on p. 216; Lean needs an edge, as stated | MATCHES-RECORD |
| 204 | Bienstock & Seymour (1991); LaPaugh (1993) | not held in `literature/` | attribution only; LaPaugh is KP 1986's ref. [3] (Thm 2.1, p. 208) | UNSOURCED |
| 210-211 | (E8) Möhring Thm 3.14; `NetGateMatrix.foldTracks_eq_pathwidth_add_one` | Möhring p. 36; `PLAFolding.lean:147` | Thm 3.14 on p. 36. Lean needs `c ≥ |N|` and `hreq` | MATCHES-RECORD |
| 217 | (E9) Lengauer Thm 4; `vsg_eq_max` (every graph); `vertexSeparation_triangleGraph` (an edge) | Lengauer p. 472; `EdgeSeparation.lean:219, 617` | checked | MATCHES-RECORD |
| 224-227 | (E10) Lengauer Thm 3, instance form for positive K; four Lean names; `pbw(G_d) = 1` if edgeless | `Pebbling.lean:887, 899, 920, 932` | `isPositiveVSG_iff_isPositivePBWP_lengauerD` has `hK : 0 < K`; `pbw_lengauerD_of_edgeless` gives `= 1` | MATCHES-RECORD |
| 235-240 | (E11) Lengauer Thm 2 form holds for K ≥ 2 and fails at K = 1; any digraph; five Lean names | Lengauer p. 469; `PebblingGu.lean:658, 668, 709, 715, 746`, docstring l. 29-35 | `hK : 2 ≤ K`; "Acyclicity is never used" | MATCHES-RECORD |
| 246-248 | (E12) `mpb_eq_mpbw`, `mpb_eq_pathwidth_add_one`, `mpbw_eq_pathwidth_add_one`, `mpb_eq_nodeSearch` | `PebblingGu.lean:1112-1124` | `[Nonempty V]`; `mpb_eq_nodeSearch` needs an edge | MATCHES-RECORD |
| 255-256 | (B1) `sb(K_2) = pw = 1`; `K_{1,3}`: `pw = 1`, `sb = 2` | `complex_check.json` `split_bandwidth`; `SplitBandwidth.lean` l. 68-72 | the checker gives `sb ≤ 2` (at most 3 splittings, an upper bound). `SplitBandwidth.lean` says "Neither value is proved in Lean". The lower bound `sb ≥ 2` is the hand argument of `equivalences.md` l. 454. The text implied Lean | DRIFT (fixed) |
| 256-258 | (B1) Fomin Thm 8 assumes connected, at least two vertices; `pathwidth_le_splitBandwidth_le_pathwidth_add_one` | Fomin p. 1 and Thm 8; `SplitBandwidth.lean:822` | checked | REPRODUCED |
| 262-264 | (B2) `K_2`: es = vs = 1; `K_{1,3}`: vs = 1, es = 2; `K_{3,3}`: vs = 3, es = 5 | `complex_check.json` `named` | values match (`es_mono` too). They are not in Lean (`equivalences.md` l. 152: "Not formalised, by choice"), but the text implied Lean | DRIFT (fixed) |
| 264-266 | (B2) EST Thm 2.1; KP 1986 p. 209; two Lean names | KP p. 209 "ns − 1 ≤ es ≤ ns + 1"; `EdgeSearchFull.lean:244`, `EdgeSearch.lean:960` | EST is a scan (see above) | MATCHES-RECORD |
| 270-272 | (N1) `EdgeSearchMonotonicity` is a stated proposition, never assumed | `EdgeSearch.lean:197` (`def ... : Prop`) | checked | MATCHES-RECORD |
| 276-280 | (N2) `pathwidth_add_one_le_tracksPinned`; on **1,027** instances `tracks_B ∈ {pw+1, pw+2}` | `OneDimLogic.lean:453`; `complex_check.json` S2b: 1,027 checked, 0 failed; split 980 / 47 | checked | MATCHES-RECORD |
| 285 | (F1) `max(pw+1, ⌈|N|/2⌉) ≤ pla` "for every matrix" | `PLAFolding.lean:159` (`pathwidth_add_one_le_plaTracks` needs `hreq`), `:165` | the `pw + 1` half needs a 1 in M. With no nets it fails (`pla = 0`) | DRIFT (fixed) |
| 286-291, 783-787 | (F1) `I_5`: pla = 3, pw + 1 = 1; `pla(I_n) = ⌈n/2⌉`; path matrix t = 2, pla ≥ ⌈n/2⌉; Möhring Prop. 3.15; three Lean names | `PLAFolding.lean:218, 241, 246, 280, 312`; checker `pla.I5 = 3`; Möhring Prop. 3.15 on p. 37 | `plaTracks_idMatrix : = (n+1)/2`; `tracks_pathMatrix_le_two` | MATCHES-RECORD |
| 296-302 | (F2) `cw(K_{1,n}) = ⌈n/2⌉`, `mcw = ⌈n/2⌉ − 1`; `K_{1,7}` breaks ±1 for cw, `K_{1,9}` for mcw; four Lean names | `EdgeSeparation.lean:889-922`; checker `named` K1,7 (cw 4, mcw 3), K1,9 (cw 5, mcw 4) | Lean proves only `n ≤ 2 cw` and `n ≤ 2 mcw + 2`; the equalities are the checker's. The arithmetic for 7 and 9 being the first stars is right (`pw + 2 < cw` first at n = 7; `pw + 2 < mcw` first at n = 9) | DRIFT (provenance; fixed) |
| 303-304 | (F2) what Lengauer proves exactly is the vertex game (E9) | Lengauer Thm 4 | checked | MATCHES-RECORD |
| 306-317 | (F3) edgeless: ns = 0, vs + 1 = θ = 1; no 1s: Z = 0; Lengauer Thm 4 at K = 0; mpb = mpbw = 1, ns = 0; Thm 2 at K = 1; five Lean names | `IntervalSearch.lean:124`, `NodeSearch.lean:746`, `EdgeSeparation.lean:646`, `PebblingGu.lean:1133, 678`; `MOSPGraph.lean:469` `mospValue_eq_zero_of_forall_not` (not named in the text) | statements match | MATCHES-RECORD |
| 356 | Lemma C: `PathDecomposition.exists_bag_of_isClique` | `MOSPGraph.lean:78` | exists | MATCHES-RECORD |
| 534, 541 | `exists_chain_step`, `exists_monotone_chain` | `NodeMonotonicity.lean:521, 270` | exist | MATCHES-RECORD |
| 592-593 | Lengauer's normal-form Lemma 5 | Lengauer p. 472 | Lemma 5 is the normal form used for Thm 4 | REPRODUCED |
| 637-638 | Lengauer proves Thm 3 from Thm 2 applied to G_d, then Thm 4 | Lengauer p. 472 | "follows from a combination of Theorem 2 with the following [Theorem 4]" | REPRODUCED |
| 719 | `equivalences.md`, P.3 | `equivalences.md` l. 1480 | the section exists | MATCHES-RECORD |
| 456 | (E4) proof: Möhring Prop. 3.5 | Möhring p. 32 | checked | REPRODUCED |

## Fixes made

All in `paper2/problem_transformations.md`:

1. l. 255-256 (B1): "$K_{1,3}$ has pw = 1 and sb = 2." → the same, followed by "(not in
   Lean: sb ≤ 2 by the brute-force check, sb ≥ 2 by hand, since splits of a tree are
   trees and keep at least three leaves)". Evidence: `SplitBandwidth.lean` l. 68-72;
   `complex_check.json` `split_bandwidth.K1,3`; `equivalences.md` l. 454.
2. l. 264 (B2): after "$K_{3,3}$ has vs = 3, es = 5" added "(values from the
   brute-force check, `complex_check.py`; not in Lean)". Evidence: `equivalences.md`
   l. 152-154; no such theorem in `EdgeSearch*.lean`.
3. l. 285 (F1): "For every matrix," → "For every matrix with at least one 1,".
   Evidence: `pathwidth_add_one_le_plaTracks (hreq : ∃ n g, M.conn n g)`.
4. l. 299 (F2): added "(Lean proves the lower bounds n ≤ 2 cw and n ≤ 2 mcw + 2, which
   is all the claim needs; the equalities are the brute-force check's at n = 7, 9.)".
   Evidence: `two_mul_cutwidth_starGraph`, `two_mul_modCutwidth_starGraph`.

None of the four touches a theorem's truth. They correct the claim that each value is proved in Lean.

## Drifts in other documents

None found. `equivalences.md` already marks the band-end values as "Not formalised, by choice".
