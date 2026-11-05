#!/usr/bin/env python3
"""Section 6 of paper 3: what follows, in general terms -- the hypotheses the
verified statement refutes, and what a lower bound derived from them loses.

Regenerates every location Section 6 cites and fails loudly if any has drifted:

  * for each hypothesis the manuscript's §1.1.1 / §1.1.2 states (ETH, SETH,
    Gap-ETH and its randomised form, NSETH, #ETH, the randomised ETH and SETH
    it names by citation), the page of paper.pdf and the line range of the
    committed extract reports/scratch/eth_audit/paper.txt (page = form feeds
    before the line + 1), with a quoted fragment that must occur in that range,
    and the bracket key of the manuscript's own source for it;
  * the manuscript's refutation paragraph (p. 4, lines 187-191), its #ETH
    sentence (p. 5, lines 211-212), its §1.1.3 sentences on what the
    refutation removes and what it does not touch (p. 5, lines 226-227,
    229-236), the transfer caveat (p. 2, lines 95-99) and the one positive
    transfer (p. 5, lines 237-243);
  * the manuscript's bibliography entries the paper's refs.bib copies for the
    hypotheses' sources (lines 3686-3811 of the extract), so that every entry
    added by item 05 has a located origin;
  * the comparator lines Section 6 relies on (the answer bit, the count tape,
    the time bound, the width predicate), read from the clone at commit
    4eaee875 with open() only; nothing of the clone is imported or run;
  * two arithmetic facts used in the text: the number of clauses of width at
    most k over n variables is at most sum_{j<=k} C(2n, j), so L is polynomial
    in n alone (the values at n = 125, k = 3 and at n = 1000, k = 3), and
    rho(n)/n -> 0 (the value at a few n, from the same formula as
    runtime_scale.py).

Writes paper3/latex/tables/hypotheses.tex (Table 6.1: hypothesis, where the
manuscript states it, its source, the quantifier form, what in the verified
statement negates it).

Run:  python3 -I paper3/scripts/consequences.py           (from the repository root)
      python3 -I paper3/scripts/consequences.py --check   (verify only, write nothing)
Exit status is non-zero if any fragment, page or line has moved.
"""
import math
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..'))
PAPER_TXT = os.path.join(ROOT, 'reports', 'scratch', 'eth_audit', 'paper.txt')
CLONE = os.path.expanduser('~/dev/untrusted/openai-math')
CLONE_COMMIT = '4eaee875'
CHALLENGE = os.path.join(CLONE, 'lean', 'ComparatorChallenges', 'SubexponentialSAT.lean')
TABLES = os.path.join(ROOT, 'paper3', 'latex', 'tables')

# --------------------------------------------------------------------------
# The hypotheses, as the manuscript states them. (key, name, first line, last
# line, expected page, fragments, the manuscript's bracket key(s), quantifier
# form as printed in the table, what in the verified statement negates it.)
# --------------------------------------------------------------------------
HYPOTHESES = [
    ('eth', 'ETH', 165, 166, 4,
     ['The Exponential Time Hypothesis (ETH) asserted that 3-SAT requires', 'deterministic time'],
     '[IP01, Theorem 1]',
     '$\\exists\\,\\delta > 0$: no deterministic $2^{\\delta n}\\,\\mathrm{poly}$ algorithm decides 3-SAT',
     'the answer bit at $k = 3$: deterministic, $2^{A\\rhon}\\,\\mathrm{poly}$, $\\rhon = o(n)$'),
    ('seth', 'SETH', 166, 169, 4,
     ['The Strong', 'Exponential Time Hypothesis (SETH)', 'for every ε ∈ (0, 1), there is a fixed k for which no deterministic algorithm'],
     '[IP01, Open Problems, item 2]',
     '$\\forall\\,\\varepsilon \\in (0,1)\\ \\exists\\,k$: no deterministic $2^{(1-\\varepsilon)n}(n+m)^{O(1)}$ algorithm for $k$-SAT',
     'the answer bit at every $k$: for each $k$, $A_k\\rhon \\le (1-\\varepsilon)n$ for all large $n$'),
    ('gap-eth', 'Gap-ETH', 172, 174, 4,
     ['The Gap Exponential Time Hypothesis (Gap-ETH) strengthens ETH by postulating constants', 'even when m = O(n)'],
     '[Din16, MR17]',
     '$\\exists\\,\\delta,\\gamma > 0$: no $O(2^{\\gamma n})$ algorithm separates satisfiable 3-CNFs from $\\delta$-far ones, even at $m = O(n)$',
     'exact decision separates the two cases; at $m = O(n)$ the bound is $2^{A\\rhon}\\,\\mathrm{poly}(n) = O(2^{\\gamma n})$ for every $\\gamma$'),
    ('gap-eth-rand', 'randomised Gap-ETH', 175, 176, 4,
     ['The randomized version rules out an algorithm with the same running time that distinguishes', 'probability at least 2/3'],
     '[CCK+ 20, Conjecture 2.5]',
     'as Gap-ETH, for algorithms correct with probability $\\ge 2/3$ on every promised input',
     'a deterministic algorithm is correct with probability $1$'),
    ('nseth', 'NSETH', 181, 183, 4,
     ['The Nondeterministic Strong Exponential Time Hypothesis (NSETH) asserts that, for every ε > 0', 'nondeterministic', 'unsatisfiable'],
     '[CGI+ 16]',
     '$\\forall\\,\\varepsilon > 0\\ \\exists\\,k$: no nondeterministic $2^{(1-\\varepsilon)n}(n+m)^{O(1)}$ algorithm decides $k$-UNSAT',
     'the answer bit is \\texttt{false} iff $\\mathtt{count}\\,F = 0$; a deterministic machine is a nondeterministic one with no guess'),
    ('eth-rand', 'randomised ETH', 190, 190, 4,
     ['bounded-error randomized versions of ETH [DHM+ 14, Section 1]'],
     '[DHM+ 14, Section 1]',
     'ETH for bounded-error randomised algorithms',
     'a deterministic algorithm is a bounded-error randomised one with error $0$'),
    ('seth-rand', 'randomised SETH', 190, 191, 4,
     ['SETH [CDL+ 16, Definition 2.1]'],
     '[CDL+ 16, Definition 2.1]',
     'SETH for bounded-error randomised algorithms',
     'as above'),
    ('sharp-eth', '\\#ETH', 204, 205, 4,
     ['The counting Exponential Time Hypothesis (#ETH) asserted that exactly counting the satisfying', 'deterministic time'],
     '[DHM+ 14, Section 1]',
     '$\\exists\\,\\delta > 0$: no deterministic $2^{\\delta n}$ algorithm counts the satisfying assignments of a 3-CNF',
     'the count tape at $k = 3$ holds $\\mathtt{countWord}\\,(\\mathtt{count}\\,F)$ within the same bound'),
]

# The manuscript's sentences Section 6 quotes. (key, first, last, page, fragments)
QUOTES = [
    ('refutes', 187, 191, 4,
     ['Theorem 1.1 refutes ETH, SETH, Gap-ETH, and NSETH. Indeed, testing whether the exact count',
      'deciding satisfiability also solves the Gap-ETH promise problem',
      'and of Gap-ETH.']),
    ('refutes-context', 191, 194, 4,
     ['It does not conflict with unconditional exponential',
      'lower bounds for restricted proof systems such as regular resolution [BI13]',
      'Merlin–Arthur version of SETH (MA-SETH)']),
    ('sharp-eth-refuted', 211, 212, 5,
     ['Our algorithm (Theorem 1.1) solves #3-SAT', 'deterministically in 2o(n) poly(n, m) time and therefore refutes #ETH.']),
    ('eth-implies-kSAT', 165, 166, 4,
     ['and hence so does k-SAT for every fixed k ⩾ 3 [IP01, Theorem 1]']),
    ('seth-motivation', 169, 171, 4,
     ['The running-time bounds for Schöning’s algorithm and', 'PPSZ helped motivate this prediction']),
    ('removes-one-basis', 226, 227, 5,
     ['Our refutation of ETH and SETH removes one basis for the hardness claims above. Some',
      'of the same lower bounds follow from weaker hypotheses that may still hold.']),
    ('ovc', 229, 232, 5,
     ['OVC asserts that for every fixed ε > 0, no',
      'contain an orthogonal pair, one vector from each set. The reduction from SAT to Orthogonal',
      'Vectors shows that SETH implies OVC [Wil05, VW19].']),
    ('unrestricted', 233, 236, 5,
     ['also follow from the hypothesis that unrestricted CNF-SAT admits no 2(1−δ)n poly(n, m)-time',
      'algorithm for any constant δ > 0 [Bri14, RV13, LMS18]. Theorem 1.1 gives a running-time guarantee',
      'for each fixed clause width k, while this hypothesis allows the width to grow with n.']),
    ('transfer-caveat', 95, 99, 2,
     ['Note that runtime bounds of the form 2o(n) do not transfer under general polynomial-time',
      'reductions', 'would be needed for this), so our result does not imply that general NP problems',
      'admit subexponential time algorithms.']),
    ('other-direction', 237, 238, 5,
     ['To obtain a faster algorithm for a target problem from our SAT algorithm, we need a reduction in',
      'the other direction, from that problem to fixed-width SAT, that controls the number of variables.']),
    ('set-splitting', 239, 243, 5,
     ['Set Splitting with sets of size at most k has such a reduction [CDL+ 16, Observation 3.6]',
      'has one variable per universe element, so for fixed k Theorem 1.1 gives subexponential time in the',
      'universe size, up to a polynomial input-size factor.']),
    ('fine-grained-list', 213, 225, 5,
     ['1.1.3. Implications for fine-grained complexity. ETH and SETH became standard assumptions for',
      'common basis for explaining the apparent optimality of algorithms across quite different problems.']),
    ('abstract-eth', 10, 11, 1,
     ['refutes the Exponential Time Hypothesis (ETH), which postulates that deciding 3-SAT on n variables',
      'time in the worst case.']),
    ('n-ge-20', 56, 57, 2,
     ['Theorem 1.1. For each fixed k ⩾ 2, there exists a deterministic algorithm that, given a k-CNF F',
      'on n ⩾ 20 declared variables']),
]

# The manuscript's bibliography entries refs.bib copies (key, first line, page, fragment).
BIB = [
    ('CGI+16', 3686, ['[CGI+ 16] Marco L. Carmosino, Jiawei Gao, Russell Impagliazzo, Ivan Mihajlin, Ramamohan Paturi, and Stefan',
                      'Nondeterministic Extensions of the Strong Exponential Time Hypothesis and Consequences for',
                      'Non-reducibility. 7th Innovations in Theoretical Computer Science Conference, 2016, 261–270.']),
    ('CCK+20', 3689, ['[CCK+ 20] Parinya Chalermsook, Marek Cygan, Guy Kortsarz, Bundit Laekhanukit, Pasin Manurangsi, Danupon',
                      'Nanongkai, and Luca Trevisan. From Gap-Exponential Time Hypothesis to Fixed Parameter Tractable',
                      'Inapproximability: Clique, Dominating Set, and More. SIAM Journal on Computing 49(4), 2020, 772–810.']),
    ('CDL+16', 3705, ['[CDL+ 16] Marek Cygan, Holger Dell, Daniel Lokshtanov, Dániel Marx, Jesper Nederlof, Yoshio Okamoto, Ramamohan',
                      'Paturi, Saket Saurabh, and Magnus Wahlström. On Problems as Hard as CNF-SAT . ACM Transactions',
                      'on Algorithms 12(3), Article 41, 2016, 1–24.']),
    ('DHM+14', 3708, ['[DHM+ 14] Holger Dell, Thore Husfeldt, Dániel Marx, Nina Taslaman, and Martin Wahlén. Exponential Time',
                      'Complexity of the Permanent and the Tutte Polynomial . ACM Transactions on Algorithms 10(4), Article 21,',
                      '2014, 1–32.']),
    ('Din16', 3711, ['[Din16]   Irit Dinur. Mildly Exponential Reduction from Gap 3SAT to Polynomial-Gap Label-Cover . Electronic',
                     'Colloquium on Computational Complexity, Report TR16-128, 2016.']),
    ('IP01', 3733, ['[IP01]   Russell Impagliazzo and Ramamohan Paturi. On the Complexity of k-SAT . Journal of Computer and',
                    'System Sciences 62(2), 2001, 367–375.']),
    ('IPZ01', 3735, ['[IPZ01]  Russell Impagliazzo, Ramamohan Paturi, and Francis Zane. Which Problems Have Strongly Exponential',
                     'Complexity? Journal of Computer and System Sciences 63(4), 2001, 512–530.']),
    ('MR17', 3759, ['[MR17]   Pasin Manurangsi and Prasad Raghavendra. A Birthday Repetition Theorem and Complexity of Approxi-',
                    'mating Dense CSPs. 44th International Colloquium on Automata, Languages, and Programming, LIPIcs',
                    '80, 2017, 78:1–78:15.']),
    ('Wil16', 3810, ['[Wil16]   Richard Ryan Williams. Strong ETH Breaks With Merlin and Arthur: Short Non-Interactive Proofs of',
                     'Batch Evaluation. 31st Conference on Computational Complexity, LIPIcs 50, 2016, 2:1–2:17.']),
]

# Comparator lines Section 6 relies on (line, fragment); clone at 4eaee875.
CHALLENGE_LINES = [
    (38, 'WidthAtMost'),
    (47, 'count'),
    (132, 'runtimeScale'),
    (147, 'countWord'),
    (194, 'theorem exact_count_and_sat'),
    (194, '2 ≤ k'),
    (203, 'countTape'),
    (205, 'answerTape'),
    (206, '0 < SAT.count F'),
    (207, 'Sum.inl (decide (0 < SAT.count F))'),
    (210, '(time : ℝ) ≤'),
    (210, 'runtimeBound C A d'),
    (211, 'formulaBitLength F) n'),
]


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


def check_page(lines, a, b, page, label):
    pa, pb = page_of(lines, a), page_of(lines, b)
    if pa != page or pb != page:
        print(f'  FAIL {label}: lines {a}-{b} are on pages {pa}-{pb}, expected {page}')
        return False
    return True


def rho_over_n(n):
    y = math.log(n + 16)
    return math.log(y) ** 2 / math.sqrt(y)


def clauses_at_most(n, k):
    return sum(math.comb(2 * n, j) for j in range(k + 1))


def main():
    check_only = '--check' in sys.argv
    failures = 0

    paper = read_lines(PAPER_TXT)
    print(f'paper.txt: {len(paper)} lines')

    print('\n1. The hypotheses, as the manuscript states them (page, lines, fragments):')
    table_rows = []
    for key, name, a, b, page, frags, src, form, negated in HYPOTHESES:
        ok = check_page(paper, a, b, page, key) & check_fragments(paper, a, b, frags, key)
        print(f'  {"ok  " if ok else "FAIL"} {name:<20} p. {page}, lines {a}-{b}, source {src}')
        failures += 0 if ok else 1
        where = f'p.~{page}, {a}' if a == b else f'p.~{page}, {a}--{b}'
        table_rows.append((name, where, src, form, negated))

    print('\n2. The sentences Section 6 quotes:')
    for key, a, b, page, frags in QUOTES:
        ok = check_page(paper, a, b, page, key) & check_fragments(paper, a, b, frags, key)
        print(f'  {"ok  " if ok else "FAIL"} {key:<22} p. {page}, lines {a}-{b}')
        failures += 0 if ok else 1

    print('\n3. The bibliography entries refs.bib copies from the manuscript:')
    for key, a, frags in BIB:
        ok = check_fragments(paper, a, a + 2, frags, key)
        pg = page_of(paper, a)
        print(f'  {"ok  " if ok else "FAIL"} {key:<8} lines {a}-{a + 2} (p. {pg})')
        failures += 0 if ok else 1

    print(f'\n4. The comparator file (clone at {CLONE_COMMIT}, read with open() only):')
    if os.path.exists(CHALLENGE):
        ch = read_lines(CHALLENGE)
        for ln, frag in CHALLENGE_LINES:
            ok = ln <= len(ch) and frag in ch[ln - 1]
            print(f'  {"ok  " if ok else "FAIL"} line {ln:<4} {frag!r}')
            failures += 0 if ok else 1
    else:
        print(f'  (clone not present at {CLONE}; comparator lines not checked)')

    print('\n5. Arithmetic used in the text:')
    for n, k in [(125, 3), (1000, 3), (125, 4)]:
        print(f'  clauses of width <= {k} over {n} variables: at most {clauses_at_most(n, k):,}')
    for n in [50, 125, 1000, 10 ** 6]:
        print(f'  rho({n})/{n} = {rho_over_n(n):.4f}')
    # rho(n)/n -> 0: the value at ln(n+16) = 10^6 (n far beyond any integer written down).
    y = 1e6
    print(f'  (ln y)^2/sqrt(y) at y = ln(n+16) = 1e6: {math.log(y) ** 2 / math.sqrt(y):.4f}')

    if not check_only:
        os.makedirs(TABLES, exist_ok=True)
        path = os.path.join(TABLES, 'hypotheses.tex')
        with open(path, 'w', encoding='utf-8') as f:
            f.write('% generated by python3 -I paper3/scripts/consequences.py; do not edit\n')
            f.write('\\begin{tabularx}{\\linewidth}{@{}>{\\raggedright\\arraybackslash}p{0.11\\linewidth}'
                    '>{\\raggedright\\arraybackslash}p{0.09\\linewidth}'
                    '>{\\raggedright\\arraybackslash}p{0.12\\linewidth}'
                    '>{\\raggedright\\arraybackslash}X'
                    '>{\\raggedright\\arraybackslash}X@{}}\n')
            f.write('\\toprule\nhypothesis & stated & source & form & negated by \\\\\n\\midrule\n')
            for name, where, src, form, negated in table_rows:
                src_tex = src.replace('#', '\\#').replace('+ ', '+').replace('[', '').replace(']', '')
                f.write(f'{name} & {where} & {src_tex} & {form} & {negated} \\\\\n')
            f.write('\\bottomrule\n\\end{tabularx}\n')
        print(f'\nwrote {path}')

    print(f'\n{"ALL CHECKS PASSED" if failures == 0 else str(failures) + " CHECK(S) FAILED"}')
    return 0 if failures == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
