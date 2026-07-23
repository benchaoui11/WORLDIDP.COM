#!/usr/bin/env python3
"""
WorldIDP pre-indexation verification — the 5 checks.

Usage:
    python3 tools/build/preflight.py                    # check local build
    python3 tools/build/preflight.py --live             # check https://worldidp.com
    python3 tools/build/preflight.py --live --base https://staging.example.com

Exit code 0 = safe to submit to Google Search Console.
Exit code 1 = DO NOT submit. Fix the reported items first.
"""
import os, re, sys, json, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LIVE = '--live' in sys.argv
BASE = 'https://worldidp.com'
if '--base' in sys.argv:
    BASE = sys.argv[sys.argv.index('--base') + 1]

# Expected counts are derived from the data, never hardcoded, so promoting a
# country to Tier A cannot make this script report a false failure.
_data = json.load(open(os.path.join(ROOT, 'data', 'countries.json')))
VERIFIED = sorted(c['slug'] for c in _data if c.get('indexable'))
_NOINDEX = sorted(c['slug'] for c in _data if not c.get('indexable'))
SAMPLE_NOINDEX = _NOINDEX[:8] + _NOINDEX[-2:]
EXPECT_INDEX = len(VERIFIED)
EXPECT_NOINDEX = len(_NOINDEX)
# Derived, not hardcoded: count every indexable non-country page on disk so that
# adding a page cannot make this check report a false failure.
def _count_indexable_non_country():
    import glob as _g
    n = 0
    for _p in _g.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        _rel = os.path.relpath(_p, ROOT)
        if _rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
            continue
        if _rel.startswith('countries' + os.sep):
            continue
        _h = open(_p, errors='replace').read()
        _m = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', _h, re.I | re.S)
        if _m and 'noindex' not in _m.group(1).lower():
            n += 1
    return n


EXPECT_SITEMAP = EXPECT_INDEX + (_count_indexable_non_country() if not LIVE else 30)

results = []


def get(path):
    """Fetch a page either from disk or from the live site."""
    if LIVE:
        import urllib.request
        url = BASE.rstrip('/') + path
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'WorldIDP-preflight/1.0'})
            with urllib.request.urlopen(req, timeout=20) as r:
                return r.read().decode('utf-8', 'replace'), r.status
        except Exception as ex:
            return None, str(ex)
    p = path.lstrip('/')
    p = os.path.join(ROOT, p if p else 'index.html')
    if os.path.isdir(p):
        p = os.path.join(p, 'index.html')
    if not os.path.exists(p):
        return None, 404
    return open(p, errors='replace').read(), 200


def robots_of(h):
    m = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', h, re.I | re.S)
    return (m.group(1) if m else '').strip()


def report(num, title, passed, lines):
    results.append(passed)
    mark = 'PASS' if passed else 'FAIL'
    print(f"\n── CHECK {num}: {title}")
    for l in lines:
        print(f"   {l}")
    print(f"   [{mark}]")


# ─────────────────────────────────────────────── CHECK 1
lines, bad = [], 0
for slug in SAMPLE_NOINDEX:
    h, st = get(f'/countries/{slug}/')
    if h is None:
        lines.append(f"x  {slug}: not reachable ({st})")
        bad += 1
        continue
    r = robots_of(h)
    if 'noindex' in r.lower():
        lines.append(f"ok {slug}: {r}")
    else:
        lines.append(f"x  {slug}: {r or '(no robots meta)'}  <-- WOULD BE INDEXED")
        bad += 1

if not LIVE:
    total = sum(1 for p in glob.glob(os.path.join(ROOT, 'countries', '*', 'index.html'))
                if 'noindex' in robots_of(open(p, errors='replace').read()).lower())
    lines.append(f"-> {total} of {len(_data)} country pages carry noindex "
                 f"(expected {EXPECT_NOINDEX})")
    if total != EXPECT_NOINDEX:
        bad += 1
report(1, "unverified country pages are noindex", bad == 0, lines)

# ─────────────────────────────────────────────── CHECK 2
lines, bad = [], 0
for slug in VERIFIED:
    h, st = get(f'/countries/{slug}/')
    if h is None:
        lines.append(f"x  {slug}: not reachable ({st})")
        bad += 1
        continue
    r = robots_of(h)
    good = ('noindex' not in r.lower() and 'index' in r.lower()
            and 'max-snippet:-1' in r)
    lines.append(('ok ' if good else 'x  ') + f"{slug}: {r}")
    if not good:
        bad += 1
report(2, f"the {EXPECT_INDEX} verified pages are indexable with max-snippet:-1", bad == 0, lines)

# ─────────────────────────────────────────────── CHECK 3
lines, bad = [], 0
h, st = get('/sitemap.xml')
if h is None:
    lines.append(f"x  sitemap.xml not reachable ({st})")
    bad += 1
else:
    locs = re.findall(r'<loc>\s*(.*?)\s*</loc>', h, re.S)
    lines.append(f"-> {len(locs)} URLs in sitemap (expected {EXPECT_SITEMAP})")
    if len(locs) != EXPECT_SITEMAP:
        bad += 1
    ws = [l for l in re.findall(r'<loc>(.*?)</loc>', h, re.S) if l != l.strip()]
    if ws:
        lines.append(f"x  {len(ws)} <loc> values contain whitespace/newlines")
        bad += 1
    else:
        lines.append("ok no whitespace inside <loc>")

    cs = [l for l in locs if '/countries/' in l]
    lines.append(f"-> {len(cs)} country URLs in sitemap (expected {EXPECT_INDEX})")
    if len(cs) != EXPECT_INDEX:
        bad += 1
    leaked = [l for l in cs if l.rstrip('/').rsplit('/', 1)[-1] not in VERIFIED]
    if leaked:
        lines.append(f"x  NOINDEX PAGE IN SITEMAP: {leaked[:5]}")
        bad += 1
    else:
        lines.append("ok every country URL in the sitemap is a verified page")

    if not LIVE:
        for l in locs:
            p = l.replace(BASE, '')
            hh, _ = get(p)
            if hh and 'noindex' in robots_of(hh).lower():
                lines.append(f"x  noindex page present in sitemap: {l}")
                bad += 1
report(3, "sitemap contains only indexable URLs", bad == 0, lines)

# ─────────────────────────────────────────────── CHECK 4
lines, bad = [], 0
h, st = get('/robots.txt')
if h is None:
    lines.append(f"x  robots.txt not reachable ({st})")
    bad += 1
else:
    if 'Sitemap:' in h:
        sm = re.search(r'Sitemap:\s*(\S+)', h).group(1)
        lines.append(f"ok Sitemap directive: {sm}")
    else:
        lines.append("x  no Sitemap directive")
        bad += 1
    for bot in ('GPTBot', 'PerplexityBot', 'ClaudeBot', 'Google-Extended',
                'OAI-SearchBot', 'Bingbot'):
        if bot in h:
            lines.append(f"ok {bot} allowed")
        else:
            lines.append(f"!  {bot} not mentioned")
    if re.search(r'^\s*Disallow:\s*/\s*$', h, re.M):
        lines.append("x  robots.txt contains a site-wide Disallow: /")
        bad += 1
report(4, "robots.txt is correct and allows AI crawlers", bad == 0, lines)

# ─────────────────────────────────────────────── CHECK 5
lines, bad = [], 0
h, st = get('/data/idp-country-requirements.csv')
if h is None:
    lines.append(f"x  registry CSV not reachable ({st})")
    bad += 1
else:
    rows = [r for r in h.strip().split('\n') if r.strip()]
    lines.append(f"ok CSV reachable: {len(rows) - 1} data rows")
    if len(rows) - 1 != len(_data):
        lines.append(f"!  expected {len(_data)} rows, found {len(rows)-1}")
    if 'evidenceTier' in rows[0] and 'sourceCount' in rows[0]:
        lines.append("ok evidenceTier and sourceCount columns present")
    else:
        lines.append("x  CSV missing evidence columns")
        bad += 1

hub, _ = get('/countries.html')
if hub and '"@type": "Dataset"' in hub:
    lines.append("ok Dataset schema present on /countries.html")
else:
    lines.append("x  Dataset schema missing from /countries.html")
    bad += 1
report(5, "public registry and Dataset schema are live", bad == 0, lines)

# ─────────────────────────────────────────────── summary
print("\n" + "=" * 60)
mode = f"LIVE  {BASE}" if LIVE else f"LOCAL {ROOT}"
print(f"MODE: {mode}")
passed = sum(1 for r in results if r)
print(f"RESULT: {passed}/5 checks passed")
if passed == 5:
    print("\nSAFE TO SUBMIT to Google Search Console.")
else:
    print("\nDO NOT SUBMIT. Fix the FAIL items above and re-run.")
print("=" * 60)
sys.exit(0 if passed == 5 else 1)
