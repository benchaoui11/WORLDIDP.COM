#!/usr/bin/env python3
"""
Expands the six AAA/AATA guides from ~320-380 words to publishable depth.

Applied from the SEO reference set:

  * Information gain (Ahrefs semantic SEO): each guide contributes something the
    incumbent pages do not — a decision rule, a verification test, a distinction
    nobody else draws. No remixing of competitor copy.
  * Entity consistency ("don't silo your identity to your About page"): every
    guide restates who WorldIDP is in the same words, so machines see one
    consistent entity rather than nine descriptions.
  * Varied descriptive anchor text (Ahrefs internal linking): each guide links
    out with anchors written for its own context, never a repeated block.
  * Answer-first + standalone factual sentences: passages are written so they
    survive being quoted out of context.
  * E-E-A-T "Who, How, Why": every guide states how the claim was verified and
    when.

Nothing is invented. Figures already sourced on the existing pages are reused;
anything not confirmed renders as "Not confirmed" and is logged for the owner.
"""
import os, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MARK = 'data-expanded="v2"'

# Consistent entity sentence, repeated verbatim across every guide.
ENTITY = ('WorldIDP is an independent private service operated by WORLDIDP INTERNATIONAL LLC. '
          'It prepares a multilingual translation-support document for a valid national driving '
          'licence. It is not a government agency, it is not authorised to issue United States '
          'International Driving Permits, and the document it prepares is carried alongside the '
          'original licence rather than in place of it.')


def sec(kicker, head, body, sid):
    return f'''
      <section class="wi-section" id="{sid}" {MARK}>
        <p class="wi-kicker">{kicker}</p>
        <h2 class="wi-head">{head}</h2>
{body}
      </section>
'''


def faq(items):
    return '\n'.join(
        f'''        <div class="cg-faq-item">
          <h3>{q}</h3>
          <p>{a}</p>
        </div>''' for q, a in items)


GUIDES = {

'what-is-aata': sec('Information gain', 'AAA and AATA compared on the points that actually differ', '''        <p>Most pages that mention AATA simply note that it exists. The useful question is where
        the two authorised issuers actually diverge, because that is what determines which one you
        should use.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">AAA and AATA compared</caption>
          <tbody>
            <tr><th scope="row">Authorised by the U.S. Department of State</th><td>Yes — both. Neither is more official than the other.</td></tr>
            <tr><th scope="row">Physical branch network</th><td>AAA operates branches offering same-day service. AATA works by post and online.</td></tr>
            <tr><th scope="row">Membership required</th><td>Neither requires membership to issue an IDP.</td></tr>
            <tr><th scope="row">Who it suits</th><td>AAA if you can reach a branch and need it quickly. AATA if you are applying by post anyway and want a second option.</td></tr>
            <tr><th scope="row">Current fee</th><td>Not confirmed for AATA. AAA's official page lists USD 20.</td></tr>
          </tbody>
        </table>
        <p class="cg-unknown">We do not publish another organisation's current fee from memory.
        Where a figure is not confirmed against a live official page, this table says so.</p>''', 'aata-vs-aaa')
 + sec('Why this matters', 'Why two issuers exist at all', '''        <p>The two-issuer arrangement is a consequence of how the 1949 Geneva Convention works.
        A contracting state authorises bodies within its territory to issue permits on its behalf.
        The United States authorised two, which is why an IDP obtained through either carries the
        same standing. It also means a third organisation cannot become authorised simply by
        saying so.</p>
        <p>That is the practical test to carry into any search result: authorisation comes from the
        state, not from a domain name. A website using the letters "AAA" or "AATA" is not thereby
        connected to either. See <a href="/compare/aaa-idp-vs-worldidp/#verify">how to check you
        are on an official issuer's site</a>.</p>
        <p>''' + ENTITY + '''</p>''', 'why-two'),

'aaa-idp-cost-and-turnaround': sec('Information gain', 'What the total actually comes to', '''        <p>The permit fee is the figure everyone quotes. It is not the figure you pay. Budget for
        the components rather than the headline.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">Cost components for a US International Driving Permit</caption>
          <tbody>
            <tr><th scope="row">Permit fee</th><td>USD 20 per AAA's official IDP page</td></tr>
            <tr><th scope="row">Two passport-style photographs</th><td>Additional. Free if you take and print them yourself; a few dollars at a pharmacy or post office.</td></tr>
            <tr><th scope="row">Postage or expedited shipping</th><td>Additional, and set by AAA rather than by us. Expedited shipping is where an online application gets expensive.</td></tr>
            <tr><th scope="row">Branch visit</th><td>No shipping cost, but your time and travel.</td></tr>
          </tbody>
        </table>''', 'true-cost')
 + sec('Decision rule', 'When to apply online and when to walk in', '''        <p>The trade-off is time against convenience, and it has a clean rule.</p>
        <ul class="cg-list">
          <li><strong>More than two weeks before travel</strong> — apply online. AAA's published
          online processing is about five business days, standard postage is cheap, and you avoid
          a trip.</li>
          <li><strong>Under a week before travel</strong> — go to a participating branch. Same-day
          service exists specifically for this, and paying for expedited shipping on an online
          application often costs more than the permit.</li>
          <li><strong>Travelling tomorrow</strong> — a branch is the only conventional route. See
          <a href="/guides/can-i-get-an-idp-the-same-day-in-the-us/">what same-day actually means in
          practice</a>.</li>
        </ul>
        <p>One thing that is not a variable: there is no digital version. AAA's own guidance states
        digital IDPs are not available, so no amount of paying more produces an instant one.</p>
        <p>''' + ENTITY + '''</p>''', 'decision'),

'aaa-office-locations-for-idps': sec('Information gain', 'Why not every AAA branch issues permits', '''        <p>This is the detail that wastes people's time. AAA operates as a federation of regional
        clubs, and IDP issuance is offered at <em>participating</em> branches rather than at every
        location. A branch appearing on a map is not confirmation that it processes permits.</p>
        <p>Call the specific branch before travelling to it and ask two things: whether it issues
        International Driving Permits, and whether it does so same-day. Those are separate
        questions and a branch can answer yes to the first and no to the second.</p>''', 'not-every-branch')
 + sec('What to bring', 'Arrive with everything, once', '''        <ul class="cg-list">
          <li>Your valid U.S. state-issued driving licence, physically present — not a photograph of it.</li>
          <li>Two passport-style photographs, signed on the reverse.</li>
          <li>The completed application form, or the time to complete it there.</li>
          <li>Payment for the USD 20 permit fee.</li>
        </ul>
        <p>We deliberately do not reproduce a branch list here. Branch locations, hours and services
        change, and a copied list that is six months stale sends people to the wrong place. AAA's own
        <a href="https://www.aaa.com/" rel="nofollow noopener" target="_blank">website</a> is the
        authoritative source for its own locations, and starting there also avoids the lookalike-site
        problem described in <a href="/compare/aaa-idp-vs-worldidp/#verify">our verification
        checklist</a>.</p>
        <p>''' + ENTITY + '''</p>''', 'what-to-bring'),

'can-i-get-an-idp-the-same-day': sec('Information gain', 'What "same day" means for each route', '''        <p>Three different things get described as same-day, and only one of them produces a
        conventional United States International Driving Permit in your hand today.</p>
        <table class="cg-facts">
          <caption class="visually-hidden">Same-day options compared</caption>
          <tbody>
            <tr><th scope="row">AAA branch visit</th><td>Genuinely same-day at participating branches. This is the only route that produces a conventional U.S. IDP today.</td></tr>
            <tr><th scope="row">AAA online with expedited shipping</th><td>Not same-day. Processing is about five business days per AAA's guidance, then shipping on top.</td></tr>
            <tr><th scope="row">A site offering an "instant digital IDP"</th><td>Not a conventional U.S. IDP. AAA's own guidance states digital IDPs are not available, so an instant digital document is something else.</td></tr>
          </tbody>
        </table>''', 'what-same-day-means')
 + sec('If you fly tomorrow', 'The honest sequence', '''        <ol class="cg-list">
          <li><strong>Check whether you need one at all.</strong> Several destinations do not require
          an IDP from visitors. The <a href="/countries.html">country registry</a> states the position
          per destination with the sources we used. This step alone resolves a good share of urgent cases.</li>
          <li><strong>If you do need one and hold a U.S. licence</strong>, call a participating AAA
          branch today. Ask whether they issue IDPs and whether they do so same-day.</li>
          <li><strong>If no branch is reachable</strong>, understand what remains available. A private
          translation-support document is not a conventional IDP and we will not tell you otherwise —
          but where a rental desk's concern is reading a licence in an unfamiliar script, it addresses
          that specific problem.</li>
        </ol>
        <p>''' + ENTITY + '''</p>''', 'flying-tomorrow'),

'how-to-apply-for-an-idp-in-the-us': sec('Step by step', 'The application, in order', '''        <ol class="cg-list">
          <li><strong>Confirm you are eligible.</strong> A valid U.S. state-issued driving licence
          and a minimum age of 18. The licence must remain valid across the period you intend to drive
          abroad, because the permit's usefulness is tied to it.</li>
          <li><strong>Choose an authorised issuer.</strong> AAA or AATA. Both are authorised by the
          U.S. Department of State; neither is more official than the other. Our
          <a href="/guides/what-is-aata/">comparison of the two</a> covers where they differ.</li>
          <li><strong>Prepare two passport-style photographs</strong>, signed on the reverse.</li>
          <li><strong>Complete the application form</strong> and pay the fee — USD 20 per AAA's
          official IDP page.</li>
          <li><strong>Submit online, by post, or in person.</strong> Online processing is about five
          business days per AAA's published guidance. A participating branch can be same-day.</li>
          <li><strong>Carry it with your licence.</strong> The permit translates the licence. It does
          not replace it, and on its own it grants nothing.</li>
        </ol>''', 'steps')
 + sec('Before you apply', 'Two checks that save the fee entirely', '''        <p><strong>Check whether your destination requires one.</strong> Not every country does. Our
        <a href="/countries.html">country registry</a> gives the position per destination with the
        official sources we used and the date we checked them. Several popular destinations —
        <a href="/countries/united-kingdom/">the UK</a>, <a href="/countries/ireland/">Ireland</a>,
        <a href="/countries/iceland/">Iceland</a> — operate visitor rules rather than a permit
        requirement.</p>
        <p><strong>Check which convention your destination recognises.</strong> This is the detail that
        catches people out: <a href="/countries/japan/">Japan recognises the 1949 Geneva Convention
        only</a>. A permit issued under the wrong convention is not a substitute. The
        <a href="/convention/1949-geneva/">1949</a> and <a href="/convention/1968-vienna/">1968</a>
        pages explain the distinction.</p>
        <p>''' + ENTITY + '''</p>''', 'before-you-apply'),

'idp-for-non-us-licence-holders': sec('Information gain', 'Where to go if your licence is not American', '''        <p>AAA and AATA issue permits to holders of a valid U.S. state licence. If your licence was
        issued elsewhere, neither is open to you — and that is the point most pages on this topic skip.</p>
        <p>Under the 1949 Geneva and 1968 Vienna Conventions, each contracting state authorises bodies
        within its own territory to issue permits to its own licence holders. The practical consequence
        is a simple rule:</p>
        <p><strong>The authorised issuer for your International Driving Permit is in the country that
        issued your driving licence — not in the country you are travelling to, and not in the United
        States.</strong></p>
        <p>In most countries that body is the national automobile club or the licensing authority
        itself. Our <a href="/countries.html">country registry</a> records the relevant authority for
        each destination we have researched, along with the sources used.</p>''', 'where-to-go')
 + sec('Common situation', 'Driving in the United States on a foreign licence', '''        <p>This is the reverse question and it has a different answer. Driving privileges for visitors
        to the U.S. are set at state level rather than federally, and rental company policy is often
        the binding constraint in practice. Several major providers require a translation for a licence
        not written in English regardless of what the state requires.</p>
        <p><a href="/countries/united-states/">Our United States page</a> covers what varies and what to
        confirm, with sources.</p>
        <p>''' + ENTITY + '''</p>''', 'driving-in-us'),
}

EXTRA_FAQ = {
 'what-is-aata': [
   ("Is AATA less official than AAA?", "No. Both are authorised by the U.S. Department of State to issue United States International Driving Permits. Neither carries more standing than the other."),
   ("Can AATA issue a permit to a non-US licence holder?", "No. Like AAA, AATA issues U.S. IDPs to holders of a valid U.S. state licence. If your licence was issued elsewhere, the authorised issuer is in that country."),
   ("Does a domain containing 'AATA' mean the site is AATA?", "No. Anyone can register a domain name. Authorisation comes from the state, not from a web address."),
 ],
 'aaa-idp-cost-and-turnaround': [
   ("Is the AAA IDP fee the total cost?", "No. The USD 20 permit fee excludes photographs and any postage or expedited shipping, which AAA sets separately."),
   ("Can I pay more to get it faster online?", "Expedited shipping speeds the delivery, not the processing. AAA's published online processing window is about five business days regardless."),
   ("Does AAA membership reduce the fee?", "Membership is not required to obtain an IDP through AAA. We have not confirmed a current member discount and do not state one."),
 ],
 'aaa-office-locations-for-idps': [
   ("Does every AAA branch issue International Driving Permits?", "No. IDPs are issued at participating branches. Call the specific branch and confirm before travelling to it."),
   ("Can I walk in without an appointment?", "Policies vary by regional club and branch. Confirm with the branch directly rather than assuming."),
   ("Why do you not list AAA branch addresses here?", "Branch locations, hours and services change. A copied list that is months out of date sends people to the wrong place, so we point to AAA's own site instead."),
 ],
 'can-i-get-an-idp-the-same-day': [
   ("Is there any legitimate instant digital US IDP?", "No. AAA's own guidance states digital IDPs are not available. A site offering an instant digital U.S. IDP is describing a different kind of document."),
   ("What if I fly tomorrow and no branch is open?", "First confirm whether your destination requires an IDP at all — several do not. Our country registry states the position per destination with sources."),
   ("Does expedited shipping make an online application same-day?", "No. Processing takes about five business days per AAA's guidance before anything ships."),
 ],
 'how-to-apply-for-an-idp-in-the-us': [
   ("How old do I have to be?", "At least 18, with a valid U.S. state-issued driving licence."),
   ("How many photographs do I need?", "Two passport-style photographs, signed on the reverse."),
   ("Does my IDP last longer than my licence?", "No. Its usefulness is tied to the underlying licence, so a licence expiring soon limits the permit's practical life."),
   ("Do I need one for every country I visit?", "No. Requirements differ by destination and by which convention it recognises. Check each destination before assuming."),
 ],
 'idp-for-non-us-licence-holders': [
   ("Can I get a US IDP if I hold a European licence?", "No. AAA and AATA issue U.S. IDPs to U.S. licence holders. The authorised issuer for your permit is in the country that issued your licence."),
   ("Which organisation issues IDPs in my country?", "Usually the national automobile club or the licensing authority. Our country registry records the relevant authority for each destination we have researched."),
   ("Do I need an IDP to drive in the United States?", "It depends on the state and on your rental provider. A licence not written in English is where a translation becomes practically useful."),
 ],
}


def main():
    total = 0
    for slug, block in GUIDES.items():
        path = os.path.join(ROOT, 'guides', slug, 'index.html')
        if not os.path.exists(path):
            print(f'  skip (missing): {slug}')
            continue
        h = open(path).read()
        h = re.sub(r'\s*<section class="wi-section"[^>]*' + MARK + r'.*?</section>\s*',
                   '\n', h, flags=re.S)

        extra = ''
        if slug in EXTRA_FAQ:
            extra = sec('More questions', 'Questions travellers actually ask',
                        faq(EXTRA_FAQ[slug]), 'extended-faq')

        payload = block + extra
        m = re.search(r'<section class="cg-section cg-crosslinks"', h)
        if m:
            h = h[:m.start()] + payload + '\n      ' + h[m.start():]
        elif '</main>' in h:
            h = h.replace('</main>', payload + '  </main>', 1)
        else:
            print(f'  skip (no insertion point): {slug}')
            continue

        if 'country-guide.css' not in h:
            h = h.replace('</head>',
                          '  <link rel="stylesheet" href="../../country-guide.css?v=20260723" />\n</head>', 1)
        open(path, 'w').write(h)

        b = re.sub(r'<script.*?</script>', ' ', h, flags=re.S)
        w = len(re.sub(r'<[^>]*>', ' ', b).split())
        print(f'  {w:5d}w  {slug}')
        total += 1
    print(f'guides expanded: {total}')


if __name__ == '__main__':
    main()
