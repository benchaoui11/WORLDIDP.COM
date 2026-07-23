#!/usr/bin/env python3
"""
Contextual internal links from pillar pages into the verified country set.

Rule this script follows: the same generic block must NOT be injected into every
page. Each pillar gets a link set chosen for that pillar's topic, with anchor
text written for that context. Only Tier A (source-backed) countries are linked
this way — passing internal equity to noindex research stubs is pointless.
"""
import json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
countries = {c['slug']: c for c in json.load(open(os.path.join(ROOT, 'data', 'countries.json')))}
verified = {s: c for s, c in countries.items() if c.get('indexable')}

MARKER = 'data-internal-links="generated"'

# Each pillar links to the countries that actually illustrate that pillar's point,
# with anchor text specific to the reason for the link.
PLANS = {
    'what-is-idp.html': {
        'heading': 'How the rules differ by destination',
        'intro': ('The convention a country belongs to decides which IDP format has a legal '
                  'basis there. These destinations show why that distinction matters in practice.'),
        'links': [
            ('japan', 'Japan recognises the 1949 Geneva Convention only'),
            ('mexico', 'Mexico sits under the 1926 Paris Convention framework'),
            ('italy', 'Italy is party to both the 1949 and 1968 conventions'),
            ('united-states', 'US requirements are set state by state, not federally'),
        ],
        'extra': [('/convention/1949-geneva/', 'What the 1949 Geneva Convention covers'),
                  ('/convention/1968-vienna/', 'What the 1968 Vienna Convention covers')],
    },
    'how-to-apply.html': {
        'heading': 'Check your destination before you apply',
        'intro': ('Apply only once you know what your destination expects. These country pages '
                  'state the requirement, name the sources and record the date we checked them.'),
        'links': [
            ('italy', 'IDP requirements for Italy'),
            ('spain', 'IDP requirements for Spain'),
            ('france', 'IDP requirements for France'),
            ('japan', 'IDP requirements for Japan'),
            ('thailand', 'IDP requirements for Thailand'),
            ('united-arab-emirates', 'IDP requirements for the United Arab Emirates'),
        ],
        'extra': [('/countries.html', 'Browse the full country registry')],
    },
    'compare/aaa-idp-vs-worldidp/index.html': {
        'heading': 'Where you are driving changes the answer',
        'intro': ('Whether AAA, AATA or a private translation document is the right route depends '
                  'on your destination as much as on your licence.'),
        'links': [
            ('united-states', 'Driving in the United States on a foreign licence'),
            ('japan', 'Japan accepts only the 1949 Geneva Convention format'),
            ('italy', 'What Italy expects from non-EU licence holders'),
        ],
        'extra': [('/guides/what-is-aata/', 'What AATA is and how it differs from AAA')],
    },
    'convention/1949-geneva/index.html': {
        'heading': 'Destinations under this convention',
        'intro': 'Verified country pages where the 1949 Geneva Convention is the operative framework.',
        'links': [
            ('japan', 'Japan — 1949 Geneva Convention only'),
            ('thailand', 'Thailand — 1949 Geneva Convention'),
            ('australia', 'Australia — state-level rules on top of the convention'),
            ('united-states', 'United States — 1949 Geneva Convention'),
        ],
        'extra': [('/convention/1968-vienna/', 'How the 1968 Vienna Convention differs')],
    },
    'convention/1968-vienna/index.html': {
        'heading': 'Destinations under this convention',
        'intro': 'Verified country pages where the 1968 Vienna Convention applies.',
        'links': [
            ('germany', 'Germany — 1968 Vienna Convention'),
            ('italy', 'Italy — party to both conventions'),
            ('spain', 'Spain — party to both conventions'),
            ('mexico', 'Mexico — a different treaty framework again'),
        ],
        'extra': [('/convention/1949-geneva/', 'How the 1949 Geneva Convention differs')],
    },
    'faq.html': {
        'heading': 'Country-specific answers',
        'intro': ('General answers only go so far. These destination pages give the sourced '
                  'position for a specific country.'),
        'links': [
            ('italy', 'Do you need an IDP in Italy?'),
            ('japan', 'Do you need an IDP in Japan?'),
            ('spain', 'Do you need an IDP in Spain?'),
            ('mexico', 'Do you need an IDP in Mexico?'),
        ],
        'extra': [('/editorial-policy.html', 'How we verify what we publish')],
    },
}


def depth_prefix(rel):
    return '../' * rel.count(os.sep)


def block(plan, rel):
    items = []
    for slug, anchor in plan['links']:
        if slug not in verified:
            continue
        items.append(f'          <li><a href="/countries/{slug}/">{anchor}</a></li>')
    for href, anchor in plan.get('extra', []):
        items.append(f'          <li><a href="{href}">{anchor}</a></li>')
    if not items:
        return None
    return f'''
      <section class="cg-section cg-crosslinks" {MARKER}>
        <h2>{plan['heading']}</h2>
        <p>{plan['intro']}</p>
        <ul class="cg-list">
{chr(10).join(items)}
        </ul>
      </section>
'''


changed = []
for rel, plan in PLANS.items():
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        print(f'  skip (missing): {rel}')
        continue
    h = open(path).read()
    h = re.sub(r'\s*<section class="cg-section cg-crosslinks".*?</section>\s*', '\n', h, flags=re.S)

    b = block(plan, rel)
    if not b:
        continue

    # insert before the closing </main>, falling back to before <footer>
    if '</main>' in h:
        h = h.replace('</main>', b + '  </main>', 1)
    elif '<footer' in h:
        i = h.find('<footer')
        h = h[:i] + b + h[i:]
    else:
        print(f'  skip (no insertion point): {rel}')
        continue

    # the block uses country-guide.css; make sure the page loads it
    if 'country-guide.css' not in h:
        css = f'<link rel="stylesheet" href="{depth_prefix(rel)}country-guide.css?v=20260723" />'
        h = h.replace('</head>', f'  {css}\n</head>', 1)

    open(path, 'w').write(h)
    n = b.count('<li>')
    changed.append((rel, n))

print(f'pillar pages given contextual country links: {len(changed)}')
for rel, n in changed:
    print(f'    {rel}: {n} links')
print(f'verified countries available to link: {len(verified)}')
