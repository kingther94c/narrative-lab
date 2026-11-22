# S2 analyst skill (v1, frozen 2026-11-22 for EXP-0036)

Status: v1. The owner agreed on 2026-11-22 to freeze it from the literature without tuning on
outcomes, and asked that what recurs and what is one-off be judged across lines, not only for
earnings. EXP-0036 uses the block between the markers below verbatim and records its hash; the
reader form (Part B) is rendered in `../experiments/exp0036_s2b_skill_v1.py`. Any change is v2. It turns literature streams 10, 11
and 12 (drafts, `../literature/streams/`) and EXP-0033's hand coding into a playbook for the S2 PM.

The owner's request (2026-11-22, changelog): "你光看这种 headline number、EPS 是涨，但里面是不是可以
持续的呢？……我觉得应该你去形成一个 skill，去更好的去 prompt 这种东西"; "从 accounting 的角度去看，其实具体
number 后面有没有什么帮助"; and on calls, "尤其是在回答问题的时候……有没有就是规避一些问题啊".

## What the evidence says about how to build it

1. **Information moves forecasts; instructions barely do.** Across 37 single and 17 compound
   prompts, none beat a probability-only control after correction; the best gained about 0.01 to
   0.02 Brier, and several, among them instructed Bayesian updating and an expert-written
   protocol, lost about 0.03 (`schoenegger-2025`). In `halawi-2024` the tuned scratchpad gained
   0.002; the gains came from new information. So most of the skill is facts placed in the input,
   not advice.
2. **Arithmetic goes to code and arrives as sentences.** Chain of thought adds little outside
   maths and loses to a tool at computation (`sprague-2025`); LLM numeric skill on statements was
   recall (`levy-2026`); our PM ignored a table of earlier quarters (EXP-0032, +0.005); the
   comparison base alone calls 65% (EXP-0034).
3. **Reasons before the probability are a risk, not a help.** A hidden bias moved answers by up to
   36 points while explanations named it once in 426 cases (`turpin-2023`); reasons-first pushes
   probabilities to the extremes (`pratt-2024`); in EXP-0029 reasons-first enlarged the old-minus-
   clean gap (0.236 against 0.155). The checklist is therefore filled by a separate reader call or
   after the probability, and every arm reports the gap.
4. **Short, and phrased as questions about the text.** No persona, no instructed updating, no
   generic mean-reversion advice (EXP-0033's wrong calls leaned on it).
5. **Small effects, few clean items.** Detecting a 0.015 Brier gain needs about 500 clean items
   (stream 12's arithmetic); we have 82 clean episodes among the 250 largest companies and about
   165 among the 500 largest. Model-arm comparisons can show large information effects and harm,
   not the size of gain a prompt usually gives. Cheap screens run in code first (EXP-0035).

## Frozen v1 text (EXP-0036)

The considerations block, identical in every PM arm of EXP-0036:

<!-- SKILL-V1-CONSIDERATIONS-START -->
Before answering, weigh these points; do not write them out:
- Line by line, which effects in this quarter will not recur next quarter, and which will start or end next quarter. Revenue: deals closed or closing, currency, calendar or an extra week, one-time or catch-up revenue, customers buying ahead or stocking up, disruptions, contracts starting or ending. Gross margin and operating costs: pricing, input costs, restructuring, one-time charges. Below operating income: gains or losses on investments or asset sales, tax items.
- What contracted or ordered revenue (backlog, bookings, remaining performance obligations), billings or deferred revenue, inventory and the company's guidance say about next quarter.
- Whether the year-ago quarter that next quarter is compared with is easier or harder than the one this quarter was compared with.
- Whether anything in management's wording is at odds with the numbers.
Prefer reasons found in this text and these facts over general habits such as "growth reverts to the mean".
<!-- SKILL-V1-CONSIDERATIONS-END -->

## Part A. Facts code states (no model; each one a sentence with its number)

- A1 **Comparison base.** "Next quarter is compared with a year-ago quarter that grew X%; this
  quarter's year-ago quarter grew Y%." (EXP-0034.)
- A2 **Reference rate.** Share of past episodes, resolved before the decision date, with the same
  comparison-base sign that accelerated (stream 12, rule 2: reference classes are the one prompt
  element with consistent small gains).
- A3 **Guidance arithmetic.** From guidance a reader quotes: implied next-quarter growth, implied
  rest-of-year growth from full-year guidance less the year to date (EXP-0032's converter, with
  "±" ranges fixed).
- A4 **Accounting items that pass EXP-0035**, e.g. "Inventory grew 18% against revenue growth of
  6%." Candidates (stream 10): remaining performance obligations, contract liabilities, inventory,
  gross margin, receivables; sector growth this quarter.

## Part B. Reader form (one call; each field a verbatim quote that code checks)

Each field: quote, value, and whether the effect is in this quarter only, next quarter only, or
both. Ranked by evidence for revenue (stream 10) and by EXP-0033's right calls.

- B1 **Contracted or ordered revenue:** backlog, bookings, book-to-bill, remaining performance
  obligations, and their change (`toynbee-2017`: backlog growth explains about 10% of next-year
  sales growth in manufacturers; annual, untested against past growth).
- B2 **Billings and deferred revenue** against revenue (Zhong et al. 2016; Prakash and Sinha 2013).
- B3 **Growth decomposition:** organic against acquired or divested, currency, price against
  volume, comparable-store against new units (Curtis et al. 2014 for retail; the rest untested).
- B4 **Effects that differ between this quarter and the next:** a deal closed during the quarter,
  currency turning, an extra week or selling days, one-time licence or catch-up revenue, buying
  ahead of a price rise or tariff, outages, strikes, weather, a contract starting or ending
  (EXP-0033: 7 of the 12 arithmetic-based right calls).
- B5 **Exit rate:** monthly cadence or "exited the quarter at" against the quarter's average.
- B6 **Guidance:** amounts, growth, and raised, kept, narrowed, lowered or withdrawn against the
  previous release (EXP-0032).
- B7 **Inventory and channel:** destocking or restocking, channel inventory, raw materials against
  finished goods if given (Bernard and Noel 1991: raw materials and work in process lead sales;
  finished goods do not).
- B8 **Management language in the release's quotes:** extreme negative words; hedges and
  uncertain words; is management gloomier than its own numbers? (`druz-2020`: unexpected gloom
  predicts next-quarter EPS beyond the release's tone; `bochkay-2020`: extreme negative words
  predict the next year's sales; both on calls, untested on release quotes.)
- B9 **Earnings label only:** one-off and non-core items (gains on investments or disposals,
  restructuring, impairments, litigation, pension marks, tax items, non-GAAP exclusions).
  `rouen-2021`: core earnings persist at 0.81, the adjustments at 0.18. These matter for EPS, not
  for revenue; a one-off inside revenue returns four quarters later as a comparison-base effect.

## Part C. PM questions (after reading the form; no more than five)

1. Which facts from A and B change next quarter's growth relative to this quarter's, and in which
   direction?
2. Is part of this quarter's growth absent next quarter, or the reverse?
3. Do contracted revenue, billings or guidance point to next quarter faster or slower than this
   one?
4. Is anything in management's wording at odds with the numbers?
5. Probability.

## Part D. Call module (only if transcripts become available)

Measured in code or by the reader, passed as features; raw call text is not given to the PM on
replayed history, because style and names re-identify the company (`lee-2016`: function words pick
the speaking manager among ten in 80 to 87% of calls). Ranked (stream 11):
- D1 gloom beyond the release, prepared remarks (`druz-2020`);
- D2 extreme negative words (`bochkay-2020`);
- D3 answers that sound scripted (`lee-2016`; needs the Q&A);
- D4 analysts' question tone (`druz-2020`; needs the Q&A);
- D5 direct refusals: read as wider uncertainty, not as a direction (`gow-2021`, `liang-2025`).
LLM labels of evasion need validation: two models disagree on about a fifth of flags and one
model repeats its own label about three times in four (`liang-2025`).

## How it is packaged

The canonical text is this file once frozen. The headless PM loads no skills
(`--setting-sources ""`, EXP-0027), so each experiment script reads the frozen text, puts it in
the prompt verbatim and records its hash. A Claude Code skill copy for interactive use can be made
from the same text.

## Development and validation

- Freeze v1 from the literature and EXP-0033 without tuning on outcomes. The 30 clean episodes
  already used serve only for format checks; the rest are opened once.
- Tuning on old episodes selects for recall (EXP-0029, stream 12 rule 9); if tuning is needed, the
  development pool is an owner decision (recall-gated old episodes, or clean items from held-out
  companies).
- Arms and readouts: see the S2 re-plan (EXP-0035 onward) in the registry.
