**Title:** [OC] Roman coins found in England, reign by reign: 275,206 coin records show coin loss peaking under Constantine (AD 330 to 348), and the old frontier keeping its early coins

**Body:**

I counted every Roman coin record in the Portable Antiquities Scheme in England, district by district and by Reece's 21 coin periods, and divided by all finds recorded in each district to allow for where people detect.

- 275,206 Roman coin records among 1,062,032 records of finds of every period (259 per 1,000).
- Coin loss per year peaks in AD 330 to 348, at 4.8x an even rate. 82% of dated coins are later than AD 260.
- I expected late coins to rise steadily towards the south east. They don't: no smooth gradient in the planned test, and all but one of 20 checks agree.
- Instead there's a step. In the North East and North West, 58% of dated coins are from before AD 222 (rest of England: 15%), and only 4% are from after AD 364 (rest: 16%).
- Constantine I is the commonest named emperor in 36 of 47 counties; Trajan leads in Cumbria.

England only (the Welsh finds weren't in the download). Counts are records, not individual coins.

Interactive map with a slider through every reign: https://maps.tristanhotham.com/roman-coins/

**Source comment:**

Data: Portable Antiquities Scheme database (finds.org.uk), public search counts, 2026; Reece period dates from Nomisma.org; ONS district boundaries (OGL v3.0). Method: binomial regressions with county-clustered errors, analysis plan written before the district shares were computed. Tools: Python (pandas, geopandas, statsmodels, matplotlib), MapLibre. Paper and code: https://github.com/Tristan-Hotham/roman-coins
