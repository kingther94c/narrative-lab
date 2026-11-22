# Stream 12: structured prompting for forecasts, and what reasons are worth (draft)

Sources checked 2026-11-22, for sub-study S2 (`../../design/substudy_s2_blind_replay.md`), after
EXP-0034. Notes are in `../papers/`; all 22 rows are in `12_forecast_prompting.csv`: 6 deep notes
and 16 triaged rows. Stream 08 already covers `levy-2026` and Zhang, Chen and Stadie (2026,
TimeSPEC); stream 02 covers `li-2024`. They are cited, not repeated. This draft is not merged into
`../matrix.csv`.

The question the stream has to settle: the owner wants a reusable analyst playbook ("skill") in
the PM prompt that tells the model what to examine in an earnings release (one-off versus
recurring items, inventory and receivables, organic versus acquired growth, guidance arithmetic,
evasiveness), on top of mean reversion and trend. Two S2 results frame it. EXP-0029: asking for
evidence before the probability raised the old-minus-clean readout from 0.155 to 0.236, and the
cited evidence already leaned towards the remembered outcome. EXP-0032 and EXP-0034: the PM did
not do comparison-base arithmetic from a table (+0.005), while the comparison-base rule alone calls
65% of episodes and right clean calls rest mostly on arithmetic the release already fixes
(EXP-0033). Does structured prompting improve forecasts, by how much, when does it hurt, and how
should a playbook be built and tested?

## What the stream establishes

**1. Structured prompts barely move forecast accuracy**

- **Empirical finding.** The largest test: 37 single-element prompts and 17 compound prompts on
  100 ForecastBench questions, four 2024 models plus o1 and o1-mini, pre-registered. No prompt
  beats a probability-only control in the clustered, corrected analysis. The best single
  elements are -0.011 to -0.019 Brier (frequency-based reasoning, base rate first, chain of
  thought, step-back) against a base near 0.21; only the base-rate pair and step-back survive
  correction, and only in the simpler t-tests. Compound prompts that bundle the good elements do
  no better (best -0.009, not significant), nor do vendors' automatic prompt writers (-0.003,
  -0.004). Reasoning models show the same pattern (`schoenegger-2025`, Tables 4, 5, 8, 9).
- **Empirical finding.** In the cleanest system ablation, the optimised scratchpad without
  retrieval or fine-tuning scores 0.206 against 0.208 for a zero-shot prompt; without retrieval,
  scratchpad and zero-shot tie for GPT-4 (0.209, 0.208). The system's gains came from retrieval
  (new information) and from fine-tuning on reasoning that beat the crowd (`halawi-2024`, Tables
  5 and 7).
- **Empirical finding.** On PaLM 2, no human forecasting strategy beat a basic prompt: breakdown
  +0.067, base rates +0.034, both sides +0.033, a persona crowd +0.049 over 0.1221
  (`pratt-2024`, Table 1; 78 events, no intervals).
- **Empirical finding.** Across 110 papers, chain of thought gains 14.2, 12.3 and 6.9 points on
  symbolic, math and logic tasks, and 0.7 points elsewhere (56.8 against 56.1). Up to 95% of the
  MMLU gain sits on questions with an "=". Where chain of thought helps, a tool helps more
  (`sprague-2025`).
- **Finance (thin).** The most-cited finance case, an analyst-step prompt on anonymised
  statements, reported 60.35% against 52.33% for a simple prompt. The paper is withdrawn, Li et al.
  (2024, stream 02) could not reproduce the headline, and Levy (2026, stream 08) attributes this
  kind of accuracy to recall (Kim, Muhn and Nikolaev, triaged). On financial sentiment, GPT-4o
  without chain of thought was best (Vamvourellis and Mehta, triaged). An expert blueprint
  raised a small base model from 63.2% to 80.5% on CFA-style questions, most for models without
  financial post-training (FinCoT, triaged): domain checklists help weak models answer
  knowledge questions, a long way from a frontier model forecasting.
- **Gap (this pass).** No study tests an analyst checklist on earnings releases with a
  forecasting outcome dated after the model's cutoff.

**2. When structure hurts**

- **Empirical finding.** Explicit Bayesian updating (+0.030 Brier), propose-evaluate-select
  (+0.033) and a superforecaster-written conditional odds-ratio protocol (+0.023) were worse than
  the control after correction (`schoenegger-2025`). Decomposition was the worst strategy in
  `pratt-2024`.
- **Empirical finding.** Chain of thought cut accuracy by up to 36.3 points on three of six tasks
  where deliberation also hurts people (Liu et al., triaged). Reasoning did not help, and
  sometimes hurt, on simple financial text judgements (Vamvourellis and Mehta, triaged).
- **Empirical finding.** Asking for reasons shifts the level of the probability. With a
  rationale first, PaLM 2's probabilities rose across events (`pratt-2024`, Figure 1). With
  reasoning first, seven models gave higher probability to their chosen MCQ option, more so when
  wrong, and calibration got worse (Fu et al., triaged). Bayesian, propose-evaluate-select and
  chain-of-thought prompts made the most decisive forecasts in `schoenegger-2025` (mean distance
  from 50% 0.199, 0.175, 0.172 against 0.134).
- **Empirical finding.** Personas do nothing reliable: superforecaster persona -0.001 and -0.002
  (`schoenegger-2025`); 162 personas on factual questions, no gain and random effects (Zheng et
  al., triaged).

**3. Reasons written before the answer are often rationalisation**

- **Empirical finding.** A hidden influence moved answers by up to 36.3 points while explanations
  mentioned it in 1 of 426 cases; 73% of unfaithful explanations argued for the biased answer,
  15% with no visible error. With zero-shot chain of thought the bias grew (accuracy 39.5% to
  23.3% for GPT-3.5): the model reasoned its way to a biased answer it avoided when answering
  directly (`turpin-2023`). This is the pattern of EXP-0029, with the remembered outcome as the
  hidden influence.
- **Empirical finding.** Strong models often fix the answer before the reasoning ends: truncating
  the reasoning changes under 10% of answers on easy tasks; larger models are less faithful on 7
  of 8 tasks (`lanham-2023`). Reasoning models verbalise hints they use in 25% (Claude 3.7
  Sonnet) and 39% (DeepSeek R1) of cases, and unfaithful traces are longer (Chen et al.,
  triaged). Rationalisation of an implicit lean also occurs with no injected bias, at 0.04% to
  13% by model (Arcuschin et al., triaged).
- **Empirical finding.** Instructions reduce such leaks without removing them. A debiasing
  instruction worked for Claude 1.0 and not for GPT-3.5 (`turpin-2023`). A temporal instruction
  cut decision-critical leakage in stock-ranking rationales from 0.171 to 0.034 and left it above
  zero (Zhang, Chen and Stadie v1, stream 08; re-checked in this pass). EXP-0029's "judge from the
  text alone" halved the S2 gap.
- **Verified fact (designs seen).** Ways to test whether an answer depends on its reasons:
  truncate the reasoning and re-ask; insert a mistake and regenerate (`lanham-2023`); pair inputs
  that differ only in the suspected influence (`turpin-2023`); ask a question and its reversal
  (`pratt-2024`, Arcuschin et al.); answer only from audited claims (TimeSPEC, stream 08).

**4. Order and format: reasons before, after, or in a form**

- **Empirical finding.** In structured outputs, a reasoning field before the answer field matches
  or beats free text; an answer field first collapses multi-step arithmetic (GSM8K: 10.98% for
  two small models against 83% to 87% reasoning-first; the reasoning-first lead was at least 37
  points in every prompt-perturbation cell, GPT-4o included); XML tags beat JSON by up to 12.2
  points; the reasoning-first XML form lowered calibration error against free text for most models
  (Kanishka and Mandora, triaged). The damage is largest where the model must compute.
- **Empirical finding.** For a judgement (rating text quality), a rating followed by an
  explanation correlated with human ratings as well as analysis followed by a rating, and both
  beat a bare score. The rating cannot depend on the later explanation, so the request for an
  explanation changed the rating itself (Chiang and Lee, triaged).
- **Empirical finding.** Verbalised probabilities from RLHF models are often better calibrated
  than token probabilities (ECE down about half; Tian et al., triaged) but overconfident;
  consistency across several sampled answers reduces the overconfidence (Xiong et al.,
  triaged).
- **Our reading.** The two kinds of playbook item want different treatment. Arithmetic items
  (comparison base, guidance minus year to date, organic versus acquired growth, inventory growth
  against sales growth) are symbolic: reasoning-first helps and code helps more [`sprague-2025`;
  Kanishka and Mandora; `levy-2026`; EXP-0032 arm s4]. Judgement items (is this charge
  recurring, is management evasive) are soft reasoning, where reasoning adds about nothing on
  average and is where rationalisation operates [`sprague-2025`, `turpin-2023`].

**5. Aggregation**

- **Empirical finding.** Averaging six forecasts gained 0.002 to 0.003 Brier on validation
  (trimmed mean 0.1649, mean 0.1656, single 0.1676); an LLM reading the six and answering lost
  0.0015 (0.1691) (`halawi-2024`, Table 14).
- **Empirical finding.** An average of twelve models matched a 925-person crowd; models leaned
  above 50% on balanced questions; showing models the human median helped by 17% to 28% but less
  than simply averaging the human and machine forecasts (Schoenegger et al. 2024, triaged).
  Averaging with the crowd at 4:1 improved the crowd's Brier from 0.149 to 0.146
  (`halawi-2024`).
- **Empirical finding.** A one-call "generate three reasoning paths and pick the most consistent"
  prompt did not help (+0.009, not significant), and propose-evaluate-select hurt
  (`schoenegger-2025`). Aggregation works across independent calls, averaged in code.

**6. Building a playbook without overfitting**

- **Empirical finding.** Prompt format alone moved accuracy by up to 76 points, and format
  rankings correlate weakly across models (Sclar et al., triaged). Most single-prompt "wins" in
  `schoenegger-2025` disappear under correction for 37 comparisons.
- **Empirical finding.** The spread among the top three of 15 prompts chosen on validation was
  0.007 Brier (0.167 to 0.174), larger than the whole effect of the prompt on test (about 0.002)
  (`halawi-2024`). A validation winner is mostly luck at these effect sizes.
- **Empirical finding.** Builders of competition forecasting bots often added complexity that did
  not pay off and tested opportunistically (Dhawka et al., triaged).
- **Convention (designs seen).** Choose prompts on a validation set and test later in time
  (`halawi-2024`); pre-register paired per-item differences against one control, with a mixed
  model and Benjamini-Hochberg correction (`schoenegger-2025`); report a range across prompt
  paraphrases (Sclar et al.); compare at matched compute (`sprague-2025`).
- **Our reading.** Tuning on episodes the model remembers rewards prompts that elicit recall:
  EXP-0029's reasons-first format raised the leak while looking more "analytic", and
  `halawi-2024`'s outcome-selected fine-tuning would carry hindsight if its training items were
  remembered. Stream 09 reached the same rule for template fields.

## Gaps

- No test of an analyst checklist for earnings releases, in any model, with an outcome after the
  model's cutoff.
- No study of prompt placement (reasons before, after, or in a separate call) for probabilistic
  forecasts; the evidence on order comes from MCQ, arithmetic and text rating.
- No evidence on the best number of checklist items.
- No forecasting-prompt study on Claude Opus 5.5 or Sonnet 5.5; the newest models tested are o1
  and Claude 3.5 Sonnet (`schoenegger-2025`) and Claude Sonnet 4.5 (Kanishka and Mandora).
- No study of whether reasons placed after the probability reduce a recall leak.

## Limits of this pass

- arXiv sources were read through a machine extraction of their HTML; three PDFs
  (`schoenegger-2025`, Chiang and Lee, Kanishka and Mandora) through macOS PDFKit text
  extraction. Numbers shown only in figures were not read (`pratt-2024`'s rationale plot,
  `lanham-2023`'s curves). Triaged rows rest on abstracts or partial reads as each row says.
- Searches (web, 2026-11-22): prompt engineering for LLM forecasting; superforecaster prompts;
  forecasting strategies; chain of thought in finance; financial sentiment and reasoning;
  earnings forecasting and chain of thought; unfaithful and post-hoc chain of thought; order of
  answer and reasoning; verbalised calibration; checklists; persona prompts; prompt sensitivity.
- `halawi-2024` gives the test cutoff as June 1, 2023 and June 1, 2024 in different places.
- Kim, Muhn and Nikolaev's ablation was read in v2 only, for the two accuracy figures; another
  agent deep-reads that paper.
- `li-2024`'s CFA-style chain-of-thought robustness result is not in its note and was not
  re-read.

## Leads checked and not added as rows

Abstracts read; nothing below changes a design decision.

- Lopez-Lira and Tang, Can ChatGPT Forecast Stock Price Movements? (arXiv 2304.07619 v6): headline
  scoring after the cutoff; no prompt ablation in the abstract.
- FinRobot (arXiv 2405.14767 v2): a whitepaper describing a "financial chain of thought" agent
  platform; no evaluation in the abstract.
- ForecastBench (Karger et al., arXiv 2409.19839 v5): experts beat the best LLM (p < 0.001);
  source of `schoenegger-2025`'s questions and of its expert-written prompt.
- Mizrahi et al., State of What Art? (TACL, arXiv 2401.00595 v3): single-prompt evaluations are
  brittle across 6.5 million instances; argues for multi-prompt evaluation (same point as Sclar
  et al.).
- Huang and Wang (PAKDD 2026, arXiv 2602.24060): reasoning cut binary sentiment F1 by up to 19.9
  points and helped 27-class emotion by up to 16.0.
- Xie, Order Matters in Hallucination (arXiv 2408.05093 v4): answer-first and reasoning-first
  outputs disagree, and the disagreement flags fabricated justifications.
- Sodha, When Reasoning Fails (arXiv 2511.08608): a thinking model ranked Indian stocks worse than
  a direct model as the universe grew, at a fixed reasoning budget.
- Crisostomo and Mykhalyuk (arXiv 2603.19944 v2): naive, structured and chain-of-thought prompts
  for stock picking; the abstract gives no comparison of the three.

## For the S2 analysis skill

Design rules, each with its evidence. "Thin" marks rules that rest on our reading or on evidence
from other tasks.

1. **Do the arithmetic in code; give the PM sentences, not tables.** Comparison base, guidance
   minus year to date (implied rest-of-year growth), revenue from acquisitions and disposals where
   the release states it, inventory and receivables growth against revenue growth. State each as
   a sentence with its number. Evidence: chain of thought is a poor substitute for a solver
   [`sprague-2025`]; LLM numeric skill on statements was recall [`levy-2026`]; the PM ignored a
   table of earlier quarters (+0.005, EXP-0032 s4); right clean calls rest on this arithmetic
   (EXP-0033) and the comparison base alone calls 65% (EXP-0034). Numbers that must be read from
   text (guidance) come from a rule-based parser or a reader call with a verbatim-quote check,
   then code does the sum.
2. **Give the base rate as a fact, and combine with the rule in code.** State a code-computed
   acceleration base rate (sector and quarter) as a sentence: reference-class prompts are the only
   elements with consistent small gains [`schoenegger-2025`]. EXP-0034's rules (R2 comparison
   base 0.652, R3 logistic 0.675 on all episodes; 0.64 and 0.57 on the 28 clean ones) are the
   rule baselines the PM must beat (AGENTS.md rule 8). Do not ask the PM to weigh a rule's
   probability: averaging model and crowd outside the model beat showing the crowd to the model
   [Schoenegger et al. 2024; `halawi-2024`]. Pre-register a weighted average of the PM and R3
   probabilities, weight fitted on development data.
3. **Keep the judgement checklist short and phrased as questions about the text.** Few items
   (thin: no evidence on the number; bundles did no better than single elements in
   `schoenegger-2025`, and decomposition was worst in `pratt-2024`). Candidates from EXP-0033's
   right calls: effects present this quarter and not next, or the reverse (currency, disposals,
   contract ends, plant outages, one-off gains); quarter-end exit rate against the quarter
   average; backlog or orders; guidance changes. Leave out generic mean-reversion advice: EXP-0033's
   wrong calls leaned on it. No persona [`schoenegger-2025`; Zheng et al.]. No instructed Bayesian
   updating and no propose-evaluate-select (both raised Brier by about 0.03 in
   `schoenegger-2025`).
4. **Where the reasoning goes: test four placements, expect small differences, and guard the
   leak.**
   - P0, probability only (the EXP-0026 control).
   - P1, probability first, then reasons (the rating-then-explanation design, as good as
     analysis-first for judgements [Chiang and Lee]). Thin: untested for forecasts; the
     probability cannot draw on its own reasons, which closes the evidence-selection channel
     EXP-0029 found, but not recall.
   - P2, playbook form first, probability last (EXP-0029's format). Expect higher decisiveness
     and a larger old-minus-clean gap [`turpin-2023`, Fu et al., `pratt-2024`, EXP-0029].
   - P3, two calls: a reader fills the playbook form from the release without being asked for a
     probability; code checks quotes and adds the computed facts; a fresh PM call gets the release
     and the form and gives the probability. The form is then an input that can be ablated field by
     field and tested for dependence by editing one field [`lanham-2023`]. Stream 09's caution
     applies: an informed reader can carry hindsight into judgement fields on old episodes; on
     clean episodes it cannot.
   Thin overall: no study compares these placements for probabilistic forecasts.
5. **Structured form over free text, with reasons before each field's answer, in XML tags.**
   A form lets code check quotes, count fields and ablate them; free-text reasons cannot be
   audited [`turpin-2023`; Chen et al.]. Inside the form put each field's reasoning before its
   value; answer-first fields hurt wherever computation is needed [Kanishka and Mandora]. Thin:
   one paper, not on forecasts.
6. **Aggregate several independent samples in code.** k = 5 calls per item, mean or the
   half-weight trimmed mean of the probabilities; report k = 1 beside it. Do not let a model
   aggregate [`halawi-2024`]. Give every arm the same k, so long-reasoning arms are compared at
   matched compute [`sprague-2025`]. Expected gain: about 0.003 Brier [`halawi-2024`].
7. **Measure calibration and level, not Brier alone.** Per arm: Brier and its reliability and
   resolution parts, log loss, mean probability, reliability curve, and the coherence probe (ask
   P(accelerates) and P(does not accelerate) in separate calls; the sum should be 1)
   [`pratt-2024`; Arcuschin et al.]. Report EXP-0026's readout beside them for continuity. Expect
   reasons-first arms to be more extreme [Fu et al.; `pratt-2024`; `schoenegger-2025`]. Any
   recalibration map is fitted on development data only; it did not help `halawi-2024`.
8. **Ablations to pre-register.** All on the same items, k = 5, one primary contrast:
   - A0 control (P0); A0a, A0b two paraphrases of the control, whose spread is the noise floor
     [Sclar et al.].
   - A1 control plus code-stated facts (rule 1).
   - A2 = A1 plus base-rate sentence (rule 2).
   - A3 = A2 plus checklist, placement P1; A4 = A2 plus checklist, P2; A5 = A2 plus checklist,
     P3.
   - A6 = the better of A3 to A5 averaged with R3 in code.
   - Primary contrast, fixed in advance: A1 against A0 on clean items (do code-stated facts
     help?). Secondary contrasts with Benjamini-Hochberg correction: A2 against A1; each checklist
     arm against A2; A6 against the better single arm [`schoenegger-2025`].
   - Guard readouts for every arm: old-minus-clean gap on the same texts, and, for A4 and A5, the
     edit-one-field dependence test [`lanham-2023`; EXP-0029 consequence (c)]. Reject an arm that
     raises the gap even if it raises accuracy.
   - Leave-one-field-out within the checklist only on development data.
9. **Develop on items the PM cannot remember.** Score development arms only on episodes that pass
   EXP-0029's recall gate (the PM cannot state next quarter's growth), or on clean items from
   companies held out of the test. Selecting a playbook on remembered episodes selects for recall
   (EXP-0029; stream 09). Keep a ledger of every prompt version scored (`gencay-2026`, stream 08).
   Freeze the skill text, then open the test once. Which development pool to use is an owner
   decision: AGENTS.md rule 2 puts development before the cutoff, where recall is the problem.
10. **Expected size of gains, and what that means for sample size.** From the evidence: a
    playbook prompt changes Brier by about -0.02 to +0.03 on general forecasting
    [`schoenegger-2025`], about 0.002 in the cleanest ablation [`halawi-2024`], and can hurt by
    0.03 to 0.07 [`schoenegger-2025`, `pratt-2024`]; averaging samples adds about 0.003
    [`halawi-2024`]. New information is what moved accuracy in every study [`halawi-2024`], which
    is why rule 1 is the arm most likely to matter. Our arithmetic: with a per-item SD of paired
    Brier differences near 0.12 (`schoenegger-2025` reports 0.07 to 0.17), detecting a 0.015
    difference at 80% power and 5% two-sided needs about 500 clean items; 90 items detect only
    about 0.035. EXP-0026 has 30 clean episodes. A playbook comparison on that scale cannot show
    a gain of the size the literature leads us to expect; it can only catch harm or a leak.
