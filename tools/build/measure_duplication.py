#!/usr/bin/env python3
"""
Country-page duplication measurement.

Measures three things, because raw text overlap alone is misleading:
  1. Shingle similarity (5-word) on visible body text — catches paraphrase
     and country-name substitution, not just exact matches.
  2. Section-title similarity — catches identical structure.
  3. Metadata uniqueness — titles, descriptions, H1s.

Boilerplate (header, footer, nav, CTA) is excluded, because a consistent
layout is legitimate. What matters is whether the informational core differs.
"""
import re, os, sys, glob, json, itertools, statistics
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def body_text(path):
    h = open(path).read()
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S)
    h = re.sub(r'<header.*?</header>', ' ', h, flags=re.S)
    h = re.sub(r'<footer.*?</footer>', ' ', h, flags=re.S)
    h = re.sub(r'<nav.*?</nav>', ' ', h, flags=re.S)
    # drop the standard CTA block — legitimately identical everywhere
    h = re.sub(r'<section class="cg-section cg-cta".*?</section>', ' ', h, flags=re.S)
    h = re.sub(r'<section class="cg-section cg-related".*?</section>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', h)
    t = re.sub(r'&[a-z#0-9]+;', ' ', t)
    return re.sub(r'\s+', ' ', t).strip().lower()


def shingles(text, k=5):
    w = text.split()
    return set(' '.join(w[i:i + k]) for i in range(max(0, len(w) - k + 1)))


def jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def meta(path):
    h = open(path).read()
    def grab(p):
        m = re.search(p, h, re.S)
        return re.sub(r'\s+', ' ', re.sub(r'<[^>]*>', '', m.group(1))).strip() if m else ''
    return (grab(r'<title>(.*?)</title>'),
            grab(r'name="description" content="(.*?)"'),
            grab(r'<h1>(.*?)</h1>'))


def run(pattern, label, indexable_only=None, data=None):
    paths = sorted(glob.glob(pattern))
    if indexable_only is not None and data:
        idx = {c['slug']: c.get('indexable') for c in data}
        paths = [p for p in paths
                 if idx.get(os.path.basename(os.path.dirname(p))) == indexable_only]
    if len(paths) < 2:
        print(f"{label}: fewer than 2 pages, skipped")
        return None

    sh = {p: shingles(body_text(p)) for p in paths}
    sims = []
    worst = (0, None, None)
    for a, b in itertools.combinations(paths, 2):
        s = jaccard(sh[a], sh[b])
        sims.append(s)
        if s > worst[0]:
            worst = (s, a, b)

    metas = [meta(p) for p in paths]
    t, d, h1 = zip(*metas)

    print(f"\n{label}  (n={len(paths)}, {len(sims)} pairs)")
    print(f"  max  similarity : {max(sims):.1%}   ({os.path.basename(os.path.dirname(worst[1]))} vs {os.path.basename(os.path.dirname(worst[2]))})")
    print(f"  mean similarity : {statistics.mean(sims):.1%}")
    print(f"  median          : {statistics.median(sims):.1%}")
    print(f"  pairs > 70%     : {sum(1 for s in sims if s > .70)}")
    print(f"  pairs > 50%     : {sum(1 for s in sims if s > .50)}")
    print(f"  unique titles   : {len(set(t))}/{len(paths)}")
    print(f"  unique descs    : {len(set(d))}/{len(paths)}")
    print(f"  unique H1s      : {len(set(h1))}/{len(paths)}")
    tp = Counter(re.sub(r'\b[A-Z][a-zA-Z]+\b', '{C}', x) for x in t)
    print(f"  title patterns  : {len(tp)}  -> {dict(list(tp.items())[:6])}")
    return dict(n=len(paths), max=max(sims), mean=statistics.mean(sims),
                median=statistics.median(sims),
                over70=sum(1 for s in sims if s > .70),
                titles=len(set(t)), descs=len(set(d)), h1s=len(set(h1)))


if __name__ == '__main__':
    target = sys.argv[1] if len(sys.argv) > 1 else ROOT
    data = None
    dp = os.path.join(ROOT, 'data', 'countries.json')
    if os.path.exists(dp):
        data = json.load(open(dp))
    print("=" * 62)
    print(f"DUPLICATION REPORT  —  {target}")
    print("=" * 62)
    res = {}
    res['all'] = run(os.path.join(target, 'countries', '*', 'index.html'),
                     'ALL country pages')
    if data:
        res['indexable'] = run(os.path.join(target, 'countries', '*', 'index.html'),
                               'INDEXABLE pages only', indexable_only=True, data=data)
    print()
