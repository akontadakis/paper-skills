# Related Work Writing Guide

**Load when:** writing or revising Related Work in a conference paper, or deciding where prior work goes in a journal paper.

**Contents:** Goal · Where This Section Lives · Workflow · Choosing Groups · Paragraph Template · Do and Don't · Checklist

## Goal

Show where the paper sits among the closest lines of work, so that a reviewer can check the
novelty claim quickly.

## Where This Section Lives

1. **Conference shape**: a standalone Related Work section, usually after the Introduction. Everything below applies as written.
2. **Journal / IMRAD**: most journals have no Related Work section. The same material goes into the Introduction, compressed, and the detailed comparison moves to Discussion. Check the venue before writing a separate section.
3. When folding into a journal Introduction: keep the grouping and the gap statement, drop the per-topic transition sentences, and cut the length by roughly half. Save the head-to-head comparison for Discussion, where you can compare against your own results.
4. The word "baseline" is conference vocabulary. In a journal, write "prior studies" or name them.

## Workflow

1. Start from the closest competitors: the methods a reviewer would name first.
2. Sort the rest into two to four groups by idea, not by year or venue.
3. For each group, say what its methods have in common, then the limitation that matters for
   the failure your paper removes (Part B of the Introduction).
4. Close each group by saying how your work differs, in technical terms.

## Choosing Groups

Typical groups are:

1. The mainstream methods for the task.
2. The methods closest to your core idea.
3. The techniques your method builds on.

For the invented daylight-surrogate study used in the conference examples, the groups would be:
faster simulation (GPU ray tracing, reduced sky models); learned daylight surrogates; and
visibility and view-factor methods from lighting and graphics.

## Paragraph Template

1. A first sentence that sets the group's scope.
2. A compact summary of its representative methods, cited.
3. Their limitation, as it bears on your failure.
4. A sentence that sets your work apart.

Within a paragraph, order the cited evidence to advance the argument — by default broad
context → specific applications → the closest precedent immediately before the gap — never
in the order you happened to read the papers.

**Diagnostic**: strip the citations and reread. The paragraph should still read as a
cumulative argument; if it collapses into a list of study summaries, it is a citation dump
(Don't rule 3), however well formatted.

## Do and Don't

1. Do compare mechanisms, assumptions and failure modes, not only results.
2. Do state the exact gap your work fills.
3. Do not turn the section into a citation dump.
4. Do not leave out the strongest competitors.
5. Do not build the section from one research group or one school. Include the strongest
   dissenting line. See the echo-chamber check in `literature-and-gap.md`.

## Checklist

1. Are the strongest and most recent competitors covered?
2. Does every group connect to your problem setting?
3. Is your difference stated in technical terms, not in promotional ones?
4. Does every core claim carry its citations?
