# Quality Minus Junk

- **Citation:** Asness, C. S., Frazzini, A., and Pedersen, L. H. (2019). Quality minus junk. *Review of Accounting Studies* 24(1), 34–112. DOI 10.1007/s11142-018-9470-2. Version read: final published version, open access (CC BY), full text.
- **Link:** https://doi.org/10.1007/s11142-018-9470-2
- **Stream:** 06, distress and failure prediction
- **Verified against source:** yes, 2026-11-12

## Question
Do investors pay more for high-quality firms, and what do high-quality stocks earn relative to low-quality ("junk") stocks?

## Data
No text. 54,616 stocks in 24 developed countries, June 1957 to December 2016: a long US sample from 1957 and a global sample from 1989. Prices and accounting data from CRSP and Compustat (North America and Global). Common stocks only; over-the-counter stocks are dropped; at least five years of history are required. Analyst target prices and earnings forecasts from I/B/E/S.

Delisting returns are included when available. When a delisting is performance-related and the return is missing, the authors assume −30%, citing Shumway (1997).

## Method
A quality score averages three components, each an average of cross-sectional rank z-scores:

- Profitability: gross profit over assets, return on equity, return on assets, cash flow over assets, gross margin, low accruals.
- Growth: five-year change in residual per-share profitability measures.
- Safety: low beta, low leverage, low bankruptcy risk (Ohlson O-score and Altman Z-score), low volatility of return on equity.

The QMJ factor is long the top 30% and short the bottom 30% by quality, within large and within small stocks, value-weighted and rebalanced monthly. Returns are regressed on market, size, value and momentum factors.

## Outcome variable and horizon
Price-to-book (cross-section); monthly excess returns and alphas of quality-sorted portfolios and of QMJ.

## Result
- Price: quality explains about 10% of the cross-section of price-to-book.
- Deciles: highest minus lowest quality earns 42 and 52 basis points a month in the two samples (t = 2.56 and 2.49).
- QMJ, United States, July 1957 to December 2016 (714 months): excess return 0.29% a month (t = 3.62); CAPM alpha 0.39% (t = 5.43); three-factor alpha 0.51% (t = 8.90); four-factor alpha 0.60% (t = 9.95); Sharpe ratio 0.47.
- QMJ, global: excess return 0.38% a month (t = 3.33); four-factor alpha 0.61% (t = 8.07). Positive in 23 of 24 countries.
- Loadings (United States): market −0.20 (t = −14.35), size −0.26, value −0.37, momentum −0.09.
- By market state (Table 6, United States, raw excess return per month): recessions 0.50% (t = 2.00); severe bear markets 0.03% (t = 0.03, 21 months); severe bull markets, defined as a market return above 25% over the past 12 months, 0.18% (t = 1.14, 144 months); months with a spike up in volatility 0.48% (t = 3.20); months with a spike down in volatility 0.00% (t = −0.04, 238 months). Four-factor alphas are positive in every state.
- The price of quality was lowest in February 2000 and low before the 1987 crash and before 2007–2009. A low price of quality predicts a high QMJ return.
- Analysts: implied return expectations are lower for quality than for junk stocks, and earnings forecasts are more over-optimistic for junk stocks.

## Look-ahead and memorisation
Accounting data for a fiscal year ending in calendar year t−1 are used from June of year t, the Fama–French convention. Whether Compustat values are first-reported or restated is not addressed. Memorisation does not arise: there is no language model.

## What it settles for us
- **Softer tier, fundamental deterioration.** Gives a published, off-the-shelf definition of quality built from ratios we can compute from as-filed figures: the profitability set and leverage need no prices. A drop in this composite is a defensible definition of deterioration.
- **Softer tier, market performance.** QMJ's market loading is −0.20: junk carries more market risk than quality. In risk-on months, when volatility falls sharply, the raw QMJ return is zero, and after strong market rallies it is not significant. A failure signal judged on raw returns will look wrong in those months; judged on alpha it does not. Market-tier outcomes should be market-adjusted and reported by market state.
- **Narrative optimism.** Analysts are most over-optimistic about junk stocks. This is indirect support for the project's premise that optimism and weak fundamentals coexist; it concerns analysts, not management text.
- **Delisting returns.** Supports the default; gives the −30% convention for missing performance-related delisting returns.

## Limits
- "Junk rallies" are not studied as events. The evidence is the average factor return by market state.
- Quality is a level, not a change; the paper does not test deterioration.
- Growth and safety components need five years of history and prices, so they are unavailable for recent listings, where failures concentrate.
- The authors are affiliated with AQR Capital Management; the paper carries a disclaimer about the firm's own investment techniques.
