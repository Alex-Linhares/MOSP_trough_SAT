"""Import closure of a Lean module, comment stripping, and keyword grep.
Run with: python3 -I closure.py <lean_root> <root_module>
Never executes anything from the untrusted tree; reads only."""
import sys, os, re, json, collections

root = sys.argv[1]
start = sys.argv[2]
out_dir = os.path.dirname(os.path.abspath(__file__))

def mod_to_path(mod):
    return os.path.join(root, *mod.split('.')) + '.lean'



def strip_comments(text):
    out = []
    i = 0; n = len(text); depth = 0
    while i < n:
        if depth == 0 and text.startswith('--', i):
            j = text.find('\n', i)
            if j == -1: break
            i = j
            continue
        if text.startswith('/-', i):
            depth += 1; i += 2; continue
        if depth > 0 and text.startswith('-/', i):
            depth -= 1; i += 2; continue
        if depth > 0:
            # preserve newlines so line numbers survive
            if text[i] == '\n': out.append('\n')
            i += 1; continue
        out.append(text[i]); i += 1
    return ''.join(out)


def imports_of(path):
    raw = open(path, encoding='utf-8', errors='replace').read()
    text = strip_comments(raw)
    mods = []
    for line in text.split('\n'):
        s = line.strip()
        if not s: continue
        if s.startswith('import '):
            mods.extend(t for t in s[7:].split() if t)
        elif s.startswith('prelude'):
            continue
        else:
            break
    return mods

seen = {}
external = collections.Counter()
queue = [start]
while queue:
    m = queue.pop()
    if m in seen: continue
    p = mod_to_path(m)
    if not os.path.exists(p):
        external[m.split('.')[0]] += 1
        seen[m] = None
        continue
    seen[m] = p
    for im in imports_of(p):
        if im not in seen:
            queue.append(im)

files = {m: p for m, p in seen.items() if p}
print('modules resolved inside', root, ':', len(files))
print('external (unresolved) imports by top-level prefix:', dict(external))

KEYWORDS = ['axiom', 'sorry', 'sorryAx', 'admit', 'native_decide', 'ofReduceBool', 'ofReduceNat',
            'implemented_by', 'extern', 'unsafe', 'partial', 'opaque', 'noncomputable', 'set_option',
            'decide', 'Classical.choice', 'stop', 'nonrec', 'autoImplicit', 'skipKernelTC', 'bootstrap',
            'constant', 'postulate', 'unsound', 'Quot.sound', 'propext', 'trust', 'elab', 'macro',
            'syntax', 'open Classical', 'simproc', 'IO', 'Lean.Elab', 'Lean.Meta', 'mutual', 'irreducible',
            'csimp', 'local instance', 'instance', 'Decidable', 'Fintype', 'termination_by', 'decreasing_by',
            'omega', 'compile_inductive', 'linter', 'with_unfolding_all', 'exact?', 'aesop', 'nofun']
pat = {k: re.compile(r'(?<![A-Za-z0-9_.!?\'])' + re.escape(k) + r'(?![A-Za-z0-9_!?\'])') for k in KEYWORDS}

counts = collections.Counter()
hits = collections.defaultdict(list)
total_lines = 0
sizes = []
for m, p in sorted(files.items()):
    raw = open(p, encoding='utf-8', errors='replace').read()
    nl = raw.count('\n') + 1
    total_lines += nl
    sizes.append((nl, p))
    stripped = strip_comments(raw)
    for ln, line in enumerate(stripped.split('\n'), 1):
        for k, r in pat.items():
            if r.search(line):
                counts[k] += 1
                hits[k].append((p, ln, line.strip()[:200]))

print('total lines (raw):', total_lines)
print('20 largest files:')
for nl, p in sorted(sizes, reverse=True)[:20]:
    print(f'  {nl:7d}  {os.path.relpath(p, root)}')
print('keyword line counts (comments stripped):')
for k in KEYWORDS:
    print(f'  {k:20s} {counts[k]}')
json.dump({k: hits[k] for k in KEYWORDS}, open(os.path.join(out_dir, 'hits.json'), 'w'), indent=1)
json.dump(sorted(files), open(os.path.join(out_dir, 'closure_modules.json'), 'w'), indent=1)
