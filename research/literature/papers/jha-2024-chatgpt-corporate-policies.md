# ChatGPT and Corporate Policies

- **Citation:** Jha, M., Qian, J., Weber, M. and Yang, B. (2024). Working paper: Chicago Booth Paper No. 23-15; arXiv 2409.17933. Version read: arXiv v2, dated February 2025 (first version July 2023). A search listing also shows it as NBER Working Paper 32161; that page was not opened.
- **Link:** https://arxiv.org/abs/2409.17933
- **Stream:** 02, LLMs extracting financial signals
- **Verified against source:** yes, 2026-11-12, against the full text of arXiv v2. The text was extracted from the PDF by script, which drops minus signs in running prose, so every signed number below was taken from the tables.

## Question

Can an LLM extract managers' expected change in capital spending from earnings calls, and does the extracted expectation predict investment and returns beyond Tobin's q?

## Data

Earnings call transcripts, 2006 to 2020 (the vendor was not recorded in this reading). 160,195 transcripts; 115,620 after the merge with CRSP and Compustat; 74,429 firm-quarters with all variables, for 3,878 US firms (the introduction says 3,863). Duke CFO Survey answers are matched to 1,338 firm-quarters. Whether delisted firms are included is not stated; every observation needs CRSP and Compustat data.

## Method

ChatGPT 3.5. Each call is split into chunks of under 2,500 words (a typical call gives three). One prompt per chunk, "Based on this text only", asks how the firm plans to change capital spending over the next year: five choices, a one-sentence explanation, and "no information is provided" as an allowed answer. The choices map to -1, -0.5, 0, 0.5 and 1; "no information" also maps to 0; the call's score is the mean over its chunks.

Validation is by four routes: a regression of CFO survey answers on the score, the aggregate time series, industry patterns, and reading excerpts. A manual check of a random sample finds that choice and explanation disagree in under 1% of cases.

The comparison model is RoBERTa fine-tuned on BoolQ, asked a yes/no question on 300-word chunks. Dividend and employment scores come from one prompt with two questions and the instruction to "answer each question independently".

## Outcome variable and horizon

- Capital expenditure over book assets in quarter t+2 (the quarter after the call) and each quarter to t+10.
- Annualised quarterly return in t+2 and to t+10: raw, Fama-French five-factor adjusted, q5 adjusted.
- Cumulative abnormal return over days [0,1], [0,3] and [0,5] from the call (Carhart four-factor).
- Change in the analyst consensus capex forecast.
- CFO survey: expected percentage change in capital spending over the next 12 months.

## Result

All are empirical findings. Standard errors are clustered by firm (by industry for the survey regressions).

- **Survey anchor.** Coefficient 30.83 (t = 4.36), R-squared 0.014, no fixed effects, N = 1,338; 21.78 (t = 3.57), R-squared 0.070, with industry and quarter fixed effects. One standard deviation of the score goes with 4.0% higher expected capex, 0.1 standard deviations. Dividend and employment scores: R-squared 0.023 (N = 666) and 0.007 (N = 1,322).
- **Future capex.** 0.477 (t = 13.91), incremental to total q, lagged capex, cash flow, leverage, size, firm and quarter fixed effects. One standard deviation of the score is 0.055 to 0.079 standard deviations of capex, which the authors put at 46 to 78% of the sensitivity to total q. Significant for nine quarters.
- **Against RoBERTa.** RoBERTa alone: 1.321 (t = 8.28), R-squared 0.573. ChatGPT alone: R-squared 0.575. Together: ChatGPT 0.444 (t = 12.99), RoBERTa 0.980 (t = 6.23), R-squared 0.575.
- **Next-quarter returns.** -9.94 (t = -4.57) raw, -8.08 (t = -3.53) FF5, -7.73 (t = -3.42) q5, incremental to total q and the lagged return. One standard deviation is -1.83%, -1.49% and -1.42% annualised.
- **Announcement return.** CAR[0,1] 3.18 (t = 12.72), incremental to Loughran-McDonald sentiment; one standard deviation is about 0.6%.
- **Coverage.** About three-quarters of chunks indicate no change; 11% increase, 10.8% decrease, 1.87% and 0.32% substantial increase and decrease. About half of calls have a non-zero score.
- **Repeatability.** Two runs on a 10% subsample give scores correlated 98.68%.

## Look-ahead and memorisation

Two tests.

1. Post-cutoff sample, 2021Q4 to 2022Q4 (the authors give September 2021 as the end of ChatGPT 3.5's training data): 0.724 (t = 5.24), N = 10,470, with industry rather than firm fixed effects. Only the capex result is reported for this sample; the return results are not.
2. Masked identity: dates and the names of firms, people and products are replaced with "###" (regular expressions plus spaCy `en_core_web_sm`) on a random 10% subsample. Coefficient 0.224 (t = 3.26), N = 7,259, against 0.323 for the unmasked score on the same subsample (stated in the text, not tabulated).

No memorisation probe is run.

## What it settles for us

- **Numeric anchor (supports, with a warning).** This is the closest published design to our L2 test: an LLM-extracted expectation checked against a number managers reported elsewhere. The anchor explains 1.4% of variance at N = 1,338. Anchored tests in our design must be powered for effects of that size.
- **Extraction accuracy as the confirmatory endpoint (leaves open, shows the gap).** The paper never scores the extraction against human labels. The under-1% figure is agreement between the model's choice and its own explanation.
- **Return prediction exploratory (supports).** The return results are not re-tested after the cutoff.
- **Each feature on its own with evidence (supports in practice, untested).** One question per prompt for the main score, an explanation with each answer, and an explicit independence instruction where two questions share a prompt. No comparison with joint extraction.
- **Unit of analysis (partly supports).** Three-quarters of chunks carry no signal, which favours selecting passages. Scores are levels per call; nothing compares consecutive calls.
- **Reusable.** The five-point prompt wording; a fine-tuned encoder asked a yes/no question as the FinBERT-class baseline; "no information" as an explicit answer, which we should keep as its own class.

## Limits

- "No information" and "no change" share the value zero.
- Prepared remarks and Q&A are not separated.
- The post-cutoff test covers five quarters and changes the fixed-effect structure.
- The masked score's coefficient is about 30% below the unmasked score's on the same subsample.
- Firm counts differ between the introduction and the data section.
- Transcripts, not press releases; one model.
