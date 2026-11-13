# Stream 06: distress and failure prediction

Notes in `../papers/`: `campbell-2008-in-search-of-distress-risk.md` [CHS], `lerman-2010-new-form-8k-disclosures.md` [LL], `asness-2019-quality-minus-junk.md` [AFP]. Rows: `06_distress.csv`. [8-K] https://www.sec.gov/files/form8-k.pdf. [CAQ] https://www.carltonfields.com/files/Uploads/Documents/2016/RWI/financial-restatement-trends-in-the-united-states-2003-2012.pdf

## What the stream establishes

- **Convention.** Failure is bankruptcy or, more broadly, bankruptcy, delisting or default [CHS]. Misreporting is an enforcement release or a restatement (Dechow, Brown rows).
- **Empirical finding: base rates per year.** Bankruptcy: 0.36–1.53% of CRSP firms, 1980–1998. Broad failure: 1.52–3.67%, 1998–2003 [CHS]. Delisting for cause: 3.25% of listed firms in 1975–1996, 3.50% in 1997–2012, very low in 2014–2021 (Doidge row). Enforcement-identified misstatement: 0.37% of firm-years, 1982–2005 (Dechow row). Item 4.02 restatements: about 1,000 in 2005 and 255 in 2012, all SEC registrants [CAQ]. Item 2.06: 532 filings in 2005–2006 [LL]. Both are counts; no impairment rate was found.
- **Empirical finding: the structured bar.** Eight accounting and market variables give pseudo-R² 0.31 at one month and 0.11 at twelve, about twice distance to default [CHS]. The F-score catches 69% of misstating firm-years at a 36% false-positive rate (Dechow row).
- **Empirical finding: text.** MD&A going-concern language and tone reach AUC 0.85 one year before bankruptcy against 0.90 for ratios, and 0.73 against 0.66 three years before (Mayew row, working-paper figures). A distress dictionary lifts holdout AUC from 0.83 to 0.90 on 34 events (Zhang row). 10-K topics improve misreporting detection by up to 59% (Brown row).
- **Empirical finding: junk.** Quality-minus-junk earns 0.29% a month (t=3.6) with market loading −0.20; its raw return is zero in months when volatility falls sharply [AFP]. Safe-minus-distressed returns turned negative by 2003 [CHS].
- **Open question.** No paper read tests an LLM-extracted signal against the hazard model.

## Design defaults

- **Four 8-K items as the hard tier: supported, with caveats.** Items 2.06, 3.01 and 4.02 carry significant negative price reactions [LL]. But 3.01 covers curable deficiencies and voluntary transfers, 2.06 exempts impairments concluded while preparing a periodic report, 1.03(b) is plan confirmation [8-K], and 4.02 was 35% of restatements by 2012 [CAQ].
- **Softer tiers pre-registered later: supported.** Published definitions exist.
- **Failure prediction exploratory: supported.** At 0.3–1.5% a year, 800 companies yield two to twelve bankruptcies.
- **Delisted stocks: supported.** Omitted delisting returns are large (Shumway row, abstract only). Conventions: −30% [AFP]; −100% for forced delistings [LL].

## Recommendation for softer tiers

1. Filing-anchored: auditor going-concern paragraph; completed delisting for cause (Doidge row codes); any restatement; impairment charge in as-filed figures.
2. Fundamental: fall in an as-filed profitability-and-leverage composite [AFP].
3. Market: twelve-month market-adjusted return including the delisting return, reported by market state.

## Gaps suggesting experiments

- Incremental AUC of the guidance signal over the eight variables plus a distress dictionary.
- Managers mention going-concern doubt in 38% of later bankruptcies (Mayew row): test narrative optimism in the rest.
- Text evidence comes from 10-Ks; earnings press releases are untested.

## Changes to the plan

- Run the hard-event census by sub-item, with firm denominators.
- The structured baseline needs daily prices for delisted firms.
- State expected event counts in EXP-0001.
