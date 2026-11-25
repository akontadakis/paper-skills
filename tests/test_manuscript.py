import tempfile
import time
import unittest
import zipfile
from pathlib import Path

from tests import _paths  # noqa: F401
from _manuscript import (abbreviations, comparisons, fold, numbers, ranges_in_words,
                         read_manuscript, split_sections, symbols)

DOCX_XML = (
    '<?xml version="1.0" encoding="UTF-8"?>'
    '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
    "<w:body><w:p><w:r><w:t>Abstract</w:t></w:r></w:p>"
    "<w:p><w:r><w:t>Mean illuminance was high.</w:t></w:r></w:p>"
    "<w:tbl><w:tr><w:tc><w:p><w:r><w:t>215 lx</w:t></w:r></w:p></w:tc></w:tr></w:tbl>"
    "</w:body></w:document>"
)


class TestFold(unittest.TestCase):
    def test_dashes_and_minus_fold_to_hyphen(self):
        self.assertEqual(fold("400–700 nm, −4.2"), "400-700 nm, -4.2")

    def test_fullwidth_digits_fold(self):
        self.assertEqual(fold("４００"), "400")

    def test_thin_and_nobreak_spaces_fold_to_space(self):
        self.assertEqual(fold("62 % of"), "62 % of")


class TestFoldKeepDashes(unittest.TestCase):
    def test_en_dash_survives_and_differs_from_hyphen(self):
        self.assertEqual(fold("400\u2013700", keep_dashes=True), "400\u2013700")
        self.assertNotEqual(fold("400\u2013700", keep_dashes=True),
                            fold("400-700", keep_dashes=True))

    def test_latex_double_hyphen_is_en_dash_only_for_tex(self):
        self.assertEqual(fold("400--700", keep_dashes=True, tex=True), "400\u2013700")
        self.assertEqual(fold("400--700", keep_dashes=True), "400--700")

    def test_minus_and_hyphen_variants_still_agree(self):
        self.assertEqual(fold("\u22124", keep_dashes=True), "-4")

    def test_default_fold_unchanged(self):
        self.assertEqual(fold("400--700 \u2013 5"), "400-700 - 5")


class TestUnitsAndRanges(unittest.TestCase):
    def test_unit_with_an_si_prefix_is_captured(self):
        self.assertEqual(numbers("5 mV, 3 kg, 2 mol/L, 4 kWh/m2, 7 \u03bcm"),
                         ["5 mV", "3 kg", "2 mol/L", "4 kWh/m2", "7 \u03bcm"])

    def test_a_word_after_a_number_is_not_a_unit(self):
        self.assertEqual(numbers("3 of the 5 and 7 zones"), ["3", "5", "7"])

    def test_en_dash_range_keeps_its_dash(self):
        self.assertEqual(numbers("400\u2013700 nm"), ["400\u2013700 nm"])
        self.assertEqual(numbers("400-700 nm"), ["400-700 nm"])

    def test_range_in_words(self):
        self.assertEqual(ranges_in_words("from 400 to 700 nm"), ["400 to 700"])
        self.assertEqual(ranges_in_words("between 400 and 700 nm"), ["400 to 700"])
        self.assertEqual(ranges_in_words("400 and 700 nm"), [])


class TestOtherFrozenTokens(unittest.TestCase):
    def test_comparisons(self):
        self.assertEqual(comparisons("p < 0.05, n \u2265 30, x = 4 \u00b1 .5"),
                         ["<0.05", "\u226530", "=4", "\u00b10.5"])
        self.assertEqual(comparisons(r"$p \leq 0.05$ and $p \geq 0.05$"), ["\u22640.05", "\u22650.05"])

    def test_comparison_without_a_number_is_ignored(self):
        self.assertEqual(comparisons("a -> b and x = y"), [])

    def test_symbols(self):
        self.assertEqual(symbols("sDA300/50 and UDI300 with CO2"), ["sDA300/50", "UDI300", "CO2"])
        self.assertEqual(symbols("\\alpha and \u03b1 and \\Delta"), ["\u03b1", "\u03b1", "\u0394"])

    def test_symbols_skip_citation_keys(self):
        self.assertEqual(symbols(r"\cite{smith2020} and [@lee2021]"), [])

    def test_abbreviations_and_standards(self):
        got = abbreviations("DGP and sDA under CIE S 026:2018, EN 17037 and ISO 9241-210.")
        for t in ("DGP", "sDA", "CIE S 026:2018", "EN 17037", "ISO 9241-210"):
            self.assertIn(t, got)

    def test_plural_s_is_not_part_of_an_abbreviation(self):
        self.assertEqual(abbreviations("two DGPs"), ["DGP"])

    def test_abbreviation_before_a_measurement_is_not_a_standard(self):
        self.assertNotIn("LED 5", abbreviations("the LED 5 lm lamp"))


class TestNumbers(unittest.TestCase):
    def test_range_is_one_token(self):
        self.assertIn("400-700 nm", numbers(fold("between 400–700 nm")))

    def test_siunitx(self):
        self.assertIn("4.2 lx", numbers(r"\SI{4.2}{\lux}"))

    def test_percent_with_thin_space(self):
        self.assertIn("62 %", numbers(fold("62 % of hours")))

    def test_percent_escaped_in_latex(self):
        self.assertIn("62 %", numbers(fold(r"62\,\% of hours")))

    def test_scientific_forms_agree(self):
        self.assertEqual(numbers("1.2e-3"), numbers(fold("1.2 × 10^{-3}")))

    def test_number_glued_to_non_latin_text(self):
        self.assertIn("84 lx", numbers("照度84 lx"))

    def test_bracketed_interval_is_kept(self):
        self.assertIn("0.71", numbers("[95% CI 0.71, 0.80]"))

    def test_float_reference_numbers_skipped(self):
        self.assertEqual(numbers("see Fig. 4 and Table 2"), [])

    def test_section_reference_numbers_skipped(self):
        self.assertEqual(numbers("as described in Section 3.2 and Eq. 5"), [])

    def test_numbers_inside_cite_and_ref_skipped(self):
        self.assertEqual(numbers(r"\cite{smith2020} and \ref{fig:4}"), [])

    # --- found in review -------------------------------------------------------------
    def test_number_after_a_float_reference_and_comma_is_kept(self):
        self.assertEqual(numbers("In Section 3, 45 participants rated glare"), ["45"])
        self.assertIn("2 m", numbers("as in Fig. 1, 2 m from the window"))

    def test_reference_list_with_and_is_still_skipped(self):
        self.assertEqual(numbers("see Figs. 4 and 5 and Tables 2 to 4"), [])

    def test_latex_double_hyphen_range_is_one_token(self):
        self.assertIn("400-700 nm", numbers(fold("between 400--700 nm")))

    def test_uppercase_and_signed_exponents(self):
        self.assertEqual(numbers("1.2E-3"), ["1.2e-3"])
        self.assertEqual(numbers("1.2e+3"), ["1.2e3"])

    def test_leading_dot_decimal(self):
        self.assertEqual(numbers("p < .05"), ["0.05"])

    def test_compound_siunitx_unit_is_kept_whole(self):
        self.assertEqual(numbers(r"\SI{4.2}{\watt\per\metre\squared}"), ["4.2 W/m2"])

    def test_thin_space_thousands_is_one_token(self):
        self.assertEqual(numbers(fold("about 10\\,000 lx")), ["10 000 lx"])

    def test_iso_date_is_not_a_range(self):
        self.assertEqual(numbers("last run on 2026-08-19"), [])

    def test_negative_number_keeps_sign(self):
        self.assertIn("-4.2", numbers(fold("a bias of −4.2")))


class TestSections(unittest.TestCase):
    def test_latex_sections(self):
        s = split_sections(
            r"\begin{abstract}A\end{abstract}\section{Introduction}I\section{Results}R", ".tex")
        self.assertEqual((s["abstract"].strip(), s["results"].strip()), ("A", "R"))

    def test_markdown_sections_and_aliases(self):
        s = split_sections("# Abstract\nA\n## 2. Materials and Methods\nM\n## Experiments\nE\n",
                           ".md")
        self.assertEqual((s["methods"].strip(), s["results"].strip()), ("M", "E"))

    def test_plain_numbered_headings(self):
        s = split_sections("Abstract\nA\n1. Introduction\nI\n4 Discussion\nD\n", ".txt")
        self.assertEqual((s["introduction"].strip(), s["discussion"].strip()), ("I", "D"))

    def test_absent_section_has_no_key(self):
        s = split_sections(r"\section{Introduction}I", ".tex")
        self.assertNotIn("discussion", s)


class TestRead(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        (d / "part.tex").write_text("Included text 12 lx.\n", encoding="utf-8")
        self.root = d / "root.tex"
        self.root.write_text("Start.\n\\input{part}\n\\input{gone}\nEnd.\n", encoding="utf-8")
        self.docx = d / "m.docx"
        with zipfile.ZipFile(self.docx, "w") as z:
            z.writestr("word/document.xml", DOCX_XML)

    def tearDown(self):
        self.tmp.cleanup()

    def test_input_is_followed(self):
        text, _ = read_manuscript(self.root)
        self.assertIn("Included text 12 lx.", text)

    def test_missing_input_is_reported(self):
        _, missing = read_manuscript(self.root)
        self.assertEqual(missing, ["gone"])

    def test_self_including_file_is_reported_not_silently_cut(self):
        loop = Path(self.tmp.name) / "loop.tex"
        loop.write_text("Text.\n\\input{loop}\n", encoding="utf-8")
        _, missing = read_manuscript(loop)
        self.assertTrue(any("depth" in m for m in missing))

    def test_braceless_input_is_followed(self):
        root = Path(self.tmp.name) / "b.tex"
        root.write_text("Start.\n\\input part\nEnd.\n", encoding="utf-8")
        text, _ = read_manuscript(root)
        self.assertIn("Included text 12 lx.", text)

    def test_docx_table_cells_are_read(self):
        text, _ = read_manuscript(self.docx)
        self.assertIn("215 lx", text)

    def test_import_family_is_followed(self):
        d = Path(self.tmp.name)
        (d / "sub").mkdir()
        (d / "sub" / "part.tex").write_text("Imported 77 lx.\n", encoding="utf-8")
        for cmd in ("import", "subimport", "includefrom", "subincludefrom"):
            root = d / f"{cmd}.tex"
            root.write_text("Start.\n\\%s{sub/}{part}\nEnd.\n" % cmd, encoding="utf-8")
            text, missing = read_manuscript(root)
            self.assertIn("Imported 77 lx.", text, cmd)
            self.assertEqual(missing, [], cmd)

    def test_missing_import_target_is_reported(self):
        root = Path(self.tmp.name) / "imp.tex"
        root.write_text("Start.\n\\import{sub/}{gone}\n", encoding="utf-8")
        _, missing = read_manuscript(root)
        self.assertEqual(missing, ["sub/gone"])


class TestReviewFindings(unittest.TestCase):
    """Findings A, B, C, G, H of the script review."""

    # A. decimal comma
    def test_decimal_comma_keeps_its_fraction(self):
        self.assertEqual(numbers("The gap was 1,5 m and 0,35 W."), ["1.5 m", "0.35 W"])

    def test_changed_decimal_comma_differs(self):
        self.assertNotEqual(numbers("1,5 m and 0,35 W"), numbers("1,9 m and 0,99 W"))

    def test_decimal_comma_equals_decimal_point(self):
        self.assertEqual(numbers("1,5 m"), numbers("1.5 m"))

    def test_thousands_comma_still_works_and_is_kept_as_written(self):
        self.assertEqual(numbers("1,200 plans"), ["1,200"])
        self.assertNotEqual(numbers("1,200 plans"), numbers("1200 plans"))

    def test_unspaced_list_of_digits_keeps_every_member(self):
        self.assertEqual(numbers("zones 1,2,3"), ["1", "2", "3"])

    # B. \pm
    def test_tex_pm_equals_unicode_pm_and_is_not_a_unit(self):
        a = numbers(r"$4.1 \pm 0.3$ lx")
        self.assertEqual(a, numbers("$4.1 \u00b1 0.3$ lx"))
        self.assertFalse(any("pm" in t for t in a), a)

    def test_unspaced_tex_pm_is_not_a_unit(self):
        self.assertEqual(numbers(r"$4.1\pm0.3$"), ["4.1", "0.3"])

    # C. capitals
    def test_capitalised_heading_is_not_a_set_of_abbreviations(self):
        a = abbreviations("THE RESULTS AND DISCUSSION", words={"results", "discussion"})
        self.assertEqual(a, [])

    def test_capitalised_ordinary_word_is_not_an_abbreviation(self):
        self.assertEqual(abbreviations("NOTE that DGP is 0.3", words={"note"}), ["DGP"])

    def test_real_abbreviation_still_found_in_a_capital_heading(self):
        self.assertIn("DGP", abbreviations("THE DGP RESULTS"))

    # G. units
    def test_caret_minus_exponent_is_one_unit_not_a_bare_number(self):
        got = numbers("150 cd m^-2 and 3 m s^-1")
        self.assertEqual(len(got), 2, got)
        self.assertFalse(any(t.startswith("-") for t in got), got)

    def test_exponent_spellings_of_one_unit_agree(self):
        self.assertEqual(numbers("150 cd m^-2"), numbers("150 cd/m\u00b2"))
        self.assertEqual(numbers("5 W/m^2"), numbers("5 W/m2"))
        self.assertEqual(numbers("5 W/m2"), numbers("5 W/m\u00b2"))

    def test_unit_with_changed_exponent_differs(self):
        self.assertNotEqual(numbers("150 cd/m2"), numbers("150 cd/m3"))

    def test_more_units_are_kept(self):
        for t in ("40 dBA", "40 dBC", "2 sr", "0.5 ACH", "30 deg"):
            self.assertEqual(numbers(t), [t], t)
        self.assertEqual(numbers("0.2 W/(m K)"), numbers("0.2 W/m2K".replace("m2K", "(m\u00b7K)")))
        self.assertEqual(len(numbers("0.2 W/(m K) and 3")), 2)
        self.assertNotEqual(numbers("0.2 W/(m K)"), numbers("0.2 W/(m s)"))
        self.assertNotEqual(numbers("40 dBA"), numbers("40 dBC"))

    # H. speed
    def test_long_digit_runs_are_linear(self):
        for text in ("1" * 20000, "123 " * 10000):
            t0 = time.time()
            numbers(text)
            self.assertLess(time.time() - t0, 3.0)

    def test_long_digit_run_between_words_is_linear(self):
        t0 = time.time()
        numbers("a " + "1" * 40000 + " b " + "1." * 20000)
        self.assertLess(time.time() - t0, 3.0)


class TestIncludeResolution(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.d = Path(self.tmp.name)
        (self.d / "sections").mkdir()
        (self.d / "sections" / "table.tex").write_text("Table text 9 lx.\n", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, name, text):
        (self.d / name).write_text(text, encoding="utf-8")

    def test_nested_input_is_resolved_against_the_root_folder(self):
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "Methods.\n\\input{sections/table}\n")
        text, missing = read_manuscript(self.d / "main.tex")
        self.assertIn("Table text 9 lx.", text)
        self.assertEqual(missing, [])

    def test_input_falls_back_to_the_current_folder(self):
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "Methods.\n\\input{table}\n")
        text, missing = read_manuscript(self.d / "main.tex")
        self.assertIn("Table text 9 lx.", text)
        self.assertEqual(missing, [])

    def test_subfile_is_resolved_against_the_current_folder(self):
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "Methods.\n\\subfile{table}\n")
        text, _ = read_manuscript(self.d / "main.tex")
        self.assertIn("Table text 9 lx.", text)

    def test_import_family_joins_dir_and_file_as_a_path(self):
        self.put("main.tex", "\\subimport{sections}{table}\n\\import{sections}{table}\n")
        text, missing = read_manuscript(self.d / "main.tex")
        self.assertEqual(text.count("Table text 9 lx."), 2)
        self.assertEqual(missing, [])

    def test_import_dir_comes_from_the_root_folder(self):
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "Methods.\n\\import{sections}{table}\n")
        text, _ = read_manuscript(self.d / "main.tex")
        self.assertIn("Table text 9 lx.", text)

    def test_audit_follows_a_nested_root_relative_input(self):
        from ai_tell_audit import with_includes
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "Methods.\n\\input{sections/table}\n")
        unchecked: list = []
        files = with_includes([self.d / "main.tex"], unchecked)
        self.assertIn((self.d / "sections" / "table.tex").resolve(),
                      [f.resolve() for f in files])
        self.assertEqual(unchecked, [])

    def test_a_target_not_found_is_still_reported(self):
        self.put("main.tex", "\\input{sections/methods}\n")
        self.put("sections/methods.tex", "\\input{sections/gone}\n")
        _, missing = read_manuscript(self.d / "main.tex")
        self.assertEqual(missing, ["sections/gone"])


class TestReviewRound2(unittest.TestCase):
    def test_section_title_with_nested_braces_is_read_whole(self):
        """A-31."""
        t = "\\section{The \\textbf{Results} of $x$}body 7\n\\section{Intro}hello\n"
        got = split_sections(t, ".tex")
        self.assertEqual(got["results"], "body 7\n")
        self.assertEqual(got["introduction"], "hello\n")
        self.assertNotIn("other", got)

    def test_output_is_input_names_the_clashing_file(self):
        """A-19: the helper the scripts use to refuse overwriting an input."""
        from _manuscript import output_is_input
        with tempfile.TemporaryDirectory() as d:
            a, b = Path(d) / "a.bib", Path(d) / "b.tex"
            a.write_text("x", encoding="utf-8")
            b.write_text("y", encoding="utf-8")
            inputs = {"the .bib file": str(a), "the --tex file": str(b), "none": None}
            self.assertEqual(output_is_input(str(a), inputs), "the .bib file")
            self.assertEqual(output_is_input(str(Path(d) / "." / "b.tex"), inputs),
                             "the --tex file")
            self.assertIsNone(output_is_input(str(Path(d) / "new.json"), inputs))
            self.assertIsNone(output_is_input(None, inputs))


class TestRound3(unittest.TestCase):
    def test_comment_after_a_line_break_is_removed_and_an_escaped_percent_kept(self):
        with tempfile.TemporaryDirectory() as d:
            f = Path(d) / "m.tex"
            f.write_text("a \\\\% gone \\input{x}\nb 50\\% kept\n", encoding="utf-8")
            text, missing = read_manuscript(f)
        self.assertNotIn("gone", text)
        self.assertEqual(missing, [])
        self.assertIn("50\\% kept", text)

    def test_the_files_the_reader_opened_are_listed(self):
        from _manuscript import read_manuscript_opened
        with tempfile.TemporaryDirectory() as d:
            d = Path(d)
            (d / "m.tex").write_text("\\input{a}\n", encoding="utf-8")
            (d / "a.tex").write_text("\\input{b}\n", encoding="utf-8")
            (d / "b.tex").write_text("x\n", encoding="utf-8")
            _, missing, opened = read_manuscript_opened(d / "m.tex")
        self.assertEqual([p.name for p in opened], ["m.tex", "a.tex", "b.tex"])


if __name__ == "__main__":
    unittest.main()
