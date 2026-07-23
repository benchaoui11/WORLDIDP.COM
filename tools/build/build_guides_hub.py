#!/usr/bin/env python3
"""
Builds /guides/ — the hub for the US permit cluster.

Titles and descriptions are read from each guide's own rendered HTML rather than
maintained separately, so the hub can never describe a page differently from how
that page describes itself. That consistency is the point: an inconsistent hub
teaches a language model two competing summaries of the same document.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
TODAY = '2026-07-23'


def e(s):
    return html.escape(str(s), quote=True)


def main():
    guides = []
    gdir = os.path.join(ROOT, 'guides')
    for slug in sorted(os.listdir(gdir)):
        f = os.path.join(gdir, slug, 'index.html')
        if not os.path.isfile(f):
            continue
        h = open(f).read()
        t = re.search(r'<title>(.*?)</title>', h, re.S).group(1).split('|')[0].strip()
        d = re.search(r'<meta[^>]*?name="description"[^>]*?content="(.*?)"', h, re.S).group(1).strip()
        guides.append((slug, html.unescape(t), html.unescape(d)))

    items = '\n'.join(f'''        <div class="cg-term">
          <h2><a href="/guides/{s}/">{e(t)}</a></h2>
          <p>{e(d)}</p>
        </div>''' for s, t, d in guides)

    title = "How to Get a US International Driving Permit: Guides | WorldIDP"
    desc = (f"{len(guides)} sourced guides for US licence holders applying for an International "
            "Driving Permit before travelling: the two authorised issuers, real costs, when "
            "same-day is possible, and what applies if your licence was issued elsewhere.")
    url = f"{SITE}/guides/"

    body = f'''    <article class="cg">
      <nav class="cg-crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">/</span>
        <span aria-current="page">Guides</span>
      </nav>

      <h1>How to Get a US International Driving Permit</h1>

      <div class="cg-answer">
        <p>Only two organisations are authorised by the U.S. Department of State to issue United
        States International Driving Permits: the American Automobile Association and the American
        Automobile Touring Alliance. These {len(guides)} guides cover how each works, what a permit
        actually costs once photographs and postage are counted, when same-day is genuinely possible,
        and what applies if your licence was issued outside the United States. Reviewed {TODAY}.</p>
      </div>

      <section class="cg-section" id="guides">
{items}
      </section>

      <section class="cg-section" id="direction">
        <h2>Looking for the other direction?</h2>
        <p>These guides are for people holding a US licence who need a permit <em>before travelling
        abroad</em>. If you hold a foreign licence and want to know what applies when
        <em>driving inside the United States</em>, that is a different question with a different
        answer — see <a href="/countries/united-states/">driving in the United States on a foreign
        licence</a>.</p>
      </section>

      <section class="cg-section" id="beyond">
        <h2>Before you apply for anything</h2>
        <p>Check whether your destination requires a permit at all. Across the destinations we have
        researched against official sources, a permit requirement is less common than the market
        implies — several operate a visitor time-limit rule instead. The
        <a href="/countries.html">country registry</a> gives the sourced position per destination,
        and our <a href="/research/idp-requirements-findings/">research findings</a> set out what the
        dataset shows overall.</p>
        <p>Then check which convention your destination recognises, because a permit issued under the
        wrong one is not a substitute. The <a href="/convention/1949-geneva/">1949 Geneva</a> and
        <a href="/convention/1968-vienna/">1968 Vienna</a> explainers cover the distinction, and the
        <a href="/glossary/">glossary</a> defines the terms.</p>
        <p class="cg-verified">Guides last reviewed:
        <time datetime="{TODAY}">{TODAY}</time>.</p>
      </section>
    </article>
'''

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": url}]},
        {"@type": "CollectionPage", "@id": url, "url": url, "name": title, "description": desc,
         "inLanguage": "en", "isPartOf": {"@id": f"{SITE}/#website"},
         "publisher": {"@id": f"{SITE}/#organization"}, "dateModified": TODAY,
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".cg-answer"]},
         "mainEntity": {"@type": "ItemList", "numberOfItems": len(guides), "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "name": t, "url": f"{SITE}/guides/{s}/"}
             for i, (s, t, _) in enumerate(guides)]}}]}

    shell = open(os.path.join(ROOT, 'templates', 'country-shell.html')).read()
    page = (shell.replace('{{TITLE}}', e(title)).replace('{{DESC}}', e(desc))
            .replace('{{ROBOTS}}', 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1')
            .replace('{{CANONICAL}}', url)
            .replace('{{SCHEMA}}', json.dumps(schema, indent=2, ensure_ascii=False))
            .replace('{{MAIN}}', body).replace('{{OGTITLE}}', e(title))
            .replace('{{COUNTRY}}', 'Guides'))
    open(os.path.join(gdir, 'index.html'), 'w').write(page)
    print(f"guides hub built: {len(guides)} guides listed")


if __name__ == '__main__':
    main()
