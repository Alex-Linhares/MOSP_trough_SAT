import sys, json, urllib.request, urllib.parse
def q(search, n=12, filt=None):
    params={'search':search,'per-page':n,'mailto':'research@example.org'}
    if filt: params['filter']=filt
    d=json.load(urllib.request.urlopen('https://api.openalex.org/works?'+urllib.parse.urlencode(params), timeout=60))
    for w in d['results']:
        oa=(w.get('best_oa_location') or {})
        src=((w.get('primary_location') or {}).get('source') or {}).get('display_name')
        print(f"{w['publication_year']} | {w['title']} | {src} | {w.get('doi')} | cit={w['cited_by_count']} | oa={oa.get('pdf_url') or oa.get('landing_page_url')} | {w['id'].split('/')[-1]}")
for s in sys.argv[1:]:
    print('###', s)
    try: q(s)
    except Exception as e: print('ERR', e)
