# Introduction Writing Guide

**Load when:** writing or revising an Introduction. Parts A/B/C are for the conference shape, `Journal Shape` for journal and review papers.

**Contents:** Which Shape · Plan Backwards, Write Forwards · Part A: The Task and Why It Matters · Part B: Why Current Methods Fail · Part C: What We Do and Why It Works · Closing the Conference Introduction · Common Mistakes (Conference Shape) · Journal Shape · Before and After (Journal Shape) · Quick Quality Checklist

## Which Shape

This file covers two shapes. The **conference shape** has three parts: Part A, the task;
Part B, why current methods fail; Part C, what we do and why it works. The **journal/IMRAD
shape** is the `Journal Shape` section near the end. `Plan Backwards, Write Forwards` applies
to both.

## Plan Backwards, Write Forwards

Plan from the contribution back to the opening. Write from the opening forward to the
contribution.

Plan, in this order:

1. What exactly do we contribute: a new task, a new measure, a newly identified failure, or a
   new technique?
2. Which measure of the task must improve (accuracy, speed, robustness), which failure of
   current methods stands in the way, and what causes that failure?
3. Why does our contribution remove that cause? This is the paper's insight. State it in one
   sentence.
4. Which prior work leads a reader, step by step, to that failure?

Write, in this order:

1. Part A: the task and why it matters.
2. Part B: prior methods, leading to the failure and its cause.
3. Part C: the contribution, how it removes the cause, and the insight.
4. A closing paragraph with the evidence and, if the venue expects one, the contributions.

## Part A: The Task and Why It Matters

Choose the opening by how familiar the task is to the venue's readers.

| The task is... | Open with... |
| --- | --- |
| niche | a one-sentence definition (what output from what input), then two or three uses |
| familiar | its uses; skip the definition |
| familiar in general, but this setting is new | the general task's uses, then the specific setting, with its exact input and output |
| familiar, and its failure is easy to show | the task, then in the same paragraph how current methods work and where they break; Part B then deepens the failure instead of introducing it (see rule 4) |

Rules:

1. Part A is one paragraph.
2. Name concrete uses that the venue's readers care about, such as "comparing façade options
   during early design". "A wide range of applications" says nothing.
3. A definition sentence names both the input and the output.
4. Opening on the failure is the less common choice. Use it only when one or two sentences can
   show the failure convincingly. The paper then runs: Part A shows the failure through a first
   group of methods; Part B shows a second group that tries to fix it and still fails; Part C
   follows. The usual run is different: Part A gives the task; Part B gives a first group of
   methods and its limitation, then a second group, whose limitation is the failure you remove.
5. When the venue cares about one requirement, such as accuracy, speed or robustness, name it
   at the end of Part A. Part B then shows where current methods fall short of it.

### Example Shape (niche task)

The study is invented. It is the conference study used in `abstract.md`.

> Daylight surrogate modelling predicts an annual daylight map directly from a floor plan,
> without running a lighting simulation. [Task: output from input.] Architects need such maps
> while the plan is still changing, when a 40-minute simulation per option is too slow to
> inform the choice between options. [Use.]

## Part B: Why Current Methods Fail

This is the technical challenge, and it is the most important part of the conference
Introduction. Part B ends on the exact failure that Part C removes. Every failure carries two
things: what goes wrong, which a reader could observe, and why it goes wrong, which is the
technical cause. A failure with no cause gives Part C nothing to answer.

Choose a path:

1. **Existing task, a chain of methods.** Start from the general difficulty. Then give the
   earlier approach and where it stopped, then the recent approach with its failure and cause.
   The last failure is the one you remove.
2. **Existing task, an idea with an older precedent.** When an older line of work used an idea
   like yours, cite it as support and say why it fell short. Then show why current methods
   still fail. The precedent makes your insight credible; it does not make it less new.
3. **New task, no direct prior method.** State the goal. Then give the reasons it is hard, one
   per sentence ("First, ...", "Second, ..."), each with its cause.

Rules:

1. Every failure carries its cause, usually in a "because" clause.
2. The last failure in Part B is the one Part C removes. Check it by reading the last sentence
   of Part B and then the first sentence of Part C.
3. Never build Part B around a simple fix of your own that the paper then improves. That
   story makes the work read as a patch, and it removes the reader's curiosity by answering
   the question before it is asked. Frame even an incremental contribution by the failure it
   removes, not by the fix.
4. Name and cite the methods. Say what they do and where they stop; do not disparage them.

### Example Shape (path 1)

> Physics-based simulation gives accurate daylight maps but is too slow for design iteration.
> [General difficulty.] Early surrogates regressed a few summary metrics from room parameters
> such as depth and window-to-wall ratio [refs], but could not produce a spatial map.
> [Earlier approach and where it stopped.] Recent image-to-image networks predict the full map
> from a floor-plan image [refs]. They are accurate near the façade but lose accuracy deep in
> the plan, because their filters see only a local neighbourhood, while the light reaching a
> deep point depends on windows several metres away. [Recent approach, failure and cause.]

## Part C: What We Do and Why It Works

Answer these before writing:

1. Which failure from Part B does our method remove?
2. What is the contribution?
3. Why does it work? This is the insight.
4. For an existing task: what does it gain over prior methods?

Choose the paragraph form by the kind of contribution.

| Contribution | Paragraph form |
| --- | --- |
| one core idea with several gains | name it; point to the overview figure; say in one sentence what is new; explain how it works ("Specifically, ..."); give each gain against prior methods |
| two linked contributions | contribution 1 and its gain; the problem that remains; contribution 2 as the answer to that problem |
| one new module in an existing pipeline | the pipeline it builds on, cited; the observation that motivates the module; the module; why it beats the generic alternative |
| a design driven by one observation | the key idea first; the observation behind it, in plain words; how it is implemented; what it gains, with a number |

Rules:

1. Explain how the contribution works, at the level of its mechanism. Vague, high-level wording
   around a simple method reads as an attempt to inflate it, and reviewers mark it down. If the
   method is simple, say so, and let the insight carry the novelty.
2. The insight sentence says why the method works, not that it works.
3. Every gain named here is one that the Experiments section measures.
4. An overview figure, if used, shows the idea, not the full architecture.

### Example Shape (a design driven by one observation)

> Our key idea is to tell the network which windows each point can see, instead of asking it to
> infer this from pixels. [Key idea.] For a given glazing type and orientation, annual daylight
> at a point depends largely on how much of its view is window and how far away that window
> is, and both can be computed directly from the plan. [Observation.] We cast rays from every grid point and pass the visible window
> fraction and the mean distance to the visible window to the network as two extra input
> channels, a window-visibility encoding. [Implementation.] With long-range light paths given as
> inputs, error deep in the plan falls sharply: in the deepest third of each room, the mean
> absolute error is 6.0 ± 0.5 percentage points, against 21.5 ± 1.2 for the best published
> baseline. [Gain, with a number.]

## Closing the Conference Introduction

1. One evidence paragraph: the cases or datasets, the main baselines, and the headline result
   with one number and its spread.
2. Any further contribution, such as a new dataset or benchmark, with what it makes possible.
3. If the venue expects a contributions statement, write it as a short prose paragraph
   ("Our contributions are threefold. First, ..."). Global Principle 10 keeps bullets out of
   the Introduction. Each contribution should match a section of the Method and an experiment.

## Common Mistakes (Conference Shape)

1. Failures in Part B with no cause.
2. A last failure in Part B that Part C does not remove.
3. An obvious solution set up only to be improved on.
4. An insight that restates the result.
5. A contribution described only in abstract terms.
6. A gain claimed that no experiment measures.

## Journal Shape

A journal Introduction narrows from a field to a question. It does not sell a pipeline, and
"previous methods have difficulty in..." is conference framing that reads as combative in a journal.

### Structure (funnel, five moves)

1. **Field** — why this class of problem matters. One or two sentences. Real stakes, not a platitude.
2. **What is known** — the established position, cited, grouped by idea rather than by paper.
3. **The gap** — what is unresolved, untested, contradictory, or untransferred. State it as a specific missing piece, not as "little attention has been paid".
4. **Objective** — the aim, question, or hypothesis, stated explicitly. This sentence is the paper's contract.
5. **Approach and scope** — one or two sentences on what was done and over what domain. Optionally one sentence previewing the principal finding, if the venue permits it.

### Hard Rules

1. The objective sentence must exist, be findable, and be phrased as a question or aim: "We asked whether...", "The aim of this study was to...".
2. The gap you state is the gap the paper fills. A mismatch here is the most common reviewer complaint, and it is invisible to you once you have read your own draft twice.
3. Cite to establish the state of knowledge, not to prove you read widely. No citation dumps.
4. Do not disparage prior work. State what it did and where it stopped.
5. No results here beyond, at most, one preview sentence.
6. Present tense for established knowledge, past tense for what individual studies found.
7. Length: typically 4-7 paragraphs, and shorter than the Discussion.

### Template

1. [Field-level stake, quantified if possible.]
2. [What is established, grouped by idea, cited.]
3. [What remains unknown, specifically.]
4. [Why that gap matters — what breaks or stays uncertain because of it.]
5. The aim of this study was to [objective].
6. We [approach] for [case/scope], and [what is assessed].

### Example Shape

> Melanopic daylight targets are set at the eye, yet most annual daylight studies still report
> horizontal-workplane metrics. [Field.] Earlier compliance studies varied climate and geometry
> and held the assessment plane fixed, and the studies that assessed at eye height used a
> single view direction (refs). [Known.] None of the studies cited above compares the effect of
> view direction with the effect of climate on the same buildings. [Gap.] If view direction has
> the larger effect, horizontal-workplane metrics may overstate the daylight that occupants
> receive. [Why it matters.] The aim of this study was to quantify how strongly view direction,
> relative to climate, governs melanopic compliance. [Objective.] We simulated 24 side-lit
> office geometries in four European climates at eye height, under the best- and worst-case
> view direction, and compared the compliant plan depth in each. [Approach and scope.]

### Common Mistakes

1. No explicit objective sentence.
2. A gap stated in the Introduction that the Results never address.
3. Opening on a textbook definition.
4. "Little attention has been paid to X" when X has a literature you did not search.
5. A Related Work section pasted in whole — compress it, see `related-work.md`.
6. Method detail that belongs in Methods.

## Before and After (Journal Shape)

The study is invented and is the same one used in `abstract.md` Version 4 and in the
`Example Shape` of this Journal Shape section. It shows the moves, not facts to reuse. The
After uses only facts from the brief. It is condensed to one paragraph to show all five moves;
a real Introduction spreads them over four to seven paragraphs.

From the brief: melanopic daylight targets are set at the eye, and most annual daylight studies
still report horizontal-workplane metrics; earlier compliance studies varied climate and
geometry but held the assessment plane fixed at a horizontal workplane [refs A]; eye-height
studies used one fixed view direction [refs B]; verified gap, with its search recorded in
`.paper/gap.yml` (OpenAlex, Crossref and Semantic Scholar; 2010 to 2026; last run on
19 August 2026): no study compares the effect of view direction with the effect of climate on
the same buildings; the authors' reasoning: if view direction has the larger effect,
horizontal-workplane metrics may overstate the daylight that occupants receive; aim: how
strongly view direction, relative to climate, governs melanopic compliance; approach: 24
side-lit office geometries, four European climates, eye height, best- and worst-case view
direction.

**Before**

> In recent years, daylighting has attracted increasing attention. Many studies have
> investigated melanopic lighting [refs A]. However, little attention has been paid to the role
> of view direction. Therefore, this paper proposes a novel framework to address this problem.

**After**

> Melanopic daylight targets are set at the eye, yet most annual daylight studies still report
> horizontal-workplane metrics. Earlier compliance studies varied climate and geometry but held
> the assessment plane fixed at a horizontal workplane [refs A]. Studies that did assess at eye
> height used a single, fixed view direction [refs B]. To our knowledge, based on a search of
> OpenAlex, Crossref and Semantic Scholar for 2010 to 2026, last run on 19 August 2026, no study
> has compared the effect of view direction with the effect of climate on the same buildings. If
> view direction has the larger effect, horizontal-workplane metrics may overstate the daylight
> that occupants receive. The aim of this study was to quantify how strongly view direction,
> relative to climate, governs melanopic compliance. We simulated 24 side-lit office geometries
> in four European climates at eye height, under the best- and worst-case view direction.

What changed:

1. "Attracted increasing attention" became a field sentence with a real stake.
2. "Many studies have investigated" became a statement of what is known, grouped by idea.
3. "Little attention has been paid" became the specific missing piece. The sentence names its
   search, as `literature-and-gap.md`, Wording a Novelty Claim, requires.
4. A sentence now says why the gap matters.
5. "A novel framework" became an explicit aim sentence.
6. A closing sentence states the approach and its scope.
7. Past tense for what earlier studies did, present tense for what is known now, as Hard
   Rule 6 requires.

## Quick Quality Checklist

1. Does the first sentence of each paragraph state its message?
2. Does each paragraph carry one message only?
3. Conference shape: does every failure in Part B carry its cause, and does Part C remove the last one?
4. Journal shape: is there an explicit objective sentence, and does the stated gap match what the paper actually fills?
5. Are claims in Introduction aligned with the evidence reported later?
6. Is terminology stable across all sections?
