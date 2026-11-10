"""Step 9: README.md and reddit/post.md from data/results.json."""
from common import *

R = jload(f"{DATA}/results.json"); B = R["build"]
def ci(c): return f"{c['or']:.2f} (95% CI {c['lo']:.2f} to {c['hi']:.2f})"
H2, H3, H4 = R["H2"]["main"], R["H3"]["main"], R["H4"]["main"]
readme = f"""# Lost money

Roman coins found in England, reign by reign. Roman coin records from the Portable Antiquities Scheme (PAS), counted by English district (ONS 2023) and by Reece's 21 coin periods, and set against all PAS records in each district as a measure of how much is found and recorded there.

Interactive page: {PAGE}
Paper: {{https://doi.org/10.5281/zenodo.24115196}}
Blog post: {{https://blog.tristanhotham.com/2026/10/31/roman-coins/}}
Code and data: {REPO}

**Coverage.** England only. The district queries were made by English ceremonial county; Welsh finds were not retrieved.

## Headline results

- {B['coins']:,} Roman coin records among {B['records']:,} PAS records in England's 296 districts ({B['coin_rate']:.0f} per 1,000). {B['dated']:,} coin records ({B['dated_pc']:.1f}%) have a Reece period from 1 to 21.
- The English profile is Reece's British site-find curve: loss per year is highest in AD 330 to 348 ({R['H1']['top1_py']:.1f} per 1,000 dated coins per year, {R['H1']['p17_x_mean']:.1f} times an even rate), then AD 364 to 378 ({R['H1']['top2_py']:.1f}) and AD 260 to 275 ({R['H1']['top3_py']:.1f}). {R['H1']['after260_pc']:.1f}% of dated coins are later than AD 260.
- Planned tests (pre-specified in a written plan, {R['sample']['d20']} districts with at least 20 dated coins), odds ratios per 100 km:
  - H2, late share (AD 364 to 402): east {ci(H2['east'])}; north {ci(H2['north'])}. Not supported.
  - H3, early share (to AD 222): east {ci(H3['east'])}; north {ci(H3['north'])}. Not supported.
  - H4, Roman coins among all records (296 districts): east {ci(H4['east'])}; north {ci(H4['north'])}. Not supported.
  - {R['robust_n']['H2']} robustness checks for H2 (thresholds, estimator, clustering, leave one region out, dropping large or hoard-like districts, intensity control, negative binomial, other late definitions) and a spatial permutation test agree, with one exception: defining late as AD 378 to 402 gives an eastward lean: {ci(R['H2']['alt_after378']['east'])}.
- Exploratory: a step, not a slope. In the North East and North West, {R['nw']['late_pc']:.1f}% of dated coins are late and {R['nw']['early_pc']:.1f}% early; elsewhere {R['nw']['rest_late_pc']:.1f}% and {R['nw']['rest_early_pc']:.1f}%. Odds ratio for late, two northern regions against the rest: {R['x']['nw_late_or']:.2f} ({R['x']['nw_late_lo']:.2f} to {R['x']['nw_late_hi']:.2f}). The South West has the highest late share ({R['x']['sw_late']:.1f}%).
- Exploratory, by period: AD 193 to 222 leans north ({R['by_period']['P10']['north_or']:.2f} per 100 km); AD 275 to 296 leans east ({R['by_period']['P14']['east_or']:.2f}); AD 388 to 402 leans east ({R['by_period']['P21']['east_or']:.2f}).
- Constantine I is the commonest named ruler in {R['rulers']['county_top_counts'][0][1]} of 47 English counties.

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

- Counts: PAS public search API facets, retrieved 2026, for each English ceremonial county: all records by district, Roman coin records by district, by Reece period and by district within each period, top 50 rulers. 1,317 queries, none failed. District lists have at most {B['max_list']} names, under the API's 50-value cap, so they are complete.
- Districts: all {B['names_in_pas']} names match ONS Local Authority Districts (December 2023) exactly; none unmatched. Counts are summed by district across counties ({B['multi_county_records']} records sit under a county other than the district's main one).
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

Hotham, T. (2026) Lost money: Roman coin loss across England by district and Reece period, from the Portable Antiquities Scheme. Zenodo. {{https://doi.org/10.5281/zenodo.24115196}}

Dr Tristan Hotham, Independent researcher. ORCID 0000-0003-4931-9349.

{AI}
"""
for bad in ("—", "–", "D" "SIT", "D" "CMS", "pre-" "registered"):
    assert bad not in readme, bad
open(f"{ROOT}/README.md", "w", encoding="utf-8").write(readme)
post = f"""**Title:** [OC] Roman coins found in England, reign by reign: {B['coins']:,} coin records show coin loss peaking under Constantine (AD 330 to 348), and the old frontier keeping its early coins

**Body:**

I counted every Roman coin record in the Portable Antiquities Scheme in England, district by district and by Reece's 21 coin periods, and divided by all finds recorded in each district to allow for where people detect.

- {B['coins']:,} Roman coin records among {B['records']:,} records of finds of every period ({B['coin_rate']:.0f} per 1,000).
- Coin loss per year peaks in AD 330 to 348, at {R['H1']['p17_x_mean']:.1f}x an even rate. {R['H1']['after260_pc']:.0f}% of dated coins are later than AD 260.
- I expected late coins to rise steadily towards the south east. They don't: no smooth gradient in the planned test, and all but one of {R['robust_n']['H2']} checks agree.
- Instead there's a step. In the North East and North West, {R['nw']['early_pc']:.0f}% of dated coins are from before AD 222 (rest of England: {R['nw']['rest_early_pc']:.0f}%), and only {R['nw']['late_pc']:.0f}% are from after AD 364 (rest: {R['nw']['rest_late_pc']:.0f}%).
- Constantine I is the commonest named emperor in {R['rulers']['county_top_counts'][0][1]} of 47 counties; Trajan leads in Cumbria.

England only (the Welsh finds weren't in the download). Counts are records, not individual coins.

Interactive map with a slider through every reign: {PAGE}

**Source comment:**

Data: Portable Antiquities Scheme database (finds.org.uk), public search counts, 2026; Reece period dates from Nomisma.org; ONS district boundaries (OGL v3.0). Method: binomial regressions with county-clustered errors, analysis plan written before the district shares were computed. Tools: Python (pandas, geopandas, statsmodels, matplotlib), MapLibre. Paper and code: {REPO}
"""
for bad in ("—", "–", "D" "SIT", "D" "CMS"):
    assert bad not in post, bad
open(f"{ROOT}/reddit/post.md", "w", encoding="utf-8").write(post)
print("README", len(readme.split()), "words; post", len(post.split()))
