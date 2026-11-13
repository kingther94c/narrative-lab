# In Search of Distress Risk

- **Citation:** Campbell, J. Y., Hilscher, J., and Szilagyi, J. (2008). In Search of Distress Risk. *Journal of Finance* 63(6), 2899–2939. DOI 10.1111/j.1540-6261.2008.01416.x. Version read: NBER Working Paper 12362 (July 2006), full text. The published abstract was checked on EconPapers. Every number below is from the working paper and may differ from the published tables.
- **Link:** https://www.nber.org/papers/w12362 (working paper); https://econpapers.repec.org/RePEc:bla:jfinan:v:63:y:2008:i:6:p:2899-2939 (published abstract)
- **Stream:** 06, distress and failure prediction
- **Verified against source:** yes, 2026-11-12 (working-paper text; published version at abstract level only)

## Question
Which firm characteristics predict corporate failure at short and long horizons, and do stocks with a high failure probability earn a premium?

## Data
No text. Monthly bankruptcy and failure indicators from Kamakura Risk Information Services, merged with Compustat quarterly accounting data and CRSP daily and monthly prices.

- Bankruptcy indicator: a Chapter 7 or Chapter 11 filing, January 1963 to December 1998, collected from the Wall Street Journal Index, SDC, SEC filings and the CCH Capital Changes Reporter.
- Failure indicator: bankruptcy, delisting, or a D rating, January 1963 to December 2003.
- 1,695,036 firm-months with complete data, of which 797 are bankruptcy months and 1,614 are failure months.
- Universe: firms in CRSP. Delisted firms are included; delisting is part of the failure definition.

## Method
Dynamic logit (hazard) model on the monthly panel, following Shumway (2001) and Chava and Jarrow (2004). Accounting data are lagged two months. All variables are winsorised at the 5th and 95th percentiles. The model is estimated for failure 1, 6, 12, 24 and 36 months ahead and compared with Shumway's five-variable model and with a Merton distance-to-default measure. Stocks are then sorted each January, 1981 to 2003, on the fitted 12-month failure probability into value-weighted portfolios held for a year.

The eight predictors: profitability (NIMTAAVG, net income over market-valued assets, weighted average of four quarters), leverage (TLMTA), past excess return (EXRETAVG), return volatility (SIGMA), relative size (RSIZE), cash (CASHMTA), market-to-book (MB) and log price per share capped at $15 (PRICE).

## Outcome variable and horizon
Failure indicator in month t+j, j from 1 to 36 months. Monthly excess returns of failure-sorted portfolios, 1981 to 2003.

## Result
Base rates (Table 1, share of active CRSP firms per year):

- Bankruptcy: none in 1967–1969; 0.60% in 1980; peak 1.53% in 1986 (95 of 6,208 firms); 0.36% to 0.65% in 1992–1998. The range for 1980–1998 is 0.36% to 1.53%.
- Failure: tracks bankruptcy until the early 1980s, then diverges: 1.52% in 1998, 2.16% in 1999, 1.77% in 2000, 3.67% in 2001 (324 of 8,817 firms), 2.68% in 2002, 2.13% in 2003.

Prediction:

- Failure is more likely with lower profitability, higher leverage, lower and more volatile past returns, lower cash, higher market-to-book and lower price per share. A one-standard-deviation increase changes the failure probability by +156% (leverage), +64% (volatility), −56% (price), −44% (profitability), −28% (past return), −21% (cash).
- McFadden pseudo-R² for failure, 1963–2003: 0.312 one month ahead, against 0.27 for the Shumway specification; 0.188 at 6 months, 0.114 at 12, 0.061 at 24 and 0.044 at 36 (Table 4). All eight coefficients at 12 months have z-statistics above 2 except price (1.40).
- Distance to default alone: pseudo-R² 0.159 at one month and 0.066 at 12 months. Adding it to the eight variables moves 0.114 to 0.117 (Table 5).
- At long horizons volatility, market-to-book and size gain weight; leverage and recent returns fade.

Returns (Table 6, 1981–2003, annualised): safest decile minus most distressed decile earns 10.2% (t = 1.90), CAPM alpha 12.6% (t = 2.36), three-factor alpha 22.9% (t = 6.15), four-factor alpha 12.2% (t = 3.45). Distressed stocks have high betas and high loadings on size and value, yet low returns. Raw long-short returns were negative in the last few years of the sample while alphas stayed steady.

## Look-ahead and memorisation
Look-ahead is handled for the prediction model: accounting data are lagged two months; out-of-sample pseudo-R² uses coefficients estimated only on earlier years (0.310 at one month and 0.108 at 12 months, close to the in-sample values); the portfolio model is re-estimated every January on past data. Whether the Compustat figures are first-reported or restated is not addressed. Memorisation does not arise: there is no language model.

## What it settles for us
- **Failure definition.** Supports a tiered definition: a narrow tier (bankruptcy filing) and a broad tier that adds delisting and default. The paper counts delisting itself as failure, which is a stronger event than our Item 3.01 notice.
- **Exploratory status of failure prediction.** Supported. At 0.4% to 1.5% a year for bankruptcy, a clean sample of 800 companies holds a handful of events.
- **Structured baseline.** Any text signal for failure has to add to these eight variables, not to accounting ratios alone. The variables need daily prices, including those of firms later delisted.
- **Delisting returns.** The authors use CRSP delisting returns where they exist (6,481 cases) and say that falling back on the last full-month return biases distressed-portfolio returns upward. Supports the default.
- **Reuse.** Variable definitions (appendix of the paper) and Table 1 as the historical base-rate reference.

## Limits
- Read in the 2006 working-paper version; the sample ends in 2003 and the bankruptcy series in 1998.
- The working paper says "delists" without restricting to performance delistings; the composition of the 1,614 failures by type is not reported.
- The failure indicator is proprietary (Kamakura), so the labels cannot be rebuilt from EDGAR.
- Equal weighting of firm-months means small firms dominate the estimates.
