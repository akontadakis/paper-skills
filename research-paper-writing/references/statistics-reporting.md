# Statistics and Numerical Reporting

**Load when:** the paper reports an inferential statistic, a model-agreement metric, a predictive score or a measurement uncertainty.

**Contents:** Goal · Scope · The Reporting Triad · P-Values · Effect Size · Sample Size and Power · What n Counts · Multiple Comparisons · Non-Significant and Null Results · Model Agreement and Calibration · Predictive Performance · Measured Quantities and Uncertainty · Precision, Rounding, and Units · Correlation and Causation · What Goes in the Claim Ledger · Common Faults · Checklist

## Goal

Report a number so a reader can judge how much to believe it, and recompute it if they
disagree.

## Scope

Load this when the paper reports any inferential statistic, any model-agreement metric, any
predictive-performance score, or the measurement uncertainty of an instrument or a method.
Do not load it for a paper that only reports descriptive summaries — a mean with its
standard deviation is one — because `results.md` and `sentence-craft.md` already cover
those. The presence of a `±` does not load this file; a study whose argument rests on how
well something was measured does.

This file governs *what accompanies a number*. `results.md` governs where the number sits in
the section, `sentence-craft.md` governs the verb attached to it, and `paper-review.md`
dimension "numerical treatment" tests the result.

## The Reporting Triad

Every inferential result carries three things. Two of the three is an incomplete result.

1. **The estimate** — the effect itself, in the units of the outcome.
2. **The uncertainty** — a confidence interval, a standard error, or a credible interval.
3. **The test statistic and its reference** — the statistic, its degrees of freedom, and the
   p-value.

For a Bayesian analysis the triad is: the posterior estimate; the credible interval with its
level; and, in place of item 3, the model and the prior, with where the prior came from, plus a
Bayes factor if one is reported. Name the software and, for a sampled posterior, its convergence check.

A bare p-value is not a result. It states only that an effect is distinguishable from zero,
not how large it is or how precisely it was measured.

The examples in this guide are invented.

| Written | Verdict |
|---|---|
| `mel-EDI differed between orientations (p < 0.05)` | Incomplete. No estimate, no uncertainty. |
| `mel-EDI was 84 lx higher facing north (p = 0.023)` | Incomplete. No uncertainty. |
| `mel-EDI was 84 lx higher facing north (95% CI 12 to 156, t(38) = 2.36, p = 0.023)` | Complete. |

## P-Values

1. Report the exact value to two or three significant figures: `p = 0.032`, not `p < 0.05`.
2. Use `p < 0.001` only below that floor. Never write `p = 0.000`.
3. Never write `p = n.s.`. Report the value.
4. State the alpha level once, in Methods, and do not restate it per test.
5. `p > 0.05` means the data did not distinguish the effect from zero. It does not mean the
   effect is zero, and it never supports "no difference" or "equivalent". For an equivalence
   claim, run an equivalence test and state its bound. The bound is fixed before the data are
   seen — see Model Agreement and Calibration, rule 9.
6. A p-value near the threshold is not "approaching significance", "trending", or "marginally
   significant". Report the value and the interval and let them speak.

## Effect Size

1. Report an effect size for every inferential comparison.
2. Prefer the raw effect in physical units. `84 lx` tells a lighting reader more than
   `d = 0.62`.
3. Report a standardised measure in addition when comparing across outcomes with different
   units, or when the field expects it: Cohen's *d*, Hedges' *g*, partial eta-squared, odds
   ratio, R².
4. State which standardised measure it is and how it was computed. Several definitions of
   partial eta-squared and of Cohen's *d* are in circulation.
5. Never interpret a standardised effect size against generic small/medium/large labels
   without saying whose labels they are. Interpret against what matters in the application:
   a 5% change in annual sDA and a 5% change in classification accuracy are not comparable
   quantities.

## Sample Size and Power

1. State how the sample size was decided, in Methods, before any result.
2. If a power analysis was run, state the target effect, the alpha, the power, and the
   resulting *n*.
3. If the sample size was set by feasibility — participants available, buildings accessible,
   compute budget — say so plainly. An honest feasibility sample is defensible; a power
   analysis reverse-engineered from the observed effect is not.
4. Never compute post-hoc power from the observed effect. It is a restatement of the p-value
   and reviewers in several fields will flag it.
5. Report the analysed *n* separately from the recruited *n*, with the attrition between them
   accounted for.
6. Justify the target effect as the smallest effect of interest — the smallest difference
   that would change a design decision or matter to an occupant — and say where that value
   comes from. An effect size borrowed from a pilot or from a generic "medium" label is not a
   justification.
7. When the sample was set by feasibility, report what it could detect: the smallest effect
   the achieved *n* resolves at the stated alpha and power. This is the honest replacement for
   post-hoc power. It is computed from *n* and the design, never from the observed effect.

## What n Counts

A sample size means nothing until the reader knows what was sampled independently.

1. Name the independent unit behind every interval and every p-value: the participant, the
   room, the building, the day, the simulation run. That unit, not the number of rows in the
   data file, sets the degrees of freedom.
2. Repeated values from one unit are not independent. These are the cases a reviewer in this
   field looks for:
   - 8,760 hourly values from one room for one year are one room, not 8,760 samples.
     Consecutive hours are strongly autocorrelated.
   - 400 points on one sensor grid are one room under one sky, not 400 samples. Neighbouring
     points share most of their daylight.
   - Twelve rooms in one building share its orientation, glazing, and controls.
   - Thirty glare votes from five participants are five participants.
3. State how the analysis handled the dependence: aggregation to the independent unit, a
   mixed model with the unit as a random effect, a blocked or clustered resampling scheme.
   "Independent samples" asserted for nested data is a fault, however small the p-value.
4. Where there is one unit — one room, one building, one simulated case — say so, report the
   difference descriptively, and drop the test. A p-value computed across the hours of a
   single case measures how many hours there were.
5. A caption's `n` names its unit too. `n = 8,760 h, one room` and `n = 12 rooms` are both
   complete; `n = 8,760` is not. See `figures-tables.md`, Self-Containment.

## Multiple Comparisons

1. State how many tests were run against each hypothesis family, including the ones that were
   not reported.
2. Name the correction and the family it was applied over: Bonferroni, Holm, Benjamini-Hochberg
   with its q. A correction applied to an unnamed family is not checkable.
3. If no correction was applied, say so and label the affected results exploratory.
4. A result that only survives uncorrected is described as exploratory in Results and does not
   appear as a claim in the Abstract.
5. Sweeping a parameter and reporting the best-performing setting is a multiplicity problem
   even when no test was run. Report the sweep, not only its maximum.

## Non-Significant and Null Results

1. Report them with the same triad as significant ones. A wide interval around zero and a
   narrow one around zero are different findings.
2. State which of the two you have: the effect is small, or the study could not resolve it.
   The confidence interval decides this, not the p-value.
3. Do not drop a pre-registered or Methods-declared outcome because it came out null. That is
   the multiplicity problem in reverse.

## Model Agreement and Calibration

For a simulation or model validated against measurement.

1. Report the error metric with its denominator and its sign convention. `RMSE`, `MBE`,
   `NMBE`, `CV(RMSE)`, `MAPE`, and `MAE` are not interchangeable, and normalised forms differ
   in what they normalise by.
2. Report both a bias metric and a scatter metric. Bias alone hides scatter; scatter alone
   hides a systematic offset.
3. State the aggregation interval. Hourly and monthly agreement are different claims, and
   monthly agreement is much easier to reach.
4. State the number of paired points and the period they cover.
5. If a published calibration criterion is being invoked — for example the hourly and monthly
   NMBE and CV(RMSE) bands in ASHRAE Guideline 14, or the equivalents in IPMVP — cite the
   document and its edition, and quote the threshold you used. Editions differ. Do not state a
   band from memory.
6. Do not report R² as evidence of agreement between a model and a measurement. This rule is
   about the squared correlation coefficient. It measures correlation, and a model with a constant offset can reach R² near 1 while being wrong
   everywhere. Report bias explicitly. A coefficient of determination computed as 1 − SS_res/SS_tot against
   the 1:1 line does penalise offset, but still report bias and the error metrics beside it.
7. State which parts of the model the validation does *not* cover. See `methods-journal.md`,
   Validation.
8. When two methods are compared — a simulation against a measurement, one sensor against
   another, one engine against another — report the mean difference and the limits of
   agreement, the interval that holds about 95% of the paired differences. State how the
   limits were computed. Say whether the difference grows with the magnitude; where it does,
   one bias figure for the whole range misleads, and the agreement is reported by range or on
   a relative scale.
9. State the acceptance margin before the comparison, and say where it comes from: a
   standard, an instrument class, the smallest difference that matters in use. A margin chosen
   after seeing the data is not an acceptance criterion, and "agreement was good" with no
   margin is not a result. Record the margin and its source in Methods.

## Predictive Performance

For a model whose claim is out-of-sample performance.

1. Report the split: train, validation, and test, with sizes and how the split was made.
2. A number computed on data used for fitting, tuning, or model selection is a fit statistic,
   not a performance estimate. Label it as such.
3. Report variability across seeds or folds, not a single run. Give the mean and the spread,
   and state how many runs.
4. State the baseline the score is compared against, and give the trivial baseline — majority
   class, persistence, climatological mean — so the reader can see the floor.
5. Match the metric to the class balance. Accuracy on an imbalanced problem is not
   informative; report per-class scores, or a balanced measure, and say which.
6. A difference between two models needs the same triad as any other comparison. Two point
   scores with no spread is not evidence of a difference.
7. Fit every preprocessing step — scaling, imputation, feature selection, resampling — inside
   each training fold, and say that this was done. A scaler fitted on the full dataset has
   seen the test set.
8. Block the split by the unit that makes samples alike. Hourly values split at random put
   10:00 in training and 11:00 in test; neighbouring grid points and rooms of one building
   leak the same way. Split by day, week, room, or building, state which, and report the
   random-split score only as a labelled upper bound. See What n Counts.

## Measured Quantities and Uncertainty

A `±` with no stated meaning is ambiguous. The reader cannot tell a standard deviation from a
standard error, a 68% interval from a 95% one, or an instrument tolerance from a spread across
rooms.

1. Say what follows the `±` once in Methods, and again in each table or figure caption that
   shows a `±` value, because captions are read alone: a standard deviation, a standard error, a confidence interval and its level,
   a standard measurement uncertainty, or an expanded uncertainty.
2. For an expanded uncertainty, give the coverage factor and the coverage level:
   `U = 14 lx (k = 2, about 95%)`. This is the convention of the *Guide to the Expression of
   Uncertainty in Measurement* (JCGM 100:2008).
3. Round the uncertainty first, to one or two significant digits, then round the value to
   the same decimal place. `412.37 ± 18.2 lx` becomes `412 ± 18 lx`. Never round the two
   independently, and keep a trailing zero that is significant: `0.10`, not `0.1`.
4. Say whether an uncertainty is absolute or relative. `± 3 lx` and `± 3%` are different
   statements, and an instrument accuracy quoted as "3% of reading ± 1 digit" is neither
   alone.
5. State the instrument uncertainty with its source: the class or the calibration
   certificate, and the date of the last calibration. A manufacturer's nominal accuracy is
   not the uncertainty of the reported mean, which also carries placement, repeatability,
   and sampling.
6. A value below the detection limit or the instrument range is reported as such. Do not
   substitute zero or half the limit without saying so.
7. A temperature difference or a temperature uncertainty is in K or in °C; the two are
   numerically equal. Use one in a paper: `ΔT = 2.5 K`, `± 0.3 K`.

## Precision, Rounding, and Units

1. Give a number no more digits than the measurement or the model supports. Simulation output
   with six decimals is false precision.
2. Round the estimate and its interval to the same precision. The uncertainty sets that
   precision — see Measured Quantities and Uncertainty, rule 3.
3. Keep precision constant for the same quantity across the whole paper, including tables and
   figures.
4. State a percentage's base. "A 20% increase" needs the reference value; percent and
   percentage point are different and are routinely confused.
5. Units, symbols, and their formatting are governed by `sentence-craft.md`, Numbers and
   Units. Do not restate those rules here.

## Correlation and Causation

1. `associated with`, `predicts`, `causes`, and `explains` are four different claims. The
   verb ladder in `sentence-craft.md` decides which the design earns.
2. A regression coefficient from observational data is an association, however many covariates
   are adjusted for.
3. State the confounders that were adjusted for and, more importantly, the ones that were not.
4. Do not report a causal mechanism in Results. Mechanism is interpretation and belongs in
   Discussion.

## What Goes in the Claim Ledger

Every statistic that supports a claim in the Abstract, Introduction, Discussion or Conclusion gets a ledger row, with the
figure, table, or reported number as its evidence cell. A claim whose only support is an
uncorrected exploratory test carries a populated risk cell. See `paper-review.md`.

## Common Faults

1. A p-value with no estimate and no interval.
2. `p = 0.000`, `p = n.s.`, or "approaching significance".
3. Non-significance reported as "no effect" or "no difference".
4. Post-hoc power.
5. A correction named without its family, or a family never disclosed.
6. R² presented as model-measurement agreement.
7. A test-set score computed after the test set informed a modelling choice.
8. A standardised effect size interpreted against unattributed size labels.
9. Precision that drifts between the text, the table, and the figure.
10. A percentage with no stated base.
11. A `±` whose meaning is never stated, or a value carrying more digits than its uncertainty.
12. Hours, grid points, or repeated votes counted as independent samples.
13. An agreement judged "good" against a margin chosen after the comparison, or against none.
14. A random split across samples that are adjacent in time or space.
15. A target effect size with no stated source.

## Checklist

1. Does every inferential result carry an estimate, an uncertainty, and a test statistic — or,
   for a Bayesian result, the model and the prior?
2. Are exact p-values reported, with `p < 0.001` used only as a floor?
3. Is an effect size given, in physical units where possible?
4. Is the sample size justified in Methods, without post-hoc power?
5. Is the number of tests per family disclosed, and the correction named over a named family?
6. Are null results reported with intervals, and distinguished from unresolved ones?
7. For a validated model: are both bias and scatter reported, with the aggregation interval,
   the pair count, and any cited criterion's edition?
8. For a predictive model: are the split, the seed or fold spread, and a trivial baseline all
   reported?
9. Is precision consistent across text, tables, and figures?
10. Does every verb match what the design earns?
11. Is the meaning of every `±` stated, and is each value rounded to its uncertainty?
12. Is the independent unit named behind every interval, p-value, and `n`, and is the
    dependence within a unit handled?
13. For a method comparison: are the limits of agreement reported, against a margin stated
    before the comparison?
14. For a predictive model: is preprocessing fitted inside the folds, and is the split blocked
    by time, room, or building?
15. Is the target effect justified as the smallest effect of interest, or is the detectable
    effect at the achieved *n* reported instead?
