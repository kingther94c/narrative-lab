# The Persistence and Pricing of the Cash Component of Earnings

- **Citation:** Dechow, P. M., Richardson, S. A. and Sloan, R. G. (2008). Journal of Accounting
  Research (volume and pages not checked). Version read: Rodney L. White Center working paper
  01-05, dated December 2004 (text extracted by script). Published abstract read through its
  OpenAlex record.
- **Link:** https://doi.org/10.1111/j.1475-679x.2008.00283.x (draft:
  https://rodneywhitecenter.wharton.upenn.edu/wp-content/uploads/2014/04/0501.pdf)
- **Stream:** 10, accounting signals
- **Verified against source:** yes, 2026-11-22; the December 2004 draft in full (Tables 2 to 4).
  Pages and numbers of the published version not checked.

## Question

Sloan (1996) showed that the accrual part of earnings is less persistent than the cash part. Which
part of the cash component carries the higher persistence, and do prices reflect it?

## Data

Compustat, 1950 to 2003: 254,596 firm-years for persistence; 150,837 with CRSP returns for pricing.
All industries. Delisted firms: returns as available in CRSP (not discussed further in the parts
read).

## Method

Annual cross-sectional regressions of next year's income (scaled by average assets) on this year's
income and its parts, averaged across years (Fama-MacBeth). Cash part split into the change in cash,
net distributions to debtholders and net distributions to equityholders. Mishkin tests compare the
persistence implied by prices with the forecasting persistence.

## Outcome variable and horizon

Next year's income over assets (a return on assets); one year.

## Result

- **Empirical finding.** Persistence of income 0.657 (t = 35.29). With the split: accruals 0.606
  (t = 27.95), free cash flow 0.681 (t = 38.82). Cash split further: change in cash 0.627,
  distributions 0.706; to equity 0.745, to debt 0.616. Adjusted R² rises only from 0.424 to 0.464
  across the four specifications (Table 3).
- **Empirical finding.** The higher persistence of cash is entirely due to distributions to
  equityholders; the change in cash and debt flows persist about as little as accruals.
- **Empirical finding.** In the returns sample, income persistence is lower (0.567), "earnings
  persistence has dropped significantly in recent decades". Prices act as if accrual persistence
  were 0.785 against an actual 0.473 (Table 4, Panel D).
- **Empirical finding (published abstract).** The accrual anomaly subsumes the external-financing
  anomaly; investors seem to misunderstand diminishing returns to new investment.

## Look-ahead and memorisation

Not addressed beyond standard Compustat and CRSP practice. No language model.

## What it settles for us

- Sizes the accrual effect that a "quality of earnings" field would chase: on annual ROA the gap
  between accrual and cash persistence is 0.61 against 0.68, and splitting into accruals and cash
  raises the R² by 1.3 points (0.424 to 0.437), four points with the full cash decomposition. Real
  for an EPS label, small, and annual.
- It concerns profitability, not revenue. Nothing here bears on next-quarter revenue growth.
- Supports giving the PM operating cash flow next to earnings only for an earnings label, and
  framing high accruals as "growth in operating assets that tends to earn less" rather than as
  manipulation.

## Limits

Draft version. Annual. All firms, mostly small by count.
