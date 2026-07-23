#!/usr/bin/env python3
"""
GEO entity consistency layer.

Applies the principle stated most directly in the semantic SEO reference:

    "Don't silo your identity to your About page. The homepage, service pages,
     even your footer — they all reinforce who you are to a machine."

and the finding that consistency, clarity and frequency of a claim is what
causes an LLM to repeat it correctly rather than hallucinate around it.

What this does, sitewide:

  1. One canonical entity description, used verbatim in Organization schema on
     every page. Not nine paraphrases of the same idea.
  2. `knowsAbout` and `slogan` on the Organization node, so the entity is tied
     to its topics rather than floating free.
  3. `mainEntity` on WebPage nodes, connecting page to subject.
  4. `isPartOf` / `publisher` wiring so the graph resolves to one entity.
  5. `speakable` on the answer block of country pages, marking the passage that
     is safe to quote out of context.
  6. A machine-readable `dateModified` consistent with the visible review date.

It writes no `sameAs` — that still requires owner-confirmed profile URLs.
Schema is only ever tightened here, never made to claim something the visible
page does not say.
"""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
ORG_ID = f'{SITE}/#organization'
SITE_ID = f'{SITE}/#website'
TODAY = '2026-07-23'

# sameAs is read from data/verified-profiles.json and only ever includes
# profiles the owner has confirmed exist. An entry that is blank or unverified
# is skipped silently — a sameAs pointing at a non-existent profile damages
# entity resolution rather than helping it.
_pp = os.path.join(ROOT, 'data', 'verified-profiles.json')
SAME_AS = []
if os.path.exists(_pp):
    SAME_AS = [x['url'] for x in json.load(open(_pp)).get('profiles', [])
               if x.get('verified') is True and x.get('url')]

# The single canonical description. Every Organization node gets this exact
# string. Consistency is the mechanism — variation is what produces hallucination.
DESCRIPTION = (
    "WorldIDP is an independent private service operated by WORLDIDP INTERNATIONAL LLC "
    "that prepares a multilingual translation-support document for a valid national "
    "driving licence. It is not a government agency and is not authorised to issue "
    "International Driving Permits. The document is carried alongside the original "
    "national driving licence and does not replace it."
)

KNOWS_ABOUT = [
    "International Driving Permit",
    "1949 Geneva Convention on Road Traffic",
    "1968 Vienna Convention on Road Traffic",
    "Driving licence translation",
    "Driving abroad requirements by country",
    "Car rental documentation requirements",
]

DISAMBIGUATING = (
    "Private translation-support service for national driving licences. "
    "Not a government agency and not an authorised issuer of International Driving Permits."
)


def walk(node, fn):
    if isinstance(node, dict):
        fn(node)
        for v in node.values():
            walk(v, fn)
    elif isinstance(node, list):
        for v in node:
            walk(v, fn)


def process(path):
    rel = os.path.relpath(path, ROOT)
    h = open(path).read()
    orig = h
    is_country = rel.startswith('countries' + os.sep) and rel.endswith('index.html')

    # visible review date, if the page shows one
    mdate = re.search(r'<time datetime="(\d{4}-\d{2}-\d{2})"', h)
    visible_date = mdate.group(1) if mdate else None

    stats = {'org': 0, 'page': 0, 'speakable': 0}

    def repair(m):
        raw = m.group(1)
        try:
            obj = json.loads(raw)
        except Exception:
            return m.group(0)

        def fix(node):
            t = node.get('@type')
            if t == 'Organization' and str(node.get('name', '')).lower().startswith('worldidp'):
                node['@id'] = ORG_ID
                node['description'] = DESCRIPTION
                node['disambiguatingDescription'] = DISAMBIGUATING
                node['knowsAbout'] = KNOWS_ABOUT
                if SAME_AS:
                    node['sameAs'] = SAME_AS
                node.setdefault('url', f'{SITE}/')
                stats['org'] += 1
            elif t == 'WebSite':
                node['@id'] = SITE_ID
                node.setdefault('url', f'{SITE}/')
                node['publisher'] = {'@id': ORG_ID}
                node.setdefault('inLanguage', 'en')
            elif t == 'WebPage':
                node.setdefault('isPartOf', {'@id': SITE_ID})
                node['publisher'] = {'@id': ORG_ID}
                node.setdefault('inLanguage', 'en')
                if visible_date:
                    node['dateModified'] = visible_date
                if is_country:
                    # mark the answer block as the quotable passage
                    node['speakable'] = {
                        '@type': 'SpeakableSpecification',
                        'cssSelector': ['.cg-answer'],
                    }
                    stats['speakable'] += 1
                stats['page'] += 1

        walk(obj, fix)
        return ('<script type="application/ld+json">\n'
                + json.dumps(obj, indent=2, ensure_ascii=False)
                + '\n  </script>')

    h = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
               repair, h, flags=re.S)

    if h != orig:
        open(path, 'w').write(h)
        return stats
    return None


def main():
    totals = {'files': 0, 'org': 0, 'page': 0, 'speakable': 0}
    for path in sorted(glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True)):
        rel = os.path.relpath(path, ROOT)
        if rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
            continue
        s = process(path)
        if s:
            totals['files'] += 1
            for k in ('org', 'page', 'speakable'):
                totals[k] += s[k]

    print(f"entity layer applied to {totals['files']} files")
    print(f"  Organization nodes given the canonical description: {totals['org']}")
    print(f"  WebPage nodes wired to publisher + isPartOf:        {totals['page']}")
    print(f"  answer blocks marked speakable:                     {totals['speakable']}")
    if SAME_AS:
        print(f"  sameAs profiles attached:                           {len(SAME_AS)}")
        for u in SAME_AS:
            print(f"      {u}")
    else:
        print("  sameAs written: 0 (no confirmed profiles yet)")


if __name__ == '__main__':
    main()
