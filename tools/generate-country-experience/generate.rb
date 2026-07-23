#!/usr/bin/env ruby
# frozen_string_literal: true

require "cgi"
require "json"
require "fileutils"

ROOT = File.expand_path("../..", __dir__)
TODAY = "2026-07-23"
DISPLAY_DATE = "23 July 2026"
CSS_VERSION = "20260723g"
ROBOTS = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
ORG = JSON.parse(File.read(File.join(ROOT, "data/organization.json")))
COUNTRIES = JSON.parse(File.read(File.join(ROOT, "data/countries.json")))
COUNTRY_BY_SLUG = COUNTRIES.to_h { |c| [c["slug"], c] }
DETAILED_SLUGS = %w[italy spain france germany united-states thailand japan united-arab-emirates mexico australia].freeze
HIGH_DEMAND_COUNTRY_ORDER = %w[
  australia united-states canada malaysia singapore united-kingdom germany france italy spain
  thailand japan united-arab-emirates mexico new-zealand ireland netherlands portugal greece turkey
  indonesia south-korea switzerland austria india saudi-arabia qatar oman kuwait egypt
].freeze

DETAILED_SUMMARIES = {
  "italy" => "Carry your original licence together with both WorldIDP formats for the most practical travel experience in Italy.",
  "spain" => "Use your WorldIDP document with your original licence when renting a vehicle or presenting your driving details in Spain.",
  "france" => "Keep your WorldIDP digital and printed documents available with your original licence for French travel checks.",
  "germany" => "Carry your WorldIDP document with your original licence so licence details are easier to read during rental and travel checks.",
  "united-states" => "Use your WorldIDP multilingual document together with your original valid driving licence when renting or driving in the United States.",
  "thailand" => "Keep your digital WorldIDP document available on your phone with your original valid driving licence while travelling in Thailand.",
  "japan" => "Carry your original licence and WorldIDP document together, and keep printed travel documents organised for in-person checks in Japan.",
  "united-arab-emirates" => "Use your WorldIDP document with your original licence when collecting a vehicle or presenting driving details in the UAE.",
  "mexico" => "Carry your WorldIDP document with your original licence and rental booking details for a smoother rental experience in Mexico.",
  "australia" => "Use your WorldIDP document with your original licence, especially when your licence details need to be read in English."
}.freeze

PRACTICAL_TIPS = {
  "italy" => "Keep an eye on city traffic-restricted zones and rental-desk document checks, especially in historic centres.",
  "spain" => "Rental desks may ask to see the original licence, booking details and travel ID before releasing the vehicle.",
  "france" => "Posted speed limits and weather conditions matter, so follow local signs and rental-provider instructions.",
  "germany" => "Motorway rules can change by posted section; keep documents organised and follow local signage.",
  "united-states" => "Local driving rules remain governed by the state where you drive.",
  "thailand" => "Keep documents easy to access during scooter, motorbike or car-rental checks.",
  "japan" => "Japan uses left-side driving and formal document checks; keep printed travel papers neatly available.",
  "united-arab-emirates" => "Keep passport, booking details and licence documents together for rental pickup.",
  "mexico" => "Carry rental booking details and insurance documents together with your driving documents.",
  "australia" => "State and territory rules can differ, so follow the rental-provider briefing and local road signs."
}.freeze

def esc(value)
  CGI.escapeHTML(value.to_s)
end

def safe(value)
  value.to_s.strip
end

def active_country?(country)
  DETAILED_SLUGS.include?(country["slug"])
end

def format_recommendation(country)
  case country["region"]
  when "Asia"
    "Digital document recommended"
  when "Europe"
    "Digital and printed documents recommended"
  else
    "Digital document ready; printed copy optional"
  end
end

def format_guidance(country)
  case country["region"]
  when "Asia"
    "For many journeys across Asia, the digital WorldIDP document provides fast and convenient access from your phone. Keep it available together with your original valid driving licence. A printed copy can also be added for extra convenience."
  when "Europe"
    "For travel across Europe, carry both the digital and printed WorldIDP documents together with your original valid driving licence. This gives you the most practical format for rental desks and in-person checks."
  else
    "Keep your digital WorldIDP document available with your original valid driving licence. Add the printed document when you prefer a physical copy for rental desks, hotels, travel folders or in-person checks."
  end
end

def country_summary(country)
  DETAILED_SUMMARIES[country["slug"]] || "Carry your original licence together with your WorldIDP multilingual document for a more practical travel and rental experience in #{country["name"]}."
end

def country_scope(country)
  return "Use your WorldIDP multilingual document together with your original valid driving licence when renting or driving in the United States. The multilingual format helps make the licence details easier to understand during rental and travel checks." if country["slug"] == "united-states"
  return safe(country["idpStatusApplies"]) unless safe(country["idpStatusApplies"]).empty?

  "Use the WorldIDP multilingual document as travel support alongside your original valid driving licence. It helps present your licence details in a clearer multilingual format."
end

def rental_guidance
  "Present your WorldIDP multilingual document together with your original valid driving licence when collecting a rental vehicle. The multilingual format is designed to help rental staff read and understand the licence information more easily."
end

def driving_side(country)
  side = safe(country["drivingSide"])
  side = safe(country["legacyDrivingSide"]) if side.empty?
  side.empty? ? "Check destination guide" : side.capitalize
end

def hub_countries
  priority = HIGH_DEMAND_COUNTRY_ORDER.each_with_index.to_h
  COUNTRIES.sort_by { |country| [priority.fetch(country["slug"], 10_000), country["name"]] }
end

def convention_text(country)
  conventions = Array(country["conventions"]).map { |c| c.tr("-", " ").split.map(&:capitalize).join(" ") }
  conventions.empty? ? "Carry your documents together and follow destination guidance" : conventions.join(", ")
end

def meta_description(country)
  "WorldIDP #{country["name"]} guide with recommended document format, what to carry, rental-car guidance, driving essentials and practical travel checklist."
end

def header(active: "Countries")
  nav = [
    ["Countries", "/countries.html"],
    ["What is IDP?", "/what-is-idp.html"],
    ["How to Apply", "/how-to-apply.html"],
    ["Pricing", "/pricing.html"],
    ["Contact Us", "/contact-us.html"],
    ["My Order", "/track-order.html"]
  ].map { |name, href| %(<a href="#{href}"#{name == active ? ' aria-current="page"' : ""}>#{name}</a>) }.join("\n        ")
  <<~HTML
    <header class="site-header" data-header>
      <a class="brand" href="/index.html" aria-label="WorldIDP home">
        <img src="/IMAGES/worldidp-international-driving-permit-logo.webp" alt="WorldIDP - Drive the World" fetchpriority="high" width="250" height="90" decoding="async" />
      </a>
      <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" data-nav-toggle><span></span><span></span><span></span></button>
      <nav class="primary-nav" aria-label="Main navigation" data-nav>
        #{nav}
      </nav>
      <div class="header-actions">
        <a class="btn btn-header" href="/pricing.html">Start Application</a>
        <button class="language-pill" type="button" aria-label="Current language: English"><span class="flag-uk" aria-hidden="true"></span> EN</button>
      </div>
    </header>
  HTML
end

def footer
  <<~HTML
    <footer class="site-footer" role="contentinfo">
      <span class="footer-aurora" aria-hidden="true"></span>
      <svg class="footer-route" viewBox="0 0 760 460" fill="none" aria-hidden="true" preserveAspectRatio="xMidYMid meet">
        <defs>
          <linearGradient id="frG" x1="0" y1="1" x2="1" y2="0"><stop offset="0" stop-color="#2456e6"/><stop offset="1" stop-color="#7ec0ff"/></linearGradient>
          <radialGradient id="frDot" cx="0.5" cy="0.4" r="0.6"><stop offset="0" stop-color="#bfe0ff"/><stop offset="1" stop-color="#2456e6"/></radialGradient>
        </defs>
        <path d="M24 414 C 250 384 470 300 742 56" stroke="rgba(126,192,255,.14)" stroke-width="1.5"/>
        <path class="fr-path" d="M24 414 C 250 384 470 300 742 56" stroke="url(#frG)" stroke-width="2.4" stroke-linecap="round" stroke-dasharray="1.5 15"/>
        <g class="fr-pin"><circle class="fr-ring" cx="24" cy="414" r="15"/><circle cx="24" cy="414" r="5" fill="url(#frDot)"/></g>
        <g class="fr-pin fr-pin-2"><circle class="fr-ring" cx="742" cy="56" r="19"/><circle cx="742" cy="56" r="6" fill="url(#frDot)"/></g>
      </svg>
      <div class="footer-inner">
        <div class="footer-cta"><div><p class="footer-cta-title">Ready to <b>drive the world?</b></p><p class="footer-cta-sub">Your multilingual driving-licence translation, prepared digitally and ready before you travel.</p></div><a class="footer-cta-btn" href="/pricing.html">Start application <span aria-hidden="true">-&gt;</span></a></div>
        <div class="footer-divider"></div>
        <div class="footer-main">
          <div class="footer-brand"><img class="footer-logo" src="/IMAGES/worldidp-logo-white.webp" alt="WorldIDP - Drive the World" width="1397" height="424" loading="lazy" title="WorldIDP white logo" decoding="async" /><p class="footer-tagline">A private, multilingual translation of your national licence - ready in minutes, carried alongside your original licence.</p><ul class="footer-contact"><li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="m3 7 9 6 9-6"/></svg><a href="mailto:hello@worldidp.com">hello@worldidp.com</a></li><li><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 11.5a8.38 8.38 0 0 1-8.5 8.5 8.5 8.5 0 0 1-3.8-.9L3 21l1.9-5.7A8.5 8.5 0 1 1 21 11.5z"/></svg><span>24/7 live chat support</span></li></ul></div>
          <nav class="footer-col" aria-label="Product"><h3>Product</h3><ul><li><a href="/pricing.html">Pricing</a></li><li><a href="/what-is-idp.html">What is an IDP?</a></li><li><a href="/countries.html">Countries</a></li><li><a href="/index.html#reviews">Reviews</a></li><li><a href="/how-to-apply.html">How to apply</a></li></ul></nav>
          <nav class="footer-col" aria-label="Support"><h3>Support</h3><ul><li><a href="/checkout.html">Start application</a></li><li><a href="/track-order.html">Track my order</a></li><li><a href="/faq.html">FAQs</a></li><li><a href="/contact-us.html">Contact us</a></li><li><a href="/refund-return-policy.html">Refund &amp; returns</a></li></ul></nav>
          <nav class="footer-col" aria-label="Company"><h3>Company</h3><ul><li><a href="/about-us.html">About us</a></li><li><a href="/contact-us.html">Partner with us</a></li><li><a href="/index.html">Blog</a></li><li><a href="/accessibility-statement.html">Accessibility</a></li></ul></nav>
          <nav class="footer-col" aria-label="Legal"><h3>Legal</h3><ul><li><a href="/privacy-policy.html">Privacy Policy</a></li><li><a href="/terms-of-service.html">Terms of Service</a></li><li><a href="/cookie-policy.html">Cookie Policy</a></li><li><a href="/legal-disclaimer.html">Legal Disclaimer</a></li><li><a href="/dmca-and-intellectual-property-policy.html">DMCA &amp; IP</a></li></ul></nav>
          <nav class="footer-col" aria-label="Policies"><h3>Policies</h3><ul><li><a href="/refund-return-policy.html">Refund &amp; Returns</a></li><li><a href="/shipping-policy.html">Shipping &amp; Delivery</a></li><li><a href="/payment-policy.html">Payment Policy</a></li></ul></nav>
        </div>
        <div class="footer-divider"></div>
        <p class="footer-disclaimer">WorldIDP provides a private multi-language translation of your valid national driver's license to help you communicate your driving credentials abroad. It is carried together with - and never replaces - your original national license. WorldIDP is an independent private company and is not a government agency.</p>
        <div class="footer-bottom"><p class="footer-copy">&copy; 2026 WORLDIDP INTERNATIONAL LLC. All rights reserved.</p><ul class="footer-legal"><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/terms-of-service.html">Terms</a></li><li><a href="/cookie-policy.html">Cookies</a></li><li><a href="/legal-disclaimer.html">Disclaimer</a></li></ul></div>
      </div>
    </footer>
    <a class="chat-fab" href="/contact-us.html" aria-label="Contact support"><span></span></a>
  HTML
end

def schema_for_country(country, faqs, desc)
  url = "https://worldidp.com/countries/#{country["slug"]}/"
  {
    "@context" => "https://schema.org",
    "@graph" => [
      { "@type" => "BreadcrumbList", "itemListElement" => [
        { "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" },
        { "@type" => "ListItem", "position" => 2, "name" => "Countries", "item" => "https://worldidp.com/countries.html" },
        { "@type" => "ListItem", "position" => 3, "name" => country["name"], "item" => url }
      ] },
      { "@type" => "WebPage", "@id" => "#{url}#webpage", "url" => url, "name" => "WorldIDP #{country["name"]} Country Guide", "description" => desc, "dateModified" => TODAY, "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" }, "publisher" => ORG, "about" => [{ "@type" => "Country", "name" => country["name"] }, { "@type" => "Thing", "name" => "WorldIDP multilingual driving document" }] },
      { "@type" => "FAQPage", "mainEntity" => faqs.map { |q, a| { "@type" => "Question", "name" => q, "acceptedAnswer" => { "@type" => "Answer", "text" => a } } } }
    ]
  }
end

def country_faq(country)
  [
    ["What should I carry in #{country["name"]}?", "Carry your original valid driving licence, your WorldIDP digital document, a printed WorldIDP document where recommended, passport or identification, and rental booking details when applicable."],
    ["How should I use WorldIDP at a rental desk?", rental_guidance],
    ["Which WorldIDP format is recommended for #{country["name"]}?", "#{format_recommendation(country)}. #{format_guidance(country)}"],
    ["Does WorldIDP replace my original licence?", "No. WorldIDP is designed to be presented together with your original valid driving licence."]
  ]
end

def guide_card(icon, title, text)
  %(<article class="guide-card"><span aria-hidden="true">#{icon}</span><h3>#{esc(title)}</h3><p>#{esc(text)}</p></article>)
end

def carry_items(country)
  items = ["Original valid driving licence", "WorldIDP digital document", "Printed WorldIDP document where recommended", "Passport or identification", "Rental booking details when applicable"]
  %(<ul class="carry-list">#{items.map { |item| "<li>#{esc(item)}</li>" }.join}</ul>)
end

def checklist
  [
    "Keep your original valid driving licence with you.",
    "Open or print your WorldIDP document.",
    "Check that your personal and licence details are correct.",
    "Present both documents when requested.",
    "Keep your rental booking and passport available."
  ].each_with_index.map { |item, i| %(<li><span>#{i + 1}</span><p>#{esc(item)}</p></li>) }.join
end

def source_cards(country)
  sources = Array(country["officialSources"]).first(4)
  if sources.empty?
    return %(<article class="country-source-card"><div><b>WorldIDP country registry</b><small>Editorial review · #{DISPLAY_DATE}</small></div><div class="country-source-tags"><span>Product guidance</span><span>Travel checklist</span></div><a href="/editorial-policy.html">Editorial policy</a></article>)
  end

  sources.each_with_index.map do |source, i|
    supports = Array(source["supports"]).first(3).map { |s| %(<span>#{esc(s.tr("-", " ").split.map(&:capitalize).join(" "))}</span>) }.join
    %(<article class="country-source-card"><div><b>#{esc(source["name"])}</b><small>Source #{i + 1}</small></div><div class="country-source-tags">#{supports}</div><a href="#{esc(source["url"])}" rel="nofollow noopener" target="_blank">Open source</a></article>)
  end.join("\n")
end

def related_cards(country)
  related = Array(country["relatedCountries"]).map { |slug| COUNTRY_BY_SLUG[slug] }.compact.first(3)
  related = COUNTRIES.select { |c| c["region"] == country["region"] && c["slug"] != country["slug"] }.first(3) if related.empty?
  related.map { |rel| %(<a class="country-related-card" href="/countries/#{rel["slug"]}/"><span>#{esc(rel["flag"])}</span><b>#{esc(rel["name"])}</b><small>#{esc(format_recommendation(rel))}</small></a>) }.join
end

def render_country(country)
  desc = meta_description(country)
  faqs = country_faq(country)
  practical = PRACTICAL_TIPS[country["slug"]] || "Before driving in #{country["name"]}, keep your licence, WorldIDP document, passport and booking information together so travel checks are easier to handle."
  secondary_note = country["slug"] == "united-states" ? "<p>Local driving rules remain governed by the state where you drive.</p>" : ""
  <<~HTML
    <!doctype html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>WorldIDP #{esc(country["name"])} Country Guide | International Driving Permit</title>
      <meta name="description" content="#{esc(desc)}" />
      <meta name="author" content="WorldIDP Editorial Team" />
      <meta name="robots" content="#{ROBOTS}" />
      <meta name="theme-color" content="#0758d8" />
      <link rel="canonical" href="https://worldidp.com/countries/#{country["slug"]}/" />
      <meta property="og:type" content="article" />
      <meta property="og:site_name" content="WorldIDP" />
      <meta property="og:title" content="WorldIDP #{esc(country["name"])} Country Guide" />
      <meta property="og:description" content="#{esc(desc)}" />
      <meta property="og:url" content="https://worldidp.com/countries/#{country["slug"]}/" />
      <meta property="og:image" content="https://worldidp.com/IMAGES/worldidp-international-driving-permit-social-preview.webp" />
      <link rel="icon" href="/IMAGES/favicon.ico" sizes="any" />
      <link rel="stylesheet" href="/styles.css" />
      <link rel="stylesheet" href="/what-is-idp.css" />
      <link rel="stylesheet" href="/knowledge.css?v=#{CSS_VERSION}" />
      <script type="application/ld+json">
    #{JSON.pretty_generate(schema_for_country(country, faqs, desc))}
      </script>
    </head>
    <body class="wi-page knowledge-page country-page final-country-page">
      <a class="sr-only" href="#main">Skip to main content</a>
      #{header}
      <main id="main">
        <section class="wi-hero country-hero premium-country-hero" aria-labelledby="country-title">
          <div class="wi-hero-grid">
            <div class="wi-hero-copy">
              <ol class="wi-breadcrumb" aria-label="Breadcrumb"><li><a href="/index.html">Home</a></li><li><a href="/countries.html">Countries</a></li><li aria-current="page">#{esc(country["name"])}</li></ol>
              <span class="wi-kicker">#{esc(country["name"])} country guide</span>
              <h1 id="country-title">WorldIDP Guide for <em>#{esc(country["name"])}</em></h1>
              <p class="wi-lede">#{esc(country_summary(country))}</p>
              <div class="wi-hero-cta"><a class="wi-btn" href="/pricing.html">Start application</a><a class="wi-btn wi-btn-ghost" href="#what-to-carry">What to carry</a></div>
            </div>
            <aside class="country-hero-card compact-summary" aria-label="#{esc(country["name"])} summary">
              <span class="country-flag" aria-hidden="true">#{esc(country["flag"])}</span>
              <b>#{esc(format_recommendation(country))}</b>
              <p>WorldIDP recommendation for #{esc(country["name"])}</p>
              <dl><div><dt>Driving side</dt><dd>#{esc(driving_side(country))}</dd></div><div><dt>Document</dt><dd>Digital + multilingual</dd></div></dl>
            </aside>
          </div>
        </section>
        <section class="country-answer"><span class="wi-kicker">Direct answer</span><h2>Select the right format before you travel</h2><p>Select your destination to check the recommended WorldIDP format. Your WorldIDP document should be presented together with your original valid driving licence when requested by a rental provider or local authority.</p></section>
        <section class="wi-section" id="what-to-carry"><div class="country-split"><article class="carry-box"><span class="wi-kicker">What to carry</span><h2>Keep these documents together</h2>#{carry_items(country)}</article><article class="format-box"><span class="wi-kicker">WorldIDP recommendation</span><h2>#{esc(format_recommendation(country))}</h2><p>#{esc(format_guidance(country))}</p></article></div></section>
        <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">How to use it</p><h2>Use your WorldIDP document with confidence</h2></div><div class="guide-card-grid">#{guide_card("1", "Keep documents together", "Store your original licence, WorldIDP document, passport and booking details in one easy-to-reach place.")}#{guide_card("2", "Present both documents", "Show the WorldIDP document together with your original valid driving licence when requested.")}#{guide_card("3", "Check the details", "Make sure your personal details and licence categories match your original licence before you travel.")}</div></section>
        <section class="wi-section"><div class="country-split"><article class="country-panel"><span class="wi-kicker">Rental-car guidance</span><h2>At the rental desk</h2><p>#{esc(rental_guidance)}</p>#{secondary_note}</article><article class="country-panel"><span class="wi-kicker">Driving essentials</span><h2>Before driving in #{esc(country["name"])}</h2><ul class="wi-flist"><li>Driving side: #{esc(driving_side(country))}</li><li>Format: #{esc(format_recommendation(country))}</li><li>Convention context: #{esc(convention_text(country))}</li><li>Keep passport or travel ID available when requested.</li></ul></article></div></section>
        <section class="wi-section wi-section-tint"><div class="country-split"><article class="country-panel"><span class="wi-kicker">Digital and printed options</span><h2>Choose the practical format</h2><p>#{esc(format_guidance(country))}</p></article><article class="country-panel"><span class="wi-kicker">Before you drive</span><h2>Simple travel checklist</h2><ol class="drive-checklist">#{checklist}</ol></article></div></section>
        <section class="wi-section"><div class="country-split"><article class="country-panel"><span class="wi-kicker">Practical tips</span><h2>Travel notes for #{esc(country["name"])}</h2><p>#{esc(practical)}</p></article><article class="country-panel"><span class="wi-kicker">Helpful reminder</span><h2>Your original licence stays essential</h2><p>WorldIDP is designed to make your licence information easier to understand in a multilingual format. It is carried with your original valid driving licence.</p></article></div></section>
        <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">FAQ</p><h2>#{esc(country["name"])} travel document questions</h2></div><div class="wi-faq country-faq">#{faqs.map { |q, a| %(<details><summary>#{esc(q)}<span class="wi-plus" aria-hidden="true"></span></summary><div class="wi-faq-body">#{esc(a)}</div></details>) }.join}</div></section>
        <section class="wi-section sources-secondary"><div class="wi-head"><p class="wi-kicker">Sources and methodology</p><h2>How this guide is maintained</h2><p>WorldIDP uses destination information, product guidance and official-source review where available. Legal requirements can change, so official local rules remain the controlling authority.</p></div><div class="country-source-list">#{source_cards(country)}</div></section>
        <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">More destinations</p><h2>Continue planning your trip</h2></div><div class="country-related-grid">#{related_cards(country)}</div></section>
        <section class="wi-cta"><h2>Prepare your WorldIDP document for #{esc(country["name"])}</h2><p>Choose digital delivery, add printed support when useful, and keep your original valid driving licence with you when you travel.</p><a class="wi-btn" href="/pricing.html">Start application</a></section>
        <div class="wi-bottom-space"></div>
      </main>
      #{footer}
      <script src="/script.js" defer></script>
      <script src="/analytics-beacon.js?v=20260722" defer></script>
    </body>
    </html>
  HTML
end

def hub_faq
  [
    ["Which country guides appear first?", "The directory starts with commonly checked travel destinations such as Australia, United States, Canada, Malaysia, Singapore, United Kingdom, Germany, France, Italy, Spain, Thailand and Japan."],
    ["What does each WorldIDP country guide explain?", "Each guide explains the recommended WorldIDP document format, what to carry, how to present the document with your original valid driving licence, rental-car guidance and driving side."],
    ["Does a WorldIDP document replace my original driving licence?", "No. A WorldIDP multilingual document is designed to be carried together with your original valid driving licence."],
    ["Should I carry a digital or printed WorldIDP document?", "The recommended format depends on the destination. Many Asia guides recommend the digital document, while many Europe guides recommend carrying both digital and printed documents."]
  ]
end

def hub_schema
  ordered = hub_countries
  {
    "@context" => "https://schema.org",
    "@graph" => [
      { "@type" => "BreadcrumbList", "itemListElement" => [{ "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" }, { "@type" => "ListItem", "position" => 2, "name" => "Countries", "item" => "https://worldidp.com/countries.html" }] },
      {
        "@type" => "CollectionPage",
        "@id" => "https://worldidp.com/countries.html#webpage",
        "name" => "International Driving Permit Requirements by Country",
        "url" => "https://worldidp.com/countries.html",
        "description" => "WorldIDP country guides explain recommended digital and printed document formats, what to carry with an original valid driving licence, rental-car guidance and driving side by destination.",
        "dateModified" => TODAY,
        "inLanguage" => "en",
        "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" },
        "publisher" => ORG,
        "about" => [
          { "@type" => "Thing", "name" => "International Driving Permit requirements by country" },
          { "@type" => "Thing", "name" => "WorldIDP multilingual driving document" },
          { "@type" => "Thing", "name" => "Driving abroad with an original valid driving licence" },
          { "@type" => "Thing", "name" => "Rental car document checks" }
        ],
        "mainEntity" => { "@id" => "https://worldidp.com/countries.html#country-guides" }
      },
      {
        "@type" => "ItemList",
        "@id" => "https://worldidp.com/countries.html#country-guides",
        "name" => "Country guides",
        "numberOfItems" => ordered.length,
        "itemListElement" => ordered.each_with_index.map { |c, i| { "@type" => "ListItem", "position" => i + 1, "name" => c["name"], "url" => "https://worldidp.com/countries/#{c["slug"]}/" } }
      },
      {
        "@type" => "FAQPage",
        "@id" => "https://worldidp.com/countries.html#faq",
        "mainEntity" => hub_faq.map { |q, a| { "@type" => "Question", "name" => q, "acceptedAnswer" => { "@type" => "Answer", "text" => a } } }
      }
    ]
  }
end

def hub_card(country, index)
  hidden = index >= 24 ? " is-hidden-initial" : ""
  %(<article class="country-guide-card#{hidden}" data-name="#{esc(country["name"].downcase)}" data-region="#{esc(country["region"])}"><div class="country-guide-top"><span aria-hidden="true">#{esc(country["flag"])}</span><div><p>#{esc(country["region"])}</p><h3>#{esc(country["name"])}</h3></div></div><strong>#{esc(format_recommendation(country))}</strong><p>#{esc(country_summary(country))}</p><dl><div><dt>Driving side</dt><dd>#{esc(driving_side(country))}</dd></div><div><dt>What to carry</dt><dd>Original licence + WorldIDP</dd></div></dl><a class="country-guide-link" href="/countries/#{country["slug"]}/">View #{esc(country["name"])} guide</a></article>)
end

def localize_site_paths(html, prefix)
  html.gsub(/(href|src)="\/(?!\/)/) { "#{$1}=\"#{prefix}" }
end

def render_hub
  ordered_countries = hub_countries
  cards = ordered_countries.each_with_index.map { |country, i| hub_card(country, i) }.join("\n")
  faqs = hub_faq
  <<~HTML
    <!doctype html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>International Driving Permit Requirements by Country | 124 WorldIDP Guides</title>
      <meta name="description" content="Explore 124 WorldIDP country guides with recommended digital or printed document format, driving side, what to carry with your original licence, and rental-car guidance." />
      <meta name="author" content="WorldIDP Editorial Team" />
      <meta name="robots" content="#{ROBOTS}" />
      <meta name="theme-color" content="#0758d8" />
      <link rel="canonical" href="https://worldidp.com/countries.html" />
      <meta property="og:type" content="article" />
      <meta property="og:site_name" content="WorldIDP" />
      <meta property="og:title" content="International Driving Permit Requirements by Country | 124 WorldIDP Guides" />
      <meta property="og:description" content="Explore 124 WorldIDP country guides with recommended digital or printed document format, driving side, what to carry with your original licence, and rental-car guidance." />
      <meta property="og:url" content="https://worldidp.com/countries.html" />
      <meta property="og:image" content="https://worldidp.com/IMAGES/worldidp-international-driving-permit-social-preview.webp" />
      <link rel="icon" href="/IMAGES/favicon.ico" sizes="any" />
      <link rel="stylesheet" href="/styles.css" />
      <link rel="stylesheet" href="/what-is-idp.css" />
      <link rel="stylesheet" href="/knowledge.css?v=#{CSS_VERSION}" />
      <script type="application/ld+json">
    #{JSON.pretty_generate(hub_schema)}
      </script>
    </head>
    <body class="wi-page knowledge-page country-hub-page final-country-hub">
      <a class="sr-only" href="#main">Skip to main content</a>
      #{header}
      <main id="main">
        <section class="wi-hero country-hub-hero" aria-labelledby="hub-title"><div class="wi-hero-grid"><div class="wi-hero-copy"><ol class="wi-breadcrumb" aria-label="Breadcrumb"><li><a href="/index.html">Home</a></li><li aria-current="page">Countries</li></ol><span class="wi-kicker">Destination guidance</span><h1 id="hub-title">International Driving Permit Requirements by Country</h1><p class="wi-lede">Choose your destination to see which WorldIDP document format to carry, how to use it with your original driving licence, and practical guidance for renting and driving abroad.</p><div class="wi-hero-cta"><a class="wi-btn" href="#country-directory">Choose destination</a><a class="wi-btn wi-btn-ghost" href="/pricing.html">View document options</a></div></div><aside class="country-hub-summary compact-summary" aria-label="WorldIDP country guide summary"><span>Travel document support</span><dl><div><dt>Countries covered</dt><dd>124</dd></div><div><dt>Available formats</dt><dd>Digital and printed</dd></div><div><dt>Languages</dt><dd>Multilingual document</dd></div><div><dt>Support</dt><dd>Worldwide customer assistance</dd></div></dl></aside></div></section>
        <section class="country-answer"><span class="wi-kicker">Direct answer</span><h2>Choose your destination and recommended format</h2><p>Select your destination to check the recommended WorldIDP format. Your WorldIDP document should be presented together with your original valid driving licence when requested by a rental provider or local authority.</p></section>
        <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Customer guidance</p><h2>Plan with a clear document checklist</h2></div><div class="country-facts-grid"><article class="country-fact-card"><span>Recommended format</span><strong>Digital, printed or both depending on destination.</strong></article><article class="country-fact-card"><span>What to carry</span><strong>Original licence, WorldIDP document, passport and booking details.</strong></article><article class="country-fact-card"><span>Rental support</span><strong>Multilingual licence details designed to help rental staff read your information.</strong></article><article class="country-fact-card"><span>Driving side</span><strong>Each guide shows whether local traffic drives on the left or right.</strong></article></div></section>
        <section class="wi-section wi-section-tint" id="country-directory"><div class="wi-head"><p class="wi-kicker">Directory</p><h2>Country guides</h2><p>Search by country or region. Each guide explains the recommended WorldIDP format, what to carry and how to use the document with your original licence.</p></div><div class="country-toolbar"><label><span>Search</span><input id="countrySearch" type="search" placeholder="Search Italy, Japan, UAE..." autocomplete="off" /></label><div class="country-filter-group" aria-label="Region filters"><button class="is-active" type="button" data-region="">All regions</button><button type="button" data-region="Europe">Europe</button><button type="button" data-region="Asia">Asia</button><button type="button" data-region="Middle East">Middle East</button><button type="button" data-region="Americas">Americas</button><button type="button" data-region="Africa">Africa</button><button type="button" data-region="Oceania">Oceania</button></div><button class="country-reset" type="button" id="countryReset">Clear filters</button><p class="country-count" id="countryCount" aria-live="polite">Showing 24 country guides</p></div><div class="country-guide-grid" id="countryGrid">#{cards}</div><div class="load-more-wrap"><button class="wi-btn" type="button" id="loadMoreCountries">Load more countries</button></div></section>
        <section class="wi-section"><div class="country-split"><article class="country-panel"><span class="wi-kicker">How to use WorldIDP</span><h2>Present both documents together</h2><p>WorldIDP is designed to help communicate your driving licence details in a multilingual format. Keep it with your original valid driving licence whenever you rent or drive abroad.</p></article><article class="country-panel"><span class="wi-kicker">Travel-ready formats</span><h2>Digital and printed options</h2><p>Digital delivery gives fast phone access. Printed support is useful for rental counters, travel folders and in-person checks.</p></article></div></section>
        <section class="wi-section wi-section-tint" id="country-faq"><div class="wi-head"><p class="wi-kicker">FAQ</p><h2>Country guide questions</h2></div><div class="wi-faq country-faq">#{faqs.map { |q, a| %(<details><summary>#{esc(q)}<span class="wi-plus" aria-hidden="true"></span></summary><div class="wi-faq-body">#{esc(a)}</div></details>) }.join}</div></section>
        <section class="wi-cta"><h2>Ready to prepare your WorldIDP document?</h2><p>Choose your destination, review the recommended format and start your application when you are ready.</p><a class="wi-btn" href="/pricing.html">View document options</a></section>
        <div class="wi-bottom-space"></div>
      </main>
      #{footer}
      <script src="/script.js" defer></script>
      <script>(function(){var q=document.getElementById('countrySearch');var count=document.getElementById('countryCount');var reset=document.getElementById('countryReset');var load=document.getElementById('loadMoreCountries');var cards=Array.prototype.slice.call(document.querySelectorAll('.country-guide-card'));var region='';var limit=24;function setActive(){document.querySelectorAll('[data-region]').forEach(function(b){b.classList.toggle('is-active',b.dataset.region===region);});}function apply(){var term=(q.value||'').toLowerCase().trim();var matches=cards.filter(function(card){return (!term||(card.dataset.name||'').indexOf(term)!==-1)&&(!region||card.dataset.region===region);});cards.forEach(function(card){card.hidden=true;});matches.forEach(function(card,i){card.hidden=i>=limit;});count.textContent='Showing '+Math.min(matches.length,limit)+' of '+matches.length+' country guides';load.hidden=matches.length<=limit;}document.querySelectorAll('[data-region]').forEach(function(b){b.addEventListener('click',function(){region=b.dataset.region;limit=24;setActive();apply();});});q.addEventListener('input',function(){limit=24;apply();});reset.addEventListener('click',function(){q.value='';region='';limit=24;setActive();apply();q.focus();});load.addEventListener('click',function(){limit+=24;apply();});apply();})();</script>
      <script src="/analytics-beacon.js?v=20260722" defer></script>
    </body>
    </html>
  HTML
end

def render_editorial_policy
  schema = { "@context" => "https://schema.org", "@type" => "WebPage", "name" => "WorldIDP Editorial Policy", "url" => "https://worldidp.com/editorial-policy.html", "dateModified" => TODAY, "publisher" => ORG }
  <<~HTML
    <!doctype html>
    <html lang="en" dir="ltr">
    <head>
      <meta charset="UTF-8" />
      <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      <title>Editorial Policy | WorldIDP</title>
      <meta name="description" content="How WorldIDP creates, reviews and updates clear travel-document guidance for international drivers." />
      <meta name="author" content="WorldIDP Editorial Team" />
      <meta name="robots" content="#{ROBOTS}" />
      <meta name="theme-color" content="#0758d8" />
      <link rel="canonical" href="https://worldidp.com/editorial-policy.html" />
      <meta property="og:type" content="article" />
      <meta property="og:site_name" content="WorldIDP" />
      <meta property="og:title" content="Editorial Policy | WorldIDP" />
      <meta property="og:description" content="How WorldIDP creates, reviews and updates clear travel-document guidance for international drivers." />
      <meta property="og:url" content="https://worldidp.com/editorial-policy.html" />
      <meta property="og:image" content="https://worldidp.com/IMAGES/worldidp-international-driving-permit-social-preview.webp" />
      <link rel="icon" href="/IMAGES/favicon.ico" sizes="any" />
      <link rel="stylesheet" href="/styles.css" />
      <link rel="stylesheet" href="/what-is-idp.css" />
      <link rel="stylesheet" href="/knowledge.css?v=#{CSS_VERSION}" />
      <script type="application/ld+json">
    #{JSON.pretty_generate(schema)}
      </script>
    </head>
    <body class="wi-page knowledge-page editorial-page">
      <a class="sr-only" href="#main">Skip to main content</a>
      #{header(active: "Editorial")}
      <main id="main">
        <section class="wi-hero editorial-hero" aria-labelledby="policy-title"><div class="wi-hero-grid"><div class="wi-hero-copy"><ol class="wi-breadcrumb" aria-label="Breadcrumb"><li><a href="/index.html">Home</a></li><li aria-current="page">Editorial Policy</li></ol><span class="wi-kicker">WorldIDP editorial policy</span><h1 id="policy-title">Clear travel-document guidance, reviewed with care</h1><p class="wi-lede">WorldIDP creates practical country and product guidance so travellers can understand what to carry, how to use their document and where to find support before they drive abroad.</p><div class="wi-hero-cta"><a class="wi-btn" href="/countries.html">Browse country guides</a><a class="wi-btn wi-btn-ghost" href="/contact-us.html">Send a correction</a></div></div><aside class="country-hub-summary compact-summary"><span>Policy focus</span><dl><div><dt>Content</dt><dd>Travel guidance</dd></div><div><dt>Review</dt><dd>Editorial team</dd></div><div><dt>Updated</dt><dd>#{DISPLAY_DATE}</dd></div><div><dt>Contact</dt><dd>hello@worldidp.com</dd></div></dl></aside></div></section>
        <section class="country-answer"><span class="wi-kicker">Short explanation</span><h2>Helpful, practical and easy to verify</h2><p>Our editorial work turns destination information, product guidance and customer-support knowledge into clear pages that help travellers prepare their WorldIDP document and original driving licence before a trip.</p></section>
        <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Creation process</p><h2>How WorldIDP content is created</h2></div><div class="guide-card-grid">#{guide_card("1", "Define the traveller question", "We start with what a customer needs to know before renting, driving or presenting a document abroad.")}#{guide_card("2", "Separate product guidance from rules", "WorldIDP recommendations are labelled as practical travel guidance, not universal government guarantees.")}#{guide_card("3", "Keep copy useful", "Pages are written in short sections, checklists and direct answers so travellers can act quickly.")}</div></section>
        <section class="wi-section wi-section-tint"><div class="country-split"><article class="country-panel"><span class="wi-kicker">Source priorities</span><h2>What we prioritise</h2><ul class="wi-flist"><li>Government, transport authority and treaty sources.</li><li>Embassy, consular and official tourism guidance.</li><li>Rental-provider information for rental-specific topics.</li><li>WorldIDP product and customer-support information for service guidance.</li></ul></article><article class="country-panel"><span class="wi-kicker">Review rhythm</span><h2>How information is reviewed</h2><p>Pages are reviewed when country information is added, when product guidance changes, or when a customer, authority or team member flags a correction.</p></article></div></section>
        <section class="wi-section"><div class="country-split"><article class="country-panel"><span class="wi-kicker">Updates</span><h2>Corrections and improvements</h2><p>When we identify a clearer source or a better customer explanation, we update the page and keep the wording focused on what travellers should carry and how they should use their WorldIDP document.</p></article><article class="country-panel"><span class="wi-kicker">What we do not claim</span><h2>Boundaries of the service</h2><p>WorldIDP is a private multilingual document service. It does not replace an original valid driving licence, act as a government agency or promise acceptance by every authority or provider.</p></article></div></section>
        <section class="wi-cta"><h2>Have a source or correction?</h2><p>Send our team the destination, page URL and source link. We will review it and update customer guidance where appropriate.</p><a class="wi-btn" href="/contact-us.html">Contact WorldIDP</a></section>
        <div class="wi-bottom-space"></div>
      </main>
      #{footer}
      <script src="/script.js" defer></script>
      <script src="/analytics-beacon.js?v=20260722" defer></script>
    </body>
    </html>
  HTML
end

Dir.chdir(ROOT) do
  File.write("countries.html", localize_site_paths(render_hub, ""))
  File.write("editorial-policy.html", localize_site_paths(render_editorial_policy, ""))
  COUNTRIES.each do |country|
    FileUtils.mkdir_p(File.join("countries", country["slug"]))
    File.write(File.join("countries", country["slug"], "index.html"), localize_site_paths(render_country(country), "../../"))
  end
  FileUtils.mkdir_p("templates")
  File.write("templates/country-page-template.html", localize_site_paths(render_country(COUNTRIES.first).gsub(COUNTRIES.first["name"], "{Country}"), "../"))
end
