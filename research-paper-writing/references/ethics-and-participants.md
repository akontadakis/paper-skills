# Ethics, Approvals, and Human Participants

**Load when:** the study involves people, personal data, or images of occupants.

**Contents:** Goal · Scope · Where Each Piece Goes · The Ethics Subsection · Describing the Sample · Describing the Protocol · Bounding the Claim to the Sample · Data Protection and Availability · Preregistration · Common Faults · Checklist

## Goal

Report the human-subject and data-governance side of a study so an editor can clear it and a
reviewer can judge whether the sample supports the claim.

## Scope

Load this when the study involves people, personal data, images or video of occupants, or
regulated field access.

Two failures live here, and they are different. The first is a **compliance** failure: a
required statement is missing and the editor stalls the paper. The second is a **validity**
failure: the sample is described so thinly that no reader can tell who the result applies to.
The compliance failure is cheap to fix and the validity failure is not.

Human-subject work in lighting and building physics — glare ratings, preference votes,
alertness or sleep measures, post-occupancy surveys, wearable dosimetry — falls in scope even
when the paper reads as a physical measurement study.

## Where Each Piece Goes

| Item | Section |
|---|---|
| Approval body, protocol number, date | Methods, Ethics subsection |
| Consent procedure | Methods, Ethics subsection |
| Recruitment, eligibility, sample description | Methods, Setting and case or a Participants subsection |
| Attrition and exclusions | Methods, Procedure; counts also in Results |
| Deviation from the approved protocol | Methods, plus the Limitations paragraph |
| Data protection, retention, anonymisation | Methods, Ethics subsection, and Data availability |
| Formal declarations statement | Front or back matter — see `submission-package.md` |

`submission-package.md` owns the portal-facing declaration blocks. This file owns what the
manuscript body must say.

## The Ethics Subsection

Four sentences, in Methods, usually enough.

1. **The approval.** Name the committee or board in full, give the protocol identifier, and
   give the approval date. "Ethical approval was obtained" without a body and a number is not
   a statement an editor can act on.
2. **The framework.** Name the declaration or regulation the study followed — for example the
   Declaration of Helsinki for human-subject research, or the applicable data-protection
   regulation. Cite the version.
3. **The consent.** State that consent was informed, whether it was written or recorded, and
   whether participants were told they could withdraw. State separately any consent for
   publishing images, audio, or identifiable data.
4. **Compensation.** State whether participants were paid or otherwise compensated, and how
   much.

Special cases that need one extra sentence:

- **Exemption or waiver.** Name the body that granted it and the ground. Never write "no
  approval was required" without saying who determined that.
- **No approval sought.** State it plainly and give the reason. Some editors will still ask,
  but an honest statement is recoverable and a missing one is not.
- **Minors or other groups needing additional protection.** State who gave consent and who
  gave assent.
- **Retrospective or secondary data.** Name the source dataset, its licence, and the consent
  under which it was originally collected.
- **Deception or incomplete disclosure.** State it, and state the debriefing procedure.

## Describing the Sample

A reviewer's question is always the same: who does this result apply to? Answer it in
Methods.

1. **Size.** The number recruited, the number analysed, and the difference accounted for.
2. **Eligibility.** Inclusion and exclusion criteria as applied, not as intended.
3. **Recruitment.** How participants were found, because that sets the selection bias.
4. **Composition.** Report the characteristics that plausibly affect the outcome. For visual
   and non-visual lighting responses that usually means age distribution, and any reported
   visual condition, colour-vision deficiency, or ocular media state. For circadian and
   alertness outcomes it usually also means chronotype, recent sleep, shift-work history,
   caffeine, and any light exposure before the session.
5. **Report only what the study measured**, and do not infer a characteristic from a name, a
   role, or an appearance.
6. **Personal characteristics.** Report a demographic variable when it is an analysis variable,
   a stated eligibility criterion, or a known moderator of the outcome — and say which of the
   three it is. Report how it was collected: self-reported in free text, chosen from a fixed
   list, or drawn from records. If it was a fixed list, give the categories. Aggregate any cell
   small enough to identify someone, and say that you did.
7. **Environmental exposure history.** For lighting studies, the light the participant received
   before the session is part of the sample description, not an afterthought.

Write the sample description before you see the results, and do not add a characteristic to it
afterwards because it turned out to correlate with the outcome. That is the multiplicity
problem in `statistics-reporting.md`, and adding it late makes it invisible.

## Describing the Protocol

Many lighting studies with people are within-subject: each participant sees every condition.
The order of the conditions is then part of the result, and a reviewer will ask about it.

1. **Order.** State the order in which conditions were presented, and how it was assigned:
   randomised per participant, counterbalanced across participants, or fixed. For a
   counterbalanced design, name the scheme and say whether every order was used equally.
2. **A fixed order is a confound.** If every participant saw the dim scene before the bright
   one, order and condition cannot be separated. Say so in Limitations; do not report the
   condition effect as if order were absent.
3. **Carry-over and adaptation.** State the adaptation time before each rating and the
   interval between conditions. Visual adaptation, after-images, and fatigue all carry from
   one scene to the next, and alerting effects of light last longer than a short break.
4. **What the participant knew.** State what participants were told about the conditions and
   the hypothesis, and whether the experimenter in the room knew which condition was running.
   A participant who can see the luminaire change is not blind to the condition; say that
   plainly instead of claiming a blinding the design cannot have.
5. **Sessions.** Time of day, session length, number of sessions per participant, and the
   time between them. For circadian and alertness outcomes the clock time is a variable.
6. **Repeated ratings.** State how many ratings each participant gave per condition. The
   participant, not the rating, is the independent unit — `statistics-reporting.md`,
   What n Counts.

## Bounding the Claim to the Sample

This is where the ethics section meets the claim ledger.

1. A result from one age band, one climate, one building type, or one season is bounded by
   those conditions in the sentence that states it.
2. A convenience sample of students is not a claim about office workers. Say which population
   was sampled and let the Discussion argue the extrapolation, with the argument marked as an
   argument.
3. Any claim that outruns the sample gets a populated risk cell in the claim ledger. See
   `paper-review.md`.
4. The Limitations paragraph in `discussion.md` names the sample limits explicitly. A reviewer
   who finds a sample limit you did not name will assume you did not look.

## Data Protection and Availability

1. State what personal data was collected, how it was stored, and how long it is kept.
2. State the anonymisation or pseudonymisation applied, and at what point in the pipeline.
3. Distinguish anonymised from pseudonymised. They are different obligations and reviewers in
   regulated fields know the difference.
4. Where consent does not permit sharing, the Data availability statement says so and names
   the access route, if any. "Data available on request" with no conditions and no contact is
   likely to be read as unavailable, and some journals do not accept it.
5. Images or video of identifiable people need their own consent statement, separate from the
   study consent.
6. Physical measurement data, model files, and code have no personal-data constraint and are
   governed by `simulation-reporting.md` and the Data availability rules in
   `submission-package.md`. Do not let a personal-data restriction quietly cover them too.

## Preregistration

1. If the study was preregistered, cite the registration with its identifier and the date, and
   state whether it preceded data collection.
2. State every deviation from the registered plan, with the reason. An acknowledged deviation
   is a minor matter; an undisclosed one found by a reviewer is not.
3. Label outcomes as preregistered or exploratory, in Results, using the registration's own
   labels.
4. If the study was not preregistered, do not describe any analysis as confirmatory. A dated
   `design.yml` lets the paper say when a choice was made. Only a registration lets it call
   an analysis preregistered or confirmatory.

## Common Faults

1. "Ethical approval was obtained" with no body, number, or date.
2. Consent mentioned for the study but not for publishing images.
3. Recruited *n* and analysed *n* silently identical when there was attrition.
4. A student convenience sample carrying an unbounded claim about occupants or workers.
5. A demographic variable reported with no stated reason for reporting it.
6. Light exposure before a circadian or alertness session left unreported.
7. A protocol deviation described only in the response to reviewers, not in the manuscript.
8. Data availability restricted "for privacy" in a way that also blocks the simulation files.
9. A within-subject study with no stated presentation order, or a fixed order reported as if
   it were neutral.
10. "Blinded" claimed for a condition the participant could see change.

## Checklist

1. Does Methods name the approving body, the protocol number, and the date?
2. Is the consent procedure stated, with a separate statement for image or media use?
3. Are recruited, analysed, and excluded counts all reported and reconciled?
4. Is every reported personal characteristic justified as a variable, a criterion, or a known
   moderator, with its collection method stated?
5. Are small cells aggregated, with that noted?
6. For a lighting or circadian study, is prior light exposure reported?
7. Is every claim bounded to the population actually sampled?
8. Does the Limitations paragraph name the sample limits?
9. Is the data-protection statement consistent with the Data availability statement?
10. If preregistered: is the identifier cited and is every deviation disclosed?
11. Are the presentation order, its assignment, the adaptation time, and what participants
    knew all stated?
