#!/usr/bin/env ruby
# frozen_string_literal: true

require "json"
require "rexml/document"

ROOT = File.expand_path("../..", __dir__)
ROBOTS_INDEX = "index, follow, max-snippet:-1, max-image-preview:large, max-video-preview:-1"
FUNNEL = %w[checkout.html payment.html upload-photos.html thank-you.html track-order.html].freeze
RENTAL_LOGOS = %w[hertz enterprise alamo thrifty localiza interrent].freeze

errors = []
warnings = []

def read(path)
  File.read(File.join(ROOT, path))
end

def html_files
  Dir[File.join(ROOT, "**/*.html")]
    .reject { |f| f.include?("/_audit/") || f.include?("/admin/") || f.include?("/templates/") }
    .sort
end

def rel(path)
  path.sub("#{ROOT}/", "")
end

begin
  facts = JSON.parse(read("data/site-facts.json"))
  countries = JSON.parse(read("data/countries.json"))
  dataset = JSON.parse(read("data/idp-country-requirements.json"))
  org = JSON.parse(read("data/organization.json"))
rescue => e
  abort "CRITICAL: missing or invalid data layer: #{e.message}"
end

html_files.each do |file|
  path = rel(file)
  html = File.read(file)
  robots = html.scan(/<meta\s+name=["']robots["'][^>]*content=["']([^"']+)["'][^>]*>/i).flatten
  errors << "#{path}: missing robots meta" if robots.empty?
  errors << "#{path}: duplicate robots meta" if robots.length > 1
  if robots.any?
    if FUNNEL.include?(File.basename(path))
      errors << "#{path}: funnel page must remain noindex" unless robots.first.downcase.include?("noindex")
    else
      errors << "#{path}: robots directive mismatch: #{robots.first}" unless robots.first == ROBOTS_INDEX
    end
  end
  canons = html.scan(/<link\s+rel=["']canonical["'][^>]*>/i)
  errors << "#{path}: missing canonical" if canons.empty? && !FUNNEL.include?(File.basename(path))
  errors << "#{path}: duplicate canonical" if canons.length > 1
  errors << "#{path}: href=\"#\" placeholder found" if html.include?('href="#"')
  errors << "#{path}: unsupported Verified Trustpilot claim" if html =~ /Verified\s+Trustpilot/i
  RENTAL_LOGOS.each do |brand|
    errors << "#{path}: rental-logo/brand reference remains: #{brand}" if html.downcase.include?("#{brand}-car-rental-logo") || html.downcase.include?("#{brand} car rental logo")
  end
  html.scan(%r{<script[^>]+type=["']application/ld\+json["'][^>]*>(.*?)</script>}mi).each do |json|
    begin
      JSON.parse(json.first.strip)
    rescue => e
      errors << "#{path}: invalid JSON-LD: #{e.message}"
    end
  end
  ids = Hash.new(0)
  html.scan(/\sid=["']([^"']+)["']/) { |m| ids[m[0]] += 1 }
  ids.select { |_id, count| count > 1 }.each_key { |id| errors << "#{path}: duplicate id #{id}" }
end

visible = html_files.map { |f| File.read(f) }.join("\n")
errors << "delivery contradiction: 8-minute claim remains" if visible =~ /8\s*(minutes|min)/i
errors << "delivery contradiction: instant delivery promise remains" if visible =~ /Instant PDF|delivered instantly|right after checkout/i
errors << "unsupported country count: 195 remains" if visible =~ /\b195\+?\b/
errors << "unsupported country count: 124+ remains" if visible.include?("124+")
errors << "organization name missing" unless org["name"] == "WORLDIDP INTERNATIONAL LLC"
errors << "sameAs must be absent until real profiles are supplied" if org.key?("sameAs")
errors << "country dataset count mismatch" unless countries.length == facts["countryDatasetCount"]
errors << "public dataset mismatch" unless dataset["countries"].length == countries.length

countries.each do |country|
  if country["pilot"]
    errors << "#{country["slug"]}: pilot missing lastVerified" if country["lastVerified"].to_s.empty?
    errors << "#{country["slug"]}: pilot missing official sources" if country["officialSources"].empty?
    errors << "#{country["slug"]}: pilot page missing" unless File.exist?(File.join(ROOT, "countries", country["slug"], "index.html"))
  elsif country["officialSources"].empty?
    warnings << "#{country["slug"]}: DATA REQUIRED"
  end
end

begin
  REXML::Document.new(read("sitemap.xml"))
rescue => e
  errors << "sitemap.xml invalid: #{e.message}"
end

missing = []
html_files.each do |file|
  path = rel(file)
  html = File.read(file)
  html.scan(/(?:href|src)=["']([^"']+)["']/i) do |m|
    url = m[0]
    next if url == "/" || url.start_with?("#", "mailto:", "tel:", "http://", "https://", "//", "javascript:")
    target = url.split(/[?#]/, 2).first.sub(%r{^/}, "")
    next if target.empty?
    missing << "#{path} -> #{url}" unless File.exist?(File.join(ROOT, target))
  end
end
errors.concat(missing.map { |m| "missing local link/asset: #{m}" })

puts "WorldIDP validator"
puts "Errors: #{errors.length}"
puts "Warnings: #{warnings.length}"
errors.each { |e| puts "ERROR: #{e}" }
warnings.first(20).each { |w| puts "WARN: #{w}" }
exit(errors.empty? ? 0 : 1)
