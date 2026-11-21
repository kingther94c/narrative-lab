# Look-Ahead-Bench: a Standardized Benchmark of Look-ahead Bias in Point-in-Time LLMs for Finance

- **Citation:** Mostapha Benhenda (2026). Preprint; the arXiv listing gives the affiliation LAGA.
  arXiv 2601.13770, v1, 20 January 2026. Version read: v1, full text.
- **Link:** https://arxiv.org/abs/2601.13770
- **Stream:** 08, blind replay (S2)
- **Verified against source:** yes, 2026-11-19 (the arXiv abstract page for author and date; the
  arXiv HTML of v1, converted to plain text and read in full: abstract, sections 1 to 5 and
  Table 1. The reference list was searched, not read. The paper has no appendix. The code
  repository was not opened.)

## Question
Does the excess return of an LLM trading agent fall when the test window moves from inside the
model's training period to after its cutoff, and do point-in-time models avoid the fall?

## Data
- **Universe.** Five large-cap US technology stocks: AAPL, MSFT, GOOGL, NVDA, TSLA.
- **Windows.** P1, 1 April to 30 September 2021 (buy-and-hold +25.32%), inside the training period
  of the standard models. P2, 1 July to 31 December 2024 (buy-and-hold +24.75%), meant to be after
  it.
- **Standard models.** Llama 3.1 8B and 70B (stated cutoff December 2023) and DeepSeek 3.2 (stated
  cutoff July 2024).
- **Point-in-time models.** Pitinf-Small, Medium and Large, proprietary models from PiT-Inference,
  described by the author as having an effective cutoff of January 2020.
- **Inputs.** Historical price data built into the agent framework. Other inputs are not listed.
- Delisted firms: not applicable (five surviving mega-caps).

## Method
- **Agent.** The open-source AI Hedge Fund multi-agent framework (valuation, sentiment,
  fundamentals, technicals and investor-persona agents, a risk manager and a portfolio manager),
  adapted to monthly rebalancing: at the start of each month the agents see data up to that point
  and output weights for the five stocks.
- **Alpha.** The LLM strategy's return minus the buy-and-hold return over the window.
- **Alpha decay.** Alpha in P2 minus alpha in P1. A negative value is read as a sign of look-ahead
  bias in P1.
- **Baselines.** Buy-and-hold, equal-weight monthly rebalance, three-month momentum, three-month
  mean reversion, a 50/100-day moving-average crossover and a random-weights control.

## Outcome variable and horizon
Six-month portfolio return in excess of buy-and-hold, and its change between the two windows.

## Result
Empirical findings from one run per model; no standard errors, seeds, sampling settings or trading
costs are reported.

| Strategy | P1 alpha (pp) | P2 alpha (pp) | Alpha decay |
|---|---|---|---|
| Llama 3.1 8B | +13.81 | -3.42 | -17.23 |
| Llama 3.1 70B | +19.27 | +4.02 | -15.25 |
| DeepSeek 3.2 | +20.73 | -1.04 | -21.77 |
| Pitinf-Small | -0.25 | +0.06 | +0.31 |
| Pitinf-Medium | +2.44 | +3.29 | +0.85 |
| Pitinf-Large | +6.02 | +7.32 | +1.30 |
| Momentum (3 months) | +7.96 | +5.75 | -2.21 |
| Mean reversion | -4.62 | -15.40 | -10.78 |
| MA crossover | -27.78 | -17.84 | +9.94 |
| Random | -13.89 | -24.19 | -10.30 |

- The three standard models lose 15 to 22 pp of alpha between windows; the three Pitinf models are
  flat.
- The rule-based strategies, which cannot remember anything, move by between -10.78 and +9.94 pp
  across the same two windows. That range is the paper's only indication of how much alpha shifts
  between windows without any memorisation; the comparison is ours, not the author's.
- The author reads the Pitinf pattern (alpha rising with model size in both windows) as reasoning
  improving with scale once memory is removed, and the standard models' pattern as larger models
  holding stronger memorised priors. Hypothesis; the paper has three models per family and one
  run each.

## Look-ahead and memorisation
The paper's subject, measured only through its downstream footprint. Cutoffs are taken as stated.
P2 begins on 1 July 2024 and DeepSeek 3.2's stated cutoff is July 2024, so P2 is not clearly after
that model's cutoff (our observation). For the Pitinf models both windows lie after the stated
January 2020 cutoff, so their flat decay is what any model without knowledge of either window would
show; the paper offers no check of that cutoff beyond the vendor's description. The paper sets
itself apart from question-and-answer probes of what a model knows and does not run one.

## What it settles for us
- **Test after every cutoff (rule 2): supported as convention**, with weak evidence.
- **Performance decay as a leakage measure: not adopted.** It needs a post-cutoff window with
  enough realised outcomes, which S2 does not have (one clean quarter); it measures model and agent
  harness together; and it confounds the cutoff with the period. The plan already treats the
  old-period against post-cutoff accuracy comparison as descriptive. The 10 pp swings of the
  rule-based strategies here support that caution.
- **Reusable.** One idea only: run memory-free rule baselines across the same two periods, so that
  the period effect on a rule that cannot remember is visible next to the model's.
- **Point-in-time models as a comparison arm:** stream 03 already found the open ones too small to
  serve as extractors. This paper adds a proprietary family whose training cannot be inspected; it
  does not change that conclusion.
- Nothing here bears on the three candidate S2 measures directly.

## Limits
- Five stocks, two six-month windows, one run per model, no uncertainty estimates.
- No trading costs.
- The author calls the paper a proof of concept and lists small caps, other sectors and at least
  four periods as future work.
- The point-in-time models are commercial and closed; their cutoff is asserted, not tested.
- The agent's inputs beyond prices are not specified, so it is unclear what the LLM could draw on
  other than memory.
