#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "csv"
require "fileutils"
require "rexml/document"

ROOT = File.expand_path("../..", __dir__)
TODAY = "2026-07-23"
ROBOTS_INDEX = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
PILOT_SLUGS = %w[italy spain france germany united-states thailand japan united-arab-emirates mexico australia].freeze

ORG = {
  "@type" => "Organization",
  "name" => "WORLDIDP INTERNATIONAL LLC",
  "alternateName" => "WorldIDP",
  "url" => "https://worldidp.com/",
  "logo" => "https://worldidp.com/IMAGES/worldidp-international-driving-permit-logo.webp",
  "email" => "hello@worldidp.com",
  "telephone" => "+14064764656",
  "address" => {
    "@type" => "PostalAddress",
    "streetAddress" => "127 N HIGGINS AVE STE 307D #2849",
    "addressLocality" => "Missoula",
    "addressRegion" => "MT",
    "postalCode" => "59802",
    "addressCountry" => "US"
  },
  "description" => "WorldIDP is a private multilingual driving-document translation service for international travelers. It is not a government authority and does not replace a valid original driver's license."
}.freeze

SITE_FACTS = {
  "digitalDeliveryEstimateMinutes" => 5,
  "digitalDeliveryCondition" => "after successful review and approval",
  "digitalDeliveryWording" => "After successful review and approval, the digital document is usually delivered by email in approximately 5 minutes.",
  "printedDeliveryText" => "Printed document timing depends on destination, shipping method, and courier availability shown during the application flow.",
  "countryDatasetCount" => 124,
  "pilotCountryCount" => 10,
  "lastUpdated" => TODAY
}.freeze

AUTHOR = {
  "id" => "worldidp-editorial-team",
  "name" => "WorldIDP Editorial Team",
  "type" => "Organization",
  "role" => "Editorial team",
  "url" => "https://worldidp.com/editorial-policy.html",
  "schema" => ORG
}.freeze

COUNTRY_SOURCES = {
  "italy" => [
    ["ACI - Codice della Strada, Art. 142", "https://www.aci.it/fileadmin/cds/art-142.php", "government", %w[speed-limits]],
    ["Italian Ministry of Infrastructure and Transport", "https://www.mit.gov.it/", "government", %w[conventions]],
    ["Italy official tourism road guidance", "https://www.italia.it/en/italy/things-to-do/driving-in-italy", "official-tourism", %w[driving-side documents-to-carry]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention]]
  ],
  "spain" => [
    ["DGT - Normas basicas de circulacion", "https://www.dgt.es/muevete-con-seguridad/viaja-seguro/consejos-extranjeros/normas-basicas-de-circulacion/index.html", "government", %w[speed-limits driving-side]],
    ["DGT - Velocidad", "https://www.dgt.es/comunicacion/notas-de-prensa/la-velocidad-sigue-siendo-uno-de-los-principales-factores-concurrentes-de-los-accidentes-de-trafico", "government", %w[speed-limits penalties]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention rental-considerations]]
  ],
  "france" => [
    ["Service-Public.fr - Vitesse au volant", "https://www.service-public.gouv.fr/particuliers/vosdroits/F19460", "government", %w[speed-limits]],
    ["Legifrance - Code de la route, vitesse", "https://www.legifrance.gouv.fr/codes/id/LEGISCTA000006159600/", "government", %w[speed-limits penalties]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention rental-considerations]]
  ],
  "germany" => [
    ["Germany StVO section 3 - Speed", "https://www.gesetze-im-internet.de/stvo_2013/__3.html", "government", %w[speed-limits]],
    ["Germany BKatV speed penalty schedule", "https://www.gesetze-im-internet.de/bkatv_2013/anhang.html", "government", %w[penalties]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention rental-considerations]]
  ],
  "united-states" => [
    ["USAGov - International driver's license for U.S. citizens", "https://www.usa.gov/international-drivers-license", "government", %w[aaa-aata documents-to-carry idp-definition]],
    ["U.S. Department of State - Driving and road safety abroad", "https://travel.state.gov/content/travel/en/international-travel/before-you-go/driving-and-road-safety.html", "government", %w[state-variation safety]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention rental-considerations]]
  ],
  "thailand" => [
    ["Thailand.go.th - temporary driver's license for foreign tourists", "https://www.thailand.go.th/issue-focus-detail/001_01_226?hl=en", "government", %w[idp-requirement documents-to-carry]],
    ["Thailand.go.th - tourist driving permission", "https://www.thailand.go.th/visit-thailand-detail/001_01_227", "government", %w[vehicle-permission]],
    ["UK Government IDP country checker", "https://www.gov.uk/driving-abroad/international-driving-permit", "government", %w[idp-convention]]
  ],
  "japan" => [
    ["Tokyo Metropolitan Police - International Driving Permit in Japan", "https://www.keishicho.metro.tokyo.lg.jp/multilingual/english/finding_services/faq/drivers_license/drivers_license01.html", "government", %w[idp-requirement convention]],
    ["Japan National Police Agency - foreign driver's licence holders", "https://www.npa.go.jp/policies/application/license_renewal/have_DL_issed_another_country.html/the_road_traffic_law.html", "government", %w[documents-to-carry translation-exceptions]],
    ["Japan National Police Agency Traffic Bureau", "https://www.npa.go.jp/english/bureau/traffic/index.html", "government", %w[foreign-driver-guidance]]
  ],
  "united-arab-emirates" => [
    ["UAE Government - Driving abroad", "https://u.ae/en/information-and-services/passports-and-traveling/driving-abroad", "government", %w[idp-definition issuer-context]],
    ["UAE Federal Decree-Law on Traffic Regulation", "https://uaelegislation.gov.ae/en/legislations/2598", "government", %w[foreign-licence-conditions penalties]],
    ["UAE Executive Regulation of Federal Traffic Law", "https://uaelegislation.gov.ae/en/legislations/1020", "government", %w[visitor-driving international-licence]]
  ],
  "mexico" => [
    ["Mexico SRE - Conducir en el extranjero", "https://www.gob.mx/sre/documentos/conducir-en-el-extranjero", "government", %w[idp-methodology official-check-warning]],
    ["Mexico SICT - federal-road speed guidance", "https://www.gob.mx/sict/prensa/sict-recomienda-respetar-los-limites-de-velocidad-al-manejar-por-carretera-durante-vacaciones", "government", %w[speed-limits road-safety]],
    ["UK Government Mexico travel advice - road travel", "https://www.gov.uk/foreign-travel-advice/mexico/safety-and-security", "government", %w[foreign-licence driving-restrictions]]
  ],
  "australia" => [
    ["Austroads - Overseas drivers", "https://austroads.gov.au/drivers-and-vehicles/overseas-drivers", "official-road-authority", %w[visitor-driving state-variation]],
    ["NSW Government - driving with an overseas licence", "https://www.nsw.gov.au/driving-boating-and-transport/driver-and-rider-licences/visiting-or-moving-to-nsw/visiting-from-overseas-or-interstate", "government", %w[documents-to-carry translation-idp]],
    ["Service NSW - International Driving Permit", "https://www.service.nsw.gov.au/transaction/apply-for-an-international-driving-permit-idp", "government", %w[australian-idp documents]]
  ]
}.freeze

PILOT_FACTS = {
  "italy" => ["required-or-official-translation", "Drivers whose licence is not issued in the EU/EEA or not accompanied by a suitable official translation should check Italian requirements before driving.", "EU/EEA licence holders are generally treated differently from non-EU/EEA visitors.", "right", 50, 90, 130, %w[1949-geneva 1968-vienna], %w[spain france germany], "Italy has city traffic-restriction zones and destination-specific rental requirements. Confirm local city and provider rules before driving."],
  "spain" => ["required-or-recommended", "Drivers whose licence is outside Spain's recognised licence framework or not easy for authorities to read should confirm whether an IDP or official translation is needed.", "Many EU/EEA licence holders can drive under EU recognition rules.", "right", 50, 90, 120, %w[1949-geneva 1968-vienna], %w[italy france mexico], "Spain uses different speed rules for urban roads, conventional roads, and motorways. Rental companies may still ask for an IDP even when local law does not."],
  "france" => ["recommended-for-non-french-or-non-eu-licences", "Drivers with licences that are not in French or are not covered by recognition arrangements should carry a translation or IDP.", "EU/EEA licence holders are generally treated separately from other visitors.", "right", 50, 80, 130, %w[1949-geneva 1968-vienna], %w[spain italy germany], "France lowers many limits in rain or poor visibility. Carry the original licence and confirm rental-provider document requirements before pickup."],
  "germany" => ["recommended-for-non-eu-or-non-german-licences", "Visitors whose licence is outside the EU/EEA recognition framework or not written in a readable format should check German translation or IDP requirements.", "EU/EEA licence holders are generally recognised under EU rules.", "right", 50, 100, nil, %w[1949-geneva 1968-vienna], %w[france italy spain], "Germany has a 130 km/h advisory speed on motorways rather than one universal motorway limit. Posted limits and weather conditions still control."],
  "united-states" => ["state-and-provider-dependent", "Visitors should check the state where they will drive and the rental provider, especially if the licence is not in English.", "Requirements vary by state, licence language, and rental provider.", "right", nil, nil, nil, %w[1949-geneva], %w[mexico australia germany], "The United States is not a single licensing rulebook for visitors. State authorities and rental providers can apply different requirements."],
  "thailand" => ["required", "Foreign tourists can use an IDP under the 1949 Geneva Convention, or an ASEAN licence where that applies.", "Some ASEAN licence holders may be accepted under regional arrangements.", "left", nil, nil, nil, %w[1949-geneva], %w[japan australia united-arab-emirates], "Thailand specifically identifies the 1949 Geneva Convention IDP for foreign tourists. If your licence cannot be used, a temporary Thai licence may be required."],
  "japan" => ["required-1949-geneva-only", "Japan recognises only IDPs issued under the 1949 Geneva Convention, with separate translation rules for a limited set of foreign licences.", "Some licence holders from designated jurisdictions may drive with an authorised Japanese translation instead of an IDP.", "left", nil, nil, nil, %w[1949-geneva], %w[thailand australia united-states], "Do not rely on a 1968 Vienna Convention IDP for Japan. Police guidance says those permits are invalid for driving in Japan."],
  "united-arab-emirates" => ["required-or-exempted-licence", "Visitors may drive with a valid international driving licence or a foreign licence from an exempted/recognised country under UAE rules.", "Some foreign licences are recognised or exempted by UAE authorities.", "right", nil, nil, nil, %w[1949-geneva 1968-vienna], %w[thailand japan australia], "UAE legislation distinguishes visitors, transit, recognised licences, and valid international licences. Confirm recognition status before driving."],
  "mexico" => ["licence-and-origin-dependent", "Visitors should confirm requirements with the destination authority, embassy, consulate, and rental provider before driving.", "Some visitor licences, such as UK photocard licences under UK guidance, may be usable without an IDP.", "right", nil, nil, 110, %w[1926-paris], %w[united-states australia spain], "Mexico has local driving restrictions in some cities and separate insurance considerations. Confirm provider and jurisdiction rules before driving."],
  "australia" => ["translation-or-state-dependent", "Visitors with non-English licences should carry an English translation or IDP, and state time limits vary.", "Visitors with a current English-language overseas licence may be able to drive temporarily, depending on state or territory rules.", "left", nil, nil, nil, %w[1949-geneva], %w[japan thailand united-states], "Australian visitor-driving rules are state and territory based. NSW and Victoria apply time limits that differ from some other states."]
}.freeze

def slugify(name)
  name.downcase.gsub("&", "and").gsub(/[^a-z0-9]+/, "-").gsub(/^-|-$/, "")
end

def esc(value)
  value.to_s.gsub("&", "&amp;").gsub("<", "&lt;").gsub(">", "&gt;").gsub('"', "&quot;")
end

def write(path, content)
  full = File.join(ROOT, path)
  FileUtils.mkdir_p(File.dirname(full))
  File.write(full, content)
end

def legacy_countries
  html = File.read(File.join(ROOT, "countries.html"))
  json = html[/<script id="co-data" type="application\/json">(.*?)<\/script>/m, 1]
  abort "Unable to locate existing country JSON in countries.html" unless json
  JSON.parse(json)
end

def countries
  legacy_countries.map do |legacy|
    slug = slugify(legacy["name"])
    c = {
      "slug" => slug,
      "name" => legacy["name"],
      "iso2" => legacy["code"],
      "flag" => legacy["flag"],
      "region" => legacy["region"],
      "legacyStatus" => legacy["idp"],
      "legacyDrivingSide" => legacy["side"] == "L" ? "left" : "right",
      "idpStatus" => nil,
      "idpStatusApplies" => nil,
      "idpStatusExempt" => nil,
      "drivingSide" => nil,
      "speedUrbanKmh" => nil,
      "speedRuralKmh" => nil,
      "speedMotorwayKmh" => nil,
      "conventions" => [],
      "digitalDocumentStatus" => "unclear",
      "digitalDocumentNote" => "No confirmed official national policy was found. Carry the printed document and original licence when a physical document is requested.",
      "minimumRentalAge" => nil,
      "bacLimit" => nil,
      "documentsToCarry" => [],
      "officialSources" => [],
      "lastVerified" => nil,
      "relatedCountries" => [],
      "pilot" => PILOT_SLUGS.include?(slug),
      "indexable" => false,
      "researchStatus" => "DATA REQUIRED"
    }
    if (facts = PILOT_FACTS[slug])
      status, applies, exempt, side, urban, rural, motorway, conventions, related, guidance = facts
      c.merge!(
        "idpStatus" => status,
        "idpStatusApplies" => applies,
        "idpStatusExempt" => exempt,
        "drivingSide" => side,
        "speedUrbanKmh" => urban,
        "speedRuralKmh" => rural,
        "speedMotorwayKmh" => motorway,
        "conventions" => conventions,
        "documentsToCarry" => ["Original valid driving licence", "Passport or travel ID where requested", "IDP, official translation, or private translation-support document where applicable"],
        "relatedCountries" => related,
        "practicalGuidance" => guidance,
        "officialSources" => COUNTRY_SOURCES[slug].map { |name, url, type, supports| { "name" => name, "url" => url, "publisherType" => type, "supports" => supports } },
        "lastVerified" => TODAY,
        "indexable" => true,
        "researchStatus" => "pilot-verified"
      )
    end
    c
  end
end

def json_ld(data)
  JSON.pretty_generate(data).gsub("</", "<\\/")
end

def head(title, desc, canonical, schema = [])
  schema_html = schema.empty? ? "" : "\n    <script type=\"application/ld+json\">\n#{json_ld("@context" => "https://schema.org", "@graph" => schema).lines.map { |l| "    #{l}" }.join}    </script>"
  <<~HTML
    <!doctype html>
    <html lang="en" dir="ltr">
      <head>
        <meta charset="UTF-8" />
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        <title>#{esc(title)}</title>
        <meta name="description" content="#{esc(desc)}" />
        <meta name="author" content="WorldIDP Editorial Team" />
        <meta name="robots" content="#{ROBOTS_INDEX}" />
        <meta name="theme-color" content="#0758d8" />
        <link rel="canonical" href="#{canonical}" />
        <meta property="og:type" content="article" />
        <meta property="og:site_name" content="WorldIDP" />
        <meta property="og:title" content="#{esc(title)}" />
        <meta property="og:description" content="#{esc(desc)}" />
        <meta property="og:url" content="#{canonical}" />
        <meta property="og:image" content="https://worldidp.com/IMAGES/worldidp-international-driving-permit-social-preview.webp" />
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:title" content="#{esc(title)}" />
        <meta name="twitter:description" content="#{esc(desc)}" />
        <meta name="twitter:image" content="https://worldidp.com/IMAGES/worldidp-international-driving-permit-social-preview.webp" />
        <link rel="icon" href="/IMAGES/favicon.ico" sizes="any" />
        <link rel="stylesheet" href="/styles.css" />
        <link rel="stylesheet" href="/what-is-idp.css" />
        <link rel="stylesheet" href="/knowledge.css" />#{schema_html}
      </head>
  HTML
end

def header(active = nil)
  nav = {
    "Countries" => "/countries.html",
    "What is IDP?" => "/what-is-idp.html",
    "How to Apply" => "/how-to-apply.html",
    "Pricing" => "/pricing.html",
    "Contact Us" => "/contact-us.html",
    "My Order" => "/track-order.html"
  }.map { |label, href| %(<a href="#{href}"#{active == label ? ' aria-current="page"' : ""}>#{label}</a>) }.join("\n        ")
  <<~HTML
    <body class="wi-page knowledge-page">
      <a class="sr-only" href="#main">Skip to main content</a>
      <header class="site-header" data-header>
        <a class="brand" href="/index.html" aria-label="WorldIDP home"><img src="/IMAGES/worldidp-international-driving-permit-logo.webp" alt="WorldIDP - Drive the World" fetchpriority="high" width="250" height="90" decoding="async" /></a>
        <button class="nav-toggle" type="button" aria-label="Open menu" aria-expanded="false" data-nav-toggle><span></span><span></span><span></span></button>
        <nav class="primary-nav" aria-label="Main navigation" data-nav>
          #{nav}
        </nav>
        <div class="header-actions"><a class="btn btn-header" href="/pricing.html">Start Application</a><button class="language-pill" type="button" aria-label="Current language: English"><span class="flag-uk" aria-hidden="true"></span> EN</button></div>
      </header>
  HTML
end

def footer
  <<~HTML
      <footer class="site-footer" role="contentinfo">
        <div class="footer-inner">
          <div class="footer-top">
            <div class="footer-brand"><a class="footer-logo" href="/index.html" aria-label="WorldIDP home"><img src="/IMAGES/worldidp-logo-white.webp" alt="WorldIDP" width="250" height="90" decoding="async" /></a><p>WorldIDP provides private multilingual driving-document translation support for travelers who carry their original valid driver's license.</p></div>
            <nav class="footer-col" aria-label="Resources"><h3>Resources</h3><ul><li><a href="/countries.html">Countries</a></li><li><a href="/what-is-idp.html">What is IDP?</a></li><li><a href="/how-to-apply.html">How to apply</a></li><li><a href="/editorial-policy.html">Editorial policy</a></li></ul></nav>
            <nav class="footer-col" aria-label="Support"><h3>Support</h3><ul><li><a href="/pricing.html">Document options</a></li><li><a href="/track-order.html">Track my order</a></li><li><a href="/faq.html">FAQs</a></li><li><a href="/contact-us.html">Contact us</a></li></ul></nav>
            <nav class="footer-col" aria-label="Legal"><h3>Legal</h3><ul><li><a href="/privacy-policy.html">Privacy Policy</a></li><li><a href="/terms-of-service.html">Terms of Service</a></li><li><a href="/legal-disclaimer.html">Legal Disclaimer</a></li><li><a href="/refund-return-policy.html">Refunds</a></li></ul></nav>
          </div>
          <div class="footer-divider"></div>
          <p class="footer-disclaimer">WorldIDP is an independent private company and is not a government agency or convention issuing authority. Requirements vary by destination, licence origin, licence language, vehicle category and third-party provider.</p>
          <div class="footer-bottom"><p class="footer-copy">© 2026 WORLDIDP INTERNATIONAL LLC. All rights reserved.</p><ul class="footer-legal"><li><a href="/privacy-policy.html">Privacy</a></li><li><a href="/terms-of-service.html">Terms</a></li><li><a href="/cookie-policy.html">Cookies</a></li></ul></div>
        </div>
      </footer>
      <script src="/script.js" defer></script>
      <script src="/analytics-beacon.js?v=20260722" defer></script>
    </body>
    </html>
  HTML
end

def country_schema(c)
  url = "https://worldidp.com/countries/#{c["slug"]}/"
  [
    { "@type" => "BreadcrumbList", "itemListElement" => [{ "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" }, { "@type" => "ListItem", "position" => 2, "name" => "Countries", "item" => "https://worldidp.com/countries.html" }, { "@type" => "ListItem", "position" => 3, "name" => c["name"], "item" => url }] },
    { "@type" => "WebPage", "@id" => "#{url}#webpage", "url" => url, "name" => "Do You Need an International Driving Permit in #{c["name"]}?", "datePublished" => TODAY, "dateModified" => TODAY, "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" }, "publisher" => ORG, "about" => [{ "@type" => "Country", "name" => c["name"] }, { "@type" => "Thing", "name" => "International Driving Permit" }] },
    { "@type" => "FAQPage", "mainEntity" => [{ "@type" => "Question", "name" => "Do I need an International Driving Permit in #{c["name"]}?", "acceptedAnswer" => { "@type" => "Answer", "text" => c["idpStatusApplies"].to_s } }, { "@type" => "Question", "name" => "Can I use a digital document in #{c["name"]}?", "acceptedAnswer" => { "@type" => "Answer", "text" => c["digitalDocumentNote"].to_s } }] }
  ]
end

def country_page(c, all)
  facts = [
    ["Requirement/status", c["idpStatus"]],
    ["Applies to", c["idpStatusApplies"]],
    ["Possible exemption", c["idpStatusExempt"]],
    ["Driving side", c["drivingSide"]],
    ["Urban speed", c["speedUrbanKmh"] ? "#{c["speedUrbanKmh"]} km/h" : "DATA REQUIRED"],
    ["Rural speed", c["speedRuralKmh"] ? "#{c["speedRuralKmh"]} km/h" : "DATA REQUIRED"],
    ["Motorway speed", c["speedMotorwayKmh"] ? "#{c["speedMotorwayKmh"]} km/h" : "DATA REQUIRED or posted/local limit"],
    ["Convention context", c["conventions"].join(", ")]
  ]
  sources = c["officialSources"].map.with_index(1) { |s, i| %(<li id="source-#{i}"><a href="#{s["url"]}" rel="nofollow noopener">#{esc(s["name"])}</a><span>#{esc(s["supports"].join(", "))}</span></li>) }.join
  related = c["relatedCountries"].map { |slug| (r = all.find { |x| x["slug"] == slug }) && %(<a href="/countries/#{r["slug"]}/">#{esc(r["name"])}</a>) }.compact.join
  title = "Do You Need an International Driving Permit in #{c["name"]}? | WorldIDP"
  desc = "Evidence-based #{c["name"]} driving document guidance: IDP status, who it applies to, conventions, documents to carry, and official sources."
  <<~HTML
    #{head(title, desc, "https://worldidp.com/countries/#{c["slug"]}/", country_schema(c))}
    #{header("Countries")}
    <main id="main" class="knowledge-main">
      <nav class="wi-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span>/</span><a href="/countries.html">Countries</a><span>/</span><span>#{esc(c["name"])}</span></nav>
      <section class="wi-hero knowledge-hero"><div class="wi-hero-grid"><div><p class="wi-kicker">Last verified #{c["lastVerified"]} · sourced pilot page</p><h1>Do You Need an International Driving Permit in #{esc(c["name"])}?</h1><p class="wi-hero-sub">#{esc(c["idpStatusApplies"])}</p><div class="wi-hero-actions"><a class="wi-btn" href="/how-to-apply.html">How to apply</a><a class="wi-btn wi-btn-ghost" href="/countries.html">Back to country hub</a></div></div><div class="wi-answer"><h2>Direct Answer</h2><p>For #{esc(c["name"])}, the safest evidence-based answer is: <strong>#{esc(c["idpStatus"])}</strong>. Always carry your original valid driver's licence. A WorldIDP document is private translation support and does not replace the original licence or grant driving rights.</p></div></div></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Requirement summary</p><h2>What the rule means for visitors</h2></div><div class="knowledge-table-wrap"><table class="knowledge-table"><tbody>#{facts.map { |k, v| "<tr><th>#{esc(k)}</th><td>#{esc(v || "DATA REQUIRED")}</td></tr>" }.join}</tbody></table></div></section>
      <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">Documents</p><h2>What to carry while driving</h2></div><ul class="knowledge-list">#{c["documentsToCarry"].map { |d| "<li>#{esc(d)}</li>" }.join}</ul><p class="knowledge-note"><strong>Digital-document status:</strong> #{esc(c["digitalDocumentStatus"])}. #{esc(c["digitalDocumentNote"])}</p></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Rental and practical guidance</p><h2>Provider rules can still vary</h2></div><p>#{esc(c["practicalGuidance"])}</p><p>Rental-company rules, insurance checks, and police interpretation can vary. Confirm the requirement directly with the destination authority and the provider before driving.</p></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">FAQ</p><h2>#{esc(c["name"])} IDP questions</h2></div><div class="wi-faq"><article><h3>Do I still need my original licence?</h3><div class="wi-faq-body">Yes. The original valid driving licence must be carried. A translation-support document does not replace it.</div></article><article><h3>Can I rely on a digital copy only?</h3><div class="wi-faq-body">No official national policy confirming digital-only acceptance was found. Carry the printed document and original licence when a physical document is requested.</div></article></div></section>
      <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">Sources</p><h2>Official evidence used</h2></div><ol class="knowledge-sources">#{sources}</ol><p class="knowledge-note">Last verified: #{c["lastVerified"]}. Missing or unverified values are marked as DATA REQUIRED rather than estimated.</p></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Related</p><h2>Continue researching</h2></div><div class="knowledge-link-row">#{related}<a href="/convention/1949-geneva/">1949 Geneva Convention</a><a href="/convention/1968-vienna/">1968 Vienna Convention</a><a href="/what-is-idp.html">What is IDP?</a></div></section>
      <section class="wi-cta"><h2>Need a private multilingual translation-support document?</h2><p>After successful review and approval, the digital document is usually delivered by email in approximately 5 minutes.</p><a class="wi-btn" href="/pricing.html">View document options</a></section>
    </main>
    #{footer}
  HTML
end

def hub_page(cs)
  cards = cs.map do |c|
    status = c["indexable"] ? c["idpStatus"] : "DATA REQUIRED"
    inner = %(<span>#{c["flag"]}</span><h3>#{esc(c["name"])}</h3><p>#{esc(c["region"])}</p><b>#{esc(status)}</b>)
    if c["indexable"]
      %(<a class="knowledge-country-card" href="/countries/#{c["slug"]}/" data-region="#{esc(c["region"])}" data-status="#{esc(status)}" data-name="#{esc(c["name"].downcase)}">#{inner}</a>)
    else
      %(<article class="knowledge-country-card is-pending" data-region="#{esc(c["region"])}" data-status="data-required" data-name="#{esc(c["name"].downcase)}">#{inner}<small>Research pending</small></article>)
    end
  end.join("\n")
  pilot = cs.select { |c| c["pilot"] }
  schema = [
    { "@type" => "BreadcrumbList", "itemListElement" => [{ "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" }, { "@type" => "ListItem", "position" => 2, "name" => "Countries", "item" => "https://worldidp.com/countries.html" }] },
    { "@type" => "CollectionPage", "name" => "International Driving Permit Country Requirements", "url" => "https://worldidp.com/countries.html", "dateModified" => TODAY, "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" }, "publisher" => ORG },
    { "@type" => "Dataset", "name" => "WorldIDP IDP Country Requirements Dataset", "description" => "A maintained country requirement dataset with unsupported fields marked null or DATA REQUIRED.", "url" => "https://worldidp.com/data/idp-country-requirements.json", "dateModified" => TODAY, "creator" => ORG, "distribution" => [{ "@type" => "DataDownload", "encodingFormat" => "application/json", "contentUrl" => "https://worldidp.com/data/idp-country-requirements.json" }, { "@type" => "DataDownload", "encodingFormat" => "text/csv", "contentUrl" => "https://worldidp.com/data/idp-country-requirements.csv" }] },
    { "@type" => "ItemList", "name" => "Verified pilot country pages", "itemListElement" => pilot.map.with_index(1) { |c, i| { "@type" => "ListItem", "position" => i, "name" => c["name"], "url" => "https://worldidp.com/countries/#{c["slug"]}/" } } }
  ]
  <<~HTML
    #{head("International Driving Permit Country Requirements | WorldIDP", "Search WorldIDP's maintained country registry for sourced IDP guidance, pilot country pages, open dataset downloads, and official-source methodology.", "https://worldidp.com/countries.html", schema)}
    #{header("Countries")}
    <main id="main" class="knowledge-main">
      <nav class="wi-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span>/</span><span>Countries</span></nav>
      <section class="wi-hero knowledge-hero"><div class="wi-hero-grid"><div><p class="wi-kicker">Country registry · #{cs.length} records · #{pilot.length} verified pilots</p><h1>International Driving Permit Country Requirements</h1><p class="wi-hero-sub">Search the maintained WorldIDP country registry. Verified pilot countries link to sourced country pages; research-pending countries are no longer routed to checkout.</p><div class="wi-hero-actions"><a class="wi-btn" href="/data/idp-country-requirements.json">Open JSON dataset</a><a class="wi-btn wi-btn-ghost" href="/data/idp-country-requirements.csv">Download CSV</a></div></div><div class="wi-answer"><h2>Direct Answer</h2><p>Country names now point to verified country guidance when available. Where official evidence is still missing, the registry marks the country as DATA REQUIRED instead of guessing.</p></div></div></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Methodology</p><h2>What the data means</h2></div><div class="knowledge-grid"><article><h3>Evidence first</h3><p>Legal and driving facts require official or reliable sources. Unsupported values are null or DATA REQUIRED.</p></article><article><h3>Private service</h3><p>WorldIDP provides private translation support and is not a government or convention issuing authority.</p></article><article><h3>Freshness</h3><p>Verified pilot records show a visible last-verified date. The public dataset was last updated #{TODAY}.</p></article></div></section>
      <section class="wi-section wi-section-tint"><div class="knowledge-filterbar"><input id="countryFilter" type="search" placeholder="Search countries" aria-label="Search countries" /><select id="regionFilter" aria-label="Filter by region"><option value="">All regions</option><option>Europe</option><option>Asia</option><option>Middle East</option><option>Americas</option><option>Africa</option><option>Oceania</option></select></div><div class="knowledge-country-grid" id="countryGrid">#{cards}</div></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Open dataset</p><h2>Use the maintained country data</h2></div><p>The dataset includes country name, ISO code, region, source coverage, indexability, pilot status, and official-source-backed fields. No licence is applied because the owner has not approved a public data licence.</p><div class="knowledge-link-row"><a href="/data/idp-country-requirements.json">JSON distribution</a><a href="/data/idp-country-requirements.csv">CSV distribution</a><a href="/editorial-policy.html">Source methodology</a></div></section>
    </main>
    <script>(function(){var q=document.getElementById('countryFilter');var r=document.getElementById('regionFilter');var cards=Array.prototype.slice.call(document.querySelectorAll('.knowledge-country-card'));function apply(){var term=(q.value||'').toLowerCase().trim();var region=r.value;cards.forEach(function(card){var okQ=!term||(card.dataset.name||'').indexOf(term)!==-1;var okR=!region||card.dataset.region===region;card.style.display=okQ&&okR?'':'none';});}q.addEventListener('input',apply);r.addEventListener('change',apply);})();</script>
    #{footer}
  HTML
end

def convention_page(slug, title, desc, points, related)
  url = "https://worldidp.com/convention/#{slug}/"
  schema = [{ "@type" => "BreadcrumbList", "itemListElement" => [{ "@type" => "ListItem", "position" => 1, "name" => "Home", "item" => "https://worldidp.com/" }, { "@type" => "ListItem", "position" => 2, "name" => title, "item" => url }] }, { "@type" => "WebPage", "name" => title, "url" => url, "dateModified" => TODAY, "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" }, "publisher" => ORG, "about" => { "@type" => "Thing", "name" => title } }]
  <<~HTML
    #{head("#{title} | WorldIDP", desc, url, schema)}
    #{header("Countries")}
    <main id="main" class="knowledge-main">
      <nav class="wi-breadcrumb" aria-label="Breadcrumb"><a href="/index.html">Home</a><span>/</span><span>#{esc(title)}</span></nav>
      <section class="wi-hero knowledge-hero"><div class="wi-hero-grid"><div><p class="wi-kicker">Convention entity · Last verified #{TODAY}</p><h1>#{esc(title)}</h1><p class="wi-hero-sub">#{esc(desc)}</p></div><div class="wi-answer"><h2>Direct Answer</h2><p>The convention framework helps define international driving-permit formats, but it does not make WorldIDP a government issuing authority and it does not override national implementation rules.</p></div></div></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Explainer</p><h2>What it governs</h2></div><ul class="knowledge-list">#{points.map { |p| "<li>#{esc(p)}</li>" }.join}</ul></section>
      <section class="wi-section wi-section-tint"><div class="wi-head"><p class="wi-kicker">Sources</p><h2>Primary treaty sources</h2></div><ol class="knowledge-sources"><li><a href="https://treaties.un.org/" rel="nofollow noopener">United Nations Treaty Collection</a><span>Treaty status and parties</span></li><li><a href="https://unece.org/transport/road-traffic-and-road-signs-and-signals-agreements-and-conventions" rel="nofollow noopener">UNECE road traffic conventions</a><span>Convention texts and transport context</span></li></ol></section>
      <section class="wi-section"><div class="wi-head"><p class="wi-kicker">Related countries</p><h2>Verified pilot examples</h2></div><div class="knowledge-link-row">#{related.map { |s| "<a href=\"/countries/#{s}/\">#{esc(s.split("-").map(&:capitalize).join(" "))}</a>" }.join}<a href="/countries.html">Country hub</a></div></section>
    </main>
    #{footer}
  HTML
end

cs = countries
write("data/site-facts.json", JSON.pretty_generate(SITE_FACTS) + "\n")
write("data/organization.json", JSON.pretty_generate(ORG) + "\n")
write("data/authors.json", JSON.pretty_generate([AUTHOR]) + "\n")
write("data/countries.json", JSON.pretty_generate(cs) + "\n")
write("data/idp-country-requirements.json", JSON.pretty_generate({ "version" => TODAY, "lastUpdated" => TODAY, "licence" => nil, "limitations" => "Unsupported fields are null or DATA REQUIRED. Country rules can change and should be confirmed with official authorities.", "countries" => cs }) + "\n")
write("data/idp-country-requirements.csv", CSV.generate { |out| out << %w[slug name iso2 region pilot indexable idpStatus drivingSide speedUrbanKmh speedRuralKmh speedMotorwayKmh sourceCount lastVerified researchStatus]; cs.each { |c| out << [c["slug"], c["name"], c["iso2"], c["region"], c["pilot"], c["indexable"], c["idpStatus"], c["drivingSide"], c["speedUrbanKmh"], c["speedRuralKmh"], c["speedMotorwayKmh"], c["officialSources"].length, c["lastVerified"], c["researchStatus"]] } })
write("templates/country-page-template.html", "<!-- Country pages are generated by tools/generate-country-pages/generate.rb from data/countries.json. -->\n")
cs.select { |c| c["pilot"] }.each { |c| write("countries/#{c["slug"]}/index.html", country_page(c, cs)) }
write("countries.html", hub_page(cs))
write("convention/1949-geneva/index.html", convention_page("1949-geneva", "1949 Geneva Convention on Road Traffic", "Entity page explaining the 1949 Geneva road-traffic convention and how it relates to international driving documents.", ["Sets a framework for international road traffic and permit formats.", "Japan and Thailand specifically reference 1949 Geneva Convention IDPs in official visitor guidance.", "National implementation still controls what a visitor must carry.", "WorldIDP is not an issuing authority under the convention."], %w[japan thailand united-states australia]))
write("convention/1968-vienna/index.html", convention_page("1968-vienna", "1968 Vienna Convention on Road Traffic", "Entity page explaining the 1968 Vienna road-traffic convention and why national IDP implementation can still vary.", ["Updates the road-traffic framework for many participating countries.", "Some destinations reference 1968 Vienna convention IDPs or licences.", "A 1968 framework does not guarantee digital-only acceptance.", "WorldIDP is a private translation-support service, not a treaty authority."], %w[spain france germany united-arab-emirates]))
editorial_schema = [{ "@type" => "WebPage", "name" => "WorldIDP Editorial Policy", "url" => "https://worldidp.com/editorial-policy.html", "datePublished" => TODAY, "dateModified" => TODAY, "author" => { "@type" => "Organization", "name" => "WorldIDP Editorial Team" }, "publisher" => ORG }]
write("editorial-policy.html", "#{head("Editorial Policy and Source Methodology | WorldIDP", "How WorldIDP verifies country driving-document information, handles missing data, and separates private service information from legal requirements.", "https://worldidp.com/editorial-policy.html", editorial_schema)}#{header}<main id=\"main\" class=\"knowledge-main\"><nav class=\"wi-breadcrumb\" aria-label=\"Breadcrumb\"><a href=\"/index.html\">Home</a><span>/</span><span>Editorial Policy</span></nav><section class=\"wi-hero knowledge-hero\"><div class=\"wi-hero-grid\"><div><p class=\"wi-kicker\">Editorial framework · Last updated #{TODAY}</p><h1>Editorial Policy and Source Methodology</h1><p class=\"wi-hero-sub\">WorldIDP uses an evidence-first editorial model for country driving-document guidance. Missing or unverified values are marked as DATA REQUIRED rather than estimated.</p></div><div class=\"wi-answer\"><h2>Author and reviewer</h2><p>Byline: WorldIDP Editorial Team. No named legal expert or government reviewer is claimed because no such identity was supplied in the project.</p></div></div></section><section class=\"wi-section\"><div class=\"wi-head\"><p class=\"wi-kicker\">Source priority</p><h2>How country facts are verified</h2></div><ol class=\"knowledge-list\"><li>National government, transport ministry, police or road authority.</li><li>Embassy, consular, UN treaty or official tourism sources.</li><li>Official rental-company policy only for rental-specific claims.</li><li>Reputable secondary sources only when primary sources are unavailable, and never as the sole source for a legal claim.</li></ol></section><section class=\"wi-section wi-section-tint\"><div class=\"wi-head\"><p class=\"wi-kicker\">Limitations</p><h2>What WorldIDP does not claim</h2></div><p>WorldIDP does not claim to be a government agency, treaty issuing authority, or universal acceptance guarantee. Destination rules and third-party requirements can change.</p></section></main>#{footer}")

public_pages = Dir[File.join(ROOT, "*.html")].map { |f| File.basename(f) }.reject { |f| %w[checkout.html payment.html upload-photos.html thank-you.html track-order.html].include?(f) }.sort
urls = public_pages.map { |f| f == "index.html" ? "https://worldidp.com/" : "https://worldidp.com/#{f}" }
urls += cs.select { |c| c["indexable"] }.map { |c| "https://worldidp.com/countries/#{c["slug"]}/" }
urls += ["https://worldidp.com/convention/1949-geneva/", "https://worldidp.com/convention/1968-vienna/"]
doc = REXML::Document.new
doc << REXML::XMLDecl.new("1.0", "UTF-8")
urlset = doc.add_element("urlset", { "xmlns" => "http://www.sitemaps.org/schemas/sitemap/0.9" })
urls.uniq.sort.each do |url|
  u = urlset.add_element("url")
  u.add_element("loc").text = url
  u.add_element("lastmod").text = TODAY
  u.add_element("changefreq").text = url.include?("/countries/") ? "monthly" : "weekly"
  u.add_element("priority").text = url == "https://worldidp.com/" ? "1.0" : "0.7"
end
sitemap = +""
doc.write(sitemap, 2)
write("sitemap.xml", sitemap + "\n")

write("_audit/63-country-data-model.md", "# Phase 7 Country Data Model\n\nGenerated #{TODAY}.\n\n- Countries in `data/countries.json`: #{cs.length}\n- Pilot countries: #{cs.count { |c| c["pilot"] }}\n- Records with official sources: #{cs.count { |c| c["officialSources"].any? }}\n- Records containing null/unconfirmed values: #{cs.count { |c| c.values.any?(&:nil?) }}\n- Indexable pilot country pages: #{cs.count { |c| c["indexable"] }}\n\nUnsupported legal and driving facts remain null or DATA REQUIRED.\n")
write("_audit/64-country-generator.md", "# Phase 7 Country Generator\n\nGenerated #{TODAY}.\n\n- Generator: `tools/generate-country-pages/generate.rb`\n- Template marker: `templates/country-page-template.html`\n- Output path: `countries/{slug}/index.html`\n- Generated pilot pages only: #{PILOT_SLUGS.join(", ")}\n- Non-pilot country records are retained in the dataset but not generated as indexable pages.\n")
write("_audit/66-open-dataset-implementation.md", "# Phase 7 Open Dataset Implementation\n\nGenerated #{TODAY}.\n\nPublished files:\n\n- `/data/idp-country-requirements.json`\n- `/data/idp-country-requirements.csv`\n\nDataset schema is present on `countries.html`. No licence was applied because no owner-approved licence was supplied.\n")
