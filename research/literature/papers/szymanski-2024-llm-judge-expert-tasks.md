# Limitations of the LLM-as-a-Judge Approach for Evaluating LLM Outputs in Expert Knowledge Tasks

- **Citation:** Annalisa Szymanski, Noah Ziems, Heather A. Eicher-Miller, Toby Jia-Jun Li, Meng
  Jiang and Ronald A. Metoyer (2024). arXiv 2410.20266 v1, 26 October 2024 (cs.HC). No venue
  stated on the version read.
- **Link:** https://arxiv.org/abs/2410.20266 (HTML read: https://arxiv.org/html/2410.20266v1)
- **Stream:** 13b, reasoning item design (LLM-judge reliability against domain experts)
- **Verified against source:** yes, 2026-11-23. HTML main text and Table 3 read through a machine
  extraction; Table 1 (aspect question wording) was not visible.

## Question
Do LLM judges agree with subject-matter experts when the instructions require expert knowledge,
and does giving the judge an expert persona help?

## Data
Two domains, dietetics and mental health. 25 instructions with two candidate responses each
(GPT-4o and GPT-3.5-turbo). Raters: 10 registered dietitians, 10 clinical psychologists, and 10
lay users per domain. Judge: GPT-4 in a modified AlpacaEval set-up with randomised order.

## Method
Pairwise preference: one overall question plus two aspect questions per instruction (accuracy,
clarity, professional standards, educational context, personalisation), each with a short written
reason. Judge run with a general prompt and with an expert-persona prompt.

## Outcome variable and horizon
Percentage agreement of the judge with experts and with lay users; expert-expert agreement.

## Result
Empirical findings.

- **Judges agree with experts less than experts agree with each other.** Overall preference:
  judge-expert 64% (dietetics) and 60% (mental health) with the general prompt, 68% and 64% with
  the persona; expert-expert 75% and 72%.
- **Judges agree with lay users more than with experts:** 80% (general) and 76% (persona) in both
  domains.
- **Aspect agreement is uneven and the persona can hurt.** Dietetics accuracy 56% (general) and
  67% (persona); mental-health clarity falls from 70% to 40% with the persona.
- **Why they disagree (qualitative).** Experts flagged harmful or inaccurate content the judge
  missed; the judge equated clarity and quality with length and detail; experts valued relevance
  over comprehensiveness.

## Look-ahead and memorisation
Not applicable.

## What it settles for us
- **Generic pairwise LLM judging overstates quality in expert domains in a known direction:
  towards longer, more comprehensive-looking answers.** That bias would favour a verbose 4B over
  a terse 0.8B for reasons unrelated to analysis. S1 should not use preference judging for
  reasoning items (our inference).
- **An expert persona is not a fix.**
- **Measure the human ceiling first.** Expert-expert agreement was only 72 to 75% on pairwise
  preferences; any judge target for S1 needs the owner's own test-retest agreement on the same
  items as its ceiling.
- **Recommendation adopted by the authors and consistent with ours:** use the model judge for
  screening and keep the expert for a validation sample.

## Limits
- Small: 25 instructions, 10 raters per group, one judge model, no significance tests for the
  judge-expert comparisons; whether 25 instructions is per domain or in total is ambiguous in the
  text.
- Pairwise preference on advice, not grading of answers with a reference; agreement rates for
  reference-guided criteria are higher elsewhere (`arora-2025`, `chandak-2025`).
- The lay-alignment explanation (RLHF on lay feedback) is a hypothesis.
