# Can Investors Detect Managers' Lack of Spontaneity? Adherence to Pre-determined Scripts during Earnings Conference Calls

- **Citation:** Joshua Lee (2016). The Accounting Review 91(1), January 2016 (volume, issue and
  month from the manuscript cover; page range not seen). Version read: the AAA "Online Early"
  accepted manuscript (submitted April 2014, accepted April 2015), before copy-editing.
- **Link:** https://aaahq.org/Portals/0/newsroom/Can%20Investors%20Detect%20Managers_%20Lack%20of%20Spontaneity%20article.pdf
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against the full accepted manuscript (text
  extracted from the PDF by script).

## Question
When managers answer analysts' questions from a script, does the market read it as bad news, and
does it predict worse unexpected future performance?

## Data
- Earnings calls from Factiva FD Wire, 2002 to 2011, nonfinancial Compustat firms matched by name;
  "earnings" in the call title and within two days of the announcement.
- 40,820 calls for 2,863 firms after requiring Compustat, CRSP and I/B/E/S data and at least 200
  words by the spokesman manager in both the prepared remarks and the Q&A.
- Not restricted to large caps. Delisted firms: not discussed.

## Method
- **Scripting measure.** Split each call into prepared remarks (MD) and Q&A by keywords; pick the
  "spokesman manager" (CEO or CFO with most words). Count the manager's function words (LIWC list:
  articles, conjunctions, pronouns, prepositions, auxiliary verbs) in each part. Scripting = cosine
  similarity of the two vectors, residualised on the lengths of both parts (with squares and
  cubes), ranked into deciles scaled 0 to 1. High = answers sound like the prepared remarks.
- **Abnormal scripting.** The same measure minus the manager's average over the previous four
  quarters, to remove a stable personal style.
- **Validation.** (1) Randomisation: a manager's Q&A (MD) vector in one quarter is most similar to
  the same manager's other quarters in 79.8% (87.0%) of calls, against nine random managers (10%
  by chance). (2) Prepared remarks and Q&A differ in style: the actual manager's Q&A ranks first
  against his own MD only 20.3% of the time. (3) Reading top and bottom deciles: spontaneous
  answers start more sentences with "and", "so" or "but" (abnormal share 18.7% in the bottom
  decile against 9.7% in the top) and have more mid-sentence pauses marked "--" (0.091 against
  0.057 per sentence). No human labels of scriptedness.
- **Tests.** OLS with manager and year-quarter fixed effects, clustered by firm. Controls include
  current earnings surprise, size, dispersion, volatility, guidance and guidance surprise, net
  tone (Loughran-McDonald), a non-response indicator (key phrases of refusal), word counts and
  tenure.

## Outcome variable and horizon
- Unexpected earnings: actual EPS minus the median pre-announcement analyst forecast, scaled by
  price, for quarter t+1, t+2 and the sum of the two.
- CAR[0,1] at the call and CAR[2,92]; revision of the t+1 consensus within 30 days; change in
  bid-ask spread; probability of guiding next-quarter EPS.

## Result
All empirical findings.
- **Future unexpected earnings (Table 4).** Top against bottom decile of scripting: -0.082 for
  t+1, -0.099 for t+2, -0.195 for t+1 and t+2 (5%, 5% and 1% levels). The author scales these to
  29.8%, 28.3% and 34.3% of the median absolute unexpected earnings. Quintile means of t+1
  unexpected earnings: -0.238 (least scripted) against -0.319 (most scripted).
- **Robust to the within-manager measure.** Abnormal scripting: -0.054, -0.061 and -0.126 (5%, 5%,
  1%). So the signal is a change from the manager's own habit, not only a trait.
- **Analysts.** The t+1 consensus falls more after scripted calls: -0.048 (1% level), 32.7% of
  the median absolute revision.
- **Market.** CAR[0,1] -0.006 (1% level; 13.0% of the median absolute CAR). CAR[2,92] -0.009,
  significant only at 10%; t-statistics fall to about -1.6 when favourable-analyst participation
  is added.
- **Less information, not more.** Spreads widen (+0.015, 5% level; also +0.008 for abnormal
  scripting). Scripted firms are 20.2% less likely to guide next-quarter EPS, but this is not
  robust to abnormal scripting.
- **Separate channels.** Scripting is uncorrelated with refusals to answer (correlation -0.002)
  and with the share of favourable analysts called on (0.008). Correlations with vocal affect
  (Mayew and Venkatachalam data, 1,513 overlapping calls) are insignificant.
- Positive call tone and positive guidance also predict higher unexpected earnings in the same
  regressions.

## Look-ahead and memorisation
Not addressed as such. The length adjustment and the decile ranks use the full 2002-2011 sample.
The abnormal measure uses only the previous four quarters and gives the same sign, which is the
closer to point-in-time version. No LLM.

## What it settles for us
- **Scripted Q&A is a tested predictor of unexpected earnings one and two quarters ahead
  (supports a checklist item).** It is incremental to tone, guidance, refusals and analysts'
  pre-announcement forecasts.
- **Needs the full call.** The measure compares the Q&A with the prepared remarks; it cannot be
  computed from either part or from a press release.
- **Reader cues (hypothesis).** A model cannot count function words reliably by eye, but the
  paper's own reading gives visible cues: complete, polished answers; few sentences starting with
  "and", "so", "but"; few broken sentences; answers that reuse prepared phrasing. Transcript
  vendors differ in whether they keep "--" and false starts, so these cues depend on the source.
- **Re-identification warning (empirical finding).** Function-word counts alone pick out the
  speaking manager among ten in 79.8% to 87.0% of calls. Style survives name removal; see the
  stream summary.
- **Not about revenue.** The outcome is earnings surprises.

## Limits
- The author cannot rule out that firms simply anticipate questions better before bad news.
- One spokesman per call; other executives' answers are ignored.
- Effects are scaled to medians of absolute values, which flatters their size; the paper gives no
  R-squared gain or out-of-sample test.
- Broad sample, not S&P 500.
