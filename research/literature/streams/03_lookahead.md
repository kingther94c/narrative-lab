# Stream 03: look-ahead bias and memorisation

Sources checked 2026-11-12. Notes are in `../papers/`; all 13 papers are in `03_lookahead.csv`.

## What the stream establishes

- **Empirical finding.** Models recall pre-cutoff values and nothing after: GPT-4o's S&P 500 error is 0.61% before October 2023 and 16.87% after. Recall is weaker for small firms (`lopez-lira-2025`).
- **Empirical finding.** Recall fades before the stated cutoff. Llama-3.3-70B's recall propensity is 0.88 for 2020, 0.016 for 2023 and zero for 2024 (`gao-2025`, Figure IV; our reading).
- **Empirical finding.** Masking transcripts fails: firms re-identified in 70% (https://conference.nber.org/conf_papers/f205530/f205530.pdf), 31% to 66% by size (`lopez-lira-2025`), 67% after entity masking and 9% after LLM rewriting, with industry still at 44% (`wu-2025`).
- **Open question.** Engelberg et al. report chance-level re-identification on news (http://asaf.manela.org/); why transcripts differ is unresolved.
- **Empirical finding.** Masking removes signal even after the cutoff (`wu-2025`).
- **Formal tests.** Gao's interaction test needs outcomes, entity-date pairs and answer-token probabilities. Sarkar–Vafa's needs events assumed unpredictable. Membership-inference scores add nothing beyond the cutoff date (https://arxiv.org/abs/2603.26797).
- **Verified fact (model cards).** Point-in-time models can be downloaded; the largest checked has 1.55B parameters and the latest vintage is 2024. ChronoBERT, ChronoGPT and ChronoGPT-Instruct: 1999 to 2024, MIT (https://huggingface.co/manelalab). DatedGPT: 2013 to 2024, no licence stated (https://huggingface.co/datedgpt). StoriesLM-v2 encoders: 1900 to 2024. TiMaGPT: CC0.

## Design defaults

- **Test after every cutoff: supported** (`lopez-lira-2025`, `gao-2025`). Post-cutoff data must be the primary sample.
- **Training earlier and company-disjoint: not addressed.** This literature covers pretraining leakage only.
- **No masking: supported.** The strongest reason for this project: neutering masks numbers, and the numbers are the guidance label (our inference from `wu-2025`).
- **Contamination labels: supported as convention.** Add the future-invariance question from `lopez-lira-2025`: "bounded" suits extraction; tone or narrative tasks on pre-cutoff text are "contaminated".
- **Memorisation probe: supported; the design should change.**

## Probe recommendation

- Give only company and fiscal quarter. Ask whether guidance was raised, lowered, maintained or "unknown"; add a numeric-range variant.
- Record answer-token probabilities for local models and repeated samples for commercial ones.
- Sample quarters from at least three years before the cutoff to after it, stratified by firm size. Quarters adjacent to the cutoff will show no gap even in a contaminated model.
- Score against a persistence baseline, since guidance changes slowly.
- Treat a null as a lower bound, never as "clean".

## Gaps

- **Hypothesis, untested in this stream:** recall inflates extraction accuracy and favours large models. Experiment: regress open-book extraction correctness on closed-book recall propensity, item by item.
- No study probes recall of guidance or as-filed fundamentals.

## Plan changes

- Roadmap link: Gao et al. is now "Detecting Lookahead Bias in LLM Forecasts" (v2).
- Methodology §3: masked transcripts are not always identifiable; LLM rewriting cuts re-identification to 9%. Rest the rule on information loss.
- Point-in-time models cannot be the extractors: context is at most 2,048 tokens and ChronoGPT-Instruct wins 13% to 17% of comparisons against a 1.8B chat model (https://arxiv.org/abs/2510.11677).
