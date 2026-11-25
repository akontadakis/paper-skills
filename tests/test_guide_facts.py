"""The guides state no fact, number or wording that a review has retired.

Each entry below was a fault found in the version 1.2.0 review: a wrong domain fact, an
example whose arithmetic does not work, or an example that breaks one of the skill's own
rules. The test fails if a retired wording comes back.

The invented journal study that runs through the examples has one set of facts:
24 side-lit office geometries, four European climates, mean compliant plan depth 5.8 m under
the best-case view direction and 3.1 m under the worst-case one, and a spread of 0.9 m across
climates. Its grid test uses 1.0 m, 0.5 m and 0.25 m spacing.
"""
import re
import unittest

from tests import _paths

FOLDERS = ("research-study-design", "research-paper-writing", "responding-to-reviewers",
           "agents", "commands")

# (pattern, why it was retired)
RETIRED = [
    # --- domain facts
    (r"only under one specific illuminant",
     "melanopic EDI and EML differ by a constant factor for every spectrum"),
    (r"(?:yield|are) upper bounds",
     "a boundary taken at the last passing grid point is a lower bound"),
    (r"right-censors? (?:the )?deep-plan", "grid spacing does not right-censor a depth"),
    (r"\b10 m (?:analysis |calculation )?(?:grid|is standard)", "a 10 m daylight grid is not plausible"),
    (r"10 m, 5 m,? and 2\.5 m", "the grid test uses 1.0 m, 0.5 m and 0.25 m"),
    (r"at 5 m spacing", "the grid test uses 1.0 m, 0.5 m and 0.25 m"),
    (r"`EML` / `circadian stimulus`", "EML and CS are related metrics, not synonyms of melanopic EDI"),
    (r"melanopic ratio in Table 2 is computed against D65", "the D65-referenced ratio is mel-DER"),
    (r"systematically high on narrow-band", "the sign of the binning bias depends on the spectrum"),
    (r"widest free index and needs no key", "OpenAlex needs a free key to page past the first page"),
    (r"state the power if you can compute", "power computed after the data are in is post-hoc power"),
    # --- arithmetic and coherence of the shared journal study
    (r"21\.7\s?:\s?1", "not a number of the shared journal study"),
    (r"4\.1% of the best", "not a number of the shared journal study"),
    (r"(?:collapsed|fell) to zero", "the worst-case compliant plan depth is 3.1 m"),
    (r"fell to 2\.1 m", "the worst-case compliant plan depth is 3.1 m"),
    (r"t\(38\) = 2\.29", "the interval 12 to 156 around 84 implies t = 2.36"),
    (r"unchanged in direction and magnitude", "a 6.1% change is a change in magnitude"),
    (r"direction and magnitude of the headline finding are unchanged",
     "a 6.1% change is a change in magnitude"),
    # --- examples that broke the skill's own rules
    (r"compliance is checked on a horizontal workplane",
     "melanopic targets are set at the eye; the premise of the shared study was corrected"),
    (r"limits compliance; climate does not", "the rewrite added a claim the source did not make"),
    (r"One hedge per claim, maximum", "hedges are frozen by the Revision Contract"),
    (r"PENDING VERIFICATION", "the contract bracket has one form: [insert ...]"),
    (r"will therefore overstate", "the authors' interpretation is hedged with 'may'"),
    (r"measured \[how/where\]", "a model output is never worded as a measurement"),
    (r"is an overestimate of what occupants receive", "the authors' interpretation is hedged with 'may'"),
    (r"Every comment has been addressed", "the example ledger holds declined and waived comments"),
    (r"None — different boundary condition", "comment R2.3 has one reason in every file"),
    (r"too strong for (?:a single|one) climate", "the shared study has four climates"),
    (r"most of its accuracy loss deep in the plan", "no experiment in experiments.md measures that"),
    (r"original submission reported 3\.3 m",
     "a depth read at the last passing grid point cannot fall when the grid is refined"),
    (r"change in sDA between refinements", "the study's outcome is compliant plan depth"),
    # --- rules that contradicted another guide
    (r"\(rRMSE, MBE, R²\)", "statistics-reporting.md: R² is not evidence of agreement"),
    (r"Past tense throughout", "a figure or table 'shows' in the present tense"),
    (r"`\.blg` show no warnings", "log warnings are triaged, not zeroed"),
    # --- found by the final review of version 2.0.0
    (r"single-climate basis", "the shared study has four climates"),
    (r"changed by 6\.1%", "the grid test changed the depth by 6.9%"),
    (r"change in sDA between successive", "the study's outcome is compliant plan depth"),
    (r'manuscript: "manuscript\.docx"', "the shared study's manuscript is manuscript.tex"),
    (r"Five specialist agents live", "the package has six agents"),
    (r"Both `SKILL\.md` files", "the package has three skills"),
    (r"`scripts/check_package\.py` when the skill itself was edited",
     "a package-maintenance script is not part of a manuscript review"),
]

# The skills, agents and commands never point a user at the package's own behaviour tests.
# Those are a developer tool; the owner decided on 2026-11-17 that the skills do not mention them.
NOT_IN_A_SKILL = [
    r"run_evals", r"\bevals/", r"plugin-evals", r"plugin eval\b",
    r"behaviou?r (?:test|suite|case)s?",
]

# "gaze" is not the study's term. These lines name it on purpose.
GAZE_ALLOWED = (
    "never_use",                    # the term lock that bans it
    "`view direction` / `gaze direction`",   # search variants in the literature
    '"gaze direction" (Methods)',   # the consistency checker's example of term drift
    "gaze-based metrics",           # a family of metrics, named once
)


def documents():
    for folder in FOLDERS:
        base = _paths.ROOT / folder
        if base.is_dir():
            yield from sorted(base.rglob("*.md"))


def flat(text: str) -> str:
    """One line of text: quote marks at line starts removed, whitespace collapsed."""
    text = re.sub(r"(?m)^\s*>\s?", "", text)
    return re.sub(r"\s+", " ", text)


class TestRetiredWordings(unittest.TestCase):
    def test_no_retired_wording_is_present(self):
        for doc in documents():
            text = flat(doc.read_text(encoding="utf-8"))
            for pattern, why in RETIRED:
                with self.subTest(doc=str(doc.relative_to(_paths.ROOT)), pattern=pattern):
                    self.assertIsNone(re.search(pattern, text), why)

    def test_no_skill_text_mentions_the_behaviour_tests(self):
        for doc in documents():
            text = flat(doc.read_text(encoding="utf-8"))
            for pattern in NOT_IN_A_SKILL:
                with self.subTest(doc=str(doc.relative_to(_paths.ROOT)), pattern=pattern):
                    self.assertIsNone(re.search(pattern, text, re.I))

    def test_the_shared_study_says_view_direction_not_gaze(self):
        for doc in documents():
            for number, line in enumerate(doc.read_text(encoding="utf-8").splitlines(), 1):
                if re.search(r"gaze", line, re.I) and not any(a in line for a in GAZE_ALLOWED):
                    with self.subTest(doc=str(doc.relative_to(_paths.ROOT)), line=number):
                        self.fail(f"'gaze' in: {line.strip()[:90]}")

    def test_a_novelty_claim_carries_its_search(self):
        """`no study has ...` is a claim about the whole literature. It names its search,
        or it is the weaker form about the authors' own reading."""
        for doc in documents():
            text = flat(doc.read_text(encoding="utf-8"))
            for hit in re.finditer(r"[Nn]o study has compared", text):
                before = text[max(0, hit.start() - 220):hit.start()]
                with self.subTest(doc=str(doc.relative_to(_paths.ROOT)), at=hit.start()):
                    self.assertRegex(before, r"To our knowledge, based on a search of")


class TestSharedJournalStudy(unittest.TestCase):
    """Where an example quotes the study's headline result, it quotes the same numbers."""

    def test_plan_depth_examples_use_the_study_numbers(self):
        for doc in documents():
            text = flat(doc.read_text(encoding="utf-8"))
            for hit in re.finditer(r"compliant (?:plan )?depth[^.]{0,80}?\bto (\d+(?:\.\d+)?) m\b", text, re.I):
                with self.subTest(doc=str(doc.relative_to(_paths.ROOT)), found=hit.group(0)[:80]):
                    self.assertEqual(hit.group(1), "3.1")


class TestContractBracketIsSearchedFor(unittest.TestCase):
    """A bracket that marks a missing fact must not reach the submitted paper."""

    PLACES = {
        "research-paper-writing/references/paper-review.md": "the Submission Gate",
        "research-paper-writing/references/latex-mechanics.md": "the LaTeX grep list",
        "research-paper-writing/references/word-manuscripts.md": "the Word checks",
    }

    def test_each_pre_submission_search_names_the_insert_bracket(self):
        for relative, name in self.PLACES.items():
            with self.subTest(place=name):
                self.assertIn("[insert", (_paths.ROOT / relative).read_text(encoding="utf-8"))


class TestOneRuleOnePlace(unittest.TestCase):
    """Where two guides once gave different rules, one guide now owns the rule and the other
    points to it."""

    def read(self, relative: str) -> str:
        return flat((_paths.ROOT / relative).read_text(encoding="utf-8"))

    def test_verb_ceiling_per_status_is_stated_once_and_pointed_to(self):
        owner = self.read("research-paper-writing/references/paper-review.md")
        self.assertIn("`shows`, `demonstrates`, `proves`, `establishes`, `confirms` or `indicates`", owner)
        for other in ("research-paper-writing/references/paper-memory.md", "agents/claim-auditor.md"):
            with self.subTest(file=other):
                self.assertIn("Status gates the verb", self.read(other))

    def test_ledger_script_uses_the_same_barred_verbs(self):
        import check_ledger
        self.assertEqual(check_ledger.STRONG_VERBS,
                         {"shows", "demonstrates", "proves", "establishes", "confirms", "indicates"})

    def test_venue_rules_have_a_field_for_each_value_the_guides_record(self):
        venue = self.read("research-paper-writing/references/venue-calibration.md")
        for field in ("reporting_guideline:", "prior_publication_policy:", "preprint_policy:"):
            with self.subTest(field=field):
                self.assertIn(field, venue)

    def test_word_guide_points_to_the_shared_table_rules(self):
        self.assertIn("Figure/Table Writing Rules",
                      self.read("research-paper-writing/references/word-manuscripts.md"))

    def test_overused_word_table_defers_to_the_cluster_rule(self):
        craft = (_paths.ROOT / "research-paper-writing/references/sentence-craft.md").read_text(encoding="utf-8")
        table = craft[craft.index("**Post-2023 overused register.**"):craft.index("## Sentence-Level Faults")]
        self.assertIn("cluster", table)


class TestHandOver(unittest.TestCase):
    """The study records written before the results are read by the later skills, so that
    nothing is retyped and nothing planned is rebuilt from memory."""

    def read(self, relative: str) -> str:
        return flat((_paths.ROOT / relative).read_text(encoding="utf-8"))

    def test_writing_skill_reads_the_study_records_at_step_zero(self):
        skill = self.read("research-paper-writing/SKILL.md")
        for name in ("question.yml", "design.yml", "runs.yml"):
            with self.subTest(file=name):
                self.assertIn(name, skill)

    def test_figure_inventory_links_each_figure_to_its_runs(self):
        memory = (_paths.ROOT / "research-paper-writing/references/paper-memory.md").read_text(encoding="utf-8")
        figures = memory[memory.index("## figures.yml"):memory.index("## terms.yml")]
        self.assertIn('runs: ["R3"]', figures)
        self.assertIn("`runs`", figures)

    def test_submission_gate_checks_provenance_and_post_hoc_wording(self):
        review = self.read("research-paper-writing/references/paper-review.md")
        gate = review[review.index("## Submission Gate"):review.index("### Waivers")]
        self.assertIn("check_provenance.py", gate)
        self.assertIn("timing: post hoc", gate)

    def test_methods_and_limitations_take_the_design_from_the_record(self):
        self.assertIn("design.yml", self.read("research-paper-writing/references/methods-journal.md"))
        self.assertIn("design.yml", self.read("research-paper-writing/references/discussion.md"))
        self.assertIn("runs.yml", self.read("research-paper-writing/references/simulation-reporting.md"))

    def test_reviewer_skill_answers_design_questions_from_the_record(self):
        self.assertIn("design.yml", self.read("responding-to-reviewers/SKILL.md"))
        comments = self.read("responding-to-reviewers/references/common-comments.md")
        self.assertIn("design.yml", comments)
        self.assertIn("runs.yml", comments)

    def test_two_commands_cover_the_plan_and_the_trace(self):
        for name in ("paper-plan", "paper-trace"):
            with self.subTest(command=name):
                text = (_paths.ROOT / "commands" / f"{name}.md").read_text(encoding="utf-8")
                self.assertIn("research-study-design", text)

    def test_design_reviewer_reports_and_does_not_edit(self):
        agent = (_paths.ROOT / "agents" / "design-reviewer.md").read_text(encoding="utf-8")
        head = agent.split("\n---\n", 1)[0]
        self.assertNotIn("Write", head)
        self.assertNotIn("Edit", head)
        self.assertRegex(head, r"Use (when|before|after)")


class TestLaterStages(unittest.TestCase):
    """The stages after the first submission, and the check of a result before it is used."""

    def text(self, relative: str) -> str:
        return (_paths.ROOT / relative).read_text(encoding="utf-8")

    def test_submission_guide_covers_rejection_supplement_and_proofs(self):
        guide = self.text("research-paper-writing/references/submission-package.md")
        for heading in ("## After a Rejection", "## Supplementary Material", "## Proofs"):
            with self.subTest(heading=heading):
                self.assertIn(heading + "\n", guide)

    def test_gate_asks_for_a_refreshed_search_behind_a_novelty_claim(self):
        review = flat(self.text("research-paper-writing/references/paper-review.md"))
        gate = review[review.index("## Submission Gate"):review.index("### Waivers")]
        self.assertIn("searched_on", gate)

    def test_run_guide_says_how_to_check_a_result_before_it_is_believed(self):
        self.assertIn("## Before a Result Is Believed\n",
                      self.text("research-study-design/references/run-record.md"))


class TestWorkedExamplePassesItsOwnRules(unittest.TestCase):
    """The journal study is the worked example of the .paper/ records. Its files must obey
    the rules the guides state."""

    def text(self, relative: str) -> str:
        return (_paths.ROOT / relative).read_text(encoding="utf-8")

    def test_the_grid_amendment_is_a_correction_not_a_choice(self):
        memory = self.text("research-study-design/references/study-memory.md")
        design = memory[memory.index("## design.yml"):memory.index("## runs.yml")]
        self.assertIn("kind: correction", design)
        self.assertIn("forced_by:", design)
        self.assertIn("`kind`", design)

    def test_a_skipped_check_in_the_example_is_listed_as_a_threat(self):
        memory = self.text("research-study-design/references/study-memory.md")
        threats = memory[memory.index("threats:"):memory.index("amendments:")]
        self.assertIn("grid convergence", threats)

    def test_claims_name_the_planned_claim_they_come_from(self):
        memory = self.text("research-paper-writing/references/paper-memory.md")
        claims = memory[memory.index("## claims.yml"):memory.index("## figures.yml")]
        self.assertIn('planned_claim: "P1"', claims)
        self.assertIn("`planned_claim`", claims)

    def test_every_table_the_example_claims_rest_on_has_a_figure_row(self):
        memory = self.text("research-paper-writing/references/paper-memory.md")
        figures = memory[memory.index("## figures.yml"):memory.index("## terms.yml")]
        self.assertIn('id: "Tab3"', figures)

    def test_gate_separates_a_choice_from_a_correction(self):
        review = flat(self.text("research-paper-writing/references/paper-review.md"))
        gate = review[review.index("## Submission Gate"):review.index("### Waivers")]
        self.assertIn("kind: choice", gate)
        self.assertIn("planned_claim", gate)


class TestGateReachesTheNewRecords(unittest.TestCase):
    def text(self, relative: str) -> str:
        return flat((_paths.ROOT / relative).read_text(encoding="utf-8"))

    def test_claim_auditor_reports_every_gate_item(self):
        agent = self.text("agents/claim-auditor.md")
        for needle in ("14", "16", "design.yml", "runs.yml"):
            with self.subTest(needle=needle):
                self.assertIn(needle, agent)
        self.assertNotIn("Read all four `.paper/` files", agent)

    def test_gate_command_names_the_provenance_check_and_the_design_record(self):
        command = self.text("commands/paper-gate.md")
        self.assertIn("check_provenance.py", command)
        self.assertIn("design.yml", command)

    def test_each_skill_says_how_a_script_path_resolves(self):
        for skill in ("research-study-design", "research-paper-writing"):
            with self.subTest(skill=skill):
                self.assertIn("full path", self.text(f"{skill}/SKILL.md"))

    def test_response_command_writes_decisions_only_after_the_author_confirms(self):
        command = self.text("commands/paper-respond.md")
        self.assertIn("proposed", command)



class TestVerifiedCitations(unittest.TestCase):
    """A citation is a fact. A draft cites only keys that were checked against a real record,
    and the checks before submission enforce it."""

    def text(self, relative: str) -> str:
        return flat((_paths.ROOT / relative).read_text(encoding="utf-8"))

    def test_revision_contract_treats_a_citation_as_a_fact(self):
        self.assertIn("verified-refs.yml", self.text("research-paper-writing/SKILL.md"))

    def test_reviewer_skill_adds_only_verified_citations(self):
        self.assertIn("verified-refs.yml", self.text("responding-to-reviewers/SKILL.md"))

    def test_the_bibliography_guide_shows_how_to_build_and_check_the_list(self):
        guide = self.text("research-paper-writing/references/latex-mechanics.md")
        section = guide[guide.index("## Reference Identity and Notices"):guide.index("## Brace Protection")]
        for needle in ("--record", "--verified", "manual"):
            with self.subTest(needle=needle):
                self.assertIn(needle, section)

    def test_the_gate_blocks_an_unverified_citation(self):
        review = self.text("research-paper-writing/references/paper-review.md")
        gate = review[review.index("## Submission Gate"):review.index("### Waivers")]
        self.assertIn("verified-refs.yml", gate)

    def test_the_gate_command_checks_the_list(self):
        self.assertIn("--verified", self.text("commands/paper-gate.md"))

    def test_the_idea_is_credited(self):
        self.assertIn("paper-orchestra", self.text("THIRD_PARTY.md"))


class TestReviewLoopUndoesAWorseFix(unittest.TestCase):
    """The review loop re-reviews after each fix pass, undoes a fix that made the text worse,
    and stops after a fixed number of rounds with the best version kept."""

    def loop(self) -> str:
        review = (_paths.ROOT / "research-paper-writing/references/paper-review.md").read_text(encoding="utf-8")
        return flat(review[review.index("### The loop"):review.index("## Pre-Submission Pass Order")])

    def test_the_reviewed_version_is_kept_before_fixing(self):
        self.assertIn("Keep the version", self.loop())

    def test_a_fix_that_introduced_a_finding_is_undone_not_patched(self):
        loop = self.loop()
        self.assertIn("Undo that fix", loop)
        self.assertIn("never patch the patch", loop.lower())

    def test_rounds_are_compared_by_severity_not_a_score(self):
        loop = self.loop()
        self.assertIn("critical", loop)
        self.assertIn("no score", loop)

    def test_the_loop_has_a_limit_and_keeps_the_best_version(self):
        loop = self.loop()
        self.assertIn("three rounds", loop)
        self.assertIn("fewest critical", loop)



class TestFigureCheckedAgainstItsSource(unittest.TestCase):
    """A figure is read against the data and the Methods it claims to show, not only against
    the design rules."""

    def guide(self) -> str:
        return (_paths.ROOT / "research-paper-writing/references/figures-tables.md").read_text(encoding="utf-8")

    def section(self) -> str:
        text = self.guide()
        start = text.index("## Check a Figure Against Its Source\n")
        end = text.index("\n## ", start + 5)
        return flat(text[start:end])

    def test_the_section_exists_and_is_listed(self):
        text = self.guide()
        self.assertIn("## Check a Figure Against Its Source\n", text)
        self.assertIn("Check a Figure Against Its Source", text.split("\n## ")[0])

    def test_a_plot_is_read_against_its_data(self):
        section = self.section()
        for needle in ("data file", "legend", "every plotted value"):
            with self.subTest(needle=needle):
                self.assertIn(needle, section)

    def test_a_diagram_is_read_against_the_methods(self):
        section = self.section()
        for needle in ("Methods do not describe", "leaves out", "order"):
            with self.subTest(needle=needle):
                self.assertIn(needle, section)

    def test_any_figure_keeps_its_caption_outside_and_its_labels_short(self):
        section = self.section()
        for needle in ("caption", "garbled", "sentence"):
            with self.subTest(needle=needle):
                self.assertIn(needle, section)

    def test_the_rendered_figure_is_looked_at(self):
        self.assertIn("rendered", self.section())

    def test_the_independent_review_includes_it(self):
        review = flat((_paths.ROOT / "research-paper-writing/references/paper-review.md").read_text(encoding="utf-8"))
        part = review[review.index("## Independent Review"):review.index("### The loop")]
        self.assertIn("Check a Figure Against Its Source", part)

    def test_the_review_command_includes_it(self):
        command = flat((_paths.ROOT / "commands/paper-independent-review.md").read_text(encoding="utf-8"))
        self.assertIn("Check a Figure Against Its Source", command)

    def test_the_idea_is_credited(self):
        self.assertIn("papervizagent", flat((_paths.ROOT / "THIRD_PARTY.md").read_text(encoding="utf-8")))



class TestSharedStudiesKeepTheirAddedFacts(unittest.TestCase):
    """The owner decided on 2026-11-19 that these facts of the two invented studies are fixed,
    beside the headline facts above. Journal study: the grid test changed the result by 6.9%
    between 1.0 m and 0.5 m and by 0.4% between 0.5 m and 0.25 m; the design was frozen on
    2026-03-02, the paper submitted on 2026-06-02 and the decision received on 2026-08-04; the
    revision added a sensitivity analysis as section 4.3 and moved the hourly data to Appendix B;
    it has no measurement. Conference study: a Radiance simulation takes about 40 minutes per
    floor plan; the error in the deepest third of each room is 6.0 ± 0.5 against 21.5 ± 1.2
    percentage points; the headline error is 4.1 ± 0.3 over five seeds."""

    def flat_documents(self):
        for doc in documents():
            yield str(doc.relative_to(_paths.ROOT)), flat(doc.read_text(encoding="utf-8"))

    def near(self, text: str, pattern: str, partner: str, width: int = 160):
        """Each match of `pattern` has `partner` within `width` characters of it."""
        for hit in re.finditer(pattern, text):
            window = text[max(0, hit.start() - width):hit.end() + width]
            yield hit.group(0), re.search(partner, window) is not None

    def test_the_grid_change_is_never_rounded(self):
        for name, text in self.flat_documents():
            with self.subTest(doc=name):
                self.assertIsNone(re.search(r"about 7\s?%", text))

    def test_the_second_grid_step_is_the_same_everywhere(self):
        seen = 0
        for name, text in self.flat_documents():
            for found, ok in self.near(text, r"0\.4\s?%", r"0\.5 m and 0\.25 m"):
                seen += 1
                with self.subTest(doc=name, found=found):
                    self.assertTrue(ok)
        self.assertGreaterEqual(seen, 2)

    def test_the_journal_study_claims_no_measurement_of_its_own(self):
        for name, text in self.flat_documents():
            with self.subTest(doc=name):
                self.assertIsNone(re.search(r"new measured values", text))

    def test_the_sensitivity_analysis_is_section_4_3(self):
        for name, text in self.flat_documents():
            if not name.startswith("responding-to-reviewers"):
                continue
            for found, ok in self.near(text, r"sensitivity analysis", r"§4\.3|Sec\. 4\.3"):
                with self.subTest(doc=name, found=found):
                    self.assertTrue(ok)

    def test_the_journal_study_dates_do_not_move(self):
        memory = flat((_paths.ROOT / "research-study-design/references/study-memory.md")
                      .read_text(encoding="utf-8"))
        ledger = flat((_paths.ROOT / "responding-to-reviewers/references/change-ledger-file.md")
                      .read_text(encoding="utf-8"))
        self.assertIn('frozen_on: "2026-03-02"', memory)
        self.assertIn('submitted: "2026-06-02"', ledger)
        self.assertIn('decision_received: "2026-08-04"', ledger)

    def test_the_deepest_third_errors_come_as_a_pair(self):
        seen = 0
        for name, text in self.flat_documents():
            for found, ok in self.near(text, r"6\.0 ± 0\.5", r"21\.5 ± 1\.2"):
                seen += 1
                with self.subTest(doc=name, found=found):
                    self.assertTrue(ok)
        self.assertGreaterEqual(seen, 2)

    def test_the_simulation_time_per_plan_is_forty_minutes(self):
        for name, text in self.flat_documents():
            for hit in re.finditer(r"(\d+) minutes per floor plan", text):
                with self.subTest(doc=name):
                    self.assertEqual(hit.group(1), "40")

    def test_the_headline_error_is_over_five_seeds(self):
        for name, text in self.flat_documents():
            for found, ok in self.near(text, r"4\.1 ± 0\.3", r"five (?:training )?seeds|9\.[18] ± 0\.[45]",
                                       width=260):
                with self.subTest(doc=name, found=found):
                    self.assertTrue(ok)

    def has(self, relative: str, *phrases: str):
        text = flat((_paths.ROOT / relative).read_text(encoding="utf-8"))
        for phrase in phrases:
            with self.subTest(doc=relative, phrase=phrase):
                self.assertIn(phrase, text)

    def test_the_conference_ablation_keeps_its_numbers(self):
        self.has("research-paper-writing/references/experiments.md",
                 "9.1 ± 0.4", "6.3 ± 0.3", "7.6 ± 0.4", "2.3 times the runtime")

    def test_the_conference_method_keeps_its_grid_and_rays(self):
        self.has("research-paper-writing/references/method.md",
                 "0.5 m spacing", "360 horizontal rays")

    def test_the_conference_metric_is_daylight_autonomy(self):
        self.has("research-paper-writing/references/abstract.md", "daylight autonomy")

    def test_the_review_round_keeps_its_comments(self):
        """R1.5 was partly conceded with the sensitivity analysis; R2.3 (Method X) and R2.8
        (solver time) were contested; R2.8 has no manuscript change, so it is waived."""
        ledger = "responding-to-reviewers/references/change-ledger-file.md"
        self.has(ledger, "| R1.5 | 1 | Add two more climates | evidence | partially concede |",
                 "| R2.3 | 2 | Add comparison to Method X | evidence | contest |",
                 "Appendix B")
        text = flat((_paths.ROOT / ledger).read_text(encoding="utf-8"))
        self.assertIsNotNone(re.search(r"\| R2\.8 \| 2 \| Report solver wall-clock time \| method \| contest \|", text))
        self.assertIsNotNone(re.search(r"R2\.8 \|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\|[^|]*\| waived \|", text))

    def test_no_page_or_distance_is_invented_in_a_model_reply(self):
        text = flat((_paths.ROOT / "responding-to-reviewers/references/response-letter.md")
                    .read_text(encoding="utf-8"))
        self.assertIsNone(re.search(r"\bp\.\s?7\b", text))
        self.assertIsNone(re.search(r"340 km", text))


if __name__ == "__main__":
    unittest.main()
