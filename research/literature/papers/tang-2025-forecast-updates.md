# Once Is Not Enough: An Analysis of Management Updates of Annual Earnings Forecasts

- **Citation:** Michael Tang, Li Yao and Paul Zarowin (2025), *Journal of Accounting, Auditing & Finance*, published online, DOI 10.1177/0148558X251394474. Version read: working paper dated 7 May 2015, titled "Once Is Not Enough: The Determinants and Consequences of Management Updates of Annual Forecasts", full text. The published abstract was read through the OpenAlex record.
- **Link:** <https://www.stern.nyu.edu/sites/default/files/assets/documents/Michael%20Tang.pdf> (working paper). Published version: <https://doi.org/10.1177/0148558X251394474>; abstract via <https://api.openalex.org/works/doi:10.1177/0148558x251394474>.
- **Stream:** 01, financial text analysis before LLMs
- **Verified against source:** yes, 2026-11-12. Every number below is from the 2015 working paper. The published abstract, ten years later, reports the same qualitative patterns but was not checked number by number; treat the figures as indicative.

## Question

After issuing an annual earnings forecast, how often do managers update it during the year, what do the updates look like (range width, midpoint, direction), and do analysts respond?

## Data

- Source: First Call Company Issued Guidance, annual EPS forecasts for fiscal years 1996 to 2011. No text is analysed; the paper uses the database's structured records.
- Sample: 63,005 forecasts reduce to 37,150 forecasts for 14,301 firm-years after dropping forecasts that are neither a point nor a closed range (4,645), long-horizon forecasts, pre-announcements after year end, and repeat forecasts within a quarter.
- Property tables use firm-years whose first forecast is in the first fiscal quarter (about 8,700 to 9,600 firm-years).
- Universe: firms in First Call that give numeric annual EPS guidance. Delisted firms are not discussed.

## Method

- Classifies firm-years by the number of quarters with a forecast: no update, sporadic update, or an update every quarter ("regular updaters").
- Logit for updating on last year's behaviour and on conditions that would call for an update (analyst error, dispersion, gap between management and analysts).
- Tabulates, update by update, whether the range width and the midpoint changed and in which direction.
- OLS of analyst consensus revisions on forecast news (management midpoint minus prior consensus, scaled by price), with interactions for first, second and third updates. Controls: concurrent earnings news, last year's forecast error, forecasting reputation, size of the news, forecast loss, book-to-market, horizon, width, year and industry effects.

## Outcome variable and horizon

Incidence and content of updates within the fiscal year; analyst consensus revision around each forecast (forecasts from 90 days before to 30 days after).

## Result

All labelled **empirical finding**.

- Prevalence: the share of annual forecasts followed by at least one update rises from about 10% in 1996 to nearly 90% after 2006. Updating every quarter appears after 2001 and covers more than half of annual forecasters from 2006. In the regression sample, 88.2% update at least once and 59.5% update every quarter.
- Routine, not news: updating every quarter last year raises the probability of doing so this year by 28.9 points (z = 17.02). Variables measuring a need to realign expectations do not predict updating, and larger analyst error predicts less of it.
- Repeats are common: about 53% of updates keep the previous range width, and about half of those also keep the midpoint.
- Regular updaters (about 4,800 firm-years), first, second and third update: midpoint unchanged in 43%, 29%, 18%; raised in 38%, 44%, 49%; lowered in 19%, 27%, 33%. Width unchanged in 71%, 55%, 34%. Raises outnumber cuts at the 1% level in each position.
- Firms with a single update (about 1,060 firm-years): unchanged 27%, raised 30%, lowered 43%. The direction mix reverses with the firm's routine.
- Ranges narrow late: the mean width for regular updaters goes from $0.12 at the first forecast to $0.07 at the last.
- Regular updaters start close to unbiased (median first-forecast error slightly pessimistic), where forecasts that are never updated are optimistic on average.
- Analysts respond to updates, less than to the initial forecast and less with each update (interaction coefficients −0.103, −0.133, −0.258; t = −3.58, −3.19, −3.77). The total response stays significant for the pooled sample; for regular updaters' last update it does not (F = 2.19).
- Untabulated in the paper: analyst dispersion falls around updates even when width and midpoint are unchanged.

## Look-ahead and memorisation

Not addressed; no model is trained. One design choice uses hindsight: the midpoint is expressed relative to realised earnings, which is fine for describing bias but is not a point-in-time quantity. The up/down/unchanged tabulation compares consecutive forecasts and needs no hindsight.

## What it settles for us

- **First benchmark is guidance revision: supported.** Updating annual guidance each quarter is the dominant practice among guiders since the mid-2000s, so consecutive press releases will usually contain a comparable pair. Updates carry information for analysts, including confirmations.
- **Class balance: a planning input.** For annual EPS guidance, expect about a quarter of updates to repeat both width and midpoint (53% keep the width, about half of those the midpoint), with the midpoint unchanged in 18 to 43% depending on the position in the year. "Raised" is ahead of "lowered" among regular updaters and the reverse among one-off updaters. "Narrowed" is frequent late in the year and co-occurs with midpoint moves, so the class scheme needs a rule for a range that both narrows and shifts. These rates are for 1996–2011 and for EPS only; the WP2 census should report the same table for the post-cutoff sample.
- **Stratify by routine.** Whether the firm updates every quarter predicts both the label and how much the update matters. Record it per company, and do not let the test set be dominated by regular updaters repeating a range.
- **"Maintained" is not a null label.** Reaffirmations reduce analyst dispersion, so a model that skips them loses information.
- **Do not redo:** whether analysts react to guidance updates.
- **Gap:** the paper works from a commercial database of numeric EPS records. It drops forecasts that are neither a point nor a closed range and says nothing about wording, about qualitative steers such as "toward the low end", or about non-EPS metrics. Classifying the change from the press-release text is not attempted.

## Limits

- Working-paper numbers from 2015; the published article was not read in full.
- First Call coverage is incomplete and the database was discontinued; the sample ends in fiscal 2011.
- Annual EPS only. Quarterly guidance and other metrics are outside the paper.
- Consequences are measured on analysts, not prices or fundamentals.
