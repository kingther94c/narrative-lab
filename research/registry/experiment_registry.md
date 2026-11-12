# Experiment registry

Newest first. Every experiment is a script in `research/experiments/`, an entry here, and data that
can be regenerated.

## Entry format

```
## EXP-NNNN — <title> (YYYY-MM-DD)

### PRE-REGISTRATION
- **Status:** not yet run. Committed before the run.
- **Claim under test:**
- **Why the answer is not obvious:**
- **Sample and scope, fixed here before looking:**
- **Method and baseline:**
- **Criteria:** numbered, each with a numeric pass / refute threshold and the random seed.
- **Contamination label of the result:** clean / bounded / contaminated / prospective.
- **Not in scope:**

### VERDICT
- **Pre-registration commit:**
- **Result:**
- **Failure analysis / slices:**
- **Leakage sign-off:**
- **Verdict:** ACCEPT / ACCEPT WITH SCOPE LIMIT / MONITOR / REJECT
```

## Reserved

- **EXP-0000** — Feasibility probes: long-prompt inference and LoRA memory on this machine. An
  engineering measurement, so it has no hypothesis and no verdict; results go to
  `research/design/feasibility.md`.
- **EXP-0001** — Sealed zero-shot forecasts on 2026 third-quarter earnings releases. To be
  pre-registered and sealed before 2027-01-10.

## Entries

None yet.
