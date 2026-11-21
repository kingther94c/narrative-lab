# Caution Ahead: Numerical Reasoning and Look-Ahead Bias in AI Models

- **Citation:** Bradford Levy (2026). Journal of Accounting Research 64(3), 1139-1188. Open
  access, first published 6 May 2026. DOI 10.1111/1475-679x.70058. Version read: the published
  article, HTML on Wiley Online Library.
- **Link:** https://onlinelibrary.wiley.com/doi/full/10.1111/1475-679x.70058
- **Stream:** 08, blind replay (also bears on 03, look-ahead bias and memorisation)
- **Verified against source:** yes, 2026-11-19 (full text of the article read as page text in the
  in-app browser: abstract, sections 1 to 5, Tables 1 to 7, Appendices A and C, the reference
  list, all figure captions and footnotes 1 to 7. Figures 3, B4 and B5 were read as images.
  Figures 1, 2, B1 to B3 and C1 were read by caption only. The online appendix (sections IA.1 to
  IA.4) and the code repository were not opened.)

## Question
Recent papers report that LLMs predict the direction of next year's earnings from financial
statements about as well as people do. Is that reasoning over the numbers, or recall of numbers
the model saw in training? The paper asks first whether LLMs can do the arithmetic at all, and
then how much of the predictive accuracy survives when recall is made impossible.

## Data
- **Source:** Compustat Annual, 1968 to 2021. Baseline sample 30,210 firms and 346,731
  firm-years after filters (standard format, consolidated, domestic; no financial services; US
  dollars; net income present this year and next; total assets above 1; assets equal liabilities
  plus equity). December fiscal-year-end sample: also price above 1; 17,493 firms and 175,305
  firm-years (Table 1).
- **Base rates (Table 4):** net income rises in 57.5% of baseline firm-years and 58.1% of
  December ones; income before extraordinary items in 58.2% and 58.8%; EPS in 51.7% and 54.6%.
- **Delisted firms:** not addressed directly. The author notes that requiring next year's net
  income, and Compustat's coverage, may bring survivorship into the base rate.
- **What the model was shown (Figures B4 and B5).** Verified fact. Two Markdown tables headed
  "CONSOLIDATED STATEMENTS OF OPERATIONS" and "CONSOLIDATED BALANCE SHEETS", with Compustat line
  names ("Cash and Short-Term Investments - Total") and columns labelled `t` and `t-1`: three
  years of income statements and two of balance sheets. No firm name, no ticker, no calendar
  year, no text. Values are in Compustat units with up to three decimals (1.357, 12.969).
  Footnote 2: the author declines to call these statements anonymised, because the numbers
  identify the firm-year.
- **Commercial models (section 4.2):** gpt-3.5-turbo-0125, gpt-4-0125-preview,
  gpt-4o-2024-08-06, gpt-4o-mini-2024-07-18. All are what the paper calls non-reasoning models.
  No reasoning model and no model from another vendor is tested.
- **Own models (section 4.1, Appendix C):** 410-million-parameter models on the Pythia-410m
  architecture, trained from random initialisation on EDGAR text (the BeanCounter corpus), one
  per yearly knowledge cutoff from 1999 to 2023, each on 8.2 billion tokens sampled from the five
  years before its cutoff.
- **Samples for the tests:** arithmetic, 100 firm-years; yearly-cutoff test, 1,500 firm-years
  from 2002 to 2020 per sample; commercial models, 1,871 baseline and 1,883 December firm-years
  drawn in proportion to each year's share of 1968 to 2021; boosted trees, the full samples.

## Method
- **Arithmetic (section 3).** Add and subtract 2, 5, 10, 15 or all core balance-sheet items
  (26.5 on average), in order or shuffled; then a DuPont analysis from the relevant items or from
  full statements. Repeated with a code interpreter that the model is told to use.
- **Perturbations of the statements (sections 4.1 to 4.3; Figure 3 caption; Figure B4).**
  - *1, 3 or 5 LSD:* the 1, 3 or 5 least significant digits of every item are replaced with
    random digits. The caption's example: with one digit and a value of 1.23, the 3 is replaced.
  - *Scaled:* every item is scaled by 1,000, which "shifts the decimal place potentially breaking
    the tokenization without changing the specific numerals". The introduction says divided by
    1,000; the tables say scaled by 1,000.
  - *Full (boosted trees only):* each item is replaced by a draw from that item's distribution
    in the sample.
- **Yearly-cutoff test (section 4.1).** Each statement set is passed through the seven models
  whose cutoffs run from three years before to three years after the statement year. The model
  output is mean-pooled into one vector, and a gradient-boosted classifier predicts the earnings
  change from it under 10-fold cross-validation. Accuracy is compared across relative cutoffs,
  with and without perturbation.
- **Commercial-model test (section 4.2).** A system message sets six steps (extract metrics,
  compute ratios, trend analysis, infer, predict, justify) with worked examples; the user message
  says "Using only the provided information" and supplies the two tables. The model answers
  increase or decrease. Token log-probabilities give an AUC. The model does its own arithmetic;
  no tool is given in this test.
- **Benchmark (section 4.3).** Gradient-boosted trees on the same items and years, trained on a
  rolling window of up to 20 years and scored on the following year. The scaled case is not run,
  on the grounds that trees are invariant to scaling every feature by a constant.

## Outcome variable and horizon
Whether net income rises in the next fiscal year: binary, one year ahead. Accuracy, F1 and AUC
with 99% bootstrap intervals.

## Result
Empirical findings.

- **Arithmetic (Table 2).** gpt-4o with chain-of-thought sums 2 items correctly 100% of the
  time, 15 items 67%, all core items 4% (99% interval 0 to 9%); shuffled, 12%. With a code
  interpreter gpt-4o-mini scores 100% on all core items and on every DuPont ratio. Without tools
  gpt-4o gets ROE right 68% (basic prompt) to 78% (chain-of-thought) of the time.
- **Yearly cutoffs (Table 5, baseline, base rate 0.56).** Unperturbed accuracy is 0.53, 0.55,
  0.55 and 0.50 for cutoffs at t-3 to t, and 0.59, 0.58 and 0.60 for t+1 to t+3 (99% interval at
  t+3: 0.58 to 0.63). With one digit randomised the t+1 to t+3 figures are 0.55, 0.54 and 0.56;
  scaled, 0.55, 0.54 and 0.53. The December sample shows the same pattern (0.57, 0.59, 0.59
  falling to 0.56, 0.55, 0.55).
- **Commercial models, baseline sample (Table 6 panel A, base rate 0.58).**

  | Model | None | 1 LSD | 3 LSD | 5 LSD | Scaled |
  |---|---|---|---|---|---|
  | gpt-4-0125-preview, accuracy | 0.60 (0.57, 0.63) | 0.51 (0.49, 0.54) | 0.50 | 0.48 | 0.51 (0.49, 0.54) |
  | gpt-4-0125-preview, AUC | 0.57 | 0.48 | 0.49 | 0.50 | 0.48 |
  | gpt-4o-2024-08-06, accuracy | 0.57 | 0.50 | 0.49 | 0.47 | 0.49 |
  | gpt-4o-mini-2024-07-18, accuracy | 0.56 | 0.48 | 0.48 | 0.46 | 0.49 |
  | gpt-3.5-turbo-0125, accuracy | 0.55 | 0.49 | 0.47 | 0.48 | 0.51 |

- **Commercial models, December sample (Table 6 panel B).** gpt-4 accuracy 0.61 (0.59, 0.64)
  falls to 0.55 (0.52, 0.58) with one digit randomised, 0.52 with three, 0.50 with five and 0.54
  (0.51, 0.57) scaled; AUC 0.59 falls to 0.53 (0.50, 0.55), 0.51, 0.51 and 0.51. The fall is
  smaller here than in the baseline sample, and at one digit the accuracy interval excludes 0.50
  while staying below the base rate. The paper's summary figures mix the panels: "60% to 51%" is
  the baseline sample and the "6%" drop is the December one. This is our reading of Table 6.
- **Share of "increase" calls.** gpt-4 predicts an increase 68% of the time unperturbed and 37%
  with five digits randomised. No LLM moves towards always predicting an increase as the input
  becomes noise.
- **Boosted trees (Table 7, baseline).** Accuracy 0.627 (0.597, 0.658), then 0.623, 0.615, 0.612
  with 1, 3 and 5 digits randomised, and 0.580 with full replacement. AUC 0.652, 0.646, 0.630,
  0.624 and 0.532. As the input turns to noise the trees predict an increase almost always
  (share 0.783 rising to 0.999), which is the base-rate strategy.
- **Stated comparison.** The trees beat the best LLM by 2.7 points of accuracy unperturbed and
  lose about 0.4 points to one-digit randomisation.
- **Uniqueness of the numbers (introduction).** Net income alone identifies about 40% of annual
  earnings announcements from 1968 to 2021, sales alone about 60%, and the pair more than 99.9%.
  The body of the article has no table for this; it may be in the online appendix, which was not
  read.
- **No identification test.** Verified fact about the text read: no test asks a model to name
  the firm or the year, before or after perturbation. Memorisation is inferred from the accuracy
  drop and from the cutoff design.

## Look-ahead and memorisation
This is the subject of the paper. Three positions matter for us.

- **Recall keys on exact numerals.** Changing the last digit, or moving the decimal point with
  every numeral kept, removes the predictive accuracy. Empirical finding.
- **Vendor cutoffs are not trusted.** Hypothesis argued in sections 2.2 and 4, not tested:
  post-training and silent updates can bring later knowledge into a model, so a test dated
  after the quoted cutoff "is unlikely to be truly out-of-sample". The author notes that
  Anthropic publishes both a reliable knowledge cutoff and a training data cutoff.
- **Censoring identifiers is doubted (section 4.4).** Two objections: it changes the input
  distribution, so it has to be applied out of sample as well; and filling in masked content is
  close to the training objective, so models are good at undoing it. The author cites Engelberg
  et al. (2025) for firm-name guess rates of 25% or more on SEC filings.
- **Recommended remedy:** fix the prompt and model, then evaluate in real time, as with a
  pre-registered trial. The author concedes that this "precludes much archival research".

## What it settles for us
- **Smallest perturbation shown to break recall.** Randomising one trailing digit of every item,
  on anonymous Compustat tables with relative year labels, took gpt-4 from 0.60 to 0.51. A
  uniform shift of the decimal point did the same with no digit changed. Both are within S2
  strategy A, levels L1 and L2a. Supported for numeric tables; not tested on text.
- **"Near-zero information loss" needs two caveats.** Both are our reading of Figure B4.
  - The trailing digit is not always small: 0.37 becomes 0.34, an 8% change, because the item
    has two significant digits.
  - Totals are randomised independently, so the perturbed statement no longer adds up (the
    current-asset lines sum to 12.962 against a displayed total of 12.960). Our sanitiser plans
    to keep such identities, which Levy's did not.
- **Scaling rules out one alternative.** The scaled statements keep every ratio and identity,
  and accuracy still falls to chance. So the fall is not a reaction to inconsistent statements.
  This is our inference.
- **No skill is left once recall is broken, for these models and this task.** Accuracy falls to
  or below the always-increase rate while trees on the same items keep an AUC near 0.65. This
  supports the plan's rule that a blind PM is judged against a statistical baseline, and
  "simple baselines first" (rule 8).
- **The perturbation test is a leakage metric we can reuse.** A call that changes when a
  decision-irrelevant detail changes is evidence of recall. This is the logic behind use 2 of
  strategy B (irrelevant perturbations should leave the call unchanged). Our inference.
- **Arithmetic belongs in code: supported.** Tool use took sums and ratios to 100%. The plan's
  sanitiser, which computes ratios and growth rates in code, follows this.
- **Open question.** The prediction test gave the model no tool and no pre-computed ratios.
  Whether an LLM handed correct ratios keeps any skill under perturbation is not tested.
- **Open question.** Recognition is never measured, so the paper cannot say whether a perturbed
  statement is still identifiable. A power-of-ten scale leaves the digit string intact, which a
  rule-based nearest-neighbour attacker would match at once. The second sentence is our
  inference.
- **Failing to name the firm does not show a clean episode.** Kim, Muhn and Nikolaev (2024,
  arXiv 2407.17866 v2, since withdrawn) gave the same model, gpt-4-0125-preview, the same kind
  of anonymous Compustat statements. They report that it names the firm 0.07% of the time and
  the year 2.95%, and conclude that memory does not drive their 60% accuracy. Levy removes that
  level of accuracy by changing one digit. If the settings match, an attacker that asks "who is
  this?" can score near zero while recall of the outcome is intact. For S2 this puts the
  outcome-leakage measures ahead of identifiability, as the plan already does. Our inference;
  Levy does not name that paper, and we read it only in keyword-selected passages of v2.
- **Rule 2 (clean tests postdate the vendor's cutoff): qualified.** The author argues the quoted
  cutoff is optimistic. No evidence is given, but it is a reason to keep a margin after the
  cutoff and to report the test date against both of Anthropic's published dates.
- **Report the base rate and AUC.** Accuracy against 50% flatters a model when 58% of outcomes
  are increases. Our main label has a base rate near 49%, which avoids most of this.
- Leads named in section 4.4 and not read here: Merchant and Levy (2025) on unlearning for
  look-ahead bias, and Koijen and Levy (2026) on real-time evaluation of agentic systems.

## Limits
- The newest commercial model is gpt-4o-2024-08-06. No reasoning model, no tool-assisted
  prediction and no second vendor.
- The input is a bare numeric table. Nothing is shown about press releases or other text, where
  wording, segment structure and ratios may identify the firm without exact numerals.
- Annual statements only; our call is quarterly.
- The trees are scored on the full samples (346,731 and 175,305 firm-years) and the LLMs on
  about 1,900. The Figure 3 caption speaks of a common sample of 1,500, which does not match
  Tables 6 and 7.
- The text read does not say whether the trees were retrained on perturbed data or only scored
  on it.
- A model that treats firm size as a signal should change its call when every item is scaled by
  1,000, so scaling is not a strictly irrelevant perturbation for a zero-shot predictor. The
  trees are excused from the scaled case on an invariance that holds for a retrained model. Our
  inference.
- The unperturbed LLM result is itself thin: 0.60 accuracy against a base rate of 0.58, AUC 0.57.
- Stated by the author: the yearly-cutoff models are small and trained only on financial text,
  which probably overstates memorisation; results from OpenAI's systems are only as reproducible
  as those systems.
- The article does not name the study it re-creates. It says only that "this literature" finds
  about 60% accuracy against 50%, and its reference list has no entry for Kim, Muhn and Nikolaev
  (2024), "Financial Statement Analysis with Large Language Models". Verified fact about the
  published text; the match to that paper is made in our triage row, not by Levy.
