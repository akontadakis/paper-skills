# Literature Search and Gap Verification

**Load when:** framing a paper, checking whether a research gap is real, or wording a novelty claim. Before drafting.

**Contents:** Goal · Where This Sits · Running It · Can the Search Find What Exists? · Three-Round Search · Concept × Method Matrix · Gap Taxonomy · Gap Evidence Package · Wording a Novelty Claim · The Two Failure Checks · When the Draft Is Already Written · Hand-Off · What This File Deliberately Omits · Checklist

## Goal

Establish that the gap you are about to claim actually exists, before you write the sentence
claiming it.

## Where This Sits

This runs **before** drafting. `introduction.md` tells you how to word a gap; this file tells
you how to earn one. The gap you verify here is the gap you state in `introduction.md`
(Journal Shape move 3, or Part B — the technical challenge — of the conference shape), and the gap that
`paper-review.md` will test the Results against — its **journal** rejection dimension 5.3,
"result already established in the literature the paper does not cite". (Note that
`paper-review.md` carries two numbering schemes: a conference set and a journal set. The
conference 5.3 is a different item.)

An unverified gap is the most expensive error in a paper. It survives every round of
sentence-level polish and is fatal at review.

## Running It

The three rounds below can be run by hand or dispatched to the `literature-crawler` agent,
which queries OpenAlex, Crossref, Semantic Scholar, arXiv, DBLP, and Europe PMC, records every
query string verbatim, deduplicates, builds the coverage matrix, and runs both failure checks.
Use `scripts/fetch_oa_pdf.py` to pull the open-access copies it finds.

Whether run by hand or by the agent, the same rule holds: **record only what a search actually
returned.** Never complete a partial record from memory and never add a paper you believe
exists but did not retrieve.

## Can the Search Find What Exists?

"Nothing found" means nothing unless the search could have found it. Test that before
reading a single result.

1. **Name your sentinel papers first.** List the papers you already know belong in the
   answer — the ones any competent search on this question must return — and check each
   one's DOI. Add one or two that should be excluded by your criteria, as controls.
   Entries in `question.yml` `closest_work` with `read: true` are the first sentinel papers,
   and candidates for `gap.yml` evidence.
2. **Run the search, then count.** Record how many sentinels the queries returned, by name:
   `sentinels found: 6 of 7; missed: Author 2019`. A missed sentinel is a fault in the
   query, the database choice, or the date limit. Find which, fix it, and re-run.
3. **The count is a floor, not a guarantee.** Finding every paper you knew about shows the
   search works for papers like those. It says nothing about the papers you did not know to
   look for. Rounds 2 and 3 are still required.
4. **Freeze the queries before you screen.** Once you start reading results, do not tune a
   query to pull in a paper you like or drop one you do not. A query changed after screening
   is a new search: record it as one, with its date.
5. **Reconcile what the database reported with what you retrieved.** For each query, record
   the total the database says matched and the number of records you actually pulled. If
   they differ, the page walk was cut short or a limit was applied. Say which.
6. **A result limit is not a search.** The first 100 hits of 2,400, ranked by a relevance
   score you cannot inspect, are a sample. Either walk the full set or state the cut and
   why it is defensible.

Record all of this in the protocol file, `.paper/corpus/<slug>-protocol.md`. The
`literature-crawler` agent does it for you.

## Three-Round Search

Do not stop after round one. Round one finds the papers you already knew about.

### Round 1 — Direct

Search your own terms, in combination:

1. Concept × concept: `melanopic` × `office`, `glare` × `automated shading`.
2. Concept × method: `mel-EDI` × `annual climate-based`, `DGP` × `field measurement`.
3. Concept × context: `daylight` × `deep-plan`, `circadian` × `high latitude`.

For each, run the name variants. Fields disagree on names:

- `melanopic EDI` / `mel-EDI` / `melanopic equivalent daylight illuminance`
- `daylight autonomy` / `climate-based daylight modelling` / `CBDM` / `annual daylight`
- `view direction` / `gaze direction` / `field of view` / `observer orientation`

Then search the related metrics alongside your own: `equivalent melanopic lux` / `EML`, and
`circadian stimulus` / `CS`. They are not synonyms. EML has a different normalisation and CS is
a different model, so a study that reports one has not reported the other. Record which metric
each study used.

Run the spelling variants too. Databases do not fold British and American spelling:
`modelling` / `modeling`, `colour` / `color`, `optimisation` / `optimization`,
`daylighting` / `day-lighting`, `behaviour` / `behavior`. A search on one spelling silently
misses the other half of the literature.

Record the keywords the retrieved papers use for your concept. They feed round two.

### Round 2 — Adjacent Fields

Use the harvested keywords to search outside your own literature. A daylighting question is
often already answered in chronobiology, ophthalmology, occupational health, transport
lighting, or horticulture. An ML question is often answered in statistics or signal
processing under a different name.

This round is where most false gaps die.

### Round 3 — Citation Tracking

1. Take the 5–8 most relevant hits from rounds 1 and 2.
2. Follow their references backward to the foundational works.
3. Follow citations forward to find who has since done what you plan to do.

Forward-tracking the most-cited paper in your area is the single highest-yield check for
"someone already did this".

**When tracking is finished.** Track in rounds: each round takes the records the previous
round added and follows their references and citations. Record, per round, how many new
records were screened and how many were included. Stop when a full round adds no new
included record, or when no untracked included record remains. Report the per-round counts
with the claim, so a reader can see the search ran dry instead of being told that it did.
One pass over five to eight papers is a start, not a finished search; say so if that is
where you stopped, and why.

## Concept × Method Matrix

Tabulate what you found. Rows are concepts or metrics, columns are methods or conditions.
White space is a candidate gap.

Example, daylighting:

```
                    | Annual CBDM | Field measurement | Lab / HDR | Subjective
--------------------|-------------|-------------------|-----------|------------
Illuminance / DA    |  many       |  many             |  many     |  some
DGP / glare         |  some       |  some             |  many     |  some
mel-EDI             |  few        |  few              |  some     |  few
View direction      |  (empty)    |  (empty)          |  few      |  (empty)
```

Rules:

1. An empty cell is a candidate, not a gap. Ask why it is empty before claiming it.
2. Some cells are empty because the combination is meaningless or impossible. Say so and
   move on.
3. Some are empty because the method cannot yet do it. That is a methods contribution, and
   a different claim from a knowledge gap.
4. Choose axes that matter to your question. Metric × method and geometry × climate are the
   two that usually pay off in building physics.

## Gap Taxonomy

Name which kind you have. They are written differently and defended differently.

| Type | Meaning | How it is written |
|---|---|---|
| **Complete** | Nobody has examined this at all | Rare. Requires the strongest evidence, because "nobody has" usually means "you have not found them yet". |
| **Partial** | Examined, but under narrower conditions than needed | The common and most defensible case. Name the conditions prior work covered and the ones it did not. |
| **Controversy** | Examined, and the literature disagrees | Name both positions and their studies. Your contribution is resolution or explanation, not novelty. |

A **controversy** gap is often the strongest paper available and is routinely overlooked
because it does not feel novel. Disagreement in the literature is a real, citable problem.

## Gap Evidence Package

Each gap you intend to claim needs, before you write it:

1. **At least three citations** that together show the gap.
2. **A quote from each**, so the claim is checkable later.
3. **Preferably, quotes where the prior authors state the limitation themselves.** A gap
   evidenced by the authors of the prior work is nearly unarguable at review.

Record it like this:

```
Gap: the effect of view direction on annual mel-EDI compliance has not been compared with the
effect of climate on the same buildings.
Type: partial
  [1] Author (2021), p.4: "all evaluations assume a fixed north-facing view"
  [2] Author (2022), p.9: "the effect of observer orientation was not modelled"
  [3] Author (2023), p.12: "future work should address view-dependent exposure"
Status: verified
```

Keep this. It becomes the Introduction gap paragraph and it answers the reviewer who asks
whether the gap is real.

## Wording a Novelty Claim

`first`, `no prior study`, `has not been studied`, `the only`, and `novel` are claims about
the whole literature. No search covers the whole literature, so the sentence carries the
search with it.

1. **Bound the claim to the search.** Write what was searched: `To our knowledge, based on a
   search of [databases] for [date range], last run on [date], no study has reported X.` The
   three bracketed items are the `search` fields of the gap's entry in `.paper/gap.yml`.
   If any of them is empty, the sentence cannot be written in this form.
2. **Never write a bare absolute.** `This is the first study of X` with no search behind it
   is the sentence a reviewer disproves with one citation.
3. **State the scope of the absence.** `No study has reported X under conditions Y` is
   usually the claim the evidence supports, and it survives the reviewer who knows a study
   of X under other conditions. It is still a claim about the literature and still names its
   search. One rule decides this: a statement about the specific papers you cite needs no
   search, and any statement about the literature as a whole names its search. The form that
   needs no search is the one in When the Draft Is Already Written, rule 3: `the studies
   cited above report X for conditions A and B, and none reports it for Y`, which a reader
   can check against those papers.
4. **Without a recorded search, use the weaker form.** `We are not aware of a study that
   reports X` is a statement about your reading and is defensible from it. It is the wording
   for a gap whose `status` is `unverified`.
5. **A dated search goes stale.** Re-run it before submission and before each resubmission,
   and update the date. A paper published during review is the reviewer's first comment.

## The Two Failure Checks

Run both before you commit to the gap.

### False Gap

The gap is already filled, under different terminology or in a neighbouring field.

1. Search each of your key terms' synonyms explicitly (round 1 list).
2. Search at least two adjacent disciplines (round 2).
3. Forward-track the field's most-cited paper (round 3).
4. Search for the *finding* you expect, not only your method: someone may have reached the
   same result by another route.

If a search finds it under another name, you do not have a gap. You may still have a
contribution — replication under new conditions, a better method, a reconciliation — but the
claim has to change.

### Echo Chamber

Every paper you found comes from one research group, one school, or one journal.

1. Check the author lists. If three or fewer groups dominate, keep searching.
2. Deliberately search for critics and alternative theoretical frames.
3. Include the strongest dissenting line in what you read, not only what supports you.

An echo-chamber reading produces a gap that exists only inside one community, and a reviewer
from outside it will say so.

## When the Draft Is Already Written

This file assumes you are working before drafting. If a finished manuscript turns out to
carry an unverified gap — the usual sign is the phrase "little attention has been paid" with
no citations behind it — the three-round search is still the fix, but you cannot always run
it: no search access, or no time before a deadline.

What to do instead, in order:

1. **Type the claim, do not delete it.** In the claim ledger, the gap statement is
   `needs evidence` with the reason "gap not verified against the literature" — the
   evidence (the three-round search) has not yet been produced, which is exactly what
   `needs evidence` means. Do not type it `gap`: that status is for claims where no
   evidence can exist, and it would trip the Submission Gate's load-bearing-gap item in
   the very deadline scenario this section handles. The row stays visible either way.
2. **Weaken the wording to what you can defend.** "We are not aware of a study that reports
   X" is defensible from your own reading. "Little attention has been paid to X" is a claim
   about the literature as a whole and needs the search.
3. **Reframe on what you can show.** A contribution stated as "the first study of X" needs a
   verified gap, and so does "X under conditions Y, which prior work has not reported": both
   speak about the literature as a whole. A statement about the papers you cite needs no
   search: "the studies cited above report X for A and B, and none reports it for Y". Use that
   form, and see Wording a Novelty Claim, rule 3.
4. **Run the search before submission anyway.** A false gap found by a reviewer costs more
   than one found late by you.

Never leave the strong wording in place unverified. That is the failure this file exists to
prevent, and it is fatal at review.

## Hand-Off

When both checks pass:

1. The verified gap goes into `introduction.md` as the gap statement — specific and missing,
   never "little attention has been paid".
2. The evidence package citations go into the Introduction and, in conference shape, into
   `related-work.md`. Each work goes into the `.bib` and onto `.paper/verified-refs.yml`
   first: the author writes a manual row, or you run `--online --record`. Cite a key only when
   it is on that list and the manuscript, the brief or `.paper/` shows that the work supports
   the sentence.
3. The dissenting studies found by the echo-chamber check go into `discussion.md`,
   `Comparing With Literature` — contradicting studies are addressed, not omitted.

## What This File Deliberately Omits

No citation-count targets, no relevance scores, no originality percentages. A tight
*Energy & Buildings* paper may cite 35 sources and a review 200; the right number is set by
the argument, not by a threshold. Any numeric quality gate on a literature search is
fabricated precision.

## Checklist

1. Have all three search rounds been run, not just the first?
2. Have the synonym variants of every key term been searched?
3. Has at least one adjacent discipline been searched?
4. Has the most-cited paper in the area been forward-tracked?
5. Is the gap typed as complete, partial, or controversy?
6. Does each gap have three citations with quotes?
7. Does any prior author state this limitation themselves?
8. Has the false-gap check been run against the *finding*, not just the method?
9. Do the sources come from more than three groups, and does the set include critics?
10. Were sentinel papers named before the search, and how many did it return?
11. Were the queries frozen before screening, with the database total and the retrieved
    count recorded for each?
12. Were British and American spellings both searched?
13. Did citation tracking run until a round added no new included record, with the
    per-round counts recorded?
14. Does every `first` or `no prior study` sentence name the databases, the date range, and
    the search date?
