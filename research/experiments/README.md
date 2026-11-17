# Experiments

One script per experiment, named `expNNNN_<slug>.py`, with a matching entry in
[`../registry/experiment_registry.md`](../registry/experiment_registry.md).

- A script is frozen once it has been run for the record. Fix forward in a new numbered script.
- Outputs go to the external drive, not here.
- Anything a script establishes that later code relies on is lifted into the package with a
  citation back to the experiment.

| Script | Experiment | What it established |
|---|---|---|
| `exp0000_feasibility_probes.py` | EXP-0000, run 2026-11-12/13 | Whole documents fit for inference (32k tokens at 4.75 GiB on Qwen3.5-4B, 6.99 GiB on the 9B). LoRA on Qwen3.5 fits only up to 512 tokens (4B) or 256 (9B) within 12 GiB; models with ordinary attention fine-tune at 2k to 4k. Details in `../design/feasibility.md`. Known defect: the training callback recorded no per-step speed; it was read from the logs. |
| `exp0002_edgar_census.py` | EXP-0002, run 2026-11-13 | Items 1.03, 2.06 and 4.02 each run at about 1% of the earnings-release universe a year; Item 3.01 at 14 to 17%, far too frequent to be failures (split by text pending). 7,244 earnings 8-Ks after the cutoff. About 39% of releases carry numeric guidance and about 8% words only (rule flags corrected by a hand check of 49 pre-cutoff releases). Details in `../design/data_audit.md`. |
| `split_v1.py` | Shared definition, not an experiment; frozen 2026-11-15 | Company split v1: salted SHA-256 of the CIK, 60% test, 10% development, 30% training; co-registrants grouped under their smallest CIK. Every later script imports it; a change is `split_v2.py`. |
| `exp0006_s1a_compression_probes.py` | EXP-0006, run 2026-11-16 | Whole 4-layer blocks come out of Qwen3.5-4B and save as stock checkpoints (16 layers: 2.42 B parameters); single DeltaNet layers do not. Expert slicing on OLMoE-1B-7B matches the masked model (1.94 against 3.63 GiB on disk). Every Qwen3.5 rung, the 0.8B included, trains at 512 tokens and not 1,024; full fine-tuning of the 0.8B fits at 512 (7.17 GiB). A 400-token excerpt leaves about 70 tokens for an answer. Details in `../design/feasibility.md` §6. |
| `exp0005_earnings_exam.py` | EXP-0005, run 2026-11-15 | EarningsExam v0 for S1: 4,420 train, 4,392 development and 18,618 test items (1,989 test companies), each confirmed by a release table row and the XBRL value; 30 of 30 hand-checked train and development golds right. Test items are not read by Claude (`show` refuses them). Details in `../design/feasibility.md` §5. |
| `exp0004_company_split.py` | EXP-0004, run 2026-11-15 | On the 3,915 companies of EXP-0003: 2,356 test, 399 development, 1,160 training (60.2 / 10.2 / 29.6%), balanced across filer sizes. Raw numeric pairs on the test side: 1,737 with the later release after the cutoff, 801 with both. Details in `../design/data_audit.md` §8a. |
| `exp0003_guidance_pairs.py` | EXP-0003, run 2026-11-13 | Keyword rules v2 (43 of 49 dev releases right; on a fresh 30, a numeric flag is right 10 times in 13). Of 6,993 post-cutoff releases with text, about 36% carry numeric guidance. Pairs with numeric guidance in both: about 1,700 to 2,200 if only the later release postdates the cutoff, 800 to 1,000 if both do. 79 co-registrant companies dropped. Details in `../design/data_audit.md` §8. |
