# Data audit

**Status, 2026-11-13.** Work package 2 of Phase 0; the plan is in
[`../registry/01_roadmap.md`](../registry/01_roadmap.md). Done: access set up and checked, the
transcript audit, the hard-event census, the guidance census and the full count of
guidance-bearing pairs. Not started: fundamentals as filed, delisting-aware returns, consensus
estimates.

Nothing pulled goes into git. Pulled data lives under
`/Volumes/Seagate Backup Plus Drive/DATA/narrative_lab/edgar/`.

## Verdicts so far

| Source or question | Verdict | Section |
|---|---|---|
| SEC EDGAR through edgartools | Usable. Timestamps to the second, item codes in the filing list, press releases parse | Access |
| Earnings call transcripts (Hugging Face set) | Secondary layer only; no clean test documents, no failure sample | 2 |
| Hard tier: Items 1.03, 2.06, 4.02 | Usable as counted, at roughly 1% of the universe a year each | 4 |
| Hard tier: Item 3.01 | Not usable until split by text: far too frequent to be failures | 4 |
| Guidance in earnings releases | Present in roughly 4 releases in 10 with numbers, about 1 in 12 with words only; rule-based detection needs work | 7 |
| Pool for Benchmark v0 | Enough if only the later release must postdate the cutoff (about 1,700 to 2,200 pairs with numeric guidance in both); borderline if both must (about 800 to 1,000), growing by about that much each season. Counted on all filers, corrected by a 30-item hand check | 8 |

## Access

Decided by the owner on 2026-11-13: the open-source package `edgartools` (MIT,
https://github.com/dgunning/edgartools). Version 5.62.1 is installed in the conda env `nlab` and
pinned in `requirements-nlab.txt`. It was the latest release at least two weeks old on that day;
6.x, first released on 2026-11-09, moves to a new HTTP client and is left to settle.

Verified by inspecting the installed package with the network blocked: 8-K objects expose `items`
and `press_releases`; filings expose `attachments`, `exhibits`, `header`, `text` and
`period_of_report`; companies expose `sic`, `tickers` and `get_facts`; the contact string is read
from `EDGAR_IDENTITY` and the cache location from `EDGAR_LOCAL_DATA_DIR`.

First live check, 2026-11-13, on Microsoft's earnings 8-K of 2026-10-28 (accession
0001193125-26-436122):

- The acceptance timestamp is exposed to the second, twice: the bulk submissions data give it in
  UTC (`2026-10-28 20:04:44+00:00`), the filing header in US Eastern time without a zone
  (`2026-10-28 16:04:44`). The two agree. Use the UTC field.
- Item codes come with the filing list (`2.02,9.01`), so no per-filing request is needed to find
  earnings releases or hard events.
- The press release is attachment EX-99.1 and `press_releases[0].text()` returned 33,798
  characters.
- Microsoft's release contains no guidance: it guides on the call. Releases without guidance are
  part of what the guidance census below counts.
- edgartools limits itself to 9 requests a second by default (`EDGAR_RATE_LIMIT_PER_SEC`). The
  census scripts set 5.

## 1. Disclosure text

Covered by the access check above: 8-K earnings releases and their EX-99.1 are retrievable with
timestamps. 10-Q and 10-K text has not been pulled yet.

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

## 3. Fundamentals as filed (SEC XBRL)

Not started. SEC's bulk `companyfacts.zip` was 1,425,313,725 bytes on 2026-11-13. Whether it
keeps first-filed values (it lists every filing's value with its accession number and filing date)
is the thing to verify.

## 4. Failure events: hard-event census

Script: `research/experiments/exp0002_edgar_census.py hard-events` (EXP-0002), run 2026-11-13.
Source: SEC's bulk submissions archive, `submissions.zip` as published 2026-11-12 04:31 UTC
(1,574,117,096 bytes, 997,850 files), stored on the external drive. Counts are read offline from
each company's filing list, so no per-filing request was made.

**Universe.** Companies that filed an earnings release (an Item 2.02 8-K) in the 365 days before
the window opened: 4,227 for the post-cutoff window, 4,327 for the year before. This is the
benchmark's population, defined point-in-time. Today's listing status is not used as a filter: the
archive records only current exchanges, so it drops companies that failed and were delisted. For
Item 1.03, 21 companies filed in the post-cutoff window but only 6 are listed today.

| Item | Post-cutoff, 2026-07-01 to 2026-11-11 (134 days) | Year before, 2025-07-01 to 2026-06-30 | Annualised share of universe, post / before |
|---|---|---|---|
| 1.03 bankruptcy or receivership | 14 companies (21 among all filers; 28 filings) | 36 (50; 70) | 0.90% / 0.83% |
| 2.06 material impairment | 12 (15; 17) | 56 (62; 64) | 0.77% / 1.29% |
| 3.01 delisting notice or transfer | 265 (421; 505) | 610 (840; 1,310) | 17.08% / 14.10% |
| 4.02 non-reliance on prior financials | 17 (39; 39) | 59 (99; 103) | 1.10% / 1.36% |

Earnings releases, the raw material for Benchmark v0: 7,244 Item 2.02 8-Ks from 3,915 companies
after the cutoff; 16,889 from 4,227 companies in the year before.

What this settles:

- **Item 1.03 matches the literature's base rate** (0.36 to 1.53% of CRSP firms a year,
  `../literature/streams/06_distress.md`): about 0.9% of the universe a year, so 14 events in the
  clean window so far. Failure prediction stays exploratory.
- **Item 3.01 is not a failure event as it stands.** At 14 to 17% of the universe a year it is
  far above any failure base rate. Inference, not yet checked against the texts: most are notices
  of a curable listing deficiency, such as a minimum bid price, or voluntary transfers between
  exchanges, both of which the item covers (SEC Form 8-K instructions). The hard tier needs 3.01
  split by text into deficiency notice, delisting determination and voluntary transfer before it
  is used.
- **Sub-items are not in the metadata.** The filing list gives item codes only; 1.03(a) against
  1.03(b), and the kinds of 3.01, need the text.
- **Amendments are few** (8-K/A: 4 of 3.01, 2 of 4.02 after the cutoff) and are counted apart.

Limits: the archive keeps each company's most recent filings (about 1,000) in the main file, so a
very high-volume filer could be truncated in the year-before window; the overflow files were not
read. Size bands use SEC's filer category, which is missing for some companies ("unknown").

## 5. Returns including delisted stocks

Not started.

## 6. Consensus estimates

Not started.

## 7. Guidance census

Script: `research/experiments/exp0002_edgar_census.py guidance` (EXP-0002), run 2026-11-13.

**Sample.** Listed companies (NYSE, Nasdaq and others, by today's listing) with at least 8
earnings 8-Ks in the bulk archive, stratified by SEC filer category and drawn with seed 20261113:
17 large accelerated filers, 17 accelerated, 16 non-accelerated or smaller. For each, the press
release (EX-99.1) of its last 8 earnings 8-Ks: 400 releases, 303 before the cutoff and 97 after.
One release had no EX-99.1. Texts are stored on the external drive (19 MB).

**Method.** Keyword rules, not a model, flag each release as `numeric` (a sentence with a guidance
word, a future period and a number), `qualitative_only` (guidance word and future period, no
number) or `none`, after dropping the safe-harbor section. The rules were checked by hand on
pre-cutoff releases only (49 drawn at random, seeds 20261113 and 20261114), so no model on the
evaluation roster read a post-cutoff release. The check was done by Claude, which is likely on the
roster; that is why it stayed on pre-cutoff documents. The owner should repeat it on a fresh
sample.

**Raw flags.**

| | Releases | Numeric | Qualitative only | None |
|---|---|---|---|---|
| All | 400 | 224 | 83 | 92 |
| Before the cutoff | 303 | 166 (55%) | 66 (22%) | 70 (23%) |
| After the cutoff | 97 | 58 (60%) | 17 (18%) | 22 (23%) |
| Large accelerated | 136 | 89 | 24 | 23 |
| Accelerated | 136 | 89 | 22 | 25 |
| Non-accelerated or smaller | 128 | 46 | 37 | 44 |

**How good the rules are** (hand check, pre-cutoff):

| Flag | Checked | Correct | What went wrong |
|---|---|---|---|
| `numeric` | 25 | 17 have in-scope numeric guidance; 1 more has a numeric outlook for an out-of-scope metric (year-end cash) | 7 wrong: a past "guidance" reference, a preliminary result for a finished year, a savings target, a stock-award target, tables of past figures; one release had only qualitative guidance |
| `qualitative_only` | 12 | 3 have qualitative guidance | 1 had numeric guidance the rule missed (its numbers sat in sentences without a guidance word, under an "Outlook" heading); 8 had none: deal closings, clinical milestones, credit-loss language |
| `none` | 12 | 12 | None missed |

**Corrected estimate, before the cutoff.** Applying those rates to the raw flags: about 39% of
releases carry in-scope numeric guidance, about 8% only qualitative guidance, and about half none.
The check samples are small, so these are planning values with wide error, not measurements. The
39% is close to the 37% of releases with an I/B/E/S management forecast reported by Bozanic,
Roulstone and Van Buskirk 2018 (`../literature/papers/bozanic-2018-other-forward-looking-statements.md`).

**Other observations.**

- Smaller companies guide less: 36% of their releases are flagged numeric against 65% for the two
  larger bands, before correction.
- Updating routine by raw flags, of 50 companies: 21 flagged numeric in at least 7 of 8 releases,
  20 in some, 9 in none. False positives inflate the first group.
- Revision words in releases with any guidance flag (307): "raised" 42, "reaffirmed" 39,
  "lowered" 14, "withdrawn" 3. The words are crude; one release that cut its range said "revised".
- Large companies may guide only on the call: Microsoft's release has no guidance (Access).
- Pre-announcements are Item 2.02 8-Ks too (Orthofix, 2026-04-09: preliminary first-quarter sales
  and a reaffirmed outlook).

**What it means for the plan.**

1. **The qualitative-only stratum is thin.** About 1 release in 12 has guidance in words only.
   Revision 2 of plan v2 made qualitative guidance a core stratum; the stratum should be redefined
   as qualitative statements anywhere, including modifiers inside numeric guidance ("toward the low
   end"), and its size counted before the test set is drawn.
2. **The pool is large enough on current estimates** (superseded by the full count, section 8). 7,244 earnings 8-Ks from 3,915 companies were
   filed after the cutoff (section 4). At about 39%, roughly 2,800 carry numeric guidance. If both
   documents of a pair must postdate the cutoff, about 1,300 to 1,500 pairs exist so far (about 1.85
   releases per company in the window); if only the later one must, about 2,800. Each season adds
   about 3,500 releases. Both figures are extrapolated from 50 companies and need the full count.
3. **The rules need three fixes before the full count**: read numbers inside an outlook section even
   without a guidance word; drop references to finished periods; drop expectations that are not
   results (closings, trials, savings targets, award targets).
4. **A design decision is needed**: whether a test pair needs both documents after the cutoff, or
   only the later one. The label depends on the later document, but the earlier one may be
   remembered.

## 8. Full count of guidance pairs

Script: `research/experiments/exp0003_guidance_pairs.py` (EXP-0003), run 2026-11-13.

**What was counted.** Every earnings 8-K (Item 2.02) filed from 2026-07-01 to 2026-11-10, plus
each of those companies' last earnings 8-K before the cutoff: 11,073 filings from 3,915 companies,
fetched from EDGAR with 0 lasting errors (6 SEC 503s were retried). 120 filings have no press
release exhibit. 79 companies were dropped as co-registrants: a subsidiary that files the same 8-K
as its parent (an airline and its holding company, a utility and its parent). That leaves 10,836
releases from 3,836 companies, 7,086 of them after the cutoff. A pair is two consecutive releases
of one company with the later one after the cutoff.

**Rules v2.** The three fixes from section 7: numbers inside an "Outlook" or "Guidance" section
count without a guidance word; statements about periods already ended are dropped; expectations
that are not results metrics are dropped. On the 49 dev releases of section 7 they agree with the
hand labels on 43 (v1: 31). On a fresh hand check of 30 pre-cutoff releases not used to build them:

| Hand label ↓ / rule flag → | Numeric | Qualitative only | None |
|---|---|---|---|
| Numeric | 10 | 0 | 0 |
| Qualitative only | 1 | 4 | 1 |
| None | 2 | 5 | 7 |

So a `numeric` flag is right about 10 times in 13, a `qualitative_only` flag 4 times in 9, a
`none` flag 7 times in 8. The rules still miss no numeric guidance in this check, but over-call
words-only guidance. One miss (a "Guidance:" heading) was fixed after the check.

**Raw flags and counts.**

| | Releases or pairs | Numeric | Qualitative only | None |
|---|---|---|---|---|
| Releases after the cutoff, with text | 6,993 | 3,307 (47%) | 586 (8%) | 3,100 (44%) |
| Last release before the cutoff | 3,723 | 1,739 (47%) | 309 (8%) | 1,675 (45%) |

| Pairs | All pairs with text | Numeric in both | Guidance of any kind in both | Guidance in one only |
|---|---|---|---|---|
| Later release after the cutoff | 6,839 | 2,887 | 3,441 | 756 |
| Both releases after the cutoff | 3,147 | 1,338 | 1,593 | 379 |

By filer category, post-cutoff releases flagged numeric: large accelerated 59%, accelerated 48%,
non-accelerated or smaller 30%.

**Corrected for the rules' errors.** Each flag is replaced by the probability of each true label
from its column of the hand-check table. For pairs, two bounds: errors independent between a
company's two releases (lower), or errors that repeat across them because the releases share a
template (upper: each pair counts the smaller of its two releases' probabilities, so raw numeric pairs
times 10/13). The truth is likely nearer the upper bound. The 90%
intervals in brackets come from resampling the 30-item check under independence and are wide.

| | Estimate |
|---|---|
| Post-cutoff releases with numeric guidance | about 2,540 of 6,993, 36% (1,850 to 3,280) |
| Post-cutoff releases with words-only guidance | about 900, 13% (460 to 1,910) |
| Pairs, later release after the cutoff, numeric in both | 1,700 to 2,200 (independence interval 810 to 2,380) |
| Pairs, both after the cutoff, numeric in both | 800 to 1,030 (independence interval 380 to 1,100) |
| Pairs, both after the cutoff, guidance of any kind in both | 1,085 to 1,440 (independence interval 720 to 1,525) |

**Caveats.**

- The error rates come from 30 pre-cutoff releases read by Claude and are applied to post-cutoff
  releases. The owner's own check, on a fresh sample, would replace them.
- 81 numeric-numeric pairs are less than 60 days apart: pre-announcements and restated releases
  are Item 2.02 filings too, so a pair is not always one quarter to the next.
- "Guidance in one only" (initiated or dropped) is the least reliable count: under independence a
  qualitative false positive on either side makes one, so the corrected figure (about 2,100 for
  later-after pairs) is likely far too high; the raw 756 is closer.
- Both-after pairs so far come from one transition only (second-quarter to third-quarter
  releases). The fourth-quarter season (January to March 2027) carries annual guidance and its
  initiations, so it will not look like this one.

**What it means for the plan.**

1. **If only the later release must postdate the cutoff, the pool is ample.** Some 1,700 to 2,200
   pairs with numeric guidance in both, enough for the 785 pairs one comparison needs at a 25%
   disagreement rate (plan v2, revision 5), with room for a development split.
2. **If both must postdate it, the pool is borderline today.** About 800 to 1,000 such pairs exist;
   each earnings season should add roughly as many again. Waiting one season (to about March 2027)
   roughly doubles it.
3. **The words-only stratum is still thin and the rules cannot measure it.** The rules over-call it
   by about half, so its size needs hand labels (or the redefinition in section 7) before any test
   set is drawn from it.
4. The open decision from section 7 (one or both releases after the cutoff) now has numbers
   attached; it is for the owner.

## 9. Go / no-go per candidate task

| Task or outcome | Status |
|---|---|
| Guidance revision on earnings releases (Benchmark v0) | Go: about 1,700 to 2,200 numeric pairs with the later release after the cutoff, 800 to 1,000 with both (section 8) |
| Qualitative-only guidance as a stratum | Thin; redefine (section 7) |
| Hard events: 1.03, 2.06, 4.02 | Go, as exploratory outcomes |
| Hard events: 3.01 | No-go until split by text |
| Transcript tasks | Deferred (section 2) |

## 10. Storage

So far 1.5 GB (bulk submissions archive), 19 MB (400 census press releases), 573 MB (10,841
releases for the full count) and 8 MB (targets, fetch log, flags, counts) on the external drive.

