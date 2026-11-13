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
