#!/usr/bin/env ruby
# frozen_string_literal: true

ROOT = File.expand_path("../..", __dir__)
INDEX_ROBOTS = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
FUNNEL = %w[checkout.html payment.html upload-photos.html thank-you.html track-order.html].freeze
PILOT_SLUGS = %w[
  italy spain france germany united-states thailand japan
  united-arab-emirates mexico australia
].freeze

def write_if_changed(path, content)
  before = File.read(path)
  return false if before == content

  File.write(path, content)
  true
end

Dir.chdir(ROOT) do
  Dir["*.html"].sort.each do |file|
    html = File.read(file)
    robots = FUNNEL.include?(file) ? "noindex, follow" : INDEX_ROBOTS
    html.sub!(/<meta name="robots" content="[^"]*"\s*\/?>/, %(<meta name="robots" content="#{robots}" />))

    html.gsub!(/\n\s*<div class="footer-social">\s*.*?\s*<\/div>/m, "")
    html.gsub!("Digital IDP ready in ~8 minutes", "Priority review after approval")
    html.gsub!("Digital IDP in as little as 8 minutes", "Digital delivery after review and approval")
    html.gsub!(
      "Instant digital International Driving Permit delivered to your inbox in about 5 minutes.",
      "After successful review and approval, the digital document is usually delivered by email in approximately 5 minutes."
    )
    html.gsub!(
      "<b>Instant digital PDF</b> — download or email it the moment it's approved.",
      "<b>Digital document after approval</b> — download or email it after successful review and approval."
    )
    html.gsub!("data-count=\"195\"", "data-count=\"124\"")
    html.gsub!("countries covered", "countries in the research dataset")
    html.gsub!("Search 124+ countries", "Search 124 countries")
    html.gsub!("124+ countries", "124 countries")

    html.gsub!(/<div class="trust-badge".*?<\/div><\/div>/m, '<p class="reviews-note">Customer testimonials are displayed without third-party review verification until official review links or a verified widget are supplied.</p>')
    html.gsub!(/<a class="review-card" href="#" rel="noopener" aria-label="[^"]*">/, '<article class="review-card" aria-label="Customer testimonial">')
    40.times do
      break unless html.gsub!(%r{(<article class="review-card" aria-label="Customer testimonial">(?:(?!<article class="review-card").)*?)</a>}m, "\\1</article>")
    end
    html.gsub!(/Verified Trustpilot review/i, "Customer testimonial")
    html.gsub!(/Read [^"]+ review on Trustpilot/i, "Customer testimonial")
    html.gsub!(/See our reviews on Trustpilot/i, "Customer testimonials")

    html.gsub!(/<div class="rental-logo-list"[^>]*>.*?<\/div>/m, '<p class="rental-logo-note">Some rental desks or local authorities may request licence translation support. Confirm requirements directly with the provider and destination authority before travel.</p>')

    html.gsub!(/<a class="country-card" href="checkout\.html"([^>]*data-slug="([^"]+)"[^>]*)>/) do
      attrs = Regexp.last_match(1)
      slug = Regexp.last_match(2)
      href = PILOT_SLUGS.include?(slug) ? "countries/#{slug}/" : "countries.html"
      %(<a class="country-card" href="#{href}"#{attrs}>)
    end

    write_if_changed(file, html)
  end

  generated_paths = Dir[
    "data/organization.json",
    "countries.html",
    "countries/*/index.html",
    "convention/*/index.html",
    "editorial-policy.html"
  ]
  generated_paths.each do |path|
    next unless File.file?(path)

    html = File.read(path)
    html.gsub!(/\n\s*"telephone": "\+1-415-555-0198",?/, "")
    html.gsub!(/,\n\s*"telephone": "\+1-415-555-0198"/, "")
    write_if_changed(path, html)
  end

  gen = File.read("tools/generate-country-pages/generate.rb")
  gen.gsub!(/\n\s*"telephone" => "\+1-415-555-0198",/, "")
  write_if_changed("tools/generate-country-pages/generate.rb", gen)

  script_path = "script.js"
  script = File.read(script_path)
  replacement = <<~JS.chomp
    const PILOT_COUNTRY_SLUGS = new Set([
      "italy", "spain", "france", "germany", "united-states", "thailand", "japan",
      "united-arab-emirates", "mexico", "australia"
    ]);

    const toCountryKnowledgeHref = (slug) =>
      PILOT_COUNTRY_SLUGS.has(slug) ? `countries/${slug}/` : "countries.html";

    document.querySelectorAll(".country-card").forEach((card) => {
      const slug = card.dataset.slug;
      if (!slug) return;
      card.setAttribute("href", toCountryKnowledgeHref(slug));
    });

    document.querySelectorAll('a > .co-fl').forEach((flag) => {
      const link = flag.closest("a");
      const slug = link?.dataset?.slug;
      if (!link || !slug) return;
      link.setAttribute("href", toCountryKnowledgeHref(slug));
    });
  JS
  script.sub!(
    /document\.querySelectorAll\("\.country-card"\).*?document\.querySelectorAll\('a\[href="#apply"\]/m,
    "#{replacement}\n\n  document.querySelectorAll('a[href=\"#apply\"]"
  )
  write_if_changed(script_path, script)
end
