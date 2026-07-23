#!/usr/bin/env python3
"""
Builds two pages designed against a specific competitor gap analysis.

--------------------------------------------------------------------------
PAGE 1  /countries/united-states/  (enriched data, rendered by the country
        generator) plus a US-specific extension block.

What the incumbents miss:

internationaldrivingpermit.org/country/united-states-of-america/
  Semrush: 1,079 US traffic, 991 keywords. Strongest page in the category.
  * Its 18-question FAQ is GENERIC — the identical block appears on every one
    of its 200+ country pages. Nothing on it is about the United States.
  * It carries no US driving information at all: no speed limits, no alcohol
    limit, no state variation, nothing about what to carry.
  * It cites no sources and shows no review date.
  * It never answers the actual query — "can I drive in the US on a foreign
    licence" — because it only covers outbound US licence holders.

internationaldriversassociation.com/international-drivers-license-united-states/
  Semrush: 186 traffic from 672 keywords — a collapsed domain.

The gap is therefore: state-level variation, real driving facts, sources, and
the inbound direction of the question. That is what this page covers.

--------------------------------------------------------------------------
PAGE 2  /guides/can-i-get-an-idp-the-same-day-in-the-us/

Competitor: fastidp.com/post/can-i-get-a-aaa-idp-same-day
  Semrush: 511 traffic, 26% of that entire domain, 98 keywords.

What they do well and we should match: a Quick Answer at the top, a named
byline, concrete numbers ($20 fee, $10-30 for photos, 20-60 minutes in branch),
and genuine operational detail — that AAA's online route runs through a third
party, and that AATA resumed issuing after a long gap.

What they leave open:
  * meta-robots is `max-image-preview:large` only — no index/follow directive
    and NO max-snippet:-1. They are capping their own snippet extraction.
  * No JSON-LD of any kind. No FAQPage, no Article, no author markup despite
    having a visible byline.
  * No sources section and no review date.
  * No structured comparison — the routes are described in prose only.
  * Their footer is duplicated three times in the served DOM.

Every claim about AAA below is drawn from AAA's own published material as cited
on the page. Nothing is estimated.
"""
import json, os, re, html

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
TODAY = '2026-07-23'


def e(s):
    return html.escape(str(s), quote=True)


# ══════════════════════════════════════════════════ PAGE 1 — US data
def enrich_us():
    p = os.path.join(ROOT, 'data', 'countries.json')
    d = json.load(open(p))
    us = [c for c in d if c['slug'] == 'united-states'][0]

    us.update({
        "idpStatus": "state-and-provider-dependent",
        "idpStatusApplies": (
            "Driving privileges for visitors are set by each state, not federally. "
            "Most states allow a visitor to drive on a valid foreign licence for a limited "
            "period, and a licence not written in English is where a translation or "
            "International Driving Permit becomes practically necessary"),
        "idpStatusExempt": (
            "A licence issued in English is generally readable without a translation, though "
            "the state's time limit still applies and rental company policy can be stricter "
            "than state law"),
        "speedUrbanKmh": 40, "speedUrbanMph": 25,
        "speedRuralKmh": 89, "speedRuralMph": 55,
        "speedMotorwayKmh": 113, "speedMotorwayMph": 70,
        "speedDisplayUnit": "mph",
        "bacLimit": 0.08,
        "bacNote": ("0.08 per cent in 49 states. Utah applies 0.05 per cent — the strictest in "
                    "the country. Every state applies zero or near-zero tolerance to drivers "
                    "under 21"),
        "minimumRentalAge": 21,
        "digitalDocumentStatus": "unclear",
        "digitalDocumentNote": (
            "No US state has published a policy accepting a digital-only driving document, and "
            "the American Automobile Association states that digital IDPs are not available. "
            "Treat printed as the only reliable format."),
        "documentsToCarry": [
            "Your original valid national driving licence — the document that grants privileges",
            "A translation or International Driving Permit where the licence is not in English",
            "Passport, which US rental companies routinely require from foreign visitors",
            "Proof of insurance — minimum liability cover is set by each state",
            "The rental agreement, which often carries stricter terms than state law"],
        "officialSources": [
            {"name": "USAGov — International Driving Permit",
             "url": "https://www.usa.gov/international-drivers-license"},
            {"name": "U.S. Department of State — Driving and road safety abroad",
             "url": "https://travel.state.gov/content/travel/en/international-travel/before-you-go/driving-and-road-safety.html"},
            {"name": "American Automobile Association — International Driving Permit",
             "url": "https://www.aaa.com/vacation/idpf.html"},
            {"name": "National Highway Traffic Safety Administration — Drunk driving",
             "url": "https://www.nhtsa.gov/risky-driving/drunk-driving"}],
        "lastVerified": TODAY,
        "relatedCountries": ["canada", "mexico", "united-kingdom"],
    })
    json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
    print('US country data enriched')


def us_notes():
    p = os.path.join(ROOT, 'data', 'country-notes.json')
    d = json.load(open(p))
    d['united-states'] = {
        "licenceOriginNotes": (
            "This question runs in two directions and they have different answers. "
            "**Driving into the United States on a foreign licence:** privileges are set by each "
            "state, most allow a visiting driver a limited period on a valid foreign licence, and "
            "the practical trigger for a translation is language — a licence not in English is one "
            "an officer or rental agent cannot read. "
            "**US licence holders driving abroad:** only two organisations are authorised by the "
            "U.S. Department of State to issue US International Driving Permits — the American "
            "Automobile Association and the American Automobile Touring Alliance. No third "
            "organisation can become authorised by describing itself as official. "
            "One rule catches people out in both directions: an IDP must be issued in the country "
            "that issued your licence. A UK licence holder cannot obtain a US IDP from AAA, and a "
            "US licence holder cannot obtain one abroad."),
        "rentalNotes": (
            "Rental policy is the binding constraint for most visitors, and it is set by the "
            "company rather than the state. Several major providers require a translation for any "
            "licence not written in English regardless of what state law says. Minimum age is "
            "commonly 21, with substantial young-driver surcharges applied below 25 and some "
            "vehicle classes excluded entirely. A passport is routinely requested alongside the "
            "licence from foreign visitors."),
        "roadsideCheckNotes": (
            "Enforcement is by state and local agencies, and rules differ meaningfully across "
            "state lines. The alcohol limit is 0.08 per cent in 49 states; Utah alone applies "
            "0.05 per cent. Speed limits range from 25 mph in residential areas to 85 mph on one "
            "Texas toll road — the widest spread of any country in this registry. Present the "
            "original licence; a translation supports it and never replaces it."),
        "countrySpecificNotes": [
            "The United States is party to the 1949 Geneva Convention.",
            "Driving privileges for visiting drivers are set at state level, not federally — there is no single national rule.",
            "AAA and AATA are the only two organisations authorised by the U.S. Department of State to issue US International Driving Permits.",
            "An IDP must be issued in the country that issued your licence, so AAA cannot issue one to a foreign licence holder.",
            "Utah applies a 0.05 per cent alcohol limit; the other 49 states apply 0.08 per cent.",
            "Speed limits are posted in miles per hour and range from 25 mph residential to 85 mph on one Texas toll road.",
            "Right turn on red is permitted in most states unless a sign prohibits it — a rule with almost no equivalent in Europe.",
            "Minimum liability insurance amounts are set by each state and differ substantially.",
        ],
        "faq": [
            {"q": "Do you need an International Driving Permit to drive in the United States?",
             "a": "It depends on the state and on your rental provider. Most states allow a visitor to drive on a valid foreign licence for a limited period. A licence not written in English is where a translation or IDP becomes practically necessary, and rental company policy is often stricter than state law."},
            {"q": "Can I drive in the US with a UK, EU or Australian licence?",
             "a": "Generally yes for a limited period, and because those licences are in English no translation is normally needed. Check the specific state you will be driving in, and confirm your rental provider's own documentation policy separately."},
            {"q": "Who issues International Driving Permits in the United States?",
             "a": "The American Automobile Association and the American Automobile Touring Alliance. They are the only two organisations authorised by the U.S. Department of State. Both issue to holders of a valid US state licence."},
            {"q": "Can a foreign visitor get an IDP from AAA while in the United States?",
             "a": "No. An International Driving Permit must be issued in the country that issued your driving licence. A UK licence holder needs a UK-issued IDP, obtained before travelling."},
            {"q": "Is a digital IDP accepted in the United States?",
             "a": "No US state has published a policy accepting a digital-only driving document, and AAA states that digital IDPs are not available. Treat printed as the only reliable format."},
            {"q": "What is the drink-drive limit in the United States?",
             "a": "0.08 per cent in 49 states. Utah applies 0.05 per cent, the strictest in the country. Every state applies zero or near-zero tolerance to drivers under 21."},
            {"q": "What are the speed limits in the United States?",
             "a": "They vary by state and road type, posted in miles per hour: roughly 25 mph residential, 55 to 70 mph on rural highways and interstates, with a maximum of 85 mph on one Texas toll road. Posted signs govern."},
            {"q": "How long can I drive in the US on a foreign licence?",
             "a": "The permitted period is set by each state rather than federally, so there is no single answer. Check the rules of the specific state where you will be driving, and note that becoming a resident brings separate licensing requirements."},
        ],
    }
    json.dump(d, open(p, 'w'), indent=2, ensure_ascii=False)
    print('US notes written: 8 US-specific FAQs, 8 country notes')


# ══════════════════════════════════════════════════ PAGE 2 — same-day guide
def build_same_day():
    slug = 'can-i-get-an-idp-the-same-day-in-the-us'
    out = os.path.join(ROOT, 'guides', slug)
    url = f'{SITE}/guides/{slug}/'

    title = "Can You Get an IDP the Same Day in the US? 2026 Answer"
    desc = ("Same-day US International Driving Permits are possible in one way only: in person at "
            "a participating AAA branch. Here is what each route actually delivers, what to bring, "
            "and what to do if no branch is reachable.")

    answer = ("Yes, but through one route only. A participating AAA branch can issue a US "
              "International Driving Permit in person the same day, typically in well under an "
              "hour once your paperwork is complete. Every other route — AAA online, AATA by post "
              "— takes days. No digital-only same-day US IDP exists; AAA states digital IDPs are "
              "not available. Sources reviewed 23 July 2026.")

    faq = [
        ("Can you get a AAA International Driving Permit the same day?",
         "Yes, at a participating AAA branch in person. Not every branch issues permits, so call the specific branch first and confirm both that it issues IDPs and that it can do so while you wait."),
        ("What do I need to bring to get an IDP the same day?",
         "Your valid US state driving licence, two passport-style photographs signed on the reverse, a completed application form, and payment of the USD 20 permit fee. Arriving without the photographs is the most common reason a same-day visit fails."),
        ("How long does it take in the branch?",
         "Once your documents are complete, issuance is generally a matter of minutes rather than days. Queue length rather than processing is usually what determines how long you are there."),
        ("Can I get a same-day IDP online?",
         "No. AAA's published online processing window is about five business days before anything ships. Paying for expedited shipping speeds delivery, not processing."),
        ("Is there an instant digital US IDP?",
         "No. AAA states that digital IDPs are not available. A website offering an instant digital 'US IDP' is not describing the document AAA issues."),
        ("Does WorldIDP offer a same-day US IDP?",
         "No, and we will not suggest otherwise. WorldIDP prepares a private multilingual translation-support document. It is not a US International Driving Permit and it is not a substitute for one. If you need a conventional US IDP today, a AAA branch is the route."),
        ("What if no AAA branch near me issues IDPs?",
         "First check whether your destination requires one at all — several do not. Our country registry states the position per destination with the official sources used and the date we checked them."),
        ("Can a foreign licence holder get a same-day IDP in the US?",
         "No. An IDP must be issued in the country that issued your licence, so AAA cannot issue one to a visitor holding a foreign licence regardless of urgency."),
    ]

    faq_html = '\n'.join(f'''        <div class="cg-faq-item">
          <h3>{e(q)}</h3>
          <p>{e(a)}</p>
        </div>''' for q, a in faq)

    body = f'''    <article class="cg">
      <nav class="cg-crumbs" aria-label="Breadcrumb">
        <a href="/">Home</a> <span aria-hidden="true">/</span>
        <a href="/guides/">Guides</a> <span aria-hidden="true">/</span>
        <span aria-current="page">Same-day IDP in the US</span>
      </nav>

      <h1>Can You Get an International Driving Permit the Same Day in the US?</h1>

      <div class="cg-answer">
        <p>{e(answer)}</p>
      </div>

      <section class="cg-section" id="routes">
        <h2>What each route actually delivers</h2>
        <p>Three different things get described as fast, and only one of them puts a conventional US
        International Driving Permit in your hand today.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">Same-day comparison of routes to a US International Driving Permit</caption>
          <thead>
            <tr><th scope="col">Route</th><th scope="col">Same day?</th><th scope="col">What you actually get</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">AAA branch, in person</th><td><strong>Yes</strong></td>
                <td>A conventional US IDP, issued while you wait, at participating branches only.</td></tr>
            <tr><th scope="row">AAA online</th><td>No</td>
                <td>A conventional US IDP after about five business days of processing per AAA's published guidance, then shipping.</td></tr>
            <tr><th scope="row">AATA by post</th><td>No</td>
                <td>A conventional US IDP. AATA is the second authorised issuer; its current turnaround is not confirmed here.</td></tr>
            <tr><th scope="row">A site selling an "instant digital IDP"</th><td>No</td>
                <td>Not a conventional US IDP. AAA states digital IDPs are not available.</td></tr>
            <tr><th scope="row">WorldIDP</th><td>No</td>
                <td>A private multilingual translation-support document. Not a US IDP and not a substitute for one.</td></tr>
          </tbody>
        </table>
        <p class="cg-unknown">We do not state another organisation's current turnaround from memory.
        Where a figure is not confirmed against a live official page, this table says so.</p>
      </section>

      <section class="cg-section" id="how">
        <h2>How the same-day branch route works</h2>
        <ol class="cg-list">
          <li><strong>Call the specific branch first.</strong> Not every AAA location issues
          International Driving Permits, and a branch can issue them without offering same-day
          service. Those are two separate questions — ask both.</li>
          <li><strong>Bring your valid US state driving licence.</strong> The physical card, not a
          photograph of it. The permit translates that licence and has no standing without it.</li>
          <li><strong>Bring two passport-style photographs, signed on the reverse.</strong> This is
          the single most common reason a same-day visit fails. Some branches can take them for you
          at additional cost; not all can.</li>
          <li><strong>Complete the application form.</strong> Filling it in before you arrive saves
          time at the counter.</li>
          <li><strong>Pay the USD 20 permit fee.</strong> That is AAA's published permit fee.
          Photographs and any additional services are separate.</li>
          <li><strong>Collect the booklet.</strong> Once the paperwork is complete, issuance is a
          matter of minutes. Arriving well before closing matters more than anything else.</li>
        </ol>
        <p>You must be at least 18 and hold a valid US state-issued licence. AAA membership is not
        required. Our <a href="/guides/how-to-apply-for-an-idp-in-the-us/">full US application
        guide</a> covers both authorised routes.</p>
      </section>

      <section class="cg-section" id="decision">
        <h2>If you are travelling within 48 hours</h2>
        <ol class="cg-list">
          <li><strong>Check whether you need one at all.</strong> This resolves a large share of
          urgent cases and costs nothing. Several popular destinations operate a visitor rule rather
          than a permit requirement — <a href="/countries/united-kingdom/">the UK</a> allows 12
          months on a foreign licence, <a href="/countries/ireland/">Ireland</a> the same, and
          <a href="/countries/iceland/">Iceland</a> accepts a Latin-script licence as it stands. Our
          <a href="/countries.html">country registry</a> gives the sourced position per
          destination.</li>
          <li><strong>Check which convention your destination recognises.</strong>
          <a href="/countries/japan/">Japan recognises the 1949 Geneva Convention only</a>. A permit
          issued under the wrong convention is not a substitute, and no amount of speed fixes
          that.</li>
          <li><strong>If you do need one and hold a US licence</strong>, call a participating AAA
          branch today.</li>
          <li><strong>If no branch is reachable</strong>, understand precisely what remains. A
          private translation-support document is not a conventional IDP, and we are not going to
          tell you it is. Where the practical problem is a rental desk unable to read a licence in
          an unfamiliar script, it addresses that specific problem and nothing more.</li>
        </ol>
      </section>

      <section class="cg-section" id="what-we-are">
        <h2>What WorldIDP is, on this page as everywhere else</h2>
        <p>WorldIDP is an independent private service operated by WORLDIDP INTERNATIONAL LLC that
        prepares a multilingual translation-support document for a valid national driving licence.
        It is not a government agency and is not authorised to issue International Driving Permits.
        The document is carried alongside the original national driving licence and does not replace
        it.</p>
        <p>If a conventional US International Driving Permit is what you need today, AAA is the
        answer and we would rather say so than sell you something that does not fit. See
        <a href="/compare/aaa-idp-vs-worldidp/">the full comparison</a>, including
        <a href="/compare/aaa-idp-vs-worldidp/#verify">how to check you are on an official issuer's
        website</a>.</p>
      </section>

      <section class="cg-section" id="faq">
        <h2>Same-day IDP questions</h2>
{faq_html}
      </section>

      <section class="cg-section" id="sources">
        <h2>Sources used on this page</h2>
        <ul class="cg-sources">
          <li><a href="https://www.usa.gov/international-drivers-license" rel="nofollow noopener" target="_blank">USAGov — International Driving Permit</a></li>
          <li><a href="https://www.aaa.com/vacation/idpf.html" rel="nofollow noopener" target="_blank">American Automobile Association — International Driving Permit</a></li>
          <li><a href="https://travel.state.gov/content/travel/en/international-travel/before-you-go/driving-and-road-safety.html" rel="nofollow noopener" target="_blank">U.S. Department of State — Driving and road safety abroad</a></li>
        </ul>
        <p class="cg-verified">Sources last reviewed:
        <time datetime="{TODAY}">{TODAY}</time>. Figures we could not confirm against a live
        official page are marked as unconfirmed rather than estimated. Our
        <a href="/editorial-policy.html">editorial policy</a> sets out the standard.</p>
      </section>

      <section class="cg-section cg-related">
        <h2>Related guidance</h2>
        <ul class="cg-list">
          <li><a href="/guides/how-to-apply-for-an-idp-in-the-us/">The full US application process, both authorised routes</a></li>
          <li><a href="/guides/aaa-office-locations-for-idps/">Why not every AAA branch issues permits</a></li>
          <li><a href="/guides/aaa-idp-cost-and-turnaround/">What a US IDP actually costs once photographs and postage are counted</a></li>
          <li><a href="/guides/what-is-aata/">AATA, the second authorised issuer</a></li>
          <li><a href="/countries/united-states/">Driving in the United States on a foreign licence</a></li>
          <li><a href="/research/idp-requirements-findings/">Our findings on digital documents across 25 destinations</a></li>
        </ul>
      </section>
    </article>
'''

    schema = {"@context": "https://schema.org", "@graph": [
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": "Guides", "item": f"{SITE}/guides/"},
            {"@type": "ListItem", "position": 3, "name": "Same-day IDP in the US", "item": url}]},
        {"@type": "Article", "@id": url + "#article", "url": url,
         "headline": "Can You Get an International Driving Permit the Same Day in the US?",
         "description": desc, "inLanguage": "en",
         "datePublished": TODAY, "dateModified": TODAY,
         "author": {"@id": f"{SITE}/#organization"},
         "publisher": {"@id": f"{SITE}/#organization"},
         "isPartOf": {"@id": f"{SITE}/#website"},
         "about": [{"@type": "Thing", "name": "International Driving Permit"},
                   {"@type": "Organization", "name": "American Automobile Association"}],
         "citation": ["https://www.usa.gov/international-drivers-license",
                      "https://www.aaa.com/vacation/idpf.html"],
         "speakable": {"@type": "SpeakableSpecification", "cssSelector": [".cg-answer"]}},
        {"@type": "FAQPage", "@id": url + "#faq", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in faq]},
        {"@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc,
         "inLanguage": "en", "isPartOf": {"@id": f"{SITE}/#website"},
         "publisher": {"@id": f"{SITE}/#organization"}, "dateModified": TODAY},
    ]}

    shell = open(os.path.join(ROOT, 'templates', 'country-shell.html')).read()
    page = (shell
            .replace('{{TITLE}}', e(title)).replace('{{DESC}}', e(desc))
            .replace('{{ROBOTS}}', 'index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1')
            .replace('{{CANONICAL}}', url)
            .replace('{{SCHEMA}}', json.dumps(schema, indent=2, ensure_ascii=False))
            .replace('{{MAIN}}', body).replace('{{OGTITLE}}', e(title))
            .replace('{{COUNTRY}}', 'United States'))

    os.makedirs(out, exist_ok=True)
    open(os.path.join(out, 'index.html'), 'w').write(page)
    words = len(re.sub(r'<[^>]*>', ' ', re.sub(r'<script.*?</script>', ' ', page, flags=re.S)).split())
    print(f'same-day guide built: {words} words, {len(faq)} FAQ entries')


if __name__ == '__main__':
    enrich_us()
    us_notes()
    build_same_day()
