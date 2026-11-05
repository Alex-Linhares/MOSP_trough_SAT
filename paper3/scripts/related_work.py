#!/usr/bin/env python3
"""Section 9 of paper 3 (related work and context): every quotation located.

Read-only. Reads (with open() only; nothing imported, built or run):

  * paper3/related/fetched/         the four sources item 08 fetched on
                                     2026-11-05 (arXiv API record and abstract
                                     page of 2608.14673; the READMEs of
                                     leanprover/comparator and ammkrn/nanoda_lib;
                                     the GitHub API records of both repositories
                                     and their latest commits);
  * ~/dev/untrusted/openai-math/    the collection at 4eaee875: history.md,
                                     lean/docs/378.md,
                                     lean/ComparatorChallenges/README.md and
                                     SubexponentialSAT.json;
  * reports/scratch/eth_audit/paper.txt   the manuscript extract (the [IP01]
                                     and [IPZ01] entries, the "exhaustive
                                     search" sentence);
  * paper3/replay/logs/nanoda/nanoda_sandbox.txt  the commit the replay ran;
  * literature/                      the holdings check.

Checks (each a line or a fragment the section quotes), then:

  * writes paper3/latex/tables/related_sources.tex  (Table 9.1: every source
    with its location, date and hash or commit);
  * prints the prior-statement search: how often the strings the title's
    observation would use occur in each searched text, with the line numbers
    in the manuscript extract.

Usage (from the repository root):

    python3 -I paper3/scripts/related_work.py           (check and write)
    python3 -I paper3/scripts/related_work.py --check   (verify only, write nothing)

Exit 0 and "ALL CHECKS PASSED" when every check holds.
"""
import hashlib
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
FETCHED = os.path.join(ROOT, "paper3", "related", "fetched")
CLONE = os.path.expanduser("~/dev/untrusted/openai-math")
PAPER_TXT = os.path.join(ROOT, "reports", "scratch", "eth_audit", "paper.txt")
TABLE = os.path.join(ROOT, "paper3", "latex", "tables", "related_sources.tex")
NANODA_LOG = os.path.join(ROOT, "paper3", "replay", "logs", "nanoda", "nanoda_sandbox.txt")
LITERATURE = os.path.join(ROOT, "literature")
CLONE_COMMIT = "4eaee875"

FAILURES = []


def check(cond, what):
    if not cond:
        FAILURES.append(what)
        print("FAIL:", what)


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def lines(path):
    return read(path).split("\n")


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        h.update(fh.read())
    return h.hexdigest()


def line_has(path, lineno, fragment, label=None):
    """Line `lineno` (1-based) of `path` contains `fragment`."""
    ls = lines(path)
    ok = lineno <= len(ls) and fragment in ls[lineno - 1]
    check(ok, f"{label or os.path.relpath(path, ROOT)} line {lineno} should contain {fragment!r}")
    return ok


def main(argv):
    check_only = "--check" in argv

    # ---- 1. the fetched files and their hashes ---------------------------
    fetched = {
        "arxiv_api": "arxiv_2608.14673_api.xml",
        "arxiv_abs": "arxiv_2608.14673_abs.html",
        "comparator_readme": "comparator_README_master.md",
        "comparator_repo": "comparator_repo.json",
        "comparator_commits": "comparator_commits.json",
        "nanoda_readme": "nanoda_README_master.md",
        "nanoda_repo": "nanoda_repo.json",
        "nanoda_commits": "nanoda_commits.json",
    }
    paths = {k: os.path.join(FETCHED, v) for k, v in fetched.items()}
    for k, p in paths.items():
        check(os.path.exists(p), f"fetched file missing: {p}")
    if FAILURES:
        return finish()
    hashes = {k: sha256(p) for k, p in paths.items()}

    # ---- 2. the human-audit paper, from the arXiv API record --------------
    api = read(paths["arxiv_api"])
    check("<id>http://arxiv.org/abs/2608.14673v3</id>" in api, "arXiv record is v3")
    check("<title>A Human Audit of OpenAIs AI-Generated Mathematical Proofs</title>" in api,
          "arXiv title (the record's own spelling, without the apostrophe)")
    check("<name>Mikołaj Sienicki</name>" in api and "<name>Krzysztof Sienicki</name>" in api,
          "arXiv authors")
    check("<published>2026-08-03T15:12:46Z</published>" in api, "arXiv v1 date")
    check("<updated>2026-09-09T12:39:56Z</updated>" in api, "arXiv v3 date")
    check('<arxiv:primary_category term="cs.AI"/>' in api, "arXiv primary class cs.AI")
    check("<arxiv:comment>8 pages, 5 references. V2: 11 pages, 8 references. V3. 13 pages, 27 references. "
          "Revised and updated version</arxiv:comment>" in api, "arXiv comment field")
    m = re.search(r"<summary>(.*?)</summary>", api, re.S)
    abstract = m.group(1).strip() if m else ""
    abstract_quotes = [
        "We assess 18 chapter-specific reviews of the ten mathematical results announced by OpenAI on "
        "1 August 2026, alongside review standards, Lean formalizations, subsequent research, and "
        "mathematical references.",
        "The article audits this review record without claiming a complete reconstruction of all ten proofs.",
        "No confirmed substantive mathematical error in a principal result remains in the examined "
        "assessments, although review depth varies and some dependencies remain partly checked.",
        "In Chapter 6, an apparent polarity error was withdrawn after an overbar lost during PDF extraction "
        "was recovered from the typeset source.",
        "We argue that confidence should combine formal checking, human reconstruction, independent "
        "mathematical use, and a public record supporting correction of both proofs and reviews.",
    ]
    for q in abstract_quotes:
        check(q in abstract, f"abstract sentence: {q[:50]!r}")
    check("378" not in abstract and "Exponential" not in abstract and "ETH" not in abstract,
          "the abstract does not mention family 378 or ETH")
    html = re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", read(paths["arxiv_abs"])))
    for v, date in (("v1", "Mon, 3 Aug 2026 15:12:46 UTC"), ("v2", "Tue, 25 Aug 2026 03:36:45 UTC"),
                    ("v3", "Wed, 9 Sep 2026 12:39:56 UTC")):
        check(f"[{v}] {date}" in html, f"arXiv abstract page lists {v} on {date}")

    # ---- 3. the comparator README and repository -------------------------
    cr = paths["comparator_readme"]
    line_has(cr, 3, "This project has been merged into core as of Lean release v4.35.0 in the form of `lake comparator`")
    line_has(cr, 8, "Comparator is a trustworthy judge for Lean proofs.")
    line_has(cr, 10, "[`landrun`](https://github.com/Zouuup/landrun)")
    line_has(cr, 11, "[`lean4export`](https://github.com/leanprover/lean4export/)")
    line_has(cr, 12, "(optional) [nanoda](https://github.com/ammkrn/nanoda_lib/)")
    line_has(cr, 13, "This is only necessary if you want to check with the nanoda kernel in addition to the builtin one.")
    line_has(cr, 27, '"permitted_axioms": ["propext", "Quot.sound", "Classical.choice"]')
    line_has(cr, 30, "contains at least a theorem named `todo1` that has a `sorry`")
    line_has(cr, 34, "Given the following assumptions:")
    line_has(cr, 43, "5. The Lean kernel is correct (with `external_kernels` this can be reduced to")
    line_has(cr, 44, '"At least one of the Lean kernel or the `external_kernels` is correct")')
    line_has(cr, 52, "All theorems in `Solution` that are listed in `theorem_names` are guaranteed to:")
    line_has(cr, 53, "1. Prove the same statement as provided in `Challenge`")
    line_has(cr, 54, "2. Use no more axioms than listed in `permitted_axioms`")
    line_has(cr, 55, "3. Be accepted by the Lean kernel")
    line_has(cr, 58, "The Trusted Code Base of Landrun naturally includes the operating system and hardware it is running on")
    line_has(cr, 70, "Comparator can additionally check solutions with external kernels.")
    line_has(cr, 86, "For backwards compatibility reasons users may instead set `enable_nanoda: true` to obtain a config")
    line_has(cr, 87, "that calls `nanoda_bin`.")
    line_has(cr, 185, "1. Build `Challenge` using `lake` in a `landrun` sandbox that has:")
    line_has(cr, 188, "2. Run `lean4export` on the produced `Challenge.olean` in a `landrun` sandbox that has:")
    line_has(cr, 190, "3. Repeat the same build sandboxed and export sandboxed steps with `Solution`")
    line_has(cr, 191, "4. Verify that all declarations used in the statement of all relevant theorems in `Challenge`")
    line_has(cr, 192, "are the same as in the `Solution` environment.")
    line_has(cr, 195, "5. Verify that the body of all relevant theorems in the `Solution` environment only uses axioms")
    line_has(cr, 196, "listed in `permitted_axioms`")
    line_has(cr, 197, "6. Replay the `Solution` environment into the Lean kernel.")
    line_has(cr, 207, "Comparator was originally developed by Lean FRO, with feedback from the AIMO team, in support of the")
    line_has(cr, 208, "AIMO series of competitions and their goal of enabling trustworthy LLM Lean evaluation on Kaggle.")
    check(len(lines(cr)) in (208, 209), "comparator README has 208 lines")
    crepo = json.loads(read(paths["comparator_repo"]))
    check(crepo.get("full_name") == "leanprover/comparator", "comparator full_name")
    check(crepo.get("archived") is True, "comparator repository is archived")
    check(crepo.get("default_branch") == "master", "comparator default branch master")
    check((crepo.get("license") or {}).get("spdx_id") == "Apache-2.0", "comparator licence Apache-2.0")
    check(str(crepo.get("pushed_at", "")).startswith("2026-10-14"), "comparator last push 2026-10-14")
    ccommit = json.loads(read(paths["comparator_commits"]))[0]
    comparator_sha = ccommit["sha"]
    check(comparator_sha.startswith("865edc14"), "comparator latest commit 865edc14")
    check(ccommit["commit"]["committer"]["date"].startswith("2026-10-14"), "comparator latest commit date")
    check(ccommit["commit"]["message"].startswith("doc: migration notice"), "comparator latest commit message")

    # ---- 4. the nanoda README and repository ------------------------------
    nr = paths["nanoda_readme"]
    line_has(nr, 3, "This is an external type checker for the [Lean 4](https://lean-lang.org/) programming language and theorem prover.")
    line_has(nr, 13, "Export files can be created with [lean4export](https://github.com/leanprover/lean4export).")
    line_has(nr, 21, "there is no old school CLI")
    line_has(nr, 23, "Given that lean4export already uses json as its export format")
    line_has(nr, 33, "The average Lean user will want to permit the three semi-official axioms, which are `Quot.sound`, `Classical.choice`, and `propext`, and most export files will also rely on `Lean.trustCompiler`.")
    line_has(nr, 39, "`\"nat_extension\"` and `\"string_extension\"` enable or disable the Nat and String kernel extensions.")
    check(len(lines(nr)) in (85, 86), "nanoda README has 85 lines")
    nrepo = json.loads(read(paths["nanoda_repo"]))
    check(nrepo.get("full_name") == "ammkrn/nanoda_lib", "nanoda full_name")
    check(nrepo.get("description") == "Library implementing type inference/checking functionality based on the Lean theorem prover",
          "nanoda repository description")
    check((nrepo.get("license") or {}).get("spdx_id") == "Apache-2.0", "nanoda licence Apache-2.0")
    check(nrepo.get("archived") is False, "nanoda repository not archived")
    ncommit = json.loads(read(paths["nanoda_commits"]))[0]
    nanoda_sha = ncommit["sha"]
    check(nanoda_sha == "8de7e0c4ed3052745a7f8725164efd9e76d84c56", "nanoda latest commit 8de7e0c4")
    check(ncommit["commit"]["committer"]["date"].startswith("2026-10-29"), "nanoda latest commit date 2026-10-29")
    # the replay (item 01) ran exactly this commit
    check(os.path.exists(NANODA_LOG), "replay nanoda log present")
    if os.path.exists(NANODA_LOG):
        check(f"nanoda_lib commit {nanoda_sha}" in read(NANODA_LOG),
              "the replay's nanoda commit equals the repository's latest commit")
        check("Compiling nanoda_lib v0.4.31" in read(NANODA_LOG), "the replay's nanoda version 0.4.31")

    # ---- 5. the collection's own texts ------------------------------------
    hist = os.path.join(CLONE, "history.md")
    check(os.path.exists(hist), "clone history.md present")
    if os.path.exists(hist):
        check(len(lines(hist)) in (56, 57), "history.md has 56 lines")
        line_has(hist, 11, "## October 26, 2026")
        line_has(hist, 18, "- *The Exponential Time Hypothesis is False.* The paper gives a deterministic algorithm that exactly counts satisfying assignments of fixed-width CNF formulas in subexponential time and polynomial space. The case of 3-SAT refutes the Exponential Time Hypothesis. An independent working group of computer scientists led by Russell Impagliazzo, Ramamohan Paturi, and Ryan Williams will examine and explain the proof. At the group\u2019s request, we are making the materials public immediately so others can examine them as well.")
        hl = lines(hist)
        check(sum("working group" in l for l in hl) == 1, "history.md names a working group exactly once")
        check(not any(re.search(r"\b(audit|review)", l, re.I) for l in hl),
              "history.md has no word 'audit' or 'review'")
        check([i + 1 for i, l in enumerate(hl) if re.search(r"verif", l, re.I)] == [27]
              and "mutually unbiased bases" in hl[26],
              "the one 'verif' in history.md is line 27, another family's Python checker")
    doc = os.path.join(CLONE, "lean", "docs", "378.md")
    line_has(doc, 9, "For fixed $k\\ge2$, Lean proves that a deterministic machine exactly counts")
    line_has(doc, 11, "the October 25 manuscript gives the sharper time bound")
    line_has(doc, 17, "[SubexponentialSAT.lean](../ComparatorChallenges/SubexponentialSAT.lean)")
    ccr = os.path.join(CLONE, "lean", "ComparatorChallenges", "README.md")
    check(len(lines(ccr)) in (10, 11), "ComparatorChallenges/README.md has 10 lines")
    line_has(ccr, 1, "# [Comparator](https://github.com/leanprover/comparator) challenges")
    line_has(ccr, 3, "Install `comparator`, `landrun`, and `lean4export`, and make them available on `PATH`.")
    line_has(ccr, 9, "lake env comparator ComparatorChallenges/QuasiRiemannHypothesis.json")
    cfg = json.loads(read(os.path.join(CLONE, "lean", "ComparatorChallenges", "SubexponentialSAT.json")))
    check(cfg.get("challenge_module") == "ComparatorChallenges.SubexponentialSAT", "JSON challenge_module")
    check(cfg.get("solution_module") == "OAI.Algorithms.SubexponentialSAT.Main", "JSON solution_module")
    check(cfg.get("theorem_names") == ["OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"],
          "JSON theorem_names")
    check(cfg.get("definition_names") == [], "JSON definition_names empty")
    check(sorted(cfg.get("permitted_axioms", [])) == ["Classical.choice", "Quot.sound", "propext"],
          "JSON permitted_axioms")
    check(cfg.get("enable_nanoda") is False, "JSON enable_nanoda false")
    check("external_kernels" not in cfg, "JSON has no external_kernels")
    # the clone's commit, by reading .git/HEAD and refs (no git run)
    head = read(os.path.join(CLONE, ".git", "HEAD")).strip()
    if head.startswith("ref: "):
        ref = os.path.join(CLONE, ".git", head[5:])
        sha = read(ref).strip() if os.path.exists(ref) else ""
        if not sha:
            packed = os.path.join(CLONE, ".git", "packed-refs")
            if os.path.exists(packed):
                for l in lines(packed):
                    if l.endswith(" " + head[5:]):
                        sha = l.split()[0]
    else:
        sha = head
    check(sha.startswith(CLONE_COMMIT), f"clone at commit {CLONE_COMMIT}")

    # ---- 6. the manuscript's own entries for the hypotheses' sources ------
    line_has(PAPER_TXT, 3733, "[IP01]   Russell Impagliazzo and Ramamohan Paturi. On the Complexity of k-SAT . Journal of Computer and", "paper.txt")
    line_has(PAPER_TXT, 3734, "System Sciences 62(2), 2001, 367\u2013375.", "paper.txt")
    line_has(PAPER_TXT, 3735, "[IPZ01]  Russell Impagliazzo, Ramamohan Paturi, and Francis Zane. Which Problems Have Strongly Exponential", "paper.txt")
    line_has(PAPER_TXT, 3736, "Complexity? Journal of Computer and System Sciences 63(4), 2001, 512\u2013530.", "paper.txt")
    line_has(PAPER_TXT, 170, "PPSZ helped motivate this prediction: their improvements over exhaustive search diminish as k", "paper.txt")
    line_has(PAPER_TXT, 171, "grows [IP01, Open Problems, item 2].", "paper.txt")
    pt = lines(PAPER_TXT)
    page_3733 = sum(l.count("\f") for l in pt[:3732]) + 1
    page_170 = sum(l.count("\f") for l in pt[:169]) + 1
    print(f"paper.txt line 3733 is on page {page_3733}; line 170 on page {page_170}")

    # ---- 7. the holdings: neither hypothesis paper nor the audit paper is in literature/
    held = os.listdir(LITERATURE) if os.path.isdir(LITERATURE) else []
    for word in ("impagliazzo", "paturi", "zane", "sienicki", "2608.14673"):
        check(not any(word in f.lower() for f in held), f"literature/ holds no file named for {word!r}")

    # ---- 8. the prior-statement search ------------------------------------
    # The strings a statement of the title's observation would be likely to
    # use. Counted in each searched text; the manuscript's hits are listed.
    needles = ["practical", "brute", "trying all", "exhaustive", "2^n", "constants are",
               "every practical", "concrete"]
    searched = {
        "history.md": read(hist),
        "arXiv 2608.14673 abstract": abstract,
        "comparator README": read(cr),
        "nanoda README": read(nr),
        "lean/docs/378.md": read(doc),
        "manuscript extract": read(PAPER_TXT),
    }
    print("\nprior-statement search (occurrences, case-insensitive):")
    print("  " + "text".ljust(28) + "  ".join(n.ljust(14) for n in needles))
    for name, text in searched.items():
        counts = [len(re.findall(re.escape(n), text, re.I)) for n in needles]
        print("  " + name.ljust(28) + "  ".join(str(c).ljust(14) for c in counts))
    # the texts other than the manuscript carry none of the strings
    for name, text in searched.items():
        if name != "manuscript extract":
            check(all(len(re.findall(re.escape(n), text, re.I)) == 0 for n in needles),
                  f"{name} has none of the search strings")
    hits = [(i + 1, l.strip()) for i, l in enumerate(pt)
            if re.search(r"practical|brute|trying all|every practical", l, re.I)]
    print("\nmanuscript lines with 'practical' / 'brute' / 'trying all':")
    for n, l in hits:
        print(f"  {n}: {l[:110]}")
    check([n for n, _ in hits] == [153], "the manuscript's only such line is 153 ('practical value of')")
    check(sum(1 for l in pt[:152] if "\f" in l) + 1 == 3, "line 153 is on page 3 (form feeds before it)")
    exh = [i + 1 for i, l in enumerate(pt) if re.search(r"exhaustive", l, re.I)]
    print("manuscript lines with 'exhaustive':", exh)
    check(170 in exh and 2480 in exh and 2487 in exh, "'exhaustive' at lines 170, 2480, 2487")

    # ---- 9. the table --------------------------------------------------------
    rows = [
        ("OpenAI collection, \\texttt{history.md} line 18",
         "clone, commit \\texttt{4eaee875}", "2026-10-29 (clone)", "--"),
        ("OpenAI collection, \\path{lean/docs/378.md}",
         "clone, commit \\texttt{4eaee875}", "2026-10-29 (clone)", "--"),
        ("OpenAI collection, \\path{lean/ComparatorChallenges/README.md} and \\path{SubexponentialSAT.json}",
         "clone, commit \\texttt{4eaee875}", "2026-10-29 (clone)", "--"),
        ("arXiv 2608.14673, API record (v3)",
         "\\path{related/fetched/arxiv_2608.14673_api.xml}", "fetched 2026-11-05", hashes["arxiv_api"][:12]),
        ("arXiv 2608.14673, abstract page",
         "\\path{related/fetched/arxiv_2608.14673_abs.html}", "fetched 2026-11-05", hashes["arxiv_abs"][:12]),
        ("\\texttt{leanprover/comparator} README (\\texttt{master})",
         "\\path{related/fetched/comparator_README_master.md}",
         f"fetched 2026-11-05; commit \\texttt{{{comparator_sha[:8]}}} of 2026-10-14; archived",
         hashes["comparator_readme"][:12]),
        ("\\texttt{ammkrn/nanoda\\_lib} README (\\texttt{master})",
         "\\path{related/fetched/nanoda_README_master.md}",
         f"fetched 2026-11-05; commit \\texttt{{{nanoda_sha[:8]}}} of 2026-10-29 (the replay's)",
         hashes["nanoda_readme"][:12]),
        ("Impagliazzo \\& Paturi 2001; Impagliazzo, Paturi \\& Zane 2001",
         "not held; manuscript extract lines 3733--3736", "--", "--"),
    ]
    tex = [
        "% Written by paper3/scripts/related_work.py (python3 -I). Do not edit by hand.",
        "\\begin{tabular}{@{}>{\\raggedright\\arraybackslash}p{0.27\\linewidth}>{\\raggedright\\arraybackslash}p{0.26\\linewidth}>{\\raggedright\\arraybackslash}p{0.22\\linewidth}l@{}}",
        "\\toprule",
        "Source & Where it is on disk & When, and at what commit & SHA-256 (first 12) \\\\",
        "\\midrule",
    ]
    for r in rows:
        tex.append(" & ".join(r) + " \\\\")
    tex += ["\\bottomrule", "\\end{tabular}", ""]
    if not check_only:
        os.makedirs(os.path.dirname(TABLE), exist_ok=True)
        with open(TABLE, "w", encoding="utf-8") as fh:
            fh.write("\n".join(tex))
        print("\nwrote", os.path.relpath(TABLE, ROOT))
    print("\nfetched-file hashes:")
    for k, v in hashes.items():
        print(f"  {fetched[k]}  {v}")
    return finish()


def finish():
    if FAILURES:
        print(f"\n{len(FAILURES)} CHECK(S) FAILED")
        return 1
    print("\nALL CHECKS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
