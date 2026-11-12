# Experiments

One script per experiment, named `expNNNN_<slug>.py`, with a matching entry in
[`../registry/experiment_registry.md`](../registry/experiment_registry.md).

- A script is frozen once it has been run for the record. Fix forward in a new numbered script.
- Outputs go to the external drive, not here.
- Anything a script establishes that later code relies on is lifted into the package with a
  citation back to the experiment.

| Script | Experiment | What it established |
|---|---|---|
