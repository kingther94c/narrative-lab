# Evaluating Financial Sentiment in the Age of AI

- **Citation:** Bisharat, A. and Hean, O. (2026). Preprint, arXiv 2609.20198 v1, submitted 29 July 2026 (draft dated 17 July 2026). Not peer reviewed.
- **Link:** https://arxiv.org/abs/2609.20198
- **Stream:** 02, LLMs extracting financial signals
- **Verified against source:** yes, 2026-11-12, against the full text of v1 (PDF, text extracted by script). Tables 2 and 3 and the figures are images; only numbers repeated in the prose are quoted.

## Question

Do general-purpose open-weight LLMs measure financial sentiment better than dictionaries and finance-specific transformers, judged two ways: agreement with human labels ("linguistic validity") and association with earnings surprises and returns ("economic validity")?

## Data

- Financial PhraseBank, the `sentences_allagree` subset, n = 2,264.
- 221 quarterly earnings press releases, each Exhibit 99.1 of an 8-K, from 2022 to mid-2026, for 15 large US firms in seven sectors. The firms were chosen purposively and the authors call the sample "illustrative rather than representative". EPS surprise uses the Yahoo Finance consensus; the return uses adjusted closing prices.

No delisted firms: all 15 are large survivors.

## Method

Twelve models in three classes. Dictionaries: VADER, TextBlob, Loughran-McDonald. Finance transformers: FinBERT, FinBERT-Tone, FinancialBERT, DistilRoBERTa-Financial, RoBERTa-Large-Financial. Open-weight LLMs, zero-shot with one common three-class prompt: Llama 3.2, Gemma 3, Qwen 2.5, Mistral. Claude Opus 4.5 is added as a closed-model reference.

Label agreement is scored by accuracy, macro-F1 and class F1, with McNemar's test for paired accuracy differences. Economic association is a Spearman correlation with a 95% bootstrap interval from 2,000 event-level resamples.

Not recorded in this reading: the parameter sizes of the open-weight models, and how sentence-level output is aggregated to a release.

## Outcome variable and horizon

Agreement with PhraseBank labels; EPS surprise (%) for the announced quarter; raw return on the first trading day after the announcement.

## Result

All are empirical findings.

- Dictionaries reach 54 to 65% accuracy on PhraseBank. Every finance transformer exceeds 90%; two of them were fine-tuned on PhraseBank, which the authors flag.
- Qwen 2.5 scores 92.1%, not significantly different from FinBERT-Tone at 91.7% (McNemar, p > 0.05).
- Claude Opus 4.5 scores 93.6% (macro-F1 93.3%), not significantly different from Qwen 2.5.
- By sentence type (negation, uncertainty, jargon, length), dictionaries have the highest error rate throughout and open-weight LLMs sit between dictionaries and finance transformers.
- No model, Claude included, has a statistically significant correlation with next-day returns.
- Several finance transformers correlate significantly with EPS surprise, FinancialBERT most strongly. Mistral and Llama 3.2 are positive and less precise. The correlations are shown in figures and none is quoted here.
- The association with EPS surprise is concentrated in the top and bottom surprise quartiles. The authors describe this analysis as exploratory.

## Look-ahead and memorisation

Not addressed. The 15 firms are among the most covered in the world and most of the sample predates the cutoffs of the models used. PhraseBank contamination is acknowledged only for the two transformers fine-tuned on it.

## What it settles for us

- **Endpoint hierarchy (supports).** Agreement with labels and economic association come apart, so a study has to say in advance which one is confirmatory. Ours names extraction accuracy.
- **Return prediction exploratory (supports).** Thirteen models, no association with next-day returns.
- **Numeric anchor (supports, with a design hint).** The earnings-surprise anchor separates models only where the number is large. Anchored tests should be stratified by the size of the numeric change.
- **Headroom and Goal C (changes emphasis).** Three-class sentence sentiment is near the ceiling for a 2026 open-weight model and for a frontier commercial one. A tone task would not separate systems, and a non-inferiority result on it would say little. This backs guidance revision and its harder strata as the benchmark task.
- **Reusable.** The baseline ladder (dictionary, finance transformer, zero-shot open-weight, commercial) is the Phase I ladder; McNemar's test fits our paired primary endpoint; error rates by negation and uncertainty are a ready-made difficulty stratification.
- **Not addressed.** Per-feature extraction, evidence quotes, consecutive document pairs.

## Limits

- 221 events from 15 megacaps, purposively chosen.
- No contamination control; PhraseBank is old and public.
- Raw rather than abnormal next-day returns; consensus from Yahoo Finance.
- Whole-release sentiment only, bivariate correlations, no controls.
- Preprint; key numbers sit in figures.
