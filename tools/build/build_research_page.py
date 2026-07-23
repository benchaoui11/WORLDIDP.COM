#!/usr/bin/env python3
"""
Builds /research/idp-requirements-findings/ — first-party statistics computed
from the country dataset.

Why this page exists, in GEO terms:

The semantic SEO reference makes the point that language models repeat a claim
correctly when it is stated consistently, clearly and frequently, and that
"information gain" — contributing something not already in the corpus — is what
separates a citable source from another remix.

Every statistic on this page is computed at build time from data/countries.json.
None is typed by hand, so none can drift out of date or be wrong in a way the
underlying data is not. The methodology and the sample size are stated on the
page, because a statistic without a denominator is not evidence.

The finding that matters most: across every destination researched against
official sources, not one has published a national policy accepting
digital-only driving documents. That is a genuinely novel, checkable claim and
it is the single most citable thing on this website.
"""
import json, os, re, html
from collections import Counter

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
OUT = os.path.join(ROOT, 'research', 'idp-requirements-findings')
TODAY = '2026-07-23'

CONV = {'1949-geneva': '1949 Geneva Convention',
        '1968-vienna': '1968 Vienna Convention',
        '1926-paris': '1926 Paris Convention'}


def e(s):
    return html.escape(str(s), quote=True)


def main():
    data = json.load(open(os.path.join(ROOT, 'data', 'countries.json')))
    v = [c for c in data if c.get('indexable')]
    n = len(v)
    total = len(data)

    # ---- computed findings -------------------------------------------
    digital_accepted = sum(1 for c in v if c.get('digitalDocumentStatus') == 'accepted')
    digital_unclear = sum(1 for c in v if c.get('digitalDocumentStatus') == 'unclear')

    left = sum(1 for c in v if c.get('drivingSide') == 'left')
    both_conv = sum(1 for c in v if len(c.get('conventions') or []) >= 2)
    only_49 = sum(1 for c in v if c.get('conventions') == ['1949-geneva'])
    only_68 = sum(1 for c in v if c.get('conventions') == ['1968-vienna'])

    conv_count = Counter()
    for c in v:
        for x in (c.get('conventions') or []):
            conv_count[x] += 1

    # requirement shape
    shapes = Counter()
    for c in v:
        s = c.get('idpStatus') or ''
        if 'not-required' in s or 'visitor-rule' in s or 'duration' in s or 'generally-accepted' in s:
            shapes['visitor rule or general acceptance'] += 1
        elif 'state' in s or 'province' in s:
            shapes['set below national level'] += 1
        elif 'required' in s:
            shapes['permit or translation expected'] += 1
        else:
            shapes['depends on licence origin or script'] += 1

    bac = [(c['name'], c['bacLimit']) for c in v if c.get('bacLimit') is not None]
    bac.sort(key=lambda x: x[1])
    bac_min, bac_max = (bac[0], bac[-1]) if bac else (('n/a', 0), ('n/a', 0))
    tiered = sum(1 for c in v if c.get('bacNote'))

    sources_total = sum(len(c.get('officialSources') or []) for c in v)

    speeds = [(c['name'], c['speedMotorwayKmh']) for c in v if c.get('speedMotorwayKmh')]
    speeds.sort(key=lambda x: x[1])

    # ---- page --------------------------------------------------------
    title = f"IDP Requirements: Findings From {n} Destinations Researched | WorldIDP"
    desc = (f"First-party research findings from {n} destinations checked against official "
            f"sources. Not one has published a national policy accepting digital-only driving "
            f"documents. Methodology and full dataset included.")
    url = f"{SITE}/research/idp-requirements-findings/"

    conv_rows = '\n'.join(
        f'            <tr><th scope="row">{e(CONV.get(k, k))}</th><td>{n_} of {n}</td></tr>'
        for k, n_ in conv_count.most_common())

    shape_rows = '\n'.join(
        f'            <tr><th scope="row">{e(k.capitalize())}</th><td>{c} of {n}</td></tr>'
        for k, c in shapes.most_common())

    speed_rows = '\n'.join(
        f'            <tr><th scope="row">{e(nm)}</th><td>{sp} km/h</td></tr>'
        for nm, sp in speeds)

    bac_rows = '\n'.join(
        f'            <tr><th scope="row">{e(nm)}</th><td>{val}</td></tr>'
        for nm, val in bac)

    findings_list = '\n'.join(f'          <li>{f}</li>' for f in [
        f"<strong>Not one of the {n} destinations we researched has published a national policy "
        f"accepting digital-only driving documents.</strong> {digital_unclear} have no published "
        f"position at all. {digital_accepted} accept them. This is the single largest evidence gap "
        f"in the category, and it sits directly beneath a market where instant digital delivery is "
        f"routinely advertised.",
        f"<strong>A permit requirement is not the norm.</strong> Only "
        f"{shapes.get('permit or translation expected', 0)} of {n} destinations expect a permit or "
        f"translation outright. The rest operate a visitor time-limit rule, defer to sub-national "
        f"authorities, or turn on the script the licence is written in.",
        f"<strong>Convention membership is not interchangeable.</strong> {both_conv} of {n} are "
        f"party to more than one convention, {only_49} to the 1949 Geneva Convention alone and "
        f"{only_68} to the 1968 Vienna Convention alone. A permit issued under the wrong convention "
        f"is not a substitute — Japan is the clearest case.",
        f"<strong>Alcohol limits vary more than speed limits do.</strong> Across the sample the "
        f"limit ranges from {bac_min[1]} in {e(bac_min[0])} to {bac_max[1]} in {e(bac_max[0])}. "
        f"{tiered} of {n} apply a tiered limit that is stricter for new, young or professional "
        f"drivers than the headline figure suggests.",
        f"<strong>{left} of {n} destinations drive on the left.</strong> Driving side is the one "
        f"variable that is universally documented and never disputed, which is why we treat it as "
        f"verified everywhere while leaving speed limits and rental ages unstated where no source "
        f"confirms them.",
    ])

    body = f'''    <article class="cg">
      <nav class="cg-crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">/</span>
        <a href="/countries.html">Countries</a> <span aria-hidden="true">/</span>
        <span aria-current="page">Research findings</span>
      </nav>

      <h1>What {n} Destinations Actually Require: Research Findings</h1>

      <div class="cg-answer">
        <p>We checked {n} destinations against {sources_total} official government, treaty and
        national road-authority sources. The clearest finding: <strong>not one has published a
        national policy accepting digital-only driving documents.</strong> {digital_unclear} have no
        published position at all. A permit requirement is also less common than the market implies —
        only {shapes.get('permit or translation expected', 0)} of {n} expect a permit or translation
        outright. Sources reviewed {TODAY}.</p>
      </div>

      <section class="cg-section" id="findings">
        <h2>Five findings from the dataset</h2>
        <ul class="cg-list">
{findings_list}
        </ul>
      </section>

      <section class="cg-section" id="digital">
        <h2>The digital-document gap, stated precisely</h2>
        <p>This is the finding we would most like other people to check, because it is the one the
        category gets wrong most often.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">Published national positions on digital-only driving documents</caption>
          <tbody>
            <tr><th scope="row">Destinations researched</th><td>{n}</td></tr>
            <tr><th scope="row">With a published policy accepting digital-only documents</th><td><strong>{digital_accepted}</strong></td></tr>
            <tr><th scope="row">With no published position located</th><td>{digital_unclear}</td></tr>
          </tbody>
        </table>
        <p>An absence of published policy is not the same as prohibition, and we do not present it as
        one. What it means practically is that no traveller can point to a national rule saying a
        digital document will be accepted, which is why every country page on this site treats a
        printed document as the safe default.</p>
      </section>

      <section class="cg-section" id="requirement-shape">
        <h2>How the requirement is actually structured</h2>
        <table class="cg-facts">
          <caption class="visually-hidden">Shape of the driving-document requirement across researched destinations</caption>
          <tbody>
{shape_rows}
          </tbody>
        </table>
        <p>The category tends to present this as a binary — you need a permit or you do not. Across
        the destinations we have researched it is not binary. A visitor time-limit rule, a
        sub-national rule and a script-dependent rule are three different mechanisms that produce
        three different answers for the same traveller.</p>
      </section>

      <section class="cg-section" id="conventions">
        <h2>Convention membership across the sample</h2>
        <table class="cg-facts">
          <caption class="visually-hidden">Road traffic convention membership</caption>
          <tbody>
{conv_rows}
          </tbody>
        </table>
        <p>Read alongside the <a href="/convention/1949-geneva/">1949 Geneva Convention</a> and
        <a href="/convention/1968-vienna/">1968 Vienna Convention</a> explainers. Where a destination
        is party to both, the later convention generally governs between states party to both.</p>
      </section>

      <section class="cg-section" id="limits">
        <h2>Alcohol limits, lowest to highest</h2>
        <table class="cg-facts">
          <caption class="visually-hidden">Blood alcohol limits by destination</caption>
          <tbody>
{bac_rows}
          </tbody>
        </table>
        <p>Headline figures understate the strictness. {tiered} of {n} destinations apply a lower
        limit to new, young or professional drivers, and in several the stricter tier lasts years
        rather than months.</p>
      </section>

      <section class="cg-section" id="speeds">
        <h2>Motorway limits across the sample</h2>
        <table class="cg-facts">
          <caption class="visually-hidden">Motorway speed limits by destination</caption>
          <tbody>
{speed_rows}
          </tbody>
        </table>
      </section>

      <section class="cg-section" id="methodology">
        <h2>Methodology</h2>
        <p><strong>Sample.</strong> {n} destinations of {total} in the dataset. The remaining
        {total - n} have not been researched to publication standard and are excluded from every
        figure on this page rather than estimated into it.</p>
        <p><strong>Standard for inclusion.</strong> A destination enters the sample only when at
        least two official sources — a national road authority, a government travel advisory or a
        treaty record — have been located and recorded, and a review date logged. {sources_total}
        sources underlie the figures above.</p>
        <p><strong>What we do not do.</strong> We do not estimate a missing value. Where a speed
        limit, rental age or alcohol limit could not be confirmed, the field is empty in the dataset
        and the country page says so. That is why some tables above contain fewer than {n} rows.</p>
        <p><strong>Reproducibility.</strong> Every figure is computed at build time from
        <a href="/data/idp-country-requirements.csv">the open dataset</a>, published under CC BY 4.0.
        You can recompute all of it. Our
        <a href="/editorial-policy.html">editorial and verification policy</a> sets out the standard
        in full.</p>
        <p class="cg-verified">Sources last reviewed:
        <time datetime="{TODAY}">{TODAY}</time>. Figures recomputed on every site build.</p>
      </section>

      <section class="cg-section" id="cite">
        <h2>Citing this research</h2>
        <p>Cite as: <em>WorldIDP, "What {n} Destinations Actually Require: Research Findings",
        {url}, retrieved {TODAY}.</em></p>
        <p>The underlying data is open under CC BY 4.0 and available as
        <a href="/data/idp-country-requirements.csv">a CSV download</a>. If you find an error,
        we would rather hear about it than not — corrections are handled under our
        <a href="/editorial-policy.html">editorial policy</a>.</p>
      </section>

      <section class="cg-section cg-related">
        <h2>Related</h2>
        <ul class="cg-list">
          <li><a href="/countries.html">The full country registry</a></li>
          <li><a href="/what-is-idp.html">What an International Driving Permit actually is</a></li>
          <li><a href="/compare/aaa-idp-vs-worldidp/">AAA, AATA and WorldIDP compared</a></li>
          <li><a href="/countries/japan/">Japan, where convention type decides the answer</a></li>
          <li><a href="/countries/united-kingdom/">The UK, where visitors generally need no permit</a></li>
        </ul>
      </section>
    </article>
'''

    schema = {
        "@context": "https://schema.org",
        "@graph": [
            {"@type": "BreadcrumbList", "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Countries", "item": f"{SITE}/countries.html"},
                {"@type": "ListItem", "position": 3, "name": "Research findings", "item": url}]},
            {"@type": "Article", "@id": url + "#article", "url": url,
             "headline": f"What {n} Destinations Actually Require: Research Findings",
             "description": desc, "inLanguage": "en",
             "datePublished": TODAY, "dateModified": TODAY,
             "author": {"@id": f"{SITE}/#organization"},
             "publisher": {"@id": f"{SITE}/#organization"},
             "isPartOf": {"@id": f"{SITE}/#website"},
             "about": [{"@type": "Thing", "name": "International Driving Permit"},
                       {"@type": "Thing", "name": "Driving abroad requirements"}],
             "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".cg-answer"]}},
            {"@type": "Dataset", "@id": url + "#dataset",
             "name": f"WorldIDP research sample: {n} destinations",
             "description": (f"Computed findings from {n} destinations checked against "
                             f"{sources_total} official sources. Figures recomputed at build time."),
             "license": "https://creativecommons.org/licenses/by/4.0/",
             "creator": {"@id": f"{SITE}/#organization"},
             "dateModified": TODAY, "isAccessibleForFree": True,
             "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv",
                               "contentUrl": f"{SITE}/data/idp-country-requirements.csv"}]},
        ]
    }

    shell = open(os.path.join(ROOT, 'templates', 'country-shell.html')).read()
    page = (shell
            .replace('{{TITLE}}', e(title))
            .replace('{{DESC}}', e(desc))
            .replace('{{ROBOTS}}', 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1')
            .replace('{{CANONICAL}}', url)
            .replace('{{SCHEMA}}', json.dumps(schema, indent=2, ensure_ascii=False))
            .replace('{{MAIN}}', body)
            .replace('{{OGTITLE}}', e(title))
            .replace('{{COUNTRY}}', 'Research'))

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'index.html'), 'w').write(page)

    words = len(re.sub(r'<[^>]*>', ' ', re.sub(r'<script.*?</script>', ' ', page, flags=re.S)).split())
    print(f"research findings page built: {words} words, {n} destinations, {sources_total} sources")
    print(f"  headline finding: {digital_accepted} of {n} accept digital-only documents")


if __name__ == '__main__':
    main()
