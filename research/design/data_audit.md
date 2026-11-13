# Data audit

Status: not started. Work package 2 of Phase 0; the plan is in
[`../registry/01_roadmap.md`](../registry/01_roadmap.md).

No SEC EDGAR request is made until the owner has chosen the contact string. Nothing pulled goes
into git.

## What each section must contain

For every source: what it covers (universe, period, whether delisted firms are included), the
timestamp that makes it point-in-time, the defect rate found in a sample pull, the licence and what
it permits, the cost, and a verdict.

## Sections

1. Disclosure text (SEC EDGAR: 8-K earnings press releases, 10-Q, 10-K)
2. Earnings call transcripts
3. Fundamentals as filed (SEC XBRL)
4. Failure events (8-K items 1.03, 3.01, 4.02, 2.06)
5. Returns including delisted stocks
6. Consensus estimates
7. Guidance census: 50 companies by 8 quarters
8. Hard-event census: filings after 2026-06-30
9. Go / no-go per candidate task and per outcome variable
10. Storage estimate

## 2. Earnings call transcripts

Audited 2026-11-12 from the card, file listing, viewer statistics and discussions of [`kurry/sp500_earnings_transcripts`](https://huggingface.co/datasets/kurry/sp500_earnings_transcripts); no data file was downloaded. **V** = verified at the linked source; **I** = inferred.

**Provenance and licence**

- V: The card names no source. It says "Licensed under MIT. For research and educational use only", which contradicts itself. A provenance question ([#3](https://huggingface.co/datasets/kurry/sp500_earnings_transcripts/discussions/3), 2026-09-07) is unanswered.
- V: `company_id` is a "Capital IQ Company identifier", and the uploader's [sibling set](https://huggingface.co/datasets/kurry/earnings_transcripts_db) has `transcriptid` and `keydevid` fields. I: those are S&P Capital IQ column names.
- I: The layout (`symbol, quarter, year, date, content`; "Speaker: text" lines; 2025 tickers on old calls) matches retail APIs such as [FMP](https://site.financialmodelingprep.com/how-to/how-to-get-earnings-call-transcripts-with-fmp-apis). The original transcriber is unknown.
- V: Each candidate upstream forbids redistribution: [FMP](https://site.financialmodelingprep.com/terms-of-service) (no distributing or publishing without written approval), [Seeking Alpha](https://about.seekingalpha.com/terms) (personal use, no scraping), [Motley Fool](https://www.fool.com/legal/terms-and-conditions/fool-rules/) (no republishing, no automated copying), and S&P's [Kensho terms](https://huggingface.co/datasets/kensho/spgispeech).
- I: The uploader cannot grant MIT. Private analysis carries less risk than redistribution (disseminating a call recording was held fair use in [Swatch v. Bloomberg](https://www.copyright.gov/fair-use/summaries/swatchgrp-bloomberg-2dcir2014.pdf)).

**Contents** (V: [file listing](https://huggingface.co/api/datasets/kurry/sp500_earnings_transcripts/tree/main?recursive=true), [viewer statistics](https://datasets-server.huggingface.co/statistics?dataset=kurry/sp500_earnings_transcripts&config=default&split=train))

- One parquet file, 1.82 GB; 33,362 transcripts; 685 tickers; last modified 2025-05-21.
- Fields: `symbol`, `quarter`, `year` (fiscal), `date`, `content`, `structured_content`, `company_name`, `company_id`.
- `date` is never null and runs from 2005-10-13 14:45 to 2025-05-15 16:30. I: it is the call start in US Eastern time; one spot check (Agilent, 2020-11-23 16:30) matches the [company's notice](https://www.businesswire.com/news/home/20201029006097/en/).
- Nothing after May 2025, so no transcript postdates the 2026-06-30 cutoff.

**Defects**

- V: [#2](https://huggingface.co/datasets/kurry/sp500_earnings_transcripts/discussions/2) (2026-05-23) reports truncated transcripts; unanswered. Viewer statistics show no length cap (median 53,734 characters, maximum 244,695), one empty transcript and 584 under 24,470 characters.
- V as reported by a [derivative set's card](https://huggingface.co/datasets/zcyeee/sp500-earnings-call-turns), not re-checked: 136 calls under 5,000 characters; 142 without speaker labels; `structured_content` keeps only each turn's first paragraph; `(symbol, year, quarter)` is unique, but 216 calls sit under two tickers; 934 of 2,215 reviewed calls belong to another company.

**Survivorship**

- V: `company_name` is null for 8,985 rows (27%). I: these are the 185 or so tickers outside the May 2025 index, so some leavers are present (SunTrust, SVB, First Republic).
- V: The tickers of Lehman, Bear Stearns, Wachovia, Merrill Lynch, Countrywide, Sears, Yahoo, Celgene and Monsanto are absent. I: leavers are covered patchily, so the set is unfit for a failure sample.

**Alternatives**

- V: Hugging Face: [Earnings-21](https://huggingface.co/datasets/Revai/earnings21) (CC-BY-SA, Rev's own transcription) has clear rights but is tiny. [`jlh-ibm/earnings_call`](https://huggingface.co/datasets/jlh-ibm/earnings_call) is tagged CC0 yet credits Thomson Reuters Eikon. Nothing found combines scale with clean rights.
- V: Paid APIs: [FMP](https://site.financialmodelingprep.com/datasets/earnings-call-transcripts) Ultimate, $139/month; [API Ninjas](https://www.api-ninjas.com/pricing) Business, $149/month, the lowest tier that allows storage, with delisted firms [covered](https://www.api-ninjas.com/api/earningscalltranscript); [EarningsCall](https://earningscall.biz/api-pricing) from $60/month; [Alpha Vantage](https://www.alphavantage.co/documentation/) since 2010Q1, 25 free requests/day. FMP and EarningsCall sell redistribution rights separately.
- V: Papers: [ECTSum](https://ar5iv.labs.arxiv.org/html/2210.12467) crawled Motley Fool; [Earnings-22](https://ar5iv.labs.arxiv.org/html/2203.15591) took audio from Seeking Alpha; [WRDS](https://wrds-www.wharton.upenn.edu/pages/grid-items/capital-iq-transcripts/) supplies Capital IQ transcripts to subscribing universities.

**Verdict: usable only as a secondary layer.** The licence audit fails: provenance is undisclosed and the MIT tag is not credible. The set can serve private, pre-cutoff development work on the external drive, with no text, excerpt or derived item published. It cannot supply clean test documents or a failure sample.

**Open questions for the owner**

1. Is private use of text under an invalid licence acceptable, or should a licensed feed be bought, and on what budget?
2. Is WRDS or another institutional subscription available?
3. Are transcripts after 2026-06-30 needed? A paid API is the only route found.
4. Should the EDGAR sample pull count transcripts furnished as 8-K exhibits?
