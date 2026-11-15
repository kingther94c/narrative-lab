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
  `research/design/feasibility.md`. Run 2026-11-12/13: inference fits whole documents; LoRA on
  Qwen3.5 is limited to short sequences by its Gated DeltaNet layers.
- **EXP-0001** — Sealed zero-shot forecasts on 2026 third-quarter earnings releases. To be
  pre-registered and sealed before 2027-01-10. Primary target: the direction of next quarter's
  guidance. Descriptive target: a hard event within six months; the pre-registration states the
  expected count (at 0.3 to 1.5% a year, 800 companies yield two to twelve bankruptcies). The
  manifest needs a push or an external time stamp.
- **EXP-0002** — SEC EDGAR censuses for the data audit: hard events and earnings releases from
  the bulk submissions archive, and a rule-based guidance census of 400 releases from 50
  companies. An engineering measurement with no hypothesis and no verdict; results in
  `research/design/data_audit.md` §4 and §7. Run 2026-11-13.
- **EXP-0003** — Full count of post-cutoff guidance pairs: every earnings 8-K filed after the
  cutoff (to 2026-11-10) and each company's last one before it, flagged by keyword rules v2 and
  corrected by a 30-item hand check of pre-cutoff releases. An engineering measurement with no
  hypothesis and no verdict; results in `research/design/data_audit.md` §8. Run 2026-11-13.
- **EXP-0004** — Census of company split v1 (`split_v1.py`) on the EXP-0003 universe. It uses
  filing metadata and rule flags only. An engineering measurement with no hypothesis and no
  verdict; results in `research/design/data_audit.md` §8a. Run 2026-11-15.

## Entries

None yet.
