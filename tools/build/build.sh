#!/usr/bin/env bash
# WorldIDP production build. Any failing gate aborts the build.
set -e
cd "$(dirname "$0")/../.."
echo "== 0/14 US pages ==";            python3 tools/build/build_us_pages.py
echo "== 1/14 enrich country data =="; python3 tools/build/enrich_countries.py
echo "== 2/6 generate country pages ==";python3 tools/build/generate_country_pages.py
echo "== 3/6 entity graph ==";          python3 tools/build/fix_entity.py
echo "== 4/6 registry (CSV + Dataset) ==";python3 tools/build/build_registry.py
echo "== 5/6 sitemap ==";               python3 tools/build/build_sitemap.py
echo "== 6/7 internal links =="; python3 tools/build/add_internal_links.py
echo "== 7/9 llms.txt =="; python3 tools/build/build_llms_txt.py
echo "== 8/10 expand AAA page =="; python3 tools/build/expand_aaa_page.py
echo "== 9/12 expand guides ==";      python3 tools/build/expand_guides.py
echo "== 10/12 GEO entity layer ==";  python3 tools/build/geo_entity_layer.py
echo "== 11/14 research findings =="; python3 tools/build/build_research_page.py
echo "== 12/15 glossary ==";          python3 tools/build/build_glossary.py
echo "== 13/15 guides hub ==";       python3 tools/build/build_guides_hub.py
echo "== 14/16 cannibalisation ==";  python3 tools/build/check_cannibalisation.py
echo "== 15/16 validate ==";              python3 tools/build/validate.py
echo ""; echo "duplication:";           python3 tools/build/measure_duplication.py
echo "== 8/8 preflight ==";           python3 tools/build/preflight.py
