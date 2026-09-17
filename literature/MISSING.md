# Papers not yet downloaded

These papers are referenced in the project but could not be downloaded due to paywalls or server issues.

## Paywalled

- **Kinnersley, N.G.** (1992). The vertex separation number of a graph equals its path-width. *Information Processing Letters*, 42(6), 345-350. DOI: 10.1016/0020-0190(92)90234-M — Elsevier paywall. Semantic Scholar status: BRONZE (DOI redirects to ScienceDirect). **= reference [13] of Table 1 in Linhares & Yanasse (2002)**, cited there for both *graph path-width* and *vertex separation*. This is the theorem the Lean development proves; we work from secondary statements of it.

- **Yanasse, H.H.** (1997). On a pattern sequencing problem to minimize the maximum number of open stacks. *European Journal of Operational Research*, 100(3), 454-463. DOI: 10.1016/S0377-2217(97)84107-0 — Elsevier paywall. Semantic Scholar status: CLOSED. **= reference [1] of Table 1 in Linhares & Yanasse (2002)**, cited there for MOSP itself. This is Yanasse 1997b, not the 1997c paper that introduces the MOSP graph.

- **Faggioli, E. & Bentivoglio, C.A.** (1998). Heuristic and exact methods for the cutting sequencing problem. *European Journal of Operational Research*, 110(3), 564-575. DOI: 10.1016/S0377-2217(97)00269-7 — Elsevier paywall.

- ~~**Chu, G. & Stuckey, P.J.** (2009)~~ — NOW AVAILABLE as `chu_stuckey_2009.pdf`.

- ~~**Yanasse, H.H. & Senne, E.L.F.** (2010)~~ — NOW AVAILABLE as `yanasse_senne_2010_properties_preprocessing.pdf`. Note the DOI recorded here previously (`10.1016/S0377-2217(09)00632-8`) was wrong; the correct one is **10.1016/j.ejor.2009.09.017**.

- **Fellows, M.R. & Langston, M.A.** (1989). On search, decision, and the efficiency of polynomial-time algorithms. *Proc. 21st ACM STOC*, 501-512. DOI: 10.1145/73007.73055 — ACM paywall.

- **Guimaraes, G.G., Poldi, K.C. & Martin, M.** (2025). Mathematical models for the one-dimensional cutting stock problem with setups and open stacks. *Journal of Combinatorial Optimization*. DOI: 10.1007/s10878-025-01276-5 — Springer paywall.

- **Poldi, K.C. et al.** (2025). On formulations for the one-dimensional cutting stock with a limited number of open stacks problem. *International Journal of Production Research*, 64(4), 1358-1385. DOI: 10.1080/00207543.2025.2568739 — Taylor & Francis paywall.

## Highest priority — harder to obtain than they look

These were identified from the reference lists of papers we hold. *Pesquisa
Operacional* is open access on SciELO, but **only digitised from 2001 onward**,
so the two 1990s papers below are not downloadable there despite the journal
being free. Routes worth trying instead: the INPE digital library (Yanasse is at
INPE/LAC and institutional repositories often hold pre-digitisation work),
Becceneri's 1999 thesis, Becceneri et al. (2004) in *Computers & Operations
Research* which implements the same arc contraction operation, or writing to the
authors.

- **Yanasse, H.H.** (1997a). A transformation for solving a pattern sequencing problem in the wood cut industry. *Pesquisa Operacional*, 17, 57-70. — Martin et al. (2022) credit this with the MOSP graph model. Needed to settle which graph the pathwidth equivalence concerns.

- **Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (1999). Bounds for a problem of sequencing patterns. *Pesquisa Operacional*, 19, 249-277. — Source of the arc contraction lower bound, which Yanasse & Senne (2010) say "dominates all previous lower bounds proposed in the literature". Our solver currently uses the *trivial* bound, so this is the most actionable missing reference.

- **Yanasse, H.H.** (1997c). — Introduces the MOSP graph (nodes = item types) and the clique / minimum-degree lower bounds. Cited throughout Yanasse & Senne (2010); **exact venue not yet identified**, and distinct from both 1997a and 1997b.

## Obtained since

- **Yanasse, H.H., Becceneri, J.C. & Soma, N.Y.** (2007). Um algoritmo exato com ordenamento parcial para solução de um problema de programação da produção: experimentos computacionais. *Gestão & Produção*, 14(2), 353-361. — in `literature/` as `yanasse_becceneri_soma_2007_algoritmo_exato.pdf`. In Portuguese. States the partial-ordering rules precisely, which Yanasse & Senne only reference:
  - **Type I**: adjacent nodes i, j both of degree 2 — some optimal solution labels them consecutively.
  - **Type II**: if `A_j ⊆ A_i ∪ {i}` then i dominates j, and some optimal solution labels j before i. If `A_j = A_i`, they are equivalent, and Becceneri et al. (2004) reduce the graph keeping only one.

  Measured on our instances: the *reduction* rules essentially never fire (0 type-I pairs and 0 equivalences on SP2/SP3/SP4), but *dominance* relations are common — 28, 21 and 27 pairs respectively. Those are symmetry-breaking constraints rather than reductions, and are unexploited by our encoding.

## Also missing, newly identified

- **De La Banda, M.G. & Stuckey, P.J.** (2007). Dynamic programming to minimize the maximum number of open stacks. *INFORMS Journal on Computing*, 19, 607-617. DOI: 10.1287/ijoc.1060.0205 — the DP that Chu & Stuckey (2009) extends.

- **Becceneri, J.C., Yanasse, H.H. & Soma, N.Y.** (2004). A method for solving the minimization of the maximum number of open stacks problem within a cutting process. *Computers & Operations Research*, 31(14), 2315-2332. DOI: 10.1016/S0305-0548(03)00189-8 — **the most valuable missing reference.** Cited for three separate things we need: the modified least-cost-node heuristic (the MCNh that Frinhani benchmarks, and which our implementation does not reproduce), the arc contraction operation behind the 1999 lower bound, and the pattern dominance pre-processing. A 2004 Elsevier paper is ordinary interlibrary-loan territory, unlike the 1990s Pesquisa Operacional issues.

  Partially substituted by Poliquit (2008), a Master's thesis of the same title now in `literature/`, which states the MCN algorithm in full (§3) and covers arc contraction (§4.2) and a lower bound implementation (§4.4). Its statement is explicitly for instances with at most two piece types per pattern, so it does not transfer directly to the general case.

- **Yanasse, H.H. & Limeira, M.S.** (2004). Refinements on an enumeration scheme for solving a pattern sequencing problem. *International Transactions in Operational Research*, 11, 277-292. DOI: 10.1111/j.1475-3995.2004.00458.x

## Table 1 of Linhares & Yanasse (2002) — the equivalent problems

Table 1 of `Linhares and Yanasse - 2002 - Connections between cutting-pattern
sequencing, VL.pdf` asserts twelve problems equivalent up to ±1, resting on
twelve distinct references. Four are held (see `../paper2/literature/`), eight
are not. Two of the eight — Kinnersley [13] and Yanasse [1] — are listed under
**Paywalled** above and are not repeated here. The other six:

- **Kashiwabara, T. & Fujisawa, T.** (1979). NP-completeness of the problem of finding a minimum clique number interval graph containing a given graph as a subgraph. *Proc. 1979 IEEE International Symposium on Circuits and Systems*, Tokyo, 657-660. No DOI — Table 1 ref [5], *interval thickness*. **The hardest of the twelve**: 1979 conference proceedings, not indexed by OpenAlex at all, never digitised by IEEE. Needs a library holding physical IEEE conference records.

- **Möhring, R.H.** (1990). Graph problems related to gate matrix layout and PLA folding. In *Computational Graph Theory*, Computing Supplementum 7, Springer-Verlag Wien, 17-51. DOI: 10.1007/978-3-7091-9076-0_2 — Table 1 refs [6], *gate matrix layout* and *PLA folding*. Springer paywall; his TU Berlin publication pages have been retired and no archived copy was found. Note Linhares & Yanasse cite this as "Computing 1990;7:17-51", which is the Springer *book series* Computing Supplementum, not volume 7 of the journal *Computing*. Route worth trying: **TU Berlin Technical Report 223 (1989)**, the earlier version, via the TU Berlin mathematics library or Möhring directly (emeritus, still contactable).

- **Ohtsuki, T., Mori, H., Kuh, E.S., Kashiwabara, T. & Fujisawa, T.** (1979). One-dimensional logic gate assignment and interval graphs. *IEEE Transactions on Circuits and Systems*, 26(9), 675-684. DOI: 10.1109/TCS.1979.1084695 — Table 1 ref [7], *one-dimensional logic*. IEEE Xplore paywall.

- **Wing, O., Huang, S. & Wang, R.** (1985). Gate matrix layout. *IEEE Transactions on Computer-Aided Design of Integrated Circuits and Systems*, 4(3), 220-231. DOI: 10.1109/TCAD.1985.1270118 — Table 1 ref [8], *gate matrix layout*. IEEE Xplore paywall.

- **Kirousis, L.M. & Papadimitriou, C.H.** (1985). Interval graphs and searching. *Discrete Mathematics*, 55(2), 181-184. DOI: 10.1016/0012-365X(85)90046-9 — Table 1 ref [9], *node search game*; the interval-thickness = node-search-number link, which we also work from secondary statements of. **Not actually paywalled** — it sits in Elsevier's open archive and is free to read, but ScienceDirect returns HTTP 403 to non-browser clients. Kirousis has uploaded it to Academia.edu (login wall) and the NTUA DSpace repository timed out on every attempt. **The most likely of the eight to be recovered**, simply by opening the DOI in a browser. Searching by title fails because ScienceDirect carries it under the typo "Interval graphs and seatching".

- **Lengauer, T.** (1981). Black-white pebbles and graph separation. *Acta Informatica*, 16(4), 465-475. DOI: 10.1007/BF00264496 — Table 1 ref [14], *edge separation*. Springer paywall. A metadata-only record exists in the Max Planck repository (MPG.PuRe) with no attached full text.

Sources checked for all eight and found to hold nothing: OpenAlex, Semantic
Scholar, CORE (rate-limited without an API key), Internet Archive Scholar
(`api.fatcat.wiki` unreachable throughout), the publishers, the authors' own
pages, and the Wayback Machine where an author page is dead.

## Server issues

- **Lopes, I.C. & De Carvalho, J.M.V.** (2015). Graph properties of minimization of open stacks problems and a new integer programming model. *Pesquisa Operacional*, 35(2), 213-250. DOI: 10.1590/0101-7438.2015.035.02.0213 — SciELO open access, but server returned 502/504 errors. Retry later.
