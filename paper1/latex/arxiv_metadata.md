# arXiv submission metadata for *The pathwidth complex*

Prepared 2026-10-19. The source bundle is built and test-compiled by
`python -m paper1.latex.make_arxiv` (output `arxiv.tar.gz`, git-ignored).
The abstract below is the metadata abstract, 1783 characters against arXiv's
limit of 1,920; the PDF keeps the longer one.

**Title:** The pathwidth complex

**Authors:** Alexandre Linhares (Getulio Vargas Foundation, on leave, and Argo Laboratory; alex@argolab.org), Horacio Hideki Yanasse (Instituto de Ciência e Tecnologia, Universidade Federal de São Paulo; horacio.yanasse@unifesp.br)

**Primary category:** cs.DS (Data Structures and Algorithms)

**Cross-lists:** math.CO, cs.DM, math.OC (`paper1/todo.md`; cs.LO optional, for the Lean development)

**Comments:** 55 pages, 7 figures. Lean 4 proofs, solvers, dataset and checkers at https://github.com/Alex-Linhares/MOSP_trough_SAT

**MSC classes:** 05C85, 68R10, 90C27, 68V20

**ACM classes:** F.2.2; G.2.2; F.4.1

**Licence:** the arXiv perpetual non-exclusive licence (the minimal one). It
keeps the copyright with the authors for the journal submission; INFORMS's
default policy (SHERPA/RoMEO, publisher policy 134) allows the submitted
version on an author's own site or a non-commercial repository without
embargo, on condition that the publisher is told where a preprint is
archived, which the IJOC submission should state. A CC BY licence would be
irrevocable and is not needed.

**Abstract:**

In 2001 we listed twelve problems from operations research, VLSI design and graph theory, the minimization of open stacks problem (MOSP) among them, as equal "plus or minus one", without proofs. We now correct and extend that table, proving in Lean that most of its rows are one quantity, graph pathwidth, studied independently by communities that rarely cite one another. Eight rows are exact, two lie in bands within one or two of pathwidth, and two are false as stated. We add three members the table missed: the maximum wavefront of sparse matrix elimination, progressive pebbling, and the vertex search of Bienstock, Robertson, Seymour and Thomas. We call this cluster the pathwidth complex. The best exact MOSP algorithm, the customer search of Chu and Stuckey (2009), is also a pathwidth algorithm. We prove in Lean that two of its published dominance rules are not true, and that on a 34-customer instance the algorithm, with its better move off, reports 7 where the optimum is 6. We prove our corrected search sound in Lean; its corrected definite move was also found by Tamaki as a lemma. We re-prove all 115 benchmark optima that rested on the previous algorithm, changing none. Ported to graphs, the corrected search proves the pathwidth of all 11,534 Rome graphs and, on every benchmark set with published exact counts, as many graphs or more than the branch and bound of Coudert, Mazauric and Nisse (2016). In the other direction, a lower bound from graph minors, proved in Lean, settles in seconds MOSP instances whose refutation took core-days, and closes the Mycielski graph M_7. We release our proofs, solvers, and a dataset of 17,714 graphs, distinct up to isomorphism, from twenty benchmark collections, 16,634 with a certified pathwidth and independent checkers.
