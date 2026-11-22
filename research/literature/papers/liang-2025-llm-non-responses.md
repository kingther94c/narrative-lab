# How do managers' non-responses during earnings calls affect analyst forecasts: a measurement by large language models

- **Citation:** Qingwen Liang and Matias Carrasco Kind (2025). arXiv 2505.18419 v1, 23 May 2025
  (econ.GN). Working paper, not peer reviewed. Version read: v1 PDF (54 pages; no HTML version).
- **Link:** https://arxiv.org/abs/2505.18419
- **Stream:** 11, call language and Q&A behaviour
- **Verified against source:** yes, 2026-11-22, against the full v1 text (extracted from the PDF
  by script). The online appendix with the prompt and stability tables is referred to but was not
  found in the PDF read; the prompt is said to be in Appendix A.

## Question
Do managers' non-responses (NORs) in the Q&A, measured with LLMs, make analysts' forecasts worse
or better: a bad-news signal that analysts read, or confusion that adds uncertainty?

## Data
- S&P 500 earnings call transcripts from S&P Capital IQ via WRDS, 2019Q1 to 2024Q3: 10,976
  transcripts with 107,564 analyst-management exchanges. The latest version of each transcript
  is kept.
- Final regression sample: 4,284 calls of 268 firms after merging with Compustat, CRSP, I/B/E/S and
  13F data.
- The unit is the whole back-and-forth with one analyst ("Q&A exchange"), not a single
  question-answer pair.

## Method
- **Models.** "Chat-GPT4" through the Azure and OpenAI APIs (exact model version not stated) and
  Llama 3.3 run locally; temperature, frequency and presence penalties 0; JSON output.
- **Prompt.** Few-shot (two demonstrations), three tasks in one prompt: (1) identify NORs and quote
  the supporting text; (2) classify each as Refusal, Lack of Info, Legal Affairs, Recall ("will get
  back to you") or Irrelevant (rambling); (3) score the answer 0 to 10 on Gricean quantity,
  relevance and clarity. The prompt definition: refusals for any reason, irrelevant answers, or
  promises to call back.
- **Validation.** 200 random exchanges hand-coded by the authors' research assistants (explicit
  refusals plus a subjective call on incomplete or irrelevant answers). The prompt was revised
  until overlap with these labels "surpasses 70%". The authors checked 200 of GPT-4's quoted
  excerpts by hand. Stability: 100 regenerations on 100 exchanges per model.
- **Tests.** Call-level count of NORs (NORFirm) regressed on analyst forecast error, dispersion and
  uncertainty, with firm and quarter fixed effects, clustered by firm; cross-sectional splits;
  post-announcement drift, volatility, volume and spreads over 60 days.

## Outcome variable and horizon
Absolute error of the consensus issued after the announcement against reported quarterly EPS,
scaled by price; dispersion of forecasts after the call; a combined uncertainty measure (Bozanic
and Thevenot 2015). The text does not say clearly which quarter's EPS the post-call forecasts
target. Market outcomes over 60 days.

## Result
- **Measurement (verified fact from the paper).** GPT-4 flags 15,645 exchanges (14.5%), Llama 3.3
  flags 12,689 (11.8%): GPT-4 finds 23.3% more. They disagree most on "Recall": 4,465 against 622.
  Formatting failures: 416 (GPT-4) and 335 (Llama). Regeneration agreement with the first run:
  76.22% (GPT-4) and 69.11% (Llama), lower on exchanges without NORs. No precision, recall or
  kappa against the 200 human labels is reported beyond the 70% overlap target.
- **Determinants (empirical finding).** Questions with more negative tone, more forward-looking
  content and fewer requests for uncertainty-related information draw more NORs, consistent with
  Barth, Mansouri and Woebbeking (2023). The model's own quantity and relevance scores are lower
  when it flags a NOR, which the authors call internal coherence.
- **Analysts (empirical finding).** One SD more NORs per call (1.435) raises the absolute forecast
  error by 0.0007 of price, 11.24% of its mean; dispersion and uncertainty by about 5.7% of their
  means (1% level). Only direct refusals drive this; among the Gricean scores only relevance is
  related to forecast quality. Effects are concentrated in multi-industry firms, firms with lower
  institutional ownership (the abstract says higher; the body says fewer), high R&D, and COVID-era
  calls.
- **Market (empirical finding).** More NORs go with stronger post-announcement drift up to 60 days,
  higher volatility and volume, and wider spreads.
- The authors read this as a "confusion effect": refusals raise uncertainty rather than giving
  analysts a clear bad-news signal. They do not test whether NORs predict the sign of future
  earnings or sales.

## Look-ahead and memorisation
Not addressed. The sample (2019 to 2024) lies inside or near the training data of the models
used, and the firms are S&P 500 names. The authors discuss replicability and hallucination, not
recall of later outcomes.

## What it settles for us
- **LLM non-answer labels are feasible on exactly our universe (supports, with a warning).** But
  two strong models disagree on about a fifth of flags and on the subtype mix, and a single model
  repeats its own label only about three times in four. A checklist item "did management refuse?"
  needs a fixed rubric, a human-labelled check set and a stability test.
- **Direction is unclear (contradicts a simple rule).** NORs here signal uncertainty, not a
  direction. For a probability of acceleration, a refusal should widen uncertainty more than move
  the point estimate, unless it is a direct refusal to a forward-looking question.
- **Subtypes matter.** "Lack of info", "legal" and "get back to you" behave differently from
  direct refusals; only the last is related to forecast quality.
- **Needs the Q&A.**

## Limits
- Weak validation: no accuracy statistics against the hand-coded set, which is small and coded by
  the authors' team.
- GPT-4 version unstated; no post-cutoff check.
- Outcome definitions are ambiguous in places, and the abstract and body disagree on the
  institutional-ownership split.
- Unpublished working paper.
