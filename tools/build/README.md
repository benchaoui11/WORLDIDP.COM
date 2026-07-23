# WorldIDP build system

Run everything:

    bash tools/build/build.sh

Pipeline, in order. Any failing gate aborts the build.

| Step | Script | What it guarantees |
|---|---|---|
| 1 | `enrich_countries.py` | Merges research + legacy data. **Derives** `evidenceTier` and `indexable` from evidence actually present — these are never hand-set. |
| 2 | `generate_country_pages.py` | Renders 124 pages. Title/H1 chosen by the country's own data pattern. Absent facts render an explicit "not confirmed" line, never an estimate. |
| 3 | `fix_entity.py` | One stable `@id` for the Organization across the whole site. Writes `sameAs` **only** from confirmed profiles in `data/verified-profiles.json`. |
| 4 | `build_registry.py` | Public CSV + `Dataset`/`DataDownload` schema, with `evidenceTier` and `sourceCount` columns so gaps are visible to anyone citing it. |
| 5 | `build_sitemap.py` | Reads the `robots` meta from each rendered file. A noindex page **cannot** enter the sitemap. |
| 6 | `add_internal_links.py` | Contextual links from pillars to verified countries. Per-pillar anchor text, not one repeated block. |
| 7 | `validate.py` | Six check groups. Exits non-zero on any failure. |

`measure_duplication.py` reports 5-word shingle Jaccard similarity on body text,
excluding header/footer/nav/CTA.

## Evidence tiers

| Tier | Requires | Result |
|---|---|---|
| **A** | idpStatus + drivingSide + conventions + lastVerified + documentsToCarry + **≥2 official sources** + ≥2 supporting notes | `index, follow` + in sitemap |
| **B** | drivingSide + (conventions or reported status) | `noindex, follow`, excluded from sitemap |
| **C** | anything less | `noindex, follow`, excluded from sitemap |

## To promote a country to Tier A

Edit `data/countries.json` for that slug:
`idpStatus`, `idpStatusApplies`, `idpStatusExempt`, `documentsToCarry`,
`officialSources` (≥2 objects with `name` + `url`), `lastVerified`.
Add supporting notes and FAQs to `data/country-notes.json`.
Then run `bash tools/build/build.sh` — the tier and sitemap update themselves.

## What this system will not do

- Invent a speed limit, legal requirement, rental age or BAC limit.
- Publish a requirement without a citable source and a review date.
- Write a `sameAs` URL that has not been confirmed to exist.
- Let a noindex page into the sitemap.
