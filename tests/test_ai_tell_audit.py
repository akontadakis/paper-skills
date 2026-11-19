import os
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

from tests import _paths
from ai_tell_audit import audit_file, read_docx, rhythm_findings

SCRIPT = _paths.SCRIPTS / "ai_tell_audit.py"
# Ten sentences of twelve words each: the even rhythm of a written procedure.
PROCEDURE = " ".join(
    f"The sensor at point {i} was read after the lamp had fully stabilised."
    for i in range(1, 15))


class Audit(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmp.cleanup()

    def rules(self, text, suffix=".txt"):
        p = Path(self.tmp.name) / f"t{suffix}"
        p.write_text(text, encoding="utf-8")
        return [h["rule"] for h in audit_file(p, None)["hits"]]

    def rhythm(self, text):
        p = Path(self.tmp.name) / "r.txt"
        p.write_text(text, encoding="utf-8")
        return audit_file(p, None)["rhythm"]


class TestRhythmSection(Audit):
    def test_procedure_text_is_exempt_from_rhythm(self):
        self.assertEqual(rhythm_findings(self.rhythm(PROCEDURE), section="methods"),
                         ["procedure text — rhythm targets do not apply"])

    def test_same_text_without_flag_is_still_measured(self):
        self.assertTrue(any("spread" in x for x in rhythm_findings(self.rhythm(PROCEDURE))))

    def test_em_dashes_are_still_counted_in_procedure_text(self):
        f = rhythm_findings(self.rhythm(PROCEDURE.replace(" was read", " — the lower one — was read")),
                            section="methods")
        self.assertTrue(any("em dash" in x for x in f))

    def test_cli_accepts_section_flag(self):
        p = Path(self.tmp.name) / "m.txt"
        p.write_text(PROCEDURE, encoding="utf-8")
        out = subprocess.run([sys.executable, str(SCRIPT), str(p), "--section", "methods"],
                             capture_output=True, text=True)
        self.assertEqual(out.returncode, 0)
        self.assertIn("rhythm targets do not apply", out.stdout)


class TestNewPatterns(Audit):
    def test_empty_transition_is_flagged(self):
        self.assertIn("T10c", self.rules("With that in mind, the grid was refined to 0.25 m."))

    def test_building_on_this_is_flagged(self):
        self.assertIn("T10c", self.rules("Building on this foundation, we add a second sensor."))

    def test_building_on_a_named_result_is_a_real_transition(self):
        self.assertNotIn("T10c", self.rules("Building on this result, we refined the grid to 0.25 m."))

    def test_reality_opener_is_flagged(self):
        self.assertIn("T11", self.rules("The reality is that glare varies with the seat."))

    def test_stacked_adjectives_flagged(self):
        self.assertIn("T1c", self.rules(
            "We propose a comprehensive, sophisticated, and innovative framework."))

    def test_noun_triple_not_flagged(self):
        self.assertNotIn("T1c", self.rules(
            "We measured illuminance, luminance, and glare at each seat."))

    def test_two_adjectives_not_flagged_as_stack(self):
        self.assertNotIn("T1c", self.rules("A robust and efficient solver was used."))

    def test_protected_term_alone_not_flagged(self):
        self.assertEqual(self.rules("A robust standard error was computed for each seat."), [])

    def test_methodology_in_running_text_is_flagged(self):
        self.assertIn("T1b", self.rules("Our methodology uses a sensor grid."))

    def test_methodology_in_heading_not_flagged(self):
        self.assertEqual(self.rules("\\section{Methodology}\n", ".tex"), [])
        self.assertEqual(self.rules("## Methodology\n", ".md"), [])


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
M_NS = "http://schemas.openxmlformats.org/officeDocument/2006/math"


class Faults(Audit):
    def hit_lines(self, text, rule, suffix=".tex"):
        p = Path(self.tmp.name) / f"f{suffix}"
        p.write_text(text, encoding="utf-8")
        return [h["line"] for h in audit_file(p, None)["hits"] if h["rule"] == rule]

    def cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)],
                              capture_output=True, text=True)

    def docx(self, body, footnotes=None, name="d.docx"):
        p = Path(self.tmp.name) / name
        head = f'<w:document xmlns:w="{W_NS}" xmlns:m="{M_NS}"><w:body>'
        with zipfile.ZipFile(p, "w") as z:
            z.writestr("word/document.xml", head + body + "</w:body></w:document>")
            if footnotes is not None:
                z.writestr("word/footnotes.xml",
                           f'<w:footnotes xmlns:w="{W_NS}">{footnotes}</w:footnotes>')
        return p

    # 1
    def test_commented_begin_figure_does_not_mask_the_rest(self):
        text = "It is crucial.\n% \\begin{figure}\nIt is pivotal.\nIt is paramount.\n"
        self.assertEqual(self.hit_lines(text, "T1"), [1, 3, 4])

    # 2
    def test_one_line_equation_does_not_mask_the_rest(self):
        text = ("It is crucial.\n\\begin{equation} a=b \\end{equation}\n"
                "It is pivotal.\nIt is paramount.\n")
        self.assertEqual(self.hit_lines(text, "T1"), [1, 3, 4])

    # 3
    def test_caption_text_is_audited_but_the_rest_of_the_float_is_not(self):
        text = ("\\begin{figure}\n a crucial label\n\\caption{A pivotal result,\n"
                "and a vital one.}\n\\end{figure}\nAfter the float.\n")
        self.assertEqual(self.hit_lines(text, "T1"), [3, 4])

    def test_table_caption_is_audited(self):
        text = ("\\begin{table}[t]\n\\caption{Paramount values}\n"
                "\\begin{tabular}{c}crucial\\end{tabular}\n\\end{table}\n")
        self.assertEqual(self.hit_lines(text, "T1"), [2])

    def test_unclosed_environment_is_reported_not_checked(self):
        p = Path(self.tmp.name) / "u.tex"
        p.write_text("Intro.\n\\begin{equation}\na=b\nIt is crucial.\n", encoding="utf-8")
        nc = audit_file(p, None)["not_checked"]
        self.assertTrue(any("equation" in x and "line 2" in x for x in nc), nc)

    # review findings I, J, K
    def test_pdf_is_not_read_as_text_and_is_not_checked(self):
        p = Path(self.tmp.name) / "x.pdf"
        p.write_bytes(b"%PDF-1.4 It is crucial.")
        out = self.cli(p)
        self.assertIn("not checked:", out.stdout)
        self.assertIn("unsupported file type", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_unsupported_file_does_not_hide_a_supported_one(self):
        good = Path(self.tmp.name) / "g.txt"
        good.write_text("It is crucial.", encoding="utf-8")
        pdf = Path(self.tmp.name) / "x.pdf"
        pdf.write_bytes(b"%PDF-1.4")
        out = self.cli(good, pdf)
        self.assertIn("[T1] Tier", out.stdout)
        self.assertIn("x.pdf: unsupported file type", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_invalid_utf8_gets_a_not_checked_note(self):
        p = Path(self.tmp.name) / "l1.txt"
        p.write_bytes("Fine text caf\u00e9.".encode("latin-1"))
        self.assertTrue(any("UTF-8" in x for x in audit_file(p, None)["not_checked"]))
        out = self.cli(p)
        self.assertIn("not checked:", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_valid_utf8_has_no_encoding_note(self):
        p = Path(self.tmp.name) / "u8.txt"
        p.write_text("Fine text caf\u00e9.", encoding="utf-8")
        self.assertEqual(audit_file(p, None)["not_checked"], [])

    def test_em_dash_between_digits_is_a_range_not_an_em_dash(self):
        r = self.rhythm("Sensors 5\u20147 and the years 2019\u20142021 were read, then one \u2014 two.")
        self.assertEqual(r["em_dashes"], 1)

    def test_spaced_double_hyphen_is_an_em_dash_in_text_and_markdown_only(self):
        for suffix, expected in ((".txt", 1), (".md", 1), (".tex", 0)):
            p = Path(self.tmp.name) / f"dd{suffix}"
            p.write_text("The sensor -- the lower one -- was read at 5--7 m.", encoding="utf-8")
            n = audit_file(p, None)["rhythm"]["em_dashes"]
            self.assertEqual(n, expected * 2, suffix)

    def test_text_box_is_skipped_once_and_reported(self):
        box = ("<w:r><mc:AlternateContent xmlns:mc=\"http://schemas.openxmlformats.org/markup-"
               "compatibility/2006\"><mc:Choice><w:txbxContent><w:p><w:r><w:t>Boxed crucial."
               "</w:t></w:r></w:p></w:txbxContent></mc:Choice><mc:Fallback><w:txbxContent><w:p>"
               "<w:r><w:t>Boxed crucial.</w:t></w:r></w:p></w:txbxContent></mc:Fallback>"
               "</mc:AlternateContent></w:r>")
        p = self.docx(f"<w:p><w:r><w:t>Body text.</w:t></w:r>{box}</w:p>")
        text = read_docx(p)
        self.assertNotIn("Boxed", text)
        nc = audit_file(p, None)["not_checked"]
        self.assertTrue(any("text boxes" in x for x in nc), nc)
        out = self.cli(p)
        self.assertIn("text boxes", out.stdout)
        self.assertEqual(out.returncode, 3)

    # 4
    def test_numeric_en_dash_range_is_not_an_em_dash(self):
        r = self.rhythm("Light of 400--700 nm was used, and 1--2 m apart.")
        self.assertEqual(r["em_dashes"], 0)

    def test_triple_hyphen_and_em_dash_are_counted(self):
        r = self.rhythm("One --- two and three \u2014 four.")
        self.assertEqual(r["em_dashes"], 2)

    # 5
    def test_unknown_rule_id_is_an_error_naming_valid_ids(self):
        p = Path(self.tmp.name) / "o.txt"
        p.write_text("Fine text.", encoding="utf-8")
        out = self.cli(p, "--only", "T99")
        self.assertNotEqual(out.returncode, 0)
        msg = out.stderr + out.stdout
        self.assertIn("T99", msg)
        self.assertIn("T10c", msg)
        self.assertNotIn("0 lexical hit", msg)

    def test_known_rule_ids_still_accepted(self):
        p = Path(self.tmp.name) / "o.txt"
        p.write_text("It is crucial.", encoding="utf-8")
        out = self.cli(p, "--only", "T1", "T2")
        self.assertEqual(out.returncode, 0)

    # 6
    def test_protected_term_nearby_does_not_hide_a_different_word(self):
        self.assertIn("T1", self.rules("The key frame was crucial."))

    def test_hit_overlapping_protected_term_is_still_suppressed(self):
        self.assertNotIn("T1b", self.rules("A contrast enhancement step was run."))

    # 7
    def test_docx_tab_becomes_a_space(self):
        p = self.docx("<w:p><w:r><w:t>The</w:t><w:tab/><w:t>crucial step.</w:t></w:r></w:p>")
        self.assertEqual(read_docx(p), "The crucial step.")
        self.assertIn("T1", [h["rule"] for h in audit_file(p, None)["hits"]])

    def test_docx_no_break_hyphen_is_a_hyphen(self):
        p = self.docx("<w:p><w:r><w:t>a cutting</w:t><w:noBreakHyphen/>"
                      "<w:t>edge tool.</w:t></w:r></w:p>")
        self.assertEqual(read_docx(p), "a cutting-edge tool.")

    def test_docx_footnote_text_is_audited(self):
        p = self.docx('<w:p><w:r><w:t>Body.</w:t><w:footnoteReference w:id="2"/></w:r></w:p>',
                      footnotes=f'<w:footnote w:id="2"><w:p><w:r><w:t>It is pivotal.</w:t>'
                                f'</w:r></w:p></w:footnote>')
        self.assertIn("pivotal", read_docx(p))
        self.assertIn("T1", [h["rule"] for h in audit_file(p, None)["hits"]])

    def test_docx_body_is_read_in_document_order_including_tables(self):
        p = self.docx("<w:p><w:r><w:t>First.</w:t></w:r></w:p>"
                      "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>Cell.</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
                      "<w:p><w:r><w:t>Last.</w:t></w:r></w:p>")
        self.assertEqual(read_docx(p).split("\n"), ["First.", "Cell.", "Last."])

    def test_docx_equations_are_reported_not_checked(self):
        p = self.docx("<w:p><w:r><w:t>Text.</w:t></w:r><m:oMath><m:r><m:t>x</m:t></m:r></m:oMath></w:p>")
        nc = audit_file(p, None)["not_checked"]
        self.assertTrue(any("equations" in x for x in nc), nc)
        out = self.cli(p)
        self.assertIn("not checked:", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_unreadable_docx_is_not_checked_never_clean(self):
        p = Path(self.tmp.name) / "bad.docx"
        p.write_bytes(b"not a zip")
        out = self.cli(p)
        self.assertIn("not checked:", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_missing_file_is_not_checked(self):
        good = Path(self.tmp.name) / "g.txt"
        good.write_text("Fine text.", encoding="utf-8")
        out = self.cli(good, Path(self.tmp.name) / "nope.tex")
        self.assertIn("not checked:", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_clean_run_exits_zero_with_nothing_not_checked(self):
        good = Path(self.tmp.name) / "g.txt"
        good.write_text("Fine text.", encoding="utf-8")
        out = self.cli(good)
        self.assertEqual(out.returncode, 0)
        self.assertNotIn("not checked:", out.stdout)

    # 8. Updated: the two bracket forms moved from T0 to their own group P0.
    def test_insert_placeholder_is_group_p0_with_its_line(self):
        text = "Fine.\nThe grid was [insert grid size] metres.\n"
        self.assertEqual(self.hit_lines(text, "P0", ".txt"), [2])
        self.assertEqual(self.hit_lines(text, "T0", ".txt"), [])

    def test_cite_placeholder_is_group_p0_with_its_line(self):
        text = "Fine.\nFine.\nAs shown before [CITE: Smith daylight glare].\n"
        self.assertEqual(self.hit_lines(text, "P0", ".tex"), [3])
        self.assertEqual(self.hit_lines(text, "T0", ".tex"), [])

    def test_p0_says_fill_it_not_delete_it(self):
        p = Path(self.tmp.name) / "p.tex"
        p.write_text("As shown [CITE: Smith glare].\n", encoding="utf-8")
        out = self.cli(p, "--only", "P0").stdout
        self.assertIn("Unresolved placeholder", out)
        self.assertIn("Fill it before submission. Do not delete it.", out)
        self.assertNotIn("Delete it", out)

    def test_true_artefact_stays_in_t0_and_says_delete(self):
        p = Path(self.tmp.name) / "a.txt"
        p.write_text("Fine.\nI hope this helps.\n", encoding="utf-8")
        out = self.cli(p, "--only", "T0").stdout
        self.assertIn("Delete it", out)

    # M-20: a bracket inside a masked region is still reported
    def test_placeholder_in_a_table_cell_is_reported(self):
        text = ("Fine.\n\\begin{table}\n\\begin{tabular}{ll}\nOslo & [insert depth for Oslo] \\\\\n"
                "\\end{tabular}\n\\end{table}\n")
        self.assertEqual(self.hit_lines(text, "P0", ".tex"), [4])

    def test_placeholder_in_math_or_algorithm_is_reported_but_not_in_a_comment(self):
        text = "$x = [insert value]$\n% [insert in a comment]\n"
        self.assertEqual(self.hit_lines(text, "P0", ".tex"), [1])

    # C-7: include targets are followed or reported
    def test_included_file_is_audited_with_its_own_name_and_line(self):
        d = Path(self.tmp.name)
        (d / "sub").mkdir()
        (d / "sub" / "part.tex").write_text("Fine.\nThe value is [insert value].\n",
                                            encoding="utf-8")
        root = d / "root.tex"
        root.write_text("Start.\n\\input{sub/part}\n", encoding="utf-8")
        out = self.cli(root)
        self.assertIn("part.tex:2: [insert value]", out.stdout)
        self.assertNotIn("not checked", out.stdout)

    def test_import_and_include_are_followed(self):
        d = Path(self.tmp.name)
        (d / "sub").mkdir()
        (d / "sub" / "part.tex").write_text("It is crucial.\n", encoding="utf-8")
        (d / "two.tex").write_text("It is crucial too.\n", encoding="utf-8")
        root = d / "root.tex"
        root.write_text("\\import{sub/}{part}\n\\include{two}\n", encoding="utf-8")
        out = self.cli(root).stdout
        self.assertIn("part.tex:1", out)
        self.assertIn("two.tex:1", out)

    def test_missing_include_is_not_checked_and_exits_3(self):
        root = Path(self.tmp.name) / "root.tex"
        root.write_text("Start.\n\\input{gone}\n", encoding="utf-8")
        out = self.cli(root)
        self.assertIn("included file not found: gone", out.stdout)
        self.assertIn("not checked:", out.stdout)
        self.assertEqual(out.returncode, 3)

    def test_include_given_on_the_command_line_is_audited_once(self):
        d = Path(self.tmp.name)
        (d / "part.tex").write_text("It is crucial.\n", encoding="utf-8")
        root = d / "root.tex"
        root.write_text("\\input{part}\n", encoding="utf-8")
        out = self.cli(root, d / "part.tex").stdout
        self.assertEqual(out.count("part.tex:1: crucial"), 1)

    def test_self_including_file_does_not_loop(self):
        root = Path(self.tmp.name) / "loop.tex"
        root.write_text("It is crucial.\n\\input{loop}\n", encoding="utf-8")
        out = self.cli(root)
        self.assertEqual(out.stdout.count("loop.tex:1: crucial"), 1)


@unittest.skipUnless(os.path.exists("/usr/bin/python3"), "no /usr/bin/python3")
class SystemPython(Audit):
    def test_runs_on_system_python(self):
        p = Path(self.tmp.name) / "s.tex"
        p.write_text("It is crucial.\n", encoding="utf-8")
        h = subprocess.run(["/usr/bin/python3", str(SCRIPT), "--help"],
                           capture_output=True, text=True)
        self.assertEqual(h.returncode, 0, h.stderr)
        r = subprocess.run(["/usr/bin/python3", str(SCRIPT), str(p)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("[T1]", r.stdout)


if __name__ == "__main__":
    unittest.main()
