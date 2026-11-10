# roman-coins: working notes and analysis plan

"Lost money: Roman coins found in England, reign by reign". Author Dr Tristan Hotham, Independent researcher.

## Status

- Phase 1 (this section, 2026): data read and checked for structure (key counts, list lengths, name matching, county totals). The analysis plan below was written after that structural inspection and **before any district-level shares, gradients or models were computed**. It is pre-specified in a written plan. Anything added later is labelled exploratory.
- What was seen before the plan, stated for honesty: the national Reece-period totals (`nat.reece`, which make the national profile in H1 visible) and the county totals of all records, Roman coins and Reece-dated coins. H1 is therefore a replication check, not a blind test. Nothing regional (H2 to H4) had been computed.

## Data found in phase 1 (facts that change the brief)

- Input: `/home/claude/newdata/raw_new14/coins/pas_roman_coins.json`, 1,317 keys, from the Portable Antiquities Scheme public search API (api.finds.org.uk), retrieved 2026. Values are facet lists `[name, count, flag]`; no flag is set anywhere. Counts are **records** (a record can hold more than one coin), not coins.
- **Coverage is England only.** The 47 "ceremonial" counties in the file are England's ceremonial counties (City of London is recorded inside Greater London). Welsh finds appear in `nat.county` (for example Monmouthshire, Conwy, Powys, Newport) but there are no per-county district keys for Wales. So the study, its title and every label say England, not England and Wales. To add Wales, the lead would need the same facet queries for the Welsh principal areas (see final report).
- District lists are complete: the longest district list has 33 names (Greater London), under the API's 50-value facet cap. Ruler lists are capped at 50 (top 50 only) and are used only descriptively.
- **District names match ONS LAD December 2023 exactly**: 296 distinct names, all 296 English LADs present, no unmatched names, so no merging to successor authorities was needed (PAS has already moved records to the 2023 districts, e.g. Cumberland, Westmorland and Furness, North and West Northamptonshire, Somerset, North Yorkshire). 11 district names appear under more than one ceremonial county (records whose county and district disagree, e.g. West Suffolk under Norfolk and Cambridgeshire); counts are summed by district, which counts each record once.
- District sums fall slightly short of the county totals (records without a district); the gap is reported in results.json.
- Reece period dates: Nomisma.org concepts reece1 to reece24 (which match finds.org.uk/romancoins/reeceperiods), fetched from GitHub nomisma/data: P1 to AD 41, P2 41-54, P3 54-68, P4 69-96, P5 96-117, P6 117-138, P7 138-161, P8 161-180, P9 180-193, P10 193-222, P11 222-238, P12 238-260, P13 260-275, P14 275-296, P15 296-317, P16 317-330, P17 330-348, P18 348-364, P19 364-378, P20 378-388, P21 388-402, P22 402-445, P23 445-498, P24 498-565. Periods 22 to 24 are fifth and sixth century and are reported separately; the analysis uses P1 to P21, Reece's 21 periods.
- Boundaries: ONS Local Authority Districts (December 2023) Boundaries UK BSC (Open Government Licence v3.0; contains OS data), already in `/home/claude/newdata/raw/geo/lad23_bsc.geojson`; English regions from the ONS topojson in the same folder. Reused rather than cloned again, to save disk.

## Pre-specified analysis plan

Unit: English local authority district (LAD 2023), N = 296. Counts are PAS records.

Measures per district:
- `records`: all PAS records of any period and type (recording intensity, the denominator).
- `coins`: Roman coin records. `rate` = coins per 1,000 records.
- `dated`: Roman coin records with a Reece period 1 to 21.
- `late` = P19 to P21 (AD 364 to 402); `early` = P1 to P10 (to AD 222).
- Per-mille profile: coins in period p per 1,000 dated coins; per-year rate = per mille divided by period length (P1 omitted from per-year, it has no start date).
- Coordinates: district centroid in British National Grid, easting and northing in 100 km.

Hypotheses and tests:

- **H1 (national profile, replication).** England's PAS profile shows the classic British site-find shape: the highest loss per year in P13 (260-275) and P17 (330-348), high in P14, P16 and P19, low in P9 to P12 and after P19. Reported descriptively with per-year rates and a period-by-period ratio to England's mean.
- **H2 (late surge south and east).** The late share (P19 to P21 of dated coins) rises to the east and falls to the north. Main model: binomial GLM (logit link) of late / dated on easting and northing, districts with at least 20 dated coins, Pearson-scaled dispersion, standard errors clustered by ceremonial county (the county in which most of the district's records sit). Report odds ratios per 100 km with 95% CI and N. Against H2: an easting OR at or below 1 or a northing OR at or above 1, or CIs including 1.
- **H3 (early north and west).** The early share (P1 to P10) rises to the north and west (the military zone). Same model. Against H3: easting OR at or above 1 or northing OR at or below 1, or CIs including 1.
- **H4 (Roman coin share of all finds).** Roman coins per 1,000 PAS records are higher in the south and east. Same model with coins / records, all 296 districts.
- **H5 (regional profiles, exploratory).** Per-mille profiles for the nine English regions; principal component analysis of district per-mille profiles (districts with at least 100 dated coins), first component interpreted only if it separates early from late periods.

Robustness (each for H2, H3, H4 where it applies):
1. Minimum dated coins 0, 50 and 100 instead of 20.
2. Weighted least squares on the empirical logit instead of the GLM.
3. Standard errors clustered by region (9 clusters; small, reported as a check).
4. Leave one region out (9 fits).
5. Drop the 10 districts with the most coin records (large sites and hoards recorded coin by coin).
6. Drop districts where one Reece period holds more than 40% of dated coins (a sign of a hoard recorded coin by coin).
7. Alternative late definitions: P20 to P21 (after 378); P17 to P21 (after 330).
8. Control for detecting intensity: add log records per km2.
9. Negative binomial count model of late coins with offset log(dated).
10. Spatial permutation (falsification): shuffle shares across district locations 999 times (seed 2026) and compare the easting and northing coefficients to the permutation distribution.

Caveats to state: PAS records are what detectorists and others choose to report, shaped by land use (arable land is detected more), access, permission, reporting culture and Finds Liaison Officer capacity (Robbins 2013; Brindle 2014); the denominator controls for overall recording but not for what is selected within it; records not coins; hoards can be recorded coin by coin; findspots are public only to district level; the analysis is descriptive and associational.

## Log

- 2026: plan written after structural checks, before any district shares or models. Reece period definitions fetched from nomisma/data (GitHub) to scratch, transcribed above, scratch deleted.

## Phase 2 log (after the plan)

- Planned results: H1 supported (replication; national totals seen before the plan). H2, H3, H4 not supported: all six gradient odds ratios have 95% intervals including 1 in the main models; robustness checks agree (two specification-dependent exceptions reported in the paper). Spatial permutation agrees.
- statsmodels quirk: `fit(scale="X2")` with two-column binomial endog gave a wrong dispersion (0.05). The reported dispersion is now Pearson chi2 / df from the unclustered fit; clustered standard errors are identical with or without the scale argument (checked), so no estimate changed.
- Exploratory, added after the planned results and labelled so everywhere: NE+NW indicator models, region Wald test, period-by-period gradients, PCA (H5 was planned as exploratory).
- Literature verified by web search (titles, venues, volumes, pages, DOIs) in 2026; claims attributed only to what abstracts or verified summaries say. Internet Archaeology charges an APC, so it is excluded in the cover note.
- Wales gap reported to the lead with the exact queries needed.

## Independent review (2026)

- Headline figures recomputed from the raw facet file and the main H2 and H4 models refitted: all match results.json.
- Wording fixed so that "records, not coins" and "all but one of 20 checks" (the AD 378 to 402 definition leans east; the negative binomial and leave-out-South-East fits for the early share also exclude 1) are stated consistently. Henry (2024) and Walton and Moorhead (2016) descriptions corrected against the sources. Ruler exceptions completed (West Yorkshire, Staffordshire, Greater Manchester). Nomisma CC BY noted.
- Figures: period small-multiple titles moved onto paper; Wales label on the district map moved to sea; hatched note no longer overlaps the legend; GIF inset ticks moved off the map, Wales label and "pale" legend note added; collage subtitle says records; map popup sits above the full-screen button.
