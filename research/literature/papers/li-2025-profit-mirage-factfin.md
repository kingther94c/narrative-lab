# Profit Mirage: Revisiting Information Leakage in LLM-based Financial Agents

- **Citation:** Xiangyu Li, Yawen Zeng, Xiaofen Xing, Jin Xu and Xiangmin Xu (2025). Preprint
  (South China University of Technology; ByteDance; Pazhou Lab). arXiv 2510.07920. Version read:
  v1 (9 October 2025), HTML full text.
- **Link:** https://arxiv.org/abs/2510.07920
- **Stream:** 08, blind replay
- **Verified against source:** yes, 2026-11-19 (the whole HTML page of v1, appendices A to E
  included, read through a machine extraction answering targeted questions, in two passes;
  sections 2.1 to 2.4, 3.1 to 3.6 and 4.1 to 4.5 and Tables 3 to 9 covered; Figures 1, 2, 3, 5, 6
  and 7 are images and their values were not read; no number was checked against the PDF)

## Question
Do the backtest returns of LLM trading agents survive past the model's knowledge cutoff, how can
the leakage be measured, and can an agent be built whose decisions depend on its inputs and not
on recalled outcomes?

## Data
- **Decay study (section 2.1).** NASDAQ-100 constituents. Backtest window Q2 to Q3 2021 (market
  return +13.79%); generalisation window Q3 to Q4 2024 (+13.35%). Backbone GPT-4o, whose training
  cutoff the authors give as October 2023.
- **Counterfactual study (2.2).** Ten stocks, January 2022 to June 2023, 30 time points per stock
  chosen around major market events.
- **FinLake-Bench (2.3, Appendix B).** 2,000 question-answer pairs about January 2022 to June
  2023 in four categories: price, trend, event impact, market performance. The appendix calls it
  FinLeak-Bench. How questions and ground truth were sourced is not stated.
- **Fine-tuning study (2.4).** FNSPID news, 30 DJIA stocks; Qwen2.5-7B and Llama-3.1-8B with LoRA.
- **FactFin test (4.1, Appendix A).** Prices and news for AAPL, NVDA, TSLA, BYD, Tencent and
  Bitcoin, 1 January 2020 to 30 June 2025, from Yahoo Finance and the Alpaca News API. Test window
  1 July 2024 to 30 June 2025.
- Delisted firms: not applicable; the assets are six hand-picked names.

## Method
- **Decay (Eq. 3).** (X_pre − X_post) / X_pre for total return and Sharpe ratio.
- **Counterfactual perturbation (2.2.1, Appendix C).** Three kinds: key events are modified or
  removed; price sequences are replaced by historical averages or random walks; technical
  indicators and fundamentals are altered. The size of the perturbation and who generates it
  (rule or model) are not stated. Appendix C shows three hand-described cases.
- **Leakage metrics (2.2.2).**
  - Prediction consistency, PC: the share of predictions unchanged after perturbation.
  - Confidence invariance, CI: one minus the mean absolute change in confidence, over the
    unchanged predictions.
  - Input dependency score, IDS: mean KL divergence between the output distributions before and
    after perturbation.
- **How the authors read PC.** Higher PC is taken as more reliance on memory. The paper does not
  ask whether a perturbation was large enough to warrant a different decision, and gives no
  threshold or sensitivity check.
- **Counterfactual labels.** The contributions list says FinLake-Bench "includes memorization
  probes and counterfactual labels". No such labels are described anywhere. FinLake-Bench is a
  closed-book recall quiz scored with tolerance bands (for a price, full marks within ±1% and
  half within ±3%). The counterfactual samples of section 2.2 carry no expected answer: PC
  compares two outputs and needs no ground truth.
- **FactFin, four components (3.2 to 3.6).**
  - Strategy Code Generator: the LLM writes executable strategy code mapping the market state to
    buy, sell or hold.
  - Retrieval-Augmented Generation: retrieves the market state and turns news into sentiment
    scores and topic distributions.
  - Monte Carlo Tree Search: explores strategy variants with UCB selection; the generator
    proposes each variant and it is scored on an evaluation set.
  - Counterfactual Simulator: perturbs the data (Gaussian noise on prices, changes to factors and
    news), computes PC, CI and IDS on the original and perturbed data, and updates the strategy
    to minimise α·PC + β·CI − γ·IDS (Eq. 20, Algorithm 1).
- **"Strategy generator, not decision-maker", operationally.** The LLM's output is code; the code
  takes each trading decision. The LLM is called many times during the tree search to write
  variants. Not stated: whether the prompt carries the asset name or dates, whether the LLM is
  called again at trading time, the window the search is run on, the reward used by the search,
  the weights α, β, γ, and how PC, CI and IDS are computed for a code strategy. The prompt
  templates are said to be in an appendix that the HTML does not contain.

## Outcome variable and horizon
Total return, Sharpe ratio and maximum drawdown of single-asset buy, sell or hold trading over a
one-year test window; the three leakage metrics.

## Result
Empirical findings, as reported by the authors. None has a confidence interval.

- **Decay past the cutoff (2.1).** Sharpe decay from 51.48% (QuantAgent) to 62.23% (FinCON);
  total-return decay from 50.18% (TradingAgents) to 71.85% (FinMem). The two windows have matched
  market returns; that is the only control.
- **Counterfactual consistency of existing agents (2.2), PC / CI / IDS.** FinMem 0.8213 / 0.8743 /
  0.2766; QuantAgent 0.7789 / 0.8362 / 0.2941; FinAgent 0.7245 / 0.7781 / 0.3598; FinCON 0.7136 /
  0.7522 / 0.3612; TradingAgents 0.6903 / 0.7016 / 0.3837.
- **Closed-book recall (2.3).** Mean accuracy over GPT-4o, Claude-Sonnet-3.7 and Grok-3: 85.37%
  on price questions, 90.23% on trend, 92.94% on event impact, 89.83% on market performance.
- **Fine-tuning (2.4).** In-distribution accuracy rises from 51.61% to 72.16% (Qwen) and from
  54.73% to 76.52% (Llama); the reported change in generalisation is −21.53% and −18.06%.
- **FactFin after the cutoff (Table 3, 1 July 2024 to 30 June 2025), total return / Sharpe.**
  AAPL 36.70% / 1.22; NVDA 71.34% / 1.29; TSLA 165.01% / 1.83; BYD 84.24% / 2.09; Tencent 81.37% /
  2.31; Bitcoin 171.46% / 2.03. The best baseline's return on the same assets: 27.79%, 59.28%,
  115.09%, 57.96%, 66.31%, 134.36%. Buy and hold: −3.36%, 27.81%, 57.88%, 32.43%, 36.82%, 70.40%.
  The authors report mean improvements over the best baseline of 31.91% in return and 22.74% in
  Sharpe.
- **FactFin's leakage metrics (Table 4).** PC between 0.24 and 0.34, CI between 0.23 and 0.31,
  IDS between 0.75 and 0.83 across the six assets.
- **Ablation (Table 5).** AAPL return rises 8.77% → 13.36% → 28.12% → 36.70% as components are
  added, and PC falls from 0.6213 to 0.3115.
- **Backbones (Table 6).** Returns from 89.45% (Gemini-2.0-Flash) to 101.69% (GPT-4o). The asset
  and period of this table are not stated.

## Look-ahead and memorisation
This is the paper's subject. It uses three instruments: a comparison of a pre-cutoff with a
post-cutoff window, consistency under input perturbation, and closed-book recall questions. The
FactFin test window postdates the cutoff the authors give for GPT-4o. Cutoffs for the other
backbones in Table 6, and for Claude and Grok in the recall quiz, are not given.

## What it settles for us
- **Strategy E (the LLM writes rules, code applies them): supported in direction, weak as
  evidence.** Among the papers read for this stream it is the only test of an LLM used as a rule
  writer whose window is stated to postdate the backbone's cutoff. It rests on six hand-picked
  assets, one year, single-asset trading and no interval, and the window the search ran on is not
  stated. `gencay-2026` finds the opposite with stricter controls.
- **FactFin's low PC is not independent evidence.** The simulator minimises PC and CI and
  maximises IDS directly, so Table 4 reports the objective it was optimised on. This is our
  inference.
- **PC alone is not a leakage metric.** A call that does not move when the input changes may be
  recall or may be robustness. The paper has no notion of a perturbation that should change the
  call against one that should not. The plan's use B-2 (irrelevant against decision-relevant
  perturbations) is the missing control; keep it. This is our inference.
- **Counterfactual edits have no true label: supported.** The paper claims counterfactual labels
  and delivers none, which matches the plan's rule that edited episodes measure sensitivity only.
- **Agents with reflective memory decay most.** FinMem has the largest return decay and the
  highest PC of the five agents. The paper does not isolate the memory component, so memory as a
  contamination channel stays a hypothesis.
- **Reusable.** The recall-quiz format with tolerance bands, for the closed-book probe of
  strategy C; the decay ratio as a descriptive statistic.
- **Open question.** Whether a code-writing LLM encodes hindsight in its choice of rule. The
  paper does not test it.

## Limits
- The page has no limitations section.
- Internal inconsistencies. The benchmark is FinLake-Bench in the body and FinLeak-Bench in the
  appendix. Section 4.3 gives 50 counterfactual scenarios per asset and Table 7 gives 229 to 279.
  FinGPT's figures in the text of 4.2 differ from Table 3. The introduction says agents fail to
  beat a random baseline, and no random baseline is reported. The 1.4-times Sharpe claim is above
  the per-asset ratios in Table 3 (about 1.10 to 1.40).
- In section 2.4 the "unseen" test window (January to June 2022) lies inside the training window
  (January 2020 to December 2022).
- Perturbation size, the search reward, the objective weights and the prompts are not available,
  so the method cannot be reproduced from the paper.
- Transaction costs and slippage are described as standard and realistic, with no values.
