# Stream 08: replaying history without look-ahead

Sources checked 2026-11-19, for sub-study S2 (`../../design/substudy_s2_blind_replay.md`). Notes
are in `../papers/`; all 19 rows are in `08_blind_replay.csv`: 13 deep notes and 6 triaged rows.
Three papers that stream 03 triaged are read in full here (`glasserman-2023`, `engelberg-2025`,
`roy-2026`); the stream 03 rows stay as that pass wrote them. Stream 03 already covers
`lopez-lira-2025`, `gao-2025` and `wu-2025`, and nothing below repeats them.

The question the stream has to settle: a commercial model cannot be retrained and has read about
the past. How can pre-cutoff episodes be made usable for an agent's learning, and how would we
know that a method worked?

## What the stream establishes

**Blinding the input**

- **Empirical finding.** Recall of financial statements keys on exact numerals. Randomising the
  last digit of every item takes gpt-4 from 0.60 to 0.51 on the direction of next year's
  earnings (base rate 0.58); moving every decimal point three places, with no digit changed,
  does the same. Boosted trees on the same items go from 0.627 to 0.623 (`levy-2026`, Tables 6
  and 7). The inputs are unnamed, undated numeric tables.
- **Empirical finding.** No skill is left once recall is broken: the LLMs fall to or below the
  always-increase rate while the trees keep an AUC near 0.65 (`levy-2026`). The models did
  their own arithmetic, which they do badly (all balance-sheet items summed correctly 4% of the
  time, 100% with a code interpreter).
- **Open question.** Whether a model handed correct ratios keeps any skill under perturbation.
  Nobody has tested it (`levy-2026`, our reading).
- **Empirical finding.** Renaming does not hide a text. Masking the name leaves 69.1% of firms
  and 92.5% of dates identifiable in news; the name plus 20 related terms, 47.3%
  (`engelberg-2025`, section 4.2).
- **Empirical finding.** Iterated masking and paraphrase reach chance (firm 0.11%, date 0.03%
  after nine rounds), by replacing every number, percentage and unit with a placeholder. An
  earnings call needs up to 93 rounds. Large firms stay above chance. 16.3% of articles lose
  their sentiment (`engelberg-2025`).
- **Open question.** The rewriter is the contaminated model and is told the firm's name. Whether
  its rewrite tilts towards what later happened is untested (`engelberg-2025`, our reading).
- **Empirical finding.** A gap between calls on raw and on blinded text is not a measure of
  leakage. On headlines the blinded version predicts better in sample, the opposite of what
  look-ahead implies; a name carries a prior of its own, larger for big firms and present after
  the cutoff (`glasserman-2023`).
- **Verified fact.** The one trading framework built on renamed tickers shows the decision date
  to the model, has no identification test and no raw-ticker arm; its authors write that the
  "anonymization effect is not directly validated" (`jeon-2026`).
- **Verified fact.** The study Levy's setting resembles reported that the model named the firm
  in 0.07% of anonymised statements and concluded there was no memory; it was later withdrawn
  (triaged: Kim, Muhn and Nikolaev 2024). An identification rate near zero did not rule out
  recall.

**Measuring leakage with black-box access**

- **Empirical finding.** What a model can be made to recall, whether it can date a masked
  input, and whether its calls shift are different properties. One model dated 9% of masked
  snapshots and still moved its calls by 19.3 points when the date was shown; another recalled
  outcomes at 0.854 propensity and showed no shift (`jia-2026`).
- **Method.** Four arms that differ only in dating information (shown, date only, masked, wrong
  date), the same contrast on post-cutoff dates as a placebo, and a 20-sample recall probe with
  a hit-rate gate (`jia-2026`). The wrong-date arm is a positive control.
- **Empirical finding.** Measured cutoffs run earlier than the vendor's date for five of seven
  models, by three to eight months; one runs a month late (`jia-2026`).
- **Empirical finding.** The interaction of recall propensity with the forecast has both signs
  across models and is undefined where recall is saturated, as it is for the frontier models
  tested (`jia-2026`). Across models, the one with the highest recall had the smallest
  pre-cutoff advantage (`wu-2026`).
- **Empirical finding.** Results move with quantisation, reasoning mode, temperature and the
  reply parser (`jia-2026`).
- **Empirical finding.** Membership-inference scores and cross-model disagreement do not detect
  contamination once scores are normalised within a model: AUC 0.99 falls to 0.49 to 0.54, and
  to 0.38 within three months of a cutoff (`roy-2026`). They also need log-probabilities.
- **Empirical finding.** Performance decay across the cutoff is confounded with the period: rule
  strategies that cannot remember moved by 10 points between the same two windows
  (`benhenda-2026`); with 21 post-cutoff months a before-and-after gap had p = 0.36 (`wu-2026`).
- **Empirical finding.** A count of predictions unchanged under perturbation is not a leakage
  measure without a perturbation that should change the call (`li-2025`, our reading).
- **Hypothesis.** A standing prior for a sector or style, pointing the way outcomes went, would
  look like recall in a test with edited numbers (`ye-2026`, our inference from the evidence it
  reports).

**Other ways to use history**

- **Empirical finding.** Telling the model to ignore later knowledge lowered agreement with the
  post-cutoff ranking from 0.779 to 0.482; replacing only name and ticker, to 0.547 (`li-2026`).
- **Verified fact.** Both published ways of subtracting memory at the output work on logits of
  open models. A repeated-sampling version is named and not tested (`li-2026`,
  `merchant-2025`).
- **Empirical finding.** An LLM as rule writer: one positive result on six assets and one year
  without intervals (`li-2025`). With forward-looking features closed off and every trial
  counted, no LLM-written strategy beat luck, and a planted feature holding tomorrow's return
  passed the overfitting statistics (`gencay-2026`).
- **Empirical finding.** Agents that learn from replayed outcomes credit a lesson with the
  market's move (rank correlation 0.91 to 0.97); a test that a lesson predicts episodes it was
  not built from passed on at most 0.6% of decisions on real data, and no such agent beat the
  equal-weight rule (`wu-2026`).
- **Triaged.** Auditing a rationale claim by claim and answering again from the admissible
  claims cut measured leakage on a stock-ranking task from 0.171 to 0.001 and rank correlation
  from 0.543 to 0.167 (Zhang, Chen and Stadie 2026). Logical consistency across related
  forecasts correlates with forecast quality, but forcing consistency did not improve it (Paleka
  et al. 2024). A playbook written with hindsight scores better as its hindsight subscore falls
  (Ghosh 2026, exploratory).

## Design defaults

- **Rule 2, test after every cutoff: supported**, and nothing found offers a substitute. Measured
  cutoffs err on the early side in most cases; one is late, so the buffer stays.
- **Rule 2, no masking for the main benchmark: supported.** The method that hides a text deletes
  its numbers.
- **GY-0000, the condition for bringing masking back: not met by any paper.** Nobody shows a
  method that hides a large company and keeps the numbers a fundamentals call needs. S2's test
  of it is new work.
- **Rule 8, simple baselines first: supported** four times over (`levy-2026`, `wu-2026`,
  `roy-2026`, `gencay-2026`).
- **Methodology §9, the memorisation probe: supported, with a better specification.** Repeated
  samples, a hit-rate gate, an "unknown" accepted in any wording, pinned sampling and reasoning
  settings (`jia-2026`); scores demeaned by entity and period (`wu-2026`).
- **Methodology §9, the item-level regression of accuracy on recall propensity: weakened.** It
  may be undefined or wrongly signed on a frontier model. Check the variance of the propensity
  first.

## What this changes in S2

Mapped to the strategy letters of the design, §4.

- **A, blind the input.** Renaming and scaling cannot be expected to hide a press release. Noise
  on numbers is supported on bare tables only; text with structure is untested (H3). Scale with
  non-round factors: a power of ten keeps the digit string, which a nearest-neighbour match
  finds at once (our inference). Keep the statements adding up, which Levy's perturbation did
  not. Rewriting by an LLM is not this task once it removes the numbers.
- **B, several views.** Assign what each view shows by design and contrast arms; do not sort
  views by what an attacker recognised. A half-fraction over four elements gives eight views.
  Add a wrong-identity arm as a positive control and run the same contrasts after the cutoff as
  a placebo. Pool before reading: a per-episode estimate is noise.
- **C, select instead of blind.** Strengthened. A closed-book probe can locate where recall
  ends, and that point is often months before the vendor's date. Gate the probe on its hit rate.
  The selection rule of `merchant-2025` (recalled in at least 3 of 4 runs, or in at most 1 of 4)
  is reusable.
- **D, change the question.** Weakened for return labels: a within-sector ranking task still
  leaked. Kept for the label only.
- **E, the model as rule writer.** Needs a closed vocabulary of as-filed features, a ledger of
  every version scored, and a stopping rule. Prior: low. Whether a rule writer picks rules it
  knows worked is untested everywhere.
- **F, the learning signal.** The lesson writer must be as blind as the forecaster. Score a
  lesson within the episode, with and without it; accept it only after it predicts unseen
  episodes; record each playbook entry's latest outcome date.
- **G, debias the output.** Not available with a commercial model. The call from company and
  period alone survives as a control and as C's gate.
- **New, J.** Audit the rationale by claim. It catches only leakage that is put into words.
- **New, K.** Outcome-free consistency checks as a diagnostic.
- **Information kept.** Measure it by accuracy and by the increment over a statistical baseline
  on post-cutoff episodes. Agreement with the raw-text call is secondary: the name can distort
  as well as inform.

## Gaps

- No study blinds text while keeping its numbers usable, or measures what that costs.
- No study tests numeric noise on a document with segment structure and narrative.
- No study measures leakage for a fundamentals call at company level with arms assigned by
  design; `jia-2026` does it for macro snapshots with a crisis list as readout.
- No study tests whether an LLM given computed ratios has skill on blinded statements.
- No study tests hindsight carried by a rewriting or lesson-writing model.
- None of the audits covers Claude Opus 5.5 or Sonnet 5.5.

## Limits of this pass

- `li-2025`, `li-2026`, `merchant-2025` and `gencay-2026` were read through a machine
  extraction of the arXiv HTML; no number was checked against a PDF.
- `engelberg-2025` was read in its draft of 26 June 2026. Earlier drafts report other rates;
  Levy cites the paper for firm-name guess rates of 25% or more, which the current draft does
  not contain.
- Not opened: Levy's online appendix; the companion paper and artefacts of `jia-2026`; arXiv
  2601.13717 (instructed against true ignorance); Lee et al., arXiv 2507.20957 (prior
  stickiness); Koijen and Levy 2026 (real-time evaluation of agents); arXiv 2607.14051. Nothing
  is claimed from them.
- The triaged rows rest on abstracts and method sections.
- A spot check of load-bearing claims against the sources is recorded in the S2 changelog entry.
