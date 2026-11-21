# The Alpha Illusion: Reported Alpha from LLM Trading Agents Should Not Be Treated as Deployment Evidence

- **Citation:** Yuxuan Ye, Jun Han, Ao Hu, Juncheng Bu, Yiyi Chen, Liangjian Wen, Danilo Mandic,
  Danny Dongning Sun, Xu Yinghui and Zenglin Xu (2026). Position paper; preprint, Fudan University
  and others. arXiv 2605.16895, v1, 16 May 2026. Version read: v1, full text.
- **Link:** https://arxiv.org/abs/2605.16895
- **Stream:** 08, blind replay (S2)
- **Verified against source:** yes, 2026-11-19 (the arXiv abstract page for authors and date; the
  arXiv HTML of v1, converted to plain text. Read in full: abstract, sections 1 to 7, Tables 1, 2,
  4 and 5, and the text of appendices A to E. The per-asset rows of Table 3 were not read line by
  line. Figures 1 to 5 were read through their captions. The reference list was searched, not
  read. The code repository was not opened.)

## Question
What evidence must the reported return of an end-to-end LLM trading agent carry before it can be
read as deployable trading ability?

## Data
Mostly a review of other papers' results. One reproduction of the authors' own:
- TradingAgents and QuantAgent, one year from 2025-01 to 2026-01, an equal-weight portfolio of
  TSLA, NVDA, KO, XOM and MSTR starting at $100K, against buy-and-hold.
- "Net" deducts commission, token cost, spread and market impact.
- The backbone model of the reproduction and its knowledge cutoff are not stated in the text read.
- Delisted firms: not applicable to the reproduction. The paper asks others to report delisting
  and suspension handling (protocol P2).

## Method
An argument in three steps, then a reporting protocol.
- **Three confounds in published results:** temporal contamination, unmodelled trading frictions,
  and short windows combined with many researcher choices.
- **Three structural mismatches:** stated confidence is not a tradable probability; fluent
  financial narrative is not numerical execution; priors in the weights act as undisclosed factor
  exposures (the authors' term is parametric prior lock-in, offered as an explanatory framework,
  not an established mechanism).
- **Six reporting protocols.**
  - P1, temporal integrity: report model version, knowledge cutoff, post-training boundary,
    retrieval-corpus timestamps and memory-update rules, and include at least one post-cutoff or
    point-in-time window.
  - P2, dynamic universe: time-varying universe, delistings, liquidity filters.
  - P3, counterfactual robustness: direction-flip rate, confidence shift and position-size shift
    under strong reverse evidence; sector-neutral and style-neutral prompt tests.
  - P4, calibration: expected calibration error and reliability curves for any confidence used in
    sizing.
  - P5, realistic implementation: gross-to-net accounting, including token cost and latency.
  - P6, multi-agent disaggregation: single-agent baseline, role similarity, disagreement rate.
- **Tiers.** A text-extraction claim needs light P1 and P3; a backtest needs P1, P2 and P5; a
  deployable-alpha claim P1 to P5; an autonomous-trading claim all six.
- **The counterfactual diagnostic (P3).** The view-flip rate is the probability that the model's
  view changes when reverse evidence of a given strength is added. The authors require only
  monotonicity: as the reverse evidence strengthens, at least one of flip rate, stated confidence
  or position size should respond.
- **Proposed alternative.** The LLM extracts structured facts from filings and news; separate
  modules own features, signal, calibration, sizing and execution. Appendix E walks an 8-K
  guidance cut through the six stages.

## Outcome variable and horizon
For the reproduction: one-year portfolio value, Sharpe ratio and drawdown, gross and net. The rest
of the paper has no outcome variable of its own.

## Result
- **Reproduction (empirical finding, one year, five tickers).** Buy-and-hold ends at $104.8K;
  TradingAgents at $106.4K gross and $102.3K net; QuantAgent at $81.4K gross and $77.9K net.
  Portfolio Sharpe falls from 0.43 to 0.22 for TradingAgents and from -0.96 to -1.15 for
  QuantAgent. Net buy-and-hold beats both agents on four of five tickers. The authors note that
  over about 252 daily observations the 95% interval of a Sharpe ratio is wide enough to span the
  whole gap.
- **Friction coverage (the authors' tabulation).** Across FinMem, TradingAgents, FinAgent, FinCon
  and QuantAgent, 35 of 40 system-by-cost-component cells are unmodelled.
- **Figures quoted from other papers, not checked by us at their sources.**
  - Li et al. (2025, arXiv 2510.07920): past the cutoff FinMem's total return falls by about
    71.85% and QuantAgent's Sharpe by about 51.48%.
  - Shah et al. (2025): LLMs answer revenue questions correctly for 54.17% of large caps in 2017
    and 6.32% in 1995.
  - Lee et al. (2025, arXiv 2507.20957): six LLMs all tilt towards technology; with 60% of the
    evidence against its view the model with the strongest tilt flips in about 8% of cases and
    GPT-4.1 in about 30%; with all the evidence against, every model flips nearly always.
  - FinBen's GPT-4 trading Sharpe is 1.51 with a standard deviation of 1.08.

**Agent memory and reflection layers as a contamination channel.** The paper says little, and
nothing specific to reflection. What the text contains:
- Section 2.2 names three places where post-event information may already sit even when the code
  feeds only contemporaneous inputs: the model weights, post-training data and retrieval corpora.
- Protocol P1 lists the timestamps of the retrieval corpus and the rules by which memory is
  updated among the items to report.
- Section 2.4 lists memory length among the researcher's degrees of freedom.
- Layered memory and verbal reinforcement appear only as descriptions of FinMem and FinCon.
The paper does not analyse how an agent's stored memories or written reflections carry outcome
knowledge forward, does not measure it, and proposes no test for it beyond the reporting items in
P1.

## Look-ahead and memorisation
The authors treat post-cutoff, contamination-free evaluation as a minimum requirement, not an
extra: strong performance only inside the cutoff is more plausibly memory than prediction. They add
that knowledge inside the cutoff is itself uneven, better for large and recent firms, so a
mega-cap backtest is fragile twice over. They cite Merchant and Levy (2025) for the claim that
prompt restrictions and retrieval controls do not remove what is in the weights. They run no
memorisation probe. The reproduction window, 2025-01 to 2026-01, is described as post-cutoff, but
the model is not named.

## What it settles for us
- **Test after every cutoff (rule 2) and contamination labels (rule 3): supported as convention.**
  A position paper; it adds no measurement.
- **Counterfactual number edits: a confound to control.** A model can fail to follow an edit
  because of a standing sector or style prior, with no memory of the episode. If that prior points
  the same way as the realised outcome (a technology tilt in years when technology firms did
  well), the "follows less when the edit contradicts the outcome" gap appears without any outcome
  recall. Controls: estimate the model's prior call for each company with no document, or with a
  post-cutoff date, and include it; or run the same contrast on post-cutoff episodes as a placebo.
  The prior-stickiness evidence is Lee et al. as reported here; the confound and the controls are
  our inference.
- **Counterfactual number edits: a dose-response check.** Vary the size of the edit and require the
  follow rate to rise with it, the monotonicity the authors ask for in P3. An edit the model
  follows at no strength is a broken edit, not leakage (our inference).
- **Memory and reflection as a channel (strategies E and F): not addressed beyond a reporting
  rule.** Adopt the rule: every S2-d run records the playbook's or memory's update rule and the
  latest outcome date that fed each entry. The substantive question stays open in this group; see
  `wu-2026-memtrial-trust-memory.md` for the nearest evidence.
- **Role of the LLM.** The paper's modular design, with the LLM as schema-bound extractor and
  arithmetic and sizing elsewhere, matches the plan's choice to have code compute ratios and to
  compare the blind PM with statistical baselines. Its worked example is an 8-K guidance cut, the
  event this programme studies.
- **Reporting.** Sampling settings, prompt versions and parsing rules are degrees of freedom; rule
  9 already records them.

## Limits
- A position paper. Its one experiment covers five tickers for one year with an unnamed backbone
  model and no uncertainty estimates.
- Most numbers are quoted from other papers.
- Parametric prior lock-in is the authors' own framing, supported by one cited study.
- The claim that the reproduction satisfies P1 cannot be checked from the text.
