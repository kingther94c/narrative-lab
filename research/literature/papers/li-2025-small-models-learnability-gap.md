# Small Models Struggle to Learn from Strong Reasoners

- **Citation:** Li, Y., Yue, X., Xu, Z. and others (2025). Findings of ACL 2025, pp. 25366-25394;
  arXiv 2502.12143. Version read: v3 (13 November 2025), HTML (about 90% of the page; the tail of
  the appendix not read). Only the first three authors were checked.
- **Link:** https://arxiv.org/abs/2502.12143 (HTML: https://arxiv.org/html/2502.12143v3)
- **Stream:** 13a (comparable domain: mathematics)
- **Verified against source:** yes, 2026-11-23, against the arXiv abstract page and the v3 HTML through
  an automated page reader.

## Question

Do small models gain from distillation of long chain-of-thought traces, or of traces from much
larger teachers, as large models do?

## Data

MATH training set, 7,500 prompts; teacher responses by greedy decoding with rejection sampling to
keep correct ones. Evaluation on MATH, GSM8K, AMC 2023, AIME 2024 and OlympiadBench (English math),
averaged; zero-shot greedy; Qwen2.5-32B-Instruct judges when exact match fails. No financial data.

## Method

- Students: Qwen2.5 0.5B, 1.5B, 3B, 7B, 14B, 32B; Llama 3.2 1B and 3B, Llama 3.1 8B, Llama 3.3 70B.
- Long against short CoT: QwQ-32B-Preview against Qwen2.5-32B-Instruct as teacher.
- Large against small teacher: Qwen2.5-72B against 3B, Llama 3.1 70B against 8B, Gemma2 27B against
  9B.
- Full fine-tuning below 14B (lr 1e-5, two epochs), LoRA above.
- Mix Distillation: blend long and short (or large- and small-teacher) traces, 1:4.

## Outcome variable and horizon

Average accuracy across the five math benchmarks. No horizon.

## Result

- Long against short CoT (Qwen, Table 1): 0.5B 14.8 against 19.5; 1.5B 27.0 against 34.2; 3B 40.3
  against 43.4; 7B 48.9 against 47.2; 14B 59.2 against 54.3; 32B 73.0 against 59.3. Short traces
  win up to 3B, long traces from 7B.
- Large against small teacher (Table 2): Qwen 0.5B and 1.5B learn better from the small teacher; 3B
  about even (+0.3); 7B and above gain from the large teacher (+6.6 at 7B). Llama crosses over
  between 1B and 3B.
- Mix Distillation at Qwen2.5-3B: 45.9 (mix-long) and 45.8 (mix-large) against best single source
  43.4; MATH 64.7 against 56.2 for long CoT alone. Smaller gain for Llama 3.2-3B (32.5 to 35.1).
- Explanations offered (hypotheses): small students fit long or large-teacher text worse (higher
  perplexity); they lack domain knowledge (a math-specialised 1.5B shows a smaller gap); long traces
  mostly change stylistic tokens. Asking the large teacher to write simpler answers did not help.
- No intervals or seeds reported in the parts read.

## Look-ahead and memorisation

Not relevant (math benchmarks); contamination not discussed.

## What it settles for us

- Directly relevant to S1's 0.8B student and 4B teacher: below about 3B, a smaller teacher and
  shorter traces are the better default. A 4B teacher for a 0.8B student is on the right side of
  this finding; switching to a much larger teacher or to long "thinking" traces is not expected to
  help, and may hurt.
- If S1 adds reasoning-style items, test short-trace against long-trace distillation, and a mix,
  rather than assuming the thinking mode of Qwen3.5-4B is the right teacher output.
- The domain-knowledge hypothesis matches finance results (`tong-2026` knowledge bottleneck;
  `zhang-2025` terminology gains from retrieval): a small student may need definitions supplied,
  not just traces.

## Limits

Math only; crossover sizes may differ for financial text; one data set (MATH) for training.
