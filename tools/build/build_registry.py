#!/usr/bin/env python3
"""
Public country registry.

Emits data/idp-country-requirements.csv and attaches Dataset + DataCatalog
schema to the countries hub.

The CSV carries an explicit `evidenceTier` and `sourceCount` column so anyone
citing it can see which rows are source-backed and which are not. Publishing a
registry that hides its own gaps would be worse than publishing none.
"""
import json, os, csv, re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data')
SITE = 'https://worldidp.com'
TODAY = '2026-07-23'

countries = json.load(open(os.path.join(DATA, 'countries.json')))

# ------------------------------------------------------------------ CSV
cols = ['slug', 'name', 'iso2', 'region', 'evidenceTier', 'indexable',
        'idpStatus', 'idpStatusApplies', 'drivingSide', 'conventions',
        'digitalDocumentStatus', 'speedUrbanKmh', 'speedRuralKmh',
        'speedMotorwayKmh', 'minimumRentalAge', 'bacLimit',
        'sourceCount', 'sourceUrls', 'lastVerified', 'researchStatus']

csv_path = os.path.join(DATA, 'idp-country-requirements.csv')
with open(csv_path, 'w', newline='') as f:
    w = csv.writer(f)
    w.writerow(cols)
    for c in countries:
        srcs = c.get('officialSources') or []
        urls = ' | '.join(s.get('url', '') for s in srcs if isinstance(s, dict) and s.get('url'))
        w.writerow([
            c.get('slug'), c.get('name'), c.get('iso2'), c.get('region'),
            c.get('evidenceTier'), c.get('indexable'),
            c.get('idpStatus') or '', c.get('idpStatusApplies') or '',
            c.get('drivingSide') or '', '|'.join(c.get('conventions') or []),
            c.get('digitalDocumentStatus') or '',
            c.get('speedUrbanKmh') or '', c.get('speedRuralKmh') or '',
            c.get('speedMotorwayKmh') or '', c.get('minimumRentalAge') or '',
            '' if c.get('bacLimit') is None else c.get('bacLimit'),
            len(srcs), urls, c.get('lastVerified') or '', c.get('researchStatus'),
        ])

verified = sum(1 for c in countries if c['evidenceTier'] == 'A')
print(f"CSV written: {len(countries)} rows ({verified} source-backed)")

# ------------------------------------------------------- Dataset schema
dataset = {
    "@type": "Dataset",
    "@id": f"{SITE}/countries.html#dataset",
    "name": "WorldIDP International Driving Permit Country Requirements Registry",
    "description": (
        "Open reference dataset of driving-document requirements by destination. "
        f"Covers {len(countries)} destinations. {verified} rows are source-backed against "
        "official national or treaty sources with a recorded review date; the remainder are "
        "marked as research-pending and carry no requirement claim. Fields with no verified "
        "source are left empty rather than estimated."
    ),
    "url": f"{SITE}/countries.html",
    "license": "https://creativecommons.org/licenses/by/4.0/",
    "creator": {"@id": f"{SITE}/#organization"},
    "publisher": {"@id": f"{SITE}/#organization"},
    "dateModified": TODAY,
    "isAccessibleForFree": True,
    "measurementTechnique": "Manual review of official national road-authority publications, "
                            "treaty depositary records and government travel guidance.",
    "variableMeasured": [
        {"@type": "PropertyValue", "name": "idpStatus",
         "description": "Whether an International Driving Permit or official translation is indicated for foreign licence holders."},
        {"@type": "PropertyValue", "name": "drivingSide",
         "description": "Side of the road on which traffic drives."},
        {"@type": "PropertyValue", "name": "conventions",
         "description": "Road traffic conventions the destination is party to (1926 Paris, 1949 Geneva, 1968 Vienna)."},
        {"@type": "PropertyValue", "name": "digitalDocumentStatus",
         "description": "Whether a digital-only driving document is accepted, rejected, provider-dependent or unconfirmed."},
        {"@type": "PropertyValue", "name": "evidenceTier",
         "description": "A = source-backed and published; B = partial evidence, not published as a requirement; C = insufficient evidence."},
        {"@type": "PropertyValue", "name": "sourceCount",
         "description": "Number of official sources recorded for the row."},
    ],
    "distribution": [{
        "@type": "DataDownload",
        "encodingFormat": "text/csv",
        "contentUrl": f"{SITE}/data/idp-country-requirements.csv",
    }],
    "citation": f"WorldIDP IDP Country Requirements Registry, {SITE}/countries.html, retrieved {TODAY}.",
}

hub = os.path.join(ROOT, 'countries.html')
h = open(hub).read()

if '#dataset' in h:
    print("Dataset schema already present on hub — replacing")
    h = re.sub(r'<script type="application/ld\+json" id="registry-dataset">.*?</script>\s*',
               '', h, flags=re.S)

block = ('<script type="application/ld+json" id="registry-dataset">\n'
         + json.dumps({"@context": "https://schema.org", "@graph": [dataset]},
                      indent=2, ensure_ascii=False)
         + '\n  </script>\n')
h = h.replace('</head>', '  ' + block + '</head>', 1)
open(hub, 'w').write(h)
print("Dataset + DataDownload schema attached to countries.html")
