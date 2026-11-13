# Stream 05: comparing adaptation methods

Read 2026-11-12. Rows: `05_adaptation.csv`. Notes: `../papers/`.

## What the stream establishes

- **Empirical finding.** With model and examples held equal, fine-tuning and in-context learning perform alike; earlier verdicts compared unequal model sizes, and the checkpoint-selection rule changes how small fine-tuned models rank (mosbach-2023).
- **Empirical finding.** Outside finance, fine-tuning and retrieval have been crossed on open and commercial models (balaguer-2024; [Sturm 2026](https://arxiv.org/abs/2605.09533)). Balaguer's GPT-4 gains are additive on accuracy (75, 80, 81, 86) and sub-additive on "fully correct" (36, 60, 45, 61).
- **Empirical finding.** Fine-tuning without retrieved context, then adding retrieval, can hurt: four of five datasets in [RAFT](https://arxiv.org/abs/2403.10131); all three models on current events in [Ovadia 2023](https://arxiv.org/abs/2312.05934).
- **Empirical finding.** In finance, tuned small models approach or pass untuned commercial ones on tagging, NER and numeric QA (phogat-2024; [FinLoRA](https://arxiv.org/abs/2505.19819); [Li 2023](https://arxiv.org/abs/2305.05862)). Neither reports intervals, and FinLoRA's XBRL value extraction is at 97 to 99% for commercial and tuned models alike.
- **Convention.** A model under test writes the training or test data and often judges (phogat-2024, balaguer-2024, Sturm). "Parity" means a non-significant difference (Sturm) or a point estimate (Phogat).
- **Empirical finding.** Code execution raised Codex accuracy on FinQA from 40.4 to 64.5 ([Chen 2023](https://arxiv.org/abs/2211.12588)).
- **Open question.** Whether tools help on non-numeric items.

## Design defaults

- **Full factorial, three retrieval levels: supported.** [FinanceBench](https://arxiv.org/abs/2311.11944) used the same levels (GPT-4-Turbo: 9% closed book, 19 to 50% retrieved, 85% oracle).
- **Same development set and evaluation count: supported.** Phogat searched LoRA settings on a development split but imported its GPT-4 baselines; [Huang 2026](https://arxiv.org/abs/2606.08051) chose the best of 12 checkpoints on test.
- **Logit scale and strata: not addressed.** No paper models interactions; Balaguer's differs by metric.
- **Commercial models without the fine-tuning factor: supported, reason amended.** Vendor fine-tuning is not absent (GPT-4, GPT-4o and Gemini were tuned) but is opaque and on another base model; Mosbach excluded GPT-3 for that.
- **Non-inferiority with a preset margin: not addressed.** Nearest is [Pecher 2025](https://arxiv.org/abs/2402.12819): break-even label counts rise 100 to 200% once variance counts; 4-bit quantisation had negligible impact.
- **Hypothesis, no four-method head-to-head in finance: not refuted** by anything opened. One candidate could not be opened ([Çağlayan 2025](https://ieeexplore.ieee.org/document/11207079/)); no claim rests on it.

## Gaps that suggest an experiment

- The planned four-factor design on narrative items, with intervals.
- Adapters trained with and without retrieved distractors, tested under retrieval.
- A no-tool arm, which Phogat lacks.

## Changes to the plan

1. Specify the fine-tuned level's training prompt: an adapter trained on bare passages confounds the fine-tuning by retrieval cells. Train with supplied and distractor passages.
2. Count checkpoint selection, LoRA search and prompt edits as development evaluations, and never select on test.
3. Run Goal C below ceiling; near 98% any margin passes.
4. Fix prompt levels on the development set: few-shot cut Orca-2 13B from 37.5 to 4.4 on FinQA.
5. Qwen 3.5 4B took LoRA on other hardware (Huang 2026, 96.6 F1); the MLX probe still stands.
