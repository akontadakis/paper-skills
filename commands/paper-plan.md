---
description: Show the state of the study plan in .paper/ — the question, the design, the open brackets — and what blocks the first production run.
disable-model-invocation: true
argument-hint: "[project folder]"
---

First invoke the Skill tool with skill `research-study-design` (listed as `paper-skills:research-study-design` when the package is installed as a plugin). If the skill cannot be loaded, report that it failed to load and stop. Do not continue from this summary.

Then report the state of the study plan in the current folder, or in `$ARGUMENTS` if a folder was given. Change nothing.

1. If `.paper/` does not exist, say so and stop. Do not build one.
2. `question.yml`: give the question, the decision with its date, the expected answer with its date, the count of `closest_work` entries with `read: false`, and the id of the gap. Read the gap's status from `.paper/gap.yml`. If a file is absent, say so.
3. `design.yml`: say whether it is frozen, and on what date. Count the planned claims with no `would_change_conclusion`, the case sets with no reason, no `bounded_to` or no contrast case, the pre-run checks by `status` (`done`, `not done`, `not planned`, `not possible`), the `not planned` and `not possible` checks that no threat names, and the threats with no decision. If the file is absent, say so.
4. List every `[insert ...]` bracket in the two files, the most important first, with what would fill it.
5. List every choice still marked `proposed, not agreed`.
6. Say what blocks the first production run today: an unfrozen design, a planned claim that cannot fail, a pre-run check with no status, or with status `not done` that no run of `kind: check` in `runs.yml` records, a `not planned` or `not possible` check with no threat, or a bracket in the outcome definition. A check recorded as `not possible`, with its threat, does not block.
7. Say that the `design-reviewer` agent can review the design before it is frozen. Do not dispatch it in this command.
