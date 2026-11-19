# Designing an ML Experiment

**Load when:** the study trains or evaluates a learned model: ML, CV, NLP, or a surrogate for a physical simulation. Load after `study-design.md`.

**Contents:** Goal · Plan From the Claims · Baselines · Data and Splits · Seeds and Variation · Ablations · Training Data From a Simulator · The Compute Budget · What Would Change the Conclusion · Checklist

## Goal

Fix the comparison before any training run, so that the result is a test and not a search. The
general steps are in `study-design.md`. The reporting side is in `research-paper-writing`:
`experiments.md` and `statistics-reporting.md`, Predictive Performance.

The examples use one invented study, the conference study of the `research-paper-writing`
guides: a daylight surrogate with a window-visibility encoding.

## Plan From the Claims

Every claim planned for the Introduction needs an experiment that could refute it. Every
module and every sensitive setting needs an ablation. Write the table before training.

| Claim, module or setting | Experiment or ablation | Metric and direction | Would refute it |
| --- | --- | --- | --- |
| The encoding reduces error on unseen buildings | the full model against the same network without the encoding | mean absolute error, percentage points, lower is better | a difference smaller than the spread across seeds |
| The gain is not from network size | a larger network without the encoding | the same | the larger network matches the full model |

A claim with no row is cut. A row with no refuting result is not a test.

## Baselines

1. **Name them before training**: the strongest published method for the task, and one simple
   method that a reviewer will think of.
2. **Give each baseline the same tuning budget** as the proposed model: the same search, the
   same number of trials, the same validation set. Record the budget.
3. **Use the baseline's published code and settings where they exist**, and record the version.
   A baseline re-implemented from the paper is named as re-implemented.
4. A baseline result quoted from a paper was obtained on that paper's data and split. Quote it
   only when the data and the split are the same, and say so.

## Data and Splits

1. **Fix the split before any training**, and record how it was made, with its seed.
2. **Split by the independent unit.** Points of one floor plan, hours of one building and
   frames of one video are not independent. A split by point puts near-copies of the test data
   into training. For a claim about unseen buildings, split by building.
3. **The test set is used once**, at the end, for the numbers that are reported. Every choice
   made by looking at a score is made on the validation set.
4. **Check for leakage**: duplicates across splits, a normalisation computed over all the data,
   a feature that encodes the target.
5. Record what the data cover. A model trained only on unobstructed side-lit plans with a
   single glazing type is tested, and claimed, for those.

## Seeds and Variation

1. Decide the number of training seeds before the first run, and run every model with that
   number. The same number for the baselines.
2. Report the mean and the standard deviation across seeds, and say that `±` is that standard
   deviation. The spread across seeds is one floor for the no-difference margin. It leaves out
   the variation from the split and from which buildings are in the test set, so plan an
   interval over test buildings as well.
3. Record each seed in `runs.yml`, one row per seed. A best-of-several result is reported as best-of-several.

## Ablations

1. One ablation removes or replaces one thing. Two changes at once explain nothing.
2. Plan the ablation that could show the proposed module is not the cause of the gain. It is
   the one a reviewer will ask for.
3. An ablation added after the main results were seen is `post hoc`, and is reported as that.

## Training Data From a Simulator

1. When the training targets come from a physics engine, that engine's settings are part of the
   experiment. Design that step with `design-simulation.md`: convergence, the validation of the
   engine, and the record of its version and inputs.
2. The surrogate can be no more accurate than its targets. State the accuracy of the targets
   where it is known.
3. An error against the simulator is not an error against a real building. Decide which one
   the claim is about.

## The Compute Budget

1. Time one training run. Multiply by models, seeds, ablations and tuning trials.
2. If it does not fit, cut a model or an ablation, not the seeds of only one arm.
3. Record the hardware and the time of each run in `runs.yml`: the fields `hardware` and
   `wall_time`, set with `--hardware` and `--wall-time` of `record_run.py`. Unequal budgets between the
   proposed model and a baseline are a threat; record them.

## What Would Change the Conclusion

Write it per claim, before training. Three results commonly refute an ML claim.

1. The gain over the baseline is within the spread across seeds.
2. The gain disappears when the baseline receives the same tuning budget.
3. The gain is present on the validation data and absent on the test data.

## Checklist

1. Does each planned claim have an experiment and a refuting result, written before training?
2. Are the baselines named, with an equal and recorded tuning budget?
3. Is the split fixed, by the independent unit, and recorded with its seed?
4. Is the test set reserved for one final use?
5. Is the number of seeds fixed, and the same for every model?
6. Does each ablation change one thing?
7. If targets come from a simulator, is that step designed and recorded?
8. Does the compute budget fit, with any cut recorded?
