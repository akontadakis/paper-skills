# Abstract Writing Guide

**Load when:** writing or revising an abstract. Versions 1-3 are for the conference shape, Version 4 for the journal and review shapes.

**Contents:** Goal · Before You Write (Conference Shape) · Version 1: Failure, Then Fix · Version 2: Failure, Insight, Then Fix · Version 3: Several Contributions · Example Shape (Version 2) · Common Mistakes (Conference Shape) · Version 4: Journal / IMRAD · Before and After (Version 4) · Abstract Quality Checklist

## Goal

An abstract is read alone, usually in a search result, by someone deciding whether to open the
paper. Write it last, from the finished paper. Revise it until every sentence does one job.

Versions 1–3 are for a conference paper, where the abstract presents a technical contribution.
Version 4 is for a journal paper, where the abstract reports a study. Choose by the paper shape
in `SKILL.md`, not by taste.

## Before You Write (Conference Shape)

Answer these four questions, one sentence each. If one has no answer, the paper is not ready
for its abstract.

1. What fails today, and why has no existing method fixed it?
2. What did we build or change?
3. Why does it work? Give the mechanism, not the result.
4. What can a reader do now that they could not do before, and what do they now understand?

Questions 1 and 4 decide the abstract. A vague answer to either gives a vague abstract.

## Version 1: Failure, Then Fix

Use when the contribution is one technique that answers one clearly stated failure.

### Structure

1. The task, in one sentence.
2. Where current methods fail, and why.
3. The contribution, named in one or two sentences.
4. What the contribution gains.
5. The evidence, with numbers.

### Rules

1. Mention only the prior work that bears on the failure you fix.
2. Name the technique. Do not walk through its steps.
3. The name must make sense on first reading. If a reader would stop to ask what it means,
   add a short plain gloss.

## Version 2: Failure, Insight, Then Fix

Use when an observation drives the design, and the observation is worth reporting in itself.

### Structure

1. The task, in one sentence.
2. Where current methods fail, and why.
3. The insight, in one sentence.
4. The technique that applies the insight, in one or two sentences.
5. What the technique gains.
6. The evidence, with numbers.

### Rules

1. The insight must be checkable: a claim the experiments test, not a slogan.
2. The technique must follow visibly from the insight. If the reader cannot see the link, the
   insight is wrong or the technique is described at the wrong level.
3. As in Version 1, name the technique and do not list its steps.

## Version 3: Several Contributions

Use when the paper makes two or three contributions that each stand on their own.

### Structure

1. The task, in one sentence.
2. Optionally, one sentence on what prior methods lack.
3. One sentence per contribution, each stating what it is and what it gains.
4. The evidence, with numbers.

### Rules

1. Each contribution and its gain share one sentence. A contribution whose gain cannot be
   stated in the same sentence is probably not a contribution.
2. Three contributions at most. A fourth is usually an implementation detail.

## Example Shape (Version 2)

The study is invented. The same conference study runs through the conference parts of
`introduction.md`, `method.md`, `experiments.md` and `conclusion.md`.

> Early-stage daylight design needs annual daylight maps within seconds, but a Radiance
> simulation takes about 40 minutes per floor plan. [Task.] Learned surrogates close this gap
> near the façade but fail deep in the plan, because their local filters cannot see the windows
> that light a distant point. [Failure and reason.] We
> observe that, for a given glazing type and orientation, annual daylight at a point depends
> largely on how much of its view is window and how far away that window is. [Insight.] We therefore give the network a window-visibility
> encoding, computed by ray casting on the plan. It gives every point its visible window
> fraction and the mean distance to the visible window. [Technique.] The encoding supplies long-range
> light paths as inputs, so the network no longer has to infer them. [Gain.] Over five
> training seeds and 1,200 floor plans from buildings not seen in training, the surrogate
> predicts daylight autonomy with a mean absolute error of 4.1 ± 0.3 percentage points (mean ±
> SD over the seeds), against 9.8 ± 0.5 for the best published baseline. It runs in 0.2 s per plan. [Evidence.]

## Common Mistakes (Conference Shape)

1. Listing the method's steps instead of naming the contribution.
2. A failure with no reason, such as "existing methods perform poorly".
3. An insight that only restates the result.
4. An evidence sentence with no number.
5. A gain claimed here that no experiment measures.

## Version 4: Journal / IMRAD

Versions 1-3 are conference abstracts: they sell a technical contribution. A journal abstract
reports a study. Use this version for journal/IMRAD papers.

### Structure

1. Context, in one or two sentences — why the question matters.
2. The gap or the unknown, in one sentence.
3. The objective, stated as a question or aim.
4. What was done: design, case, method, scale. Two sentences at most.
5. What was found: the primary result **with numbers**, then at most two secondary results.
6. What it means, bounded: one sentence of implication, one clause of scope.

### Hard Rules

1. Numbers are mandatory. A journal abstract with no quantitative result reads as having nothing to report. For a review, the numbers describe the corpus: the records screened and the studies included, beside the databases and the search date. A narrative review states its search strategy instead.
2. Results carry direction and magnitude, not just significance.
3. No citations, no undefined abbreviations, no figure or table references.
4. Self-contained: it will be read alone, in a database, by someone who never opens the paper.
5. Flowing prose, no labelled sections (`Background:`, `Methods:`), unless the venue requires them.
6. No claim here that the paper does not support. This is the most-read and least-checked part of the paper.
7. Respect the word limit exactly. Count it.

### Venue Limits

The skill carries no venue table — limits change and a stale table is worse than none. Get the
number from the journal's current author guidelines before counting, and record it with the
draft so the check is repeatable.

If the limit is genuinely unavailable, say so rather than reporting the check as passed, and
work to a generic 150–250-word assumption, labelled as an assumption to confirm — never as
the requirement. No named-venue numbers are kept here, deliberately: they go stale, and a
stale number reported as the rule is worse than none.

### Template

1. [Context sentence establishing why the quantity matters.]
2. [What remains unknown or untested.]
3. We [aim/asked whether] ...
4. [Design, case, scale, method, in one or two sentences.]
5. [Primary finding with number and direction.] [Secondary finding with number.]
6. [Implication], although [scope bound].

## Before and After (Version 4)

The study below is invented. It shows the moves, not facts to reuse. The same invented study
runs through the pairs in `introduction.md` and `methods-journal.md`. The After uses only facts
from the brief, as the Revision Contract in `SKILL.md` requires.

From the brief: melanopic daylight targets are set at the eye; most annual daylight studies
still report horizontal-workplane metrics; the gap, as the authors' own reading (the recorded
search is in `.paper/gap.yml` and is named in the Introduction): they know of no study that
compares the effect of view direction with the effect of climate on the same buildings; aim:
how strongly view direction, relative to climate, governs melanopic compliance; side-lit
offices; 24 office geometries; four European climates; simulation at eye height under the
best- and worst-case view direction; compliant plan depth is the distance from the window to
the deepest desk that met the target; the worst-case view direction cut the mean compliant
plan depth from 5.8 m to 3.1 m; the spread across climates was 0.9 m; no statistical test was
run, and the authors agreed to drop "significant"; the authors' interpretation: horizontal-workplane metrics may overstate the daylight that
occupants receive.

**Before**

> Daylight is very important for building occupants and has many benefits. In this paper, a
> comprehensive study of melanopic light in offices is presented using advanced simulation
> tools. The results show that view direction has a significant effect on compliance, which
> highlights the importance of considering occupants in daylight design.

**After**

> Melanopic daylight targets are set at the eye, yet most annual daylight studies still report
> horizontal-workplane metrics. We are not aware of a study that compares the effect of view
> direction with the effect of climate on the same buildings. We asked how strongly view
> direction, relative to climate, governs melanopic compliance in side-lit offices. We simulated
> 24 office geometries in four European climates at eye height, under the best- and worst-case
> view direction. The worst-case view direction reduced the mean compliant plan depth, the
> distance from the window to the deepest desk that met the target, from 5.8 m to 3.1 m, whereas
> the spread across climates was 0.9 m. Horizontal-workplane metrics may overstate the daylight
> that occupants receive, at least in the climates and geometries studied.

What changed:

1. The opening platitude became a context sentence with a stake.
2. "Comprehensive" and "advanced" are gone. They were empty modifiers that carried no fact.
3. A gap sentence and an aim sentence now exist. The gap is worded as the authors' own reading
   ("We are not aware of"). An abstract has no room for the search that a stronger form must
   name; the Introduction carries it. See `literature-and-gap.md`, Wording a Novelty Claim.
4. "Significant" is gone: no test was run, and the authors agreed to drop it. The numbers carry
   the effect.
5. The one new metric is defined where it first appears.
6. The closing claim keeps the authors' hedge ("may"). It is bounded to the climates and
   geometries in the brief, as Global Principle 15 requires.

## Abstract Quality Checklist

1. Conference shape: can a reader find the task, the failure, the contribution and the evidence in one pass?
2. Are all major claims supported by experiments?
3. Are technical names self-contained and readable?
4. Is there any sentence that mixes too many messages?
5. Journal shape: is there at least one number, with direction and magnitude?
6. Journal shape: is the closing claim bounded by its scope in the same sentence?
7. Is every abbreviation defined here, independently of the main text?
8. Is it within the venue's word limit?
