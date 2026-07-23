#!/usr/bin/env python3
"""
Keyword cannibalisation check and consolidation.

Two pages competing for the same query is a self-inflicted ranking problem. The
market leader demonstrates it: on Semrush its homepage and /how-to-apply/ both
rank for "idp" (positions 6 and 13) and for "international driver's license"
(positions 6 and 16). Two pages splitting the signal beats neither.

This script:
  1. Detects title/H1 overlap across all indexable pages using token similarity.
  2. Applies the consolidation map below — the weaker page is removed and a 301
     added to vercel.json so its equity flows to the survivor.

Consolidations are declared explicitly rather than inferred, because merging the
wrong pair is worse than leaving both.
"""
import json, os, re, glob, itertools, shutil

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from -> to. The 'from' directory is deleted and a 301 written to vercel.json.
CONSOLIDATE = {
    '/guides/can-i-get-an-idp-the-same-day/':
        '/guides/can-i-get-an-idp-the-same-day-in-the-us/',
}

STOP = {'the', 'a', 'an', 'in', 'to', 'for', 'of', 'and', 'is', 'i', 'you',
        'can', 'do', 'need', 'get', 'what', 'how', 'worldidp', 'official',
        'guide', 'evidence', 'based', 'source', 'summary', 'options', 'answer'}


def tokens(s):
    return {w for w in re.findall(r'[a-z0-9]+', s.lower()) if w not in STOP and len(w) > 2}


def detect():
    pages = []
    for p in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('admin', 'templates', '_audit')):
            continue
        h = open(p, errors='replace').read()
        m = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', h, re.I | re.S)
        if m and 'noindex' in m.group(1).lower():
            continue
        t = re.search(r'<title>(.*?)</title>', h, re.S)
        h1 = re.search(r'<h1[^>]*>(.*?)</h1>', h, re.S)
        if not t:
            continue
        title = re.sub(r'\s+', ' ', t.group(1)).strip()
        head = re.sub(r'<[^>]*>', '', h1.group(1)).strip() if h1 else ''
        pages.append((rel, title, head, tokens(title + ' ' + head)))

    def entity(rel):
        """The disambiguating entity a page targets — its country or guide slug."""
        parts = rel.replace(os.sep, '/').split('/')
        if len(parts) >= 2 and parts[0] in ('countries', 'guides', 'compare', 'convention'):
            return f'{parts[0]}:{parts[1]}'
        return f'page:{parts[-1]}'

    risks = []
    for (r1, t1, _, s1), (r2, t2, _, s2) in itertools.combinations(pages, 2):
        if not s1 or not s2:
            continue
        # Two pages about different named entities are not cannibalising each
        # other, however similar their title structure. /countries/japan/ and
        # /countries/thailand/ answer different queries by definition.
        # A hub page aggregates its children and will always share generic
        # tokens with them. That is its job, not cannibalisation.
        def is_hub(rel):
            parts = rel.replace(os.sep, '/').split('/')
            return len(parts) == 2 and parts[1] == 'index.html'
        if is_hub(r1) != is_hub(r2):
            continue

        e1, e2 = entity(r1), entity(r2)
        if e1 != e2 and e1.split(':')[0] == e2.split(':')[0] == 'countries':
            continue
        # Same reasoning for two different convention pages.
        if e1 != e2 and e1.split(':')[0] == e2.split(':')[0] == 'convention':
            continue
        j = len(s1 & s2) / len(s1 | s2)
        if j >= 0.55:
            risks.append((round(j, 3), r1, t1, r2, t2))
    risks.sort(reverse=True)
    return risks


def consolidate():
    if not CONSOLIDATE:
        return 0
    vpath = os.path.join(ROOT, 'vercel.json')
    v = json.load(open(vpath)) if os.path.exists(vpath) else {}
    redirects = v.get('redirects', [])
    existing = {r.get('source') for r in redirects}

    done = 0
    for src, dest in CONSOLIDATE.items():
        d = os.path.join(ROOT, src.strip('/'))
        if os.path.isdir(d):
            shutil.rmtree(d)
            print(f'  removed {src}')
        if src.rstrip('/') not in existing:
            redirects.append({'source': src.rstrip('/'),
                              'destination': dest, 'permanent': True})
            redirects.append({'source': src.rstrip('/') + '/',
                              'destination': dest, 'permanent': True})
            print(f'  301 {src} -> {dest}')
        done += 1

    v['redirects'] = redirects
    json.dump(v, open(vpath, 'w'), indent=2)
    return done


if __name__ == '__main__':
    n = consolidate()
    print(f'consolidations applied: {n}')
    print()
    risks = detect()
    if risks:
        print(f'remaining title/H1 overlap above 0.55 Jaccard: {len(risks)}')
        for j, r1, t1, r2, t2 in risks[:10]:
            print(f'  {j}  {r1}')
            print(f'        vs {r2}')
    else:
        print('no cannibalisation risk detected across indexable pages')
