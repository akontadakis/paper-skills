---
description: Run one round of the Independent Review on a section or a whole manuscript with a fresh reviewer that does not see the writer's self-assessment. It reports and does not fix.
disable-model-invocation: true
argument-hint: "[file or section to review]"
---

First invoke the Skill tool with skill `research-paper-writing` (listed as `paper-skills:research-paper-writing` when the package is installed as a plugin). If the skill cannot be loaded, report that it failed to load and stop. Do not continue from this summary.

Then run one round of the loop in the skill's `references/paper-review.md`, `Independent Review`, on `$ARGUMENTS`, or on the whole manuscript if nothing was given. A round is one review of one saved version of the text.

1. Run the mechanical checks and paste the output. A check that was not run is reported as not run.
2. Dispatch a fresh reviewer. Give it the text, the study type, and the dimension list. Do not give it any statement that the text is finished. Have it open every figure the text cites and read each against its source, as the skill's `references/figures-tables.md`, Check a Figure Against Its Source, says. Have it write its failure criteria per dimension before it reads the text.
3. Collect its findings in the form of the finding contract: severity, a quotation of at most 25 words or the places searched, and the source of any field norm.
4. Verify each finding against the manuscript before acting on it.
5. If `.paper/reviews/` holds an earlier round for the same scope, compare the two rounds as `The loop`, step 6, says: test each new finding against the version that earlier round reviewed. Name each finding that sits in a passage the earlier "Fixes applied" note lists as changed.
6. Write the round to `.paper/reviews/<date>-<scope>.md`. Do not fix anything in this command; report the findings and stop. The fix pass is a separate step of the loop.
