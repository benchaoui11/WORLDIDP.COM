#!/usr/bin/env python3
"""
WorldIDP country page generator (v2).

Design rules this generator enforces:
  1. Title and H1 come from real search intent, selected by the country's own
     data pattern — never one template string with the name swapped in.
  2. The first text in the DOM is a factual answer block, not marketing.
  3. Tier A pages carry country-specific evidence and are indexable.
     Tier B/C pages are `noindex, follow`, excluded from the sitemap, and
     honestly labelled — they exist for navigation and research only.
  4. Nothing is invented. Absent data renders an explicit "not confirmed"
     statement telling the traveller what to check and with whom.
  5. Internal links are chosen contextually from the country's own attributes.
  6. Schema is generated from the same variables as the visible text, so the
     two can never disagree.
"""
import json, os, re, html, datetime
from collections import defaultdict

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'countries')
SITE = 'https://worldidp.com'
TODAY = '2026-07-23'

CONV_LABEL = {
    '1949-geneva': '1949 Geneva Convention',
    '1968-vienna': '1968 Vienna Convention',
    '1926-paris': '1926 Paris Convention',
}
CONV_URL = {
    '1949-geneva': '/convention/1949-geneva/',
    '1968-vienna': '/convention/1968-vienna/',
}


def e(s):
    return html.escape(str(s), quote=True) if s is not None else ''


THE = {'United States', 'United Arab Emirates', 'United Kingdom', 'Netherlands',
       'Philippines', 'Bahamas', 'Maldives', 'Gambia', 'Czech Republic',
       'Dominican Republic', 'Central African Republic'}


# Short forms used in title tags only. Shorter titles avoid SERP truncation and
# match how people actually search ("UK", "UAE", "USA" rather than the full name).
SHORT = {
    'United Kingdom': 'the UK',
    'United States': 'the US',
    'United Arab Emirates': 'the UAE',
    'Netherlands': 'the Netherlands',
    'Bosnia and Herzegovina': 'Bosnia',
    'Trinidad and Tobago': 'Trinidad',
    'Dominican Republic': 'the Dominican Republic',
    'Czech Republic': 'Czechia',
    'Antigua and Barbuda': 'Antigua',
    'Saint Vincent and the Grenadines': 'Saint Vincent',
    'Central African Republic': 'the CAR',
    'Papua New Guinea': 'Papua New Guinea',
}


def short(name):
    return SHORT.get(name, name)


def join_list(items):
    """Oxford-free English list join: 'A', 'A and B', 'A, B and C'."""
    items = list(items)
    if len(items) <= 1:
        return ''.join(items)
    return ', '.join(items[:-1]) + ' and ' + items[-1]


def art(name, cap=False):
    """Country name with the definite article where English requires one."""
    if name in THE:
        return ('The ' if cap else 'the ') + name
    return name


# --------------------------------------------------------------- intent model
def page_angle(c):
    """
    Choose the search-intent angle from the country's own evidence pattern.
    Returns (title, h1, description, angle_key).

    Different data patterns produce genuinely different pages, which is what
    stops this from being one template with a name substituted.
    """
    n = c['name']
    N = art(n)
    Nc = art(n, cap=True)
    S = short(n)
    status = (c.get('idpStatus') or '')
    convs = c.get('conventions') or []

    # -- visitors generally exempt (e.g. United Kingdom) -----------------
    if 'not-required' in status or 'exempt-for-visitors' in status:
        return (f"Do You Need an IDP to Drive in {S}? {TODAY[:4]} Rules",
                f"Do You Need an International Driving Permit in {N}?",
                f"Most visitors drive in {N} on their own national licence rather than on an "
                f"International Driving Permit. Here is the rule, how long it lasts, and what "
                f"actually gets checked.",
                'visitor-exempt')

    # -- convention-specific requirement (e.g. Japan) --------------------
    if 'geneva-only' in status or ('1949-geneva' in convs and '1968-vienna' not in convs
                                   and status.startswith('required')):
        cl = CONV_LABEL.get(convs[0], 'the applicable convention') if convs else 'the applicable convention'
        return (f"Do You Need an IDP in {S}? {cl.split()[0]} Convention Rules",
                f"Do You Need an International Driving Permit in {N}?",
                f"{Nc} recognises IDPs issued under the {cl}. Check which format applies to your licence, what to carry, and what rental desks ask for.",
                'convention-specific')

    # -- sub-national variation (e.g. United States, Australia) ----------
    if 'state' in status:
        return (f"International Driving Permit in {S}: State Rules {TODAY[:4]}",
                f"Do You Need an International Driving Permit in {N}?",
                f"Driving rules for visitors in {N} are set at state or territory level rather than nationally. Here is what varies, what to carry, and what to confirm before you drive.",
                'sub-national')

    # -- licence-origin dependent (e.g. Mexico, UAE) ---------------------
    if 'origin' in status or 'exempted' in status:
        return (f"Can You Drive in {S} With a Foreign Licence? IDP Rules",
                f"Do You Need an International Driving Permit in {N}?",
                f"Whether you need an IDP in {N} depends on where your licence was issued. Here is how the rules differ by licence origin, and what to confirm before you travel.",
                'origin-dependent')

    # -- translation / EU-recognition split (Italy, France, Germany, Spain)
    if 'translation' in status or 'eu' in status.lower() or 'recommended' in status:
        return (f"Do You Need an International Driving Permit in {S}?",
                f"Do You Need an International Driving Permit in {N}?",
                f"{Nc} treats EU/EEA licences differently from other licences. Here is which rule applies to you, what to carry, and what rental desks ask for.",
                'recognition-split')

    # -- plain requirement (Thailand) ------------------------------------
    if status.startswith('required'):
        return (f"International Driving Permit for {S}: What You Need",
                f"Do You Need an International Driving Permit in {N}?",
                f"An International Driving Permit is part of the documentation foreign visitors are expected to carry in {N}. Here is the format that applies and what to carry with it.",
                'required')

    # -- tier B / C: research page, explicitly not a guide ----------------
    return (f"Driving in {S}: What to Check Before You Go",
            f"Driving in {N}: What to Confirm Before You Travel",
            f"We have not yet completed source-backed research for {N}. This page explains what to check and where, rather than presenting unverified requirements as fact.",
            'research-pending')


# --------------------------------------------------------------- answer block
def answer_block(c, angle):
    """40-70 word extractable answer. Facts only. No CTA."""
    n = c['name']
    N = art(n)
    Nc = art(n, cap=True)
    side = c.get('drivingSide')
    convs = c.get('conventions') or []
    conv_txt = join_list(CONV_LABEL.get(x, x) for x in convs)

    if angle == 'research-pending':
        return (f"We have not completed source-backed research for {N}, so this page does not "
                f"state whether an International Driving Permit is required. "
                + (f"{Nc} drives on the {side}. " if side else "")
                + (f"{Nc} is party to the {conv_txt}. " if convs else "")
                + "Confirm current requirements with the relevant national authority and your rental provider before you drive.")

    parts = []
    applies = c.get('idpStatusApplies')
    if applies:
        parts.append(applies.rstrip('.') + '.')
    if convs:
        parts.append(f"{Nc} is party to the {conv_txt}.")
    if side:
        parts.append(f"Traffic drives on the {side}.")
    if c.get('speedDisplayUnit') == 'mph' and c.get('speedMotorwayMph'):
        parts.append(f"Motorway limit {c['speedMotorwayMph']} mph.")
    elif c.get('speedMotorwayKmh'):
        parts.append(f"Motorway limit {c['speedMotorwayKmh']} km/h.")
    if c.get('lastVerified'):
        parts.append(f"Sources reviewed {c['lastVerified']}.")
    return ' '.join(parts)


# --------------------------------------------------------------- fact table
def facts_table(c):
    rows = []

    def row(label, value, note=None):
        if value in (None, '', []):
            return
        rows.append((label, value, note))

    side = c.get('drivingSide')
    if side:
        conf = c.get('drivingSideConfidence')
        row('Driving side', side.capitalize(),
            'Reference list' if conf == 'high' else 'Official source')
    convs = c.get('conventions') or []
    if convs:
        row('Road traffic convention', ', '.join(CONV_LABEL.get(x, x) for x in convs))
    mph = (c.get('speedDisplayUnit') == 'mph')
    for label, kmh_key, mph_key in (('Motorway speed limit', 'speedMotorwayKmh', 'speedMotorwayMph'),
                                    ('Rural speed limit', 'speedRuralKmh', 'speedRuralMph'),
                                    ('Built-up area limit', 'speedUrbanKmh', 'speedUrbanMph')):
        kmh, m = c.get(kmh_key), c.get(mph_key)
        if mph and m:
            row(label, f'{m} mph ({kmh} km/h)' if kmh else f'{m} mph')
        elif kmh:
            row(label, f'{kmh} km/h')
    if c.get('minimumRentalAge'):
        row('Minimum rental age', c['minimumRentalAge'])
    if c.get('bacLimit') is not None:
        row('Blood alcohol limit', c.get('bacNote') or f"{c['bacLimit']} g/l")

    unknown = []
    if not c.get('speedMotorwayKmh'):
        unknown.append('speed limits')
    if not c.get('minimumRentalAge'):
        unknown.append('minimum rental age')
    if c.get('bacLimit') is None:
        unknown.append('blood alcohol limit')
    return rows, unknown


# --------------------------------------------------------------- sections
def section(title, body, sid=None):
    idattr = f' id="{sid}"' if sid else ''
    return f'''      <section class="cg-section"{idattr}>
        <h2>{title}</h2>
{body}
      </section>
'''


def build_body(c, angle):
    n = c['name']
    N = art(n)
    Nc = art(n, cap=True)
    out = []

    # ---- 1. requirement -------------------------------------------------
    if angle != 'research-pending':
        b = []
        if c.get('idpStatusApplies'):
            b.append(f'        <p><strong>Who this applies to.</strong> {e(c["idpStatusApplies"])}</p>')
        if c.get('idpStatusExempt'):
            b.append(f'        <p><strong>Who is treated differently.</strong> {e(c["idpStatusExempt"])}</p>')
        if c.get('licenceOriginNotes'):
            b.append(f'        <p>{e(c["licenceOriginNotes"])}</p>')
        if b:
            head = (f'Who actually needs an IDP in {e(N)}'
                    if angle == 'visitor-exempt' else f'Who needs an IDP in {e(N)}')
            out.append(section(head, '\n'.join(b), 'requirement'))

    # ---- 2. convention --------------------------------------------------
    convs = c.get('conventions') or []
    if convs:
        links = []
        for x in convs:
            u = CONV_URL.get(x)
            lbl = CONV_LABEL.get(x, x)
            links.append(f'<a href="{u}">{lbl}</a>' if u else lbl)
        b = [f'        <p>{e(Nc)} is party to the {join_list(links)}. '
             'The convention determines which IDP format has a legal basis here, '
             'which is why two IDPs that look similar are not always interchangeable.</p>']
        if len(convs) > 1:
            b.append('        <p>Where a country is party to more than one convention, '
                     'the more recent convention generally governs between states that are '
                     'party to both.</p>')
        out.append(section('Which convention applies', '\n'.join(b), 'convention'))

    # ---- 3. facts table -------------------------------------------------
    rows, unknown = facts_table(c)
    if rows:
        tr = '\n'.join(
            f'            <tr><th scope="row">{e(l)}</th><td>{e(v)}</td></tr>'
            for l, v, _ in rows)
        b = [f'''        <table class="cg-facts">
          <caption class="visually-hidden">Driving facts for {e(N)}</caption>
          <tbody>
{tr}
          </tbody>
        </table>''']
        if unknown:
            b.append(f'        <p class="cg-unknown">Not confirmed for {e(n)}: '
                     f'{e(", ".join(unknown))}. We do not estimate these. '
                     'Check the posted signs and your rental agreement.</p>')
        out.append(section(f'Driving facts for {e(N)}', '\n'.join(b), 'facts'))

    # ---- 4. digital document -------------------------------------------
    st = c.get('digitalDocumentStatus') or 'unclear'
    note = c.get('digitalDocumentNote')
    label = {'accepted': 'Accepted', 'rejected': 'Not accepted',
             'unclear': 'Not confirmed', 'provider-dependent': 'Depends on the provider'}.get(st, 'Not confirmed')
    b = [f'        <p><strong>{label}.</strong> {e(note) if note else ""}</p>']
    if st == 'unclear':
        b.append('        <p>This is the least documented question in this category. '
                 'Most national authorities have not published a position on digital-only '
                 'driving documents, and rental companies set their own rules. '
                 'Carry a printed document and treat any digital copy as a convenience, '
                 'not a substitute. See our '
                 '<a href="/what-is-idp.html">explanation of what an IDP is</a> for more.</p>')
    out.append(section(f'Is a digital IDP accepted in {e(N)}?', '\n'.join(b), 'digital'))

    # ---- 5. documents to carry -----------------------------------------
    docs = c.get('documentsToCarry') or []
    if docs:
        li = '\n'.join(f'          <li>{e(d)}</li>' for d in docs)
        out.append(section('What to carry',
                           f'        <ul class="cg-list">\n{li}\n        </ul>\n'
                           '        <p>Your original national driving licence is the document that '
                           'grants driving privileges. A translation-support document is presented '
                           'alongside it and never replaces it.</p>', 'carry'))

    # ---- 6. rental / roadside ------------------------------------------
    b = []
    if c.get('rentalNotes'):
        b.append(f'        <p><strong>At the rental desk.</strong> {e(c["rentalNotes"])}</p>')
    if c.get('roadsideCheckNotes'):
        b.append(f'        <p><strong>In a roadside check.</strong> {e(c["roadsideCheckNotes"])}</p>')
    if b:
        out.append(section(f'Rental desks and roadside checks in {e(N)}', '\n'.join(b), 'practical'))

    # ---- 7. country notes ----------------------------------------------
    notes = c.get('countrySpecificNotes') or []
    if notes:
        li = '\n'.join(f'          <li>{e(x)}</li>' for x in notes)
        out.append(section(f'Specific to {e(N)}',
                           f'        <ul class="cg-list">\n{li}\n        </ul>', 'specific'))

    # ---- 8. research-pending explanation --------------------------------
    if angle == 'research-pending':
        rep = []
        if c.get('reportedIdpStatus'):
            rep.append(f'an internal dataset records this destination as '
                       f'"{e(c["reportedIdpStatus"])}", which we have not yet confirmed against an official source')
        if c.get('reportedSpeedMotorwayKmh'):
            rep.append(f'a motorway limit of {c["reportedSpeedMotorwayKmh"]} km/h is recorded but unconfirmed')
        extra = ('<p>For transparency: ' + '; and '.join(rep) + '.</p>') if rep else ''
        out.append(section(
            'Why this page does not state a requirement',
            f'''        <p>We publish a requirement only when we can point to an official source and
        record the date we checked it. That research is not yet complete for {e(n)}, so this page
        deliberately does not tell you whether an IDP is required.</p>
        {extra}
        <p>Confirm with the national road authority or embassy for {e(N)}, and separately with your
        rental provider, whose contractual rules can be stricter than the law.</p>
        <p>Our <a href="/editorial-policy.html">editorial and verification policy</a> explains the
        standard a page has to meet before we publish a requirement.</p>''', 'pending'))

    # ---- 9. FAQ ---------------------------------------------------------
    faq = c.get('faq') or []
    if faq:
        items = '\n'.join(
            f'''        <div class="cg-faq-item">
          <h3>{e(f["q"])}</h3>
          <p>{e(f["a"])}</p>
        </div>''' for f in faq)
        out.append(section(f'{e(n)} driving document questions', items, 'faq'))

    # ---- 10. sources ----------------------------------------------------
    srcs = c.get('officialSources') or []
    if srcs:
        li = []
        for s in srcs:
            if isinstance(s, dict):
                nm, url = s.get('name'), s.get('url')
            else:
                nm, url = s, None
            li.append(f'          <li><a href="{e(url)}" rel="nofollow noopener" target="_blank">{e(nm)}</a></li>'
                      if url else f'          <li>{e(nm)}</li>')
        out.append(section('Sources used on this page',
                           '        <ul class="cg-sources">\n' + '\n'.join(li) + '\n        </ul>\n'
                           f'        <p class="cg-verified">Sources last reviewed: '
                           f'<time datetime="{e(c.get("lastVerified") or TODAY)}">{e(c.get("lastVerified") or TODAY)}</time>. '
                           'Facts we could not confirm are marked as unconfirmed rather than estimated.</p>',
                           'sources'))
    return ''.join(out)


# --------------------------------------------------------- contextual links
def related_links(c, index):
    """Contextual, not a fixed block. Chosen from this country's own attributes."""
    out = []
    convs = c.get('conventions') or []
    for x in convs:
        if x in CONV_URL:
            out.append((CONV_URL[x], f'How the {CONV_LABEL[x]} works'))
    for slug in (c.get('relatedCountries') or [])[:3]:
        peer = index.get(slug)
        if peer:
            verb = 'IDP rules for' if peer.get('indexable') else 'Driving in'
            out.append((f'/countries/{slug}/', f'{verb} {peer["name"]}'))
    if (c.get('idpStatus') or '').find('state') >= 0 or c['slug'] == 'united-states':
        out.append(('/compare/aaa-idp-vs-worldidp/', 'AAA and AATA compared with a private translation document'))
        out.append(('/guides/what-is-aata/', 'What AATA is and how it differs from AAA'))
    if (c.get('digitalDocumentStatus') or 'unclear') == 'unclear':
        out.append(('/what-is-idp.html', 'What an International Driving Permit actually is'))
    out.append(('/how-to-apply.html', 'How the WorldIDP application works'))
    seen, uniq = set(), []
    for u, t in out:
        if u not in seen:
            seen.add(u)
            uniq.append((u, t))
    return uniq[:6]


# --------------------------------------------------------------- schema
ORG_NODE = {
    "@type": "Organization",
    "@id": f"{SITE}/#organization",
    "name": "WorldIDP",
    "legalName": "WORLDIDP INTERNATIONAL LLC",
    "url": f"{SITE}/",
    "logo": f"{SITE}/IMAGES/worldidp-international-driving-permit-logo.webp",
    "email": "hello@worldidp.com",
    "description": (
        "WorldIDP is an independent private service operated by WORLDIDP INTERNATIONAL LLC "
        "that prepares a multilingual translation-support document for a valid national "
        "driving licence. It is not a government agency and is not authorised to issue "
        "International Driving Permits. The document is carried alongside the original "
        "national driving licence and does not replace it."
    ),
    "disambiguatingDescription": (
        "Private translation-support service for national driving licences. "
        "Not a government agency and not an authorised issuer of International Driving Permits."
    ),
    "knowsAbout": [
        "International Driving Permit",
        "1949 Geneva Convention on Road Traffic",
        "1968 Vienna Convention on Road Traffic",
        "Driving licence translation",
        "Driving abroad requirements by country",
        "Car rental documentation requirements",
    ],
}


def build_schema(c, title, desc, angle, url):
    # The Organization is defined in full on every page, not merely referenced.
    # A language model reading a single country page in isolation should be able
    # to resolve who published it without following an @id to another document.
    graph = [
        dict(ORG_NODE),
        {"@type": "WebSite", "@id": f"{SITE}/#website", "url": f"{SITE}/",
         "name": "WorldIDP", "inLanguage": "en",
         "publisher": {"@id": f"{SITE}/#organization"}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Countries", "item": f"{SITE}/countries.html"},
            {"@type": "ListItem", "position": 3, "name": c['name'], "item": url},
        ]},
        {"@type": "WebPage", "@id": url, "url": url, "name": title,
         "description": desc, "inLanguage": "en",
         "isPartOf": {"@id": f"{SITE}/#website"},
         "publisher": {"@id": f"{SITE}/#organization"},
         "dateModified": c.get('lastVerified') or TODAY,
         "about": {"@type": "Country", "name": c['name']}},
    ]
    faq = c.get('faq') or []
    if faq:
        graph.append({"@type": "FAQPage", "mainEntity": [
            {"@type": "Question", "name": f["q"],
             "acceptedAnswer": {"@type": "Answer", "text": f["a"]}} for f in faq]})
    if c.get('officialSources') and c.get('indexable'):
        cites = [s.get('url') for s in c['officialSources']
                 if isinstance(s, dict) and s.get('url')]
        if cites:
            graph[1]["citation"] = cites
    return json.dumps({"@context": "https://schema.org", "@graph": graph},
                      indent=2, ensure_ascii=False)


# --------------------------------------------------------------- page shell
def render(c, index, shell):
    slug = c['slug']
    url = f"{SITE}/countries/{slug}/"
    title, h1, desc, angle = page_angle(c)
    indexable = bool(c.get('indexable'))
    robots = ("index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
              if indexable else "noindex, follow")

    ans = answer_block(c, angle)
    body = build_body(c, angle)
    links = related_links(c, index)
    linkhtml = '\n'.join(f'          <li><a href="{u}">{e(t)}</a></li>' for u, t in links)

    status_banner = ''
    if not indexable:
        status_banner = (
            '      <p class="cg-status" role="note">Research in progress — this page does not '
            'yet state a requirement for this destination.</p>\n')

    schema = build_schema(c, title, desc, angle, url)

    main = f'''    <article class="cg">
      <nav class="cg-crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">/</span>
        <a href="/countries.html">Countries</a> <span aria-hidden="true">/</span>
        <span aria-current="page">{e(c['name'])}</span>
      </nav>

      <h1>{e(h1)}</h1>

{status_banner}      <div class="cg-answer">
        <p>{e(ans)}</p>
      </div>

{body}
      <section class="cg-section cg-related">
        <h2>Related guidance</h2>
        <ul class="cg-list">
{linkhtml}
        </ul>
      </section>

      <section class="cg-section cg-cta">
        <h2>Before you apply</h2>
        <p>WorldIDP is an independent private translation-support service. It is not a government
        agency and does not replace your original national driving licence. Check the requirement
        for your destination first, then apply only if a private translation document fits your
        situation.</p>
        <p><a class="cg-btn" href="/how-to-apply.html">See how the application works</a></p>
      </section>
    </article>
'''
    return (shell
            .replace('{{TITLE}}', e(title))
            .replace('{{DESC}}', e(desc))
            .replace('{{ROBOTS}}', robots)
            .replace('{{CANONICAL}}', url)
            .replace('{{SCHEMA}}', schema)
            .replace('{{MAIN}}', main)
            .replace('{{OGTITLE}}', e(title))
            .replace('{{COUNTRY}}', e(c['name'])))


def main():
    countries = json.load(open(os.path.join(DATA, 'countries.json')))
    index = {c['slug']: c for c in countries}
    shell = open(os.path.join(ROOT, 'templates', 'country-shell.html')).read()

    written = 0
    for c in countries:
        d = os.path.join(OUT, c['slug'])
        os.makedirs(d, exist_ok=True)
        with open(os.path.join(d, 'index.html'), 'w') as f:
            f.write(render(c, index, shell))
        written += 1

    idx = sum(1 for c in countries if c.get('indexable'))
    print(f"generated {written} country pages")
    print(f"  indexable:  {idx}")
    print(f"  noindex:    {written - idx}")


if __name__ == '__main__':
    main()
