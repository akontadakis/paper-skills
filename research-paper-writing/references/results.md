# Results Writing Guide

**Load when:** writing or revising the Results of a journal paper, or a combined Results and Discussion section.

**Contents:** Goal · Hard Rules · Ordering · Paragraph Pattern · Reporting Numbers · Figures and Tables · Negative and Null Results · When the Journal Combines Results and Discussion · Common Mistakes · Checklist

## Goal

Report what was found, in an order the reader can follow, with zero interpretation.

Use this guide for journal-shape papers (IMRAD). For conference-shape papers with baselines and
ablations, use `experiments.md` instead. Do not load both, except the
`Figure/Table Writing Rules` section of `experiments.md`, which applies to any paper with a table.

## Hard Rules

1. No interpretation, no mechanism, no comparison to other studies. Those belong in Discussion.
2. No result may appear in Discussion that was not first reported here.
3. Do not restate a table in prose. The text names the pattern; the table carries the numbers.
4. Past tense for what you did and found. Present tense for what a figure or table shows: `Figure 3 shows`.
5. Every number in the text must be traceable to a table, figure, or stated computation.
6. A result from an analysis chosen after the data were seen — a threshold, a subgroup, a
   climate subset, a metric picked because the first runs suggested it — is labelled
   exploratory where it is reported, and is never worded as the planned test. Record it as
   `analysis_status: post hoc` in `.paper/claims.yml`; see `paper-memory.md`.

## Ordering

1. Order by the research questions stated in the Introduction, in the same sequence.
2. Primary outcome first, secondary outcomes after, exploratory findings last and labelled as such.
3. Within an outcome: overall result, then breakdown by condition/subgroup.
4. Do not order by the sequence in which you happened to run things.

## Paragraph Pattern

Each paragraph answers one question and follows the same three moves:

1. **Point** — the finding, in the first sentence, as a claim with direction and size.
2. **Evidence** — the number(s) with uncertainty, and the pointer (`Table 3`, `Fig. 5b`).
3. **Qualifier** — the condition under which it holds, if it does not hold everywhere.

Example shape. The study is invented; it is the journal study used in `abstract.md` Version 4.

> Compliance depended more on view direction than on climate. The mean compliant plan depth
> fell from 5.8 m under the best-case view direction to 3.1 m under the worst-case one (means
> over the 24 geometries in four climates, [insert the spread across geometries]; Table 2), a
> reduction of 2.7 m. The spread across the four climates was 0.9 m.

## Reporting Numbers

1. Report the effect and its uncertainty, not a p-value alone. `statistics-reporting.md`
   carries the full rule — the estimate, the uncertainty, and the test statistic, all three —
   plus what to report for a null result, a validated model, and a predictive score.
2. Give the direction and magnitude in words before the digits: "fell by a third (34%)".
3. Keep decimal places consistent within a metric, and no more than the measurement supports.
4. State the denominator for every percentage.
5. State n for every aggregate — points, hours, timesteps, or sites, whichever it is.
6. Name the summary statistic explicitly (mean, median, spatial mean over the grid).
7. If a value is bounded by something physical, say so where you report it, not later.
8. A difference in significance is not a significant difference. If A reached significance
   and B did not, that does not establish A ≠ B — test the difference (or interaction)
   directly, or do not claim it.

## Figures and Tables

1. Plan the display items first; the Results text is written against them.
2. Each display item carries one message, named in the caption.
3. Text and display item must not duplicate. If the table already says it, the text says why it matters — and if that is interpretation, it goes to Discussion instead.
4. Reference every display item in the text, in numerical order.
5. See `figures-tables.md` for caption anatomy, error bars, and palette rules.

## Negative and Null Results

1. Report them. A pre-registered comparison that came out flat is a result.
2. Do not describe a null as "a trend towards" anything.
3. Distinguish "no effect detected" from "effect indistinguishable from zero at this power".
4. If a result contradicts an expectation stated in the Introduction, report it plainly here and explain it in Discussion.

## When the Journal Combines Results and Discussion

Many engineering journals use one combined section. Keep the two kinds of sentence apart
inside each paragraph:

1. First the finding, with its number, its unit and its figure or table, and no interpretation.
2. Then the interpretation, marked by its hedging verb.

An interpretation carries no number that the finding sentence did not give. The limitations
paragraph is still written, as `discussion.md` says.

## Common Mistakes

1. Sneaking interpretation in ("as expected", "confirming that", "due to").
2. Repeating every table cell as a sentence.
3. Reporting significance without effect size.
4. Introducing a new metric that was never defined in Methods.
5. Changing terminology from Methods (same concept, new word).
6. Reporting a substituted default as if it were measured. See `simulation-reporting.md`.

## Checklist

1. Does each paragraph state one finding in its first sentence?
2. Is every claim here free of interpretation?
3. Does every number have uncertainty, n, and a denominator where applicable?
4. Is every display item referenced, in order, exactly once as a primary reference?
5. Is the ordering the same as the research questions in the Introduction?
6. Is terminology identical to Methods?
7. Is anything reported here missing from Methods (an undefined metric or unstated procedure)?
