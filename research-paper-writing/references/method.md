# Method Writing Guide (Conference Shape)

**Load when:** writing or revising the Method section of a conference paper.

**Contents:** Goal · Before You Write · Start From the Pipeline Figure · Section Layout · Three Elements of a Pipeline Module · Clarity Check · Implementation Details · Common Mistakes

## Goal

Let a reader understand what was built, why each part is there, and why it works, well enough
to reimplement it.

This is the conference Method section: a pipeline of technical parts. For a journal/IMRAD
Methods section (design, materials, procedure, analysis), use `methods-journal.md` instead. Do
not load both — they describe different sections with the same name.

## Before You Write

List the modules of the pipeline. Then answer three questions for each one, in a table:

| Module | What does it do? (input, steps, output) | Why is it needed? (which problem) | Why does it work better than the obvious alternative? |
| --- | --- | --- | --- |

A module with an empty cell is not ready to write. An empty "why is it needed" cell usually
means the module is not needed.

## Start From the Pipeline Figure

Sketch the overview figure before writing prose. Each block of the figure becomes one
subsection, in the figure's order. If a subsection has no block, or a block has no subsection,
fix the figure or the outline first.

## Section Layout

1. **Overview.** The setting, meaning the input and the output, in one or two sentences. The
   core contribution in one or two sentences. A pointer to the overview figure if the pipeline
   is new. One sentence per subsection saying what it covers.
2. **One subsection per module**, in the order of the figure.
3. **Implementation details**, as the last subsection or in an appendix.

## Three Elements of a Pipeline Module

Each module subsection carries three elements, normally in this order in the text:

1. **Motivation.** The problem that makes the module necessary. Write it problem first:
   "Because X, we need Y". Typical openings name a problem left by the previous module ("This
   still leaves ..."), or a failure of prior methods stated in Part B of the Introduction
   ("Prior surrogates cannot ..., because ...").
2. **Design.** First the structure: the representation, network or data structure. Then the
   forward pass in the order it runs: given the input, first ..., then ..., finally ..., which
   gives the output and what it is used for.
3. **Advantage.** Why the module is better than the obvious alternative. Tie the advantage to
   something measurable, and to the experiment that measures it.

Draft the design first; it is the backbone of the subsection. Add the motivation and the
advantage around it afterwards.

### Example Shape (one module)

The study is invented. It is the conference study used in `abstract.md` and `introduction.md`.

> Image-based surrogates lose accuracy deep in the plan, because the light reaching a deep
> point depends on windows outside their filters' reach (Section 1). [Motivation.] We
> therefore compute a window-visibility encoding before the network runs. Given a floor plan
> with marked windows, we first place grid points at 0.5 m spacing. We then cast 360
> horizontal rays from each point and record which of them reach a window. Finally, we store
> for each point the visible window fraction, which is the share of rays that reach a window,
> and the mean distance those rays travel. The two values are stacked with the plan image as
> extra input channels. [Design: structure, then input, steps and output.] A deeper network or
> larger filters would widen the receptive field only gradually, and at growing cost. The
> encoding supplies the long-range information directly, at a fixed cost per plan. Section 4.3
> compares it with a network of twice the receptive field. [Advantage, tied to an experiment.]

## Clarity Check

Check the finished section at three levels.

1. **Logic.** Summarise the section in five lines. Do the lines read as one sequence?
2. **Paragraph.** Does each paragraph's first sentence say what the paragraph is about? Does
   each paragraph carry one message? See `paragraph-flow.md`.
3. **Sentence.** For every sentence, does the reader know why it is there? Are key terms
   fixed, never renamed between the Overview and the subsections?

## Implementation Details

Give everything a reimplementer needs: hyperparameters such as layer count and feature size,
normalisation, coordinate conventions, the training schedule, hardware and runtime. Nothing
here argues for the method. If a pipeline step runs a physics engine, for example Radiance
rendering the training data, that step also passes the gate in `simulation-reporting.md`
(see that file, When This Gate Applies).

## Common Mistakes

1. A module with a design but no motivation.
2. A motivation that restates the design, such as "we use X to apply X".
3. An advantage claimed with no experiment behind it.
4. Subsections in a different order from the overview figure.
5. A term renamed between the Overview and the subsections.
