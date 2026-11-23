# FinChain: A Symbolic Benchmark for Verifiable Chain-of-Thought Financial Reasoning

- **Citation:** Zhuohan Xie, Daniil Orel, Rushil Thareja and 22 others, including Preslav Nakov
  (2025). arXiv 2506.02515; v3 of 8 January 2026 (v1, June 2025). No venue stated. Version read:
  v3, HTML.
- **Link:** https://arxiv.org/abs/2506.02515 (HTML read: https://arxiv.org/html/2506.02515v3)
- **Stream:** 13b, reasoning item design (templated finance items; step-level grading)
- **Verified against source:** yes, 2026-11-23. Whole HTML (137,230 characters) read through a
  machine extraction in two passes; the template code and Figure 6 were not visible.

## Question
Can a finance benchmark check the intermediate steps of a model's reasoning, not just its final
number, and how do models of different sizes and specialisations compare on it?

## Data
- 12 financial domains, 58 topics (proposed with LLM help, curated by experts). Five templates per
  topic: two basic, two intermediate, one advanced (290 templates; 2.0, 3.0 and 3.9 steps on
  average). Each template is an executable Python program that draws the inputs and writes out
  every intermediate step and the final answer.
- 10 instances per template with distinct seeds: 2,900 test items. English, US-centric,
  textbook-style word problems (interest, valuation, ratios and similar), not filings.
- LLMs drafted the templates; ten annotators (three industry professionals, seven finance or
  accounting graduate students) reviewed them after a calibration pilot. Automated checks for
  precision, units, complete inputs and non-informative steps.
- 26 models evaluated zero-shot with a step-by-step prompt; no tools or code execution for the
  evaluated models.

## Method
ChainEval. Each predicted and gold step is embedded with a sentence encoder (cosine similarity)
and its numeric result compared with the gold value within 5% relative error; a step pair counts
only when both agree (a gate). Dynamic time warping aligns the two step sequences. Final score:
0.9 times the aligned step score plus 0.1 times final-answer correctness (weight chosen by grid
search for correlation with expert ratings).

## Outcome variable and horizon
ChainEval and final-answer correctness (FAC). Not a forecasting task.

## Result
Empirical findings.

- **Frontier models are close on steps.** ChainEval: GPT-5-mini 67.17, GPT-5 66.57, Claude
  Sonnet 4.5 66.33, Gemini 2.5 Pro 66.04. FAC: GPT-4.1 84.66, Gemini 2.5 Pro 84.34.
- **Size alone does not decide it.** Qwen2.5-Instruct-7B 60.35, Mathstral-7B 59.87 and Fin-R1-7B
  58.14 approach the frontier on ChainEval; Fino1-8B 41.50, Finance-LLaMA-8B 41.35,
  Finance-Qwen-7B 34.57, MetaMath-7B 7.93. Finance fine-tuning is no guarantee.
- **Final answer and process diverge.** DeepSeek-R1: ChainEval 51.22 against FAC 28.97; GPT-4.1:
  65.34 against 84.66 (our reading; the scales differ and the paper does not discuss the gap).
- **The automatic step metric agrees only moderately with experts.** On 100 expert-rated
  responses (20 questions, five models, five-point scales), the best variant reaches Spearman
  0.655, Pearson 0.584, Kendall 0.509 against expert ratings of reasoning quality; ROUGE-2 0.469,
  BERTScore 0.287 (Spearman). The two expert dimensions (process and final answer) correlate
  above 0.94 with each other.

## Look-ahead and memorisation
Claimed "contamination-free" because instances are regenerated from seeds. No test of whether
topics or templates resemble training data, and no held-out template set reported.

## What it settles for us
- **Executable templates that print their own step chain are feasible in finance and give a free
  process label.** For S1, each generator can emit the gold intermediate figures (for example
  revenue growth, then margin change, then the call), so a model's stated intermediate numbers
  can be checked against gold with a numeric tolerance. That is cheaper and more defensible than
  semantic similarity of steps.
- **Do not grade process by text similarity.** Even the best similarity-based metric reaches only
  about 0.6 rank correlation with experts on 100 items, and experts' process and outcome ratings
  were nearly collinear (0.94). For S1, a step check limited to numeric claims, plus a
  perturbation test of whether the answer depends on them, is the better design (our inference,
  with `lanham-2023`).
- **Small distilled or finance-tuned models can lose process quality while keeping answers, or
  the reverse.** Report final-answer accuracy and step accuracy separately for the 0.8B student
  and the 4B teacher.
- **The 5% tolerance follows materiality conventions.** S1's numeric grader is stricter;
  keep strict grading for numbers and use bands only for direction calls (convention).

## Limits
- Synthetic textbook problems; no tables, filings or distracting context; judgement is out of
  scope by the authors' own statement.
- Expert validation is small (100 responses) and done on the authors' metric variants.
- The model prompt and step parsing are format-sensitive, as the authors state.
- LLM-drafted templates: errors in the template code would propagate to every instance; the
  review process is described, its error rate is not reported.
