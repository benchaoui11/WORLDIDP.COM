#!/usr/bin/env python3
"""
Entity graph consolidation.

Two jobs:
  1. Give every Organization node a stable @id so AI systems resolve one entity
     across the site instead of 294 unlinked copies.
  2. Attach `sameAs` — but ONLY from data/verified-profiles.json, which contains
     profiles the site owner has confirmed exist. Nothing is invented here. If
     the file is empty, no sameAs is written and the script says so loudly.
"""
import json, os, re, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
ORG_ID = f'{SITE}/#organization'
SITE_ID = f'{SITE}/#website'

profiles_path = os.path.join(ROOT, 'data', 'verified-profiles.json')
profiles = []
if os.path.exists(profiles_path):
    raw = json.load(open(profiles_path))
    profiles = [p['url'] for p in raw.get('profiles', []) if p.get('verified') is True]

skipped = [p['url'] for p in (json.load(open(profiles_path)).get('profiles', [])
           if os.path.exists(profiles_path) else []) if p.get('verified') is not True]

changed = 0
org_nodes = 0
for path in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
    rel = os.path.relpath(path, ROOT)
    if rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
        continue
    h = open(path).read()
    orig = h

    def fix(m):
        global org_nodes
        block = m.group(1)
        try:
            obj = json.loads(block)
        except Exception:
            return m.group(0)

        def walk(node):
            global org_nodes
            if isinstance(node, dict):
                t = node.get('@type')
                if t == 'Organization' and node.get('name', '').lower().startswith('worldidp'):
                    node.setdefault('@id', ORG_ID)
                    if profiles:
                        node['sameAs'] = profiles
                    org_nodes += 1
                elif t == 'WebSite':
                    node.setdefault('@id', SITE_ID)
                    node.setdefault('publisher', {'@id': ORG_ID})
                for v in node.values():
                    walk(v)
            elif isinstance(node, list):
                for v in node:
                    walk(v)

        walk(obj)
        return '<script type="application/ld+json">\n' + \
               json.dumps(obj, indent=2, ensure_ascii=False) + '\n  </script>'

    h = re.sub(r'<script type="application/ld\+json">\s*(.*?)\s*</script>',
               fix, h, flags=re.S)
    if h != orig:
        open(path, 'w').write(h)
        changed += 1

print(f"files updated: {changed}")
print(f"Organization nodes given stable @id: {org_nodes}")
if profiles:
    print(f"sameAs attached ({len(profiles)} verified profiles):")
    for p in profiles:
        print("   ", p)
else:
    print("sameAs NOT written — data/verified-profiles.json contains no confirmed profiles.")
    print("  This is deliberate. Inventing social URLs would break entity resolution")
    print("  rather than fix it. Add real profiles to that file and re-run.")
if skipped:
    print(f"unconfirmed profiles skipped: {len(skipped)}")
    for p in skipped:
        print("   ", p)
