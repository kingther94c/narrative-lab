# To CoT or not to CoT? Chain-of-thought helps mainly on math and symbolic reasoning

- **Citation:** Zayne Sprague, Fangcong Yin, Juan Diego Rodriguez, Dongwei Jiang, Manya Wadhwa,
  Prasann Singhal, Xinyu Zhao, Xi Ye, Kyle Mahowald and Greg Durrett (2025). ICLR 2025. arXiv
  2409.12183, v3 of 7 May 2025.
- **Link:** https://arxiv.org/abs/2409.12183
- **Stream:** 12, forecast prompting
- **Verified against source:** yes, 2026-11-22. arXiv HTML of v3 read as extracted text:
  abstract, sections 1 to 6 (the first part of the discussion), Table 1. Appendix tables and the
  figures' numbers not read.

## Question
On which kinds of task does chain-of-thought prompting beat answering directly, and why?

## Data
- Meta-analysis: all papers at ICLR 2024, EACL 2024 and NAACL 2024 (4,642), filtered to 110
  papers with 1,218 comparisons of chain of thought against direct answers.
- Own experiments: 20 datasets, 14 models, zero-shot and few-shot, greedy decoding. Categories:
  commonsense, knowledge, symbolic, mathematical, soft reasoning.
- Planning and execution experiments on GSM8K, GSM8K-Hard, ContextHub and FOLIO.

## Method
- Compare direct-answer prompts (answer immediately; the answer's position in the output is
  checked) with chain-of-thought prompts.
- Significance on 13 non-symbolic datasets by paired bootstrap with a Bonferroni threshold
  (p = 0.00027).
- On MMLU and MMLU-Pro, split questions by whether the question or the model's output contains
  "=".
- Separate planning from execution: direct answer, chain of thought, plan then direct answer,
  plan then chain-of-thought solver, plan then a tool (Python interpreter or the Z3 solver).

## Outcome variable and horizon
Accuracy (or judge score for BiGGen Bench). Not a forecasting task.

## Result
Empirical findings.

- **Literature.** Symbolic, math and logical tasks gain 14.2, 12.3 and 6.9 points on average.
  Across all other categories, accuracy is 56.8 with chain of thought against 56.1 without.
- **Own experiments.** On commonsense, language understanding and reading comprehension sets,
  zero-shot chain of thought and direct answers are about equal. MATH and GSM8K gain up to 41.6
  and 66.9 points. About 32% (59) of the positive comparisons on knowledge, soft-reasoning and
  commonsense sets are significant, nearly half of them on MMLU and MMLU-Pro.
- **The "=" split.** As much as 95% of the gain on MMLU comes from questions whose question or
  output contains "=". For non-math questions the authors found no feature that predicts when
  chain of thought helps.
- **Few-shot and prompt variants.** Few-shot chain of thought performs like zero-shot; different
  reasoning prompts gave slight differences.
- **Tools beat chain of thought at execution.** Having only a plan recovers little of the gain;
  executing the plan step by step recovers most of it; feeding the plan to a symbolic solver beats
  chain of thought in most settings. The authors call chain of thought "a poor (but universal)
  approximation" to such solvers.
- **Outlier relevant to us.** The meta-analysis lists eliciting verbalised confidence (Xiong et al.
  2024) among the few non-math tasks that benefit from chain of thought.

## Look-ahead and memorisation
Partly: GSM8K-Hard is used because GSM8K may be contaminated. Otherwise not addressed.

## What it settles for us
- **Split the playbook into arithmetic and judgement.** The S2 checklist has two kinds of item.
  Arithmetic items (comparison base, guidance-implied growth, organic versus acquired growth,
  inventory growth against sales growth) are symbolic: chain of thought helps there, and a tool
  helps more. Judgement items (is this charge recurring, is management evasive) are soft
  reasoning, where chain of thought adds about nothing on average. This supports computing the
  arithmetic in code and stating it as sentences (Levy 2026, stream 08, reached the same advice
  for financial statements), and expecting little from free-text reasoning on the judgement items.
- **Expected size of a reasoning gain on non-symbolic judgement: under one point** of accuracy
  on average across the literature, with outliers. A larger S2 gain would need a reason.
- **Compute-matched comparison (convention to adopt).** The authors note that a fair comparison
  should match compute, for example by ensembling direct answers. An S2 playbook arm that writes
  long reasoning should be compared with a direct arm averaged over several samples.

## Limits
- Benchmarks are mostly multiple choice or short answer; no probabilistic forecasting.
- Models up to mid-2024 (the list read runs from Llama 2 7B to GPT-4o 2024-08-06 and Claude 3.5
  Sonnet 2024-06-20); no reasoning-trained model in that list.
- Our reading: the literature meta-analysis may inherit publication bias towards positive
  chain-of-thought results.
