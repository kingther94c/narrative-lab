# Can Language Models Use Forecasting Strategies?

- **Citation:** Sarah Pratt, Seth Blumberg, Pietro Kreitlon Carolino and Meredith Ringel Morris
  (2024). arXiv 2406.04446, v1 of 6 June 2024 (the only version). No venue stated.
- **Link:** https://arxiv.org/abs/2406.04446
- **Stream:** 12, forecast prompting
- **Verified against source:** yes, 2026-11-22. arXiv HTML of v1 read as extracted text:
  abstract, sections 1 to 7 and Tables 1 to 3. Appendix tables (test-set results, Table 6) and
  figures read by caption or not at all.

## Question
Do strategies that help human forecasters (break the event down, start from base rates, argue
both sides, average a crowd of personas, read the news) help an LLM forecaster?

## Data
- GleanGen, Google's internal play-money prediction market (more than 2,000 employees). Internal
  Google topics removed; Covid-19, Finance, Technology Industry and Miscellaneous kept. 351
  validation and 341 test events. Most events resolve "No".
- The comparison is made on one date, 1 August 2022, just after the model's pre-training end
  (July 2022). 78 validation events were open on that date. Human baseline: the market's
  midpoint on that date.

## Method
- Model: PaLM 2. Each strategy is a chain of LLM calls whose last call gives a probability.
- Arms: Basic (event details, give a probability); Forecaster (the prompt of Schoenegger et al.
  2023); Breakdown (sub-events); Base Rates; Both Sides; Crowd (many personas of one model,
  averaged); News API (New York Times and Hacker News headlines).
- Extra analyses: a "Weighted Brier" that averages the Brier on Yes and on No events; the same
  events with and without a rationale before the answer; the reversed event ("does not happen")
  subtracted from 1.

## Outcome variable and horizon
Brier score on events open on 1 August 2022, resolved later (many at the end of 2022).

## Result
Empirical findings.

- **Validation Brier (Table 1).** Basic 0.1221, News API 0.1235, human market 0.1334, Forecaster
  0.1483, Both Sides 0.1553, Base Rates 0.1562, Crowd 0.1706, Breakdown 0.1895. No strategy beats
  the basic prompt; the authors say the same holds on the test set (Appendix Table 6, not read).
- **Weighted Brier (Table 2).** Humans are best (0.1746); Basic 0.1955; Crowd 0.1860; Base Rates
  0.2540. On events resolving Yes, Basic scores 0.3407 against the humans' 0.2592; on events
  resolving No, 0.0503 against 0.0901.
- **Rationale shifts the level.** With a rationale before the answer, the model gives
  consistently higher probabilities than when it "just answers" (Figure 1; no table of numbers).
  With mostly "No" events, higher probabilities raise Brier.
- **Incoherence.** Mean probability 0.2529 for the event, but 1 minus the probability of the
  reversed event is 0.3965 (Table 3). The model leans low on both the event and its negation.
- **Authors' reading (hypothesis).** The basic prompt's apparent win comes from a bias towards low
  probabilities meeting a base rate of mostly "No", not from forecasting skill.

## Look-ahead and memorisation
Handled by choosing a model with a known pre-training end (July 2022, obtained by personal
correspondence with the model's engineers) and forecasting from 1 August 2022. The authors note
that models may misstate their own cutoff.

## What it settles for us
- **Asking for reasons changes the probability level, not only its quality.** A
  rationale-first prompt moved PaLM 2's probabilities up across events. In S2, EXP-0029's
  reasons-first format moved readouts towards the realised outcome on old episodes. Any playbook
  arm must be compared on calibration and mean probability, not only on Brier, and its effect on
  the old-minus-clean gap reported.
- **Check the base rate before reading a Brier gain.** A model biased towards one side can win on
  a skewed sample. S2 should report the base rate of acceleration in each evaluation set and a
  class-balanced score beside Brier.
- **Coherence probe to reuse.** Ask for P(accelerates) and, separately, P(does not accelerate);
  their sum is a cheap test of a level bias in each arm.
- **Decomposition did worst.** Breakdown raised Brier by 0.067 over the basic prompt here. Weak
  support for keeping playbook steps few.

## Limits
- One older model (PaLM 2); 78 events on one date; play-money market of company employees.
- No intervals or significance tests in the tables read.
- The rationale effect is shown only as a scatter plot.
