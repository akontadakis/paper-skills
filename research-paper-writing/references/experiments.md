# Experiments Writing Guide (Conference Shape)

**Load when:** writing a conference Experiments section, or any paper has a table (then the `Figure/Table Writing Rules` section only).

**Contents:** Goal · Three Questions the Section Must Answer · Plan From the Claims · Section Layout · Figure/Table Writing Rules · Rigor Checklist

This file is for the conference Experiments section. One section is shape-neutral:
`Figure/Table Writing Rules` applies to any paper with a table (see `What to Load` in
`SKILL.md`). For a journal paper, use `results.md` and `discussion.md` instead.

Numerical reporting in this section is governed by `statistics-reporting.md`. Four of its rules
decide most conference-paper reviews: report the train/validation/test split and never present
a fit statistic as performance; report spread across seeds or folds rather than a single run;
give the trivial baseline so the reader can see the floor; and treat a swept hyperparameter
reported at its best value as a multiplicity problem even though no test was run. A difference
between two models needs an estimate and a spread, not two point scores.

## Goal

Show, with fair evidence, that the method works, which of its parts make it work, where it
stops working, and what it is worth in practice.

## Three Questions the Section Must Answer

1. **Does it beat the strongest fair alternatives?** Compare against recent, strong methods,
   not convenient weak ones. Use the same data, splits, preprocessing and metrics for every
   method. Include the reference the field trusts, such as the physics simulation that a
   surrogate replaces.
2. **Which parts cause the gain?** Ablate each claimed contribution: remove it, replace it, or
   disable it, and report the change against the full method. When two parts interact, also
   ablate them together.
3. **Where does it stop working?** Test harder or out-of-distribution cases: more complex
   scenes, rarer cases, noisier inputs, stricter constraints. For a daylight surrogate, that
   means deeper plans, unusual window layouts, and climates outside the training set. Report
   the failures with the same care as the successes. They show the reader where the method's
   boundary lies.

## Plan From the Claims

Every contribution claimed in the Introduction needs an experiment that tests it. Every module
and every sensitive parameter in the Method needs an ablation. Build this table before running
anything. It lives in `.paper/design.yml` (`planned_claims`) and is made with
`research-study-design`:

| Claim, module or parameter | Experiment or ablation | Metric and direction | Table or figure |
| --- | --- | --- | --- |

A claim with no row is either tested or cut.

## Section Layout

1. **Setup.** Datasets or cases, splits, metrics with their direction and units, baselines, and
   implementation details not already in the Method.
2. **Main comparison** against the baselines and the reference.
3. **Ablations.** One core table that covers every contribution, then small focused tables for
   individual design choices. Pair each important ablation with a qualitative example, such as
   the predicted map beside the reference, so the reader sees the effect as well as the number.
4. **Limits and failure cases.**

### Example Shape (an ablation paragraph)

The study is invented. It is the conference study used in `abstract.md`, `introduction.md` and
`method.md`.

> Table 3 isolates the window-visibility encoding; every value is a mean over five training
> seeds ± SD. Removing the encoding raises the mean absolute error from 4.1 ± 0.3 to
> 9.1 ± 0.4 percentage points, close to the best published baseline (9.8 ± 0.5). Keeping only
> the distance channel gives 6.3 ± 0.3, so both channels contribute. A variant of our network
> with twice the receptive field and no encoding gives 7.6 ± 0.4, at 2.3 times the runtime. In
> the deepest third of each room, the full model reaches 6.0 ± 0.5, against 21.5 ± 1.2 for the
> best published baseline. In this test, the encoding, not network size, accounts for most of
> the gain.

## Figure/Table Writing Rules

A good table is part of the argument. Captions matter as much as the figures and tables they
describe.

### Hard rules

1. Put the caption above the table.
2. No vertical lines (`|`) between columns.
3. No double rules, and no stacks of `\hline`.
4. Use `booktabs` rules: `\toprule`, `\midrule`, `\bottomrule`.
5. Use as few horizontal rules as possible. A rule separates groups of rows, not every row.
6. Highlight only the key numbers, such as the best and second-best result or the row of the
   proposed method, with restrained colour or weight.

### Readability rules

1. Show the metric direction in the column header, for example `MAE ↓` or `R² ↑`.
2. Give units wherever a value cannot be read without them.
3. Align text columns left. Align numeric columns on the decimal point.
4. Use the same number of decimal places within one metric column.
5. Group results across datasets or settings with `\multicolumn` and `\cmidrule`, not with
   vertical separators.
6. One table carries one message. Do not mix unrelated results in one table.
7. When rows differ by attribute, such as which module is removed, make that attribute explicit
   in the row label or in its own column.
8. The caption states the setting, the protocol and the notation, and one sentence that names the message. It does not interpret.
9. If the table needs little explanation, one sentence summarising the main result is enough.
10. In a two-column layout, place a single-column table or figure in the right-hand column
    when the layout allows. The reader then enters the page from the top-left text without a
    break.

### Minimal LaTeX checklist

1. Load the packages in the preamble: `\usepackage{booktabs}`, `\usepackage{colortbl,xcolor}`,
   and optionally `\usepackage{siunitx}` for decimal alignment.
2. Replace `\hline` with `\toprule`, `\midrule` and `\bottomrule`.
3. Put `\caption{...}` before `\label{...}`, with the caption above the table.
4. Keep highlighting restrained. Never colour many cells.

## Rigor Checklist

1. Are the baselines recent and strong, and run under the same protocol?
2. Does every claimed contribution have an ablation?
3. Are the metrics standard for the task, with direction and units?
4. Is the spread across seeds or folds reported?
5. Does every number quoted in the Abstract and Introduction appear here?
6. Are the failure cases and the limits of the evaluation stated?
