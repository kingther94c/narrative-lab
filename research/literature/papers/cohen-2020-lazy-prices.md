# Lazy Prices

- **Citation:** Lauren Cohen, Christopher Malloy and Quoc Nguyen (2020), *Journal of Finance* 75(3), 1371–1415. Version read: NBER Working Paper 25084 (September 2018, revised March 2019), full text. The published abstract was checked on EconPapers.
- **Link:** <https://www.nber.org/papers/w25084> (full text: <https://www.nber.org/system/files/working_papers/w25084/w25084.pdf>). Published version: <https://doi.org/10.1111/jofi.12885>; abstract at <https://econpapers.repec.org/RePEc:bla:jfinan:v:75:y:2020:i:3:p:1371-1415>.
- **Stream:** 01, financial text analysis before LLMs
- **Verified against source:** yes, 2026-11-12. Every number below is from the working paper and was not re-checked against the journal version.

## Question

When a firm changes the wording of its 10-K or 10-Q relative to the comparable report a year earlier, does the change predict the firm's future returns and operations, and do prices react when the report is filed?

## Data

- Text source: all complete 10-K, 10-K405, 10-KSB and 10-Q filings on EDGAR, 1995 to 2014. Main text only: tables (more than 15% numeric characters), exhibits, HTML and XBRL are removed.
- Sample (Table I): 86,965 10-Ks (mean 44,509 words) and 258,271 10-Qs (mean 15,806 words); 327,130 filings with a similarity score.
- Other data: CRSP monthly returns, Compustat, I/B/E/S, the Loughran–McDonald word lists (to sign the changes), bankruptcy events from Capital IQ, and the SEC's EDGAR download logs (attention).
- Universe: all US filers that match to CRSP. The paper does not say how delisting returns are treated, and delisted firms are not discussed.

## Method

- Four similarity scores between a filing and the same firm's comparable filing one year earlier (10-K against the prior 10-K; 10-Q against the same fiscal quarter's 10-Q): cosine, Jaccard, minimum edit distance, and a diff-based score (words added, deleted or changed, scaled by document length). All run from 0 to 1; higher means less change.
- The year-over-year pairing is deliberate: the authors argue that seasonality makes the prior quarter's report a poor comparison.
- Calendar-time quintile portfolios. A stock enters in the month after its filing becomes public and is held for three months. Q1 holds the largest changers, Q5 the smallest.
- Monthly Fama–MacBeth regressions of firm returns on similarity plus size, log book-to-market, last month's return, 12-month momentum and standardised unexpected earnings (SUE). Robustness adds accruals, investment, gross profitability, free cash flow, document length and its change, and dictionary tone change.

## Outcome variable and horizon

- Monthly stock returns over the three-month holding period; event-time returns out to six months in the figures, and the text reports continued drift to 18 months.
- Operating income, net income and sales over lagged assets, two quarters ahead.
- Next-quarter SUE, the number of 8-Ks in the next six months, and a bankruptcy indicator for the next year.
- Announcement-window returns from ten days before to ten days after the filing.

## Result

All labelled **empirical finding** unless stated.

- Long Q5, short Q1, value-weighted, five-factor alpha (market, size, value, momentum, liquidity), percent per month: 0.34 (t = 2.53) cosine, 0.46 (t = 3.44) Jaccard, 0.37 (t = 2.45) edit distance, 0.51 (t = 3.14) diff-based. The largest three-factor alpha is 0.58 (t = 3.59). Equal-weighted five-factor alphas run from 0.27 to 0.45 (t from 3.01 to 5.46).
- Fama–MacBeth coefficient on similarity with size, book-to-market, past returns and SUE in the regression: Jaccard 0.59 (t = 3.41), cosine 0.37 (t = 2.18), edit distance 0.29 (t = 2.00), diff-based 0.03 (t = 2.11). The authors translate the last into 36 basis points a month per standard deviation of similarity.
- Incremental to tone: with the change in Loughran–McDonald negative and positive word shares in the regression, the Jaccard coefficient is 0.58 (t = 3.29). The tone changes also predict returns in that regression: negative −0.29 (t = −5.83), positive 0.18 (t = 3.58). With document length and its change included, Jaccard stays at 0.58 (t = 3.82).
- No announcement effect: returns around the filing date are economically and statistically zero in the full sample. The drift arrives later.
- Sign: 86% of the changes are negative in sentiment; the positive 14% predict positive returns.
- By section: changes in Risk Factors give the largest spread, up to 188 basis points a month (t = 2.76); MD&A changes give 11 to 22. The authors call the section results suggestive, not definitive, because they vary across specifications.
- Real outcomes: lower similarity predicts lower operating income, net income and sales two quarters ahead (Jaccard on operating income over assets: 0.68, t = 10.68, with month, industry and firm fixed effects). It also predicts lower next-quarter SUE and, for two of the four measures at the 5% level, more bankruptcies in the next year. The paper itself calls the bankruptcy and 8-K evidence suggestive.
- Mechanism: the return spread is concentrated in the roughly two-thirds of filings with no explicit comparison to the prior period, and is about 22% weaker per standard deviation of readers who download both years' filings.
- The only sequential-quarter test reported (Risk Factors sections of consecutive 10-Qs, appendix) gives a value-weighted five-factor alpha of 1.13% a month (t = 2.30).

## Look-ahead and memorisation

No pretrained model is used, so memorisation does not arise. On timing, the signal is dated by the public filing date and trading starts the following month; quintile breakpoints come from the earlier distribution of scores. The sample ends in 2014 and the paper circulated from 2018, so decay after publication is untested. The Loughran–McDonald lists used to sign changes were built on 1994–2008 10-Ks, which overlaps the sample; this touches only the sentiment split.

## What it settles for us

- **Unit of analysis: supported.** A pair of documents from the same firm carries information that a single document's level features do not, and the pair is what investors under-process. The project's "pair of consecutive outlook passages" follows the same logic.
- **Pairing rule: a question for the design.** The paper pairs year over year to remove seasonality. Our default pairs consecutive quarters. Guidance for a fiscal year is naturally sequential, but any "narrative change" item should be checked against the same quarter a year earlier.
- **Baseline to beat.** Jaccard or cosine similarity of the pair, plus the change in dictionary tone, costs nothing to compute on EDGAR text. An LLM "narrative change" feature has to add to these, not just to a levels baseline.
- **Text source: supported** for 10-K and 10-Q. The paper says nothing about earnings press releases or guidance.
- **Do not redo:** the similarity-to-returns test. Returns are deferred in our plan anyway; the real-outcome results support treating association with hard events as an exploratory endpoint.
- **Reusable:** the four similarity definitions; the parsing recipe (the paper points to the Notre Dame SRAF "stage one" 10-X parse); the comparative-phrase idea for a difficulty stratum.

## Limits

- Working-paper numbers; the journal version may differ.
- The measure is unsigned. Direction comes from a dictionary applied to the changed text.
- Section-level results are unstable by the authors' own account.
- Treatment of delisting returns is not stated, which matters for a short leg that loads on firms heading for bad news.
- Table numbering in the working paper is inconsistent between text and tables (the "real effects" table is cited as X and printed as IX).
