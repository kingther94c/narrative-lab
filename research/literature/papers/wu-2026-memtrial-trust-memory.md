# MemTrial: Learning When to Trust Memory in LLM Portfolio Agents

- **Citation:** Guanghao Wu, Zhuo Cai and Shoujin Wang (2026). Preprint; the HTML shows University
  of Technology Sydney. arXiv 2610.11732. v1 is dated 8 October 2026 and v2 11 October 2026.
  Version read: v2.
- **Link:** https://arxiv.org/abs/2610.11732
- **Stream:** 08, blind replay (S2)
- **Verified against source:** yes, 2026-11-19 (the arXiv abstract page for authors and dates; the
  arXiv HTML of v2, converted to plain text. Read in full: abstract, sections 1 to 5 with Tables 1
  to 4, and appendices D.2, D.3, D.4, D.11, D.13 (text and Table D.21), D.14, D.15, G.2 and H.
  Not read: appendices A, B, C, D.1, D.5 to D.10, D.12, E, F, G.1 and G.3. Figures were read
  through their captions. The code was not opened.)

## Question
An LLM portfolio agent that learns from stored experiences credits each experience with the outcome
of the decisions that used it. How can the agent measure what an experience actually changes, and
know when that measured value can be trusted on dates it has not seen?

## Data
- **PortBench:** 99 assets in six classes, monthly decisions held 20 trading days; 20 test dates in
  2023 and 2024; 338 earlier decision records as the experience pool.
- **InvestorBench:** four stocks and cash, daily decisions with news headlines; 149 test days from
  October 2020 to May 2021; 63 lessons written by the agent in a warm-up from July to September
  2020.
- **ClassAlloc** (the authors' own, built from PortBench prices): five asset classes, monthly; 71
  test months from May 2020 to March 2026, so it runs 21 months past the cutoff of the main model;
  58 warm-up lessons.
- **PlantedMem:** semi-synthetic. Real prices and real LLM allocations, with twelve planted
  experiences of known quality (three useful, six neutral, three misleading); 100 test worlds.
- **Models.** gpt-4.1-mini (stated cutoff June 2024) at temperature 0.7 for the main runs. Seven
  others for robustness: gpt-4.1-nano, gpt-5-mini, Gemini 2.5 Flash, Claude Haiku 4.5,
  Llama-3.3-70B, Qwen3-235B and DeepSeek-V3.1.
- Delisted firms: not stated. A month in which a held asset has no price is dropped.

## Method
- **Designed drafts.** On every date the agent retrieves four experiences and writes eight drafts
  of the decision, each with a different subset of the four. The subsets are the even-sized ones,
  a half-fraction factorial design of resolution IV: each experience is in half the drafts and its
  main effect is not mixed with any two-way interaction.
- **Contribution.** The mean utility of the drafts that had the experience minus the mean of those
  that did not. All drafts face the same market, so the shared move cancels. Contributions are
  centred within the date.
- **Pooling.** A hierarchical model (Fay-Herriot) shrinks each experience's mean contribution
  towards a value predicted from its content.
- **Trust test.** Before each date the model predicts the values of the retrieved experiences;
  after the outcome, the prediction is correlated with the measured contributions. The agent acts
  on its values only with at least 10 such forward scores and a one-sided t-test at 0.05.
- **Anchor.** Otherwise it holds a blend of the equal-weight portfolio and the average draft, with
  prior weight 0.9 on equal weight.
- **Baselines.** Fourteen, among them a memory-free draft, self-consistency, similarity retrieval,
  FinMem, MemRL, Reflexion and ExpeL. The method was frozen before any InvestorBench decision.
- **Look-ahead checks (Appendix D.14), on ClassAlloc.**
  - *Memorisation probe.* For each of 129 decision dates the LLM gets only the date and is asked
    for the percentage return of each asset class over the next 20 trading days: no market data,
    no memory, three draws per date at the run temperature. The prompt asks for a best estimate
    and offers no "unknown" answer. Scoring: "absolute recall" is the correlation over months
    between recalled and realised returns; "relative recall" is the same correlation after
    removing each class's mean and each month's mean. Both are computed before and after each
    model's stated cutoff.
  - *Dates hidden.* ClassAlloc is rerun for gpt-4.1-mini and gpt-5-mini with no calendar date in
    the context and with lessons stored and retrieved without dates.

## Outcome variable and horizon
Investor utility per decision: return net of 15 bp trading costs minus a risk-aversion penalty on
variance, averaged over three investor profiles. Horizon 20 trading days, or one day on
InvestorBench.

## Result
Empirical findings; means over three seeds unless stated.

- **Outcome credit follows the market.** The Spearman correlation between an experience's outcome
  credit and the utility of equal weight on the same date is +0.91 to +0.97 on the four
  benchmarks. Between outcome credit and the counterfactual contribution it is -0.03 to +0.11.
- **A single date says little.** Retrieved experiences change utility detectably on 2 to 4 of 56
  PortBench months, about what chance gives; on 126 to 127 of 149 InvestorBench days; on 53 to 57
  of 71 ClassAlloc months.
- **No learning agent beats equal weight on PortBench or InvestorBench.** PortBench-Full, % per
  month: equal weight 2.02, memory-free 1.60, FinMem 1.63, Reflexion 1.40, MemTrial 1.98.
  InvestorBench, bp per day: equal weight 10.45, memory-free 8.43, ExpeL 8.93, MemTrial 10.40.
- **The learned values did not carry forward.** The trust test passed on 0.0%, 0.6% and 0.3% of
  decisions on PortBench-Full, PortBench-Raw and InvestorBench, although experiences changed the
  decision on about 85% of InvestorBench days. It passed on 14.6% of ClassAlloc decisions, where
  the trusted drafts then earned 0.05 pp less (s.e. 0.07) than the blend they replaced.
- **The gain is abstention.** With the same anchor every LLM baseline comes within 1% of MemTrial.
  The authors write that gains from memory on real markets remain to be shown.
- **ClassAlloc.** The memory-free draft earns 0.657% per month against 0.623% for equal weight; no
  form of memory improves on memory-free (0.59 to 0.65).
- **Where quality is known (PlantedMem).** After ten years of monthly decisions the rank
  correlation between learned values and planted quality is 0.08 for outcome credit and 0.81 for
  counterfactual contributions. Adjusting outcome credit for the market by regression closes a
  third of the gap.
- **Before and after the cutoff (Table D.21, utility minus equal weight, pp per month).**
  gpt-4.1-mini memory-free: +0.082 over 50 months before, -0.082 over 21 months after; the
  difference is not significant (Welch p = 0.36). Of the six models with a published cutoff, five
  trail equal weight afterwards by 0.06 to 0.09. Claude Haiku 4.5 is the exception: +0.040 before,
  +0.079 in the eight months after.
- **Memorisation probe (Table D.22).** Before the cutoff, absolute recall is 0.10 to 0.63 and
  relative recall 0.06 to 0.50. After it, -0.16 to +0.09 and -0.10 to +0.01. Gemini 2.5 Flash is
  highest (0.63 and 0.50); Claude Haiku 4.5 has 0.27 and 0.27 before, -0.16 and -0.07 after. Each
  model has 102 to 121 dates before its cutoff and 8 to 27 after.
- **Recall does not order the advantage.** Gemini 2.5 Flash, which recalls most, beats equal weight
  by 0.008 pp before its cutoff; gpt-5-mini, with absolute recall 0.22, by 0.157 pp.
- **Hiding dates does not remove the pre-cutoff advantage (Table D.23).** gpt-4.1-mini memory-free:
  +0.127 before and -0.099 after with dates hidden, against +0.082 and -0.082 with dates shown.
  gpt-5-mini: +0.136 and -0.066 against +0.157 and -0.059. None of the 58 dateless warm-up lessons
  mentions a year or a month. The authors offer two explanations and do not choose: the model
  recognises the period from the returns it is shown, or its allocations happened to suit 2020 to
  2024.
- **Cost.** Eight drafts per decision, eight times the calls of a single-draft agent; about
  USD 0.05 per PortBench decision. The two look-ahead checks cost USD 3.87.

## Look-ahead and memorisation
Treated as a limitation, with the two checks above. The main model's cutoff is later than the whole
InvestorBench test period, 15 of the 20 PortBench test months and 50 of the 71 ClassAlloc months.
Dates were not hidden on PortBench or InvestorBench. The authors argue that the exposure affects
every LLM method alike, and that PlantedMem and the post-cutoff months are free of it. In the
standard runs the lessons are written by the model after it sees the realised returns, and they
carry their dates and a description of what happened (the example lesson in Appendix G.2 is stamped
2018-04-02 and names the month and how each asset class had moved). The paper does not study the
stored lessons as a leakage channel of their own.

## What it settles for us
- **Learning from replayed outcomes (strategy F and stage S2-d): a warning.** Crediting a lesson
  with the outcome of the episode that used it measures the common shock, not the lesson. On real
  data no experience-learning agent beat a rule baseline, and values learned on past dates did not
  predict later ones. S2-d should (a) score a lesson by a within-episode contrast, the same
  episode with and without it, (b) accept a lesson only after it has predicted episodes it was not
  built from, and (c) keep a rule baseline as the fallback. Points (a) to (c) are the paper's
  method; applying them to a playbook is our inference.
- **Rule baseline first (rule 8, and the plan's comparison of the blind PM with statistical
  baselines): supported.**
- **Closed-book recall probe: a second scoring rule.** Ask for a number, correlate with the
  realised value, and remove the entity mean and the period mean first. For S2 that means
  demeaning by company and by quarter, so that knowing that a firm usually grows, or that 2021 was
  a good year, does not count as recall of the episode. This sharpens the persistence baseline in
  the stream 03 probe recommendation. The probe here has no "unknown" option, so it measures
  accuracy and not propensity; S2 wants both.
- **Before-and-after performance as a leakage measure: not usable.** With 21 post-cutoff months the
  gap had p = 0.36, and it survived hiding the dates. This supports the plan's choice to treat the
  old-period against post-cutoff accuracy comparison as descriptive.
- **Hiding the date (hypothesis H2): open.** Removing every date did not remove the advantage, and
  the authors cannot tell recognition from the data apart from regime luck. An S2 arm that hides
  dates needs its own leakage measure; a performance gap will not settle it.
- **Recall as a moderator: weakened across models.** The model with the highest recall had the
  smallest pre-cutoff advantage. This says nothing about variation within one model.
- **Design for multi-view runs (strategy B).** The half-fraction layout fits eight views: switch
  four perturbation factors on and off across the views so that each factor's main effect on the
  call is estimated within the episode and the episode's own difficulty cancels. Our inference;
  the paper applies the design to memories, not to perturbations.
- **Noise.** A contribution measured on one date is mostly noise. Expect the same of a per-episode
  leakage estimate; pool across episodes before reading anything.
- **Open question.** Whether lessons written after outcomes carry outcome knowledge into later
  decisions is not measured here.

## Limits
- Portfolio allocation across assets or asset classes, not company fundamentals.
- The main results use one small commercial model; the trust test's false-pass rate has no formal
  bound (2% to 3% measured where there is no signal).
- The probe uses three draws per date and forces an estimate.
- The dates-hidden check covers two models and one benchmark, and the returns shown may still date
  the period.
- 8 to 27 post-cutoff months per model; no cutoff comparison is significant.
- ClassAlloc and PlantedMem are the authors' own constructions.
- The ablation, hyperparameter and case-study appendices were not read for this note.
