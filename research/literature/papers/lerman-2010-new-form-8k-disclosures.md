# The New Form 8-K Disclosures

- **Citation:** Lerman, A., and Livnat, J. (2010). The new Form 8-K disclosures. *Review of Accounting Studies* 15(4), 752–778. DOI 10.1007/s11142-009-9114-7. Version read: SSRN working paper, draft of 29 April 2008 (copy in the NYU Faculty Digital Archive), full text. The published abstract was checked on IDEAS/RePEc. Numbers below are from the working paper.
- **Link:** https://archive.nyu.edu/handle/2451/27579 (working paper); https://doi.org/10.1007/s11142-009-9114-7 (published)
- **Stream:** 06, distress and failure prediction
- **Verified against source:** yes, 2026-11-12 (working-paper text; published version at abstract level only)

## Question
After the SEC expanded Form 8-K and shortened its deadline to four business days (effective 23 August 2004), how often is each item filed, how fast, and how do prices and volume react?

## Data
Form 8-K, 10-K and 10-Q filings from EDGAR, 1994 to 2007. The paper uses the item codes and dates, not the text. Filings are matched to Compustat through the S&P Filing Dates database, a point-in-time link that keeps firms that later became inactive through merger, going private or bankruptcy, and then to CRSP. A filing is kept only if the firm has valid returns and volume from one day before the event to one day after the filing. That gives 346,646 8-K filings overall. The item-level analysis uses 2005–2006: 127,273 filings, or 125,468 after merging same-day filings by event date.

Delisted firms are included up to the event. Delisting returns come from CRSP; a forced delisting with a missing return is set to −100%.

## Method
Event study. Three-day buy-and-hold abnormal returns against size and book-to-market matched portfolios, abnormal volume and abnormal volatility, measured around the event date and around the filing date. Drift is measured over 30, 60 and 90 days after filing.

## Outcome variable and horizon
Abnormal return, volume and volatility over three days around the event and the filing, and over 30 to 90 days after the filing.

## Result
Counts in 2005–2006 (Table 1, share of all 8-K filings in the sample):

| Item | Filings | Share |
|---|---|---|
| 1.03 Bankruptcy or receivership | 18 | 0.0% |
| 2.06 Material impairments | 532 | 0.4% |
| 3.01 Notice of delisting or transfer of listing | 2,137 | 1.7% |
| 4.02 Non-reliance on prior financial statements | 1,124 | 0.9% |
| 2.02 Results of operations | 37,704 | 30.1% |

Abnormal returns (Table 3, significance stars as printed in the paper):

| Item | 3 days, event | 3 days, filing | Event to filing | Drift 30 / 60 / 90 days |
|---|---|---|---|---|
| 1.03 | +5.77% | −11.90% * | −8.86% | −14.70% ** / −13.32% ** / −19.00% ** |
| 2.06 | −1.13% *** | −1.65% *** | −2.31% *** | −1.23% *** / −1.62% ** / −1.95% ** |
| 3.01 | −1.13% *** | −2.90% *** | −3.65% *** | −0.54% / −0.44% / +0.27% |
| 4.02 | −1.04% *** | −1.61% *** | −2.34% *** | +0.13% / +0.52% / +0.94% |

Timeliness: nearly 95% of filings arrive within four business days. Among single-item filings, 93.9% of Section 3 filings and 92.8% of Section 4 filings meet the deadline; about 28% and 33% arrive on the last permitted day.

All items, old and new, come with abnormal volume and volatility at both dates. Periodic reports do not lose information content.

## Look-ahead and memorisation
The design separates the event date from the EDGAR filing date and measures reactions at both, which is the distinction our point-in-time protocol needs. The Compustat link is point-in-time. Memorisation does not arise: there is no language model.

## What it settles for us
- **Hard-event tier.** Supports using Items 2.06, 3.01 and 4.02 as adverse events: each has a significant negative price reaction at the event and at the filing. For Item 1.03 the sample holds only 18 filings, probably because the return requirement drops firms that had already left the exchange (my reading; the paper does not say). A census built from EDGAR alone should find more 1.03 filings than this.
- **Order of events.** Campbell et al. (2008) note that delisting sometimes precedes bankruptcy, so an Item 3.01 notice can lead Item 1.03 for the same firm. The tier needs a rule for which event counts first.
- **Base rates.** About 1,070 Item 3.01, 560 Item 4.02 and 270 Item 2.06 filings a year in 2005–2006 among firms with CRSP prices (my division of the two-year counts). The paper gives no count of firms, so these are not rates.
- **Drift.** Impairments drift down for 90 days; delisting notices and non-reliance do not. A prediction window that opens after the filing would find little left for 3.01 and 4.02.
- **Reuse.** The event-date versus filing-date design, and the −100% convention for forced delistings with a missing return.

## Limits
- Two years only, immediately after the rule change and at the peak of restatement activity.
- The table in the extracted text prints labels and numbers in separate runs. The figures for 2.06 and 4.02 sit on their own lines; those for 1.03 and 3.01 were assigned by their order within a block and should be rechecked against the published table before they are quoted.
- Item 3.01 pools deficiency notices with voluntary transfers of listing; the paper does not split them.
- Item counts are filings, not firms; one firm can file the same item more than once.
