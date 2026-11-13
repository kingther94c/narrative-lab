# Fine-tuning Smaller Language Models for Question Answering over Financial Documents

- **Citation:** Phogat, K. S., Puranam, S. A., Dasaratha, S., Harsha, C., Ramakrishna, S. (2024). Findings of EMNLP 2024, pp. 10528-10548, doi 10.18653/v1/2024.findings-emnlp.617. Version read: arXiv 2408.12337v1 (22 August 2024), HTML full text.
- **Link:** https://aclanthology.org/2024.findings-emnlp.617/ (full text: https://arxiv.org/html/2408.12337v1)
- **Stream:** 05, comparing adaptation methods
- **Verified against source:** yes, 2026-11-12, against the ACL Anthology page, the arXiv abstract page and the HTML full text. Read through an automated page reader; table values are as it returned them and were not re-keyed from the PDF.

## Question
Can open-weight models of 4B to 14B parameters, fine-tuned on programs written by GPT-4, reach GPT-4's accuracy on multi-step numeric questions over financial reports?

## Data
FinQA (6,251 train, 883 dev, 1,147 test), ConvFinQA (2,737, 300, 421) and the arithmetic questions of TATQA (4,992, 550, 718). All are built from published company reports; the paper says nothing about periods or delisted firms. FinQA is scored on its test split; the other two on their official dev splits, with 10% of train held out for development. The gold passage and table are placed in the prompt. Nothing is retrieved.

## Method
- Students: Mistral 7B, Orca-2 7B and 13B, phi-3-mini (3.8B), phi-3-medium (14B). Teacher: GPT-4.
- Training data: GPT-4 writes a commented Python program for each training question from a 4-shot program-of-thought prompt that includes the gold expression as a hint. Programs whose executed result is wrong are dropped. Training sizes listed later are 5,698 (FinQA) and 2,550 (ConvFinQA).
- Fine-tuning: LoRA, rank 512, alpha 1024, all linear layers, 6 epochs, one A100 80GB. Learning rate and rank were searched on the dev split (three rates, four ranks).
- Every system answers by generating Python that is run by an interpreter, so the tool is always on.
- Baselines: each student zero-shot and 4-shot. GPT-3.5 and GPT-4 numbers are copied from the authors' 2023 paper, not re-run.
- A second analysis uses GPT-4 as judge of concept understanding and entity extraction, with 50 low-rated samples per model checked by hand.

## Outcome variable and horizon
Execution accuracy of the generated program against the gold answer. No horizon.

## Result
Accuracy in percent (zero-shot, few-shot, fine-tuned):

| Model | FinQA | ConvFinQA | TATQA |
|---|---|---|---|
| Mistral 7B | 41.58, 50.82, 76.63 | 31.82, 18.52, 76.48 | 66.01, 66.85, 88.71 |
| Orca-2 7B | 2.78, 15.34, 71.57 | 2.61, 10.68, 70.30 | 4.59, 26.88, 88.57 |
| Orca-2 13B | 37.49, 4.36, 73.75 | 28.03, 11.88, 75.77 | 44.29, 17.83, 88.86 |
| phi-3-mini 3.8B | 57.62, 42.45, 73.49 | 48.21, 41.33, 76.00 | 78.27, 59.33, 90.52 |
| phi-3-medium 14B | 70.35, 66.95, 77.59 | 59.38, 60.09, 81.94 | 85.37, 76.32, 93.73 |
| GPT-3.5 Turbo | 66.52, 67.39, n/a | 67.45, 65.79, n/a | 85.00, 74.75, n/a |
| GPT-4 (teacher) | 77.51, 78.46, n/a | 76.95, 82.42, n/a | 93.00, 91.89, n/a |

- Empirical finding: after fine-tuning the students span 71.6 to 77.6 on FinQA against 2.8 to 70.4 zero-shot. Fine-tuning closes most of the gap between small models and most of the gap to GPT-4.
- Empirical finding: few-shot prompting lowered accuracy for three of five students on FinQA (Orca-2 13B from 37.49 to 4.36).
- A 1,500-example FinQA subset came within 3 to 8 points of full-data training.
- No intervals, tests or seeds. On 1,147 FinQA items a 95% interval is about ±2.4 points (my calculation), so "phi-3-medium matches GPT-4" (77.59 against 77.51 or 78.46) and the ordering of the fine-tuned students are not established. The authors themselves say small differences may reflect hyperparameters that are "not fully optimal".

## Look-ahead and memorisation
Not addressed. FinQA, ConvFinQA and TATQA predate every model used, and the gold context is in the prompt, so in our terms the results are "bounded" at best.

## What it settles for us
- Goal C: the closest finance evidence that a tuned small model can sit next to a commercial one. It is a point estimate with no margin, which is the practice the non-inferiority default replaces.
- Unequal effort, shown concretely: the fine-tuned arm got a hyperparameter search on a dev split, the zero-shot arm got unreported "prompt engineering experiments", and the commercial baselines were imported from another paper. Supports the equal-budget default.
- Teacher leakage: the teacher wrote the training programs, is the comparison target and is the judge in the capability analysis. Training labels were filtered against gold answers, which limits label noise but not the circularity. Our rule-based training labels avoid it.
- Tools: no arm runs without the interpreter, so the tool effect and the tool-by-fine-tuning interaction are not measured. Our two-level tool factor adds that.
- Prompt factor: few-shot can hurt small models, so the two prompt levels must be fixed on the development set and cannot be assumed ordered.
- Reusable: the recipe of executing generated code to filter training examples; the 1,500-example result as a prior for how many training pairs are worth labelling.

## Limits
Numeric QA with gold context, not narrative reading; no retrieval; baselines not re-run; single run per cell; GPT-4 as judge; rank-512 LoRA on an 80GB GPU is far from a 32GB machine.
