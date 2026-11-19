# Paragraph Flow

**Load when:** a passage does not flow or is unclear, after drafting each section, or when a text must be cut to a word limit.

**Contents:** Goal · 1. Read It as a Stranger · 2. Reverse Outline · 3. Temporary Headings · 4. Name the Relation Between Sentences · Before and After · Cutting to a Length Limit · Checklist

## Goal

A reader says a text "flows" when each sentence answers the question the previous one raised.
When they say it does not flow, they rarely mean the words. They mean one of three faults: a
paragraph with no clear message, paragraphs that do not serve the section's claim, or
sentences whose relation to each other is left for the reader to guess. This guide finds which
of the three it is, and fixes that one.

Use it when the user asks whether a passage flows or is clear, and after drafting each section
(Core Workflow step 4 in `SKILL.md`).

## 1. Read It as a Stranger

You cannot judge flow in your own text by rereading it, because you supply the missing links
from memory. Read it as a competent researcher from a neighbouring field would: someone who
knows what illuminance is, but not your model, your case, or your abbreviations.

Ask of each paragraph:

1. Can I say its one message in one sentence?
2. Does its first sentence tell me what that message is?
3. Is every key term defined before it is used, or common to the field?
4. Can I name how each sentence relates to the one before it?

A "no" to 1 or 2 is a paragraph fault; go to section 2. A "no" to 4 is a sentence fault; go to
section 4. A "no" to 3 belongs to `sentence-craft.md`.

## 2. Reverse Outline

A reverse outline is made after writing, from the text as it stands. It shows the structure the
reader will actually meet, which is often not the one you planned.

1. Write down the section's main claim in one sentence.
2. Under it, write the first sentence of every paragraph, in order.
3. Under each first sentence, list the evidence or explanation that paragraph gives.
4. Check each first sentence against the main claim. Does it advance the claim?
5. Check each piece of evidence against its first sentence. Does it support that paragraph's
   message, or a different one?
6. Fix what does not map. Rewrite a first sentence that hides its message; move evidence to the
   paragraph it supports; cut or merge a paragraph that serves no part of the claim.

If the outline is easy to write, the section is organised. If it is hard to write, the main
claim or the first sentences are unclear, and no sentence-level edit will fix that.

## 3. Temporary Headings

When a full reverse outline is too much, insert a working heading above each group of
paragraphs, naming what that group does. Headings that repeat, or a group that resists a
heading, show where the structure breaks. Remove the working headings before the draft is
final, unless the venue's format uses subsection headings at that level.

## 4. Name the Relation Between Sentences

Every pair of adjacent sentences stands in a relation. Flow breaks when the reader cannot see
which one. Find the relation first, then decide whether the text needs to state it.

| Relation | The second sentence... | Words that name it |
| --- | --- | --- |
| Cause | gives the reason for the first | because |
| Consequence | follows from the first | so, therefore, as a result |
| Contrast | limits or opposes the first | but, however, whereas, although |
| Comparison | matches the first in another case | similarly, likewise |
| Example | instances the first | for example, in the north rooms |
| Refinement | narrows or qualifies the first | specifically, in particular |
| Sequence | happens after the first | then, after, once |

Rules:

1. A connective is a label. It must match the real relation. `Therefore` in front of a sentence
   that does not follow is worse than no connective, because it asserts a link that is false.
2. Use a connective only where the order and content of the sentences do not already show the
   relation. A condition placed before its consequence often needs no word at all.
3. `Moreover`, `Furthermore`, `In addition` and `Additionally` name no relation except "here is
   another thing". Several in a row mean the paragraph is a list, not an argument. Find the
   real relation, or split the list into its own paragraph. See `ai-tells.md` on empty
   transitions.
4. If no relation can be named, the sentence belongs in another paragraph, or nowhere.

## Before and After

The case is invented. The After uses only facts in the Before, as the Revision Contract in
`SKILL.md` requires. Only the order and the connectives change.

**Before**

> Furthermore, glare was assessed with DGP at each desk. The south rooms had the highest
> daylight autonomy. Moreover, the blinds were modelled as lowered when DGP exceeded 0.40. In
> addition, the south rooms had the lowest daylight autonomy once blinds were included.

**After**

> The south rooms had the highest daylight autonomy. Glare was
> assessed with DGP at each desk, and the blinds were modelled as lowered when DGP exceeded
> 0.40. Once blinds were included, the south rooms had the lowest daylight autonomy.

What changed:

1. `Furthermore`, `Moreover` and `In addition` are gone. None of them named a relation.
2. The glare rule now comes before the result it changes, so the sequence carries the
   relation without a connective.
3. The contrast between the two results is carried by the opening of the last sentence
   ("Once blinds were included"), which now follows the rule it depends on.
4. Every number, term and finding is unchanged, and no reason was added. Why the south rooms
   fell furthest is not in the Before, so the After does not say it.

## Cutting to a Length Limit

A word limit names no specific change, so the Revision Contract holds for the text you keep.

1. Cut repetition and throat-clearing first: a sentence that restates the one before, an
   announced opener, a sentence that only says what the section will do.
2. Then propose detail to move to the supplement. Move it only when the author agrees, and
   write the pointer as `[insert the supplement section]` until that section exists.
3. Then merge paragraphs that carry one message.
4. Numbers, units, citations and hedges stay as they are.
5. Remove a claim only by the author's decision, and update its `claims.yml` row in the same
   pass.
6. Report the word count before and after, and list what was cut.

## Checklist

1. Does every paragraph have one message, stated in its first sentence?
2. Does every first sentence advance the section's main claim?
3. Can you name the relation between every pair of adjacent sentences?
4. Does every connective name the relation that is really there?
5. Are there no runs of `Moreover` / `Furthermore` / `In addition`?
