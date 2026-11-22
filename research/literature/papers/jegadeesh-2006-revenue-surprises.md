# Revenue Surprises and Stock Returns

- **Citation:** Jegadeesh, N. and Livnat, J. (2006). Journal of Accounting and Economics 41(1-2),
  147-171. Version read: working paper "This Version: July 2004" (the JAE submission), hosted on
  the second author's NYU page; text extracted by script. The published version was not opened.
- **Link:** https://doi.org/10.1016/j.jacceco.2005.10.003 (draft:
  https://pages.stern.nyu.edu/~jlivnat/JAE%20submission.pdf)
- **Stream:** 10, accounting signals
- **Verified against source:** yes, 2026-11-22, against the July 2004 draft.

## Question

Do revenue surprises carry information about future earnings growth beyond earnings surprises, and
do prices and analysts absorb it on time?

## Data

Compustat quarterly data, CRSP returns, I/B/E/S forecasts, 1987 to 2003. Financials and utilities
excluded; price at least $5. 165,708 firm-quarters (116,573 small, 49,135 large, split at the NYSE
median). A firm needs 12 prior quarters. Delisted firms: not stated.

## Method

SUE: seasonal change in quarterly EPS less drift, scaled by the standard deviation of the past
eight seasonal differences (a seasonal random walk with drift; chosen because announcement returns
track it better than an AR(1) model, citing Freeman and Tse). SURGE: the same for quarterly revenue
per share. Fama-MacBeth regressions over six-month cohorts:
SUE(t) on SURGE(t-1..t-4) and SUE(t-1..t-4) (Table 3). Announcement-window and post-announcement
returns by SURGE and SUE quintiles. Analyst revisions and errors on past SURGE and SUE.

## Outcome variable and horizon

Next quarter's SUE (earnings growth); returns over the next quarters; analysts' errors for one to
several quarters ahead.

## Result

- **Empirical finding.** Revenue surprises predict next-quarter earnings growth beyond four lags of
  earnings surprises. Full sample: SURGE(t-1) 0.0610 (significant), SURGE(t-2) -0.0121
  (significant), SURGE(t-3) -0.0068, SURGE(t-4) 0.0012. SUE lags: 0.3026, 0.1013, 0.0576, -0.3032
  (Table 3). The authors read only the immediately preceding revenue surprise as informative; the
  lag-2 coefficient is small but marked significant in the table.
- **Empirical finding.** The fourth-lag SUE coefficient is negative (-0.30): this year's seasonal
  earnings surprise partly reverses in the same quarter next year. This is the seasonal reversal
  behind a "comparison base" effect (our reading).
- **Empirical finding.** The revenue-to-earnings link is stronger for growth firms (Table 3 split).
- **Empirical finding.** Prices react to both surprises at the announcement and keep drifting after
  large revenue surprises when earnings surprises are held fixed; there is no post-announcement
  drift after revenue surprises for large firms (conclusion).
- **Empirical finding.** Analysts revise for revenue surprises but slowly; their later errors load
  positively on past SURGE and SUE (Table 10); "analysts take up to six months" to incorporate
  revenue surprises.

## Look-ahead and memorisation

Quintile cut-offs come from the previous six months' distribution, so portfolio assignment is
point in time. Compustat quarterly data are used as restated by the vendor at download (not
discussed). No language model.

## What it settles for us

- For an EPS label: an earnings beat that comes with a revenue beat is more persistent than one
  driven by costs. A PM skill can ask "is the beat revenue-led or cost-led?".
- For S2's revenue label: this paper does not test whether a revenue surprise predicts next
  quarter's revenue growth; that remains open in the sources read.
- The seasonal-reversal coefficient supports treating the comparison base as the baseline that any
  new signal must beat, not as a model insight.
- For S&P 500 names the market effect is weaker (no drift for large firms), so expect smaller
  incremental value of this kind of signal in our universe.

## Limits

Draft version, not the published one; numbers may have changed. Earnings, not revenue, is the
outcome. 1987 to 2003, mostly small firms by count.
