# Hyperbole or Reality? Investor Response to Extreme Language in Earnings Conference Calls

- **Citation:** Khrystyna Bochkay, Jeffrey Hales and Sudheer Chava (2020). The Accounting Review
  95(2), 31-60. Version read: the typeset journal article posted by the AAA newsroom (Allen Press
  proof dated 18 December 2019, 32 pages). The online appendix was not opened.
- **Link:** https://aaahq.org/portals/0/newsroom/2020/hyperbole%20or%20reality%20article.pdf
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against the full article (text extracted from the
  PDF by script). The extraction drops some minus signs in the tables (for example NegExtreme in
  Table 10); signs below follow the text, which states the direction.

## Question
Does the extremity of managers' words, beyond their tone, move markets and analysts, and does it
carry information about future operating performance?

## Data
- All earnings call transcripts on Seeking Alpha for 2006 to 2015, downloaded as HTML: 60,940
  calls; 45,056 matched to Compustat; 35,155 firm-quarters after data filters and at least 1,000
  words (36,171 observations in the future-performance table).
- About 80% of calls are on the announcement day, 18% the day after.
- Broad US sample, not S&P 500 only. Delisted firms: not discussed.

## Method
- **Dictionary.** All adjectives, nouns and verbs and their phrases from the 60,940 calls, plus
  synonyms: 23,355 entries. Each rated by five Amazon Mechanical Turk Masters on -5 (extremely
  negative) to +5 (extremely positive) for "an earnings announcement". Intra-class correlation 88%;
  after dropping entries with mean absolute rating below 1, 13,513 entries, ICC 90.4%. A check
  with business graduate students (200 words, ten ratings each) correlates 94.4% with MTurk.
- **Measures.** Extreme = absolute rating 4 or 5; moderate = 1 to 3; negation flips and shrinks
  ratings. SignedExtreme = extreme positive minus extreme negative share; SignedModerate likewise.
  Extremity is only weakly related to word rarity (correlation with idf 4.8%).
- **Tests.** OLS with year-quarter fixed effects, two-way clustering by firm and year-quarter.
  Controls: earnings surprise and loss indicators, ROA, past changes in ROA and sales, accruals,
  earnings volatility, size, market-to-book, leverage, Z-score, pre-announcement return, return
  volatility, analyst following, segments, firm age, and call content (forward-looking, risk,
  uncertainty and number counts).

## Outcome variable and horizon
- Change in earnings and change in sales from quarter q to q+4, scaled by current total assets.
- BHAR and abnormal volume over [0,2]; analyst forecast revisions after the call.

## Result
All empirical findings.
- **Future sales and earnings (Table 10, with controls).** SignedExtreme: +1.457 on the change in
  sales (t = 6.31) and +0.766 on the change in ROA (t = 6.77). One SD of SignedExtreme raises the
  four-quarter change in sales by 0.0038 of assets and in earnings by 0.0020. The medians are
  0.0075 (sales) and 0.0007 (earnings); the SD of the sales change is 0.0591, so one SD of
  extremity is about 6% of an SD of the sales change. SignedModerate: +0.114 on sales (t = 2.04),
  0.002 on ROA (not significant). Extreme equals moderate is rejected (F = 27.8 sales, 38.7
  earnings).
- **Both directions (Table 10, columns with controls).** Sales change: extreme positive +1.119
  (t = 4.59), extreme negative -2.979 (t = -4.22), moderate negative -0.571 (t = -2.90), moderate
  positive not significant. ROA change: extreme positive +0.705 (t = 6.47), extreme negative -1.503
  (t = -2.96), moderate words not significant. Negative language, extreme or moderate, matters
  more for sales than moderate positive language.
- **Market.** One SD of SignedExtreme: +0.87% BHAR[0,2], against +0.28% for SignedModerate;
  median absolute reaction 4.33%. No significant drift or reversal over the next 60 days.
- **Prepared remarks and Q&A (online appendix, not read).** The text says market reactions to
  extreme language are stronger than to moderate language in both sections, that in the Q&A both
  managers' and analysts' extremity matter, and (footnote 30) that the future-performance results
  hold when the call is split into prepared remarks and Q&A.
- Results hold with "abnormal" extremity estimated as in Huang, Teoh and Zhang (2014) and with
  firm fixed effects (footnote 30).

## Look-ahead and memorisation
Not addressed as such. The dictionary was built from all 2006-2015 calls, but the ratings use no
outcome data, so it is not fitted to outcomes. All regressions are in sample. No LLM.

## What it settles for us
- **The only study in this pass with sales as the outcome (supports a checklist item).** Unhedged
  superlatives and stark negatives in the call predict the next year's sales change beyond the
  current quarter's numbers, the earnings surprise and standard text controls. Moderate positive
  language carries nothing once controls are in; moderate negative language still predicts lower
  sales.
- **Works on prepared remarks (supports, from footnote 30 only).** A transcript-free design that
  sees only prepared remarks or management quotes could test this.
- **Human-rated lexicon (reusable).** The rating protocol (five raters, -5 to +5, ICC reported) is
  a template for validating an LLM extremity score.
- **Caveat for our target.** The outcome is a level change in sales over four quarters scaled by
  assets, not acceleration of year-over-year growth.

## Limits
- Not controlled for the press release's language or for analysts' forecasts of sales.
- Effects are small relative to the variance of sales changes.
- Section-level results are in an appendix that was not read.
- Seeking Alpha transcripts; the data audit (section 2) found its terms forbid redistribution.
