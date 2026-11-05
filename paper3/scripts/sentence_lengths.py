#!/usr/bin/env python3
"""Sentence lengths of paper 3's LaTeX sections (item 12, 2026-11-05).

Crude and stated as such: LaTeX commands, maths and comments are stripped,
the text is split at a full stop, question or exclamation mark followed by
white space and a capital letter or an opening bracket, and words are
counted on white space. Table rows, list items, captions and quotations
are not separated out, so a long "sentence" here may be one of those.
The numbers are for the plain-English rule's bookkeeping only; nothing in
the paper's text cites them.

Usage:
  python3 -I paper3/scripts/sentence_lengths.py            # working tree
  python3 -I paper3/scripts/sentence_lengths.py --ref 66a755ac2   # a commit
  python3 -I paper3/scripts/sentence_lengths.py --list 45  # list sentences over 45 words
Run from the repository root.
"""
import glob, re, subprocess, sys

ROOT = 'paper3/latex'

def strip(t):
    t = re.sub(r'(?<!\\)%.*', '', t)
    t = re.sub(r'\\(label|ref|cite[pt]?|leanref|eqref|input|include)\*?\{[^}]*\}', ' ', t)
    t = re.sub(r'\\(repofile|clonefile|leannames|path|texttt|emph|textit|textbf|url)\{([^}]*)\}', r'\2', t)
    t = re.sub(r'\$[^$]*\$', 'X', t)
    t = re.sub(r'\\[a-zA-Z]+\*?(\[[^\]]*\])?', ' ', t)
    t = re.sub(r'[{}]', '', t)
    return t

def sentences(text):
    out = []
    lines = text.split('\n'); cur = []; start = 1
    paras = []
    for i, l in enumerate(lines, 1):
        if l.strip() == '':
            if cur: paras.append((start, ' '.join(cur))); cur = []
        else:
            if not cur: start = i
            cur.append(l)
    if cur: paras.append((start, ' '.join(cur)))
    for st, p in paras:
        for se in re.split(r'(?<=[.!?])\s+(?=[A-Z\(`])', strip(p)):
            w = len(se.split())
            if w: out.append((st, w, se))
    return out

def load(f, ref):
    if ref is None:
        return open(f).read()
    return subprocess.run(['git', 'show', f'{ref}:{f}'], capture_output=True, text=True).stdout

def main():
    ref = None; lst = None
    a = sys.argv[1:]
    if '--ref' in a: ref = a[a.index('--ref') + 1]
    if '--list' in a: lst = int(a[a.index('--list') + 1])
    files = sorted(glob.glob(f'{ROOT}/sec*.tex'))
    tot = [0, 0, 0, 0]
    print(f"{'file':34} {'sent':>5} {'mean':>6} {'>45':>4} {'>58':>4}")
    for f in files:
        ss = sentences(load(f, ref))
        n = len(ss); words = sum(w for _, w, _ in ss)
        o45 = sum(1 for _, w, _ in ss if w > 45); o58 = sum(1 for _, w, _ in ss if w > 58)
        tot[0] += n; tot[1] += words; tot[2] += o45; tot[3] += o58
        print(f"{f.split('/')[-1]:34} {n:5d} {words/n:6.1f} {o45:4d} {o58:4d}")
        if lst:
            for st, w, se in ss:
                if w > lst: print(f"    line {st} [{w}] {se}")
    print(f"{'all':34} {tot[0]:5d} {tot[1]/tot[0]:6.1f} {tot[2]:4d} {tot[3]:4d}")

if __name__ == '__main__':
    main()
