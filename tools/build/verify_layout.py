#!/usr/bin/env python3
"""
Rendered-layout verification.

Everything before this script checked that files return 200 and that classes
have definitions somewhere. Neither of those tells you whether the page looks
right — which is why broken layouts shipped. This actually renders each page in
Chromium and measures geometry.

Failures it detects:

  overflow      element extends past the viewport (horizontal scrollbar)
  full-bleed    body copy sits outside the column its own heading occupies
  crushed       an h1 narrower than 200px, i.e. text wrapping one word per line
  huge-gap      more than 200px of empty space between consecutive sections
  header-clash  the h1 renders underneath the fixed header
  tiny-text     computed font-size under 12px

Run: python3 tools/build/verify_layout.py [--port 8899]
Exit code 1 on any failure.
"""
import json, os, re, subprocess, sys, threading, time, http.server, socketserver, functools

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PORT = int(sys.argv[sys.argv.index('--port') + 1]) if '--port' in sys.argv else 8899

VIEWPORTS = [('desktop', 1440, 900), ('mobile', 390, 844)]

PAGES = [
    '/', '/countries.html', '/countries/italy/', '/countries/albania/',
    '/countries/united-states/', '/glossary/', '/research/idp-requirements-findings/',
    '/guides/', '/guides/what-is-aata/', '/guides/aaa-idp-cost-and-turnaround/',
    '/guides/aaa-office-locations-for-idps/', '/guides/how-to-apply-for-an-idp-in-the-us/',
    '/guides/idp-for-non-us-licence-holders/',
    '/guides/can-i-get-an-idp-the-same-day-in-the-us/',
    '/compare/aaa-idp-vs-worldidp/', '/convention/1949-geneva/', '/convention/1968-vienna/',
    '/what-is-idp.html', '/how-to-apply.html', '/faq.html', '/pricing.html',
    '/terms-of-service.html', '/editorial-policy.html', '/about-us.html',
]

PROBE = r"""
() => {
  const out = { overflow: [], fullbleed: [], crushed: [], gaps: [], tiny: [], header: null };
  const vw = window.innerWidth;

  // Real horizontal overflow means the document itself scrolls sideways.
  // An absolutely positioned decoration inside an overflow-clip ancestor
  // extends past the viewport without ever creating a scrollbar, so measuring
  // element rects alone produces false positives.
  const docScroll = document.documentElement.scrollWidth;
  if (docScroll > vw + 2) {
    document.querySelectorAll('main *, header *, footer *').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0) return;
      const cs = getComputedStyle(el);
      if (cs.position === 'absolute' || cs.position === 'fixed') return;
      if (r.right > vw + 2 || r.left < -2) {
        out.overflow.push({ tag: el.tagName, cls: el.className.toString().slice(0, 50),
                            left: Math.round(r.left), right: Math.round(r.right) });
      }
    });
    if (!out.overflow.length) {
      out.overflow.push({ tag: 'document', cls: '(source not isolated)',
                          left: 0, right: docScroll });
    }
  }

  // body copy escaping the column its own heading sits in
  document.querySelectorAll('section').forEach(sec => {
    const h = sec.querySelector('h2');
    if (!h) return;
    const hr = h.getBoundingClientRect();
    if (hr.width === 0) return;
    sec.querySelectorAll(':scope > p, :scope > ul, :scope > ol, :scope > table').forEach(el => {
      const r = el.getBoundingClientRect();
      if (r.width === 0) return;
      // A wide, centre-aligned block with short text is a deliberate layout,
      // not full-bleed copy. Only flag left-aligned text that actually runs
      // wider than the column its heading occupies.
      const ecs = getComputedStyle(el);
      if (ecs.textAlign === 'center') return;
      if (r.width > hr.width * 1.35) {
        out.fullbleed.push({ tag: el.TagName || el.tagName,
                             head: h.textContent.trim().slice(0, 34),
                             headW: Math.round(hr.width), elW: Math.round(r.width),
                             headL: Math.round(hr.left), elL: Math.round(r.left) });
      }
    });
  });

  // h1 crushed into a narrow column
  document.querySelectorAll('h1').forEach(h => {
    const r = h.getBoundingClientRect();
    if (r.width > 0 && r.width < 200 && vw > 500) {
      out.crushed.push({ text: h.textContent.trim().slice(0, 40), w: Math.round(r.width) });
    }
  });

  // excessive empty space between consecutive sections
  const secs = [...document.querySelectorAll('main section')];
  for (let i = 1; i < secs.length; i++) {
    const a = secs[i - 1].getBoundingClientRect(), b = secs[i].getBoundingClientRect();
    const gap = b.top - a.bottom;
    if (gap <= 200) continue;
    // Anything actually rendered in that band? Sample the midpoint.
    const midY = a.bottom + gap / 2;
    const hit = document.elementFromPoint(vw / 2, Math.min(midY, window.innerHeight - 2));
    const filled = hit && hit !== document.body &&
                   hit !== document.documentElement && hit.tagName !== 'MAIN';
    if (!filled) {
      out.gaps.push({ gap: Math.round(gap),
                      after: (secs[i-1].textContent || '').trim().slice(0, 32) });
    }
  }

  // h1 hidden behind the fixed header
  const hdr = document.querySelector('.site-header');
  const h1 = document.querySelector('main h1');
  if (hdr && h1) {
    const hb = hdr.getBoundingClientRect(), h1b = h1.getBoundingClientRect();
    if (h1b.top < hb.bottom && h1b.bottom > hb.top) {
      out.header = { headerBottom: Math.round(hb.bottom), h1Top: Math.round(h1b.top) };
    }
  }

  // Unreadably small text. An uppercase eyebrow with letter-spacing at ~11.8px
  // is a deliberate and legible pattern; genuine body copy below 11px is not.
  document.querySelectorAll('main p, main li, main td, main th').forEach(el => {
    const cs = getComputedStyle(el);
    const fs = parseFloat(cs.fontSize);
    if (!fs) return;
    const isEyebrow = cs.textTransform === 'uppercase' &&
                      parseFloat(cs.letterSpacing) > 0.3;
    const floor = isEyebrow ? 11 : 12;
    if (fs < floor) {
      out.tiny.push({ tag: el.tagName, fs: Math.round(fs * 100) / 100,
                      eyebrow: isEyebrow,
                      text: (el.textContent || '').trim().slice(0, 44) });
    }
  });

  return out;
}
"""


def serve():
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=ROOT)
    socketserver.TCPServer.allow_reuse_address = True
    httpd = socketserver.TCPServer(('127.0.0.1', PORT), handler)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def main():
    from playwright.sync_api import sync_playwright
    httpd = serve()
    time.sleep(0.6)

    failures = 0
    checked = 0
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for vname, w, h in VIEWPORTS:
            page = browser.new_page(viewport={'width': w, 'height': h})
            print(f"\n{'='*66}\n{vname.upper()}  {w}x{h}\n{'='*66}")
            for path in PAGES:
                page.goto(f'http://127.0.0.1:{PORT}{path}', wait_until='networkidle')
                page.wait_for_timeout(120)
                r = page.evaluate(PROBE)
                checked += 1
                probs = []
                if r['header']:
                    probs.append(f"h1 under header (header ends {r['header']['headerBottom']}px, "
                                 f"h1 starts {r['header']['h1Top']}px)")
                for o in r['overflow'][:2]:
                    probs.append(f"overflow <{o['tag'].lower()} class='{o['cls'][:26]}'> "
                                 f"right={o['right']} vw={w}")
                for f_ in r['fullbleed'][:2]:
                    probs.append(f"full-bleed under '{f_['head']}': heading {f_['headW']}px @x{f_['headL']}, "
                                 f"body {f_['elW']}px @x{f_['elL']}")
                for c in r['crushed'][:1]:
                    probs.append(f"h1 crushed to {c['w']}px: '{c['text']}'")
                for g in r['gaps'][:2]:
                    probs.append(f"{g['gap']}px empty gap after '{g['after'][:26]}'")
                for t in r['tiny'][:2]:
                    probs.append(f"text {t['fs']}px on <{t['tag'].lower()}>: "
                                 f"\"{t.get('text','')}\"")

                if probs:
                    failures += 1
                    print(f"  FAIL  {path}")
                    for pr in probs:
                        print(f"          {pr}")
                else:
                    print(f"  ok    {path}")
            page.close()
        browser.close()
    httpd.shutdown()

    print(f"\n{'='*66}")
    print(f"{checked} renders checked, {failures} with layout problems")
    print('='*66)
    return 1 if failures else 0


if __name__ == '__main__':
    sys.exit(main())
