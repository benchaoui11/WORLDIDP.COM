#!/usr/bin/env python3
"""
Sitemap builder.

Hard rule: a URL enters the sitemap only if the page it points to actually
serves `index`. The robots directive in the rendered HTML is the source of
truth, not a list maintained by hand — that is how noindex URLs end up in
sitemaps.
"""
import os, re, glob, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = 'https://worldidp.com'
TODAY = datetime.date.today().isoformat()

PRIORITY = {
    '/': ('1.0', 'weekly'),
    '/countries.html': ('0.9', 'weekly'),
    '/what-is-idp.html': ('0.9', 'monthly'),
    '/how-to-apply.html': ('0.9', 'monthly'),
    '/pricing.html': ('0.8', 'monthly'),
    '/faq.html': ('0.8', 'monthly'),
    '/compare/aaa-idp-vs-worldidp/': ('0.9', 'monthly'),
    '/convention/1949-geneva/': ('0.8', 'yearly'),
    '/convention/1968-vienna/': ('0.8', 'yearly'),
    '/editorial-policy.html': ('0.5', 'yearly'),
}
SKIP = {'checkout.html', 'payment.html', 'thank-you.html', 'upload-photos.html',
        'track-order.html'}


def is_indexable(path):
    h = open(path, errors='ignore').read()
    m = re.search(r'<meta[^>]*?name="robots"[^>]*?content="([^"]*)"', h, re.I | re.S)
    if not m:
        return False                       # no directive = do not submit
    return 'noindex' not in m.group(1).lower()


def url_for(path):
    rel = os.path.relpath(path, ROOT).replace(os.sep, '/')
    if rel == 'index.html':
        return '/'
    if rel.endswith('/index.html'):
        return '/' + rel[:-len('index.html')]
    return '/' + rel


def main():
    paths = []
    for p in glob.glob(os.path.join(ROOT, '**', '*.html'), recursive=True):
        rel = os.path.relpath(p, ROOT)
        if rel.startswith(('admin', 'templates', '_audit', 'node_modules')):
            continue
        if os.path.basename(p) in SKIP:
            continue
        paths.append(p)

    entries, excluded = [], []
    for p in sorted(paths):
        u = url_for(p)
        if is_indexable(p):
            pr, cf = PRIORITY.get(u, ('0.6', 'monthly') if u.startswith('/countries/')
                                  else ('0.6', 'monthly'))
            if u.startswith('/countries/'):
                pr, cf = '0.7', 'monthly'
            if u.startswith('/legal') or 'policy' in u or 'terms' in u or 'disclaimer' in u:
                pr, cf = '0.3', 'yearly'
            entries.append((SITE + u, pr, cf))
        else:
            excluded.append(u)

    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for u, pr, cf in entries:
        lines += ['  <url>',
                  f'    <loc>{u}</loc>',
                  f'    <lastmod>{TODAY}</lastmod>',
                  f'    <changefreq>{cf}</changefreq>',
                  f'    <priority>{pr}</priority>',
                  '  </url>']
    lines.append('</urlset>')

    with open(os.path.join(ROOT, 'sitemap.xml'), 'w') as f:
        f.write('\n'.join(lines) + '\n')

    print(f"sitemap.xml written: {len(entries)} URLs")
    print(f"  excluded (noindex): {len(excluded)}")
    ccount = sum(1 for u, _, _ in entries if '/countries/' in u)
    print(f"  country URLs included: {ccount}")


if __name__ == '__main__':
    main()
