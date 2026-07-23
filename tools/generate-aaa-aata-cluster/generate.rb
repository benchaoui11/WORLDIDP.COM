#!/usr/bin/env ruby
# frozen_string_literal: true

require "cgi"
require "json"
require "fileutils"
require "rexml/document"

ROOT = File.expand_path("../..", __dir__)
TODAY = "2026-07-23"
ROBOTS = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
ORG = JSON.parse(File.read(File.join(ROOT, "data/organization.json")))

SOURCES = {
  usagov: ["USAGov - International driver's license for U.S. citizens", "https://www.usa.gov/international-drivers-license"],
  state: ["U.S. Department of State - Driving and Road Safety Abroad", "https://travel.state.gov/content/travel/en/international-travel/before-you-go/driving-and-road-safety.html"],
  aaa: ["AAA - International Driving Permit", "https://www.aaa.com/vacation/idp.html"],
  aaa_faq: ["AAA - Online IDP FAQ", "https://ace.aaa.com/travel/information/international-driving-permit/online-idp-faq.html"],
  aata_steps: ["AATA - Steps for Getting Your IDP", "https://www.aataidp.com/idp-steps"],
  aata_faq: ["AATA - IDP FAQ", "https://www.aataidp.com/faq"],
  aata_app: ["AATA - IDP Application", "https://www.aataidp.com/application"]
}.freeze

PAGES = [
  {
    path: "compare/aaa-idp-vs-worldidp/index.html",
    title: "AAA IDP vs WorldIDP | Evidence-Based Comparison",
    description: "A factual comparison of AAA conventional IDPs and WorldIDP private translation-support documents, with official source links.",
    h1: "AAA IDP vs WorldIDP",
    kicker: "Comparison guide",
    direct: "AAA is one of the two U.S. Department of State-authorized organizations for conventional U.S. IDPs. WorldIDP is a private multilingual translation-support service and is not a U.S. government-authorized IDP issuer.",
    sections: [
      ["When AAA is the right path", "Use AAA when you hold a valid U.S. driver license and need a conventional U.S. International Driving Permit. AAA offers online, mail and branch options, and its official page states that digital IDPs are not available."],
      ["When WorldIDP may be relevant", "WorldIDP may be useful when a traveler needs private multilingual translation support for a valid national driver's license. It does not replace the original license and does not grant legal driving privileges."],
      ["What not to confuse", "A conventional IDP issued through AAA or AATA is different from a private translation-support document. Travelers should check destination rules and carry the original valid driver license."]
    ],
    faq: [
      ["Is WorldIDP an AAA replacement?", "No. For U.S. conventional IDPs, official U.S. sources identify AAA and AATA as the authorized issuers. WorldIDP is a private translation-support service."],
      ["Should WorldIDP recommend AAA sometimes?", "Yes. If a U.S. license holder needs a conventional U.S. IDP, AAA or AATA is the appropriate official route."]
    ],
    sources: %i[usagov state aaa aaa_faq aata_faq]
  },
  {
    path: "guides/how-to-apply-for-an-idp-in-the-us/index.html",
    title: "How to Apply for an IDP in the US | Official Routes",
    description: "How U.S. license holders can apply for a conventional International Driving Permit through official U.S. routes.",
    h1: "How to Apply for an IDP in the US",
    kicker: "United States guide",
    direct: "U.S. license holders should use AAA or AATA for a conventional International Driving Permit because official U.S. sources identify those as the authorized U.S. issuers.",
    sections: [
      ["Official issuer choice", "USAGov and the Department of State identify AAA and AATA as the two authorized U.S. organizations for IDPs."],
      ["Typical documents", "AAA and AATA guidance points to a valid U.S. driver license and passport-style photo requirements. Applicants should follow the exact current instructions on the chosen issuer site."],
      ["Before travel", "Check destination-specific driver license rules and carry the IDP together with the original valid driver license."]
    ],
    faq: [
      ["Can a non-U.S. license holder get a U.S. IDP?", "AATA states that it does not issue IDPs for foreign driver licenses. The IDP should generally be issued in the same country as the license."],
      ["Is an IDP renewable?", "USAGov states that an IDP is valid for one year and cannot be renewed."]
    ],
    sources: %i[usagov state aaa aata_steps aata_faq]
  },
  {
    path: "guides/aaa-idp-cost-and-turnaround/index.html",
    title: "AAA IDP Cost and Turnaround | Official Source Summary",
    description: "A sourced summary of AAA IDP fees, online processing, branch processing, mail options and digital-IDP limitations.",
    h1: "AAA IDP Cost and Turnaround",
    kicker: "AAA guide",
    direct: "AAA's official IDP page lists a USD 20 permit fee, online processing of about 5 business days plus shipping, and no digital IDP option.",
    sections: [
      ["Cost evidence", "AAA's official page lists a USD 20 permit fee and a USD 10 passport-photo fee for online applications, plus applicable shipping and tax."],
      ["Turnaround evidence", "AAA states that online IDP processing typically takes 5 business days plus selected shipping time. AAA branch service can be same-day when the branch offers IDP services."],
      ["Digital format", "AAA states that IDPs are physically printed and mailed and that digital versions are not available."]
    ],
    faq: [
      ["Can online AAA IDP processing be expedited?", "AAA's online FAQ says online applications are processed in the order received and cannot be expedited."],
      ["Can I pick up an online AAA application at a branch?", "AAA's online FAQ says online applications are processed centrally and cannot be picked up at a branch."]
    ],
    sources: %i[aaa aaa_faq]
  },
  {
    path: "guides/what-is-aata/index.html",
    title: "What Is AATA? | American Automobile Touring Alliance IDP Guide",
    description: "A sourced explanation of AATA, its U.S. IDP role, eligibility statements and application limits.",
    h1: "What Is AATA?",
    kicker: "AATA entity guide",
    direct: "AATA, the American Automobile Touring Alliance, is identified by official U.S. sources as one of two organizations authorized to issue U.S. International Driving Permits.",
    sections: [
      ["Issuer role", "USAGov names AATA alongside AAA as an authorized U.S. IDP issuer."],
      ["Eligibility", "AATA's FAQ says applicants must be 18 or older and hold a valid U.S. driver's license; it says AATA does not issue IDPs for foreign driver licenses."],
      ["Digital limitation", "AATA's FAQ states that there is no digital version of an IDP and that IDPs are physical documents."]
    ],
    faq: [
      ["Does AATA serve foreign license holders?", "AATA says it does not issue IDPs for foreign driver licenses."],
      ["Does AATA offer a digital IDP?", "AATA says there is no digital version of an IDP."]
    ],
    sources: %i[usagov aata_steps aata_faq aata_app]
  },
  {
    path: "guides/can-i-get-an-idp-the-same-day/index.html",
    title: "Can I Get an IDP the Same Day? | Official Options",
    description: "A sourced guide to same-day conventional IDP options and where private translation support differs.",
    h1: "Can I Get an IDP the Same Day?",
    kicker: "Urgency guide",
    direct: "For U.S. conventional IDPs, AAA branch service may be same-day when the branch provides IDP services. Online processing is not the same as same-day issuance.",
    sections: [
      ["Same-day official route", "AAA states that full-service branch processing can provide an IDP the same day, but branch availability should be confirmed directly."],
      ["Online route", "AAA states that online processing typically takes 5 business days plus shipping. AATA lists processing and shipping separately."],
      ["WorldIDP distinction", "WorldIDP can provide private translation support after review and approval, but that is not the same as a conventional U.S. IDP from AAA or AATA."]
    ],
    faq: [
      ["Can WorldIDP issue a U.S. conventional IDP?", "No. Official U.S. sources identify AAA and AATA as the authorized U.S. IDP issuers."],
      ["Can a digital document replace a conventional physical IDP?", "AAA and AATA both state that conventional IDPs are physical documents and digital versions are not available."]
    ],
    sources: %i[usagov aaa aaa_faq aata_faq]
  },
  {
    path: "guides/aaa-office-locations-for-idps/index.html",
    title: "AAA Office Locations for IDPs | How to Verify Service",
    description: "How to verify whether a AAA branch provides International Driving Permit services without relying on stale location lists.",
    h1: "AAA Office Locations for IDPs",
    kicker: "Branch verification guide",
    direct: "WorldIDP does not maintain an official AAA branch database. Travelers should use AAA's own branch tools and contact the branch directly to confirm IDP service availability.",
    sections: [
      ["Why no copied branch list", "AAA branch services can vary. Re-publishing branch lists can become stale and misleading."],
      ["What to verify", "Confirm IDP service availability, photo requirements, payment methods, branch hours and whether same-day processing is available."],
      ["Mail and online alternatives", "AAA also describes mail and online routes for eligible U.S. license holders."]
    ],
    faq: [
      ["Does every AAA branch issue IDPs?", "AAA instructs travelers to contact the branch office directly to verify IDP service availability."],
      ["Should I trust copied office lists?", "Use AAA's current tools or contact the branch directly because availability and hours can change."]
    ],
    sources: %i[aaa aaa_faq]
  },
  {
    path: "guides/idp-for-non-us-licence-holders/index.html",
    title: "IDP for Non-US Licence Holders | Evidence-Based Guide",
    description: "What non-U.S. licence holders should know about conventional U.S. IDPs and private translation-support documents.",
    h1: "IDP for Non-US Licence Holders",
    kicker: "Eligibility guide",
    direct: "AAA and AATA U.S. IDP routes are for eligible U.S. driver license holders. Non-U.S. licence holders should check the issuing-country rules for their original licence.",
    sections: [
      ["Official U.S. limitation", "AATA states that it does not issue IDPs for foreign driver licenses. AAA materials focus on valid U.S. or territorial driver licenses."],
      ["What travelers should do", "Check the authority in the country that issued the original license, then check destination rules before driving."],
      ["Where WorldIDP fits", "WorldIDP may provide private multilingual translation support for a valid national licence, but it does not replace the original licence or a conventional IDP where one is legally required."]
    ],
    faq: [
      ["Can I use AAA if my licence is not from the United States?", "AAA's application materials focus on U.S. or territorial licenses. Confirm eligibility directly with AAA if unsure."],
      ["Can WorldIDP grant driving rights?", "No. WorldIDP does not grant driving rights and must be used with the original valid license."]
    ],
    sources: %i[usagov aaa aata_faq]
  }
].freeze

def esc(value)
  CGI.escapeHTML(value.to_s)
end

def header
  <<~HTML
    <header class="site-header" data-header>
      <a class="brand" href="/index.html" aria-label="WorldIDP home"><img src="/IMAGES/worldidp-international-driving-permit-logo.webp" alt="WorldIDP - Drive the World" fetchpriority="high" width="250" height="90" decoding="async" /></a>
      <button class="nav-toggle" type="button" data-nav-toggle aria-label="Open navigation" aria-expanded="false"><span></span><span></span><span></span></button>
      <nav class="primary-nav" aria-label="Primary navigation"><a href="/how-to-apply.html">How to apply</a><a href="/what-is-idp.html">What is an IDP?</a><a href="/countries.html">Countries</a><a href="/pricing.html">Pricing</a><a href="/faq.html">FAQ</a></nav>
      <div class="header-actions"><a class="btn btn-secondary" href="/track-order.html">Track order</a><a class="btn btn-primary" href="/checkout.html">Start application</a></div>
    </header>
  HTML
end

def footer
  <<~HTML
    <footer class="site-footer" role="contentinfo">
      <div class="footer-inner">
        <div class="footer-brand"><a class="footer-logo" href="/index.html" aria-label="WorldIDP home"><img src="/IMAGES/worldidp-logo-white.webp" alt="WorldIDP" width="250" height="90" decoding="async" /></a><p>WorldIDP provides private multilingual driving-document translation support for travelers who carry their original valid driver's license.</p></div>
        <div class="footer-links"><div><h3>Guides</h3><a href="/how-to-apply.html">How to apply</a><a href="/what-is-idp.html">What is an IDP?</a><a href="/countries.html">Countries</a><a href="/faq.html">FAQ</a></div><div><h3>Legal</h3><a href="/privacy-policy.html">Privacy Policy</a><a href="/terms-of-service.html">Terms of Service</a><a href="/legal-disclaimer.html">Legal Disclaimer</a></div></div>
      </div>
      <p class="footer-disclaimer">WorldIDP is an independent private company and is not a government agency or U.S. Department of State-authorized IDP issuer. Requirements vary by destination, licence origin, licence language, vehicle category and third-party provider.</p>
      <div class="footer-bottom"><p class="footer-copy">&copy; 2026 WORLDIDP INTERNATIONAL LLC. All rights reserved.</p></div>
    </footer>
  HTML
end

def page_schema(page, url)
  {
    "@context" => "https://schema.org",
    "@graph" => [
      ORG,
      {
        "@type" => "WebPage",
        "@id" => "#{url}#webpage",
        "url" => url,
        "name" => page[:h1],
        "description" => page[:description],
        "datePublished" => TODAY,
        "dateModified" => TODAY,
        "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" },
        "publisher" => ORG
      },
      {
        "@type" => "BreadcrumbList",
        "itemListElement" => [
          { "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" },
          { "@type" => "ListItem", "position" => 2, "name" => page[:h1], "item" => url }
        ]
      },
      {
        "@type" => "FAQPage",
        "mainEntity" => page[:faq].map do |q, a|
          { "@type" => "Question", "name" => q, "acceptedAnswer" => { "@type" => "Answer", "text" => a } }
        end
      }
    ]
  }
end

def render(page)
  url = "https://worldidp.com/#{page[:path].sub(%r{/index\.html$}, "/")}"
  sources = page[:sources].map { |key| SOURCES.fetch(key) }
  source_html = sources.each_with_index.map { |(name, link), idx| %(<li id="source-#{idx + 1}"><a href="#{esc(link)}" rel="nofollow noopener">#{esc(name)}</a></li>) }.join
  sections = page[:sections].map { |h, p| %(<section class="wi-section"><div class="wi-head"><p class="wi-kicker">Sourced guidance</p><h2>#{esc(h)}</h2></div><p>#{esc(p)}</p></section>) }.join("\n")
  faq = page[:faq].map { |q, a| %(<article class="faq-item"><h3>#{esc(q)}</h3><p>#{esc(a)}</p></article>) }.join
  <<~HTML
    <!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1" />
      <title>#{esc(page[:title])}</title>
      <meta name="description" content="#{esc(page[:description])}" />
      <meta name="robots" content="#{ROBOTS}" />
      <link rel="canonical" href="#{url}" />
      <meta property="og:site_name" content="WorldIDP" />
      <meta property="og:title" content="#{esc(page[:title])}" />
      <meta property="og:description" content="#{esc(page[:description])}" />
      <meta property="og:type" content="article" />
      <meta property="og:url" content="#{url}" />
      <link rel="stylesheet" href="/styles.css" />
      <link rel="stylesheet" href="/knowledge.css" />
      <script type="application/ld+json">
    #{JSON.pretty_generate(page_schema(page, url))}
      </script>
    </head>
    <body>
    <a class="skip-link" href="#main">Skip to content</a>
    #{header}
    <main id="main" class="knowledge-main">
      <nav class="wi-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span>/</span><span>#{esc(page[:h1])}</span></nav>
      <section class="wi-hero knowledge-hero"><div class="wi-hero-grid"><div><p class="wi-kicker">#{esc(page[:kicker])} · Last verified #{TODAY}</p><h1>#{esc(page[:h1])}</h1><p class="wi-hero-sub">#{esc(page[:description])}</p></div><div class="wi-answer"><h2>Direct Answer</h2><p>#{esc(page[:direct])}</p></div></div></section>
      #{sections}
      <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">FAQ</p><h2>Common questions</h2></div><div class="knowledge-faq">#{faq}</div></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Sources</p><h2>Official evidence used</h2></div><ol class="knowledge-sources">#{source_html}</ol><p class="knowledge-note">Last verified: #{TODAY}. Unavailable facts are not estimated.</p></section>
      <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">Next step</p><h2>Check destination requirements before applying</h2></div><p>Use the country registry first, then apply only if a private translation-support document fits your situation.</p><div class="wi-hero-actions"><a class="wi-btn wi-btn-ghost" href="/countries.html">Search countries</a><a class="wi-btn" href="/how-to-apply.html">How to apply</a></div></section>
    </main>
    #{footer}
    <script src="/script.js" defer></script>
    </body>
    </html>
  HTML
end

Dir.chdir(ROOT) do
  PAGES.each do |page|
    FileUtils.mkdir_p(File.dirname(page[:path]))
    File.write(page[:path], render(page))
  end

  sitemap = File.read("sitemap.xml")
  PAGES.each do |page|
    loc = "https://worldidp.com/#{page[:path].sub(%r{/index\.html$}, "/")}"
    next if sitemap.include?(loc)

    sitemap.sub!(%r{</urlset>}, <<~XML)
        <url>
          <loc>
            #{loc}
          </loc>
          <lastmod>
            #{TODAY}
          </lastmod>
          <changefreq>
            monthly
          </changefreq>
          <priority>
            0.65
          </priority>
        </url>
      </urlset>
    XML
  end
  File.write("sitemap.xml", sitemap)
end
