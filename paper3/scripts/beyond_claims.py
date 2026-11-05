#!/usr/bin/env python3
"""Section 3 of paper 3: what the manuscript claims beyond the verified statement.

Regenerates every number and every location Section 3 cites, and fails loudly if
any of them has drifted:

  * for each manuscript claim, the page of paper.pdf and the line range of the
    committed extract reports/scratch/eth_audit/paper.txt (page = form feeds
    before the line + 1), with a quoted fragment that must occur in that range;
  * for each Lean fact, the file and line in the read-only clone at commit
    4eaee875 (~/dev/untrusted/openai-math), with a fragment that must occur
    there; the clone is read with open() only, nothing of it is imported or run;
  * the three exponents of Theorem 1.1 relative to n (the verified
    rho(n) = n (ln ln(n+16))^2 / sqrt(ln(n+16)), the general n ln ln n / sqrt(ln n),
    the fixed-density n / sqrt(ln n)), all at constant 1, at a few sizes, and the
    peak of the general one (2/e at ln n = e^2).

Writes paper3/latex/tables/beyond_claims.tex (the claim table) and
paper3/latex/tables/beyond_exponents.tex (the exponent table).

Run:  python3 -I paper3/scripts/beyond_claims.py      (from the repository root)
      python3 -I paper3/scripts/beyond_claims.py --check   (verify only, write nothing)
Exit status is non-zero if any fragment, page or line has moved.
"""
import json
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PAPER_TXT = os.path.join(ROOT, 'reports', 'scratch', 'eth_audit', 'paper.txt')
CLONE = os.path.expanduser('~/dev/untrusted/openai-math')
CLONE_COMMIT = '4eaee875'
CLOSURE = os.path.join(ROOT, 'reports', 'scratch', 'eth_audit', 'closure_modules.json')
TABLES = os.path.join(ROOT, 'paper3', 'latex', 'tables')

# --------------------------------------------------------------------------
# Manuscript claims. (key, claim, first line, last line, expected page(s),
# fragments that must occur in those lines, status, where proved / why.)
# Status vocabulary (Section 3.1 of the paper):
#   verified   -- the comparator statement itself, or a conjunct of it
#   supported  -- follows from the comparator statement by an argument that is
#                 on paper only (a reduction or a citation); not in the Lean
#                 library; the exponent it inherits is rho(n)
#   paper-only -- rests on a bound that is not in the Lean library at 4eaee875
# --------------------------------------------------------------------------
CLAIMS = [
    ('abstract', 'Abstract: time $(n+m)^{O_k(1)}\\,2^{n/(\\log n)^{1/2+o(1)}}$, polynomial space',
     6, 11, (1,), ['refutes the Exponential Time Hypothesis'],
     'verified (as a form)',
     '$\\rhon = n/(\\log n)^{1/2+o(1)}$ too (p.~2, lines 64--66); the $o(1)$ absorbs the difference between all three exponents'),
    ('thm11-general', 'Theorem 1.1, general: $(n+m)^{O_k(1)}\\,2^{O_k(n\\log\\log n/\\sqrt{\\log n})}$',
     56, 59, (2,), ['Theorem 1.1. For each fixed k'],
     'paper-only',
     'proved in Appendix D.3 (p.~57, lines 3222--3246); the comparator has $(\\log\\log)^2$; \\path{docs/378.md} line 11'),
    ('thm11-density', 'Theorem 1.1, $m \\le Dn$: $(n+m)^{O_{k,D}(1)}\\,2^{O_{k,D}(n/\\sqrt{\\log n})}$',
     60, 62, (2,), ['For each fixed D > 0', 'm ⩽ Dn is'],
     'paper-only',
     'proved in Appendix D.2 (p.~54, lines 3045--3064); no density case in the Lean; \\path{docs/378.md} line 11'),
    ('thm11-space', 'Theorem 1.1: $(n+m)^{O_k(1)}$ bits of space',
     60, 60, (2,), ['bits of space'],
     'verified',
     'the conjunct $\\mathtt{visitedSpace} \\le S(L+1)^e$ at every prefix, $L = O(knm)$; as $(n+|F|+1)^{e}$ in \\path{Final.lean} 104--147'),
    ('weaker', 'The weaker exponent $O_k(\\rhon)$, Proposition 6.4',
     63, 66, (2,), ['gives the weaker exponent'],
     'verified',
     'the comparator statement (Section~\\ref{sec:statement}), with the $n \\ge 20$ proviso removed; Prop.~6.4 at p.~43, lines 2474--2476'),
    ('prop64-params', 'Proposition 6.4\'s parameters $\\lambda_n = \\lceil\\log_2 n\\rceil$, $\\nu_n = \\lceil\\log_2\\lambda_n\\rceil$, $s = \\lfloor\\sqrt{\\lambda_n}/\\nu_n^2\\rfloor$',
     2480, 2486, (43,), ['select the sparsification parameter', 's2 νn4 ⩽ λn'],
     'verified (the same parameters)',
     '\\path{Asymptotics.lean} lines 14--20 define \\texttt{sparsifyLambda}, \\texttt{sparsifyNu}, \\texttt{sparsifySchedule} identically'),
    ('appendix-d-both', '``Appendix D proves both bounds in Theorem 1.1 by tensor contraction\'\'',
     67, 67, (2,), ['Appendix D proves both bounds'],
     'paper-only',
     'no tensor-network declaration in the library (Section~\\ref{sec:beyond-lean})'),
    ('self-reduction', 'Self-reduction finds a satisfying assignment; exactly uniform sampling',
     68, 71, (2,), ['standard self-reduction', 'exactly uniform random satisfying assignment'],
     'supported',
     'calls the verified counter $n$ times; the reduction is prose; cites [JVV86]'),
    ('cor12', 'Corollary 1.2: Max-$k$-SAT within $\\varepsilon m$, randomised, $2^{O_{k,\\varepsilon}(\\rhon)}$',
     77, 81, (2,), ['Corollary 1.2', 'ρ(n)'],
     'supported',
     'stated with $\\rhon$ itself; its proof (lines 82--94) samples clauses and reduces a threshold circuit to 3-CNF, on paper'),
    ('transfer-caveat', 'Caveat: $2^{o(n)}$ bounds do not transfer under polynomial-time reductions',
     95, 99, (2,), ['do not transfer under general polynomial-time'],
     'a caveat, not a claim',
     'quoted in Section~\\ref{sec:consequences}'),
    ('cor13', 'Corollary 1.3: independent sets, $q$-colourings in $2^{o(v)}$; perfect matchings in $2^{o(v+e)}$',
     100, 103, (2,), ['Corollary 1.3'],
     'supported',
     'counting-preserving encodings (lines 107--120), one variable per vertex, $q$ per vertex, one per edge plus a circuit; needs only $\\rhon = o(n)$'),
    ('cor14', 'Corollary 1.4: $C_L(n) > c\\,n\\sqrt{\\log n}$ for some $L \\in \\mathrm{E}^{\\mathrm{NP}}$',
     123, 127, (3,), ['Corollary 1.4', 'for infinitely many n'],
     'paper-only',
     'its proof (p.~51--52, lines 2925--2967) uses ``the constant-density part of Theorem 1.1\'\' (line 2949), the $2^{AV/\\sqrt{\\log_2 V}}$ bound'),
    ('s111', '\\S1.1.1: Theorem 1.1 refutes ETH, SETH, Gap-ETH, NSETH and their bounded-error randomised forms',
     187, 191, (4,), ['Theorem 1.1 refutes ETH, SETH, Gap-ETH, and NSETH'],
     'supported',
     'the one-line reason is the manuscript\'s own: a positive-or-zero test on the verified count, in $2^{o(n)}(n+m)^{O_k(1)}$; Section~\\ref{sec:consequences}'),
    ('s112', '\\S1.1.2: Theorem 1.1 refutes \\#ETH',
     211, 212, (5,), ['refutes #ETH'],
     'supported',
     'the verified machine is a deterministic $2^{o(n)}\\,\\mathrm{poly}(n,m)$ \\#3-SAT counter'),
    ('s113-basis', '\\S1.1.3: ``removes one basis for the hardness claims above\'\'; OVC and unrestricted CNF-SAT may still hold',
     226, 236, (5,), ['removes one basis', 'allows the width to grow with n'],
     'paper-only (remarks)',
     'statements about other hypotheses and reductions; nothing of them is in the library; Section~\\ref{sec:consequences}'),
    ('s113-setsplit', '\\S1.1.3: Set Splitting with sets of size $\\le k$ in subexponential time',
     237, 243, (5,), ['Set Splitting'],
     'supported',
     'one variable per element, two clauses per set (lines 239--243), on paper; inherits $\\rhon$'),
    ('corC1', 'Corollary C.1: $\\mathrm{E}^{\\mathrm{NP}} \\not\\subseteq \\mathrm{SIZE}(O(n))$',
     2912, 2916, (51,), ['Corollary C.1', 'if ETH is false'],
     'supported',
     'needs only a deterministic $2^{o(n)}$ 3-SAT decision (line 2915) plus Williams 2013, Theorem 6.1, cited'),
    ('corC2', 'Corollary C.2: inversion and exact preimage counting of constant-locality maps, $2^{O_d(\\rhon)}$',
     2974, 2977, (52,), ['Corollary C.2', 'ρ(n)'],
     'supported',
     'stated with $\\rhon$ and $n \\ge 20$; a width-$d$ CNF on the same $n$ variables, $k = \\max\\{2, d\\}$ (lines 2984--2988)'),
    ('appD', 'Appendix D: Theorem D.1 (tensor contraction), Lemma D.2, both proofs of Theorem 1.1',
     3001, 3028, (53,), ['Appendix D. A sharper bound for exact counting', 'Theorem D.1 (Boolean tensor contraction)'],
     'paper-only',
     'proofs at p.~54 (3045--3064) and p.~57 (3222--3250); D.4 uses base-2 logarithms (p.~57, lines 3251--3252)'),
]

# Lean facts: (key, path relative to the clone, first line, last line, fragments).
LEAN = [
    ('docs-378-scope', 'lean/docs/378.md', 9, 9,
     ['Lean proves that a deterministic machine exactly counts', '(\\log\\log n)^2/\\sqrt{\\log n}']),
    ('docs-378-sharper', 'lean/docs/378.md', 11, 11,
     ['the October 25 manuscript gives the sharper time bound', 'n\\log\\log n/\\sqrt{\\log n}', 'n/\\sqrt{\\log n}']),
    ('json-theorem', 'lean/ComparatorChallenges/SubexponentialSAT.json', 1, 14,
     ['"OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat"', '"enable_nanoda": false']),
    ('comparator-scale', 'lean/ComparatorChallenges/SubexponentialSAT.lean', 132, 134,
     ['runtimeScale', 'Real.log (Real.log', '^ 2']),
    ('final-compiled', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 10, 10,
     ['theorem compiled_exact_count_and_sat (k : ℕ) (hk : 2 ≤ k)']),
    ('final-main', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 74, 74,
     ['theorem exact_count_and_sat (k : ℕ) (hk : 2 ≤ k)']),
    ('final-eth', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 104, 147,
     ['theorem exact_count_eth (k : ℕ) (hk : 2 ≤ k)', '20 ≤ n → SAT.WidthAtMost k F',
      '((n + F.card + 1 : ℕ) : ℝ) ^ d', '(2 : ℝ) ^ (A * rho n)', '4 * A', '2 * d, 2 * e']),
    ('final-sat', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 149, 149,
     ['theorem sat_polynomial_space (k : ℕ) (hk : 3 ≤ k)']),
    ('final-sat-iff', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 150, 183,
     ['(answer = true ↔ SAT.Satisfiable F)']),
    ('final-original', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 184, 184,
     ['theorem original_sat_main : OAI.Algorithms.SubexponentialSAT.SqrtLog.Statement.MainTheorem']),
    ('final-axioms', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean', 197, 201,
     ['#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.compiled_exact_count_and_sat',
      '#print axioms OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.original_sat_main']),
    ('rho-base2', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Asymptotics.lean', 10, 11,
     ['noncomputable def rho (n : ℕ) : ℝ :=', 'Real.logb 2 (Real.logb 2 n)) ^ 2 / Real.sqrt (Real.logb 2 n)']),
    ('sparsify-params', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Asymptotics.lean', 14, 20,
     ['def sparsifyLambda (n : ℕ) : ℕ := Nat.clog 2 n', 'def sparsifyNu (n : ℕ) : ℕ := Nat.clog 2 (sparsifyLambda n)',
      'Nat.sqrt (sparsifyLambda n) / sparsifyNu n ^ 2']),
    ('rho-4', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Asymptotics.lean', 190, 191,
     ['theorem runtimeScale_le_four_rho {n : ℕ} (hn : 20 ≤ n)', '≤ 4 * rho n']),
    ('canonical-main', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLog/StatementCanonical.lean', 37, 37,
     ['def MainTheorem : Prop := ∀ width : ℕ, 3 ≤ width → Feasible width']),
    ('canonical-decides', 'lean/OAI/Algorithms/SubexponentialSAT/SqrtLog/StatementCanonical.lean', 21, 28,
     ['def DecidesWithBound', '(answer = true ↔ SAT.Satisfiable F)']),
]

# Identifiers that would have to exist if any corollary or Appendix D were formalised.
ABSENT_IDENTIFIERS = ['SimpleGraph', 'PerfectMatching', 'Coloring', 'IndepSet', 'IndependentSet',
                      'CircuitSize', 'OrthogonalVectors', 'MaxSat', 'TensorNetwork', 'HermiteInterp',
                      'ENP', 'SIZE', 'SetSplitting', 'GapETH', 'NSETH']
FAMILY_DIR = 'lean/OAI/Algorithms/SubexponentialSAT'


def read_lines(path):
    with open(path, encoding='utf-8') as f:
        return f.read().split('\n')


def page_of(lines, lineno):
    """Page of paper.pdf = form feeds strictly before the line + 1 (form feeds on
    the line itself open the next page, so a line that starts with one is on it)."""
    ff = sum(l.count('\f') for l in lines[:lineno - 1])
    ff += lines[lineno - 1].count('\f')
    return ff + 1


def check_fragments(lines, a, b, fragments, label):
    block = '\n'.join(lines[a - 1:b])
    ok = True
    for frag in fragments:
        if frag not in block:
            print(f'  FAIL {label}: fragment not found in lines {a}-{b}: {frag!r}')
            ok = False
    return ok


def main():
    check_only = '--check' in sys.argv
    failures = 0

    # 1. The manuscript.
    paper = read_lines(PAPER_TXT)
    ffs = sum(l.count('\f') for l in paper)
    print(f'paper.txt: {len(paper)} lines, {ffs} form feeds (paper.pdf has 67 pages; the last form feed closes page 67)')
    print('\n== manuscript claims (page of paper.pdf; lines of paper.txt) ==')
    rows = []
    for key, claim, a, b, pages, frags, status, why in CLAIMS:
        pa, pb = page_of(paper, a), page_of(paper, b)
        got = tuple(sorted({pa, pb}))
        ok = check_fragments(paper, a, b, frags, key)
        if got != tuple(pages):
            print(f'  FAIL {key}: expected page(s) {pages}, computed {got}')
            ok = False
        if not ok:
            failures += 1
        where = f'p.~{pa}' if pa == pb else f'pp.~{pa}--{pb}'
        where += f', {a}--{b}' if a != b else f', {a}'
        print(f'  {"ok  " if ok else "FAIL"} {key:16s} {where:18s} {status}')
        rows.append((claim, where, status, why))

    # 2. The clone, read only.
    print(f'\n== Lean facts (clone at {CLONE}, expected commit {CLONE_COMMIT}) ==')
    head_path = os.path.join(CLONE, '.git', 'HEAD')
    try:
        head = open(head_path, encoding='utf-8').read().strip()
        if head.startswith('ref: '):
            head = open(os.path.join(CLONE, '.git', head[5:]), encoding='utf-8').read().strip()
        print(f'  HEAD {head[:12]} {"ok" if head.startswith(CLONE_COMMIT) else "FAIL: not " + CLONE_COMMIT}')
        if not head.startswith(CLONE_COMMIT):
            failures += 1
    except OSError as e:
        print(f'  (could not read HEAD: {e})')
    for key, rel, a, b, frags in LEAN:
        path = os.path.join(CLONE, rel)
        try:
            lines = read_lines(path)
        except OSError as e:
            print(f'  FAIL {key}: {e}')
            failures += 1
            continue
        ok = check_fragments(lines, a, b, frags, key)
        if not ok:
            failures += 1
        print(f'  {"ok  " if ok else "FAIL"} {key:20s} {rel}:{a}' + (f'--{b}' if b != a else ''))

    # 3. Absence: no corollary or tensor-network identifier anywhere in the family.
    fam = os.path.join(CLONE, FAMILY_DIR)
    n_files, hits = 0, {}
    for dirpath, _, files in os.walk(fam):
        for fn in files:
            if not fn.endswith('.lean'):
                continue
            n_files += 1
            try:
                text = open(os.path.join(dirpath, fn), encoding='utf-8').read()
            except OSError:
                continue
            for ident in ABSENT_IDENTIFIERS:
                # whole-word match, as an identifier
                import re
                if re.search(r'\b' + re.escape(ident) + r'\b', text):
                    hits.setdefault(ident, []).append(os.path.relpath(os.path.join(dirpath, fn), CLONE))
    print(f'\n== identifier search over {n_files} .lean files under {FAMILY_DIR} ==')
    if hits:
        for ident, files in hits.items():
            print(f'  FAIL {ident}: found in {files[:3]}')
        failures += 1
    else:
        print(f'  ok   none of {ABSENT_IDENTIFIERS} occurs as an identifier')

    # 4. Where the strings ETH / SETH occur outside the family (and whether in the closure).
    eth_files = []
    import re
    for dirpath, _, files in os.walk(os.path.join(CLONE, 'lean')):
        if '.lake' in dirpath:
            continue
        for fn in files:
            if not fn.endswith('.lean'):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, CLONE)
            if rel.startswith(FAMILY_DIR):
                continue
            try:
                text = open(p, encoding='utf-8').read()
            except OSError:
                continue
            if re.search(r'\b(ETH|SETH)\b', text):
                eth_files.append(rel)
    closure = set(json.load(open(CLOSURE, encoding='utf-8')))
    print(f'\n== files outside the family whose text contains ETH or SETH ==')
    for rel in sorted(eth_files):
        mod = rel[len('lean/'):-len('.lean')].replace('/', '.')
        print(f'  {rel}  in closure: {mod in closure}')
    if not eth_files:
        print('  none')

    # 4b. Where the word ETH occurs inside the family (item 10, after the refuter):
    #     comments only, plus the theorem name exact_count_eth; SETH nowhere.
    fam_eth_lines, fam_eth_files, fam_seth = [], set(), 0
    for dirpath, _, files in os.walk(os.path.join(CLONE, FAMILY_DIR)):
        for fn in files:
            if not fn.endswith('.lean'):
                continue
            p = os.path.join(dirpath, fn)
            rel = os.path.relpath(p, CLONE)
            for i, line in enumerate(open(p, encoding='utf-8'), 1):
                if re.search(r'\bSETH\b', line):
                    fam_seth += 1
                if re.search(r'\bETH\b', line):
                    fam_eth_lines.append((rel, i, line.rstrip()))
                    fam_eth_files.add(rel)
    print(f'\n== lines inside the family whose text contains the word ETH ==')
    for rel, i, line in sorted(fam_eth_lines):
        print(f'  {rel}:{i}: {line[:90]}')
    decl = re.compile(r'^\s*(theorem|lemma|def|abbrev|structure|inductive|instance)\b')
    all_comments = all(not decl.match(line) for _, _, line in fam_eth_lines)
    final_rel = FAMILY_DIR + '/SqrtLogSpace/Final.lean'
    has_eth_name = 'exact_count_eth' in open(os.path.join(CLONE, final_rel), encoding='utf-8').read()
    if (len(fam_eth_lines) == 6 and len(fam_eth_files) == 5 and all_comments
            and fam_seth == 0 and (final_rel, 6) in [(r, i) for r, i, _ in fam_eth_lines] and has_eth_name):
        print('  ok   six comment lines in five files (Final.lean line 6 among them), SETH nowhere, exact_count_eth present')
    else:
        print(f'  FAIL lines={len(fam_eth_lines)} files={len(fam_eth_files)} comments={all_comments} seth={fam_seth} name={has_eth_name}')
        failures += 1

    # 5. The three exponents relative to n, at constant 1.
    def r_ver(n):
        y = math.log(n + 16.0)
        return math.log(y) ** 2 / math.sqrt(y)

    def r_gen(n):
        y = math.log(n)
        return math.log(y) / math.sqrt(y)

    def r_den(n):
        return 1.0 / math.sqrt(math.log(n))

    sizes = [(20, '20'), (50, '50'), (125, '125'), (1e3, '10^{3}'),
             (math.exp(math.e ** 2), 'e^{e^{2}} \\approx 1{,}618'), (1e6, '10^{6}'), (10 ** 23.7, '10^{23.7}')]
    print('\n== exponent / n at constant 1 ==')
    print(f'  {"n":>22s} {"verified":>9s} {"general":>9s} {"density":>9s}')
    exp_rows = []
    for n, label in sizes:
        v, g, d = r_ver(n), r_gen(n), r_den(n)
        print(f'  {label:>22s} {v:9.4f} {g:9.4f} {d:9.4f}')
        exp_rows.append((label, v, g, d))
    gen_peak_n = math.exp(math.e ** 2)
    print(f'  general exponent peaks at ln n = e^2, n = e^(e^2) = {gen_peak_n:.1f}, value 2/e = {2 / math.e:.4f}')
    print(f'  density exponent is decreasing in n; at n = 20 it is {r_den(20):.4f}')
    if not (r_gen(gen_peak_n) < 1 and max(r_gen(n) for n, _ in sizes) < 1 and r_ver(50) > 1):
        print('  FAIL: expected the two paper-only exponents below n at constant 1 and the verified one above n at 50')
        failures += 1

    # 6. Tables.
    if not check_only:
        os.makedirs(TABLES, exist_ok=True)
        with open(os.path.join(TABLES, 'beyond_claims.tex'), 'w', encoding='utf-8') as f:
            f.write('% generated by python3 -I paper3/scripts/beyond_claims.py; do not edit\n')
            f.write('\\begin{tabularx}{\\linewidth}{@{}>{\\raggedright\\arraybackslash}p{0.33\\linewidth}'
                    '>{\\raggedright\\arraybackslash}p{0.10\\linewidth}'
                    '>{\\raggedright\\arraybackslash}p{0.10\\linewidth}X@{}}\n')
            f.write('\\toprule\nclaim & stated & status & why \\\\\n\\midrule\n')
            for claim, where, status, why in rows:
                f.write(f'{claim} & {where} & {status} & {why} \\\\\n')
            f.write('\\bottomrule\n\\end{tabularx}\n')
        with open(os.path.join(TABLES, 'beyond_exponents.tex'), 'w', encoding='utf-8') as f:
            f.write('% generated by python3 -I paper3/scripts/beyond_claims.py; do not edit\n')
            f.write('\\begin{tabular}{@{}lrrr@{}}\n\\toprule\n')
            f.write('$n$ & verified $\\rhon/n$ & general $\\ln\\ln n/\\sqrt{\\ln n}$ & density $1/\\sqrt{\\ln n}$ \\\\\n\\midrule\n')
            for label, v, g, d in exp_rows:
                f.write(f'${label}$ & {v:.3f} & {g:.3f} & {d:.3f} \\\\\n')
            f.write('\\bottomrule\n\\end{tabular}\n')
        print(f'\nwrote {TABLES}/beyond_claims.tex and beyond_exponents.tex')

    print(f'\n{"ALL CHECKS PASSED" if failures == 0 else str(failures) + " CHECK(S) FAILED"}')
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
