# When Is a Liability Not a Liability? Textual Analysis, Dictionaries, and 10-Ks

- **Citation:** Tim Loughran and Bill McDonald (2011), *Journal of Finance* 66(1), 35–65. Version read: the published article, full text (copy hosted by the University of Technology Sydney).
- **Link:** <https://www.uts.edu.au/globalassets/sites/default/files/adg_cons2015_loughran-mcdonald-je-2011.pdf>. Index entry: <https://econpapers.repec.org/RePEc:bla:jfinan:v:66:y:2011:i:1:p:35-65>.
- **Stream:** 01, financial text analysis before LLMs
- **Verified against source:** yes, 2026-11-12, against the published text.

## Question

Do general-purpose negative word lists measure tone in financial filings, and does a list built for finance relate better to market and firm outcomes?

## Data

- Text source: 10-K and 10-K405 filings on EDGAR, 1994 to 2008, excluding amendments. Tables and exhibits are removed.
- Sample: 50,115 firm-year filings from 8,341 firms, out of 121,217 downloaded. An MD&A-only subsample has 37,287 filings.
- Filters: a CRSP match; NYSE, Amex or NASDAQ listing; price of at least $3 before filing; at least 60 trading days in the year before and the year after filing; more than 2,000 words.
- Delisted firms: not discussed. The requirement of 60 trading days after filing excludes firms that stop trading soon after they file.
- Event samples: 585 firm-years tied to Rule 10b-5 class actions alleging accounting fraud (among 35,992 filings to September 2004) and 708 material-weakness disclosures (among 17,143 filings, 2001 to 2005).

## Method

- Bag of words. Tone is the share of a filing's words that appear on a list, either as a raw proportion or with tf.idf term weights.
- Lists compared: the Harvard General Inquirer negative list with inflections (H4N-Inf, 4,187 words) and the authors' finance lists: negative (Fin-Neg, 2,337 words), positive (353), uncertainty (285), litigious (731), strong modal (19) and weak modal (27).
- The finance lists were built by reading every word that occurs in at least 5% of the 10-Ks and judging its usual meaning in filings. The authors chose judgement over fitting words to returns, on the argument that a short fitted list would be easy for managers to avoid.
- Fama–MacBeth regressions over 60 quarters with Newey–West errors. Controls: log size, log book-to-market, log share turnover, pre-filing Fama–French alpha, institutional ownership, a NASDAQ indicator and 48 industry dummies. Logit for the fraud and material-weakness samples.

## Outcome variable and horizon

- Filing-period excess return, days 0 to 3.
- Abnormal volume over the same four days.
- Return volatility over the 252 days after filing.
- Analyst-based earnings surprise for the quarter reported within three months of the filing.
- A 10b-5 suit in the year after filing; a material-weakness disclosure within 18 months.
- A long-short portfolio on the prior year's negative-word share, held 12 months.

## Result

All labelled **empirical finding**.

- Misclassification: 73.8% of the Harvard negative word count in 10-Ks comes from words that are not negative in a financial context (tax, cost, liability, board and the like).
- Filing returns, raw proportions: Fin-Neg −19.54 (t = −2.64); the Harvard list −7.42 (t = −1.35). With tf.idf weights the two lists are both significant and indistinguishable (t = −3.16 and −3.11).
- Explanatory power is small: average R² of 2.4 to 2.6% with all controls. The authors say plainly that textual analysis is not the key to returns. The result needs the four-day window; nothing is significant over days 0 to 1.
- MD&A alone is not better than the whole filing: insignificant with raw proportions, marginal with term weights (t = −1.96).
- No return predictability: the four-factor alpha of the long-short portfolio on negative-word share is positive but not significant.
- Volatility is where the lists do best: every list except litigious is positively related to post-filing volatility (Fin-Neg t = 12.59).
- Earnings surprise: more negative words in the 10-K go with a *higher* subsequent surprise (Fin-Neg 2.68, t = 2.41), the opposite sign to news-based tone. The authors suggest managers may be lowering expectations.
- Fraud and material weakness: with raw proportions no list predicts the fraud suits; with term weights Fin-Neg, uncertainty and litigious do. Fin-Neg predicts material weakness under both weightings (z = 3.95 and 5.10).
- Changes versus levels: using normalised differences from the firm's own history leaves signs and significance unchanged; the authors conclude that differencing does not reduce the noise.

## Look-ahead and memorisation

Not addressed in those terms. Two things to record. The word lists were compiled from the same 1994–2008 filings on which they are tested, although by judgement and not by fit to outcomes. And the sample filter looks forward (trading in the year after filing). No pretrained model is involved.

## What it settles for us

- **Tone deferred: supported.** Dictionary tone in periodic filings is a weak signal: small R², no tradable return spread, and a sign for earnings surprise that runs against intuition because the author of the text has incentives. This is a poor first target for a benchmark that needs a clear ground truth. It does not show that tone is uninformative, only that the level of a word count is a noisy measure of it.
- **Baseline to beat.** Any tone or confidence feature added later must beat the Fin-Neg share (with tf.idf weights) and the uncertainty and modal lists, with size, book-to-market, turnover, prior alpha and industry as controls. The lists are public at the Notre Dame Software Repository for Accounting and Finance.
- **Text source.** The whole 10-K does as well as the MD&A, so there is no evidence here for restricting filings to the MD&A when computing lexical baselines.
- **Changes versus levels.** This paper finds differencing a word share adds nothing, where Cohen, Malloy and Nguyen find that changes in the text itself add a great deal. The two fit together: what matters is which text changed, not the change in a tone total.
- **Failure outcomes.** Term-weighted negative, uncertainty and litigious shares are associated with later fraud suits and material weaknesses. This is a ready lexical baseline for the exploratory hard-event endpoint.
- **Do not redo:** the dictionary-tone-to-returns test on 10-Ks.

## Limits

- 10-Ks only; earnings press releases and 10-Qs are not tested. The authors expect the lists to transfer and give only correlations for two other settings.
- Word counts ignore context and negation (handled for positive words only).
- Coefficients on raw proportions are hard to compare across lists of different sizes.
- The event samples are small and end in 2004 to 2005.
