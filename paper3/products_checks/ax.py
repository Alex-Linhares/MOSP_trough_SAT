import sys, urllib.request, urllib.parse, re, time
for t in sys.argv[1:]:
    q=urllib.parse.quote(t)
    x=urllib.request.urlopen(f'http://export.arxiv.org/api/query?search_query={q}&max_results=6',timeout=60).read().decode()
    ents=re.findall(r'<entry>(.*?)</entry>',x,re.S)
    print('###',t, len(ents))
    for e in ents:
        print('  ',re.search(r'<id>(.*?)</id>',e).group(1), re.sub(r'\s+',' ',re.search(r'<title>(.*?)</title>',e,re.S).group(1))[:110])
    time.sleep(3)
