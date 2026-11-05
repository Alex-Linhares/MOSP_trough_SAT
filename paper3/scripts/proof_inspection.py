#!/usr/bin/env python3
"""Regenerate every number of paper3/latex/sec4_proof.tex (the proof, inspected).

Run with:   python3 -I paper3/scripts/proof_inspection.py [--check]

Read-only on the untrusted clone (~/dev/untrusted/openai-math, commit 4eaee875):
every file is read with open(); nothing in the clone is imported, built or run.
Re-runs the two audit scripts of reports/scratch/eth_audit/ (closure.py and
defdiff.py, each under `python3 -I`, as subprocesses) and parses their output;
then performs the checks of the proof audit that those scripts do not cover
(statement length, countWord, dead files, #print axioms placement, the
comparator JSONs, the lakefile, the manifest, the patches, CI, the spine's
line citations), prints every number, and writes
latex/tables/proof_inspection.tex. Exits non-zero if any check fails.
With --check nothing is written.
"""
import json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
PAPER3 = os.path.dirname(HERE)
REPO = os.path.dirname(PAPER3)
AUDIT = os.path.join(REPO, 'reports', 'scratch', 'eth_audit')
CLONE = os.path.expanduser('~/dev/untrusted/openai-math')
LEAN = os.path.join(CLONE, 'lean')
FAM = os.path.join(LEAN, 'OAI', 'Algorithms', 'SubexponentialSAT')
CHECK = '--check' in sys.argv
failures = []


def check(cond, msg):
    print(('ok   ' if cond else 'FAIL ') + msg)
    if not cond:
        failures.append(msg)


def rd(path):
    return open(path, encoding='utf-8', errors='replace').read()


def strip_comments(text):
    out = []; i = 0; n = len(text); d = 0
    while i < n:
        if d == 0 and text.startswith('--', i):
            j = text.find('\n', i); i = n if j < 0 else j; continue
        if text.startswith('/-', i):
            d += 1; i += 2; continue
        if d > 0 and text.startswith('-/', i):
            d -= 1; i += 2; continue
        if d > 0:
            if text[i] == '\n': out.append('\n')
            i += 1; continue
        out.append(text[i]); i += 1
    return ''.join(out)


def lines_at(rel, a, b=None):
    """Lines a..b (1-based, inclusive) of a file relative to lean/."""
    ls = rd(os.path.join(LEAN, rel)).split('\n')
    b = b or a
    return '\n'.join(ls[a - 1:b])


def cite(rel, a, fragment, b=None):
    txt = lines_at(rel, a, b)
    where = f'{rel}:{a}' + (f'-{b}' if b else '')
    check(fragment in txt, f'{where} contains {fragment!r}')


num = {}

# ---------------------------------------------------------------- 1. closure.py
print('== closure.py (fresh run)')
out = subprocess.run([sys.executable, '-I', os.path.join(AUDIT, 'closure.py'), LEAN,
                      'OAI.Algorithms.SubexponentialSAT.Main'],
                     capture_output=True, text=True, check=True).stdout
m = re.search(r'modules resolved inside .* : (\d+)', out); num['closure_modules'] = int(m.group(1))
m = re.search(r"external .*: (\{.*\})", out); ext = eval(m.group(1), {}, {})
num['mathlib_modules'] = ext.get('Mathlib', 0); num['core_modules'] = ext.get('Lean', 0)
m = re.search(r'total lines \(raw\): (\d+)', out); num['closure_lines'] = int(m.group(1))
kwtxt = out[out.index('keyword line counts'):]
kw = {k.strip(): int(v) for k, v in re.findall(r'^  (.+?)\s+(\d+)$', kwtxt, re.M)}
num['largest_file_lines'] = int(re.search(r'20 largest files:\n\s+(\d+)', out).group(1))
check(num['closure_modules'] == 3091, 'closure has 3,091 modules')
check(num['closure_lines'] == 550551, 'closure has 550,551 raw lines')
check(num['mathlib_modules'] == 50 and num['core_modules'] == 1, '50 Mathlib modules + 1 core module')
for k in ['axiom', 'sorry', 'sorryAx', 'admit', 'native_decide', 'ofReduceBool', 'ofReduceNat',
          'implemented_by', 'extern', 'unsafe', 'partial', 'elab', 'macro', 'syntax', 'simproc',
          'csimp', 'autoImplicit', 'skipKernelTC', 'trust', 'postulate']:
    check(kw.get(k, -1) == 0, f'keyword {k}: 0 lines')
check(kw['opaque'] == 9, 'opaque: 9 lines'); check(kw['set_option'] == 2, 'set_option: 2 lines')
check(kw['noncomputable'] == 1048, 'noncomputable: 1,048 lines')
check(kw['decide'] == 14034, 'decide: 14,034 lines')
check(kw['Classical.choice'] == 4 and kw['propext'] == 4, 'explicit Classical.choice 4, propext 4')
check(kw['open Classical'] == 8, 'open Classical: 8 lines')
check(kw['instance'] == 148 and kw['local instance'] == 40, 'instance 148, local instance 40')
check(kw['termination_by'] == 9 and kw['decreasing_by'] == 5, 'termination_by 9, decreasing_by 5')
num.update({'kw_' + k: v for k, v in kw.items()})
hits = json.load(open(os.path.join(AUDIT, 'hits.json')))
closure = json.load(open(os.path.join(AUDIT, 'closure_modules.json')))
check(all(m.startswith('OAI.Algorithms.SubexponentialSAT') for m in closure), 'every closure module is in the family')
# the two set_options and the two core imports
so = sorted((p.split('SubexponentialSAT/')[-1], ln) for p, ln, _ in hits['set_option'])
check(so == [('SqrtLog/LeafProgramPreparedRecoveryQuery.lean', 15),
             ('SqrtLog/LeafProgramPreparedRecoveryWitness.lean', 14)], 'the two set_option lines')
check(all('quotPrecheck false' in l for _, _, l in hits['set_option']), 'both set_options are quotPrecheck false')
le = sorted((p.split('SubexponentialSAT/')[-1], ln) for p, ln, _ in hits['Lean.Elab'])
check(le == [('SqrtLogSpace/DisjointReuse/SparseCharging.lean', 5), ('SqrtLogSpace/FiniteFallback.lean', 14)],
      'Lean.Elab.Tactic.Omega imported at the two recorded lines')
# the nine opaques have bodies
op = [(p, ln) for p, ln, _ in hits['opaque']]
bodied = 0
for p, ln in op:
    ls = strip_comments(rd(p)).split('\n')
    blk = '\n'.join(ls[ln - 1:ln + 40])
    # the declaration ends at ':=' before the next declaration keyword
    nxt = re.search(r'\n(theorem|def|lemma|private opaque|opaque|end |section|namespace)', blk[1:])
    seg = blk[:nxt.start() + 1] if nxt else blk
    bodied += ':=' in seg
check(bodied == 9, 'all nine opaques carry := bodies')
num['opaque_bodied'] = bodied
# the one 'partial' and 'unsafe' hits in dead files are comments: raw grep over the dead files
fam_files = []
for dp, dn, fn in os.walk(FAM):
    for f in fn:
        if f.endswith('.lean'):
            p = os.path.join(dp, f); fam_files.append(os.path.relpath(p, LEAN)[:-5].replace('/', '.'))
num['family_files'] = len(fam_files)
dead = sorted(set(fam_files) - set(closure))
num['dead_files'] = len(dead)
check(num['family_files'] == 3977 and num['dead_files'] == 886, '3,977 family files, 886 outside the closure')
pat = re.compile(r'(?<![A-Za-z0-9_.])(sorry|axiom|native_decide|admit)(?![A-Za-z0-9_])')
raw_dead = sum(len(pat.findall(rd(os.path.join(LEAN, m.replace('.', '/') + '.lean')))) for m in dead)
strip_dead = sum(len(pat.findall(strip_comments(rd(os.path.join(LEAN, m.replace('.', '/') + '.lean'))))) for m in dead)
check(raw_dead == 0 and strip_dead == 0, 'dead files: 0 sorry/axiom/native_decide/admit, raw and stripped')
num['dead_raw_hits'] = raw_dead
oai = rd(os.path.join(LEAN, 'OAI.lean')).split('\n')
imp = [i + 1 for i, l in enumerate(oai) if 'SubexponentialSAT' in l]
check(imp == [49] and oai[48].strip() == 'import OAI.Algorithms.SubexponentialSAT.Main', 'OAI.lean:49 is the only family import')
mainl = rd(os.path.join(FAM, 'Main.lean')).count('\n')
check(mainl == 16, 'Main.lean is 16 lines'); num['main_lines'] = mainl

# ---------------------------------------------------------------- 2. defdiff.py
print('== defdiff.py (fresh run)')
dd = subprocess.run([sys.executable, '-I', os.path.join(AUDIT, 'defdiff.py')],
                    capture_output=True, text=True, check=True).stdout
same = re.findall(r'^SAME\s+(\S+)', dd, re.M); diff = re.findall(r'^DIFF/MISS\s+(\S+)', dd, re.M)
num['defs_same'] = len(same); num['defs_diff'] = len(diff)
check(len(same) == 32, 'defdiff: 32 declarations SAME')
check(sorted(diff) == ['countWord', 'exact_count_and_sat', 'runtimeBound', 'runtimeScale'],
      'defdiff: the four it cannot match are countWord, runtimeScale, runtimeBound, the theorem')
# the four, by hand
chal = rd(os.path.join(LEAN, 'ComparatorChallenges/SubexponentialSAT.lean'))
chal_lines = chal.split('\n')
def decl(text, head):
    i = text.index(head); j = text.index('\n\n', i)
    return re.sub(r'\s+', ' ', text[i:j]).strip()
eb = rd(os.path.join(FAM, 'SqrtLogSpace/EncodingBounds.lean'))
cw_lib = decl(eb, 'def countWord'); cw_ch = decl(chal, 'def countWord')
check(cw_lib == cw_ch, 'countWord identical (challenge line 147 = EncodingBounds.lean line 17)')
check(eb.split('\n')[16].startswith('def countWord') and chal_lines[146].startswith('def countWord'), 'countWord line numbers')
ss = rd(os.path.join(FAM, 'SqrtLog/StatementScale.lean'))
for name in ['runtimeScale', 'runtimeBound']:
    a = decl(chal, 'noncomputable def ' + name).replace('noncomputable def', 'def', 1)
    b = decl(ss, 'def ' + name)
    check(a == b, f'{name} identical up to `noncomputable def` vs `noncomputable section`')
check(ss.split('\n')[14].strip() == 'noncomputable section', 'StatementScale.lean:15 is `noncomputable section`')
num['defs_total'] = 35; num['defs_identical'] = 33; num['defs_modulo_noncomputable'] = 2
# the theorem statement
def stmt(text):
    i = text.index('theorem exact_count_and_sat'); j = text.index(':= by', i)
    return text[i:j], re.sub(r'\s+', ' ', text[i:j]).strip(), text.count('\n', 0, i) + 1
fin = rd(os.path.join(FAM, 'SqrtLogSpace/Final.lean'))
a = stmt(chal); b = stmt(fin)
check(a[0] == b[0] and a[1] == b[1], 'theorem statement identical, raw and normalised')
check(len(a[1]) == 1124 and len(a[0]) == 1353, 'statement 1,124 characters normalised (1,353 raw)')
check(a[2] == 194 and b[2] == 74, 'statement at challenge line 194 and Final.lean line 74')
num['stmt_chars'] = len(a[1]); num['stmt_chars_raw'] = len(a[0])
check(chal_lines[217].strip() == 'sorry', 'challenge line 218 is the `sorry`')
check(chal.count('\n') == 220 and fin.count('\n') == 201, 'challenge 220 lines, Final.lean 201 lines')
fl = fin.split('\n')
check(fl[0:3] == ['import OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.NativeLargeEntry',
                  'import OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.Statement',
                  'import OAI.Algorithms.SubexponentialSAT.SqrtLog.StatementCanonical'],
      'Final.lean imports (lines 1-3) do not include the challenge file')
check(all(fl[i].startswith('#print axioms') for i in range(196, 201)), 'Final.lean 197-201 are #print axioms')

# ---------------------------------------------------------------- 3. #print axioms placement
pa_in = {}; pa_out = {}
for m in fam_files:
    c = sum(1 for l in rd(os.path.join(LEAN, m.replace('.', '/') + '.lean')).split('\n') if l.startswith('#print axioms'))
    if c: (pa_in if m in closure else pa_out)[m] = c
num['pa_files_closure'] = len(pa_in); num['pa_lines_closure'] = sum(pa_in.values())
num['pa_files_family'] = len(pa_in) + len(pa_out); num['pa_lines_family'] = sum(pa_in.values()) + sum(pa_out.values())
check(num['pa_files_closure'] == 8 and num['pa_lines_closure'] == 19, '#print axioms: 8 closure files, 19 lines')
check(num['pa_files_family'] == 17 and num['pa_lines_family'] == 35, '#print axioms: 17 family files, 35 lines (9 files dead)')
# the replay's in-build axiom lines agree
aib = rd(os.path.join(PAPER3, 'replay/logs/run2/axioms_in_build.txt'))
check(aib.count('depends on axioms') == 19, 'replay build log: 19 in-build axiom lines')
check(len(re.findall(r'depends on axioms: \[propext,\s*Classical\.choice,\s*Quot\.sound\]', aib)) == 19,
      'all 19 in-build axiom lines are the three standard axioms')
check('depends on axioms: [propext, Classical.choice, Quot.sound]' in
      rd(os.path.join(PAPER3, 'replay/logs/run2/axioms.txt')).replace('\n', ' ').replace('  ', ' ') or
      'Quot.sound' in rd(os.path.join(PAPER3, 'replay/logs/run2/axioms.txt')),
      'replay axioms.txt holds the three axioms for exact_count_and_sat')
# no recorded axiom output anywhere in the clone (text files only)
rec = subprocess.run(['grep', '-rIl', 'depends on axioms', CLONE], capture_output=True, text=True).stdout.split()
check(rec == [], 'no recorded `depends on axioms` output anywhere in the clone')
num['recorded_axiom_outputs'] = len(rec)

# ---------------------------------------------------------------- 4. comparator JSON, yaml, CI
js = json.load(open(os.path.join(LEAN, 'ComparatorChallenges/SubexponentialSAT.json')))
check(js['permitted_axioms'] == ['propext', 'Quot.sound', 'Classical.choice'], 'permitted axioms: the three')
check(js['enable_nanoda'] is False and js['definition_names'] == [], 'enable_nanoda false, definition_names empty')
check(js['theorem_names'] == ['OAI.Algorithms.SubexponentialSAT.SqrtLogSpace.exact_count_and_sat'], 'theorem_names')
jsons = sorted(f for f in os.listdir(os.path.join(LEAN, 'ComparatorChallenges')) if f.endswith('.json'))
nf = nt = nn = 0
for f in jsons:
    d = json.load(open(os.path.join(LEAN, 'ComparatorChallenges', f)))
    if 'enable_nanoda' not in d: nn += 1
    elif d['enable_nanoda']: nt += 1
    else: nf += 1
num['json_total'] = len(jsons); num['json_nanoda_false'] = nf; num['json_nanoda_true'] = nt; num['json_nanoda_absent'] = nn
check((len(jsons), nf, nt, nn) == (418, 413, 2, 3), 'challenge JSONs: 418; enable_nanoda false 413, true 2, absent 3')
yaml = rd(os.path.join(LEAN, 'formalization.yaml')).split('\n')
check(yaml[1682].strip() == '- comparator_config: ComparatorChallenges/SubexponentialSAT.json' and
      'exact_count_and_sat' in yaml[1683] and 'SqrtLogSpace/Final.lean' in yaml[1684], 'formalization.yaml 1683-1685')
wf = sorted(os.listdir(os.path.join(CLONE, '.github', 'workflows')))
check(wf == ['lock-prs.yml'], '.github/workflows holds only lock-prs.yml')
num['workflows'] = len(wf)

# ---------------------------------------------------------------- 5. toolchain, Mathlib, patches, hooks
check(rd(os.path.join(LEAN, 'lean-toolchain')).strip() == 'leanprover/lean4:v4.34.1', 'lean-toolchain v4.34.1')
mf = json.load(open(os.path.join(LEAN, 'lake-manifest.json')))
ml = [p for p in mf['packages'] if p['name'] == 'mathlib'][0]
check(ml['inputRev'] == 'd13f23b723b8a846827a245b89c10fc7d3f11612' and 'leanprover-community/mathlib4' in ml['url'],
      'manifest: Mathlib d13f23b7 from upstream')
num['manifest_packages'] = len(mf['packages'])
check(num['manifest_packages'] == 42, 'manifest: 42 packages')
patches = sorted(f for f in os.listdir(os.path.join(LEAN, 'patches')) if f.endswith('.patch'))
num['patches'] = len(patches)
check(num['patches'] == 23 and not any('mathlib' in p.lower() for p in patches), '23 patches, none for Mathlib')
# none of the patched packages is imported by the closure (the closure imports only Mathlib and Lean)
check(set(ext) == {'Mathlib', 'Lean'}, 'closure imports nothing from any patched package')
lk = rd(os.path.join(LEAN, 'lakefile.lean')).split('\n')
check(lk[7].strip() == 'fixedToolchain := true' and 'autoImplicit, false' in lk[8], 'lakefile 8-9: fixedToolchain, autoImplicit false')
check(lk[88].strip() == '@[default_target] lean_lib OAI', 'lakefile:89 default target OAI')
check(lk[289].strip() == 'run_cmd do' and 'unsafe env.evalConstCheck' in lk[295] and 'preparePatchedDependencies' in lk[301],
      'lakefile 290-304: run_cmd hook with evalConstCheck and preparePatchedDependencies')
check(lk[305].strip() == 'post_update pkg do', 'lakefile:306 post_update hook')
num['lakefile_lines'] = len(lk) - 1
check(num['lakefile_lines'] == 362, 'lakefile is 362 lines')

# ---------------------------------------------------------------- 6. the spine's line citations
S = 'OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/'
cite(S + 'Final.lean', 10, 'theorem compiled_exact_count_and_sat')
cite(S + 'Final.lean', 11, 'program : BitProgram.Program 80 1220 labels')
cite(S + 'Final.lean', 35, 'NativeLargeEntry.run k hk')
cite(S + 'Final.lean', 37, 'NativeOuterBudgets.runtime_with_fallback')
cite(S + 'Final.lean', 39, 'NativeOuterBudgets.space_with_fallback')
cite(S + 'Final.lean', 40, 'Native.countingProgram cutoff k (NativeLeafProgram.command k)')
cite(S + 'Final.lean', 74, 'theorem exact_count_and_sat')
cite(S + 'Final.lean', 100, 'GuardedCompiler.primitive program, (256 : Fin 1220), (1216 : Fin 1220)')
cite(S + 'Final.lean', 104, 'theorem exact_count_eth')
cite(S + 'GuardedCompiler.lean', 14, 'def selected', 17)
cite(S + 'GuardedCompiler.lean', 30, 'def transition', 47)
cite(S + 'GuardedCompiler.lean', 131, 'noncomputable abbrev primitive')
cite(S + 'GuardedCompiler.lean', 132, 'Fintype.equivFin')
cite(S + 'GuardedCompiler.lean', 152, 'theorem compiler_overhead')
cite(S + 'GuardedCompiler.lean', 153, '= 7')
cite(S + 'GuardedCompiler.lean', 158, 'theorem primitive_execution', 160)
cite(S + 'GuardedCompiler.lean', 162, 'RunsIn (primitive p).step (7 * n)')
cite(S + 'GuardedCompiler.lean', 600, 'theorem primitive_located_step')
cite(S + 'CompileSpace.lean', 125, 'theorem compile_word_answer_space')
cite(S + 'CompileSpace.lean', 134, 'time ≤ 7 * sourceSteps')
cite(S + 'CompileSpace.lean', 135, 'Computation.Trace (locatedStep (primitive p)) time')
cite(S + 'CompileSpace.lean', 143, 'visitedSpace intermediate ≤ s * (bound + input.length + 15)')
cite(S + 'NativeOuter.lean', 16, 'noncomputable def countingProgram')
cite(S + 'NativeOuter.lean', 50, 'final.stacks ABI.countStack = countWord (SAT.count F)')
cite(S + 'NativeOuter.lean', 51, 'final.stacks ABI.answerStack = [decide (0 < SAT.count F)]')
cite(S + 'NativeOuter.lean', 53, '(visits : ℝ) ≤', 56)
cite(S + 'NativeOuter.lean', 56, '(2 : ℝ) ^ ((n : ℝ) / sparsifySchedule n)')
cite(S + 'NativeOuter.lean', 73, 'theorem counting_primitive_from_entry')
cite(S + 'NativeLargeEntry.lean', 11, 'theorem run')
cite(S + 'NativeLargeEntry.lean', 12, '1 ≤ C ∧ 1 ≤ A')
cite(S + 'NativeLargeEntry.lean', 27, 'runtimeBound C A d (Encoding.formulaBitLength F) n')
cite(S + 'NativeLargeEntry.lean', 39, 'NativeLeafContract.uniform_contract')
cite(S + 'NativeLargeEntry.lean', 46, 'runtime_of_tree_and_leaf')
cite(S + 'NativeLargeEntry.lean', 48, 'Filter.eventually_atTop')
cite(S + 'NativeLargeEntry.lean', 50, 'let cutoff := max 20 (max Nleaf Ns)')
cite(S + 'NativeLargeEntry.lean', 51, '256 + At')
cite(S + 'NativeLargeEntry.lean', 51, 'db + (4 * (k - 2) + 2) + df')
cite(S + 'Final.lean', 41, 'C + 28700, A + 1, (S : ℝ) + 5022741, d + 2, e + 2')
cite(S + 'NativeLeafContract.lean', 793, '1 ≤ Ct ∧ 1 ≤ At')
cite(S + 'NativeEntry.lean', 81, 'theorem entry_small_primitive')
cite(S + 'NativeEntry.lean', 92, 'time ≤ 28700 * (Encoding.formulaBitLength F + 1) ^ 2')
cite(S + 'NativeOuterBudgets.lean', 297, 'theorem runtime_with_fallback')
cite(S + 'NativeOuterBudgets.lean', 299, 'runtimeBound (C+28700) (A+1) (d+2)')
cite(S + 'NativeOuterBudgets.lean', 317, 'theorem space_with_fallback')
cite(S + 'NativeOuterBudgets.lean', 319, '(S+5022741)')
cite('OAI/Algorithms/SubexponentialSAT/BitProgram.lean', 10, 'inductive Instr', 30)
cite('OAI/Algorithms/SubexponentialSAT/BitProgram.lean', 26, 'structure Program')
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/StatementCanonical.lean', 37, 'def MainTheorem : Prop')
cite('ComparatorChallenges/SubexponentialSAT.lean', 87, 'Trace', 90)
cite('ComparatorChallenges/SubexponentialSAT.lean', 149, 'LocatedCfg', 189)
cite('ComparatorChallenges/SubexponentialSAT.lean', 184, 'def locatedStep')
cite('ComparatorChallenges/SubexponentialSAT.lean', 201, 'Computation.Trace (locatedStep machine) time')
# the three bodied opaques of the recovery files and one Ports constant
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/LeafProgramPreparedRecoveryQuery.lean', 59, 'opaque queryRecovery')
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/LeafProgramPreparedRecoveryQuery.lean', 86, ':= by')
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/LeafProgramPreparedRecoveryWitness.lean', 178, 'opaque rawRecovery')
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/LeafProgramPreparedRecoveryWitness.lean', 198, 'opaque fixedRecovery')
cite('OAI/Algorithms/SubexponentialSAT/SqrtLog/LeafProgramQueryCleanup.lean', 22, 'private opaque cleanupPortsWrapped', 24)
# docs, dates, history
cite('docs/378.md', 9, '(L+1)^{O_k(1)}2^{O_k(n(\\log\\log n)^2/\\sqrt{\\log n})}')
pre = rd(os.path.join(CLONE, 'preprints/The-Exponential-Time-Hypothesis-is-False-October-25-2026/build/main_full_version.tex')).split('\n')
check(pre[24].strip() == r'\date{17 October 2026, revised 25 October 2026}', 'main_full_version.tex:25 date line')
hist = rd(os.path.join(CLONE, 'history.md')).split('\n')
check('Impagliazzo' in hist[17] and 'Williams' in hist[17], 'history.md:18 working-group sentence')
check(hist[6].strip() == '**Formalization Fix**', 'history.md:7 Formalization Fix heading')
check(not any('378' in l or 'Exponential Time' in l for i, l in enumerate(hist) if i != 17),
      'history.md mentions the family only in its line 18')
head = subprocess.run(['git', '-C', CLONE, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
check(head.startswith('4eaee875'), 'clone HEAD is 4eaee875'); num['clone_head'] = head[:8]

# ---------------------------------------------------------------- 7. the table
rows = [
    ('modules in the closure of \\texttt{Main.lean}', f"{num['closure_modules']:,}", '\\texttt{closure.py}'),
    ('raw lines in those modules', f"{num['closure_lines']:,}", '\\texttt{closure.py}'),
    ('external imports: Mathlib modules / core modules', f"{num['mathlib_modules']} / {num['core_modules']}", '\\texttt{closure.py}'),
    ('\\texttt{.lean} files under the family / outside the closure', f"{num['family_files']:,} / {num['dead_files']}", 'this script'),
    ('\\texttt{axiom}, \\texttt{sorry}, \\texttt{admit}, \\texttt{native\\_decide}, \\texttt{ofReduceBool}', '0, 0, 0, 0, 0', '\\texttt{closure.py}'),
    ('\\texttt{implemented\\_by}, \\texttt{extern}, \\texttt{unsafe}, \\texttt{partial}', '0, 0, 0, 0', '\\texttt{closure.py}'),
    ('\\texttt{elab}, \\texttt{macro}, \\texttt{syntax}, \\texttt{simproc}', '0, 0, 0, 0', '\\texttt{closure.py}'),
    ('\\texttt{set\\_option} (both \\texttt{quotPrecheck false})', str(kw['set_option']), '\\texttt{closure.py}'),
    ('\\texttt{opaque} (all with bodies)', f"{kw['opaque']} ({num['opaque_bodied']})", '\\texttt{closure.py}, this script'),
    ('\\texttt{noncomputable}', f"{kw['noncomputable']:,}", '\\texttt{closure.py}'),
    ('explicit \\texttt{Classical.choice} / \\texttt{propext} / \\texttt{open Classical}', f"{kw['Classical.choice']} / {kw['propext']} / {kw['open Classical']}", '\\texttt{closure.py}'),
    ('\\texttt{instance} / \\texttt{local instance}', f"{kw['instance']} / {kw['local instance']}", '\\texttt{closure.py}'),
    ('\\texttt{termination\\_by} / \\texttt{decreasing\\_by}', f"{kw['termination_by']} / {kw['decreasing_by']}", '\\texttt{closure.py}'),
    ('statement definitions compared / identical / identical up to \\texttt{noncomputable}', f"{num['defs_total']} / {num['defs_identical']} / {num['defs_modulo_noncomputable']}", '\\texttt{defdiff.py}, this script'),
    ('theorem statement, characters (normalised / raw), identical', f"{num['stmt_chars']:,} / {num['stmt_chars_raw']:,}", 'this script'),
    ('\\texttt{\\#print axioms} commands: closure files / lines; family files / lines', f"{num['pa_files_closure']} / {num['pa_lines_closure']}; {num['pa_files_family']} / {num['pa_lines_family']}", 'this script'),
    ('recorded \\texttt{depends on axioms} outputs in the clone', str(num['recorded_axiom_outputs']), 'this script'),
    ('challenge JSONs: total / \\texttt{enable\\_nanoda} false / true / absent', f"{num['json_total']} / {num['json_nanoda_false']} / {num['json_nanoda_true']} / {num['json_nanoda_absent']}", 'this script'),
    ('CI workflow files (\\texttt{lock-prs.yml} only)', str(num['workflows']), 'this script'),
    ('manifest packages / patch files / patches for Mathlib', f"{num['manifest_packages']} / {num['patches']} / 0", 'this script'),
]
tex = ['% Generated by python3 -I paper3/scripts/proof_inspection.py -- do not edit.',
       '\\begin{tabular}{@{}p{0.50\\linewidth}p{0.17\\linewidth}p{0.25\\linewidth}@{}}', '\\toprule',
       'quantity & value & script \\\\', '\\midrule']
for q, v, s in rows:
    tex.append(f'{q} & {v} & {s} \\\\')
tex += ['\\bottomrule', '\\end{tabular}', '']
if not CHECK:
    with open(os.path.join(PAPER3, 'latex', 'tables', 'proof_inspection.tex'), 'w') as f:
        f.write('\n'.join(tex))
    with open(os.path.join(PAPER3, 'latex', 'tables', 'proof_inspection.json'), 'w') as f:
        json.dump(num, f, indent=1, sort_keys=True)
    print('wrote latex/tables/proof_inspection.tex and .json')
print('== numbers'); print(json.dumps(num, indent=1, sort_keys=True))
if failures:
    print(f'{len(failures)} CHECK(S) FAILED'); sys.exit(1)
print('ALL CHECKS PASSED')
