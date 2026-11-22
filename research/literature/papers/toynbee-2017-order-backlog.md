# Implications of Disclosing Order Backlog

- **Citation:** Toynbee, S. M. (2017). PhD dissertation, Foster School of Business, University of
  Washington (chair S. E. McVay). Version read: the deposited dissertation (83 pages, text extracted
  by script).
- **Link:** http://hdl.handle.net/1773/39889
- **Stream:** 10, accounting signals
- **Verified against source:** yes, 2026-11-22, against the full text (main tests and Appendix E).
  A dissertation, not peer-reviewed in this form.

## Question

Does disclosing the dollar amount of order backlog in the 10-K (Regulation S-K, Item 1) change how
much future earnings are priced, investment efficiency, and the persistence of profitability? As a
side test: how well does backlog predict next year's sales compared with inventory?

## Data

Compustat and CRSP, fiscal 1996 to 2014, firms in 15 manufacturing industries where 37.8% to 95.3%
of firms disclose backlog. Price at least $1; returns truncated at the 1st and 99th percentiles.
Propensity-matched sample of 13,742 firm-years. Delisted firms: not stated.

## Method

For the side test (Appendix E, Table E.2): pooled OLS of next-year percentage sales growth on the
percentage change in backlog intensity (backlog over sales), on the percentage change in inventory
over sales, and on both; split by make-to-stock (finished goods over half of inventory) or not;
standard errors clustered by firm and year; Vuong test. Main tests: future earnings response
coefficients, investment efficiency, persistence of RNOA by backlog growth decile.

## Outcome variable and horizon

Sales growth from year t to t+1; next-year earnings; RNOA persistence. Annual.

## Result

- **Empirical finding.** Backlog growth alone explains 9.9% of the variance of next-year sales
  growth (coefficient 0.141, t = 13.25, n = 6,761); inventory growth alone 2.3% (0.136, t = 6.06);
  both together 10.5%, each still significant (0.132 and 0.070). Make-to-order firms: 10.7% against
  2.2%. Make-to-stock firms: 6.8% against 2.7%, and the difference is not significant (Vuong
  p = 0.061; F-test p = 0.838) (Table E.2).
- **Empirical finding.** The change in backlog adds to next-year earnings beyond current earnings
  (0.017, t = 3.99; with cash flow and accruals split, 0.020, t = 8.66) (Table E.3).
- **Empirical finding.** Persistence of operating profitability is 11.1% higher in the top decile
  of backlog-intensity growth than the bottom (0.732 against 0.659).
- **Verified fact.** Only 27.6% of disclosers report non-zero deferred revenue, and backlog exceeds
  deferred revenue for 93.3% of those: backlog covers far more orders than those already paid for.
- **Empirical finding (main thesis).** Disclosers have higher forward earnings response
  coefficients and investment efficiency, concentrated in make-to-order firms.

## Look-ahead and memorisation

Not addressed. Annual Compustat data as downloaded. No language model.

## What it settles for us

- The clearest number found for backlog as a revenue lead: about 10% of the variance of next-year
  sales growth in manufacturers. Its regressions have no control for current or past sales growth,
  so they do not show that backlog adds to a past-growth baseline such as EXP-0034's. That test is
  ours to run.
- Supports a template field "backlog, book-to-bill or remaining performance obligations, and their
  change", with more weight for make-to-order businesses (industrial, aerospace, defence).
- Backlog is broader than deferred revenue; under ASC 606 the comparable disclosure is remaining
  performance obligations (the dissertation anticipates this).

## Limits

Annual horizon; manufacturers only; no past-growth control in the sales test; a dissertation.
