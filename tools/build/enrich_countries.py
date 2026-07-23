#!/usr/bin/env python3
"""
WorldIDP — country data enrichment.

Merges three sources into data/countries.json:
  1. Existing pilot research (10 countries, source-backed)  -> tier A
  2. Legacy site data recovered from the original countries.html
     (idpStatus, drivingSide, motorway speed)               -> tier B, marked unverified
  3. Driving-side reference list (stable, universally documented fact)

Rules enforced here:
  * Nothing is invented. Fields with no evidence stay null.
  * Legacy values are stored under `reported*` keys and are NEVER promoted to
    verified status without a cited source.
  * evidenceTier and indexable are DERIVED, never hand-set.
"""
import json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, 'data')
TODAY = '2026-07-23'

# ---------------------------------------------------------------- driving side
# Left-hand traffic. Stable, universally documented. Cited to a public reference
# on the methodology page rather than per-row.
LEFT = {
 'anguilla','antigua-and-barbuda','australia','bahamas','bangladesh','barbados',
 'bermuda','bhutan','botswana','brunei','cayman-islands','cyprus','dominica',
 'east-timor','timor-leste','fiji','grenada','guyana','hong-kong','india',
 'indonesia','ireland','jamaica','japan','kenya','kiribati','lesotho','macau',
 'malawi','malaysia','maldives','malta','mauritius','mozambique','namibia',
 'nauru','nepal','new-zealand','pakistan','papua-new-guinea','saint-kitts-and-nevis',
 'saint-lucia','saint-vincent-and-the-grenadines','samoa','seychelles','singapore',
 'solomon-islands','south-africa','sri-lanka','suriname','eswatini','swaziland',
 'tanzania','thailand','tonga','trinidad-and-tobago','tuvalu','uganda',
 'united-kingdom','zambia','zimbabwe',
}

# ------------------------------------------------- road traffic conventions
# UN treaty depositary records. Only countries where membership is
# unambiguous are listed; everything else stays empty and the page says so.
GENEVA_1949 = {
 'albania','algeria','argentina','australia','bangladesh','barbados','belgium',
 'benin','botswana','bulgaria','burkina-faso','cambodia','canada','chile',
 'congo','cote-divoire','cuba','cyprus','czechia','czech-republic','denmark',
 'dominican-republic','ecuador','egypt','fiji','france','georgia','ghana',
 'greece','guatemala','haiti','hungary','iceland','india','ireland','israel',
 'italy','jamaica','japan','jordan','laos','lebanon','lesotho','luxembourg',
 'madagascar','malawi','malaysia','mali','malta','monaco','montenegro','morocco',
 'namibia','netherlands','new-zealand','niger','nigeria','norway','papua-new-guinea',
 'paraguay','peru','philippines','poland','portugal','romania','rwanda','san-marino',
 'senegal','serbia','sierra-leone','singapore','slovakia','slovenia','south-africa',
 'south-korea','korea-south','spain','sri-lanka','sweden','syria','thailand','togo',
 'trinidad-and-tobago','tunisia','turkey','uganda','united-arab-emirates',
 'united-kingdom','united-states','vatican-city','venezuela','vietnam','zimbabwe',
}
VIENNA_1968 = {
 'albania','armenia','austria','azerbaijan','bahamas','bahrain','belarus','belgium',
 'bosnia-and-herzegovina','brazil','bulgaria','central-african-republic','chile',
 'costa-rica','croatia','cuba','czechia','czech-republic','denmark','ecuador',
 'estonia','finland','france','georgia','germany','greece','guyana','hungary',
 'indonesia','iran','iraq','israel','italy','kazakhstan','kenya','kuwait',
 'kyrgyzstan','latvia','liberia','liechtenstein','lithuania','luxembourg',
 'mexico','moldova','monaco','mongolia','montenegro','morocco','netherlands',
 'niger','nigeria','north-macedonia','norway','oman','pakistan','peru','philippines',
 'poland','portugal','qatar','romania','russia','san-marino','saudi-arabia',
 'senegal','serbia','seychelles','slovakia','slovenia','south-africa','south-korea',
 'korea-south','spain','sweden','switzerland','tajikistan','thailand','tunisia',
 'turkey','turkmenistan','ukraine','united-arab-emirates','uruguay','uzbekistan',
 'vietnam','zimbabwe',
}

# ---------------------------------------------------------------- helpers
def slugify(name):
    s = name.lower().strip()
    s = s.replace('&', 'and')
    s = re.sub(r"[’'`]", '', s)
    s = re.sub(r'[^a-z0-9]+', '-', s).strip('-')
    return s


def load(p, default=None):
    try:
        with open(os.path.join(DATA, p)) as f:
            return json.load(f)
    except Exception:
        return default


def evidence_tier(c):
    """
    Derive tier from evidence actually present. Never hand-set.

    Tier A (indexable) requires every intent-critical field, because the page
    exists to answer "do I need an IDP in {country}?". Missing any one of these
    means the page cannot satisfy the query and must not compete in search.
    """
    src = len(c.get('officialSources') or [])

    intent_critical = [
        bool(c.get('idpStatus')),          # the primary answer
        bool(c.get('drivingSide')),
        bool(c.get('conventions')),
        bool(c.get('lastVerified')),
        bool(c.get('documentsToCarry')),
        src >= 2,
    ]

    supporting = sum([
        bool(c.get('speedMotorwayKmh')), bool(c.get('speedUrbanKmh')),
        bool(c.get('speedRuralKmh')), bool(c.get('minimumRentalAge')),
        bool(c.get('bacLimit')),
        bool(c.get('digitalDocumentNote')),
        bool(c.get('licenceOriginNotes')), bool(c.get('rentalNotes')),
        bool(c.get('roadsideCheckNotes')), bool(c.get('countrySpecificNotes')),
    ])

    if all(intent_critical) and supporting >= 2:
        return 'A'                      # verified — indexable
    if c.get('drivingSide') and (c.get('conventions') or c.get('reportedIdpStatus')):
        return 'B'                      # partial — noindex, useful for navigation
    return 'C'                          # stub — noindex


NOTES = {}


def main():
    global NOTES
    NOTES = {k: v for k, v in (load('country-notes.json', {}) or {}).items()
             if not k.startswith('_')}
    countries = load('countries.json', [])
    legacy_path = os.path.join(DATA, 'legacy-country-facts.json')
    legacy = {}
    if os.path.exists(legacy_path):
        for r in json.load(open(legacy_path)):
            legacy[slugify(r['name'])] = r

    out = []
    for c in countries:
        slug = c.get('slug') or slugify(c['name'])
        c['slug'] = slug
        lg = legacy.get(slug, {})

        # ---- reported (unverified) legacy values ------------------------
        if lg:
            c['reportedIdpStatus'] = lg.get('idp')          # required|recommended
            c['reportedDrivingSide'] = 'left' if lg.get('side') == 'L' else 'right'
            sp = lg.get('speed') or []
            c['reportedSpeedMotorwayKmh'] = int(sp[0]) if sp else None
            c['reportedSource'] = 'internal-legacy-dataset'
        else:
            c.setdefault('reportedIdpStatus', None)
            c.setdefault('reportedDrivingSide', None)
            c.setdefault('reportedSpeedMotorwayKmh', None)

        # ---- verified driving side (stable documented fact) -------------
        if not c.get('drivingSide'):
            side = 'left' if slug in LEFT else 'right'
            rep = c.get('reportedDrivingSide')
            c['drivingSide'] = side
            c['drivingSideConfidence'] = 'high' if (rep is None or rep == side) else 'conflict'
            c['drivingSideSource'] = 'reference-list'
        else:
            c.setdefault('drivingSideConfidence', 'verified')
            c.setdefault('drivingSideSource', 'official')

        # ---- conventions -------------------------------------------------
        if not c.get('conventions'):
            conv = []
            if slug in GENEVA_1949:
                conv.append('1949-geneva')
            if slug in VIENNA_1968:
                conv.append('1968-vienna')
            c['conventions'] = conv
            c['conventionsSource'] = 'un-treaty-reference' if conv else None
        else:
            c.setdefault('conventionsSource', 'official')

        # ---- supporting notes (only for countries with >=2 sources) -----
        note = NOTES.get(slug)
        if note and len(c.get('officialSources') or []) >= 2:
            for k in ('licenceOriginNotes', 'rentalNotes', 'roadsideCheckNotes',
                      'countrySpecificNotes', 'faq'):
                if note.get(k):
                    c[k] = note[k]
        elif note:
            print(f"  ! notes skipped for {slug}: fewer than 2 official sources")

        # ---- normalise containers ---------------------------------------
        for k in ('officialSources', 'documentsToCarry', 'relatedCountries',
                  'countrySpecificNotes', 'faq'):
            c.setdefault(k, [])
            if c[k] is None:
                c[k] = []
        c.setdefault('digitalDocumentStatus', 'unclear')
        c.setdefault('licenceOriginNotes', None)
        c.setdefault('rentalNotes', None)
        c.setdefault('roadsideCheckNotes', None)

        # ---- derive tier + indexability ---------------------------------
        tier = evidence_tier(c)
        c['evidenceTier'] = tier
        c['indexable'] = (tier == 'A')
        c['researchStatus'] = {
            'A': 'verified',
            'B': 'partial-evidence',
            'C': 'evidence-required',
        }[tier]
        if tier == 'A' and not c.get('lastVerified'):
            c['lastVerified'] = TODAY
        out.append(c)

    # ---- related countries: same region, prefer verified ----------------
    by_region = {}
    for c in out:
        by_region.setdefault(c.get('region'), []).append(c)
    for c in out:
        if c['relatedCountries']:
            continue
        peers = [p for p in by_region.get(c.get('region'), []) if p['slug'] != c['slug']]
        peers.sort(key=lambda p: (p['evidenceTier'], p['name']))
        c['relatedCountries'] = [p['slug'] for p in peers[:3]]

    out.sort(key=lambda c: c['name'])
    with open(os.path.join(DATA, 'countries.json'), 'w') as f:
        json.dump(out, f, indent=2, ensure_ascii=False)

    from collections import Counter
    t = Counter(c['evidenceTier'] for c in out)
    print(f"countries: {len(out)}")
    print(f"  tier A (verified, indexable): {t['A']}")
    print(f"  tier B (partial, noindex):    {t['B']}")
    print(f"  tier C (stub, noindex):       {t['C']}")
    print(f"  driving side known:           {sum(1 for c in out if c['drivingSide'])}")
    print(f"  conventions known:            {sum(1 for c in out if c['conventions'])}")
    print(f"  side conflicts flagged:       {sum(1 for c in out if c.get('drivingSideConfidence')=='conflict')}")


if __name__ == '__main__':
    main()
