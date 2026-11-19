# Designing a Measurement Campaign or a Study With Participants

**Load when:** the results will come from instruments in a real space, or from people: ratings, votes, task performance, surveys, wearable sensors. Load after `study-design.md`.

**Contents:** Goal · Part 1: Measurement Campaigns · Part 2: Studies With Participants · How n Depends on the Effect · Decisions to Fix Before the First Session · Checklist

## Goal

Plan what cannot be repeated. A simulation can be rerun; a week of measurements in March, or a
session with a participant, cannot. `study-design.md` holds the general steps. The reporting
side is in `research-paper-writing`: `ethics-and-participants.md` and
`statistics-reporting.md`.

## Part 1: Measurement Campaigns

### The quantity and the instrument

1. Name the quantity and its unit, and the instrument that measures it.
2. Record the instrument's stated accuracy, its last calibration date, and what the calibration
   is traceable to. A calibration that has expired is recorded as expired.
3. Check that the instrument measures the quantity the claim is about. An illuminance meter
   reports photopic illuminance. A melanopic quantity needs a spectral measurement, or a
   stated conversion with its assumed spectrum.

### The uncertainty budget, before measuring

1. List each source: the instrument's accuracy, its cosine and spectral response, temperature,
   the logger's resolution, the placement and levelling of the sensor.
2. Estimate each, and combine them by the method of the Guide to the Expression of Uncertainty
   in Measurement (JCGM 100).
3. Compare the uncertainty of the difference with the difference the study hopes to show.
   Errors common to both readings cancel in a paired difference; the rest do not. If the
   uncertainty of the difference is the larger, the campaign cannot show the effect. Change
   the instrument, the design or the claim now.

### When, how long, how often

1. **Sampling interval.** Choose it from how fast the quantity changes. Daylight under broken
   cloud changes within seconds; a ten-minute spot reading misses that.
2. **Duration and season.** A week in June says nothing about December. State which seasons
   and sky conditions the campaign covers, and bound the claim to them.
3. **A reference measurement** taken at the same time, outside or unobstructed, so that an
   indoor change can be told apart from a change of the sky.

### Placement and the log

1. Record where each sensor is, at what height, facing where, and what it stands for: a desk,
   an eye position, a surface.
2. Keep a log of events that change the reading: blinds moved, lights switched, people present,
   windows cleaned, furniture moved.
3. Fix the rule for missing and faulty data before the campaign: what counts as a fault, and
   whether a gap is left, filled or excluded.
4. Run one pilot day. Download and plot the data before the campaign continues.

## Part 2: Studies With Participants

### Before anything else

1. **Ethics approval comes before any data**, including any pilot session with participants;
   ask the board. Record the board, the reference and the date in the `ethics` block of
   `design.yml` when they exist; until then the slot is a bracket.
2. Decide what personal data is collected, where it is stored, and when it is deleted.
3. Consider registering the hypotheses and the analysis plan before data collection. A date
   typed into `design.yml` cannot be checked. At the freeze, commit the file and record the
   commit id in `frozen_commit` of `design.yml`, or record a registry entry. If the study was not preregistered, no analysis is
   called confirmatory: see `ethics-and-participants.md` in `research-paper-writing`.

### The design

1. **Within or between.** In a within-participant design each person sees every condition. It
   needs fewer people, and it needs a plan for order.
2. **Order.** Balance the order of conditions across participants, and record how the order was
   assigned.
3. **Carry-over.** State the time allowed between conditions, and its reason. Visual
   adaptation is the usual one in a lighting study.
4. **What is held constant**: time of day, task, position, view, prior exposure.
5. **The outcome and its scale.** A rating on a four-point scale is ordinal. Decide now how it
   will be analysed.
6. **Exclusion criteria**, fixed before recruitment: who cannot take part, and which sessions
   will be discarded.

### The sample

1. State the basis: `power`, `precision` or `feasibility`. See `study-design.md`, Sample Size.
2. For `power`, the smallest effect of interest comes from the researcher: the smallest
   difference in the outcome that would change a design decision or matter to an occupant, and
   where that value comes from. A "medium effect" is not a source.
3. For `feasibility`, state the n that can be recruited, and the smallest effect it can detect.
   For `precision`, state the widest interval that still answers the question, and its source.
4. Plan for dropout: recruit more than the analysed n, and report both numbers later.
5. Describe who will be recruited. The sample bounds the claim: age range, vision, familiarity
   with the task.

## How n Depends on the Effect

When the researcher asks for a number and has no effect size, do not choose one for them. Show
how the number depends on it, and leave the slot open.

For a two-sided comparison of two conditions in the same participants, at a significance level
of 0.05 and a power of 0.80, a normal approximation gives

    n ≈ 8 / d² + 2

where d is the mean of the paired differences divided by their standard deviation.

| Smallest effect of interest, d | Participants, about |
|---|---|
| 0.3 | 90 |
| 0.5 | 34 |
| 0.8 | 15 |

Rules:

1. The table shows the dependence. It does not supply the effect. The row is chosen by the
   researcher's smallest effect of interest, with its source.
2. The approximation is for planning. Confirm the final number with a power tool, for the test
   that will be used.
3. An ordinal outcome analysed with a rank test needs a few more participants than the table
   gives.
4. The sentence for an ethics form states the basis. With a sourced effect: the effect, its
   source, the level, the power, the n. Without one: `[insert the smallest effect of interest
   and its source]`, or the feasibility wording with the detectable effect.

## Decisions to Fix Before the First Session

Each goes in `design.yml`, under `analysis`.

1. The primary outcome, and which outcomes are secondary: `primary_outcome` and
   `secondary_outcomes`.
2. The test or model, and the level.
3. The exclusion rules: `exclusion_rules`.
4. The stopping rule, in `stopping_rule`: the n at which recruitment stops. Stopping when the
   result looks good is a `post hoc` choice.
5. What result would change the conclusion, and the no-difference margin.

## Checklist

1. Does the instrument measure the quantity the claim is about, and is its calibration current?
2. Is the combined uncertainty smaller than the difference the study hopes to show?
3. Do the sampling interval, the duration and the seasons fit the claim?
4. Is there a reference measurement and an event log?
5. Is the rule for missing data fixed in advance?
6. Is ethics approval in hand before any data, or bracketed as pending?
7. Are order, carry-over and exclusion rules fixed?
8. Does the sample size state its basis, with a sourced effect or a detectable effect?
9. Is the stopping rule fixed?
