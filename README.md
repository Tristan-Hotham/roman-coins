# Lost money

Roman coins found in England, reign by reign. Roman coin records from the Portable Antiquities Scheme (PAS), counted by English district (ONS 2023) and by Reece's 21 coin periods, and set against all PAS records in each district as a measure of how much is found and recorded there.

Interactive page: https://maps.tristanhotham.com/roman-coins/
Paper: https://doi.org/10.5281/zenodo.24115196
Blog post: https://blog.tristanhotham.com/2026/10/31/roman-coins/
Code and data: https://github.com/Tristan-Hotham/roman-coins

**Coverage.** England only. The district queries were made by English ceremonial county; Welsh finds were not retrieved.

## Headline results

- 275,206 Roman coin records among 1,062,032 PAS records in England's 296 districts (259 per 1,000). 188,831 coin records (68.6%) have a Reece period from 1 to 21.
- The English profile is Reece's British site-find curve: loss per year is highest in AD 330 to 348 (13.2 per 1,000 dated coins per year, 4.8 times an even rate), then AD 364 to 378 (9.6) and AD 260 to 275 (8.9). 82.4% of dated coins are later than AD 260.
- Planned tests (pre-specified in a written plan, 173 districts with at least 20 dated coins), odds ratios per 100 km:
  - H2, late share (AD 364 to 402): east 0.94 (95% CI 0.83 to 1.06); north 0.98 (95% CI 0.89 to 1.08). Not supported.
  - H3, early share (to AD 222): east 0.85 (95% CI 0.65 to 1.12); north 1.16 (95% CI 0.93 to 1.43). Not supported.
  - H4, Roman coins among all records (296 districts): east 1.04 (95% CI 0.85 to 1.27); north 0.89 (95% CI 0.78 to 1.03). Not supported.
  - 20 robustness checks for H2 (thresholds, estimator, clustering, leave one region out, dropping large or hoard-like districts, intensity control, negative binomial, other late definitions) and a spatial permutation test agree, with one exception: defining late as AD 378 to 402 gives an eastward lean: 1.15 (95% CI 1.03 to 1.29).
- Exploratory: a step, not a slope. In the North East and North West, 4.3% of dated coins are late and 57.9% early; elsewhere 15.9% and 14.7%. Odds ratio for late, two northern regions against the rest: 0.23 (0.14 to 0.37). The South West has the highest late share (17.2%).
- Exploratory, by period: AD 193 to 222 leans north (1.43 per 100 km); AD 275 to 296 leans east (1.31); AD 388 to 402 leans east (1.19).
- Constantine I is the commonest named ruler in 36 of 47 English counties.

## Files

| File | What it is |
|---|---|
| `index.html`, `js/page.js` | Interactive page: MapLibre on OpenFreeMap Positron; districts coloured by coins per 1,000 finds or against England, a slider and Play button through the 21 periods, search, layers, full screen, popups with each district's profile and its county's commonest rulers. |
| `header.png` | Social card, 1200 x 630. |
| `data/districts.csv` | One row per English district: all records, Roman coin records, records in each Reece period 1 to 24, dated, early and late counts, area, centroid easting and northing, region, county. |
| `data/periods_england.csv` | Reece periods with dates and England totals (county facet, district sum, PAS national). |
| `data/county_rulers.json` | Top 50 rulers on Roman coin records per county, and nationally. |
| `data/profiles_region.csv`, `data/district_profiles.csv` | Regional profiles; district table with the exploratory principal component. |
| `data/results.json`, `data/results_models.json`, `data/build.json` | Every number quoted anywhere, every estimate, data checks. |
| `data/districts.geojson`, `data/counties.geojson`, `data/england.geojson`, `data/site.json` | Page data. |
| `code/` | Scripts in order, templates, `qa.js`. |
| `release/` | Paper (PDF, LaTeX, figures, `cover_note.md`), blog post and figures, Zenodo files. |
| `reddit/` | Collage, its script, the looping GIF and the post text. |
| `NOTES.md` | Working notes and the analysis plan, written before any district shares were computed. |

## Method in brief

- Counts: PAS public search API facets, retrieved 2026, for each English ceremonial county: all records by district, Roman coin records by district, by Reece period and by district within each period, top 50 rulers. 1,317 queries, none failed. District lists have at most 33 names, under the API's 50-value cap, so they are complete.
- Districts: all 296 names match ONS Local Authority Districts (December 2023) exactly; none unmatched. Counts are summed by district across counties (57 records sit under a county other than the district's main one).
- Measures: per-mille and per-year profiles by Reece period; late share (periods 19 to 21) and early share (1 to 10) of dated coins; Roman coins per 1,000 records.
- Models: binomial GLMs of each share on easting and northing (100 km units), standard errors clustered by ceremonial county; planned checks and a 999-shuffle spatial permutation (statsmodels).

## How to rerun

Needs Python 3 with pandas, numpy, geopandas, statsmodels, scipy, matplotlib, Pillow; xelatex and pdftotext; node with Playwright for QA. Inputs are listed in `code/common.py`.

```
python3 code/01_build.py        # district table, geometry, rulers
python3 code/02_models.py       # planned and exploratory models
python3 code/03_results.py      # results.json
python3 code/04_figures.py      # figures and header
python3 code/05_site_data.py    # page data
python3 code/06_site.py         # index.html
python3 code/07_paper.py        # paper (DOI=10.5281/zenodo.N to fill the DOI)
python3 reddit/collage.py
python3 code/09_readme.py       # README, Reddit post
python3 code/08_release.py      # blog post, Zenodo files
node code/qa.js                 # screenshots in qa/
```

## Sources and licences

- Portable Antiquities Scheme database, finds.org.uk (British Museum and Amgueddfa Cymru): public search facet counts, retrieved 2026. Only aggregate counts are republished; findspots are public only to district level. With thanks to the finders and Finds Liaison Officers.
- Reece period dates: Nomisma.org concepts reece1 to reece24 (github.com/nomisma/data), CC BY.
- Boundaries: ONS Local Authority Districts (December 2023) Boundaries UK BSC; ONS regions; ceremonial counties. Open Government Licence v3.0; contains OS data (c) Crown copyright and database right.
- Base map: OpenFreeMap Positron (OpenStreetMap contributors, ODbL). MapLibre GL JS (BSD 3-Clause).
- Text, figures and derived data CC BY 4.0; code MIT.

## Citation

Hotham, T. (2026) Lost money: Roman coin loss across England by district and Reece period, from the Portable Antiquities Scheme. Zenodo. https://doi.org/10.5281/zenodo.24115196

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

I wrote the text, with drafting and editing assistance from Claude (Anthropic), which also helped prepare the analysis code. I reviewed and checked all text and results.
