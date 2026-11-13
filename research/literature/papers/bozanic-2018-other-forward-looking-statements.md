# Management earnings forecasts and other forward-looking statements

- **Citation:** Zahn Bozanic, Darren T. Roulstone and Andrew Van Buskirk (2018), *Journal of Accounting and Economics* 65(1), 1–20. Version read: working paper dated May 2015 (Ohio State University), full text. The published abstract was checked on EconPapers.
- **Link:** <https://www.stern.nyu.edu/sites/default/files/assets/documents/Darren%20Roulstone_51415.pdf> (working paper). Published version: <https://econpapers.repec.org/RePEc:eee:jaecon:v:65:y:2018:i:1:p:1-20>.
- **Stream:** 01, financial text analysis before LLMs
- **Verified against source:** yes, 2026-11-12. Every number below is from the 2015 working paper and was not re-checked against the journal version. The published abstract states the same main conclusions.

## Question

Numeric earnings forecasts are what the guidance literature studies. How much of the forward-looking content of an earnings press release are they, do the other forward-looking statements matter to investors and analysts, and do managers issue the two kinds under the same conditions?

## Data

- Text source: quarterly earnings press releases furnished on 8-K ("Results of Operations and Financial Condition") on EDGAR, filed within five days of the Compustat announcement date, 2004 to 2014. 2004 is the first year these 8-Ks exist electronically.
- Sample: 67,276 earnings announcements from 4,476 firms. Each needs I/B/E/S actuals and at least one analyst estimate, CRSP and Compustat data, and the prior quarter's 8-K.
- Universe: tilted to larger covered firms (median market value about $1.2 billion, median analyst coverage 4), as the authors note. Delisted firms are not discussed.
- Benchmark label: an I/B/E/S Guidance record within one day of the announcement.

## Method

- Sentence-level keyword rules in Perl. Safe-harbour boilerplate is removed. A sentence is forward-looking if it contains a term from a list that follows Li (2010), such as "anticipate", "expect" or "forecast"; the list is printed in the paper's Appendix A.
- Each forward-looking sentence is tagged on two dimensions: earnings-related (contains "earnings", "income", "loss", "profit" or similar) and quantitative (a dollar sign, a percentage, or a scale word such as "million").
- "Forecast-like" means both tags. Everything else is "other".
- Validation: of 60 hand-read First Call guidance records, 58 contained one of the earnings terms. In a probit for the presence of an I/B/E/S forecast, the share of forecast-like sentences has z = 23.58 (pseudo-R² 0.14) and the share of other forward-looking sentences has no association.

## Outcome variable and horizon

- Absolute three-day stock return around the announcement.
- Change in analysts' absolute error for next quarter's earnings, from before the announcement to seven days after.
- The share of each sentence type in the release, as a function of five uncertainty proxies (loss, earnings volatility, expectations gap, implied volatility, analyst dispersion).

## Result

All labelled **empirical finding**.

- Prevalence: a release averages 76.7 sentences, 11.6 of them forward-looking (14.3%). Of those, 1.9 are earnings-related and 2.1 quantitative; only 0.6 are both, against 11.0 "other". Forecast-like sentences are about 5% of forward-looking sentences (9.1% for firms with an I/B/E/S forecast, 2.5% for the rest).
- 37% of announcements (24,690) carry an I/B/E/S management forecast, between 33% and 41% in every year; 2,385 of the 4,476 firms never have one. Yet 75% of announcements contain at least five forward-looking sentences.
- Consequences: more forward-looking content goes with larger absolute announcement returns and a larger fall in analyst error, controlling for the size of the earnings surprise (separately for positive and negative), earnings volatility, a loss indicator, size, book-to-market and return volatility. Per sentence, a forecast-like sentence matters more (0.125 against 0.0221, difference p < 0.01). Per standard deviation, the two are indistinguishable (0.0018 against 0.00158, p = 0.82 for returns; p = 0.36 for analyst error).
- Independence: firms with and without an I/B/E/S forecast issue the same share of "other" forward-looking sentences (13.9% against 13.2%, not significant).
- Stickiness: the previous release's share is by far the strongest predictor of this release's share. Adding it lifts R² from 0.017 to 0.43 for forecast-like sentences and from 0.001 to 0.54 for the rest (coefficient about 0.73). The authors read this as firms reusing a template and updating the numbers.
- Uncertainty: for all five proxies, higher uncertainty goes with fewer forecast-like sentences and more of the other kind. Holding "quantitative" fixed, uncertainty depresses earnings statements much more than non-earnings ones; holding "earnings" fixed, it barely separates quantitative from qualitative. The authors conclude that managers avoid forecasting what they cannot control more than they avoid being checkable.

## Look-ahead and memorisation

Not addressed, and not at issue for the method: rules, no trained or pretrained model. The outcome windows start at the announcement. The sample requires analyst coverage and a prior-quarter 8-K, which conditions on the firm being established, not on later survival.

## What it settles for us

- **Text source: supported.** Guidance and other outlook statements are in the Item 2.02 press release, on EDGAR, parseable at scale since 2004. This is the same document the project chose.
- **First benchmark is guidance revision: supported, with a coverage warning.** Numeric earnings guidance is real but a minority: roughly a third of covered firm-quarters, fewer among small firms that the I/B/E/S filter drops. The guidance census in WP2 should expect this and should count non-EPS numeric guidance separately. The paper's "other" bucket includes numeric revenue, margin and capital-expenditure guidance, which our tuple (metric, period, low, high, basis) would capture.
- **Qualitative stratum: supported.** Non-numeric outlook statements move prices and analyst accuracy.
- **Numeric anchor rule: partly contradicted.** Under high uncertainty (losses, volatile earnings), firms drop numeric earnings forecasts and say more in other forms. A benchmark and an L2 test confined to numeric anchors under-samples exactly the firm-quarters closest to failure. This is a selection effect to report, even if the rule stays.
- **Consecutive-release pairs: supported.** Releases are templates; the lagged share explains about half the variance. "Maintained" wording will be common, and departures from the template are the signal.
- **Baseline to beat.** The keyword rules here are the natural rule baseline for "find the outlook sentences". The word lists are published in the paper's appendix.
- **Label source.** Commercial guidance databases are the literature's labels. The paper notes that fewer than 5% of post-Regulation FD records in First Call are qualitative, so those databases cannot label the qualitative stratum.

## Limits

- Working-paper numbers.
- The paper counts sentences; it does not read their direction. Outcomes are unsigned (absolute returns, error reduction), so it shows that other forward-looking statements matter, not what they say.
- The quantitative tag fires on any dollar sign or percentage in a forward-looking sentence, and the earnings tag on any earnings word; neither checks that the number is the forecast.
- No extraction of the forecast itself (metric, period, range), and no comparison across consecutive releases beyond the lagged share.
