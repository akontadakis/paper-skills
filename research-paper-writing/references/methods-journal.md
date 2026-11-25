# Methods Writing Guide (Journal Shape)

**Load when:** writing or revising the Methods of a journal paper.

**Contents:** Goal · Governing Test · Standard Subsections · Hard Rules · Writing Each Subsection · Common Mistakes · Checklist · Before and After (Procedure and Outcomes)

## Goal

Let a competent stranger repeat the study and get the same answer.

This is the journal/IMRAD Methods section: study design, materials, procedure, analysis.
For a conference paper whose Method section describes a pipeline of technical modules, use
`method.md` instead. Do not load both — they describe different sections with the same name.

## Governing Test

Reproducibility, not persuasion. Methods does not argue, compare, or interpret. If a sentence
justifies why your approach is better than someone else's, it belongs in the Introduction or
Discussion.

## Standard Subsections

Order them so a reader could execute them in sequence.

1. **Design** — study type, comparison structure, what varies and what is held fixed.
2. **Setting and case** — site, building, sample, population, model domain, period.
3. **Materials and inputs** — instruments, software, datasets, geometry, material properties, with sources.
4. **Procedure** — what was done, in order, with the parameters that govern it.
5. **Outcomes** — every quantity you will report, defined exactly, with its standard.
6. **Analysis** — statistics or post-processing, including how aggregates were formed.
7. **Validation or verification** — what the method was checked against, and over what domain.
8. **Ethics, approvals, availability** — as the venue requires, and per
   `ethics-and-participants.md` for any human-subject work.

For a modelling or simulation study, subsections 3, 4, 6, and 7 must satisfy the gate in
`simulation-reporting.md`. That gate is the reproducibility floor, not an optional extra.

Two subsections have their own reference file, and neither is optional where it applies.
Subsection 6, **Analysis**, is governed by `statistics-reporting.md` for any study reporting an
inferential statistic, a model-agreement metric, or a predictive score — it decides what must
accompany each number. Subsection 8, **Ethics**, is governed by `ethics-and-participants.md`
for any study involving people, personal data, or images of occupants — including glare
ratings, preference votes, alertness measures, and post-occupancy surveys, which are
human-subject work even when the paper reads as a physical measurement study.

## Hard Rules

1. Past tense for what you did. Present tense only for what a tool or standard does.
2. Every quantity you report in Results is defined here first. No new metric may appear later.
3. Every input value carries its provenance. See the provenance-language table in `simulation-reporting.md`.
4. Terminology fixed here is used unchanged for the rest of the paper.
5. Enough detail to repeat the work; anything longer goes to Supplementary with a pointer.
6. No results. Not even a preview.

## Writing Each Subsection

### Design

1. Name the design in the first sentence: comparative simulation study, parametric sweep, measurement campaign, validation study.
2. State the independent variables, their levels, and the full factorial or sampled subset.
3. State what is held constant, because that is what bounds the conclusions.
4. State the unit of analysis: the sensor point, the hour, the room, the site. Then state
   which unit is independent. Hours of one room and points of one grid are not, and that
   decides what any test may claim — `statistics-reporting.md`, What n Counts.
5. For a sampled parameter space, name the sampling design, the sample count, and the seed —
   `simulation-reporting.md`, section 2, rule 6.
6. For a study with participants, state the order in which conditions were presented and how
   it was assigned — `ethics-and-participants.md`, Describing the Protocol.
7. Mark each design choice that was made after the first results were seen: a threshold, a
   climate set, a grid size, a metric. It is reported as such, never as planned. See
   `paper-memory.md`, `analysis_status`.
8. When `.paper/design.yml` exists, take the design from it: the factors, the cases with their
   reasons, what was held constant, the analysis plan, and each amendment with its date and
   timing. A case chosen because its data were at hand is reported as that. When no dated
   design exists, describe what was done and call nothing planned. Never rebuild a plan from
   memory.

### Setting and Case

1. Describe the case well enough that a reader can picture it and rebuild it.
2. Give the reason the case was chosen, in one clause, if the choice is not obvious.
3. Distinguish a real case from a representative or synthetic one. Never let a synthetic case read as measured.

### Materials and Inputs

1. Instruments: make, model, quantity measured, resolution, calibration date.
2. Software: name, exact version, and any local modification.
3. Datasets: source, version, coverage, licence.
4. Physical properties: value, and where it came from — measured, datasheet, standard table, or assumed.
5. Tabulate anything with more than about six entries.

### Procedure

1. Chronological, numbered where a reader must follow order.
2. Include the settings that change the answer, not the ones that do not.
3. State every parameter that was swept and the value used for headline results.
4. State exclusions and failures: what was dropped, how many, and why.
5. Put a condition before the action it controls: `When the window luminance exceeded
   2000 cd/m², the blind was lowered`, not the reverse. A reader repeating the procedure
   meets the condition first. One action per sentence, in the order it was done.
6. A procedure is short, even sentences by design. Do not vary their length for rhythm; the
   length targets in `ai-tells.md` section 8 exempt procedure text.

### Outcomes

1. Define each reported quantity by its exact name, not its family. State the standard and edition.
2. Give the threshold and its source for any pass/fail metric.
3. Say where the quantity is evaluated: at which plane, which direction, which points, which hours.
4. Distinguish the primary outcome from secondary and exploratory ones, before you see the results.

### Analysis

0. `statistics-reporting.md` governs this subsection. What follows is the Methods-side
   subset; that file carries the full rules, including sample-size justification, the
   multiple-comparisons disclosure, and what a validation error metric must state.
1. Name the summary statistic and the population it summarises.
2. Name every test, with its assumptions and how they were checked.
3. State the software and version used for analysis.
4. State how missing data was handled.
5. State any normalisation, weighting, or convention that has more than one accepted form, and which form you used.

### Validation

1. State what was compared to what, and the error metric with its denominator.
2. State the domain over which agreement holds.
3. State which parts of the model were not validated. A declared partial validation is stronger than an implied complete one.

## Common Mistakes

1. Justifying the method instead of describing it.
2. Reporting a result ("the grid was refined until values stabilised at 4.2%") — the number belongs in Results.
3. A metric that first appears in Results.
4. Passive voice hiding who or what did something, when it matters.
5. A default silently substituted for a missing input, with no disclosure.
6. Recipe-style detail on the trivial, and silence on the parameter that actually moves the answer.
7. Terminology that drifts from Methods to Results.

## Checklist

1. Could a competent stranger repeat this and get the same number?
2. Is every quantity reported in Results defined here?
3. Does every input value state its provenance?
4. Are all version numbers present — software, datasets, standards?
5. Are exclusions and failures reported with counts and reasons?
6. Is the primary outcome distinguished from the secondary ones?
7. Is every multi-form convention declared?
8. Is there any result, comparison, or justification in this section that should move?
9. For a modelling study, does it pass every item of the gate in `simulation-reporting.md`?

## Before and After (Procedure and Outcomes)

The study is invented and is the same one used in `abstract.md` and `introduction.md`. It
shows the moves, not facts to reuse. The After uses only facts from the brief.

From the brief: 24 side-lit office geometries; four European climates, each with its own annual
climate file, with names and source not yet supplied; a virtual sensor at seated eye height of 1.2 m
at each desk, where vertical illuminance was computed in 8 view directions; Radiance, with all 8 directions in
one run per geometry and climate; Radiance version, sky model and rendering parameters not yet
supplied; conversion to melanopic equivalent daylight illuminance (EDI) following
CIE S 026:2018; per desk, the best- and worst-case direction was kept; target: melanopic EDI of
at least 250 lx for at least 50% of occupied hours (08:00–18:00), with the author's citation,
written here as [ref C]; primary outcome:
compliant plan depth, the distance from the window to the deepest desk that met the target,
reported as a mean over the 24 geometries and four climates; desks stand at the points of the
analysis grid; secondary outcome: the spread
across climates, the range of the four climate means under the best-case view direction; no geometry or desk
was excluded; no validation against measurement; the author agreed to cut the claim that the
approach is more accurate than previous methods.

**Before**

> We use Radiance to compute the illuminance. Then we calculate the melanopic EDI. We use 8 view
> directions. This approach is more accurate than previous methods.

**After**

> We simulated 24 side-lit office geometries in four European climates [insert the climate
> names, the weather files and their source]. At each desk, a virtual sensor sat at seated eye
> height (1.2 m). We computed vertical illuminance at each sensor in 8 view directions, with all
> 8 directions in one Radiance run per geometry and climate [insert the Radiance version, the
> sky model and the rendering parameters]. We converted the result to melanopic equivalent
> daylight illuminance (EDI) following CIE S 026:2018. For each desk, we kept the best- and
> worst-case view direction. No geometry or desk was excluded.
>
> The primary outcome was the compliant plan depth: the distance from the window to the deepest
> desk at which melanopic EDI, at 1.2 m in the given view direction, reached at least 250 lx for
> at least 50% of occupied hours (08:00–18:00) [ref C]. Desks stood at the points of the
> analysis grid. The depth was computed for the best- and worst-case view direction, as a mean
> over the 24 geometries and four climates. The secondary
> outcome was the spread across climates: the range of the four climate means under the
> best-case view direction.

What changed:

1. Past tense for what was done, as Hard Rule 1 requires.
2. The procedure runs in the order it was done, one action per sentence.
3. The primary outcome has its exact name, threshold and source, plane, direction and hours.
   The conversion names its standard and edition. These are the `Outcomes` rules.
4. The secondary outcome is defined here, so the 0.9 m in the Abstract has a definition.
   Hard Rule 2 requires that.
5. Missing climate and Radiance details became `[insert ...]` brackets, the form the Revision
   Contract asks for. `simulation-reporting.md` requires the details.
6. Exclusions are stated, even though there were none.
7. "More accurate than previous methods" is gone, because the author agreed to cut it, as
   `SKILL.md` Execution Rule 2 requires. Methods does not compare, by the Governing
   Test. The claim can return in the Discussion only with a validation, and there is none.
