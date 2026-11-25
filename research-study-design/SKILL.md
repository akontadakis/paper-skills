---
name: research-study-design
description: Use when a researcher is at an early stage, before the results exist or while the work is running - has an idea or a topic and no clear research question, asks whether an idea is new or worth a paper, must choose cases, climates, samples, participants, simulation runs or measurements, asks how many are enough, plans an analysis or a validation before the data, must choose an analysis after the results are in, or needs to record which code, inputs and tool versions produced a result. Not for writing or revising the paper (research-paper-writing) or for answering reviewers (responding-to-reviewers).
---
# Research Study Design

## Overview

Take a researcher from an idea to a study that can answer a question, and keep a dated record
of every decision made before the results exist. A fault in the design cannot be repaired by
good writing. The core rule is the Study Contract below.

## When to Use

- The researcher has an idea, a topic or an observation, and no sharp question yet.
- They ask whether an idea is new, or worth a paper.
- They choose cases, climates, samples, participants, runs or measurements, or ask how many
  (a power analysis).
- They plan an analysis, a validation or a pre-registration before the data exist, or must
  choose an analysis after the results are in. That choice is then recorded as `post hoc`.
- They run the work and need to record which code and inputs gave each result.

Not for writing or revising the paper: use `research-paper-writing`. Not for answering
reviewers: use `responding-to-reviewers`. Not for theses or grant proposals.

## Study Contract

1. **Decide before you look.** The question, the expected answer, the cases, the analysis, and
   the result that would change the conclusion are written to `.paper/` with a date, before
   the first production run. A choice made or changed after a result was seen is recorded as
   an amendment marked `post hoc`. Write that something was planned, fixed or pre-specified
   only when a dated record shows it.

2. **Every fact has a source.** The sources are the researcher, the project files, and a
   recorded literature search. What you recall about the literature is a lead, not a source:
   say it is from memory and unverified, and cite no paper from memory. Where a fact is
   missing — an effect size, a sample size, a threshold, a tool version, the reason for a
   case — write a bracket that starts with `insert` and names what is missing:
   `[insert the smallest glare-rating difference that would change the shading choice]`.
   A request for "just the number" still gets the bracket, with what the number depends on.

3. **The researcher decides. You challenge.** For each decision, state the strongest objection
   a reviewer would raise and the real options, with what each costs. Record the researcher's
   choice and reason. A choice you made for them is marked `proposed, not agreed` until they
   confirm it. Start from what this researcher observed, has, or doubts; do not hand over a
   list of typical gaps or typical contributions.

## Core Workflow

0. Read `.paper/` if the project has one. `references/study-memory.md` describes the three
   files this skill owns: `question.yml`, `design.yml` and `runs.yml`.
1. Find the stage the researcher is at, and load its guide from the table below.
2. Work through that guide's record, slot by slot. A slot the researcher has not filled stays
   a bracket. A short deadline does not change this.
3. Write the record to `.paper/` in the same turn, and show it. If the project has no `.paper/`
   folder, create it in the project's top folder.
4. Before the first production run, offer the `design-reviewer` agent
   (`paper-skills:design-reviewer` as a plugin), and give it this skill's folder path. It reads
   the two records as a reviewer would and reports; it decides nothing. Then freeze the design
   with a date.
5. When results exist, hand over to `research-paper-writing`. It reads the three files; nothing
   is retyped.

## What to Load

All guides are in `references/`.

| Stage | Load | Record |
| --- | --- | --- |
| An idea or topic; a question to sharpen; "is this new?"; go or stop | `question.md` | `.paper/question.yml` |
| Designing any study | `study-design.md`, then the field guide for each kind of evidence | `.paper/design.yml` |
| A simulation or modelling study | `design-simulation.md` | |
| A measurement campaign, or a study with participants | `design-measurement-and-participants.md` | |
| An ML, CV or NLP experiment | `design-ml.md` | |
| Running the work: pipeline, runs, code and input provenance | `run-record.md` | `.paper/runs.yml` |
| The layout of the three files, and who reads them later | `study-memory.md` | |
| An analysis chosen after the results are in | `study-design.md`, Freeze and Amend; then `statistics-reporting.md` of `research-paper-writing` | `.paper/design.yml` amendment |
| A review paper | `question.md`; the review protocol is in `review-papers.md` of `research-paper-writing` | `.paper/question.yml` |

A novelty claim needs a recorded search. The search method is in the `research-paper-writing`
skill: its `references/literature-and-gap.md`, and the `literature-crawler` agent.

## Output Contract

Return, in this order:

1. The record for the stage, as it was written to `.paper/`: every slot filled from a source, or
   bracketed.
2. For each decision in it: the strongest objection, and the options.
3. The open items: each bracket the researcher must fill, most important first, with what would
   fill it.
4. The files written, named.

## Scripts

Two scripts in `scripts/` keep the run record. Run them through the interpreter, from the
project folder, and give each script its full path under this skill's base directory:
`python3 <skill folder>/scripts/record_run.py --help` and
`python3 <skill folder>/scripts/check_provenance.py --help`.
`references/run-record.md` says when. Neither edits a manuscript, and a file a script could
not read is refused or reported as not checked, never as clean.
