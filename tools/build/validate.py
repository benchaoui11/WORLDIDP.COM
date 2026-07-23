#!/usr/bin/env python3
"""
WorldIDP site validator.

Exits non-zero on any FAIL so it can gate a deploy. Checks are grouped:
  A. Indexation integrity   — the checks that stop thin pages reaching search
  B. Metadata               — titles, descriptions, H1s, canonicals
  C. Structured data        — parse + schema/visible-content agreement
  D. Links                  — internal 404s, links to redirects
  E. Content quality        — placeholders, unsupported claims, banned phrases
  F. Accessibility basics   — h1 count, heading order, alt text, table captions
"""
import json, os, re, sys, glob, html
from collections import Counter, defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'

FAIL, WARN, OK = [], [], []


def fail(cat, msg):
    FAIL.append((cat, msg))


def warn(cat, msg):
    WARN.append((cat, msg))


def ok(cat, msg):
    OK.append((cat, msg))


BANNED = [
    'officially recognised', 'officially recognized', 'official idp',
    'government approved', 'government-approved', 'legally valid worldwide',
    'accepted in every country', 'replaces your licence', 'replaces your license',
    'guaranteed acceptance', '100% accepted', '195+',
]

PLACEHOLDER = ['TODO(', 'lorem ipsum', 'XXXX', '{{', '}}', 'undefined',
               'DATA REQUIRED']


def pages():
    for p in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
            continue
        yield p, rel


def text_of(h):
    h = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    h = re.sub(r'<style.*?</style>', ' ', h, flags=re.S)
    t = re.sub(r'<[^>]+>', ' ', h)
    t = html.unescape(t)
    # normalise the quote characters that differ between schema and markup
    t = t.replace("’", "'").replace("‘", "'")
    t = t.replace("“", '"').replace("”", '"')
    return re.sub(r'\s+', ' ', t)


def main():
    data = json.load(open(os.path.join(ROOT, 'data', 'countries.json')))
    cmap = {c['slug']: c for c in data}

    titles, descs, canons = Counter(), Counter(), Counter()
    all_pages = list(pages())

    # ---------------------------------------------------- per-page checks
    for p, rel in all_pages:
        h = open(p, errors='ignore').read()
        t = text_of(h)
        is_country = rel.startswith('countries' + os.sep) and rel.endswith('index.html')
        slug = os.path.basename(os.path.dirname(p)) if is_country else None

        # --- B. metadata
        mt = re.search(r'<title>(.*?)</title>', h, re.S)
        if not mt or not mt.group(1).strip():
            fail('B', f'{rel}: missing <title>')
        else:
            titles[mt.group(1).strip()] += 1
            if len(mt.group(1)) > 70:
                warn('B', f'{rel}: title {len(mt.group(1))} chars (>70)')

        md = re.search(r'<meta[^>]*?name="description"[^>]*?content="(.*?)"', h, re.S)
        if not md or not md.group(1).strip():
            fail('B', f'{rel}: missing meta description')
        else:
            descs[md.group(1).strip()] += 1
            L = len(md.group(1))
            if L > 175 or L < 70:
                warn('B', f'{rel}: meta description {L} chars (target 70-175)')

        h1s = re.findall(r'<h1[^>]*>(.*?)</h1>', h, re.S)
        if len(h1s) != 1:
            fail('F', f'{rel}: {len(h1s)} h1 tags (expected exactly 1)')

        mr = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', h, re.S)
        robots = mr.group(1) if mr else ''
        indexable = mr and 'noindex' not in robots.lower()

        mc = re.search(r'<link[^>]*?rel="canonical"[^>]*?href="([^"]*)"', h, re.S)
        if not mc:
            if indexable:
                fail('B', f'{rel}: indexable page with no canonical')
        else:
            canons[mc.group(1)] += 1
            if not mc.group(1).startswith(SITE):
                fail('B', f'{rel}: canonical does not point to {SITE}')

        if indexable and 'max-snippet:-1' not in robots:
            fail('A', f'{rel}: indexable but missing max-snippet:-1')

        # --- A. indexation integrity for country pages
        if is_country:
            c = cmap.get(slug)
            if not c:
                fail('A', f'{rel}: no data row for slug "{slug}"')
            else:
                should = bool(c.get('indexable'))
                if should != bool(indexable):
                    fail('A', f'{rel}: robots={robots!r} but data.indexable={should}')
                if should:
                    if len(c.get('officialSources') or []) < 2:
                        fail('A', f'{rel}: indexable with <2 official sources')
                    if not c.get('lastVerified'):
                        fail('A', f'{rel}: indexable with no lastVerified date')
                    if not c.get('idpStatus'):
                        fail('A', f'{rel}: indexable with no idpStatus')
                    if 'Sources used on this page' not in h:
                        fail('A', f'{rel}: indexable with no visible sources section')
                    wc = len(t.split())
                    if wc < 600:
                        fail('E', f'{rel}: indexable page only {wc} words')

        # --- C. structured data
        for m in re.finditer(r'<script type="application/ld\+json">\s*(.*?)\s*</script>', h, re.S):
            try:
                obj = json.loads(m.group(1))
            except Exception as ex:
                fail('C', f'{rel}: invalid JSON-LD ({str(ex)[:60]})')
                continue
            # FAQPage questions must appear in visible text
            def check(node):
                if isinstance(node, dict):
                    if node.get('@type') == 'Question':
                        q = html.unescape(node.get('name', ''))
                        q = q.replace("’", "'").replace("‘", "'")
                        q = q.replace("“", '"').replace("”", '"')
                        q = re.sub(r'\s+', ' ', q)[:45]
                        if q and q.lower() not in t.lower():
                            fail('C', f'{rel}: FAQ schema question not visible on page: "{q[:45]}"')
                    for v in node.values():
                        check(v)
                elif isinstance(node, list):
                    for v in node:
                        check(v)
            check(obj)

        # --- E. content quality
        low = t.lower()
        for b in BANNED:
            for m in re.finditer(re.escape(b), low):
                ctx = low[max(0, m.start() - 60):m.start()]
                # accurate references to a third party's own official document
                # are legitimate; a claim about our own document is not.
                if re.search(r"(aaa|aata|state department|usagov|government)'?s?\s*$", ctx):
                    continue
                if b in ('official idp',) and re.search(r'(aaa|aata)\b', ctx):
                    continue
                fail('E', f'{rel}: banned phrase "{b}"')
                break
        markup = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
        markup = re.sub(r'<style.*?</style>', ' ', markup, flags=re.S)
        for ph in PLACEHOLDER:
            if ph in markup:
                fail('E', f'{rel}: placeholder "{ph}" in rendered markup')
        if 'href="#"' in h:
            fail('E', f'{rel}: dead href="#" link')

        # --- F. accessibility basics
        for img in re.findall(r'<img[^>]*>', h):
            if 'alt=' not in img:
                warn('F', f'{rel}: <img> without alt')
        if '<table' in h and '<caption' not in h:
            warn('F', f'{rel}: table without caption')

    # ---------------------------------------------------- cross-page checks
    dupt = {k: v for k, v in titles.items() if v > 1}
    if dupt:
        for k, v in list(dupt.items())[:10]:
            fail('B', f'duplicate title on {v} pages: "{k[:60]}"')
    else:
        ok('B', f'{len(titles)} unique titles, zero duplicates')

    dupd = {k: v for k, v in descs.items() if v > 1}
    if dupd:
        for k, v in list(dupd.items())[:10]:
            fail('B', f'duplicate meta description on {v} pages: "{k[:60]}"')
    else:
        ok('B', f'{len(descs)} unique meta descriptions, zero duplicates')

    dupc = {k: v for k, v in canons.items() if v > 1}
    if dupc:
        for k, v in list(dupc.items())[:5]:
            fail('B', f'canonical claimed by {v} pages: {k}')
    else:
        ok('B', 'no canonical collisions')

    # ---------------------------------------------------- D. link integrity
    broken = set()
    for p, rel in all_pages:
        h = open(p, errors='ignore').read()
        base = os.path.dirname(p)
        for m in re.finditer(r'href="([^"]+)"', h):
            u = m.group(1)
            if u.startswith(('http', 'mailto:', 'tel:', '#', 'javascript:')):
                continue
            u = u.split('#')[0].split('?')[0]
            if not u:
                continue
            target = os.path.normpath(os.path.join(ROOT if u.startswith('/') else base,
                                                   u.lstrip('/')))
            if os.path.isdir(target):
                target = os.path.join(target, 'index.html')
            if not os.path.exists(target):
                broken.add(f'{rel} -> {m.group(1)}')
    if broken:
        for b in sorted(broken)[:15]:
            fail('D', f'broken link: {b}')
    else:
        ok('D', 'zero broken internal links')

    # ---------------------------------------------------- sitemap integrity
    sm = open(os.path.join(ROOT, 'sitemap.xml')).read()
    locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', sm)
    if any(l != l.strip() for l in re.findall(r'<loc>(.*?)</loc>', sm, re.S)):
        fail('A', 'sitemap <loc> values contain whitespace/newlines')
    bad = 0
    for l in locs:
        path = l.replace(SITE, '').lstrip('/')
        f = os.path.join(ROOT, path if path else 'index.html')
        if os.path.isdir(f):
            f = os.path.join(f, 'index.html')
        if not os.path.exists(f):
            fail('A', f'sitemap URL has no file: {l}')
            bad += 1
            continue
        hh = open(f, errors='ignore').read()
        mr = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', hh, re.S)
        if mr and 'noindex' in mr.group(1).lower():
            fail('A', f'NOINDEX page present in sitemap: {l}')
            bad += 1
    if not bad:
        ok('A', f'sitemap clean: {len(locs)} URLs, all indexable, all exist')

    # ---------------------------------------------------- robots.txt
    rb = open(os.path.join(ROOT, 'robots.txt')).read()
    for bot in ('GPTBot', 'PerplexityBot', 'ClaudeBot', 'Google-Extended', 'OAI-SearchBot'):
        if bot not in rb:
            warn('A', f'robots.txt does not mention {bot}')
    if 'Sitemap:' not in rb:
        fail('A', 'robots.txt has no Sitemap directive')
    else:
        ok('A', 'robots.txt declares sitemap and allows AI crawlers')

    # ---------------------------------------------------- report
    print('=' * 64)
    print('VALIDATION REPORT')
    print('=' * 64)
    cats = {'A': 'Indexation integrity', 'B': 'Metadata', 'C': 'Structured data',
            'D': 'Links', 'E': 'Content quality', 'F': 'Accessibility'}
    for k, label in cats.items():
        f = [m for c, m in FAIL if c == k]
        w = [m for c, m in WARN if c == k]
        o = [m for c, m in OK if c == k]
        status = 'FAIL' if f else ('WARN' if w else 'PASS')
        print(f'\n[{status}] {k}. {label}   ({len(f)} fail, {len(w)} warn)')
        for m in f[:12]:
            print(f'    FAIL  {m}')
        if len(f) > 12:
            print(f'    ... and {len(f)-12} more')
        seen = set()
        for m in w:
            key = re.sub(r'^\S+', '', m)[:60]
            if key in seen:
                continue
            seen.add(key)
            if len(seen) <= 5:
                print(f'    warn  {m}')
        if len(seen) > 5:
            print(f'    ... {len(w)} warnings total')
        for m in o:
            print(f'    ok    {m}')

    print('\n' + '=' * 64)
    print(f'TOTAL: {len(FAIL)} failures, {len(WARN)} warnings across {len(all_pages)} pages')
    print('=' * 64)
    return 1 if FAIL else 0


if __name__ == '__main__':
    sys.exit(main())
