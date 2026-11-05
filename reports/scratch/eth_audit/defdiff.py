import re, sys
root='/home/al/dev/untrusted/openai-math/lean/'
chal=open(root+'ComparatorChallenges/SubexponentialSAT.lean').read()
libfiles=['OAI/Algorithms/SubexponentialSAT/SAT.lean','OAI/Algorithms/SubexponentialSAT/BinaryArithmetic.lean','OAI/Algorithms/SubexponentialSAT/Encoding.lean','OAI/Algorithms/SubexponentialSAT/Computation.lean','OAI/Algorithms/SubexponentialSAT/SqrtLog/StatementScale.lean','OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/VisitedTape.lean','OAI/Algorithms/SubexponentialSAT/SqrtLogSpace/Final.lean']
lib='\n'.join(open(root+f).read() for f in libfiles)
def strip(text):
    out=[];i=0;n=len(text);d=0
    while i<n:
        if d==0 and text.startswith('--',i):
            j=text.find('\n',i); i=n if j<0 else j; continue
        if text.startswith('/-',i): d+=1;i+=2;continue
        if d>0 and text.startswith('-/',i): d-=1;i+=2;continue
        if d>0: i+=1;continue
        out.append(text[i]);i+=1
    return ''.join(out)
chal=strip(chal); lib=strip(lib)
heads=r'(?:noncomputable\s+)?(?:private\s+)?(?:def|abbrev|structure|inductive|theorem|lemma|instance|class|opaque)\s+'
def blocks(text):
    res={}
    # split at declaration starts (line beginning with head keyword, possibly after attributes) 
    pat=re.compile(r'^(?:@\[[^\]]*\]\s*)?'+heads+r'([^\s(:{\[]+)',re.M)
    ms=list(pat.finditer(text))
    for i,m in enumerate(ms):
        end=ms[i+1].start() if i+1<len(ms) else len(text)
        body=text[m.start():end]
        # cut at next top-level keyword like 'end ', 'namespace', 'section', 'variable', 'open', 'universe'
        cut=re.search(r'^(end|namespace|section|variable|open|universe|#print)\b',body,re.M)
        if cut: body=body[:cut.start()]
        name=m.group(1)
        res.setdefault(name,[]).append(re.sub(r'\s+',' ',body).strip())
    return res
cb=blocks(chal); lb=blocks(lib)
for name,vs in cb.items():
    c=vs[0]
    cands=lb.get(name,[])
    if c in cands:
        print('SAME     ',name)
    else:
        print('DIFF/MISS',name, '| library candidates:',len(cands))
        print('   CHAL:',c[:400])
        for x in cands[:3]: print('   LIB :',x[:400])
