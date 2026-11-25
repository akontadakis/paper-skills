# Study Design

**Load when:** the researcher designs a study of any type: before choosing cases, sample sizes, checks or an analysis. Then load the field guide for each kind of evidence.

**Contents:** Goal · Design Backwards From the Claim · Factors and What Is Held Constant · Choosing Cases · The Unit and What n Counts · Sample Size · Checks Before the Production Run · The Analysis Plan · What Would Change the Conclusion · Threats to Validity · Freeze and Amend · Before and After · Checklist

## Goal

Fix, before the first production run, what will be run, how it will be analysed, and what
result would prove the researcher wrong. The record is `.paper/design.yml`; its fields are in
`study-memory.md`.

This guide holds the steps every study shares. The detail that differs by study type is in one
field guide: `design-simulation.md`, `design-measurement-and-participants.md` or `design-ml.md`.
Load the field guide for each kind of evidence: a surrogate trained on simulated targets needs
two.

Every decision here is the researcher's. For each, give the strongest objection a reviewer
would raise and the real options. A choice you made is written as `proposed, not agreed`.

## Design Backwards From the Claim

Start from the sentence the researcher hopes to write in the Abstract. Work backwards.

| Planned claim | Evidence it needs | Run or measurement | Metric and direction | Figure or table |
| --- | --- | --- | --- | --- |
| View direction changes compliant plan depth more than climate does | the depth under the best- and worst-case view direction, and the range across climates | 24 geometries × 4 climates = 96 runs, 8 view directions in each run | compliant plan depth in m; larger is better | one table |

Rules:

1. Every planned claim has a row. A claim with no row is cut now, not at review.
2. Every planned run serves a row. A run that serves no claim is curiosity. It may be worth
   doing, and it is then labelled exploratory before it is run.
3. The table is written before anything runs. For a conference paper the same table is in
   `experiments.md` of `research-paper-writing`, Plan From the Claims; this is its form for any
   study.

## Factors and What Is Held Constant

1. Name each factor that is varied, and its levels.
2. Name what is held constant, with its value and source. What is held constant bounds the
   conclusion as much as what is varied: a result found at one glazing type is a result for that
   glazing type.
3. Count the runs: the product of the levels, or the sample size of a sampled design. Compare
   the count with the time one run takes.
4. Ask which two factors might interact. If the effect of one could reverse at a level of the
   other, the design must cross them, and the claim is then stated per level.

## Choosing Cases

A case is a building, a climate, a room, a dataset, a site, a participant group.

1. **Give the reason for each case set.** There are three honest reasons: it spans the range of
   the thing that drives the outcome; it contrasts two conditions the question is about; or it
   was what could be obtained. The third is common and legitimate. It is written down as the
   reason, and it limits the claim.
2. **Write the limit now.** The cases sampled are the conditions the claim holds for. Four
   climates in one narrow band of latitude support a claim about that band. They do not
   support a claim about "European climates", and they cannot show that climate matters
   little. Put the limit in `bounded_to`; the claim in `claims.yml` starts from it.
3. **Add a contrast case.** Ask which case is most likely to reverse the result, and include
   it, or record that none is included. A set of similar cases agrees with itself.
4. **Do not write a justification the researcher did not give.** "Representative of" needs a
   source: a stock survey, a standard, a classification. Without one it is a bracket.

## The Unit and What n Counts

1. Name the unit that is analysed: the sensor point, the hour, the room, the participant.
2. Name the unit that is independent. Hours of one room are not independent, nor are points of
   one grid, nor plans from one building.
3. Any n in the paper counts independent units. Decide it here; the reporting rule is in
   `statistics-reporting.md` of `research-paper-writing`, What n Counts.

## Sample Size

There are four honest bases. Record which one in `sample_size.basis`.

1. **Power.** Start from the smallest effect of interest: the smallest difference that would
   change a design decision or matter to an occupant. It comes from the researcher, with its
   source. Then n follows. An effect size taken from a "medium" label, or supplied by you, is
   not a source. If the researcher has none, the slot is a bracket, and the reply shows how n
   depends on it.
2. **Feasibility.** The n that can be afforded is fixed first. Then state the smallest effect
   that n can detect, computed from n, the design, the significance level and the power, never
   from the observed effect.
3. **Precision.** Start from the widest interval that still answers the question, with its
   source. Then n follows.
4. **Full enumeration.** Every case in a defined set is run. No sampling, so no power. A
   deterministic simulation of a fixed set is this case.

A number given without its basis will be asked for again by an ethics board, a reviewer, or
both.

## Checks Before the Production Run

Each check is listed in `pre_run_checks` with its `status`: `done`, `not done`, `not planned` or
`not possible`, and the detail in `note`. A check that is skipped is written as skipped, and
becomes a threat.

1. **A pilot** on the smallest case and on the hardest case. It gives the run time and finds the
   failures that would otherwise appear in week three.
2. **Convergence** of every numerical setting the outcome is sensitive to. The field guide says
   which.
3. **Validation**: what the model or the instrument will be checked against, and the margin of
   agreement that will count as acceptable. The margin is written before the comparison.
4. **Noise**: how much the result changes when nothing but the random seed or the day changes.
   A difference smaller than that is not a result.

## The Analysis Plan

Write it as it will appear in Methods.

1. The outcome, defined exactly: quantity, threshold, plane or position, hours.
2. The summary statistic, and over which units.
3. The comparison, and whether a test or an interval will be used. If runs are deterministic
   and the cases are not a sample of a population, say that no test is planned.
4. What happens to failed, missing and excluded runs. The rule is fixed now. They are counted
   and reported; they are never dropped silently.
5. Which analyses are planned and which are exploratory.
6. For a study with participants or measurements: the primary and the secondary outcomes, the
   exclusion rules and the stopping rule, in `primary_outcome`, `secondary_outcomes`,
   `exclusion_rules` and `stopping_rule`.
7. When the plan holds more than one test, fix the family of tests and the correction now, and
   record both in `analysis`. See `statistics-reporting.md` of `research-paper-writing`,
   Multiple Comparisons.

Offer the researcher options for each. A test, a model or a sensitivity range that you chose is
`proposed, not agreed`.

## What Would Change the Conclusion

For each planned claim, write two things.

1. **The refuting result.** The outcome that would make the claim false: "the reduction from
   best to worst view direction is smaller than the spread across climates".
2. **The no-difference margin.** The size below which a difference is treated as none, with its
   reason: the resolution of the grid, the noise from the seed, the uncertainty of the
   instrument, or the smallest effect of interest.

A planned claim with no refuting result describes a study that cannot fail, and a study that
cannot fail teaches little. If the researcher cannot name one, the claim is too vague, or the
design does not test it.

This is written before the runs. Written afterwards, it is a description of what happened.

## Threats to Validity

List what could make the result wrong or narrow. For each, one decision.

| Decision | Meaning |
|---|---|
| `remove` | change the design so the threat is gone |
| `reduce` | add a check, a case or a sensitivity run |
| `accept` | leave it, and record its consequence |

An accepted threat is not a failure. It becomes a sentence of the Limitations paragraph, in the
same words, with its direction and rough size where they are known. A threat found by a
reviewer costs a revision; the same threat written here costs a line.

## Freeze and Amend

1. When the researcher agrees the design, write `frozen_on` with the date. The freeze comes
   on or before the date of the first production run.
2. After the freeze, every change is an amendment: what changed, why, the date, and the
   `timing`. `changed before analysis` means no result had been seen. `post hoc` means one had.
   An amendment dated after the first production run is `post hoc`, unless it records
   `results_seen: false` with the reason in a `reason` field (`why` does not count): for
   example, data were collected and not yet opened.
3. Never edit the frozen entries to match a later choice. Never write that a choice was planned
   unless the dated record shows it.
4. A `post hoc` choice is legitimate. It is reported as made after the results, the analysis
   under the original choice is reported beside it, and the claim it supports is labelled
   exploratory. Record it with `kind: choice`, and the result under the original choice in
   `old_result`.
5. A `post hoc` correction is different. A check exposed a fault, such as a grid that had not
   converged, and the fix did not depend on which result was preferred. Record it with
   `kind: correction`, the check that forced it, and the result under the old setting. The
   claim keeps its status. A change that could have gone either way is a choice.

If results already exist and there is no dated plan, say so plainly. The design file can still
be written, as a description. Its choices are then `post hoc`, and nothing in it is called
planned.

## Before and After

The example is invented. It is not the journal study of `study-memory.md`.

**What the researcher said**

> I will use four climates. I already have those weather files. Write the Cases paragraph so I
> can start the runs tonight.

**A record that hides the problem**

> Four climates were selected to represent a range of European conditions.

"Selected to represent" is a reason the researcher never gave.

**A record that helps**

```yaml
cases:
  - set: "climates"
    members: "[insert the four climate names and their weather files]"
    reason: "the weather files were at hand"
    bounded_to: "[insert the latitude band and the sky conditions the four cover]"
    contrast_case: "none included"
```

> Strongest objection: the four may be alike in the one thing that drives daylight, so the
> study could not show a climate effect even if one exists. A reviewer will then reject any
> claim that climate matters little. Options: add one climate chosen to differ most, which costs one more set of
> runs; or keep the four and bound the claim to their band, which costs nothing and narrows the
> paper.

## Checklist

1. Does each planned claim have its evidence, its run and its metric, written before any run?
2. Is each varied factor named with its levels, and each constant with its value?
3. Does each case set have a reason, a limit on the claim and a contrast case?
4. Is the independent unit named?
5. Does the sample size state its basis, and does any effect size have a source?
6. Is each pre-run check listed with its status?
7. Is the analysis plan written as Methods will state it, with the rule for failed runs?
8. Does each planned claim say what result would refute it, and the no-difference margin?
9. Does each threat have one decision?
10. Is the design frozen with a date before the first production run?
11. Is each choice you made for the researcher marked `proposed, not agreed`?
