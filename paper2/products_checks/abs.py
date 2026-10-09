import sys, json, urllib.request
for doi in sys.argv[1:]:
    d=json.load(urllib.request.urlopen(f'https://api.openalex.org/works/doi:{doi}?mailto=research@example.org',timeout=60))
    inv=d.get('abstract_inverted_index') or {}
    pos=sorted((p,w) for w,ps in inv.items() for p in ps)
    b=d.get('biblio',{})
    print('###',doi,d['title'],d['publication_year'],[a['author']['display_name'] for a in d['authorships']], b.get('volume'),b.get('first_page'),b.get('last_page'))
    print(' '.join(w for _,w in pos) or '(no abstract)')
