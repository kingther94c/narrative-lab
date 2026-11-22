# Stream 10: accounting signals for next-quarter revenue and earnings persistence (draft)

Sources checked 2026-11-22, for sub-study S2 (`../../design/substudy_s2_blind_replay.md`), after
EXP-0034. Notes are in `../papers/`; all 25 rows are in `10_accounting_signals.csv`: 6 deep notes
and 19 triaged rows. `li-2024` (stream 02) is used below and not repeated. This draft is not merged
into `../matrix.csv`.

The question the stream has to settle: the owner wants the PM to read the accounting structure
behind the numbers (one-off vs recurring earnings, inventory turning faster or slower, receivables
against sales, organic vs acquired growth, price vs volume). Which financial-statement and
disclosure items does the accounting literature show to predict (a) next-period revenue growth and
(b) the persistence of current earnings or revenue? Which are incremental to time-series baselines
and to analysts, with what effect size and horizon? EXP-0034 sets the bar: the comparison-base rule
calls 65% of 22,373 episodes and a five-lag logistic 67%.

## What the stream establishes

**1. The baseline is the seasonal structure of quarterly series**

- **Empirical finding.** Quarterly sales, expenses and earnings each have an adjacent-quarter
  component and a seasonal component, and both can be modelled at firm level for one-step-ahead
  forecasts (Foster 1977, abstract).
- **Empirical finding.** In quarterly earnings surprises measured against a seasonal random walk,
  the fourth lag enters with -0.30: a seasonal surprise partly reverses in the same quarter a year
  later (`jegadeesh-2006`, Table 3, 1987 to 2003).
- **Our reading.** EXP-0034's "comparison base" rule is this seasonal reversal. The literature
  treats it as the baseline, not as an insight. Every signal below has to be judged by what it adds
  to it.
- **Empirical finding.** Industry-specific mean-reversion models forecast firm growth better than
  economy-wide ones, but not profitability (Fairfield, Ramnath and Yohn 2009, abstract). A
  sector-relative growth term is the one baseline refinement the literature supports.
- **Empirical finding (what does not persist).** There is no persistence in long-term earnings
  growth beyond chance; I/B/E/S long-term growth forecasts are optimistic and add little;
  valuation ratios predict growth weakly (Chan, Karceski and Lakonishok 2003, abstract).

**2. Leading indicators of revenue**

- **Empirical finding (backlog).** In manufacturers 1996 to 2014, the change in backlog intensity
  explains 9.9% of the variance of next-year sales growth (coefficient 0.141, t = 13.25), against
  2.3% for the change in inventory over sales; together 10.5%. The gap is large for make-to-order
  firms (10.7% against 2.2%) and not significant for make-to-stock firms (`toynbee-2017`, Table
  E.2). These regressions have no control for current or past sales growth.
- **Empirical finding (backlog and direction).** The more backlog relative to assets, the less
  likely next-period sales fall; above the median, a current sales decrease is no longer bad news
  (Banker, Barber, Hollie and Park 2019, abstract). This is the closest result to S2's label.
- **Empirical finding (backlog and earnings).** Backlog predicts future earnings; the market
  overweights it, and the mispricing is not due to analysts (Rajgopal, Shevlin and Venkatachalam
  2003, abstract). Backlog changes add to next-year earnings beyond current earnings (0.017,
  t = 3.99, `toynbee-2017` Table E.3).
- **Verified fact.** Backlog is much broader than deferred revenue: only 27.6% of backlog
  disclosers report deferred revenue, and backlog exceeds it for 93.3% of those (`toynbee-2017`).
  Under ASC 606 the comparable disclosure is remaining performance obligations.
- **Empirical finding (deferred revenue).** Changes in current deferred revenue are positively
  associated with sales growth, gross margin, profit margin and ROA over the next two years
  (Zhong, Wang and Ning 2016, abstract). Rising deferrals depress current sales and margins and
  inflate future ones; analysts then underestimate future earnings, and their sales and margin
  forecasts err in the direction of the deferral change (Prakash and Sinha 2013, abstract).
- **Empirical finding (inventory by component).** For manufacturers, unexpected changes in raw
  materials and work in process, after controlling for current sales, lead future sales positively
  and are neutral for earnings. Finished goods have little or no relation with future sales and
  lead earnings negatively. For retailers, inventory leads earnings negatively and sales only
  briefly (Bernard and Noel 1991, abstract; incremental to current and past sales and earnings).
- **Empirical finding (inventory and margin, retailers).** Inventory and gross margin are jointly
  determined with sales (a 1% rise in inventory per store raises sales per store by 0.29%; inventory
  lowers margin). A joint model beat time-series models and analysts on annual sales (working paper
  MAPE 5.82% against 8.62% for ARIMA; 2.45% against 6.36% for analysts on 42 firms)
  (`kesavan-2010`). The working paper's comparison is not point in time: the forecasts use the
  target year's store growth, SG&A per store and store count, and analysts' forecasts 13 months old.
  The published abstract keeps the claim that analysts do not fully use the information.
- **Empirical finding (units times rate).** Splitting retail sales growth into growth in
  sales-generating units (new stores) and in the sales rate of existing units (comparable stores)
  gives in-sample errors under 2% of sales, out-of-sample errors almost as small as analysts', and,
  combined with analysts, a forecast significantly more accurate than analysts alone (Curtis,
  Lundholm and McVay 2014, abstract).
- **Gap.** No study found tests organic against acquired growth, price against volume, or FX for
  next-period revenue. EXP-0033 found deals annualising and FX turning behind right calls; the
  literature read does not cover them.

**3. Persistence of earnings: one-off against recurring**

- **Empirical finding.** Removing non-core items gives a much more persistent earnings measure:
  annual cross-sectional persistence of net income 0.637, of Core Earnings 0.810, of the
  adjustments 0.178. Non-core items average 19% of net income, about half are disclosed off the
  face of the income statement, and the next-year forecast error falls by 20% (MSE). Core Earnings
  is incremental to net income, CFO, Compustat measures and street earnings (`rouen-2021`).
- **Empirical finding.** "One-off" items are not unimportant: higher exclusions from pro forma
  earnings predict lower future cash flows, and investors miss it (Doyle, Lundholm and Soliman
  2003, abstract). Special items are largely but not wholly transitory and prices do not fully
  reflect them; a strategy on their sign earns small 3-day returns four quarters later
  (Burgstahler, Jiambalvo and Shevlin 2002, abstract). In low-accrual firms, special items drive
  the low persistence of earnings (Dechow and Ge 2006, abstract).
- **Empirical finding.** Accruals are less persistent than cash flows, but the gap is small on
  annual ROA: 0.606 against 0.681, and splitting raises the R² from 0.424 to 0.437. The cash
  premium comes entirely from distributions to equity holders; earnings persistence has fallen
  over time (`dechow-2008`, Table 3). The accrual-return relation is mainly inventory changes
  (Thomas and Zhang 2002, abstract).
- **Empirical finding.** An earnings surprise that comes with a revenue surprise is more persistent:
  last quarter's revenue surprise adds 0.061 to this quarter's earnings surprise beyond four lags of
  earnings surprises; older revenue surprises are small (-0.012 at lag 2, near zero at lags 3 and
  4), and the authors read only the first lag as informative (`jegadeesh-2006`, Table 3). Investors
  value a dollar of revenue surprise more than a dollar of expense surprise (Ertimur, Livnat and
  Martikainen 2003, abstract).
- **Empirical finding.** Costs fall less when sales fall than they rise when sales rise. A model
  using this beats line-item models for next-year ROE but not analysts (Banker and Chen 2006,
  abstract). Disaggregating ROA levels into turnover and margin adds nothing for next-year ROA
  change; the change in asset turnover does help (Fairfield and Yohn 2001, abstract). Abnormal
  inventory growth has an inverted-U relation with next-year EPS for retailers (Kesavan and Mani
  2013, abstract).
- **Open question.** None of these papers tests whether a one-off in revenue (a licence, an extra
  week, a large order) predicts the next quarter's revenue growth. Our reading: in year-over-year
  growth it shows up four quarters later as a comparison-base effect, which code can measure if the
  release names the item.

**4. Incremental to analysts, and the large-firm caveat**

- **Empirical finding.** Analysts under-use several of these items: inventory and margin
  (`kesavan-2010`), deferral changes (Prakash and Sinha), abnormal inventory growth (Kesavan and
  Mani), non-core items disclosed in footnotes (`rouen-2021`, Table 8: footnote items have the
  largest coefficient for later upward revisions), and revenue surprises, which they take "up to six
  months" to absorb (`jegadeesh-2006`).
- **Empirical finding.** The effects are weaker for large firms: there is no post-announcement drift
  after revenue surprises for large firms (`jegadeesh-2006`). Most samples above are all listed
  firms, mostly small by count.
- **Convention.** Almost all of this evidence is annual. One-quarter-ahead evidence is limited to
  Foster (1977), `jegadeesh-2006` and Burgstahler et al. (2002), all about earnings. Bernard and
  Noel's horizon is not stated in the abstract.

**5. LLM evidence on reading the accounting structure**

- **Empirical finding (withdrawn).** A four-step chain-of-thought prompt (notable changes, ratios
  with formulas, interpretation, call) on anonymised annual statements was reported at 60% for the
  sign of next-year EPS change, with the simple prompt at 52% (`kim-2024`). The paper is withdrawn
  for data inconsistencies; another team found GPT-4 Turbo at 48 to 49% against analysts' 71% from
  press releases (`li-2024`, stream 02).
- **Gap.** No LLM study read asks the model to judge earnings quality or persistence and validates
  it. Shaffer and Wang (2024) appear to do this for core earnings from 10-Ks, but only the authors'
  blog summary was read (unverified lead below).

**6. Point-in-time warnings**

- **Verified fact.** Compustat's special-items fields carry hindsight: a "three-year rule" decides
  non-recurrence with later years in view, and a "majority rule" leaves special items blank when
  most cannot be placed on a line (`rouen-2021`, section 2, examples GM 2011 to 2013 and Ford 2006).
  The New Constructs data were back-filled before 2008.
- **Our reading.** Features for S2 should come from the as-filed release or as-filed XBRL, never
  from vendor-adjusted fields.

## Gaps

- No study read tests any accounting item for next-quarter year-over-year revenue growth
  acceleration, incremental to a seasonal or comparison-base baseline. The nearest are annual
  (backlog, inventory, deferred revenue, units times rate) and have weak or no past-growth
  controls.
- No academic study found on remaining performance obligations (ASC 606) as a revenue predictor;
  the search returned only practitioner material.
- Organic against acquired growth, price against volume and FX are not covered by the sources read.
- No validated LLM judgement of earnings persistence (`kim-2024` withdrawn; Shaffer and Wang not
  opened).
- Large-firm (S&P 500) effect sizes are not reported separately in the sources read, except the
  large-firm drift result in `jegadeesh-2006`.

## Limits of this pass

- SSRN, ScienceDirect, core.ac.uk and the Hawaii repository refused automated access (SSRN,
  core.ac.uk and Hawaii with a bot check, which was not bypassed); JSTOR was not tried. Full
  texts came from author or institutional copies: four working-paper or manuscript versions
  (`rouen-2021`, `jegadeesh-2006`, `kesavan-2010`, `dechow-2008`), one dissertation and one arXiv
  HTML. Numbers may differ from the published versions.
- This machine has no PDF text tool; PDFs were read with a standard-library extractor written for
  this pass (ligatures such as "fi" drop out). Tables were read from extracted text, which can
  misalign columns; key numbers were cross-checked against the prose that reports them.
- Triaged rows rest on abstracts from publisher pages (Springer) or the OpenAlex record of the DOI.
- A web-search summary said the market "underweights" backlog (Rajgopal et al. 2003); the abstract
  says it overweights. The abstract is used.
- Searches (web, 2026-11-22): inventory and gross margin sales forecasts; retail sales forecasting;
  order backlog and future sales; deferred revenue and RPO; pro forma exclusions; special items;
  accrual persistence; cost stickiness; quarterly time-series models of sales; growth persistence;
  LLM earnings-quality and revenue forecasting.

## Unverified leads

Seen only in search results, keyword records or secondary summaries; nothing is claimed from them.

- Abarbanell and Bushee (1997), "Fundamental Analysis, Future Earnings, and Stock Prices", Journal
  of Accounting Research 35(1) 1-24 (title corrected from the brief's "Financial statement
  analysis"): record shows keywords only. The 1998 companion is a triaged row.
- Lev and Thiagarajan (1993), "Fundamental Information Analysis", Journal of Accounting Research:
  keywords only.
- Sloan (1996), The Accounting Review: only an index summary was reached; its persistence result is
  used here as reported in `dechow-2008`.
- Richardson, Sloan, Soliman and Tuna (2005), "Accrual reliability, earnings persistence and stock
  prices", Journal of Accounting and Economics 39(3): no abstract reachable.
- Brown and Rozeff (1979) and Lorek (2014, Advances in Accounting): no abstracts reachable. A search
  snippet says Lorek supports the Brown-Rozeff ARIMA model for quarterly operating cash flow.
- Shaffer and Wang (2024), "Scaling Core Earnings Measurement with Large Language Models", SSRN
  4979501: per the authors' blog, a three-pass GPT-4o prompt on 10-Ks (unusual expenses, unusual
  gains, tabulate) gives adjustments with zero autocorrelation and beats net income in forecasting;
  a baseline prompt confused core earnings with EBITDA; memorisation acknowledged, not ruled out.
- Published Kesavan, Gaur and Raman (2010): a university news item reports MAPE 4.67% against
  5.67% for analysts (not read in the paper).
- Fildes, Ma and Kolassa (2019, MPRA 89356), a retail forecasting review, describes chain-level
  sales research as mostly one year ahead (read, not a primary source).

## For the S2 analysis checklist

Ranked for S2's label (next quarter's year-over-year revenue growth accelerates, S&P 500). Each item
says what a reader could extract from the release or code could compute from as-filed XBRL; the
evidence, effect size and horizon; whether it is plausibly incremental to past-growth baselines;
and whether it bears on revenue or only on earnings. The comparison base and the guidance
arithmetic stay in code (template v3); this literature does not cover management guidance.

1. **Order backlog, book-to-bill, remaining performance obligations (RPO, current RPO) and their
   change.** Release text for backlog and bookings; XBRL `RevenueRemainingPerformanceObligation`
   (10-Q/10-K). Evidence: backlog growth explains about 10% of next-year sales growth variance in
   manufacturers, four times inventory's share, more in make-to-order firms (`toynbee-2017`); high
   backlog makes a sales decline less likely (Banker et al. 2019); backlog predicts earnings
   (Rajgopal et al. 2003). Horizon: annual. Incremental to past growth: untested (hypothesis,
   plausible because it is contracted future revenue). Bears on revenue and earnings.
2. **Deferred revenue or contract liabilities, change against revenue (billings).** XBRL
   `ContractWithCustomerLiabilityCurrent`, `DeferredRevenueCurrent`. Evidence: leads sales growth
   and margins over two years (Zhong et al. 2016); deferral changes cause analysts' sales and margin
   errors (Prakash and Sinha 2013). Horizon: one to two years. Incremental to analysts: yes; to past
   growth: hypothesis. Bears on revenue and on margin timing.
3. **Units times rate: comparable-store (same-store, organic) growth against unit growth; by
   analogy volume against price, organic against acquired.** Release text. Evidence: retail model
   with in-sample errors under 2% of sales that improves on analysts when combined (Curtis et al.
   2014). Horizon: annual. Incremental: yes to analysts in retail; the non-retail analogues are
   untested here (gap). Bears on revenue.
4. **Inventory relative to sales, by component.** XBRL `InventoryNet`, `InventoryRawMaterials`,
   `InventoryWorkInProcess`, `InventoryFinishedGoods` (component detail usually in the 10-Q, not the
   release). Evidence: manufacturers' raw materials and work in process lead sales; finished goods
   do not (Bernard and Noel 1991, incremental to past sales); retailers' inventory and margin help
   annual sales forecasts (`kesavan-2010`, accuracy edge not point in time); inventory growth alone
   explains 2.3% of next-year sales growth (`toynbee-2017`). Bears on revenue (raw materials and
   work in process) and on earnings (finished goods and retail inventory build-ups lead earnings
   down).
5. **Sector-relative growth (code).** Company growth against the sector median of the same
   quarter. Evidence: industry-specific mean reversion forecasts growth better than economy-wide
   (Fairfield et al. 2009). Horizon: annual. Incremental: a refinement of the baseline itself.
   Bears on revenue.
6. **Gross margin change.** XBRL `Revenues`, `CostOfRevenue`. Evidence: input to retailer sales
   forecasts (`kesavan-2010`); a standard earnings signal (Abarbanell and Bushee 1998). Bears on
   revenue weakly (markdowns signal weak demand), on earnings more.
7. **Receivables growth against revenue growth (days sales outstanding).** XBRL
   `AccountsReceivableNetCurrent`. Evidence: the better manipulation flag (Stubben 2010, detection
   only); part of the standard earnings signal set (Abarbanell and Bushee 1998). Revenue use is a
   hypothesis: revenue pulled forward lowers the next quarter. **Mainly an earnings-quality item.**
8. **Revenue-led or cost-led earnings beat.** Release table. Evidence: a revenue-led beat persists
   more (`jegadeesh-2006`, +0.061 per unit of last quarter's revenue surprise); investors value
   revenue surprises more (Ertimur et al. 2003). Horizon: one quarter. **Earnings label only.**
9. **One-off and non-core items: special items, restructuring, gains on investments or disposals,
   litigation, pension mark-to-market, currency, items excluded from non-GAAP EPS.** Release
   reconciliation table; footnotes. Evidence: core earnings persistence 0.81 against 0.18 for the
   adjustments, 19% of net income, half off the income statement (`rouen-2021`); exclusions predict
   lower cash flows (Doyle et al. 2003); special items are not fully transitory (Burgstahler et al.
   2002; Dechow and Ge 2006). Horizon: one quarter to five years. **Earnings label only**, except a
   one-off inside revenue, which becomes a comparison-base effect four quarters later (our
   reading; untested).
10. **Accruals and cash conversion (operating cash flow against net income).** XBRL
    `NetCashProvidedByUsedInOperatingActivities`. Evidence: accrual persistence 0.61 against 0.68
    for cash on annual ROA (`dechow-2008`); the accrual-return link is mostly inventory (Thomas and
    Zhang 2002). **Earnings label only; small.**
11. **Cost stickiness when sales fall.** Evidence: improves line-item ROE forecasts, not analysts'
    (Banker and Chen 2006). **Earnings label only** (margins given a revenue path).
12. **Change in asset turnover.** Evidence: helps forecast next-year ROA change (Fairfield and Yohn
    2001). **Earnings label only.**

**Not predictive, or not worth the PM's attention, per the sources read:**

- Long-run growth persistence: a firm's past high earnings growth does not persist beyond chance;
  analysts' long-term growth forecasts add little; valuation ratios predict growth weakly (Chan et
  al. 2003).
- The ROA level split into turnover and margin (Fairfield and Yohn 2001).
- Finished-goods inventory as a lead for sales (Bernard and Noel 1991).
- Revenue surprises older than one quarter, for next-quarter earnings: coefficients of -0.012 or
  less (`jegadeesh-2006`).
- Non-core adjustments found only in the cash flow statement, except for future cash flow
  (`rouen-2021`).
- Vendor-adjusted fields (Compustat special items, OIADP adjustments) as point-in-time features:
  they carry hindsight or miss recurring items (`rouen-2021`).
- A free-form "analyse the statements" prompt: 52% in the withdrawn `kim-2024`, and an LLM below
  analysts on direction in `li-2024`. Any accounting skill has to beat 0.65 (EXP-0034) on clean
  episodes before it is believed.
- Expect small gains in S&P 500 names: the market and analysts absorb revenue information faster
  for large firms (`jegadeesh-2006`).
