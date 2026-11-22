# Do Inventory and Gross Margin Data Improve Sales Forecasts for U.S. Public Retailers?

- **Citation:** Kesavan, S., Gaur, V. and Raman, A. (2010). Management Science 56(9), 1519-1533.
  Version read: the earlier working paper, "Incorporating Price and Inventory Endogeneity in
  Firm-Level Sales Forecasting", Harvard Business School Working Paper 07-056, draft of 9 January
  2007 (full text, extracted by script). Of the published version only the abstract was read
  (OpenAlex record of the DOI).
- **Link:** https://doi.org/10.1287/mnsc.1100.1209 (working paper:
  https://www.hbs.edu/ris/Publication%20Files/07-056.pdf)
- **Stream:** 10, accounting signals
- **Verified against source:** yes, 2026-11-22; the working paper in full, the published paper's
  abstract only. Numbers below are the working paper's; the published version may differ.

## Question

Are retailers' sales, inventory and gross margin jointly determined, and does modelling them
jointly improve firm-level sales forecasts over time-series models and analysts?

## Data

Compustat annual and quarterly data for US-listed retailers, 1994 to 2004; store counts and
selling space hand-collected from 10-Ks; University of Michigan consumer sentiment; I/B/E/S annual
sales forecasts. Starting from the 311 firms of Gaur, Fisher and Raman (2005); final sample 149
firms in five retail segments (jewellery dropped). Survivorship: firms with missing data or
accounting changes were filtered out, so the panel favours survivors (our reading).

## Method

Three simultaneous equations in logs (sales per store at cost, inventory per store, gross margin
as sales over COGS), identified by "curve shifters": SG&A per store, share of new inventory, store
growth, capital investment per store, consumer sentiment, lagged sales and margin. Segment-specific
coefficients. Reduced-form equations produce the forecasts. Baselines: ARIMA(1,1,1) on sales per
store and margin; the same plus SG&A per store, store growth and sentiment. Fit 1994 to 2003, test
on 2004.

## Outcome variable and horizon

Sales revenue per store; one fiscal year ahead.

## Result

- **Empirical finding.** Mutual causation, all p < 0.001: a 1% rise in inventory per store raises
  sales per store by 0.29%; a 1% rise in sales raises inventory by 0.76%; margin raises inventory
  (1.81); inventory lowers margin (-0.14). A 1% rise in SG&A per store raises sales per store by
  0.77% (reduced form).
- **Empirical finding (working paper).** 2004 test-year MAPE: joint model 5.82%, ARIMA 8.62%,
  augmented time series 6.41% (Table 7). Against analysts, 42 firms: model 2.45%, analysts 6.36%
  (Table 8).
- **Empirical finding (published abstract).** Sales forecasts from the model are more accurate than
  analyst consensus; "historical inventory and gross margin contain information useful to forecast
  sales", and analysts do not fully use it. The model's residuals in one year predict where its
  edge over analysts is large the next year.

## Look-ahead and memorisation

Not discussed. In the working paper the "ex-post forecasts" use the reduced form with the forecast
year's exogenous variables (store growth, SG&A per store, consumer sentiment), as in Pindyck and
Rubinfeld's ex-post design, and analysts' sales forecasts are divided by the store count to compare
per store. Both put information from the target year into the model's side (our reading of
equations 10 to 12 and section 6.3). The analyst benchmark is taken 13 months before fiscal
year-end, which disadvantages analysts. The published version may have changed this; not checked.

## What it settles for us

- Supports inventory relative to sales, and gross margin, as inputs that bear on future revenue for
  retailers, with an operational story (stock drives service level; heavy stock forces markdowns).
- Does not show a one-quarter-ahead, real-time edge. Before using its effect size, treat the
  working-paper accuracy as optimistic: the comparison is not point in time.
- For a template field: inventory growth minus sales growth, and the gross margin change, are cheap
  to compute from as-filed XBRL (InventoryNet, CostOfRevenue, Revenues).

## Limits

Retailers only (few S&P 500 retailers). Annual horizon. One test year. Survivor sample. Working
paper numbers.
