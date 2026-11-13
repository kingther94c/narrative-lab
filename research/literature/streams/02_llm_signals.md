# Stream 02: LLMs extracting financial signals

Twelve papers triaged, three deep-read (2026-11-12). Short names are notes in `../papers/`; rows are in `02_llm_signals.csv`.

## What the stream establishes

1. **Empirical finding.** LLM measures beat dictionaries and BERT-class models downstream, by little. A ChatGPT capex-plan score keeps t = 13 beside a fine-tuned RoBERTa score, while R² moves from 0.573 to 0.575 (jha-2024). GPT risk measures subsume bigram measures for volatility (https://arxiv.org/abs/2310.17721).
2. **Empirical finding.** Label accuracy and economic association differ. On PhraseBank, Qwen 2.5 ties FinBERT-Tone and Claude Opus 4.5 (92 to 94%) and dictionaries score 54 to 65%. On 221 8-K press releases, no model's sentiment relates to next-day returns (bisharat-2026).
3. **Convention.** Studies validate by downstream association, not against gold labels. Jha et al. check only that answer and explanation agree. The exception found is de Kok 2025: 96% accuracy on non-answers (abstract only, https://doi.org/10.1287/mnsc.2023.03253).
4. **Empirical finding.** Forecasts worsen after the cutoff. GPT-4 Turbo's EPS error rises (t = 3.10) while its confidence does not fall; direction is 48 to 49% correct against analysts' 71% (li-2024). The result it could not reproduce, https://arxiv.org/abs/2407.17866, was withdrawn by its authors in February 2025.
5. **Empirical finding.** Return effects decay: the headline strategy's Sharpe ratio fell from 6.54 (2021Q4) to 1.22 (January to May 2024) and is unprofitable at 20 bp costs (https://arxiv.org/abs/2304.07619).

## Design defaults

- **Extraction confirmatory, interpretation anchored, returns exploratory: supported** by claims 2, 4 and 5. The CFO-survey anchor explains 1.4% of variance (jha-2024), so anchored tests need large samples.
- **Each feature alone, with its own quote: supported by practice, untested.** Single-question prompts with explanations are usual (jha-2024); nobody compares joint with separate extraction. GPT's chosen sentences skew early and long (li-2024), so log each quote's position.
- **Pairs of outlook passages: not addressed directly.** Forecasts sit in 5.4% of press-release sentences and three-quarters of call chunks carry no capex signal, which favours passages (li-2024, jha-2024). Only https://arxiv.org/abs/2510.03195 compares consecutive quarters, on S&P 100 call transcripts.

## Gaps that suggest an experiment

- **Open question.** Four targeted searches found no study scoring LLM extraction of guidance tuples or revision classes against gold labels. Benchmark v0 fills this.
- Joint versus separate feature extraction, scored on accuracy: add as a prompt-factor level.
- Extraction accuracy, not forecasting, before and after a cutoff: extend WP3 probe 4.

## Already answered; do not redo

- Dictionary versus transformer on sentence sentiment (https://doi.org/10.1111/1911-3846.12832; bisharat-2026).
- Whether headline sentiment predicts next-day returns (https://arxiv.org/abs/2304.07619).

## Changes to the plan

- Sentence sentiment is near ceiling for open-weight models (hypothesis from claim 2). Start the headroom pilot on the qualitative-guidance stratum.
- Keep "no guidance stated" as its own class; Jha et al. fold "no information" into zero.
- Stratify anchored tests by the size of the numeric change (bisharat-2026).
- Drop the withdrawn arXiv 2407.17866 from the seeds.
- Read de Kok 2025 in full; SSRN and INFORMS refused automated access.
- Chen, Kelly and Xiu 2022 is unverified and unused.
