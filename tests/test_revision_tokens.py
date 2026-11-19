import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from tests import _paths
from check_revision_tokens import compare

SCRIPT = _paths.SCRIPTS / "check_revision_tokens.py"
TEXT = (r"Mean illuminance was \SI{412}{\lux} (95\% CI 380--444) in zone A \cite{smith2020,lee2021}. "
        r"As Fig.~\ref{fig:plan} shows, the core may remain under-lit between 400--700 nm.")


def clean(d):
    return all(not v["removed"] and not v["added"] for v in d.values())


class TestCompare(unittest.TestCase):
    def test_range_broken_apart(self):
        d = compare("between 400–700 nm", "between 400 and 700 nm", ".txt", [])
        self.assertIn("400\u2013700 nm", d["numbers"]["removed"])

    def test_hedge_deleted(self):
        d = compare("The core may remain under-lit.", "The core remains under-lit.", ".txt", [])
        self.assertEqual(d["hedges"]["removed"], ["may"])

    def test_claim_verb_strengthened(self):
        d = compare("This suggests a link.", "This demonstrates a link.", ".txt", [])
        self.assertEqual((d["hedges"]["removed"], d["hedges"]["added"]),
                         (["suggest"], ["demonstrate"]))

    def test_citation_dropped(self):
        d = compare(r"as shown \cite{a,b}", r"as shown \cite{a}", ".tex", [])
        self.assertEqual(d["citations"]["removed"], ["b"])

    def test_author_year_citation_dropped(self):
        d = compare("Glare rises (Smith et al., 2020; Lee, 2021).", "Glare rises (Lee, 2021).",
                    ".txt", [])
        self.assertEqual(d["citations"]["removed"], ["Smith et al., 2020"])

    def test_crossref_changed(self):
        d = compare(r"see \ref{fig:a}", r"see \ref{fig:b}", ".tex", [])
        self.assertEqual((d["crossrefs"]["removed"], d["crossrefs"]["added"]),
                         (["fig:a"], ["fig:b"]))

    def test_plain_section_pointer_changed(self):
        d = compare("see Section 4.1", "see Section 4.3", ".txt", [])
        self.assertEqual((d["crossrefs"]["removed"], d["crossrefs"]["added"]),
                         (["Section 4.1"], ["Section 4.3"]))

    def test_protected_term_half_lost(self):
        d = compare("a state-of-the-art baseline", "a baseline", ".txt", [])
        self.assertIn("state-of-the-art", d["terms"]["removed"])

    def test_locked_term_from_terms_list(self):
        d = compare("the view direction", "the gaze direction", ".txt", ["view direction"])
        self.assertEqual(d["terms"]["removed"], ["view direction"])

    def test_identical_text_is_clean(self):
        self.assertTrue(clean(compare(TEXT, TEXT, ".tex", [])))

    def test_reordered_sentences_are_clean(self):
        a = "Zone A reached 412 lx. Zone B reached 215 lx."
        b = "Zone B reached 215 lx. Zone A reached 412 lx."
        self.assertTrue(clean(compare(a, b, ".txt", [])))

    def test_fullwidth_respelling_is_clean(self):
        self.assertTrue(clean(compare("at 400 lx", "at ４００ lx", ".txt", [])))

    def test_thousands_separator_change_is_reported(self):
        d = compare("n = 612,418", "n = 612418", ".txt", [])
        self.assertTrue(d["numbers"]["removed"])

    def test_repeated_number_dropped_once_is_reported(self):
        d = compare("412 lx here and 412 lx there", "412 lx here", ".txt", [])
        self.assertEqual(d["numbers"]["removed"], ["412 lx"])


def differs(d):
    return not clean(d)


class TestKnownFaults(unittest.TestCase):
    """One test per fault found in review: each change below once printed 'No token differences'."""

    def test_fault1_metric_name_with_digits_is_one_token(self):
        self.assertTrue(differs(compare("sDA300/50 was 62 %", "sDA500/50 was 62 %", ".txt", [])))
        self.assertTrue(differs(compare("UDI300 was high", "UDI500 was high", ".txt", [])))

    def test_fault2_unit_outside_the_closed_list(self):
        self.assertTrue(differs(compare("a drop of 5 mV", "a drop of 5 V", ".txt", [])))
        self.assertTrue(differs(compare("a mass of 3 kg", "a mass of 3 g", ".txt", [])))

    def test_fault3_comparison_sign_next_to_a_number(self):
        self.assertTrue(differs(compare("p < 0.05", "p > 0.05", ".txt", [])))
        self.assertTrue(differs(compare("n \u2264 30", "n \u2265 30", ".txt", [])))
        self.assertTrue(differs(compare("x = 4 \u00b1 1", "x = 4", ".txt", [])))
        self.assertTrue(differs(compare(r"$p \leq 0.05$", r"$p \geq 0.05$", ".tex", [])))

    def test_fault4_range_written_in_words(self):
        self.assertTrue(differs(compare("400 to 700 nm", "400 and 700 nm", ".txt", [])))

    def test_fault4_words_for_a_range_are_interchangeable(self):
        self.assertTrue(clean(compare("from 400 to 700 nm", "between 400 and 700 nm", ".txt", [])))

    def test_fault5_cross_reference_list(self):
        self.assertTrue(differs(compare("see Figs. 3 and 4", "see Figs. 3 and 5", ".txt", [])))
        self.assertTrue(differs(compare("see Figs. 3, 4 and 5", "see Figs. 3, 4 and 6", ".txt", [])))

    def test_fault6_dash_inside_a_range_is_frozen(self):
        self.assertTrue(differs(compare("400\u2013700 nm", "400-700 nm", ".txt", [])))

    def test_fault6_latex_double_hyphen_is_the_en_dash(self):
        self.assertTrue(clean(compare("400--700 nm", "400\u2013700 nm", ".tex", [])))
        self.assertTrue(clean(compare("a 400\u2013700 nm band", "a 400--700 nm band", ".tex", [])))

    def test_fault7_tense_of_a_claim_verb(self):
        self.assertTrue(differs(compare("Results suggest a link.", "Results suggested a link.",
                                        ".txt", [])))

    def test_fault7_agreement_change_is_not_a_tense_change(self):
        self.assertTrue(clean(compare("The result suggests a link.", "Results suggest a link.",
                                      ".txt", [])))

    def test_fault8_greek_symbol(self):
        self.assertTrue(differs(compare("the \u03b1 level", "the \u03b2 level", ".txt", [])))
        self.assertTrue(clean(compare(r"the $\alpha$ level", "the \u03b1 level", ".tex", [])))
        self.assertTrue(differs(compare(r"the $\alpha$ level", r"the $\beta$ level", ".tex", [])))

    def test_fault8_abbreviation_dropped(self):
        d = compare("DGP and sDA and EDI were computed", "glare and daylight were computed",
                    ".txt", [])
        removed = [t for g in d.values() for t in g["removed"]]
        for t in ("DGP", "sDA", "EDI"):
            self.assertIn(t, removed)

    def test_fault8_standard_name_changed(self):
        for a, b in (("CIE S 026:2018", "CIE T 026:2018"), ("EN 17037", "BS 17037"),
                     ("ISO 9241", "ISO 9242")):
            self.assertTrue(differs(compare(f"per {a} here", f"per {b} here", ".txt", [])), a)
        self.assertTrue(differs(compare("per CIE S 026 here", "per CIE here", ".txt", [])))


class TestCitationParser(unittest.TestCase):
    def test_every_key_of_a_biblatex_multicite_is_read(self):
        d = compare(r"see \cites{a}{b}{c}", r"see \cites{a}{b}{z}", ".tex", [])
        self.assertEqual((d["citations"]["removed"], d["citations"]["added"]), (["c"], ["z"]))

    def test_multicite_with_optional_arguments(self):
        d = compare(r"\parencites[see][p.~3]{a}[cf.]{b}", r"\parencites[see][p.~3]{a}[cf.]{x}",
                    ".tex", [])
        self.assertEqual((d["citations"]["removed"], d["citations"]["added"]), (["b"], ["x"]))

    def test_space_between_optional_arguments(self):
        d = compare(r"\citep[see] [p.~3]{k}", "text", ".tex", [])
        self.assertEqual(d["citations"]["removed"], ["k"])

    def test_single_cite_followed_by_a_group_is_not_a_second_key(self):
        d = compare(r"\cite{a}{text}", "x", ".tex", [])
        self.assertEqual(d["citations"]["removed"], ["a"])


class TestFrozenSetCoverage(unittest.TestCase):
    """The hedges, approximators and proper names that SKILL.md freezes."""

    def removed(self, a, b, group, suffix=".txt"):
        return compare(a, b, suffix, [])[group]["removed"]

    def test_dropped_approximator_is_reported(self):
        self.assertEqual(self.removed("approximately 5.8 m", "5.8 m", "hedges"),
                         ["approximately"])
        self.assertEqual(self.removed("roughly 5 m, nearly 6 m, almost 7 m", "5 m, 6 m, 7 m",
                                      "hedges"), ["almost", "nearly", "roughly"])

    def test_dropped_modal_is_reported(self):
        self.assertEqual(self.removed("It can rise and would fall.", "It rises and falls.",
                                      "hedges"), ["can", "would"])

    def test_at_least_to_more_than_is_reported(self):
        d = compare("at least 250 lx", "more than 250 lx", ".txt", [])
        self.assertEqual((d["hedges"]["removed"], d["hedges"]["added"]),
                         (["at least"], ["more than"]))

    def test_bounds_are_each_one_token(self):
        for phrase in ("up to", "at most", "less than", "no more than", "no less than"):
            self.assertEqual(self.removed(f"{phrase} 5 m", "5 m", "hedges"), [phrase], phrase)

    def test_about_counts_only_before_a_number(self):
        self.assertEqual(self.removed("about 5.8 m", "5.8 m", "hedges"), ["about"])
        self.assertEqual(self.removed("We talk about glare.", "We talk of glare.", "hedges"), [])

    def test_changed_proper_names_are_reported(self):
        d = compare("We used Radiance with the Perez sky.", "We used EnergyPlus with the CIE sky.",
                    ".txt", [])
        self.assertEqual(d["names"]["removed"], ["Perez", "Radiance"])
        self.assertEqual(d["names"]["added"], ["EnergyPlus"])

    def test_sentence_start_word_is_not_a_name(self):
        self.assertTrue(clean(compare("Results are shown. The core is dim.",
                                      "Findings are shown. This core is dim.", ".txt", [])))

    def test_mixed_case_name_at_sentence_start_is_a_name(self):
        self.assertEqual(self.removed("EnergyPlus ran first.", "The model ran first.", "names"),
                         ["EnergyPlus"])

    def test_tex_commands_are_not_names(self):
        self.assertTrue(clean(compare(r"\textbf{bold} \emph{note}", "bold note", ".tex", [])))


class TestHonestEdits(unittest.TestCase):
    """A style edit that touches no frozen token must report no difference."""

    RICH = ("It is worth noting that sDA300/50 reached 62 % (p < 0.05) at 5 mV, "
            "as Figs. 3 and 4 show for 400\u2013700 nm under CIE S 026:2018 with \u03b1 = 0.05. "
            "Results suggest that UDI300 may rise by 3 kg.")

    def test_filler_removed(self):
        a = ("It is worth noting that sDA300/50 reached 62 % (p < 0.05) at 5 mV, "
             "as Figs. 3 and 4 show for 400\u2013700 nm.")
        b = "sDA300/50 reached 62 % (p < 0.05) at 5 mV, as Figs. 3 and 4 show for 400\u2013700 nm."
        self.assertTrue(clean(compare(a, b, ".txt", [])))

    def test_sentence_split(self):
        b = self.RICH.replace(", as Figs. 3", ". Figs. 3").replace(" with ", ". We used ")
        self.assertTrue(clean(compare(self.RICH, b, ".txt", [])))

    def test_sentences_reordered(self):
        a = ("Zone A reached 412 lx at 5 m. Zone B reached 215 lx at 3 m. "
             "Results suggest that UDI300 may rise by 3 kg.")
        b = ("Results suggest that UDI300 may rise by 3 kg. Zone A reached 412 lx at 5 m. "
             "Zone B reached 215 lx at 3 m.")
        self.assertTrue(clean(compare(a, b, ".txt", [])))

    def test_numeric_citation_reordered(self):
        self.assertTrue(clean(compare("as shown [12, 13].", "as shown [13, 12].", ".txt", [])))
        self.assertTrue(clean(compare("as shown [12-14].", "as shown [12, 13, 14].", ".txt", [])))

    def test_tex_pm_respelled_as_the_unicode_sign(self):
        self.assertTrue(clean(compare(r"Mean $4.1 \pm 0.3$ lx.", "Mean $4.1 \u00b1 0.3$ lx.",
                                      ".tex", [])))
        self.assertTrue(clean(compare(r"Mean $4.1\pm0.3$ lx.", "Mean $4.1 \u00b1 0.3$ lx.",
                                      ".tex", [])))

    def test_heading_changed_from_capitals_to_sentence_case(self):
        a = "THE RESULTS AND DISCUSSION\nNOTE that DGP is 0.3."
        b = "Results and discussion\nNote that DGP is 0.3."
        self.assertTrue(clean(compare(a, b, ".txt", [])))

    def test_unit_exponent_respelled(self):
        self.assertTrue(clean(compare("Luminance was 150 cd m^-2.", "Luminance was 150 cd/m\u00b2.",
                                      ".txt", [])))
        self.assertTrue(clean(compare("At 5 W/m^2.", "At 5 W/m2.", ".txt", [])))

    def test_sentence_split_after_a_figure_pointer(self):
        a = "Results are shown in Fig. 2, and 5 sensors were used."
        b = "Results are shown in Fig. 2. 5 sensors were used."
        self.assertTrue(clean(compare(a, b, ".txt", [])))
        a = "See Fig. 2, 30 plans were run."
        b = "30 plans were run (Fig. 2)."
        self.assertTrue(clean(compare(a, b, ".txt", [])))
        self.assertTrue(clean(compare("Eq. (3) and 4.", "Eq. (3). Then 4.", ".txt", [])))

    def test_decimal_comma_respelled_as_a_point(self):
        self.assertTrue(clean(compare("The gap was 1,5 m.", "The gap was 1.5 m.", ".txt", [])))

    def test_citation_spacing_and_pointer_with_measurement(self):
        a = "Fig. 2, 412 lx at 5 m2 [1, 2]."
        b = "At 5 m2, Fig. 2, 412 lx [1,2]."
        self.assertTrue(clean(compare(a, b, ".txt", [])))

    def test_tex_markup_respelling_of_dashes_and_greek(self):
        a = r"Over 400--700 nm, $\alpha = 0.05$ and $p < 0.05$."
        b = "Over 400\u2013700 nm, \u03b1 = 0.05 and p < 0.05."
        self.assertTrue(clean(compare(a, b, ".tex", [])))

    def test_clauses_reordered_within_a_sentence(self):
        a = "Zone A reached 412 lx (p < 0.05) and zone B 215 lx."
        b = "Zone B reached 215 lx, and zone A 412 lx (p < 0.05)."
        self.assertTrue(clean(compare(a, b, ".txt", [])))


class TestReviewFindings(unittest.TestCase):
    """Findings A, C, E, F: a real change is still reported."""

    def groups(self, a, b, suffix=".txt"):
        d = compare(a, b, suffix, [])
        return {g: v for g, v in d.items() if v["removed"] or v["added"]}

    def test_changed_decimal_comma_is_reported(self):
        got = self.groups("The gap was 1,5 m and 0,35 W.", "The gap was 1,9 m and 0,99 W.")
        self.assertEqual(got["numbers"]["removed"], ["0.35 W", "1.5 m"])

    def test_tex_pm_changed_value_is_reported(self):
        self.assertIn("numbers", self.groups(r"$4.1 \pm 0.3$ lx", r"$4.1 \pm 0.4$ lx", ".tex"))

    def test_removed_real_abbreviation_is_reported_beside_a_case_change(self):
        got = self.groups("NOTE that DGP is 0.3", "Note that is 0.3")
        self.assertEqual(got["abbrevs"]["removed"], ["DGP"])
        got = self.groups("NOTE that DGP is 0.3", "Note that DGI is 0.3")
        self.assertEqual((got["abbrevs"]["removed"], got["abbrevs"]["added"]), (["DGP"], ["DGI"]))

    def test_cross_reference_list_after_plural_pointer_still_works(self):
        got = self.groups("see Figs. 3 and 4", "see Figs. 3 and 5")
        self.assertEqual((got["crossrefs"]["removed"], got["crossrefs"]["added"]),
                         (["Fig. 4"], ["Fig. 5"]))
        d = compare("Figs. 2, 3 and 5", "Figs. 2, 3 and 5", ".txt", [])
        self.assertTrue(clean(d))
        self.assertEqual(compare("Figs. 2, 3 and 5", "x", ".txt", [])["crossrefs"]["removed"],
                         ["Fig. 2", "Fig. 3", "Fig. 5"])

    def test_singular_pointer_reads_one_target(self):
        self.assertEqual(compare("Fig. 2, and 5 sensors", "x", ".txt", [])["crossrefs"]["removed"],
                         ["Fig. 2"])

    def test_changed_numeric_citation_member_is_reported(self):
        got = self.groups("as shown [12, 13].", "as shown [12, 14].")
        self.assertEqual((got["citations"]["removed"], got["citations"]["added"]),
                         (["[13]"], ["[14]"]))

    def test_citation_range_is_expanded(self):
        got = self.groups("as shown [12\u201314].", "as shown [12, 13].")
        self.assertEqual(got["citations"]["removed"], ["[14]"])

    def test_changed_unit_exponent_is_reported(self):
        self.assertIn("numbers", self.groups("150 cd m^-2", "150 cd m^-3"))
        self.assertIn("numbers", self.groups("40 dBA", "40 dBC"))


class TestCli(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        d = Path(self.tmp.name)
        self.a, self.b = d / "a.txt", d / "b.txt"
        self.a.write_text("The core may remain under-lit at 215 lx.", encoding="utf-8")
        self.b.write_text("The core remains under-lit at 212 lx.", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_default_exit_is_zero_even_with_differences(self):
        p = self.run_cli("--source", str(self.a), "--revised", str(self.b))
        self.assertEqual(p.returncode, 0)
        self.assertIn("215 lx", p.stdout)

    def test_strict_exit_code(self):
        p = self.run_cli("--source", str(self.a), "--revised", str(self.b), "--strict")
        self.assertEqual(p.returncode, 1)

    def test_strict_clean_is_zero(self):
        p = self.run_cli("--source", str(self.a), "--revised", str(self.a), "--strict")
        self.assertEqual(p.returncode, 0)

    def test_unreadable_file_exits_2(self):
        p = self.run_cli("--source", str(self.a), "--revised", str(self.a) + ".missing")
        self.assertEqual(p.returncode, 2)

    def test_missing_include_changes_the_verdict_line(self):
        a = Path(self.tmp.name) / "a.tex"
        a.write_text("Core at 215 lx.\n\\input{gone}\n", encoding="utf-8")
        p = self.run_cli("--source", str(a), "--revised", str(a), "--strict")
        self.assertNotIn("No token differences.", p.stdout)
        self.assertIn("not checked", p.stdout)
        self.assertEqual(p.returncode, 3)

    def docx_with_equation(self, name, value):
        import zipfile
        path = Path(self.tmp.name) / name
        with zipfile.ZipFile(path, "w") as z:
            z.writestr("word/document.xml",
                       '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.'
                       'openxmlformats.org/wordprocessingml/2006/main" xmlns:m="http://schemas.'
                       'openxmlformats.org/officeDocument/2006/math"><w:body><w:p><w:r><w:t>Core.'
                       f'</w:t></w:r><m:oMath><m:r><m:t>x = {value}</m:t></m:r></m:oMath></w:p>'
                       "</w:body></w:document>")
        return str(path)

    def test_docx_equation_is_not_checked_and_says_so(self):
        a, b = self.docx_with_equation("a.docx", "3"), self.docx_with_equation("b.docx", "4")
        p = self.run_cli("--source", a, "--revised", b)
        self.assertNotIn("No token differences.", p.stdout)
        self.assertIn("equations", p.stdout)
        self.assertIn("not checked", p.stdout)

    def test_docx_equation_gives_exit_3_under_strict(self):
        a, b = self.docx_with_equation("a.docx", "3"), self.docx_with_equation("b.docx", "4")
        self.assertEqual(self.run_cli("--source", a, "--revised", b, "--strict").returncode, 3)

    def test_docx_pair_is_compared(self):
        import zipfile
        head = ('<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.'
                'openxmlformats.org/wordprocessingml/2006/main"><w:body>')
        paths = []
        for name, value in (("a.docx", "215 lx"), ("b.docx", "212 lx")):
            path = Path(self.tmp.name) / name
            with zipfile.ZipFile(path, "w") as z:
                z.writestr("word/document.xml", head + f"<w:p><w:r><w:t>Core at {value}.</w:t>"
                           "</w:r></w:p></w:body></w:document>")
            paths.append(str(path))
        p = self.run_cli("--source", paths[0], "--revised", paths[1])
        self.assertIn("- 215 lx", p.stdout)
        self.assertIn("+ 212 lx", p.stdout)

    def terms_run(self, content=None, name="terms.yml"):
        args = ["--source", str(self.a), "--revised", str(self.a), "--strict"]
        path = Path(self.tmp.name) / name
        if content is not None:
            path.write_text(content, encoding="utf-8")
        return self.run_cli(*args, "--terms", str(path))

    def test_fault9_missing_terms_file_is_not_checked_exit_3(self):
        p = self.terms_run(None, "nope.yml")
        self.assertEqual(p.returncode, 3)
        self.assertNotIn("No token differences.", p.stdout)
        self.assertIn("not checked", p.stdout)

    def test_fault10_terms_file_that_is_a_list_is_not_checked_exit_3(self):
        p = self.terms_run("- canonical: view direction\n- canonical: glare\n")
        self.assertEqual(p.returncode, 3)
        self.assertNotIn("Traceback", p.stderr)
        self.assertIn("not checked", p.stdout)

    def test_good_terms_file_still_exits_0_when_clean(self):
        p = self.terms_run("terms:\n  - canonical: view direction\n    abbrev: VD\n")
        self.assertEqual(p.returncode, 0)

    def test_terms_file_without_a_terms_key_is_not_checked_exit_3(self):
        p = self.terms_run("term:\n  - canonical: view direction\n")
        self.assertEqual(p.returncode, 3)
        self.assertIn("not checked", p.stdout)
        self.assertNotIn("No token differences.", p.stdout)

    def test_report_states_its_limit(self):
        p = self.run_cli("--source", str(self.a), "--revised", str(self.b))
        self.assertIn("cannot see negation", p.stdout)


class TestPython39(unittest.TestCase):
    def test_fault11_script_runs_on_the_system_python(self):
        import shutil
        import subprocess as sp
        exe = "/usr/bin/python3" if Path("/usr/bin/python3").exists() else shutil.which("python3.9")
        if not exe:
            self.skipTest("no /usr/bin/python3")
        v = sp.run([exe, "-c", "import sys; print(sys.version_info[0]*100+sys.version_info[1])"],
                   capture_output=True, text=True)
        if v.returncode != 0 or int(v.stdout.strip()) < 309:
            self.skipTest("interpreter older than 3.9")
        with tempfile.TemporaryDirectory() as tmp:
            a, b = Path(tmp) / "a.txt", Path(tmp) / "b.txt"
            a.write_text("Results suggest 5 mV [1].", encoding="utf-8")
            b.write_text("Results suggest 5 V [1].", encoding="utf-8")
            h = sp.run([exe, str(SCRIPT), "--help"], capture_output=True, text=True)
            self.assertEqual(h.returncode, 0, h.stderr)
            p = sp.run([exe, str(SCRIPT), "--source", str(a), "--revised", str(b)],
                       capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)
            self.assertIn("5 mV", p.stdout)


class TestRound2(unittest.TestCase):
    def groups(self, a, b, suffix=".tex"):
        return compare(a, b, suffix, [])

    def test_rewrapped_tex_paragraph_has_no_difference(self):
        a = ("We used Radiance in the\nMediterranean climate. Ward's method is described\n"
             "in Sec. 2. Results follow.\n")
        b = ("We used Radiance in the Mediterranean\nclimate. Ward's method is\n"
             "described in Sec. 2. Results follow.\n")
        for suffix in (".tex", ".md"):
            self.assertTrue(clean(self.groups(a, b, suffix)), suffix)
        a2 = "Mediterranean sites were used.\nWe also used Ward and Mediterranean sites."
        b2 = "We used Mediterranean sites.\nWard and Mediterranean sites were also used."
        self.assertTrue(clean(self.groups(a2, b2)))

    def test_moving_a_name_to_a_sentence_start_is_not_a_change(self):
        self.assertTrue(clean(self.groups("Ward showed it. The method of Ward holds.",
                                          "The method of Ward holds. Ward showed it.")))

    def test_names_run_in_linear_time(self):
        import time
        from check_revision_tokens import _names
        text = " ".join(["the quick Brown fox jumps over the lazy dog."] * 3400)
        self.assertGreater(len(text.split()), 30000)
        t = time.time()
        _names(text)
        self.assertLess(time.time() - t, 2.0)

    def test_multicite_with_global_notes(self):
        d = self.groups(r"\cites(see)(p.~3)[1]{a}[2]{b}", "x")
        self.assertEqual(d["citations"]["removed"], ["a", "b"])

    def test_citation_setup_commands_are_not_citations(self):
        for cmd in (r"\setcitestyle{authoryear,round}", r"\citestyle{authoryear}",
                    r"\citetext{see Smith}", r"\citeindextrue{x}", r"\citeindexfalse{x}",
                    r"\DeclareCiteCommand{\foo}{}{}{}", r"\bibcite{a}{1}", r"\citation{a}"):
            self.assertEqual(self.groups(cmd, "x")["citations"]["removed"], [], cmd)
        self.assertEqual(self.groups(r"\citep{a} \cite{b}", "x")["citations"]["removed"],
                         ["a", "b"])

    def test_hedge_false_positives(self):
        def h(t):
            return self.groups(t, "x", ".txt")["hedges"]["removed"]
        self.assertEqual(h("it is no  less than 5"), ["no less than"])
        self.assertEqual(h("it is no\nless than 5"), ["no less than"])
        self.assertEqual(h("the file is up to date"), [])
        self.assertEqual(h("as can be seen in Fig. 2"), [])
        self.assertEqual(h("as can be clearly seen"), [])
        self.assertEqual(h("it can fail"), ["can"])
        self.assertEqual(h("up to 5 m"), ["up to"])

    def test_json_to_a_missing_folder_exits_2_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as tmp:
            a = Path(tmp) / "a.txt"
            a.write_text("x 1 m", encoding="utf-8")
            p = subprocess.run([sys.executable, str(SCRIPT), "--source", str(a), "--revised",
                                str(a), "--json", str(Path(tmp) / "nope" / "o.json")],
                               capture_output=True, text=True)
            self.assertEqual(p.returncode, 2, p.stdout + p.stderr)
            self.assertNotIn("Traceback", p.stderr)
            self.assertIn("--json", p.stderr)


if __name__ == "__main__":
    unittest.main()
