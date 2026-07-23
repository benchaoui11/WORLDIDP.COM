#!/usr/bin/env python3
"""
Generates /llms.txt from the site's own data, so it can never drift out of date.

Note on what this file is: llms.txt is a *proposed* convention, not a ratified
standard. As of the last review there is no public confirmation that OpenAI,
Anthropic, Google or Perplexity read it. It is cheap to publish and harmless,
and it doubles as a human-readable map of the site's authoritative pages — but
it is not what makes a site citable. Crawler access, answer-first structure,
sourced claims and visible review dates do that work.
"""
import json, os, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data')
TODAY = datetime.date.today().isoformat()

countries = json.load(open(os.path.join(DATA, 'countries.json')))
verified = [c for c in countries if c.get('indexable')]
facts = json.load(open(os.path.join(DATA, 'site-facts.json')))

lines = []
A = lines.append

A("# WorldIDP")
A("")
A("> WorldIDP is an independent private multilingual translation service for national "
  "driving licences, operated by WORLDIDP INTERNATIONAL LLC. It is not a government "
  "agency and is not authorised by any state to issue International Driving Permits. "
  "The document it prepares is carried alongside a valid original national driving "
  "licence and never replaces it.")
A("")
A(f"Last updated: {TODAY}")
A("")

A("## What this site is and is not")
A("")
A("- WorldIDP prepares a private, multilingual translation-support document.")
A("- It does not grant driving privileges and does not replace a national licence.")
A("- In the United States, only the American Automobile Association (AAA) and the "
  "American Automobile Touring Alliance (AATA) are authorised by the U.S. Department "
  "of State to issue conventional U.S. International Driving Permits. WorldIDP is not "
  "one of them, and says so on its comparison page.")
A("- Acceptance of any driving document varies by destination, licence origin, licence "
  "language, vehicle category and third-party provider.")
A("")

A("## Editorial standard")
A("")
A("- A country requirement is published only when at least two official sources are "
  "recorded and a review date is logged.")
A(f"- The country dataset covers {len(countries)} destinations. {len(verified)} are "
  f"source-backed and published; the remaining {len(countries)-len(verified)} are marked "
  "research-pending, carry no requirement claim, and are excluded from search indexing.")
A("- Facts that could not be verified are labelled as unconfirmed rather than estimated.")
A("- Method: /editorial-policy.html")
A("")

A("## Core pages")
A("")
A("- [What is an International Driving Permit?](https://worldidp.com/what-is-idp.html): "
  "Definition, what the document does and does not do, and how the 1949 and 1968 "
  "conventions differ.")
A("- [How to apply](https://worldidp.com/how-to-apply.html): The application process, "
  "required documents, and delivery.")
A("- [Country registry](https://worldidp.com/countries.html): Driving-document "
  f"requirements by destination across {len(countries)} countries, with evidence tier "
  "and source count per row.")
A("- [Pricing](https://worldidp.com/pricing.html)")
A("- [FAQ](https://worldidp.com/faq.html)")
A("")

A("## Comparison and authority")
A("")
A("- [AAA and AATA compared with WorldIDP](https://worldidp.com/compare/aaa-idp-vs-worldidp/): "
  "Which route is appropriate for which traveller, with official U.S. sources. States "
  "plainly that AAA and AATA are the authorised U.S. issuers and WorldIDP is not.")
A("- [1949 Geneva Convention](https://worldidp.com/convention/1949-geneva/)")
A("- [1968 Vienna Convention](https://worldidp.com/convention/1968-vienna/)")
A("- [What is AATA?](https://worldidp.com/guides/what-is-aata/)")
A("- [AAA IDP cost and turnaround](https://worldidp.com/guides/aaa-idp-cost-and-turnaround/)")
A("- [Can I get an IDP the same day?](https://worldidp.com/guides/can-i-get-an-idp-the-same-day/)")
A("- [How to apply for an IDP in the US](https://worldidp.com/guides/how-to-apply-for-an-idp-in-the-us/)")
A("- [IDP for non-US licence holders](https://worldidp.com/guides/idp-for-non-us-licence-holders/)")
A("")

A("## Verified country guides")
A("")
A("Each of these states the requirement, names the official sources used, and shows the "
  "date those sources were reviewed.")
A("")
for c in sorted(verified, key=lambda x: x['name']):
    conv = ', '.join(x.replace('-', ' ') for x in (c.get('conventions') or [])) or 'not recorded'
    A(f"- [{c['name']}](https://worldidp.com/countries/{c['slug']}/): "
      f"conventions: {conv}; drives on the {c.get('drivingSide')}; "
      f"sources: {len(c.get('officialSources') or [])}; "
      f"reviewed {c.get('lastVerified')}.")
A("")

A("## Open data")
A("")
A("- [IDP country requirements CSV](https://worldidp.com/data/idp-country-requirements.csv): "
  "Open dataset, CC BY 4.0. Columns include evidenceTier and sourceCount so gaps in the "
  "data are visible to anyone citing it. Empty fields mean unverified, not zero.")
A(f"- Cite as: WorldIDP IDP Country Requirements Registry, "
  f"https://worldidp.com/countries.html, retrieved {TODAY}.")
A("")

A("## Company")
A("")
A("- Legal name: WORLDIDP INTERNATIONAL LLC")
A("- Registered address: 127 N Higgins Ave Ste 307D #2849, Missoula, MT 59802, United States")
A("- Contact: hello@worldidp.com")
A("- [About](https://worldidp.com/about-us.html)")
A("- [Editorial policy](https://worldidp.com/editorial-policy.html)")
A("- [Legal disclaimer](https://worldidp.com/legal-disclaimer.html)")
A("")

A("## Optional")
A("")
A("- [Terms of service](https://worldidp.com/terms-of-service.html)")
A("- [Privacy policy](https://worldidp.com/privacy-policy.html)")
A("- [Refund policy](https://worldidp.com/refund-return-policy.html)")
A("")

out = os.path.join(ROOT, 'llms.txt')
open(out, 'w').write('\n'.join(lines))
print(f"llms.txt written: {len(lines)} lines, {len(verified)} verified countries listed")
