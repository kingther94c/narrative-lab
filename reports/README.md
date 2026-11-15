# Reports

This repository runs a series of studies. Each finished study is reported here, in its own folder,
so that a reader can see what was found and repeat it. The owner set this up on 2026-11-15
(AGENTS.md rule 13).

A study is reported when its verdicts are in, whatever their direction. A refuted hypothesis gets
the same report as a confirmed one.

## One folder per study

```
reports/<study>/
  README.md        findings and how to reproduce them (the template below)
  manifests/       lists of every input by public ID, with SHA-256 hashes; no third-party text
  results/         the numbers behind each table: small CSV or JSON written by the scripts
```

`<study>` is a short slug with the date the report was first published, for example
`2027-02_s1-compression`.

## Template for `README.md`

### 1. Summary

The question, the answer in two or three sentences, and the kind of claim each one is (verified
fact, empirical finding, convention, hypothesis, open question or judgement).

### 2. Findings

One table per result. Every number carries:

- its contamination label (clean, bounded, contaminated or prospective);
- the experiment ID, the commit of its pre-registration and the commit of its verdict;
- an interval, and the unit it was clustered on.

### 3. What it does not show

Scope limits, failed checks, and the slices where the result does not hold.

### 4. Reproduce

Written so that someone with a fresh clone and no access to this machine can follow it.

1. **Hardware it ran on**, and the memory each step needs.
2. **Environment.** The conda command, the pinned requirements file, and Python and library
   versions.
3. **Data.** Commands to fetch every input from its public source, for example SEC EDGAR by
   accession number, with the contact string the source requires set by the reader. The input
   manifest in `manifests/` lets the reader check, by hash, that they fetched the same text.
4. **Models.** Each model's repository and revision hash, or its commercial model ID and the date
   it was called.
5. **Commands, in order**, from fetching through scoring. Each with its expected run time and
   the output it writes.
6. **Checks.** The numbers or hashes a reader should get at each stage, and how much they may
   differ (sampling temperature, hardware).
7. **What cannot be reproduced from the repository alone**, and why: licensed text, or gold test
   labels kept private so that they do not become training data (roadmap decision 8). Say how a
   reader can still verify the result, for example by hash or on request.

### 5. Links

The registry entries, the design documents, and the changelog entries the study relied on.

## Rules

- Nothing licensed, gold or secret goes in here (AGENTS.md rule 12). Inputs are listed by public
  ID and hash, never copied.
- Numbers in a report come from files in `results/` written by a committed script. None are typed
  in by hand.
- A report is not edited after publication except to correct an error. A correction says what
  changed and when, at the top of the report.

No study has been reported yet.
