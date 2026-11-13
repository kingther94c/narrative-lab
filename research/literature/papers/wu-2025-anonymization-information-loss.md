# Anonymization and Information Loss

- **Citation:** Ke Wu, Baozhong Yang, Zhenkun Ying and Dexin Zhou (2025). Working paper (Renmin
  University of China; Georgia State University; Baruch College). arXiv 2511.15364. v1 (19
  November 2025) centred on earnings-call sentiment and returns; v2 (5 September 2026) leads with
  credit-rating downgrades. Version read: v2, full text.
- **Link:** https://arxiv.org/abs/2511.15364
- **Stream:** 03, look-ahead bias and memorisation
- **Verified against source:** yes, 2026-11-12 (abstract, sections 3.2, 3.4, 4.1, 4.2, 6.2.1, 7 and
  Table 2 read in the full text; other tables through a machine summary of the HTML)

## Question
Anonymising financial text is used to stop an LLM from recognising the firm. Does it also remove
economic signal, and can that loss be told apart from the removal of look-ahead bias?

## Data
- Text: Seeking Alpha earnings call transcripts for constituents of the iShares Russell 3000 ETF.
  Mean length 9,539 tokens; transcripts over 15,000 tokens are excluded.
- Period: November 2023 to December 2024 (after the models' cutoff) is the main sample. November
  2022 to October 2023 is added for the look-ahead diagnostic, on firms present in both windows.
- Downgrade sample: 2,488 post-cutoff transcripts, excluding utilities and financials and
  requiring an existing S&P rating and controls.
- News: 52,716 Yahoo Finance headlines from the Finnhub API, 30,950 firm-days, November 2023 to
  December 2024.
- Outcomes from S&P ratings, CRSP, Compustat and I/B/E/S.
- Delisted firms: not addressed. The universe is the membership of a current ETF.
- Models: GPT-4o-mini-2024-07-18 (main), GPT-4o-2024-08-06 and o3-mini-2025-01-31, all with an
  October 2023 knowledge cutoff taken from a third-party list.

## Method
- Two anonymisers. **TRF**: named-entity recognition with spaCy `en_core_web_trf`, entities
  replaced by numbered placeholders. **LLM**: GPT-4o-mini masks, a re-identification test is run,
  the text is paraphrased and tested again, for at most three rounds, following Engelberg et al.
  (2025).
- The model scores each transcript three times: raw, TRF and LLM.
- Standalone and horse-race regressions with industry-by-quarter fixed effects, firm controls
  (including Z-score and O-score) and standard errors clustered by industry.
- Look-ahead diagnostic: the score interacted with a pre-cutoff indicator. A positive interaction
  would indicate look-ahead bias.
- **Anonymisation gap**: the absolute difference between the anonymised score, rescaled by its
  correlation with the raw score, and the raw score. It needs no outcome data.

## Outcome variable and horizon
An S&P downgrade within 12 months of the call (3 months as a check). Secondary: announcement
returns, return volatility, capital expenditure, sales growth, value-added growth.

## Result
Empirical findings.

- **Re-identification after anonymisation (Table 2, GPT-4o-mini as attacker).** Firm name: 66.88%
  after TRF, 9.04% after LLM. Ticker: 53.90% and 9.12%. Industry: 50.56% and 44.01%. Date within
  seven days: 6.03% and 2.81%.
- **Downgrades, with controls (Table 3).** One standard deviation of the raw score raises
  downgrade probability by 6.1 percentage points (t = 5.52); TRF 4.7 (t = 4.80); LLM 4.9
  (t = 4.92). In a horse race the raw score keeps 0.073 (t = 3.58) and the anonymised scores fall
  to -0.012 (t = -0.72) and -0.007 (t = -0.52).
- **Look-ahead diagnostic (Table 4).** Interactions with the pre-cutoff year are -0.005
  (t = -0.31), -0.009 (t = -0.59) and -0.010 (t = -0.63). No sign of inflation before the cutoff.
- **Gap (Table 5).** A gap one standard deviation larger cuts the anonymised score's effect by
  about 37% (TRF) and 24% (LLM).
- **Which entities matter (section 5.1).** Keeping only numbers or only agent names recovers the
  most signal; places and other entities recover least. No single category restores the raw
  signal.
- **Returns (section 6.2.1).** Raw sentiment 2.487 (t = 18.83); in a horse race the TRF
  coefficient drops from 2.331 to 0.775, a 67% reduction.
- **Headlines (section 6.3).** In a horse race raw is 0.315 against 0.135 for TRF.
- The pattern holds for GPT-4o and o3-mini.

## Look-ahead and memorisation
The main sample postdates the models' cutoff, so the information loss is measured where look-ahead
cannot operate. The authors warn against reading a fall in predictive power after anonymisation as
proof that look-ahead bias was removed, and cite Lopez-Lira et al. (2025) for the point that
masked text often stays identifiable.

## What it settles for us
- **Masking is not used: supported, for three reasons.**
  - Standard entity masking leaves two thirds of firms identifiable from a transcript.
  - Iterative LLM rewriting cuts that to 9%, but industry is still recovered 44% of the time and
    the signal loss is the same.
  - Numbers carry much of the signal. In a guidance benchmark the numbers are the label, so a
    masked version of the task would not be the same task. This last step is our inference.
- **Test documents postdate every cutoff: supported.** The authors treat a post-cutoff sample as
  the only way to separate information loss from bias removal.
- The pre-cutoff diagnostic covers only the 12 months before the cutoff. Gao et al. (2025) find
  recall already weak in that window, so the null result says little about older documents. This
  is our inference.
- Reusable: the horse-race design for any masked-versus-raw comparison; the gap as a diagnostic
  that needs no outcomes.
- **Open question.** Whether masking degrades extraction accuracy, as opposed to predictive
  signal, is not measured.

## Limits
- All three models come from one vendor and share one cutoff.
- The attacker in the re-identification test is the small model that did the masking; a stronger
  attacker is not tried.
- The downgrade sample covers about 14 months and rated non-financial firms only.
- The framework's two assumptions (the raw score contains everything the anonymised score does;
  the relation is stable across the cutoff) are assumed, not tested.
