# loop0014 item 01 — the audit (2026-11-04)

Reading item: no reduction or encoding is stated in it, so there is no
brute-force check to 7 vertices here (TASK.md requires one per reduction;
none was proposed). The report section is `reports/subexp_pathwidth.md` §1.

Files (the `*.txt` extracts are git-ignored; regenerate as below):

- `eth.txt` — `pdftotext -layout` of the untrusted ETH paper
  (`~/dev/untrusted/openai-math/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf`,
  887,884 bytes, 64 pages; 3,814 lines of text). Read only; nothing in the
  clone was built or run.
- `<YEAR-Author-Title>.txt` — `pdftotext -layout` of ten held PDFs in
  `literature/` with the same stem: Suchan–Villanger 2009; Kitsunai et al.
  2016; BFKKT 2006 TR and 2012 note; Kobayashi–Nakahata 2021; Bentert et al.
  ITCS 2025; Bansal–Katzelnick 2023; Fomin–Høie 2006; Bodlaender 2024
  survey; Kaneda–Kobayashi–Tamaki 2026.
- `bonnet_hdr.txt` — extract of Bonnet's twin-width HDR (held); no ETH
  statement about pathwidth or treewidth in it.
- `second_reading.md` — the one subagent's independent reading of
  `eth.txt`, kept as the cross-check of §1.3 (committed).

Regenerate:

    cd ~/dev/MOSP
    D=reports/scratch/subexp_pathwidth/01_audit
    pdftotext -layout ~/dev/untrusted/openai-math/preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf $D/eth.txt
    for f in 2009-Suchan-Villanger-Computing-Pathwidth-Faster-Than-2n-IWPEC \
             2016-Kitsunai-Kobayashi-Komuro-Tamaki-Tano-Computing-Directed-Pathwidth-1.89n-Algorithmica \
             2006-Bodlaender-Fomin-Koster-Kratsch-Thilikos-Exact-Algorithms-Treewidth-TR-UU-CS-2006-032 \
             2012-Bodlaender-Fomin-Koster-Kratsch-Thilikos-Note-Exact-Algorithms-Vertex-Ordering-TOCS \
             2021-Kobayashi-Nakahata-Note-Exponential-Time-Algorithms-Linearwidth-arXiv \
             2025-Exponential-Time-Approximation-Schemes-Vertex-Ordering-ITCS \
             2023-Bansal-Katzelnick-On-Approximating-Cutwidth-and-Pathwidth-arXiv \
             2006-Fomin-Hoie-Pathwidth-Cubic-Graphs-Exact-Algorithms-IPL \
             2024-Bodlaender-Approximation-Algorithms-Treewidth-Pathwidth-Treedepth-Short-Survey-WG \
             2026-Kaneda-Kobayashi-Tamaki-Fast-Practical-Single-Exponential-Algorithms-Branchwidth-arXiv; do
      pdftotext -layout literature/$f.pdf $D/$f.txt; done
    pdftotext -layout literature/2024-Bonnet-Twin-Width-Contraction-Sequences-HDR-ENS-Lyon-tel-04990502.pdf $D/bonnet_hdr.txt
    grep -n -i -E 'exponential time hypothesis|\bETH\b|SETH|subexponential|2\^\{o\(n\)' $D/*.txt
    # the two OpenAlex abstracts quoted in §1.2 (Bonnet 2025; Lampis 2025) are in
    # paper1/data/openalex_candidates.json under the titles
    # "Treewidth Inapproximability and Tight ETH Lower Bound" and "The Primal Pathwidth SETH".
