# Labelling codebook

**Draft v1, 2026-11-13.** Work package 4 of Phase 0; the plan is in
[`../registry/01_roadmap.md`](../registry/01_roadmap.md). This draft has not been tried on real
documents: no SEC EDGAR pull has been made yet. Every example below is constructed for
illustration and is not taken from a filing. The owner reviews this draft before round 1; the
points that need a decision are collected in section 11.

No model on the evaluation roster labels or pre-labels test items. A rule-based parser may propose
tuples. Label files are kept outside git.

## 1. What is being labelled

**Guidance** is a statement by a company about its own expected results for a stated period that
has not yet been reported.

In scope: revenue, earnings per share, operating income, operating margin, gross margin, EBITDA,
net income, capital expenditure, free cash flow.

Out of scope in v1:

- targets with no period ("over the medium term", "our long-term model");
- statements about the industry or the economy;
- analyst estimates the company quotes;
- capital return plans (buybacks, dividends), tax rate and share count;
- anything said only on the earnings call and not in the text.

**An item** is a pair of outlook passages from one company's consecutive documents. P0 is the
earlier and P1 the later. A document is an earnings press release (8-K Item 2.02, Exhibit 99.1) or
a pre-announcement between two of them. The outlook passage is the part of the document that
states guidance; if a document states none, its passage is empty and the item is still kept.

## 2. The guidance tuple

One tuple per metric and period, per passage.

| Field | Values | Notes |
|---|---|---|
| `metric` | `revenue`, `eps`, `operating_income`, `operating_margin`, `gross_margin`, `ebitda`, `net_income`, `capex`, `free_cash_flow`, `other` | `other` is recorded but not scored |
| `metric_text` | verbatim | The company's own name for the metric |
| `period_type` | `fiscal_year`, `fiscal_quarter`, `half_year`, `other` | |
| `period_label` | as stated, for example `FY2026`, `Q4 FY2026` | Use the company's fiscal calendar |
| `basis` | `gaap`, `non_gaap`, `constant_currency`, `organic`, `unspecified` | Plus `basis_text`, verbatim |
| `form` | `point`, `range`, `floor`, `ceiling`, `qualitative` | "at least" is a floor; "up to" is a ceiling |
| `approx` | true / false | "approximately", "about", "roughly" |
| `low`, `high` | numbers or null | Point: both equal. Floor: `low` only. Ceiling: `high` only. Qualitative: both null |
| `unit` | `usd`, `usd_per_share`, `percent`, `percent_growth`, `bps`, `other` | |
| `scale` | `units`, `thousands`, `millions`, `billions` | |
| `position_in_range` | `none`, `low_end`, `midpoint`, `high_end` | Where the company says it expects to land |
| `qualitative_text` | verbatim or null | For qualitative guidance and for modifiers such as "toward the low end" |
| `conditions` | verbatim or null | Stated assumptions and exclusions |
| `evidence` | verbatim quote with character offsets | The shortest span that justifies the tuple |

Rules for filling it in:

- Record what the text says, not what it implies. Do not compute a figure the company did not
  state.
- A growth rate and an absolute amount for the same metric are two tuples with different units.
- If the company restates its earlier guidance on a new basis in P1, record that restatement as
  a P0 tuple with `restated_in_p1 = true`, and use it for the comparison.

## 3. Matching tuples across the pair

A P0 tuple and a P1 tuple match when `metric`, `period_label`, `basis` and `unit` are the same.
Everything else is unmatched.

## 4. The revision label

One label per metric and period. It has a state, and for matched tuples two attributes.

### State

| State | When |
|---|---|
| `continued` | The tuple is matched. Direction and width apply |
| `initiated` | In P1 only, and P0 gave no guidance for that metric and period |
| `withdrawn_announced` | In P0 only, and P1 says the guidance is withdrawn or suspended. Set `temporary = true` if the text says so |
| `no_longer_mentioned` | In P0 only, P1 is silent about it, and the period has not ended |
| `period_completed` | In P0 only, and P1 reports actual results for that period. Not a revision |
| `none_stated` | Item-level: neither passage gives guidance in scope |

`period_completed` is bookkeeping added in this draft so that year-end is not read as a silent
drop.

### Direction

`raised`, `maintained`, `lowered` or `indeterminate`.

For numeric tuples, compare a reference value:

| Form | Reference value |
|---|---|
| Point | The value |
| Range | The midpoint |
| Floor | `low` |
| Ceiling | `high` |

- Same form in P0 and P1: `raised` if the reference value is higher, `lowered` if lower,
  `maintained` if the change is within tolerance.
- Range in P0, point in P1: `raised` if the point is above the old `high`, `lowered` if below the
  old `low`, otherwise `maintained`.
- Point in P0, range in P1: `raised` if the point is below the new `low`, `lowered` if above the
  new `high`, otherwise `maintained`.
- Floor or ceiling against a range or point: `indeterminate` unless the new guidance lies wholly
  outside the old.
- Tolerance (suggested): a relative change of less than 0.5% in the reference value, or a
  difference only in the last reported digit, is `maintained`.

When the numbers are unchanged but the wording moves the expectation, the wording decides:

- P1 says results are expected toward the low end, below the midpoint, or "at the lower half" of an
  unchanged range, and P0 did not: `lowered`.
- The mirror case: `raised`.
- Record `label_basis = wording`. Otherwise `label_basis = numbers`.

For qualitative guidance with no numbers in either passage:

- Use explicit comparative language only: "now expect", "lower than previously anticipated",
  "continue to expect", "reaffirm".
- If there is none, the direction is `indeterminate`. Do not infer direction from tone.

### Width

`narrowed`, `unchanged`, `widened` or `not_applicable`.

- Range to range: compare `high - low`, with the same tolerance.
- Range to point: `narrowed`. Point to range: `widened`.
- Anything else: `not_applicable`.

### Flags

| Flag | When |
|---|---|
| `label_basis` | `numbers` or `wording`, as above |
| `stated_reason` | `operations`, `m_and_a`, `fx`, `tax`, `accounting`, `other`, `none_stated`, plus the verbatim reason. L2 uses it; L1 scoring does not |
| `cadence_change` | The company moves between quarterly and annual guidance |
| `basis_changed` | The metric's definition or basis differs between P0 and P1 with no restatement |
| `wording_number_conflict` | The wording says one thing and the numbers another |
| `temporary` | A withdrawal described as temporary |

## 5. Rules for the hard cases

1. **Numbers beat wording.** "We reaffirm" with different numbers is labelled by the numbers, with
   `wording_number_conflict = true`.
2. **A new fiscal year is not a revision.** Guidance for FY2027 in P1 after FY2026 guidance in P0
   is `initiated` for FY2027; FY2026 is `period_completed` if P1 reports it.
3. **Cadence change.** Quarterly guidance in P0 and only annual in P1: the quarterly tuple is
   `withdrawn_announced` if the company says it will no longer guide quarterly, otherwise
   `no_longer_mentioned`; the annual tuple is `initiated`. Both carry `cadence_change = true`.
4. **Temporary suspension.** `withdrawn_announced` with `temporary = true`. If a later document
   brings the guidance back, that item's label is `initiated`.
5. **Changed basis.** No match, so the P0 tuple is `no_longer_mentioned` and the P1 tuple
   `initiated`, both with `basis_changed = true`, unless P1 restates the earlier figure.
6. **Stock split.** If P1 restates earlier EPS guidance on the new share count, compare with the
   restatement. If not, direction is `indeterminate`.
7. **Acquisitions, disposals, currency, accounting changes.** Label by the numbers and record the
   reason in `stated_reason`. Whether the change reflects the business is an L2 question.
8. **A range that shifts and narrows.** Direction from the midpoint, width from the width. Both
   are recorded; neither overrides the other.
9. **Narrowing to one end.** A range of 2.00 to 2.20 becoming 2.10 to 2.20 is `raised` and
   `narrowed`. Becoming 2.00 to 2.10 it is `lowered` and `narrowed`.
10. **"At least" becoming a range**, or the reverse: `indeterminate`, unless the new guidance lies
    wholly above or below the old.
11. **Several statements about one metric in one passage.** Use the most specific statement for
    the stated period; quote it in `evidence`.
12. **Guidance repeated from an earlier document inside P1** ("as previously announced on ...").
    Record it as P1's guidance. It is not a second revision.
13. **Pre-announcements.** They are documents like any other. A pre-announcement that only reports
    preliminary results for a finished period carries no guidance tuple for that period.
14. **Nothing in scope in either passage.** One item-level label, `none_stated`.

## 6. How the label is computed

The annotator enters tuples and flags. A script then:

1. matches tuples (section 3);
2. assigns the state to every metric and period;
3. computes direction and width for matched numeric tuples with `label_basis = numbers`;
4. leaves direction for the annotator wherever `label_basis = wording` or the guidance is
   qualitative.

The annotator checks every computed label and may override it with a written reason. Overrides are
counted and reported: rule-against-human agreement is the share of computed labels left unchanged.

## 7. Constructed examples

These are invented to show the rules. They are not quotations.

| P0 | P1 | Label |
|---|---|---|
| "We expect fiscal 2026 revenue of $4.00 billion to $4.20 billion." | "We now expect fiscal 2026 revenue of $4.15 billion to $4.25 billion." | `continued`; direction `raised` (midpoint 4.10 to 4.20); width `narrowed`; basis `numbers` |
| "We expect fiscal 2026 EPS of $2.00 to $2.20." | "We continue to expect fiscal 2026 EPS of $2.00 to $2.20 and now anticipate results toward the low end of the range." | `continued`; direction `lowered`; width `unchanged`; basis `wording` |
| "Fiscal 2026 revenue of $4.00 to $4.20 billion and operating margin of about 15%." | "Fiscal 2026 revenue of $4.00 to $4.20 billion." | Revenue: `continued`, `maintained`, `unchanged`. Operating margin: `no_longer_mentioned` |
| "We expect third-quarter revenue of $900 to $950 million." | "Given limited visibility, we are suspending quarterly guidance until conditions stabilise." | `withdrawn_announced`, `temporary = true` |
| "We expect fiscal 2026 EPS of $2.00 to $2.20." | "Fiscal 2026 EPS was $2.14. For fiscal 2027 we expect EPS of $2.30 to $2.50." | FY2026: `period_completed`. FY2027: `initiated` |
| "We remain confident in our outlook for the year." | "We remain cautious given the demand environment." | `none_stated`: no metric and period in scope. Direction is not inferred from tone |

## 8. Minimal pairs

Each minimal pair starts from a real item and edits P1 only.

| Edit | What changes | Label |
|---|---|---|
| Number edit | Only the figures | Recomputed by rule from the edited figures |
| Substantive wording edit | Only words that move the expectation, such as adding "toward the low end" | Changes, with `label_basis = wording` |
| Paraphrase | Wording only, meaning kept | Unchanged |
| Control | Nothing | Unchanged |

- Systems see the original item and the edited item separately, never side by side. Consistency is
  scored afterwards.
- Controls give the false-positive rate: how often a system reports a change where there is none.
- Each edit passes two checks before it is kept: the passage still reads as a plausible release,
  and the label by construction is the label a reader would give. Expect to lose about a fifth of
  wording edits here.
- Edits are written by the owner or by a model that is not on the evaluation roster.

## 9. The pilot

- 100 items, sampled across three strata: numeric against qualitative guidance; whether the
  company updates every quarter or only occasionally; company size.
- Two rounds, 14 days apart. Round 2 uses a different order and is done without sight of round 1.
- Agreement between rounds, per attribute:
  - tuples: matched on `metric`, `period_label`, `basis` and `unit`, values within 1%; report
    precision, recall and F1 of round 2 against round 1;
  - state, direction and width: raw agreement, Cohen's kappa with a bootstrap interval, and
    Gwet's AC1. One class will dominate, which depresses kappa, so all three are reported.
- Gate, to be fixed before round 1. Suggested: the lower bound of the 95% interval for kappa is at
  least 0.7 for state and for direction, and rule-against-human agreement is at least 90%.
- If the gate is missed, the codebook is revised and the pilot repeated on fresh items.

## 10. Adjudication of unmatched extractions

Single-annotator gold misses things. After systems have run on the pilot items, a random sample of
50 tuples that a system produced and gold lacks is shown to the annotator, who marks each as valid
guidance or not. The share found valid estimates what gold is missing and is reported with every
recall figure.

## 11. Decisions for the owner before round 1

1. **Within-range shifts.** This draft labels "toward the low end of an unchanged range" as
   `lowered` with `label_basis = wording`. The alternative keeps direction `maintained` and records
   the shift as a separate attribute.
2. **Tolerance.** 0.5% of the reference value, or the last reported digit.
3. **Metric list.** Whether tax rate, share count and capital return belong in scope.
4. **`period_completed` and `indeterminate`.** Both are additions to the plan's label set.
5. **The gate.** The thresholds in section 9.
6. **Who writes minimal-pair edits.** The owner, or a model outside the roster.

## 12. Files

One JSON object per item, in JSON Lines, on the external drive under
`DATA/narrative_lab/gold/pilot/round1.jsonl` and `round2.jsonl`. Each object holds the item id,
the two document accession numbers and acceptance timestamps, the passages, the tuples for P0 and
P1, the labels, the flags, the annotator's overrides with reasons, and the time spent. Nothing
under `gold/` is committed.
