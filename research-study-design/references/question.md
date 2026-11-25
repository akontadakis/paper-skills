# From an Idea to a Research Question

**Load when:** the researcher has an idea, a topic or an observation and no sharp question, or asks whether an idea is new or worth a paper.

**Contents:** Goal · Start From What the Researcher Has · From Topic to Question · The Outcome Table · The Reader and the Decision · The Closest Work · Name the Contribution · Feasibility · Go, Narrow or Stop · Before and After · What This File Leaves Out · Checklist

## Goal

Turn an idea into a question that a study can answer, and decide honestly whether to go on.
The record is `.paper/question.yml`; its fields are in `study-memory.md`.

A weak question survives every later step. The design answers it faithfully, the runs succeed,
the paper is well written, and the reviewer asks what anyone learns from it.

## Start From What the Researcher Has

A question that belongs to this researcher starts from something they have. Ask which of these
five it is, and write the answer in `origin`, in their words.

| Starting point | Ask |
|---|---|
| An observation | What did you see that you did not expect? Where, and how often? |
| A contradiction | Which two results, or which result and which practice, do not agree? |
| A complaint from practice | Who is stuck, on what decision, and what do they do today? |
| A new tool, dataset or access | What can you measure or compute that could not be done before? |
| A method from another field | What does it do there, and why might it fail here? |

Do not supply the starting point. A list of typical gaps in the field, offered for the
researcher to pick from, gives a paper that any group could have written. If the researcher has
none of the five, say so: the next step is reading or a pilot, not a pitch.

## From Topic to Question

A topic names an area. A question names three things.

1. **The outcome**: the quantity that will be reported.
2. **The comparison**: against what. Another condition, another method, a threshold, a
   prediction.
3. **The conditions**: where the answer is meant to hold.

| | Topic | Question |
|---|---|---|
| Journal study | melanopic daylight in offices | In side-lit offices, does the occupant's view direction change the compliant plan depth more than the climate does? |
| Conference study | machine learning for daylight prediction | Does telling a surrogate which windows each point can see reduce its error on floor plans from buildings it has not seen? |

Narrow until the three parts can be written. Each narrowing step is the researcher's choice;
offer two or three ways to narrow and what each gives up.

"Can X be done?" and "we will develop a framework for X" are not questions. Ask what would be
known after the work that is not known now.

## The Outcome Table

Before any run, write every answer the study could give, and the paper each one makes.

| If the result is | The paper says | Worth a paper? |
|---|---|---|
| view direction changes the depth more than climate | horizontal-workplane metrics may overstate what occupants receive | yes |
| climate changes it more | one fixed view direction is an adequate simplification | yes |
| similar size | neither can be held fixed | yes |

Read the table three ways.

1. **Only one row gives a paper.** The study is a bet. Say so, record it as a risk, and look for
   a design in which the other rows also teach something.
2. **Every row gives the same paper.** The study cannot change anyone's mind. The question is
   not sharp yet.
3. **A row is missing.** "It did not work" and "no difference" are answers. Write them in.

The researcher then writes which row they expect, in `expected_answer`, and the date in
`expected_answer_on`. That sentence, written before the runs, is what later allows a result to
be called expected or surprising.

## The Reader and the Decision

Name one reader and what they would do differently for each row: a designer, a standards
committee, a researcher choosing a method, a manufacturer. "Researchers in the field will be
interested" names nobody.

If no reader acts differently on any row, the work may still be worth doing, as a dataset or a
replication. Then name it as that, under `contribution_type`.

## The Closest Work

Ask for the three to five papers nearest to the question. Record each in `closest_work`: `cite`,
what it `did`, how this study differs in `difference`, and `read`. One line each.

1. **The difference is stated against a paper, not against the field.** "No one has studied X"
   is a claim about the whole literature. "Author 2021 fixed the view direction; this study
   varies it" can be checked by anyone who opens Author 2021.
2. **What you remember is a lead.** If you recall work in the area, say that it is from memory
   and unverified, and describe it without a citation. The researcher, or a recorded search,
   turns a lead into an entry. Mark an entry `read: false` until someone has read the paper.
   An entry with `read: false` supports no claim. An entry with `read: true` is one of the
   first sentinel papers of the literature search, and a candidate for evidence in `gap.yml`.
3. **An idea is not new because nobody has named a paper.** Without a recorded search the gap is
   `unverified`. The search method is in `literature-and-gap.md` of the
   `research-paper-writing` skill, and its `literature-crawler` agent runs it.
4. **Until the search has run, the honest wording is about the researcher's reading**: "We are
   not aware of a study that ...". Do not offer "has received limited attention" or "little
   attention has been paid". Each is a claim about the literature with no search behind it.

If the closest paper already answers the question, that is a finding of this stage. The
options are to narrow to what that paper left open, to replicate it under new conditions, or to
stop.

## Name the Contribution

One type, named honestly: `finding`, `method`, `dataset`, `validation`, `replication`,
`negative result`, `review`.

A replication under new conditions is a contribution; a replication presented as a first is an
overclaim. A method paper still needs a question: what does the method make possible, and
against which existing method is it compared?

Write the contribution as one sentence in `contribution`, in the form the Abstract will need: what was found, or
what can now be done, and under which conditions. If the sentence would fit a dozen other
papers unchanged, it is not yet specific to this study.

## Feasibility

Five lines, each from the researcher or a bracket.

1. **Data**: what exists, who holds it, and under what terms.
2. **Tools**: what will run it, and whether the researcher has used it for this before.
3. **Time**: the cost of one case, from a pilot. A guess is a bracket.
4. **Ethics**: whether people, personal data or images are involved. If so, approval comes
   before any data.
5. **The smallest version**: the least study that would still answer the question. Run it first.

## Go, Narrow or Stop

The decision is the researcher's. Record it with its date and its reason.

| Decision | When |
|---|---|
| `go` | the question has its three parts, the outcome table has more than one useful row, and the smallest version is feasible |
| `narrowed` | the question was too wide for the data or the time; record what was cut |
| `stopped` | the closest work already answers it, no row would change what a reader does, or it is not feasible |
| `exploring` | reading or a pilot is needed before the decision |

Give your own view plainly, with the strongest objection. Agreement that the idea is good is not
help; a reviewer will not give it.

## Before and After

Both studies in the table under From Topic to Question are invented. The one below is the
conference study used in the `research-paper-writing` guides.

**What the researcher said**

> I want to write a paper on using machine learning to predict daylight in buildings. I think
> it is novel.

**A reply that does not help**

> This is a timely and promising topic. Typical gaps include generalisation, uncertainty and
> benchmarking. Contributions: (1) a dataset, (2) a model, (3) an evaluation.

It praises, it offers a menu, and its contribution list fits any surrogate paper.

**A reply that helps**

> "Machine learning for daylight prediction" is a topic. From memory, and unverified:
> surrogates for annual daylight metrics have been published for many years, so the topic alone
> is not new.
>
> What made you start on this? [insert the observation: for example, where existing surrogates
> failed on your plans]
>
> A question needs three parts: the outcome [insert the metric and its unit], the comparison
> [insert the baseline you would beat, by name], and the conditions [insert the building types
> and the plans the model has not seen].
>
> Closest work: [insert the three papers nearest to your idea, and one line on how yours
> differs from each].
>
> Until those are filled and a search is recorded, the honest status is: `exploring`, gap
> `unverified`.

**The same idea after the researcher answered**

> Does telling a surrogate which windows each point can see reduce its error on floor plans
> from buildings it has not seen? Outcome: mean absolute error in percentage points. Comparison:
> the best published baseline, and the same network without the encoding. Conditions:
> unobstructed side-lit plans, a single glazing type.

## What This File Leaves Out

1. The search itself: `literature-and-gap.md` in `research-paper-writing`.
2. The choice of journal: `submission-package.md` in `research-paper-writing`.
3. The design: `study-design.md`.

## Checklist

1. Is `origin` in the researcher's own words?
2. Does the question name an outcome, a comparison and the conditions?
3. Does the outcome table list every answer, including "no difference"?
4. Is the expected answer written down, with a date, before any run?
5. Is there a named reader who acts differently on at least two rows?
6. Is each closest paper recorded with its difference, and marked read or not read?
7. Is the gap `unverified` until a recorded search exists?
8. Is the contribution one honest type, in one sentence that fits no other paper?
9. Is the decision recorded with its date and its reason?
