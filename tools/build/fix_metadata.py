#!/usr/bin/env python3
"""
Two targeted repairs found by validate.py:

  1. Seven core pages carry og:description and twitter:description but no
     <meta name="description">. Search engines use the latter; the social tags
     do not substitute for it. We derive the description from the existing
     og:description so the wording stays the one already reviewed.

  2. Several FAQPage schema questions do not match the visible heading on the
     page (e.g. schema says "Does a longer validity period cost more?" while the
     page shows "Does a longer validity cost more?"). Schema must reflect what a
     user sees. We rewrite the schema to the visible wording, never the reverse.
"""
import json, os, re, glob, html, difflib

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

meta_fixed = []
faq_fixed = []


def visible(h):
    b = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    b = re.sub(r'<style.*?</style>', ' ', b, flags=re.S)
    t = html.unescape(re.sub(r'<[^>]+>', ' ', b))
    t = t.replace('\u2019', "'").replace('\u2018', "'")
    t = t.replace('\u201c', '"').replace('\u201d', '"')
    return re.sub(r'\s+', ' ', t)


def headings(h):
    b = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    out = []
    for m in re.finditer(r'<(h2|h3|h4|summary|button)[^>]*>(.*?)</\1>', b, re.S):
        t = html.unescape(re.sub(r'<[^>]+>', '', m.group(2)))
        t = t.replace('\u2019', "'").replace('\u2018', "'")
        t = re.sub(r'\s+', ' ', t).strip()
        if t.endswith('?') and 8 < len(t) < 180:
            out.append(t)
    return out


for path in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
    rel = os.path.relpath(path, ROOT)
    if rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
        continue
    h = open(path).read()
    orig = h

    # ---------------------------------------------- 1. meta description
    if not re.search(r'<meta\s+name="description"', h, re.I):
        og = re.search(r'<meta\s+property="og:description"\s+content="([^"]*)"', h)
        tw = re.search(r'<meta\s+name="twitter:description"\s+content="([^"]*)"', h)
        src = (og or tw)
        if src:
            desc = src.group(1)
            anchor = re.search(r'(<title>.*?</title>\s*\n)', h, re.S)
            tag = f'  <meta name="description" content="{desc}" />\n'
            if anchor:
                h = h[:anchor.end()] + tag + h[anchor.end():]
            else:
                h = h.replace('</head>', tag + '</head>', 1)
            meta_fixed.append(f'{rel}  ({len(desc)} chars, from og:description)')

    # ---------------------------------------------- 2. FAQ schema alignment
    vis = visible(h)
    heads = headings(h)

    def repair(m):
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except Exception:
            return m.group(0)
        touched = [False]

        def walk(node):
            if isinstance(node, dict):
                if node.get('@type') == 'Question':
                    q = html.unescape(node.get('name', ''))
                    q = q.replace('\u2019', "'").replace('\u2018', "'")
                    q = re.sub(r'\s+', ' ', q).strip()
                    if q and q[:45].lower() not in vis.lower():
                        match = difflib.get_close_matches(q, heads, n=1, cutoff=0.55)
                        if match:
                            faq_fixed.append(f'{rel}: "{q[:52]}" -> "{match[0][:52]}"')
                            node['name'] = match[0]
                            touched[0] = True
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(obj)
        if not touched[0]:
            return m.group(0)
        return ('<script type="application/ld+json">\n'
                + json.dumps(obj, indent=2, ensure_ascii=False)
                + '\n  </script>')

    h = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
               repair, h, flags=re.S)

    if h != orig:
        open(path, 'w').write(h)

print(f'meta descriptions added: {len(meta_fixed)}')
for m in meta_fixed:
    print('   ', m)
print(f'FAQ schema questions realigned to visible text: {len(faq_fixed)}')
for m in faq_fixed:
    print('   ', m)
