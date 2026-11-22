# Core Earnings: New Data and Evidence

- **Citation:** Rouen, E., So, E. C. and Wang, C. C. Y. (2021). Journal of Financial Economics
  142(3), 1068-1091. Version read: accepted manuscript dated November 2020, Harvard DASH
  open-access copy (text extracted by script; tables read through the prose that reports them).
- **Link:** https://doi.org/10.1016/j.jfineco.2021.04.025 (open copy:
  https://nrs.harvard.edu/URN-3:HUL.INSTREPOS:37373901)
- **Stream:** 10, accounting signals
- **Verified against source:** yes, 2026-11-22, against the full text of the DASH manuscript.

## Question

How large and how frequent are the non-core (transitory or ancillary) parts of GAAP earnings, where
in the 10-K are they disclosed, does removing them give a more persistent earnings measure that
forecasts future performance, and do analysts and prices absorb them on time?

## Data

New Constructs (a research firm) classifies every income-statement-related number in the 10-K,
including footnotes, MD&A and the cash flow statement. More than 60,000 firm-years, 1998 to 2017,
US listed firms. Delisted firms: not stated in the parts read.

## Method

Core Earnings = net income plus net expenses from eight categories: acquisitions, currency,
discontinued operations, legal or regulatory events, pensions, restructuring, items labelled
"other" on the income statement, and other gains and losses the data firm judges transitory or
ancillary. Persistence regressions of next-year performance on this year's, with year fixed
effects; forecast regressions of next-year net income on core earnings and alternatives (net
income, CFO, Compustat IBSPI, OIADP, OPEPS, street earnings); analyst-revision and return tests.

## Outcome variable and horizon

Next-year net income (and CFO, IBSPI, OIADP, OPE, street earnings); one to five years. Analyst
revisions over the 12 months after the 10-K filing. Twelve-month returns.

## Result

- **Empirical finding.** Non-core items are common and large: the average 10-K has six (1998) to
  eight (2017) of them; in total they average 19% of average net income; about half by count or
  value are disclosed off the face of the income statement (footnotes, MD&A, cash flow statement).
- **Empirical finding.** Cross-sectional persistence (Table 3, Panel A): net income 0.637, Core
  Earnings 0.810, Total Adjustments 0.178. CFO 0.785 and total accruals 0.459. Compustat OIADP is
  the most persistent (0.861) but its own adjustments persist at 0.612, so it leaves recurring
  items out; OPEPS behaves most like Core Earnings.
- **Empirical finding.** Forecasting: the time-series average mean squared error of a next-year
  net income forecast is 20% lower using Core Earnings than using net income. Core Earnings is
  incremental to net income, CFO, IBSPI, OIADP and OPE (largest coefficient, significant at 1%,
  Table 4) and to street earnings (5%, Table 7), over one to five years.
- **Empirical finding.** The adjustments' predictive content comes from items on the income
  statement, in footnotes and in MD&A; cash-flow-statement items are significant only for future
  CFO. Seven of eight economic categories carry it; currency and company-defined "other" are weak.
  Income-decreasing adjustments (net gains) are generally less persistent.
- **Empirical finding.** Total Adjustments predict upward analyst EPS revisions over the next 12
  months (5% level); the footnote items have the largest and most significant coefficient (Table
  8). Value-weighted 12-month raw returns: 11.9% for the top decile of adjustments against 3.5% for
  the bottom (8.4 points); the spread sits mostly in the bottom decile, firms whose GAAP earnings
  are inflated by large non-recurring gains (Table 9).

## Look-ahead and memorisation

The data firm parsed part of the early years later; from 2008 data were parsed "on a real-time
going-forward basis" with no back-filling, and the main inferences hold on 2008 to 2017 (online
appendix). The paper also documents hindsight in Compustat itself: under a "three-year rule"
Compustat decides whether an item is non-recurring with later years in view, and under a "majority
rule" it leaves special items blank when it cannot place most of them on a line (examples: GM
2011-2013, Ford 2006). Memorisation is not relevant (no language model).

## What it settles for us

- Supports asking the PM, for an EPS-type label, to separate recurring from one-off items, and to
  look past the income statement: half the non-core value sits in notes and MD&A that a press
  release may not carry.
- Gives a concrete eight-category list for a "one-off" field in a template, and a validation test
  for any LLM-made core-earnings figure: its adjustments should have persistence near 0.18 and the
  core figure near 0.8 (annual, all firms).
- Point-in-time warning for code: do not use Compustat special items or adjusted fields as
  features; they can carry later knowledge. Use as-filed XBRL or the release itself.
- Bears on earnings persistence only. It says nothing about next-quarter revenue.

## Limits

Annual data and horizons; all listed firms, not S&P 500 alone. The classification is a vendor's
judgement. The analyst and return effects are averages that may be smaller for large firms (not
split in the parts read). Online appendix tables not read.
