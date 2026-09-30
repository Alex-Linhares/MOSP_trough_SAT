# Matrix-problem benchmark hunt: MOSP, GMLP, one-dimensional logic, PLA folding

Compiled 2026-09-30. Scope: 0/1-matrix instance collections for problems proved
exactly equal to pathwidth + 1 (MOSP, "open orders" MOOP, pattern sequencing,
gate matrix layout, linear gate assignment, one-dimensional logic, multiple PLA
folding), plus related problems recorded but marked out of scope.

The downloads are under `paper2/benchmarks/raw/`, which `paper2/benchmarks/.gitignore` excludes from git.

Already held, not hunted again:
- `benchmarks/instances/ChallengeInstances2005`: Constraint Modelling Challenge 2005, v1.1 (Harvey, Miller, Shaw, Simonis, Wilson).
- `benchmarks/instances/MOSP_Instances`: the Frinhani et al. (2018) PLOS ONE S1 Dataset (Challenge 46, Chu & Stuckey 200, Faggioli & Bentivoglio 300, SCOOP 24). It is byte-identical to the official supplement downloaded below.

## Summary

| Collection | Problem | # inst. | Size range (rows × cols) | Optima / BKS published? | Overlap with held | Downloaded? | Local path |
|---|---|---|---|---|---|---|---|
| Frinhani, Carvalho & Soma 2018, PLOS ONE S1 Dataset | MOSP | 570 (46+200+300+24) | 10×10 to 134×49 | Yes. S1 Table has Chu & Stuckey OPT per instance or class | **Identical** to `MOSP_Instances` | yes (0.43 MB zip + 0.45 MB S1 Table PDF) | `raw/frinhani2018_plos_s1/` |
| Carvalho & Soma 2015 "Larger & Harder" | MOSP | 150 | 150×150, 175×175, 200×200 | Yes. Class-mean OPT in PLOS S1 Table; per-instance values in the PT-MOSP xlsx | none (held stops at 125) | yes (0.27 MB tar.gz, 9.3 MB unpacked) | `raw/carvalho_soma2015/` |
| Frinhani, Carvalho & Soma 2018 "Large datasets" / "Very Hard" | MOSP | 610 | 400×400 to 1000×1000 | No optima. Heuristic values only (S1 Table class means, PT-MOSP xlsx) | none | yes (15.4 MB tar.xz, 685 MB unpacked) | `raw/frinhani2018_large/` |
| VLSI gate-matrix circuits (Lorena/INPE "Linear Gate Assignment" page, from Linhares) | GMLP / linear gate assignment | 11 | 10 to 202 nets × 10 to 141 gates | Yes. Best tracks in Oliveira & Lorena 2002 Table I, Gonçalves et al. 2016 Table 9, Hu & Chen 1990 Table II | none | yes (11 files, 84 KB; Wayback copy of the official page) | `raw/lorena_vlsi/` |
| VLSI circuits not online: v1, vc1, vw1, vw2, wan (Hu & Chen 1990) and x1–x9 | GMLP | 5 + 9 | 5×7 to 15×25 for the GM_Plan five; x1–x9 unknown | Track values in Hu & Chen 1990 Table II; x1–x9 values only in the PT-MOSP xlsx | none | **no**: not found online | — |
| Becceneri, Yanasse & Soma 2004 | MOSP | 710 (per Lima et al. 2024) | 10×10 to 150×150 | Class means only (Becceneri 2004 Table 2) | none | **no**: not found online | — |
| SCOOP full set (187 real instances) | MOSP | 187 | small to 134×49 | 24 in S1 Table / Gonçalves 2016 | the 24 selected are held | **no**: site dead, not archived | — |
| PT-MOSP repository (Santos Filho & Carvalho, ITOR in press) | MOSP | 720 classical + 610 large | as above | BKS/OPT xlsx tables | repackages all of the above | only the Carvalho_Soma and Frinhani folders | as above |
| Gazzinelli ILP repo (`GITHUB.zip`) | MOSP | ≈1,180 | as above | none | repackages S1 Dataset and the Frinhani large set | no (scratch copy used only to cross-check) | — |
| DFKI stigmergy-mosp | MOSP | 7 toy RDF models | 7–10 × 6–20 | no | none | no | — |
| Devadas 1986 (GENIE) circuits | multiple PLA folding / array compaction, area objective | ≈40 named | 20×27 to 644×561 | area results only | none | no: out of scope, matrices not printed | — |
| Hu & Chen / Wing et al. circuits printed in papers | GMLP | see §5 | small | yes | — | print only | — |
| Gate matrix connection cost (De Giovanni et al. 2013) | **different objective**, out of scope | ? | ? | ? | ? | no | — |

## 1. Frinhani, Carvalho & Soma (2018): PLOS ONE S1 Dataset and S1 Table

- **Problem**: MOSP (matrices stored patterns × pieces).
- **Paper**: Frinhani R.M.D., Carvalho M.A.M., Soma N.Y. "A PageRank-based heuristic for the minimization of open stacks problem." *PLOS ONE* 13(8): e0203076, 2018. DOI 10.1371/journal.pone.0203076.
- **URLs** (verified 2026-09-30, HTTP 200):
  - S1 Dataset (zip): https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0203076.s002 (DOI 10.1371/journal.pone.0203076.s002)
  - S1 Table (PDF, detailed results): https://journals.plos.org/plosone/article/file?type=supplementary&id=10.1371/journal.pone.0203076.s001
- **Licence**: CC BY 4.0, as for PLOS ONE supplements. The instances themselves are third-party.
- **Format**: one file per instance. First line `m n` (patterns, pieces), then an m × n 0/1 matrix.
- **Contents**: Challenge 46, Chu_Stuckey 200, Faggioli_Bentivoglio 300, SCOOP 24. The README PDF points to the two ResearchGate datasets in §2 and §3.
- **Optima**: S1 Table gives OPT per instance for Challenge (GP, NWRS, SP, Miller, Shaw mean) and Chu & Stuckey class means (via Chu & Stuckey 2009). For Carvalho & Soma it gives class means labelled OPT. For the Frinhani large sets it gives heuristic values only.
- **Overlap**: `diff -r` against `benchmarks/instances/MOSP_Instances` shows them **identical**, so this is the held copy's source.
- **sha256**:
  - `pone.0203076.s002_S1_Dataset.zip`: `036f0020d89fcf4b8ce2ed0f92ecff047ae2f2e40a227d2586217bb0bd28289f`
  - `pone.0203076.s001_S1_Table.pdf`: `2eeb11dd140138f2b3620b7e5efe85106cc5c70895cfddc143c002240f655270`

## 2. Carvalho & Soma (2015), "Larger & Harder" random set

- **Problem**: MOSP. Generated with Chu & Stuckey's generator; 150 instances in 15 classes, `Random-{150,175,200}-{same}-{2,4,6,8,10}-{1..10}`.
- **Paper**: Carvalho M.A.M., Soma N.Y. "A breadth-first search applied to the minimization of the open stacks." *J. Oper. Res. Soc.* 66: 936–946, 2015. DOI 10.1057/jors.2014.60. Dataset DOI 10.13140/2.1.3035.4886 (ResearchGate).
- **URLs**:
  - Original (ResearchGate): https://www.researchgate.net/profile/Marco_Carvalho7/publication/267864061_Minimization_of_Open_Stacks_Problem_MOSP_or_Minimization_of_Open_Orders_Problem_MOOP_Instances/data/545b64cd0cf2f1dbcbc9e11c/mosp-instances.zip. **Returns HTTP 403 to scripts. Not verified, not downloaded from there.** Its README notes these matrices are *piece × pattern*.
  - Downloaded from: https://github.com/Laps-F/PT-MOSP, folder `Instances/Carvalho_Soma`, commit `05edbfd9a1b9bf2548c1ce5f7ceb5704ccb572ce`. The repository is by Santos Filho & **Carvalho** (UFOP), a co-author of the set.
- **Licence**: the PT-MOSP repo is CC BY-NC 4.0, but its LICENSE says third-party instance sets "remain subject to the terms of their original publications". No licence is stated for the set itself.
- **Format**: `m n` header then a 0/1 matrix (the PT-MOSP copy has 200 200 headers etc.).
- **Optima**: PLOS S1 Table gives class-mean OPT. The PT-MOSP file `MOSP/Results-tables/BenchmarksClassicos/LARGER AND HARDER RANDOM.xlsx`, copied here as `PT-MOSP_reference_values_LARGER_AND_HARDER_RANDOM.xlsx`, has a sheet "optimal solutions known" with 150 per-instance values and a sheet "best solutions larger random". Who certified them is not stated.
- **Overlap**: none with held (held Chu & Stuckey stops at 125).
- **Archive**: `PT-MOSP_05edbfd9a1b9_Instances_Carvalho_Soma.tar.gz`, made by `git archive` of that commit, then `gzip -n`. This is **our** archive, since no original archive could be fetched. sha256 `577ad058e575a6737ee4b87792f707d60b5fe76644f750630c9e68f4edb1f35d`. Per-file sums are in `SHA256SUMS_files`.

## 3. Frinhani, Carvalho & Soma (2018), large datasets ("Very Hard")

- **Problem**: MOSP. 610 instances from Chu & Stuckey's generator. The Dataset_Description says polynomial topologies were excluded.
- **Sizes and classes** (pieces per pattern, 10 instances each), counted from the files:
  - 400×400: 2, 4, 6, 8, 10, 14, 18, 20, 24, 28, 30, 34 (120)
  - 600×600: 2 to 40 (14 classes, 140)
  - 800×800: 2 to 50 (17 classes, 170)
  - 1000×1000: 2 to 54 (18 classes, 180)

  The bundled description differs slightly: it lists "55" at 1000 and omits 34 at 600 to 1000. The files are authoritative.
- **Paper / DOI**: as §1. Dataset DOI 10.13140/RG.2.2.31716.48006/1.
- **URLs**:
  - Original (ResearchGate): https://www.researchgate.net/profile/Rafael_De_Magalhaes_Dias_Frinhani/publication/324497787_Large_datasets_for_the_MOSP/data/5b6c9dda299bf14c6d97d073/MOSPFrinhaniCarvalhoSoma.zip. **HTTP 403. Not verified.**
  - Downloaded from: https://github.com/Laps-F/PT-MOSP, `Instances/Frinhani`, commit `05edbfd9…`.
  - Independent cross-check: `GITHUB.zip` in https://github.com/ggazzinelli/Integer-Linear-Programming-for-the-Minimization-of-Open-Stacks-Problem (third party, not kept). All 611 files, description included, are **byte-identical** to the PT-MOSP copy.
- **Licence**: as §2.
- **Optima**: none. PLOS S1 Table gives class means for HBF2r (400/600 only), MCNh, PieceRank, Yuen3 and Ashikaga & Soma. Per-instance PT-MOSP, BRKGA, SA and SND results are in the PT-MOSP xlsx files, which were not copied.
- **Overlap**: none.
- **Archive**: `PT-MOSP_05edbfd9a1b9_Instances_Frinhani.tar.xz` (ours, from `git archive`, xz -9), 15.4 MB, sha256 `c6db46573426bc35e71c110c2a33d779ba8d26c7c42ff057a98bf0bc3b171229`. It unpacks to 685 MB in `Frinhani/`. Per-file sums are in `SHA256SUMS_files`.

## 4. VLSI gate matrix circuits (11 instances, online)

- **Problem**: GMLP / linear gate assignment (tracks = max open nets = MOSP on the net × gate matrix).
- **Instances** (gates × nets, matching Hu & Chen 1990 Table II exactly):
  - wli 10×11, wsn 25×17, v4000 17×10, v4050 16×13, v4090 27×23, v4470 47×37
  - x0 48×40, w1 21×18, w2 33×48, w3 70×84, w4 141×202
- **Origin**: v4000, v4050, v4090 and v4470 come from Heinbuch's CMOS cell book. w2 (ITT1), w3 (4-bit ALU) and w4 (ITT2) are from Wing & Huang (private correspondence 1988). w1 is from Wing 1985 ISCAS, wsn from Yu, wli from ref [11] of GM_Plan, and x0 from Nakatani et al. All as cited by Hu Y.H., Chen S.J., "GM_Plan: a gate matrix layout algorithm based on artificial intelligence planning techniques," *IEEE TCAD* 9(8): 836–845, 1990, DOI 10.1109/43.57791, Table II on p. 844.
- **Other papers using them**:
  - Linhares A., Yanasse H.H., Torreão J.R.A. "Linear gate assignment: a fast statistical mechanics approach," *IEEE TCAD* 18(12): 1750–1758, 1999 (DOI 10.1109/43.811324).
  - Oliveira A.C.M., Lorena L.A.N. "A constructive genetic algorithm for gate matrix layout problems," *IEEE TCAD* 21(8): 969–974, 2002 (DOI 10.1109/TCAD.2002.800454).
  - Mendes A., Linhares A. *Int. J. Systems Science* 35(1), 2004 (DOI 10.1080/00207720310001657054).
  - Gonçalves, Resende & Costa 2016, ITOR 23: 25–46 (DOI 10.1111/itor.12109), which calls them "11 individual instances from the VLSI industry; Hu and Chen (1990)".
- **URLs**:
  - Official page: http://www.lac.inpe.br/~lorena/instancias.html, section "Linear Gate Assignment", "Thanks to Alexandre Linhares". The host **timed out** on 2026-09-30.
  - Files taken from Wayback snapshots dated 2019-01-08 of `http://www.lac.inpe.br/~lorena/alexandre/{W1,W2,W3,W4,Wli,Wsn,X0,v4000,v4050,V4470,v4090}.txt`. The page snapshot is saved as `wayback_20201130173500_lorena_instancias.html`.
- **Licence**: none stated.
- **Format**: first line `gates nets`, then one row per net of `gates` 0/1 values. Every file checked for consistent dimensions.
- **Best known / optimal tracks**: wli 4, wsn 8, v4000 5, v4050 5, v4090 10, v4470 9, x0 11, w1 4, w2 14, w3 18, w4 27. Sources are Oliveira & Lorena 2002 Table I and Gonçalves 2016 Table 9, which gives the same BKS. Hu & Chen 1990 mark some as proved minimal (w1, w2, wsn). `PT-MOSP_reference_values_VLSI_GMPLAN.xlsx` repeats them.
- **Overlap**: none with held.
- **Checksums**: no archive exists, so individual files are summed in `SHA256SUMS`.

## 5. VLSI circuits not found online

- **Hu & Chen 1990 Table II, not on the Lorena page** (nets × gates, ref in GM_Plan, published tracks):
  - vc1: 15×25, ref [2] (Chang et al.), 9 tracks
  - v1: 6×8, ref [26] (Leong), 3 tracks
  - vw1: 5×7, ref [9] (Wing 1985 ISCAS), 4 tracks
  - vw2: 8×8, ref [10] (Wing, Huang & Wang 1985 TCAD), 5 tracks
  - wan: 8×7, ref [27] (Wing & Huang, private correspondence), 6 tracks

  These are print-only at best. `literature/wing_huang_wang_1985_gate_matrix_layout.pdf` is a scan and was not checked for a printed matrix. GM_Plan itself prints only its worked example w1 (p. 842).
- **x1–x9**: the PT-MOSP file "VLSI GMPLAN.xlsx" lists them with values 5, 6, 7, 2, 2, 2, 4, 4, 4, beside the 16 GM_Plan circuits (25 in total). **Origin not found**; possibly Linhares et al. 1999 or Mendes & Linhares 2004, neither checked. No files were found.
- **Ohtsuki et al. 1979** (one-dimensional logic, `literature/ohtsuki_…pdf`): worked examples only. No benchmark set.

## 6. Becceneri, Yanasse & Soma (2004) set

- **Problem**: MOSP. Random generator with a cap C on ones per row, and a graph generator that deletes arcs from K_n. The source is *Computers & OR* 31: 2315–2332, DOI 10.1016/S0305-0548(03)00189-8.
- **Size**: Table 2 of the paper (p. 2327) gives 31 classes, 10×10 to 150×150, with class means only. Lima, Santos & Carvalho 2024 (arXiv 2409.04926) use a "Becceneri instance set" of **710 instances**, 10 to 150.
- **URL**: none found, not on GitHub or the authors' repos. **Missing.** The UFOP group (Carvalho, mamc@ufop.edu.br) evidently holds a copy.

## 7. SCOOP project, full set

- 187 real woodcutting instances; the 24 non-trivial ones are held. The original URL http://www.scoop-project.net/DOCUMENTI/File/scoop_large_instances_data_set.zip no longer resolves (DNS failure, 2026-09-30) and the Wayback Machine has no capture. The domain later changed owner. **The remaining 163 are missing.**
- The PT-MOSP copies of SCOOP and Faggioli & Bentivoglio are **transposed and renumbered** relative to the held S1 copies (for example FB `p1010n0` vs `p1010n1`). Their Challenge and Chu_Stuckey folders are identical to the held ones.

## 8. Repackagings (no new instances)

- **PT-MOSP**, https://github.com/Laps-F/PT-MOSP (CC BY-NC 4.0; Santos Filho & Carvalho, "Optimizing Cutting Sequences through Parallel Tempering", ITOR in press). It contains Carvalho_Soma, Challenge, Chu_Stuckey, Faggioli_Bentivoglio, SCOOP and Frinhani, three split copies of Frinhani, and reference-value spreadsheets. Only the §2 and §3 folders and two xlsx files were taken.
- **Gazzinelli**, https://github.com/ggazzinelli/Integer-Linear-Programming-for-the-Minimization-of-Open-Stacks-Problem: S1 Dataset plus the Frinhani large set in one zip.
- **Martin, Yanasse & Pinto 2022** (ITOR, DOI 10.1111/itor.13053): uses Challenge #A (20), SCOOP #B (24) and FB #C (300), "all available in the supplementary material of Frinhani et al. (2018)". Nothing new.
- **Gonçalves, Resende & Costa 2016**: Challenge (Harvey 2130, Simonis 3630, Shaw 25, Miller + Wilson 21), FB 300, SCOOP 24 and VLSI 11 (§4). No instance page; http://mauricio.resende.info/data/index.html lists no MOSP data.
- **Carvalho's GitHub** (MarcoCarvalhoUFOP: HBF2r, HNCM, Lookahead-MOSP, MOSPDeltaEvaluation): code only, with one sample 50×50 `instance.txt`.
- **Constraint Modelling Challenge 2005** (Smith & Gent 2005): held. Its hosts ipg.host.cs.st-andrews.ac.uk and www.cs.st-andrews.ac.uk/~ipg/challenge now fail or redirect. The Wayback Machine holds `http://www.dcs.st-and.ac.uk/~ipg/challenge/instances.html` (2008) and a `ChallengeInstances2005.tgz` entry that is a 301 redirect, so it was not re-fetched.
- **Chu & Stuckey 2009**: no public instance page was found. Their set is in the S1 Dataset ("obtained directly with authors").
- **Faggioli & Bentivoglio 1998**: the generator is not public. The instances are in S1.
- **Yanasse & Senne 2010**: no instance set found.
- **Lopes & Valério de Carvalho** (interval graph completion formulations): no new public set found (not exhaustively checked).
- **DFKI stigmergy-mosp** (https://github.com/dfki-asr/stigmergy-mosp): 7 toy Turtle/RDF models, not worth cataloguing further.

## 9. Out of scope, recorded

- **Devadas 1986 GENIE** (`literature/devadas_1986_…pdf`):
  - Circuits: MAT1–MAT10 (multi-level matrices, 22×42 to 109×95), PLA1–PLA12, and the MO-GS set (DK27, BENCH2, SEX, B12, B3, PI, SHIFT, B4, LUC, P3, SPAM1, ALCOM, CLPL, SIGNET, MISJ, TS10), the SOAR control logic (260×296 PLA, 644×561 multi-level), and gate-matrix/Weinberger examples MAT1–6 and ARR1–4 (Table 5.1).
  - Why out of scope: the objective is folded area with row and column multiple folding and constraints, not track count, and no matrices are printed.
  - Several names (dk27, bench, sex, b12, b3, p3, shift, b4, luc, spam, alcom, clpl, signet, misj, ts10) are Espresso/MCNC PLA benchmarks, but no paper found uses them as GMLP or one-dimensional-logic instances.
- **Gate matrix connection cost** (De Giovanni, Massi, Pezzella, Pfetsch, Rinaldi, Ventura, ITOR 20(5): 627–643, 2013, DOI 10.1111/itor.12025): a different objective (wire length), so out of scope. Instance availability not investigated.
- **MORP** (minimization of order spread; Linhares & Yanasse 2002 eq. 5, maximum over orders of the spread minus 1): a **different objective**, bandwidth-like, not open stacks. "MOOP" (minimization of open orders), as in Carvalho & Soma's dataset title, is the same problem as MOSP.
- **Interval graph augmentation / minimum clique interval supergraph**: no matrix benchmark collection found.

## Not verified

- The ResearchGate originals of §2 and §3 (HTTP 403). The GitHub copies are by a co-author and agree across two independent repositories for §3.
- Whether the Wayback copies in §4 equal what is on the (unreachable) INPE server today.
- The origin of x1–x9, and who certified the per-instance "optimal solutions known" values for §2.
- Becceneri's 710-instance count, which comes only from Lima et al. 2024.
