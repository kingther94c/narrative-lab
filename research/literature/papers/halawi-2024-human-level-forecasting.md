# Approaching Human-Level Forecasting with Language Models

- **Citation:** Danny Halawi, Fred Zhang, Chen Yueh-Han and Jacob Steinhardt (2024). arXiv
  2402.18563, v1 of 28 February 2024 (the only version listed on the abstract page). A NeurIPS
  2024 poster page appeared in search results and was not opened.
- **Link:** https://arxiv.org/abs/2402.18563
- **Stream:** 12, forecast prompting
- **Verified against source:** yes, 2026-11-22. arXiv HTML of v1 read as extracted text:
  abstract, sections 1 to 8, Tables 2, 5 and 7, Appendix A.2, the hyperparameter sweep (section
  5.2 and appendix), Table 14 and Figures 5, 6, 15 and 17 as text. Figures with plots read by
  caption only.

## Question
Can a retrieval-augmented LLM system forecast binary questions as well as the crowd on
competitive forecasting platforms? Which parts of the system carry the gain?

## Data
- 48,754 questions from Metaculus, Good Judgment Open, INFER, Polymarket and Manifold, 2015 to
  2024. Curated binary set: 3,762 train, 840 validation, 914 test.
- Test questions were all opened after the models' knowledge cutoff; train and validation
  questions all resolved before it; questions spanning the date were dropped. The text gives the
  date as June 1, 2023 in one place and June 1, 2024 in another; the table caption says 2023.
- No company documents. News articles retrieved with date filters (NewsCatcher, Google News).

## Method
- Retrieval: the model writes search queries, filters articles by relevance and summarises the
  top k. Up to five retrieval dates per question.
- Reasoning: a scratchpad prompt chosen from 15 hand-written candidates on validation. The best
  one (Figure 15) asks the model to rephrase the question, give reasons for no and for yes with a
  strength for each, aggregate "like a superforecaster", give an initial probability, check for
  over- or under-confidence and base rates, then give a final probability.
- Fine-tuning: 16 candidate forecasts per training question; keep those that beat the crowd;
  fine-tune GPT-4-0613 on the reasoning without the scratchpad instructions.
- Aggregation: six forecasts (three base-model prompts, three fine-tuned samples at temperature
  0.5) combined by a trimmed mean (the forecast furthest from the median gets half weight).
- Baselines: 14 models with no retrieval, zero-shot and scratchpad prompts, each prompt chosen on
  200 validation questions.

## Outcome variable and horizon
Brier score averaged over retrieval dates and then over questions; accuracy; RMS calibration
error. Horizons are those of the platform questions.

## Result
Empirical findings unless marked.

- **No-retrieval baselines (Table 7).** Scratchpad does not beat zero-shot. GPT-4-1106-Preview
  0.208 zero-shot and 0.209 scratchpad; GPT-4-0613 0.219 and 0.222; Claude-2.1 0.220 and 0.215;
  GPT-3.5-Turbo 0.237 and 0.257; Llama-2-13B 0.226 and 0.268. Crowd 0.149; random 0.250. On
  validation, "all prompts yield similar Brier scores" for scratchpads, so the winner was picked by
  fewer refusals.
- **Full system.** 0.179 (SE 0.003) against the crowd's 0.149 overall (Table 4). Averaging with
  the crowd gives 0.146.
- **Ablations (Table 5).** Full system 0.179; without fine-tuning 0.186; without fine-tuning and
  without retrieval 0.206, close to the 0.208 zero-shot baseline. The authors read this as the
  optimised reasoning prompt alone giving "fairly a minor improvement".
- **Prompt selection on validation.** Best of 15 prompts 0.167; next two 0.170 and 0.174. These
  are the winners of a search on validation, so the spread is an upper bound on the true gain.
- **Ensembling (Table 14, validation).** Mean of six base reasonings' individual scores 0.1676;
  mean 0.1656; median 0.1651; geometric mean 0.1655; trimmed mean 0.1649; universal
  self-consistency (an LLM reads the six reasonings and answers) 0.1691, worse than no ensemble.
- **Calibration.** Test RMS calibration error 0.42 against the crowd's 0.38. Zero-shot baselines
  were poorly calibrated. Binning and isotonic recalibration did not help the system.
- **Where it fails.** The system "rarely outputs low probabilities". When the crowd is between
  0.3 and 0.7 it scores 0.199 against the crowd's 0.246 (validation). When the crowd is within
  0.05 of 0 or 1 its accuracy is 7% higher but its Brier is 0.04 worse. The authors attribute the
  hedging to safety training (hypothesis).

## Look-ahead and memorisation
Test questions open after the stated cutoff; retrieval date-filtered; retrieval dates not tied to
resolution dates; hyperparameters set on validation only. Appendix A.2 asked GPT-4-1106-Preview
about 20 events of June to September 2023 and found no sign of post-training leakage. Retrieval
leakage through page edits or wrong publication dates is not tested (stream 08's TimeSPEC row
reports that such leakage exists).

## What it settles for us
- **Prompt structure alone is worth about 0.002 Brier** in the cleanest ablation available: the
  optimised scratchpad without retrieval or fine-tuning (0.206) against the zero-shot baseline
  (0.208). The gains came from new information (retrieval) and from training on good reasoning.
  For S2, where the model gets one release and no tools, the analogue of retrieval is facts the
  model would not otherwise use (code-computed comparisons, base rates), not instructions.
- **Aggregation: average numbers, do not ask a model to aggregate.** Averaging six forecasts
  gained about 0.002 to 0.003; an LLM aggregator lost 0.0015. Use a mean or trimmed mean of
  several samples.
- **Selection on validation is the protocol to copy,** with a test set later in time. The
  spread across the top three prompts (0.007) shows how much a validation winner can be luck.
- **Calibration needs its own check.** The hedging pattern means a prompt that adds decisiveness
  can help or hurt depending on how often the true answer is extreme; report reliability, not
  Brier alone.

## Limits
- Non-financial questions; information arrives as news, not as a disclosure to read.
- 2023 models; the test cutoff date is inconsistent in the text.
- Standard errors assume independence across questions and dates; the authors say they likely
  understate error.
- The fine-tuning selects reasoning that beat the crowd, so the trained reasoning is shaped by
  outcomes; this is legitimate for pre-cutoff training questions but is the kind of
  outcome-shaped tuning that would carry hindsight if the training items were remembered.
