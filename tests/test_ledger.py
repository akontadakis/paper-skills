import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import _paths

try:
    import yaml  # noqa: F401
    HAVE_YAML = True
except ImportError:
    HAVE_YAML = False

import check_ledger
from check_ledger import audit

SCRIPT = _paths.SCRIPTS / "check_ledger.py"
SEEDED = _paths.FIXTURES / "seeded"
CLEAN, DEFECTIVE = SEEDED / "clean", SEEDED / "defective"
MANIFEST = json.loads((SEEDED / "manifest.json").read_text(encoding="utf-8"))


# The tail of row R1.2 in the clean fixture: a contested comment with no manuscript change.
WAIVED_TAIL = ('status: waived\n    waived_by: "corresponding author, 2026-11-09"\n'
               '    waived_risk: "Reviewer 1 may repeat the request in round two."\n'
               '    flagged_to_editor: true\n    response_paragraph: "R1.2"')


def codes(findings):
    return {f["code"] for f in findings}


class PaperDir(unittest.TestCase):
    """A scratch copy of the clean `.paper/` that a test can break in one place."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.paper = Path(self.tmp.name) / ".paper"
        shutil.copytree(CLEAN / ".paper", self.paper)

    def tearDown(self):
        self.tmp.cleanup()

    def edit(self, name, old, new):
        p = self.paper / name
        text = p.read_text(encoding="utf-8")
        self.assertEqual(text.count(old), 1, f"{old!r} must occur once in {name}")
        p.write_text(text.replace(old, new), encoding="utf-8")

    def audit(self):
        return audit(self.paper, None)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestChangeVocabulary(PaperDir):
    """The change ledger and the triage guide use one list of comment types, one list of
    severities and one list of statuses. A value outside a list is a finding."""

    def test_comment_type_outside_the_list_is_reported(self):
        self.edit("changes.yml", "    type: claim\n", "    type: trivial\n")
        self.assertIn("CHANGE_TYPE_INVALID", codes(self.audit()))

    def test_every_triage_type_is_accepted(self):
        for kind in ("misreading", "missing information", "method", "evidence", "claim",
                     "framing", "presentation", "language", "out of scope", "wrong"):
            with self.subTest(type=kind):
                self.setUp()
                self.edit("changes.yml", "    type: claim\n", f"    type: {kind}\n")
                self.assertNotIn("CHANGE_TYPE_INVALID", codes(self.audit()))
                self.tearDown()

    def test_needs_evidence_claim_worded_with_indicates_exceeds_its_status(self):
        self.edit("claims.yml", "    status: supported", "    status: needs evidence")
        self.assertIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_severity_outside_the_list_is_reported(self):
        self.edit("changes.yml", "    severity: blocking\n", "    severity: major\n")
        self.assertIn("CHANGE_SEVERITY_INVALID", codes(self.audit()))

    def test_promised_row_in_a_conference_rebuttal_is_settled(self):
        self.edit("changes.yml", "decision: major_revision", "decision: rebuttal")
        self.edit("changes.yml", '    status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  '    status: promised\n    verified_on: null\n    response_paragraph: "R1.1"')
        found = codes(self.audit())
        self.assertFalse(found & {"CHANGE_STATUS_INVALID", "CHANGE_OPEN", "CHANGE_PROMISED_OUTSIDE_REBUTTAL"},
                         found)

    def test_promised_row_outside_a_rebuttal_is_reported(self):
        self.edit("changes.yml", '    status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  '    status: promised\n    verified_on: null\n    response_paragraph: "R1.1"')
        self.assertIn("CHANGE_PROMISED_OUTSIDE_REBUTTAL", codes(self.audit()))

    def test_promised_row_needs_done_when(self):
        self.edit("changes.yml", "decision: major_revision", "decision: rebuttal")
        self.edit("changes.yml", '    status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  '    status: promised\n    verified_on: null\n    response_paragraph: "R1.1"')
        self.edit("changes.yml", '    done_when: "The Abstract and the Conclusion each name the four climates and the south orientation."\n', "")
        self.assertIn("CHANGE_NO_DONE_WHEN", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestSeededPair(unittest.TestCase):
    def test_clean_copy_has_no_findings(self):
        self.assertEqual(audit(CLEAN / ".paper", None), [])

    def test_verb_exceeds_status(self):
        self.assertIn("CLAIM_VERB_EXCEEDS_STATUS", codes(audit(DEFECTIVE / ".paper", None)))

    def test_done_without_verified_on(self):
        self.assertIn("CHANGE_DONE_NOT_VERIFIED", codes(audit(DEFECTIVE / ".paper", None)))

    def test_every_ledger_defect_in_manifest_is_reported(self):
        expected = {r["expected_code"] for r in MANIFEST
                    if r["expected_detector"] == "check_ledger" and not r["needs_manuscript"]}
        self.assertTrue(expected)
        self.assertTrue(expected <= codes(audit(DEFECTIVE / ".paper", None)))

    def test_findings_name_the_row(self):
        f = [x for x in audit(DEFECTIVE / ".paper", None)
             if x["code"] == "CLAIM_VERB_EXCEEDS_STATUS"][0]
        self.assertEqual((f["file"], f["id"]), ("claims.yml", "C2"))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestClaimRules(PaperDir):
    def test_invalid_status(self):
        self.edit("claims.yml", "status: supported", "status: mostly supported")
        self.assertIn("CLAIM_STATUS_INVALID", codes(self.audit()))

    def test_empty_evidence_on_supported_claim(self):
        self.edit("claims.yml", 'evidence:\n      - "Fig. 2"\n      - "Table 1"', "evidence: []")
        self.assertIn("CLAIM_EVIDENCE_EMPTY", codes(self.audit()))

    def test_gap_without_reason(self):
        self.edit("claims.yml",
                  '    gap_reason: "No grid-convergence test was run, and the simulation '
                  'allocation has ended, so none can be produced for this paper. Stated as a '
                  'limitation in the Discussion."\n', "")
        self.assertIn("CLAIM_GAP_NO_REASON", codes(self.audit()))

    def test_row_without_id_has_its_own_code(self):
        self.edit("claims.yml", "  - id: C2\n    text:", "  - text:")
        found = codes(self.audit())
        self.assertIn("CLAIM_ID_MISSING", found)
        self.assertNotIn("CLAIM_ID_DUPLICATE", found)

    def test_claim_verb_change_without_decision(self):
        self.edit("claims.yml", "    load_bearing: true\n",
                  '    load_bearing: true\n    verb_change:\n      before: "suggests"\n      after: "indicates"\n')
        self.assertIn("CLAIM_VERB_NO_DECISION", codes(self.audit()))

    def test_claim_verb_change_keep_with_reason_is_accepted(self):
        self.edit("claims.yml", "    load_bearing: true\n",
                  '    load_bearing: true\n    verb_change:\n      before: "suggests"\n      after: "indicates"\n'
                  '      decision: keep\n      reason: "Table 1 added in revision."\n')
        self.assertEqual(self.audit(), [])

    def test_duplicate_id(self):
        self.edit("claims.yml", "- id: C2", "- id: C1")
        self.assertIn("CLAIM_ID_DUPLICATE", codes(self.audit()))

    def test_empty_location(self):
        self.edit("claims.yml", 'location: ["Methods L4"]', "location: []")
        self.assertIn("CLAIM_LOCATION_EMPTY", codes(self.audit()))

    def test_load_bearing_gap(self):
        self.edit("claims.yml", "load_bearing: false", "load_bearing: true")
        self.assertIn("CLAIM_LOAD_BEARING_GAP", codes(self.audit()))

    def test_invalid_analysis_status(self):
        self.edit("claims.yml", "    load_bearing: true\n",
                  "    load_bearing: true\n    analysis_status: confirmatory-ish\n")
        self.assertIn("CLAIM_ANALYSIS_STATUS_INVALID", codes(self.audit()))

    def test_valid_analysis_status_is_accepted(self):
        self.edit("claims.yml", "    load_bearing: true\n",
                  "    load_bearing: true\n    analysis_status: post hoc\n")
        self.assertEqual(self.audit(), [])

    def test_absent_analysis_status_is_not_a_finding(self):
        self.assertNotIn("CLAIM_ANALYSIS_STATUS_INVALID", codes(self.audit()))

    def test_evidence_names_unknown_figure(self):
        self.edit("claims.yml", '- "Fig. 2"', '- "Fig. 7"')
        self.assertIn("CLAIM_EVIDENCE_UNKNOWN_FIGURE", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestFigureGapRules(PaperDir):
    def test_invalid_figure_status(self):
        self.edit("figures.yml", 'key_numbers: []\n    supports_claims: []\n    cited_in: ["Sec. 2"]\n    status: final',
                  'key_numbers: []\n    supports_claims: []\n    cited_in: ["Sec. 2"]\n    status: done')
        self.assertIn("FIG_STATUS_INVALID", codes(self.audit()))

    def test_regenerate_blocks(self):
        self.edit("figures.yml", 'cited_in: ["Sec. 2"]\n    status: final',
                  'cited_in: ["Sec. 2"]\n    status: regenerate')
        self.assertIn("FIG_REGENERATE", codes(self.audit()))

    def test_duplicate_figure_id(self):
        self.edit("figures.yml", '- id: "Tab1"', '- id: "Fig2"')
        self.assertIn("FIG_ID_DUPLICATE", codes(self.audit()))

    def test_supports_unknown_claim(self):
        self.edit("figures.yml", 'key_numbers: []\n    supports_claims: []',
                  'key_numbers: []\n    supports_claims: ["C9"]')
        self.assertIn("FIG_SUPPORTS_UNKNOWN_CLAIM", codes(self.audit()))

    def test_unverified_gap_linked_to_supported_claim(self):
        self.edit("gap.yml", "status: verified", "status: unverified")
        self.assertIn("GAP_UNVERIFIED_LINKED", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestChangeRules(PaperDir):
    def test_invalid_change_status(self):
        self.edit("changes.yml", WAIVED_TAIL,
                  'status: finished\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.2"')
        self.assertIn("CHANGE_STATUS_INVALID", codes(self.audit()))

    def test_concede_done_without_change(self):
        self.edit("changes.yml",
                  'manuscript_change: "Bounded the Abstract and Conclusion to the simulated '
                  'climates and orientation."', "manuscript_change: null")
        self.assertIn("CHANGE_CONCEDE_NO_CHANGE", codes(self.audit()))

    def test_contest_without_reason(self):
        self.edit("changes.yml",
                  'reason: "A north window does not trigger the glare-led controller, so the '
                  'comparison would have no treatment."', "reason: null")
        self.assertIn("CHANGE_CONTEST_NO_REASON", codes(self.audit()))

    def test_waived_without_who_and_risk(self):
        self.edit("changes.yml", '    waived_by: "corresponding author, 2026-11-09"\n', "")
        self.assertIn("CHANGE_WAIVED_INCOMPLETE", codes(self.audit()))

    def test_open_row(self):
        self.edit("changes.yml", WAIVED_TAIL,
                  'status: open\n    verified_on: null\n    response_paragraph: "R1.2"')
        self.assertIn("CHANGE_OPEN", codes(self.audit()))

    ROW2_TAIL = WAIVED_TAIL

    def test_unsettled_concede_row_without_done_when(self):
        self.edit("changes.yml", '    status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  '    status: open\n    verified_on: null\n    response_paragraph: "R1.1"')
        self.edit("changes.yml", '    done_when: "The Abstract and the Conclusion each name the four climates and the south orientation."\n', "")
        self.assertIn("CHANGE_NO_DONE_WHEN", codes(self.audit()))

    def test_settled_concede_row_without_done_when_is_flagged_too(self):
        # Changed from "is not flagged": done_when is required on every concede row.
        self.edit("changes.yml", '    done_when: "The Abstract and the Conclusion each name the four climates and the south orientation."\n', "")
        self.assertIn("CHANGE_NO_DONE_WHEN", codes(self.audit()))

    def test_partial_without_reason(self):
        self.edit("changes.yml", self.ROW2_TAIL,
                  'status: partial\n    verified_on: null\n    response_paragraph: "R1.2"')
        self.assertIn("CHANGE_PARTIAL_NO_REASON", codes(self.audit()))

    def test_partial_with_reason_is_accepted(self):
        self.edit("changes.yml", self.ROW2_TAIL,
                  'status: partial\n    partial_reason: "East case added; north case not run."\n'
                  '    verified_on: null\n    response_paragraph: "R1.2"')
        self.assertNotIn("CHANGE_PARTIAL_NO_REASON", codes(self.audit()))

    def test_made_worse_is_valid_but_open(self):
        self.edit("changes.yml", self.ROW2_TAIL,
                  'status: made worse\n    verified_on: null\n    response_paragraph: "R1.2"')
        found = codes(self.audit())
        self.assertNotIn("CHANGE_STATUS_INVALID", found)
        self.assertIn("CHANGE_OPEN", found)

    def test_verb_change_without_decision(self):
        self.edit("changes.yml", self.ROW2_TAIL, self.ROW2_TAIL +
                  '\n    claim_verb_change:\n      - claim: C1\n        before: "indicates"\n        after: "shows"')
        self.assertIn("CHANGE_VERB_NO_DECISION", codes(self.audit()))

    def test_verb_change_keep_needs_a_reason(self):
        self.edit("changes.yml", self.ROW2_TAIL, self.ROW2_TAIL +
                  '\n    claim_verb_change:\n      - claim: C1\n        before: "indicates"\n        after: "shows"\n        decision: keep')
        self.assertIn("CHANGE_VERB_NO_DECISION", codes(self.audit()))

    def test_verb_change_restore_is_accepted(self):
        self.edit("changes.yml", self.ROW2_TAIL, self.ROW2_TAIL +
                  '\n    claim_verb_change:\n      - claim: C1\n        before: "indicates"\n        after: "shows"\n        decision: restore')
        self.assertEqual(self.audit(), [])

    def test_verb_change_pause_is_open(self):
        self.edit("changes.yml", self.ROW2_TAIL, self.ROW2_TAIL +
                  '\n    claim_verb_change:\n      - claim: C1\n        before: "indicates"\n        after: "shows"\n        decision: pause')
        self.assertIn("CHANGE_OPEN", codes(self.audit()))

    def test_conflict_type_invalid(self):
        self.edit("changes.yml", "conflicts: []",
                  'conflicts:\n  - between: ["R1.1", "R1.2"]\n    type: argument\n    description: "x"\n    resolution: "y"')
        self.assertIn("CONFLICT_TYPE_INVALID", codes(self.audit()))

    def test_conflict_type_valid(self):
        self.edit("changes.yml", "conflicts: []",
                  'conflicts:\n  - between: ["R1.1", "R1.2"]\n    type: direction\n    description: "x"\n    resolution: "y"')
        self.assertEqual(self.audit(), [])

    def test_affects_unknown_claim(self):
        self.edit("changes.yml", 'affects_claims: ["C1"]', 'affects_claims: ["C8"]')
        self.assertIn("CHANGE_AFFECTS_UNKNOWN", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestBrokenFiles(PaperDir):
    def test_empty_yaml_file_is_unparseable_not_clean(self):
        (self.paper / "claims.yml").write_text("", encoding="utf-8")
        self.assertIn("FILE_UNPARSEABLE", codes(self.audit()))

    def test_broken_yaml_does_not_crash(self):
        (self.paper / "claims.yml").write_text("claims: [: :", encoding="utf-8")
        self.assertIn("FILE_UNPARSEABLE", codes(self.audit()))

    def test_rows_that_are_not_mappings(self):
        (self.paper / "figures.yml").write_text("figures:\n  - just a string\n", encoding="utf-8")
        self.assertIn("FILE_UNPARSEABLE", codes(self.audit()))

    def test_misspelled_top_level_key_is_not_clean(self):
        self.edit("claims.yml", "\nclaims:\n", "\nclaim:\n")
        f = [x for x in self.audit() if x["code"] == "FILE_UNPARSEABLE"]
        self.assertEqual([x["file"] for x in f], ["claims.yml"])

    def test_malformed_conflicts_block_is_reported(self):
        self.edit("changes.yml", "conflicts: []", "conflicts: nonsense")
        self.assertIn("FILE_UNPARSEABLE", codes(self.audit()))

    def test_never_use_given_as_a_single_string(self):
        self.edit("terms.yml", 'never_use: ["glare index", "glare probability index"]',
                  'never_use: "glare index"')
        self.assertEqual(audit(self.paper, CLEAN / "manuscript.tex"), [])

    def test_provides_evidence_is_not_a_strong_verb(self):
        # Changed: the row is now `needs evidence`, because a gap row carries no claim verb.
        self.edit("claims.yml", '    status: gap\n    evidence: []\n    verb: "assume"',
                  '    status: needs evidence\n    evidence: []\n    verb: "provides evidence that"')
        self.assertNotIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_proves_is_a_strong_verb(self):
        self.edit("claims.yml", 'verb: "assume"', 'verb: "proves"')
        self.assertIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_absent_optional_file_is_not_a_finding_but_is_listed(self):
        (self.paper / "gap.yml").unlink()
        self.assertEqual(self.audit(), [])
        self.assertIn("gap.yml", check_ledger.not_checked(self.paper))


DOCX_HEAD = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.'
             'openxmlformats.org/wordprocessingml/2006/main"><w:body>')


def make_docx(path, paragraphs):
    import zipfile
    body = "".join(f"<w:p><w:r><w:t>{p}</w:t></w:r></w:p>" for p in paragraphs)
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("word/document.xml", DOCX_HEAD + body + "</w:body></w:document>")


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestNumericTrace(PaperDir):
    def write_tex(self, text):
        p = Path(self.tmp.name) / "m.tex"
        p.write_text(text, encoding="utf-8")
        return p

    def test_clean_copy_with_manuscript_has_no_findings(self):
        self.assertEqual(audit(CLEAN / ".paper", CLEAN / "manuscript.tex"), [])

    def test_abstract_number_differs_from_key_numbers(self):
        f = audit(DEFECTIVE / ".paper", DEFECTIVE / "manuscript.tex")
        hits = [x for x in f if x["code"] == "NUMBER_NOT_IN_LEDGER"]
        self.assertEqual([(x["id"], "212 lx" in x["message"]) for x in hits], [("abstract", True)])

    def test_key_number_never_quoted(self):
        f = audit(DEFECTIVE / ".paper", DEFECTIVE / "manuscript.tex")
        hits = [x for x in f if x["code"] == "KEY_NUMBER_NOT_IN_PROSE"]
        self.assertEqual([(x["id"], "0.29" in x["message"]) for x in hits], [("Tab1", True)])

    def test_every_manifest_defect_for_check_ledger_is_reported(self):
        expected = {r["expected_code"] for r in MANIFEST if r["expected_detector"] == "check_ledger"}
        self.assertTrue(expected <= codes(audit(DEFECTIVE / ".paper", DEFECTIVE / "manuscript.tex")))

    def test_methods_parameters_are_not_flagged(self):
        f = audit(self.paper, CLEAN / "manuscript.tex")
        self.assertNotIn("NUMBER_NOT_IN_LEDGER", codes(f))

    def test_missing_section_is_not_checked(self):
        m = self.write_tex(r"\begin{abstract}Core illuminance was \SI{215}{\lux}.\end{abstract}"
                           r"\section{Results}It was \SI{215}{\lux} and \SI{148}{\lux}; sDA "
                           r"41\,\% and 58\,\%; DGP 0.38 and 0.31.")
        f = audit(self.paper, m)
        missing = {x["id"] for x in f if x["code"] == "SECTION_NOT_CHECKED"}
        self.assertEqual(missing, {"introduction", "discussion", "conclusion"})

    def test_missing_results_section_stops_the_trace(self):
        m = self.write_tex(r"\begin{abstract}Core illuminance was \SI{999}{\lux}.\end{abstract}")
        f = audit(self.paper, m)
        self.assertIn(("SECTION_NOT_CHECKED", "results"), {(x["code"], x["id"]) for x in f})
        self.assertNotIn("NUMBER_NOT_IN_LEDGER", codes(f))

    def test_missing_input_file_is_reported(self):
        m = self.write_tex((CLEAN / "manuscript.tex").read_text(encoding="utf-8")
                           + "\n\\input{appendix-gone}\n")
        f = audit(self.paper, m)
        self.assertIn(("INPUT_NOT_FOUND", "appendix-gone"), {(x["code"], x["id"]) for x in f})

    def test_never_use_term_in_manuscript(self):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8").replace(
            "Daylight glare probability (DGP) was computed",
            "Daylight glare probability (DGP), a glare index, was computed")
        f = audit(self.paper, self.write_tex(text))
        self.assertEqual([(x["code"], x["file"]) for x in f],
                         [("TERM_NEVER_USE_PRESENT", "terms.yml")])

    def test_never_use_term_inside_quotation_is_not_flagged(self):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8").replace(
            "Daylight glare probability (DGP) was computed",
            "Daylight glare probability (DGP), which older work calls a ``glare index'', was computed")
        self.assertEqual(audit(self.paper, self.write_tex(text)), [])

    def test_docx_manuscript_is_traced(self):
        m = Path(self.tmp.name) / "m.docx"
        make_docx(m, ["Abstract", "Core illuminance was 212 lx with the controller.",
                      "1. Introduction", "Shading matters.",
                      "2. Results", "Core illuminance was 215 lx and 148 lx. sDA was 41 % and "
                      "58 %. DGP was 0.38 and 0.31.",
                      "3. Discussion", "The gain was real.", "4. Conclusion", "It worked."])
        f = audit(self.paper, m)
        self.assertEqual([(x["code"], x["id"]) for x in f], [("NUMBER_NOT_IN_LEDGER", "abstract")])

    def test_year_ranges_and_numeric_citations_are_not_flagged(self):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8").replace(
            "This indicates that glare control",
            "Earlier work from 2019-2021 [12-14] agrees (pp. 12-15). This indicates that glare control")
        self.assertEqual(audit(self.paper, self.write_tex(text)), [])

    def test_number_restated_from_methods_is_not_flagged(self):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8").replace(
            "This indicates that glare control",
            "The grid was \\SI{0.5}{\\metre} and Radiance~5.4 was used. This indicates that glare control")
        self.assertEqual(audit(self.paper, self.write_tex(text)), [])

    def test_unreadable_manuscript_is_not_checked_not_a_crash(self):
        bad = Path(self.tmp.name) / "broken.docx"
        bad.write_text("this is not a zip file", encoding="utf-8")
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.paper), "--manuscript", str(bad)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 3)
        self.assertIn("not checked", p.stdout)

    def test_parent_folder_of_paper_dir_is_accepted(self):
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.paper.parent)],
                           capture_output=True, text=True)
        self.assertEqual(p.returncode, 0)
        self.assertIn(".paper", p.stdout)

    def test_unread_section_gives_exit_3_not_0(self):
        m = self.write_tex((CLEAN / "manuscript.tex").read_text(encoding="utf-8").replace(
            r"\section{Conclusion}", r"\section{Outlook}"))
        p = subprocess.run([sys.executable, str(SCRIPT), str(self.paper), "--manuscript", str(m)],
                           capture_output=True, text=True)
        self.assertIn("conclusion", p.stdout)
        self.assertEqual(p.returncode, 3)       # nothing wrong was found, and not all was read


def run_cli(*args):
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestMissingFilesMeanNotChecked(PaperDir):
    """Fault 1. Required by the consistency rules: claims.yml (1, 2, 5, 6, 9), figures.yml
    (1, 2, 3, 4), terms.yml (7, 8), gap.yml (9, 10). Optional by design: changes.yml (exists
    only after peer review) and venue.yml (only with a corpus; the script does not read it)."""

    def test_only_claims_yml_present_exits_3_and_names_the_rules(self):
        for name in ("figures.yml", "terms.yml", "gap.yml", "changes.yml"):
            (self.paper / name).unlink()
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 3, p.stdout)
        for line in ("figures.yml is absent", "rules 1, 2, 3, 4 ", "terms.yml is absent",
                     "rules 7, 8 ", "gap.yml is absent", "rules 9, 10 "):
            self.assertIn(line, p.stdout)

    def test_each_required_file_absent_alone_exits_3(self):
        for name, rules in (("figures.yml", "rules 1, 2, 3, 4"), ("terms.yml", "rules 7, 8"),
                            ("gap.yml", "rules 9, 10")):
            with self.subTest(name):
                (self.paper / name).rename(self.paper / (name + ".off"))
                try:
                    p = run_cli(str(self.paper))
                finally:
                    (self.paper / (name + ".off")).rename(self.paper / name)
                self.assertEqual(p.returncode, 3, p.stdout)
                self.assertIn(rules, p.stdout)

    def test_claims_yml_absent_names_its_rules(self):
        (self.paper / "claims.yml").unlink()
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 3)
        self.assertIn("rules 1, 2, 5, 6, 9", p.stdout)

    def test_changes_yml_absent_is_optional_and_does_not_cause_exit_3(self):
        (self.paper / "changes.yml").unlink()
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("changes.yml", p.stdout)
        self.assertIn("optional", p.stdout)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestFieldWrittenAsString(PaperDir):
    """Fault 2. The guide writes `evidence`, `supports_claims`, `linked_claims` as lists. A
    bare string is a schema fault (FIELD_NOT_LIST), and is still read as one item."""

    def test_evidence_string_is_a_schema_fault_and_read_as_one_item(self):
        self.edit("claims.yml", 'evidence:\n      - "Fig. 2"\n      - "Table 1"',
                  'evidence: "Fig. 9"')
        f = self.audit()
        self.assertEqual([(x["file"], x["id"]) for x in f if x["code"] == "FIELD_NOT_LIST"],
                         [("claims.yml", "C1")])
        unknown = [x for x in f if x["code"] == "CLAIM_EVIDENCE_UNKNOWN_FIGURE"]
        self.assertEqual(len(unknown), 1)
        self.assertIn("Fig9", unknown[0]["message"])

    def test_supports_claims_string_is_not_split_into_characters(self):
        self.edit("figures.yml",
                  'plot_core.py"\n    caption_gist: "Mean core illuminance by shading mode, '
                  'averaged over four climates."\n    key_numbers:\n      - "core illuminance 215 lx with the controller, 148 lx with fixed blinds"\n    supports_claims: ["C1"]',
                  'plot_core.py"\n    caption_gist: "Mean core illuminance by shading mode, '
                  'averaged over four climates."\n    key_numbers:\n      - "core illuminance 215 lx with the controller, 148 lx with fixed blinds"\n    supports_claims: "C1"')
        found = codes(self.audit())
        self.assertIn("FIELD_NOT_LIST", found)
        self.assertNotIn("FIG_SUPPORTS_UNKNOWN_CLAIM", found)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule8Symbols(PaperDir):
    def symbols(self, rows):
        self.edit("terms.yml", "symbols: []", "symbols:\n" + rows)

    def test_one_symbol_two_meanings(self):
        self.symbols('  - symbol: "E"\n    means: "illuminance"\n'
                     '  - symbol: "E"\n    means: "energy use intensity"\n')
        f = [x for x in self.audit() if x["code"] == "SYMBOL_TWO_MEANINGS"]
        self.assertEqual([x["id"] for x in f], ["E"])

    def test_one_quantity_two_symbols(self):
        self.symbols('  - symbol: "E"\n    means: "illuminance"\n'
                     '  - symbol: "L_v"\n    means: "Illuminance"\n')
        self.assertIn("QUANTITY_TWO_SYMBOLS", codes(self.audit()))

    def test_symbol_repeated_with_same_meaning_is_fine(self):
        self.symbols('  - symbol: "E"\n    means: "illuminance"\n'
                     '  - symbol: "E"\n    means: "illuminance"\n')
        self.assertEqual(self.audit(), [])

    def test_terms_row_symbol_conflicts_with_symbols_register(self):
        self.edit("terms.yml", "    abbrev: \"sDA\"\n    defined_at: \"Sec. 2\"\n    unit: \"%\"\n    symbol: null",
                  "    abbrev: \"sDA\"\n    defined_at: \"Sec. 2\"\n    unit: \"%\"\n    symbol: \"E\"")
        self.symbols('  - symbol: "E"\n    means: "illuminance"\n')
        self.assertIn("SYMBOL_TWO_MEANINGS", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule10Dissent(PaperDir):
    ENTRY = '    dissenting_studies: ["Okafor 2020 \u2014 reports no effect; address in Discussion"]'

    def setUp(self):
        super().setUp()
        self.edit("gap.yml", "    dissenting_studies: []", self.ENTRY)

    def tex(self, discussion_extra="", drop_discussion=False):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8")
        if drop_discussion:
            text = text.replace(r"\section{Discussion}", r"\section{Outlook}")
        text = text.replace("The finding is limited", discussion_extra + " The finding is limited")
        p = Path(self.tmp.name) / "m.tex"
        p.write_text(text, encoding="utf-8")
        return p

    def test_dissenting_study_absent_from_discussion_is_reported(self):
        f = audit(self.paper, self.tex())
        self.assertEqual([(x["code"], x["id"]) for x in f if x["code"] == "DISSENT_NOT_IN_DISCUSSION"],
                         [("DISSENT_NOT_IN_DISCUSSION", "G1")])

    def test_cited_only_in_introduction_is_not_enough(self):
        # the clean Introduction already cites okafor2020
        self.assertIn("DISSENT_NOT_IN_DISCUSSION", codes(audit(self.paper, self.tex())))

    def test_named_in_discussion_passes(self):
        self.assertEqual(audit(self.paper, self.tex("Okafor (2020) found no effect.")), [])

    def test_cited_by_key_in_discussion_passes(self):
        self.assertEqual(audit(self.paper, self.tex(r"Another study differs \cite{okafor2020}.")), [])

    def test_no_discussion_section_is_not_checked(self):
        f = audit(self.paper, self.tex(drop_discussion=True))
        self.assertIn(("RULE_NOT_CHECKED", "rule10"), {(x["code"], x["id"]) for x in f})
        self.assertNotIn("DISSENT_NOT_IN_DISCUSSION", codes(f))

    def test_without_manuscript_output_says_rule_10_not_checked(self):
        p = run_cli(str(self.paper))
        self.assertIn("rule 10", p.stdout)
        self.assertIn("not checked", p.stdout)

    def test_no_dissenting_entries_means_nothing_to_check(self):
        self.edit("gap.yml", self.ENTRY, "    dissenting_studies: []")
        self.assertNotIn("RULE_NOT_CHECKED", codes(audit(self.paper, self.tex())))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule3Integers(PaperDir):
    def tex(self, abstract_old, abstract_new, methods_old=None, methods_new=None, extra=""):
        text = (CLEAN / "manuscript.tex").read_text(encoding="utf-8")
        text = text.replace(abstract_old, abstract_new)
        if methods_old:
            text = text.replace(methods_old, methods_new)
        text = text.replace("This indicates that glare control", extra + " This indicates that glare control")
        p = Path(self.tmp.name) / "m.tex"
        p.write_text(text, encoding="utf-8")
        return p

    def setup_key_integer(self):
        self.edit("figures.yml", 'key_numbers: []\n    supports_claims: []',
                  'key_numbers:\n      - "24 geometries"\n    supports_claims: []')

    def test_bare_integer_in_abstract_that_differs_from_key_number(self):
        self.setup_key_integer()
        m = self.tex("in a side-lit office. With", "in a side-lit office of 25 geometries. With",
                     "The office is", "The 24 geometries share an office that is")
        hits = [x for x in audit(self.paper, m) if x["code"] == "NUMBER_NOT_IN_LEDGER"]
        self.assertEqual([(x["id"], "25" in x["message"]) for x in hits], [("abstract", True)])

    def test_matching_bare_integer_is_accepted(self):
        self.setup_key_integer()
        m = self.tex("in a side-lit office. With", "in a side-lit office of 24 geometries. With",
                     "The office is", "The 24 geometries share an office that is")
        self.assertEqual(audit(self.paper, m), [])

    def test_key_number_integer_missing_from_prose_is_reported(self):
        self.setup_key_integer()
        f = audit(self.paper, CLEAN / "manuscript.tex")
        self.assertIn("KEY_NUMBER_NOT_IN_PROSE", codes(f))

    def test_years_section_numbers_lists_and_citations_are_not_flagged(self):
        extra = ("Since 2021 [12] and [3, 4] (Smith et al., 2019), Section 3 and Sec. 2.1 "
                 "and Fig.~2 agree; see pp. 12-15, 3D models, and the 2nd study. "
                 "Run on 5 March 2026.\n\n1. First point\n2) Second point\n")
        self.assertEqual(audit(self.paper, self.tex("x", "x", extra=extra)), [])


class TestPython39(unittest.TestCase):
    def test_script_compiles_on_system_python3(self):
        py = "/usr/bin/python3"
        if not os.path.exists(py):
            self.skipTest("no /usr/bin/python3")
        with tempfile.TemporaryDirectory() as d:
            p = subprocess.run([py, "-m", "py_compile", str(SCRIPT)],
                               capture_output=True, text=True,
                               env=dict(os.environ, PYTHONPYCACHEPREFIX=d))
        self.assertEqual(p.returncode, 0, p.stderr)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestHonestOutput(PaperDir):
    def test_clean_run_lists_what_the_script_does_not_check(self):
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 0)
        self.assertIn("not checked by this script", p.stdout)
        self.assertIn("rule 10", p.stdout)


DONE_WHEN = ('    done_when: "The Abstract and the Conclusion each name the four climates and the '
             'south orientation."\n')


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestChangeLedgerCompleteness(PaperDir):
    """Rules of change-ledger-file.md that the script once skipped."""

    def test_clean_fixture_is_clean_under_the_new_rules(self):
        self.assertEqual(self.audit(), [])

    def test_duplicate_id(self):
        self.edit("changes.yml", "  - id: R1.2\n", "  - id: R1.1\n")
        self.assertIn("CHANGE_ID_DUPLICATE", codes(self.audit()))

    def test_missing_id(self):
        self.edit("changes.yml", "  - id: R1.2\n", "  - reviewer: 1\n")
        self.assertIn("CHANGE_ID_MISSING", codes(self.audit()))

    def test_decision_outside_the_three_values(self):
        for bad in ("partial", "accept", "concede (proposed)"):
            with self.subTest(bad):
                self.setUp()
                self.edit("changes.yml", "    decision: concede\n", f"    decision: {bad}\n")
                self.assertIn("CHANGE_DECISION_INVALID", codes(self.audit()))
                self.tearDown()

    def test_missing_decision(self):
        self.edit("changes.yml", "    decision: concede\n", "")
        self.assertIn("CHANGE_DECISION_INVALID", codes(self.audit()))

    def test_partially_concede_is_accepted(self):
        self.edit("changes.yml", "    decision: concede\n", "    decision: partially concede\n")
        self.assertNotIn("CHANGE_DECISION_INVALID", codes(self.audit()))

    def test_misspelt_decision_does_not_switch_off_the_done_when_check(self):
        self.edit("changes.yml", "    decision: concede\n", "    decision: accept\n")
        self.edit("changes.yml", DONE_WHEN, "")
        found = codes(self.audit())
        self.assertIn("CHANGE_DECISION_INVALID", found)

    def test_proposed_decision_is_reported(self):
        self.edit("changes.yml", "    decision: concede\n",
                  "    decision: concede\n    decision_confirmed: false\n")
        f = [x for x in self.audit() if x["code"] == "CHANGE_DECISION_PROPOSED"]
        self.assertEqual([x["id"] for x in f], ["R1.1"])

    def test_confirmed_decision_is_not_reported(self):
        self.edit("changes.yml", "    decision: concede\n",
                  "    decision: concede\n    decision_confirmed: true\n")
        self.assertNotIn("CHANGE_DECISION_PROPOSED", codes(self.audit()))

    def test_done_when_is_required_whatever_the_status(self):
        done = 'status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"'
        waived = ('status: waived\n    waived_by: "x"\n    waived_risk: "y"\n'
                  '    flagged_to_editor: false\n    response_paragraph: "R1.1"')
        for tail in (done, waived):
            with self.subTest(tail.split("\n")[0]):
                self.setUp()
                self.edit("changes.yml", done, tail)
                self.edit("changes.yml", DONE_WHEN, "")
                self.assertIn("CHANGE_NO_DONE_WHEN", codes(self.audit()))
                self.tearDown()

    def test_contest_row_does_not_need_done_when(self):
        self.assertNotIn("CHANGE_NO_DONE_WHEN", codes(self.audit()))

    def test_done_row_with_empty_manuscript_change_whatever_the_decision(self):
        self.edit("changes.yml", WAIVED_TAIL,
                  'status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.2"')
        self.assertIn("CHANGE_DONE_NO_CHANGE", codes(self.audit()))

    def test_done_row_with_empty_location_whatever_the_decision(self):
        self.edit("changes.yml", WAIVED_TAIL,
                  'status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.2"')
        found = [x for x in self.audit() if x["code"] == "CHANGE_LOCATION_EMPTY"]
        self.assertEqual([x["id"] for x in found], ["R1.2"])

    def test_concede_row_done_with_empty_location(self):
        self.edit("changes.yml", 'location: ["Abstract L6", "Conclusion L1"]', "location: []")
        self.assertIn("CHANGE_LOCATION_EMPTY", codes(self.audit()))

    def test_concede_row_partial_with_empty_location(self):
        self.edit("changes.yml", 'location: ["Abstract L6", "Conclusion L1"]', "location: []")
        self.edit("changes.yml", 'status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  'status: partial\n    partial_reason: "x"\n    response_paragraph: "R1.1"')
        self.assertIn("CHANGE_LOCATION_EMPTY", codes(self.audit()))

    def test_open_concede_row_may_have_no_location_yet(self):
        self.edit("changes.yml", 'location: ["Abstract L6", "Conclusion L1"]', "location: []")
        self.edit("changes.yml", 'status: done\n    verified_on: "2026-11-10"\n    response_paragraph: "R1.1"',
                  'status: open\n    response_paragraph: "R1.1"')
        self.assertNotIn("CHANGE_LOCATION_EMPTY", codes(self.audit()))

    def test_row_without_response_paragraph(self):
        self.edit("changes.yml", '    response_paragraph: "R1.2"\n', "")
        f = [x for x in self.audit() if x["code"] == "CHANGE_NO_RESPONSE_PARAGRAPH"]
        self.assertEqual([x["id"] for x in f], ["R1.2"])

    def test_waived_row_needs_a_decision_on_flagged_to_editor(self):
        self.edit("changes.yml", "    flagged_to_editor: true\n", "")
        self.assertIn("CHANGE_WAIVED_INCOMPLETE", codes(self.audit()))

    def test_waived_row_flagged_false_is_a_decision(self):
        self.edit("changes.yml", "    flagged_to_editor: true\n", "    flagged_to_editor: false\n")
        self.assertNotIn("CHANGE_WAIVED_INCOMPLETE", codes(self.audit()))

    def test_editor_row_and_optional_fields_are_accepted(self):
        self.edit("changes.yml", "conflicts: []", '''  - id: E.1
    reviewer: editor
    comment: "Name every request that was not carried out in the cover letter."
    type: presentation
    severity: substantive
    decision: concede
    reason: null
    done_when: "The cover letter lists R1.2 as a point for the editor."
    manuscript_change: null
    location: []
    affects_claims: []
    affects_figures: []
    affects_runs: ["R3"]
    amendment: "A1"
    status: open
    response_paragraph: "E.1"

conflicts: []''')
        found = codes(self.audit())
        self.assertEqual(found, {"CHANGE_OPEN"})

    def test_not_covered_note_lists_the_change_ledger_cross_checks(self):
        p = run_cli(str(self.paper))
        for phrase in ("cross-check 1", "7 (a claim weakened", "8 (a regenerated figure",
                       "9 (every paragraph", "cross-check 10"):
            self.assertIn(phrase, p.stdout)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestChangesWithoutClaims(PaperDir):
    def test_changes_findings_are_printed_when_claims_yml_is_absent(self):
        (self.paper / "claims.yml").unlink()
        self.edit("changes.yml", "    decision: concede\n", "    decision: accept\n")
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 1, p.stdout)
        self.assertIn("CHANGE_DECISION_INVALID", p.stdout)
        self.assertIn("claims.yml is absent", p.stdout)
        self.assertIn("rules 1, 2, 5, 6, 9", p.stdout)

    def test_clean_changes_without_claims_exits_3(self):
        (self.paper / "claims.yml").unlink()
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 3, p.stdout)
        self.assertIn("claims.yml is absent", p.stdout)
        self.assertIn("0 finding(s)", p.stdout)

    def test_neither_file_exits_3_with_the_old_message(self):
        (self.paper / "claims.yml").unlink()
        (self.paper / "changes.yml").unlink()
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 3)
        self.assertIn("not checked: claims.yml is absent", p.stdout)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestVerbCeilingAndRejected(PaperDir):
    GAP = '    status: gap\n    evidence: []\n    verb: "assume"'

    def test_gap_row_with_a_claim_verb_is_flagged(self):
        self.edit("claims.yml", 'verb: "assume"', 'verb: "suggests"')
        self.assertIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_gap_row_may_state_an_assumption(self):
        for verb in ("assume", "assumes"):
            with self.subTest(verb):
                self.setUp()
                self.edit("claims.yml", 'verb: "assume"', f'verb: "{verb}"')
                self.assertNotIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))
                self.tearDown()

    def test_gap_row_with_no_verb_is_fine(self):
        self.edit("claims.yml", '    verb: "assume"\n', "    verb: null\n")
        self.assertEqual(self.audit(), [])

    def test_rejected_row_is_a_finding(self):
        self.edit("claims.yml", self.GAP, '    status: rejected\n    evidence: ["Fig. 2"]\n    verb: null')
        f = [x for x in self.audit() if x["code"] == "CLAIM_REJECTED"]
        self.assertEqual([x["id"] for x in f], ["C2"])

    def test_rejected_row_with_any_verb_exceeds_its_status(self):
        self.edit("claims.yml", self.GAP, '    status: rejected\n    evidence: ["Fig. 2"]\n    verb: "shows"')
        self.assertIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_needs_evidence_allows_suggests(self):
        self.edit("claims.yml", self.GAP, '    status: needs evidence\n    evidence: []\n    verb: "suggests"')
        self.assertNotIn("CLAIM_VERB_EXCEEDS_STATUS", codes(self.audit()))

    def test_coverage_note_lists_all_six_verbs_and_the_rule(self):
        p = run_cli(str(self.paper))
        for verb in ("shows", "demonstrates", "proves", "establishes", "confirms", "indicates"):
            self.assertIn(verb, p.stdout)
        self.assertIn("assume", p.stdout)
        self.assertIn("rejected", p.stdout)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestDesignLink(PaperDir):
    DESIGN = """version: 1
updated: "2026-08-08"
planned_claims:
  - id: P1
    text: "View direction changes depth more than climate does."
  - id: P2
    text: "A second planned claim."
amendments:
  - id: A1
    date: "2026-08-08"
    timing: post hoc
    kind: choice
    affects: ["P1"]
"""

    def put_design(self, text=None):
        (self.paper / "design.yml").write_text(text or self.DESIGN, encoding="utf-8")

    def link(self, claim_id_line="    status: supported", planned="P1", analysis=None):
        extra = f'    planned_claim: "{planned}"\n'
        if analysis:
            extra += f'    analysis_status: {analysis}\n'
        self.edit("claims.yml", claim_id_line, extra + claim_id_line)

    def test_design_absent_is_silent(self):
        p = run_cli(str(self.paper))
        self.assertNotIn("design.yml", p.stdout)

    def test_unclaimed_planned_claim_is_a_note_not_a_failure(self):
        self.put_design()
        self.link(planned="P1", analysis="post hoc")
        f = self.audit()
        note = [x for x in f if x["code"] == "PLANNED_CLAIM_NOT_YET_CLAIMED"]
        self.assertEqual([x["id"] for x in note], ["P2"])
        p = run_cli(str(self.paper))
        self.assertEqual(p.returncode, 0, p.stdout)
        self.assertIn("P2", p.stdout)
        self.assertIn("not yet claimed", p.stdout)

    def test_post_hoc_choice_claim_not_marked_post_hoc_is_a_finding(self):
        self.put_design()
        self.link(planned="P1", analysis="planned")
        f = [x for x in self.audit() if x["code"] == "CLAIM_POST_HOC_NOT_MARKED"]
        self.assertEqual([x["id"] for x in f], ["C1"])
        self.assertEqual(run_cli(str(self.paper)).returncode, 1)

    def test_claim_without_analysis_status_is_also_a_finding(self):
        self.put_design()
        self.link(planned="P1")
        self.assertIn("CLAIM_POST_HOC_NOT_MARKED", codes(self.audit()))

    def test_claim_marked_post_hoc_is_fine(self):
        self.put_design()
        self.link(planned="P1", analysis="post hoc")
        self.assertNotIn("CLAIM_POST_HOC_NOT_MARKED", codes(self.audit()))

    def test_correction_amendment_does_not_change_the_claim_status(self):
        self.put_design(self.DESIGN.replace("kind: choice", "kind: correction"))
        self.link(planned="P1", analysis="planned")
        self.assertNotIn("CLAIM_POST_HOC_NOT_MARKED", codes(self.audit()))

    def test_changed_before_analysis_amendment_is_not_post_hoc(self):
        self.put_design(self.DESIGN.replace("timing: post hoc", "timing: changed before analysis"))
        self.link(planned="P1", analysis="planned")
        self.assertNotIn("CLAIM_POST_HOC_NOT_MARKED", codes(self.audit()))


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestDocxPartsNotChecked(PaperDir):
    def docx_with_text_box(self):
        import zipfile
        path = Path(self.tmp.name) / "paper.docx"
        ns = ('xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"')
        body = ("<w:p><w:r><w:t>Abstract</w:t></w:r></w:p>"
                "<w:p><w:r><w:t>Plain text.</w:t></w:r>"
                "<w:r><w:txbxContent><w:p><w:r><w:t>9.9 m gaze</w:t></w:r></w:p></w:txbxContent></w:r></w:p>")
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("word/document.xml", f'<?xml version="1.0"?><w:document {ns}><w:body>'
                       f"{body}</w:body></w:document>")
        return path

    def test_skipped_docx_part_is_reported_and_exits_3(self):
        m = self.docx_with_text_box()
        p = run_cli(str(self.paper), "--manuscript", str(m))
        self.assertIn("text boxes", p.stdout)
        self.assertIn("not checked", p.stdout)
        self.assertIn(p.returncode, (1, 3))
        found = audit(self.paper, m)
        self.assertTrue([x for x in found if x["code"] == "PART_NOT_CHECKED"])

    def test_clean_run_with_skipped_part_exits_3_not_0(self):
        m = self.docx_with_text_box()
        found = audit(self.paper, m)
        if not [x for x in found if x["code"] not in check_ledger.INFO_CODES]:
            self.assertEqual(run_cli(str(self.paper), "--manuscript", str(m)).returncode, 3)


class TestCli(unittest.TestCase):
    def run_cli(self, *args, env=None):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True,
                              text=True, env=env)

    def test_no_pyyaml_exits_3(self):
        env = dict(os.environ, PAPER_LEDGER_NO_YAML="1")
        p = self.run_cli(str(CLEAN / ".paper"), env=env)
        self.assertEqual(p.returncode, 3)
        self.assertIn("not checked: install pyyaml", p.stdout)

    def test_missing_paper_dir_exits_3(self):
        p = self.run_cli(str(CLEAN / ".no-such-dir"))
        self.assertEqual(p.returncode, 3)
        self.assertIn("not checked", p.stdout)

    @unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
    def test_clean_exits_0_and_defective_exits_1(self):
        self.assertEqual(self.run_cli(str(CLEAN / ".paper")).returncode, 0)
        self.assertEqual(self.run_cli(str(DEFECTIVE / ".paper")).returncode, 1)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestJsonWriteFailure(PaperDir):
    def test_json_to_a_missing_folder_exits_2_without_a_traceback(self):
        p = run_cli(str(self.paper), "--json", str(Path(self.tmp.name) / "nope" / "o.json"))
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("--json", p.stderr)

    def test_json_to_a_directory_exits_2_without_a_traceback(self):
        p = run_cli(str(self.paper), "--json", self.tmp.name)
        self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
        self.assertNotIn("Traceback", p.stderr)


if __name__ == "__main__":
    unittest.main()
