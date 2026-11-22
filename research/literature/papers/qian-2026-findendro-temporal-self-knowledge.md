# LLMs Don't Know What They Know: Benchmarking Temporal Self-Knowledge for Financial Backtesting

- **Citation:** Lingfei Qian, Yan Wang, Xueqing Peng, Yupeng Cao, Yuechen Jiang, Zhuohan Xie,
  Anke Xu, Wenbo Cao, Jiarui Chen, Zehan Li, Jimin Huang, Alejandro Lopez-Lira, Yuehua Tang,
  Sophia Ananiadou and Jian-Yun Nie (2026). arXiv 2611.06808 v1, 4 November 2026. Version read:
  v1, HTML.
- **Link:** https://arxiv.org/abs/2611.06808 (HTML read: https://arxiv.org/html/2611.06808v1)
- **Stream:** 09, rewrite blinding (question 5: alternatives that keep a commercial model; also
  question 2)
- **Verified against source:** yes, 2026-11-22 (abstract, benchmark construction, Tables 4, 6,
  8 and 9, the procedure and the limitations, through a machine extraction of the HTML; the
  benchmark's name is garbled in the HTML and is taken from the abstract page)

## Question
Can a backtest be certified free of look-ahead by trusting a vendor's cutoff, by asking the model
what it knows, or by telling it to answer as of a date?

## Data
FinDendro: 2,226 dated US facts, January 1999 to September 2026, from a pool of 20,972: 1,353
first-release macro observations (12 FRED series), 540 month-end closing prices of 50 large
companies, 333 Federal Reserve rate decisions. Dense from 2021 (1,170 facts).

## Method
Four prompts per fact: choose the value (no claim); choose among value-and-claim pairs
("know" or "don't know"), in a recall and a predict wording; and the predict wording with "Assume
that today is [date]". Four candidate values with the true rank random; a persistence control
drops the 47% of numeric facts where last month's value is correct; policy facts scored by
balanced accuracy. Chance is about 0.27 on the controlled subset of 1,340 facts. Models: GPT-5,
DeepSeek-V3.2, GPT-4o, Llama-3.3-70B, Qwen3-8B, Qwen3.5-9B, and three point-in-time model
families (TiMaGPT, ChronoGPT-Instruct, DatedGPT). No Claude model.

## Outcome variable and horizon
Accuracy, rate of knowledge claims, measured knowledge boundary. No horizon.

## Result
Empirical findings.

- **Self-reports understate knowledge (Table 4):** GPT-5 is right on 0.76 of controlled facts,
  claims to know 0.38, and is right on 0.61 of the facts it says it does not know.
- **Declaring a date removes claims, not knowledge (Table 4):** GPT-5's claims fall from 0.39 to
  0.01 while accuracy goes from 0.76 to 0.75; Llama-3.3-70B's claims fall from 0.63 to 0.00 with
  accuracy 0.41 to 0.41.
- **Boundaries (Table 9):** GPT-5's measured knowledge ends 2024Q3, matching its vendor date;
  GPT-4o's ends 2023Q1, about seven months before its stated cutoff; Llama-3.3-70B's ends 2021Q2
  while its claims persist to 2023Q1, seven quarters later.
- **Point-in-time models (Table 8)** stay near chance before and after their cutoffs.
- Procedure proposed: measure accuracy on dated facts of the target domain, set the boundary
  halfway between the model's 2015 to 2020 accuracy and chance, test only after it with a margin,
  never rely on self-reports or declared dates, re-measure when the model changes.

## Look-ahead and memorisation
The paper's subject.

## What it settles for us
- **An instruction to answer only from the text, or as of a date, certifies nothing.** A model
  told the date stops saying it knows and answers just as well. The same holds for an extractor
  told to use only the release: its compliance cannot be read from its output (our reading,
  consistent with `ludwig-2025` on date-restriction prompts).
- **Rule 2 and the S2 recall probe: supported.** The boundary should be measured behaviourally
  for the roster models, which this paper does not cover.
- **Alternative to blinding:** choose replay periods after a measured knowledge boundary. For a
  frontier model that leaves only months, not years, of history (our reading).

## Limits
- Macro values, prices and rate decisions, not company documents or guidance.
- One response per prompt at temperature 0 through an API router.
- Multiple-choice claims only; free-text behaviour may differ.
