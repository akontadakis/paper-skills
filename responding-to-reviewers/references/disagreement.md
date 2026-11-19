# Contesting a Reviewer

**Load when:** contesting a comment or declining a request.

**Contents:** Goal · Before You Contest · Who You Are Writing For · The Structure of a Contest · Types of Contest · Wording · After Contesting · Checklist

## Goal

Disagree in a way that persuades the editor and does not antagonise the reviewer who will
read your revision.

## Before You Contest

Answer these honestly. Most intended contests fail here.

1. Is the reviewer actually wrong, or did the paper fail to make the point clearly? If a
   competent reader reached the wrong conclusion, the writing caused it. That is a
   clarification, not a disagreement.
2. Can you show it, with a number, a citation, or a quoted line of the manuscript? If the
   argument reduces to your judgement against theirs, you will lose.
3. Is the point load-bearing? Winning an argument about something that does not affect the
   contribution costs more than conceding it.
4. Would conceding damage the paper? If not, concede.
5. Is your contest rate already high? Past roughly a fifth of substantive comments, each
   additional contest reads as a pattern rather than a position.

## Who You Are Writing For

The editor decides. The reviewer advises.

This means a contested point must be legible to someone who is not a specialist in the
sub-topic. State the disagreement plainly enough that an editor can see who is right without
adjudicating the technical detail themselves.

It also means the reviewer will read it. Anything that reads as scoring a point will come
back in round two.

## The Structure of a Contest

Four moves, in order. Skipping the first is the most common failure.

1. **Restate their concern accurately**, in its strongest form. If they would not recognise
   your restatement, you are arguing with something else.
2. **Concede whatever is true in it.** There almost always is something.
3. **Give the evidence.** A number, a citation, a quoted line from the manuscript, or a
   stated boundary condition.
4. **Offer something.** A clarification, an added sentence, a limitation, an appendix. A
   contest that ends in "so we changed nothing" rarely lands, even when correct.

The examples in this guide are invented.

Worked example:

> **Comment R2.3.** *"The comparison with Method X is missing and is essential to assess the
> contribution."*
>
> **Response.** We agree that a comparison against Method X would be informative, and that
> its absence should have been explained. Method X requires a bidirectional transmission
> dataset for the shading layer, which is not available for the assemblies studied here — those
> assemblies are characterised only by normal-incidence transmittance. Running Method X would
> require substituting a generic BSDF, which would compare our result against an assumed
> optical model rather than against Method X as applied. We have added this reasoning to §2.5
> and cited the two studies that report Method X under conditions where the data do exist,
> so a reader can place our results against them.

Note what it does: concedes the omission of an *explanation*, gives a concrete technical
obstacle, names what a naive compliance would actually measure, and still adds text.

## Types of Contest

### The reviewer is factually wrong

Correct it without saying they were wrong.

> The quantity in [insert the table] is the melanopic daylight efficacy ratio (mel-DER) of CIE S 026,
> which is referenced to D65. The melanopic ratio the reviewer cites is referenced to an
> equal-energy spectrum. The two differ by a constant factor of about 1.10, which accounts for
> the difference. We have named the quantity and its reference illuminant in the caption and in
> §2.3 to prevent the ambiguity.

This example is from another manuscript, one that reports mel-DER. The correction is the
fact plus the fix. No "in fact", no "actually", no "contrary to the reviewer's assertion".

### The request is out of scope

Say what the paper is.

> This paper examines [scope] under [conditions]. The reviewer's question concerns [other
> thing], which would require [what it needs]. We have sharpened the scope statement in §1
> so this boundary is clear from the outset, and noted the question as future work.

### Two reviewers disagree

Name it. Do not quietly pick one. First label the conflict — `direction`, `severity`,
`existence`, or `view`, as defined in `triage.md`, Step 5 — because the label decides whether
the answer is a choice, a concession to the stricter reading, or evidence. The example below
is a `direction` conflict: the two requests cannot both be met in the main text.

> Reviewer 1 asks for the analysis to be aggregated by orientation; Reviewer 2 asks for it to
> be disaggregated by hour. These cannot both be presented in the main text within the length
> limit. We have kept the orientation aggregation in the main text, since it carries the
> headline finding, and added the hourly disaggregation as Appendix B. We would welcome the
> editor's guidance if a different balance is preferred.

Then flag it in the cover letter.

### Complying would over-claim

The strongest contest available, because it defends the paper's integrity.

> The reviewer suggests stating that the compliance shortfall under the worst-case view
> direction is what occupants receive. Our study is a simulation with no validation against
> measurement, so we cannot support a statement about what occupants receive. We have kept
> the wording that describes the simulated result, and added to [insert the section] the
> specific measurement that would test the statement.

Never comply with a request to strengthen a claim past the evidence, however senior the
reviewer. See the hedging ladder in
`research-paper-writing/references/sentence-craft.md`.

### The request is infeasible

Be specific. "Not feasible" without detail reads as unwillingness.

State: what exactly is missing, why it cannot be obtained, and what you did instead.

## Wording

**Use:**

- "We agree that [point]. We did not [request] because [reason]."
- "Our reasoning was as follows, which we have now made explicit in §X:"
- "This would require [X], which is not available for [reason]."
- "We would prefer to retain [X], because [evidence]. We have added [Y] to address the
  underlying concern."
- "We may not have made this clear in the original submission."

**Never use:**

- "The reviewer misunderstood / is mistaken / clearly did not read"
- "As we already stated in Section X" — if they missed it, it was not clear enough
- "Obviously", "clearly", "trivially"
- "It is well known that" — this is an appeal to authority, not evidence
- "We respectfully disagree" as a whole answer — respectful of what, on what grounds?
- Sarcasm, or any rhetorical question

## After Contesting

1. Add something anyway. A clarifying sentence, a limitation, an appendix. If nothing is
   changed in the manuscript, the ledger row is `waived`, with `waived_by`, `waived_risk` and
   `flagged_to_editor`, never `done`.
2. Note in the cover letter which points you contested and why, in one line each. The editor
   should not have to reconstruct it from the point-by-point.
3. If the same point returns in round two, the argument did not work. Concede, or find a
   genuinely different one. Do not resend the first answer.

## Checklist

1. Is the reviewer wrong, or was the paper unclear?
2. Is there a number, citation, or quoted line behind the contest?
3. Is their concern restated in a form they would recognise?
4. Is whatever is true in their point conceded?
5. Does the response still add something to the manuscript?
6. Is the contest legible to a non-specialist editor?
7. Is the contest rate under roughly a fifth of substantive comments?
8. Any banned phrase from the list above?
9. Is every contested point summarised for the editor in the cover letter?
