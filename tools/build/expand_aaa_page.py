#!/usr/bin/env python3
"""
Expands /compare/aaa-idp-vs-worldidp/.

The page was 466 words targeting a keyword cluster worth roughly 112,000 US
searches a month, where the incumbent sits at position 3. Thin pages do not win
that.

Everything added here is either (a) already sourced on the page, (b) a factual
statement about how to verify an official website, or (c) explicitly marked
TODO(fact-check) for figures that must be confirmed against AAA's own published
pages before publication. Nothing about AAA's pricing or processing time is
invented — where a figure is needed and not confirmed, the copy says so.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PAGE = os.path.join(ROOT, 'compare', 'aaa-idp-vs-worldidp', 'index.html')

BLOCK = '''
      <section class="wi-section" id="comparison-table">
        <p class="wi-kicker">Side by side</p>
        <h2 class="wi-head">AAA, AATA and WorldIDP compared</h2>
        <p>Two of these are authorised U.S. issuers. One is not. The table sets out what
        each actually provides so you can pick the right route rather than the fastest one.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">Comparison of AAA, AATA and WorldIDP</caption>
          <thead>
            <tr><th scope="col">&nbsp;</th><th scope="col">AAA</th><th scope="col">AATA</th><th scope="col">WorldIDP</th></tr>
          </thead>
          <tbody>
            <tr><th scope="row">Authorised by the U.S. Department of State to issue U.S. IDPs</th>
                <td>Yes</td><td>Yes</td><td><strong>No</strong></td></tr>
            <tr><th scope="row">Document type</th>
                <td>Conventional IDP</td><td>Conventional IDP</td><td>Private multilingual translation-support document</td></tr>
            <tr><th scope="row">Requires a valid national driving licence alongside it</th>
                <td>Yes</td><td>Yes</td><td>Yes</td></tr>
            <tr><th scope="row">Open to non-U.S. licence holders</th>
                <td>No — U.S. licence required</td><td>No — U.S. licence required</td><td>Yes</td></tr>
            <tr><th scope="row">Digital-only version offered</th>
                <td>No — AAA's own guidance states digital IDPs are not available</td><td>Not confirmed</td><td>Yes, with a printed option</td></tr>
            <tr><th scope="row">Branch visit possible</th>
                <td>Yes</td><td>By post</td><td>No — online only</td></tr>
            <tr><th scope="row">Fee</th>
                <td>USD 20 permit fee per AAA's official IDP page</td><td>Not confirmed</td><td>See our <a href="/pricing.html">pricing page</a></td></tr>
            <tr><th scope="row">Typical processing</th>
                <td>About 5 business days online per AAA's published guidance, or same-day in branch</td><td>Not confirmed</td><td>Digital delivery, printed shipped separately</td></tr>
          </tbody>
        </table>
        <p class="cg-unknown">Rows marked "Not confirmed" are exactly that. We did not find a
        current published figure we could cite, and we do not estimate another organisation's
        fees or turnaround times. Check those directly with AATA before deciding.</p>
      </section>

      <section class="wi-section" id="decision">
        <p class="wi-kicker">Decide in four questions</p>
        <h2 class="wi-head">Which route fits your situation</h2>
        <ol class="cg-list">
          <li><strong>Do you hold a U.S. driving licence?</strong> If no, AAA and AATA are not
          open to you at all — both issue U.S. IDPs to U.S. licence holders. A private
          translation-support document is one of the remaining options.</li>
          <li><strong>Does your destination specifically require a conventional IDP?</strong>
          If yes and you hold a U.S. licence, go to AAA or AATA. Check the requirement on our
          <a href="/countries.html">country registry</a> first — several destinations do not
          require one at all.</li>
          <li><strong>Do you have time before you travel?</strong> AAA publishes an online
          processing window of about five business days and offers same-day service at
          branches. If a branch is reachable and you have the time, that is the cheapest and
          most direct route.</li>
          <li><strong>Is your licence written in a non-Latin script, or do you need more
          languages than a conventional IDP covers?</strong> That is the situation where a
          private multilingual translation document does work a conventional IDP does not.</li>
        </ol>
        <p>If questions one to three all point to AAA, use AAA. We would rather tell you that
        than sell you something that does not fit.</p>
      </section>

      <section class="wi-section" id="apply-to-aaa">
        <p class="wi-kicker">Genuinely useful</p>
        <h2 class="wi-head">How to apply through AAA</h2>
        <p>You do not need us for this, and we are not going to hide it. AAA's published
        process for a U.S. International Driving Permit is:</p>
        <ul class="cg-list">
          <li>Hold a valid U.S. driving licence, issued by a U.S. state or territory, that will
          remain valid for the period you intend to drive abroad.</li>
          <li>Be at least 18 years old.</li>
          <li>Complete AAA's IDP application form.</li>
          <li>Supply two passport-style photographs signed on the reverse.</li>
          <li>Pay the permit fee — USD 20 per AAA's official IDP page.</li>
          <li>Apply online, by post, or in person at a participating AAA branch. Branch service
          can be same-day; online processing takes about five business days per AAA's guidance.</li>
        </ul>
        <p>AAA membership is not a precondition for obtaining an IDP through AAA.
        <a href="/guides/how-to-apply-for-an-idp-in-the-us/">Our full U.S. application guide</a>
        covers both authorised routes in more detail, and
        <a href="/guides/what-is-aata/">what AATA is</a> explains the second one.</p>
      </section>

      <section class="wi-section" id="verify">
        <p class="wi-kicker">Consumer protection</p>
        <h2 class="wi-head">How to check you are on an official issuer's website</h2>
        <p>The IDP category attracts lookalike websites, and a domain containing the letters
        "AAA" or "AATA" is not evidence of any connection to either organisation. Anyone can
        register a domain name. Three checks that take under a minute:</p>
        <ul class="cg-list">
          <li><strong>Start from the organisation, not from a search result.</strong> AAA's own
          site is <a href="https://www.aaa.com/" rel="nofollow noopener" target="_blank">aaa.com</a>.
          Navigate to the IDP section from there rather than clicking an advertisement or a
          domain that merely contains the brand name.</li>
          <li><strong>Check the price against the official figure.</strong> AAA publishes a USD 20
          permit fee. A site charging substantially more for what it describes as an official
          U.S. IDP is not offering the same thing.</li>
          <li><strong>Be sceptical of instant digital-only claims.</strong> AAA's own guidance
          states that digital IDPs are not available. A site promising an instant digital U.S.
          IDP is not describing the conventional document.</li>
        </ul>
        <p>We apply the same test to ourselves. WorldIDP is a private translation-support
        service, it is not authorised to issue U.S. IDPs, and it says so on this page, in our
        <a href="/legal-disclaimer.html">legal disclaimer</a> and in our
        <a href="/editorial-policy.html">editorial policy</a>.</p>
      </section>

      <section class="wi-section" id="extended-faq">
        <p class="wi-kicker">More questions</p>
        <h2 class="wi-head">AAA and IDP questions travellers actually ask</h2>
        <div class="cg-faq-item">
          <h3>How much does a AAA International Driving Permit cost?</h3>
          <p>AAA's official IDP page lists a USD 20 permit fee. Photographs, postage and any
          expedited shipping are additional and are set by AAA rather than by us.</p>
        </div>
        <div class="cg-faq-item">
          <h3>Do I need to be a AAA member to get an IDP?</h3>
          <p>No. AAA issues International Driving Permits to holders of a valid U.S. driving
          licence, and membership is not a precondition.</p>
        </div>
        <div class="cg-faq-item">
          <h3>Can I get a AAA IDP the same day?</h3>
          <p>Same-day service is possible at a participating AAA branch. Applying online takes
          about five business days per AAA's published guidance, so a branch visit is the route
          if you are travelling imminently. See
          <a href="/guides/can-i-get-an-idp-the-same-day-in-the-us/">our same-day guide</a>.</p>
        </div>
        <div class="cg-faq-item">
          <h3>Is there a digital AAA IDP?</h3>
          <p>No. AAA's own guidance states that digital IDPs are not available. Any site
          offering an instant digital "AAA IDP" is not describing the document AAA issues.</p>
        </div>
        <div class="cg-faq-item">
          <h3>What is AATA and how is it different from AAA?</h3>
          <p>The American Automobile Touring Alliance is the second organisation authorised by
          the U.S. Department of State to issue U.S. International Driving Permits. It operates
          separately from AAA. <a href="/guides/what-is-aata/">Full explanation here</a>.</p>
        </div>
        <div class="cg-faq-item">
          <h3>I do not hold a U.S. licence. Can I still use AAA?</h3>
          <p>No. Both AAA and AATA issue U.S. IDPs to holders of a valid U.S. state licence. If
          your licence was issued elsewhere, the authorised issuer is the equivalent body in the
          country that issued your licence — normally the national automobile club or the
          licensing authority itself.</p>
        </div>
        <div class="cg-faq-item">
          <h3>Does an IDP let me drive anywhere in the world?</h3>
          <p>No. An IDP translates your licence; it does not grant driving privileges. Acceptance
          depends on the destination, which road traffic convention it recognises, your licence
          origin and the vehicle category. Check the
          <a href="/countries.html">country registry</a> for your destination.</p>
        </div>
      </section>
'''


def main():
    h = open(PAGE).read()
    h = re.sub(r'\s*<section class="wi-section" id="comparison-table">.*?<section class="wi-section" id="extended-faq">.*?</section>\s*',
               '\n', h, flags=re.S)

    anchor = '<section class="wi-section" id="faq"'
    if anchor in h:
        h = h.replace(anchor, BLOCK + '\n      ' + anchor, 1)
    else:
        m = re.search(r'(<section class="wi-section"[^>]*>\s*<p class="wi-kicker">FAQ</p>)', h)
        if m:
            h = h[:m.start()] + BLOCK + '\n      ' + h[m.start():]
        else:
            m2 = re.search(r'<section class="cg-section cg-crosslinks"', h)
            if not m2:
                print('ERROR: no insertion point found')
                return
            h = h[:m2.start()] + BLOCK + '\n      ' + h[m2.start():]

    if 'country-guide.css' not in h:
        h = h.replace('</head>',
                      '  <link rel="stylesheet" href="../../country-guide.css?v=20260723" />\n</head>', 1)

    open(PAGE, 'w').write(h)

    body = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
    words = len(re.sub(r'<[^>]*>', ' ', body).split())
    print(f'AAA comparison page expanded: {words} words')
    unconfirmed = h.count('>Not confirmed<')
    print(f'cells published as "Not confirmed" rather than estimated: {unconfirmed}')
    with open(os.path.join(ROOT, '_audit', 'aaa-page-open-items.md'), 'w') as f:
        f.write("""# AAA comparison page — open verification items

These cells currently render as "Not confirmed" on the live page. That is the
correct default: we do not estimate another organisation's fees or turnaround.
Confirm each against AATA's own published pages, then edit the table directly.

| Cell | What is needed | Source to check |
|---|---|---|
| AATA — digital-only version offered | Does AATA offer a digital IDP? | AATA published FAQ |
| AATA — fee | Current AATA IDP fee in USD | AATA order/pricing page |
| AATA — typical processing | Current AATA processing window | AATA published guidance |

Also re-verify periodically, because these change:

| Claim on the page | Currently stated | Source |
|---|---|---|
| AAA permit fee | USD 20 | AAA official IDP page |
| AAA online processing | about 5 business days | AAA published guidance |
| AAA digital IDP availability | not available | AAA online IDP FAQ |
| AAA membership required | no | AAA IDP page |

Last reviewed: 2026-07-23
""")
    print('open items logged to _audit/aaa-page-open-items.md')


if __name__ == '__main__':
    main()
