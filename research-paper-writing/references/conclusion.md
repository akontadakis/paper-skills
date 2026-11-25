# Conclusion Writing Guide

**Load when:** writing or revising a Conclusion. The sections before `Journal Shape` are for the conference shape, `Journal Shape` for journal and review papers.

**Contents:** Goal · Conference Shape · Structure · Limitations · Template · Journal Shape

## Goal

Leave the reader with the paper's takeaway, its strongest evidence, and an honest boundary.

## Conference Shape

The structure, limitation guidance, and template below are written for a conference paper whose
evidence is baselines and ablations. For a journal/IMRAD paper, use the `Journal Shape` section
at the end of this file instead — and note that in IMRAD most of this work is already done by
Discussion, so the Conclusion is short.

## Structure

1. The failure the paper removes, and the core idea that removes it, in one or two sentences.
2. The strongest evidence, with one number.
3. What the idea makes possible, or what it teaches.
4. One limitation paragraph.
5. One specific next step.

## Limitations

State a limitation as the boundary of what was shown. Tie it to the setting: the data the
method was trained and tested on, the assumptions it makes, and the conditions it was run in.
For example: trained only on side-lit plans; assumes a fixed sky model; tested only on
single-storey layouts.

Keep two kinds apart:

1. **Scope limitation.** Within the tested setting the method is competitive with the best
   current methods; outside it, it is untested. State this plainly in the Conclusion.
2. **Technical defect.** The method loses to strong alternatives on a key metric, or its gain
   costs too much elsewhere. This belongs in Experiments, with numbers. Do not move it into the
   Conclusion as a "limitation".

Leave out shortcomings that are only unfinished engineering. Mention one only if it marks
the edge of what the method can do.

## Template

1. [Failure] is removed by [core idea], because [mechanism].
2. On [cases], this gives [headline number], against [best alternative].
3. A limitation is [scope boundary]; [specific next step].

### Example Shape (conference)

The study is invented. It is the conference study used in `abstract.md`, `introduction.md`,
`method.md` and `experiments.md`.

> Telling a surrogate which windows each point can see accounted for most of its accuracy gain
> in our tests, because long-range light paths no longer have to be inferred from pixels. On
> 1,200 floor plans from buildings not seen in training, the mean absolute error was
> 4.1 ± 0.3 percentage points over five seeds. The best published baseline reached 9.8 ± 0.5,
> and the surrogate runs in 0.2 s per plan. It was trained only on unobstructed side-lit plans
> with a single glazing type. It has not been tested on atria or toplit spaces, and extending
> the encoding to roof openings is the next step.

## Journal Shape

In IMRAD the Conclusion is short — one paragraph, rarely two — because Discussion already carried
the interpretation, the comparison, and the limitations. Do not repeat Discussion here.

### Structure

1. The answer to the research question, stated as a finding, not as an activity.
2. The single most important number, with its scope condition attached.
3. What follows for practice or for the next study.
4. Nothing else.

### Hard Rules

1. No new results, no new citations, no new limitations.
2. Do not open with "In conclusion" or "In this paper we have presented".
3. Do not restate the method. The reader has just read it.
4. Bound the claim in the same sentence that makes it. An unbounded closing claim is the sentence reviewers quote back at you.
5. Some journals fold this into the last paragraph of Discussion. Check the venue before writing a separate section.

### Template

1. [Finding], under [scope condition].
2. [Strongest supporting number], obtained [how/where].
3. This implies [who should do what differently], provided [the binding limitation].

### Example Shape

The study is invented. It is the journal study used in `abstract.md` Version 4.

> These simulations suggest that view direction affected melanopic compliance more than climate
> did in the side-lit offices we simulated: the worst-case view direction reduced the mean
> compliant plan depth from 5.8 m to 3.1 m, against a spread of 0.9 m across four European
> climates. Horizontal-workplane metrics may overstate the daylight that occupants receive in
> such rooms. [insert the practice recommendation, if the Discussion makes one]
