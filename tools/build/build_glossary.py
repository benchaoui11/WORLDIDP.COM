#!/usr/bin/env python3
"""
Builds /glossary/ — the definitional layer.

Why: the market leader's strongest asset is that it owns the "what is X"
answers, and language models anchor an entity's definition to whoever states it
most clearly and consistently. A glossary with DefinedTerm markup is the
cheapest way to compete for that layer, and definitions are the single most
frequently extracted content type in AI answers.

Each definition is written to survive being quoted with no surrounding context —
that is the test applied to every entry here.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
OUT = os.path.join(ROOT, 'glossary')
TODAY = '2026-07-23'


def e(s):
    return html.escape(str(s), quote=True)


TERMS = [
 ("International Driving Permit", "international-driving-permit",
  "An International Driving Permit is a standardised multilingual translation of a national "
  "driving licence, issued under one of the United Nations road traffic conventions. It carries "
  "no driving privileges of its own and is valid only when presented together with the original "
  "national licence it translates.",
  "IDP"),
 ("1949 Geneva Convention on Road Traffic", "1949-geneva-convention",
  "The 1949 Geneva Convention on Road Traffic is a United Nations treaty that standardises the "
  "International Driving Permit and defines the format contracting states recognise. Japan, "
  "Thailand, India and the United States are among the states party to it. A permit issued under "
  "this convention is not automatically interchangeable with one issued under the 1968 Vienna "
  "Convention.", "1949 Convention"),
 ("1968 Vienna Convention on Road Traffic", "1968-vienna-convention",
  "The 1968 Vienna Convention on Road Traffic is the later United Nations road traffic treaty. "
  "Where two states are both party to it, it generally supersedes the 1949 Geneva Convention "
  "between them. Germany, Austria, Brazil and Russia are among the states party to it but not to "
  "the 1949 convention.", "1968 Convention"),
 ("Contracting state", "contracting-state",
  "A contracting state is a country that has formally acceded to a road traffic convention. Only a "
  "contracting state can authorise bodies within its territory to issue International Driving "
  "Permits, which is why authorisation comes from a government rather than from a company "
  "describing itself as official.", None),
 ("Authorised issuer", "authorised-issuer",
  "An authorised issuer is an organisation empowered by a contracting state to issue International "
  "Driving Permits to holders of that state's licences. In the United States there are exactly two: "
  "the American Automobile Association and the American Automobile Touring Alliance. A domain name "
  "containing a brand does not confer authorisation.", None),
 ("Licence translation document", "licence-translation-document",
  "A licence translation document is a private multilingual rendering of the information on a "
  "national driving licence. It is not issued under a road traffic convention, carries no legal "
  "standing of its own, and is useful only as a practical aid where an official or a rental desk "
  "cannot read the original licence.", "translation-support document"),
 ("Visitor rule", "visitor-rule",
  "A visitor rule is a national provision allowing a person to drive on a foreign licence for a "
  "defined period after arrival, without any permit. The United Kingdom applies a 12-month window, "
  "Turkey six months and Costa Rica the length of the authorised tourist stay. Where a visitor rule "
  "applies, an International Driving Permit is generally not what grants the entitlement.", None),
 ("Digital IDP", "digital-idp",
  "A digital IDP is an electronic copy of a driving-document translation, delivered as a file "
  "rather than on paper. Across the destinations WorldIDP has researched against official sources, "
  "no national authority has published a policy accepting a digital-only driving document. The "
  "American Automobile Association states that digital IDPs are not available.", None),
 ("Reciprocity", "reciprocity",
  "Reciprocity is an arrangement under which two states recognise each other's driving licences "
  "directly, without requiring a permit or translation. EU and EEA mutual recognition is the "
  "largest such arrangement, which is why an EU licence holder driving within the EU generally "
  "needs no International Driving Permit.", None),
 ("Licence origin", "licence-origin",
  "Licence origin is the country or jurisdiction that issued a driving licence. It, rather than "
  "nationality or residence, usually determines whether a permit or translation is expected — which "
  "is why the same requirement can differ between two people travelling together.", None),
 ("Non-Latin script licence", "non-latin-script-licence",
  "A non-Latin script licence is one printed in an alphabet such as Arabic, Cyrillic, Japanese, "
  "Korean, Thai or Chinese. Several countries base their translation requirement on readability "
  "rather than nationality, so a non-Latin script licence triggers a translation requirement where "
  "a Latin-script licence from the same country would not.", None),
 ("Green card insurance", "green-card-insurance",
  "A green card is an international motor insurance certificate evidencing that a vehicle carries "
  "the minimum liability cover required in the countries it will be driven through. It concerns the "
  "vehicle rather than the driver, and is separate from any driving licence or permit requirement.", None),
]


def main():
    n = len(TERMS)
    title = "International Driving Permit Glossary: Terms Defined | WorldIDP"
    desc = (f"Plain definitions of the {n} terms that decide whether you need a driving document "
            "abroad — conventions, authorised issuers, visitor rules, licence origin and the "
            "difference between an IDP and a private translation.")
    url = f"{SITE}/glossary/"

    entries = []
    for term, slug, definition, alt in TERMS:
        altline = (f'\n          <p class="cg-alt">Also written as: {e(alt)}</p>' if alt else '')
        entries.append(f'''        <div class="cg-term" id="{slug}">
          <h2>{e(term)}</h2>
          <p>{e(definition)}</p>{altline}
        </div>''')

    body = f'''    <article class="cg">
      <nav class="cg-crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">/</span>
        <span aria-current="page">Glossary</span>
      </nav>

      <h1>International Driving Permit Glossary</h1>

      <div class="cg-answer">
        <p>An International Driving Permit is a standardised multilingual translation of a national
        driving licence, issued under a United Nations road traffic convention. It carries no driving
        privileges of its own and is valid only alongside the original licence. The {n} definitions
        below cover the terms that actually decide what you need. Reviewed {TODAY}.</p>
      </div>

      <section class="cg-section" id="terms">
{chr(10).join(entries)}
      </section>

      <section class="cg-section" id="notes">
        <h2>How these definitions were written</h2>
        <p>Each definition is written to be correct when read on its own, with no surrounding
        context. Where a definition contains a factual claim about a specific country, that claim is
        sourced on the relevant <a href="/countries.html">country page</a> rather than restated here
        without evidence.</p>
        <p>The statement that no researched destination has published a policy accepting
        digital-only documents is a finding from our own dataset, not an assertion. The sample size,
        method and full figures are on the
        <a href="/research/idp-requirements-findings/">research findings page</a>, and the
        underlying data is <a href="/data/idp-country-requirements.csv">openly downloadable</a>.</p>
        <p class="cg-verified">Definitions last reviewed:
        <time datetime="{TODAY}">{TODAY}</time>.</p>
      </section>

      <section class="cg-section cg-related">
        <h2>Where these terms apply</h2>
        <ul class="cg-list">
          <li><a href="/what-is-idp.html">What an International Driving Permit actually is</a></li>
          <li><a href="/convention/1949-geneva/">How the 1949 Geneva Convention works</a></li>
          <li><a href="/convention/1968-vienna/">How the 1968 Vienna Convention differs</a></li>
          <li><a href="/compare/aaa-idp-vs-worldidp/">Authorised issuers compared with a private service</a></li>
          <li><a href="/countries.html">Requirements by destination</a></li>
        </ul>
      </section>
    </article>
'''

    defined = [{
        "@type": "DefinedTerm",
        "@id": f"{url}#{slug}",
        "name": term,
        "description": definition,
        "inDefinedTermSet": {"@id": f"{url}#termset"},
        **({"alternateName": alt} if alt else {}),
    } for term, slug, definition, alt in TERMS]

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Glossary", "item": url}]},
        {"@type": "DefinedTermSet", "@id": f"{url}#termset", "name":
         "International Driving Permit Glossary", "url": url,
         "description": desc, "inLanguage": "en",
         "publisher": {"@id": f"{SITE}/#organization"},
         "hasDefinedTerm": [{"@id": f"{url}#{s}"} for _, s, _, _ in TERMS]},
        *defined,
        {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc,
         "inLanguage": "en", "isPartOf": {"@id": f"{SITE}/#website"},
         "publisher": {"@id": f"{SITE}/#organization"}, "dateModified": TODAY,
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".cg-answer"]}},
    ]}

    shell = open(os.path.join(ROOT, 'templates', 'country-shell.html')).read()
    page = (shell
            .replace('{{TITLE}}', e(title)).replace('{{DESC}}', e(desc))
            .replace('{{ROBOTS}}', 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1')
            .replace('{{CANONICAL}}', url)
            .replace('{{SCHEMA}}', json.dumps(schema, indent=2, ensure_ascii=False))
            .replace('{{MAIN}}', body).replace('{{OGTITLE}}', e(title))
            .replace('{{COUNTRY}}', 'Glossary'))

    os.makedirs(OUT, exist_ok=True)
    open(os.path.join(OUT, 'index.html'), 'w').write(page)
    words = len(re.sub(r'<[^>]*>', ' ', re.sub(r'<script.*?</script>', ' ', page, flags=re.S)).split())
    print(f"glossary built: {n} DefinedTerm entries, {words} words")


if __name__ == '__main__':
    main()
