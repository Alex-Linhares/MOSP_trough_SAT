# loop0014 item 03 — the reduction catalogue (2026-11-04)

Report section: `reports/subexp_pathwidth.md` §3. Code:
`learning/subexp_reductions.py`, tests `tests/test_subexp_reductions.py`.

Files:

- `check_atlas7.log`, `check.json` — the brute-force check of every reduction
  claimed linear (and Lengauer's quadratic one) on every graph of the
  networkx atlas to 7 vertices; §3.5 tabulates it. Committed.
- `explore.py` — the exploration that preceded §3.4: which candidate
  transforms (closed-neighbourhood double, clique blow-up, four
  cutwidth-to-vertex-separation candidates) give exact identities on all
  graphs to 6 vertices. Not the deliverable; committed for the record.
- `*.txt` — `pdftotext -layout` extracts of the held papers read for the
  catalogue (git-ignored; regenerate below). Five held PDFs are scanned and
  give no text (Ellis–Sudborough–Turner 1994; BGHK 1991; Kloks–Bodlaender
  1992; Bodlaender–Möhring 1990; Kloks–Kratsch 1992); no OCR tool is
  installed.

Regenerate:

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/03_reductions
    for f in lengauer_1981_black_white_pebbles_graph_separation \
             1988-Megiddo-Hakimi-Garey-Johnson-Papadimitriou-Complexity-Searching-Graph-JACM \
             ohtsuki_mori_kuh_kashiwabara_fujisawa_1979_one_dimensional_logic \
             1993-Gustedt-Pathwidth-Chordal-Graphs-DAM \
             1998-Bodlaender-Partial-k-Arboretum-Bounded-Treewidth-TCS \
             diaz_petit_serna_2002_survey_graph_layout_problems \
             2009-Mihai-Todinca-Pathwidth-NP-Hard-Weighted-Trees-FAW-author \
             kinnersley_1992_vertex_separation_equals_pathwidth \
             fellows_langston_1987_nonconstructive_advances_ipl \
             1994-Kinnersley-Langston-Obstruction-Set-Isolation-Gate-Matrix-Layout-DAM \
             1997-Bodlaender-Treewidth-Algorithmic-Techniques-Results-MFCS \
             2011-Petit-Addenda-Survey-Layout-Problems-BEATCS \
             mohring_1990_gate_matrix_layout_pla_folding \
             2023-Bansal-Katzelnick-On-Approximating-Cutwidth-and-Pathwidth-arXiv \
             2021-Groenland-Joret-Nadara-Walczak-Approximating-Pathwidth-Small-Treewidth-SODA-TALG \
             1996-Bodlaender-Kloks-Efficient-Constructive-Algorithms-Pathwidth-Treewidth-JAlg \
             2004-Ellis-Markov-Computing-Vertex-Separation-Unicyclic-Graphs-IC \
             1997-Kloks-Kratsch-Spinrad-Treewidth-Fill-in-AT-Free-Graphs-TCS \
             1995-Bodlaender-Kloks-Kratsch-Muller-Treewidth-Fill-in-d-Trapezoid-Graphs-TR-UU-CS-95-34; do
      pdftotext -layout literature/$f.pdf $D/$f.txt; done
    pdftotext -layout "literature/Linhares and Yanasse - 2002 - Connections between cutting-pattern sequencing, VL.pdf" $D/linhares_yanasse_2002.txt
    nice -n 19 python3 -m learning.subexp_reductions --nmax 7 > $D/check_atlas7.log
    python3 -m pytest tests/test_subexp_reductions.py -q
    nice -n 19 python3 $D/explore.py 6
