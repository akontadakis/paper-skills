import subprocess
import sys
import unittest

from tests import _paths
from bib_check import (cited_keys, normalise_doi, offline_checks, online_checks, parse_bib)

SCRIPT = _paths.SCRIPTS / "bib_check.py"
SEEDED = _paths.FIXTURES / "seeded"
CLEAN_BIB = (SEEDED / "clean" / "refs.bib").read_text(encoding="utf-8")

GOOD = """
@article{a2020,
  author = {Able, Ann}, title = {Daylight in deep rooms}, journal = {J. Test},
  year = {2020}, volume = {3}, pages = {10--19}, doi = {10.5555/a.2020}
}
"""


def codes(findings):
    return {f["code"] for f in findings}


def check(bib, cited=None):
    return offline_checks(parse_bib(bib), cited)


class TestParse(unittest.TestCase):
    def test_fields_and_type(self):
        e = parse_bib(GOOD)[0]
        self.assertEqual((e["key"], e["type"], e["fields"]["year"]), ("a2020", "article", "2020"))

    def test_nested_braces_in_title_parse(self):
        e = parse_bib('@misc{k, title = {Validating {Radiance} against {HDR} data}, year = 2021}')[0]
        self.assertEqual(e["fields"]["title"], "Validating {Radiance} against {HDR} data")

    def test_quoted_values_and_comments_are_handled(self):
        e = parse_bib('% a comment\n@comment{ignored}\n@book{b, title = "A, B and C", year = "2019"}')
        self.assertEqual([(x["key"], x["fields"]["title"]) for x in e], [("b", "A, B and C")])

    def test_clean_fixture_parses_four_entries(self):
        self.assertEqual(len(parse_bib(CLEAN_BIB)), 4)


class TestOffline(unittest.TestCase):
    def test_clean_bib_has_no_findings(self):
        cited = cited_keys((SEEDED / "clean" / "manuscript.tex").read_text(encoding="utf-8"))
        self.assertEqual(check(CLEAN_BIB, cited), [])

    def test_missing_required_field(self):
        f = check(GOOD.replace("volume = {3}, ", ""))
        self.assertEqual([(x["code"], x["key"]) for x in f], [("BIB_MISSING_FIELD", "a2020")])
        self.assertIn("volume", f[0]["message"])

    def test_book_accepts_editor_in_place_of_author(self):
        self.assertEqual(check('@book{b, editor = {Ed, E.}, title = {T}, publisher = {P}, year = {2001}}'), [])

    def test_type_without_field_rules_is_reported_not_checked(self):
        f = check('@artwork{o, title = {T}}\n@artwork{o2, title = {U}}\n@letter{d, title = {V}}')
        msgs = sorted(x["message"] for x in f if x["code"] == "BIB_TYPE_NOT_CHECKED")
        self.assertEqual(msgs, ["not checked: no field rules for @artwork (2 entries)",
                                "not checked: no field rules for @letter (1 entries)"])
        self.assertTrue(all(x["reason"] == "no_field_rules" for x in f))

    def test_common_non_article_types_have_field_rules(self):
        """A bibliography with a web page, a dataset or a piece of software is ordinary.
        These types are checked, so their presence alone does not make the run 'not checked'."""
        complete = (
            '@online{o, author = {A, B.}, title = {T}, year = {2024}, url = {https://example.org}}\n'
            '@dataset{d, author = {A, B.}, title = {U}, year = {2024}, doi = {10.1234/d}}\n'
            '@software{s, author = {A, B.}, title = {V}, year = {2024}, version = {5.4}}\n'
            '@report{r, author = {A, B.}, title = {W}, institution = {I}, year = {2024}}\n'
            '@thesis{t, author = {A, B.}, title = {X}, school = {S}, year = {2024}}\n'
            '@inbook{i, author = {A, B.}, title = {Y}, chapter = {3}, publisher = {P}, year = {2024}}\n'
            '@unpublished{u, author = {A, B.}, title = {Z}, year = {2024}, note = {Manuscript}}\n'
            '@proceedings{p, title = {Q}, year = {2024}}\n')
        self.assertEqual(check(complete), [])

    def test_online_entry_without_a_url_is_a_missing_field(self):
        f = check('@online{o, author = {A, B.}, title = {T}, year = {2024}}')
        self.assertEqual([(x["code"], x["key"]) for x in f], [("BIB_MISSING_FIELD", "o")])
        self.assertIn("url", f[0]["message"])

    def test_dataset_without_doi_or_url_is_a_missing_field(self):
        f = check('@dataset{d, author = {A, B.}, title = {U}, year = {2024}}')
        self.assertEqual([x["code"] for x in f], ["BIB_MISSING_FIELD"])

    def test_comment_block_containing_an_entry_is_skipped(self):
        e = parse_bib('@Comment{@article{ghost, title = {X}}}\n@preamble{"@misc{p, a = 1}"}\n'
                      '@string{s = "@book{q, a = 1}"}\n' + GOOD)
        self.assertEqual([x["key"] for x in e], ["a2020"])

    def test_duplicate_key(self):
        self.assertIn("BIB_DUPLICATE_KEY", codes(check(GOOD + GOOD.replace("10.5555/a.2020", "10.5555/x")
                                                       .replace("Daylight in deep rooms", "Other"))))

    def test_duplicate_doi_ignores_url_form_and_case(self):
        other = GOOD.replace("a2020", "b2020").replace("Daylight in deep rooms", "Another title") \
                    .replace("10.5555/a.2020", "https://doi.org/10.5555/A.2020")
        self.assertIn("BIB_DUPLICATE_DOI", codes(check(GOOD + other)))

    def test_duplicate_title_ignores_case_and_braces(self):
        other = GOOD.replace("a2020", "b2020").replace("Daylight in deep rooms", "{D}aylight in Deep Rooms.") \
                    .replace("10.5555/a.2020", "10.5555/b.2020")
        self.assertIn("BIB_DUPLICATE_TITLE", codes(check(GOOD + other)))

    def test_single_hyphen_page_range(self):
        self.assertIn("BIB_PAGE_RANGE_FORM", codes(check(GOOD.replace("10--19", "10-19"))))

    def test_en_dash_and_single_page_are_accepted(self):
        self.assertEqual(check(GOOD.replace("10--19", "10–19")), [])
        self.assertEqual(check(GOOD.replace("10--19", "e0123")), [])

    def test_cited_key_without_entry(self):
        f = check(GOOD, {"a2020", "ghost2019"})
        self.assertEqual([(x["code"], x["key"]) for x in f], [("BIB_CITED_NOT_DEFINED", "ghost2019")])

    def test_entry_never_cited(self):
        f = check(GOOD, {"other"})
        self.assertIn(("BIB_DEFINED_NOT_CITED", "a2020"), {(x["code"], x["key"]) for x in f})

    def test_seeded_defective_reports_the_undefined_key(self):
        cited = cited_keys((SEEDED / "defective" / "manuscript.tex").read_text(encoding="utf-8"))
        bib = (SEEDED / "defective" / "refs.bib").read_text(encoding="utf-8")
        self.assertEqual([(x["code"], x["key"]) for x in check(bib, cited)],
                         [("BIB_CITED_NOT_DEFINED", "nowak2019")])


class TestCitedKeys(unittest.TestCase):
    def test_cite_variants_and_lists(self):
        tex = r"\cite{a, b} \citep[see][p.~4]{c} \textcite{d} % \cite{commented}"
        self.assertEqual(cited_keys(tex), {"a", "b", "c", "d"})

    def test_nocite_star_means_everything_is_cited(self):
        self.assertEqual(check(GOOD, cited_keys(r"\nocite{*}")), [])

    def test_biblatex_multicites_give_every_key(self):
        for tex, want in (
                (r"\cites{a}{b}", {"a", "b"}),
                (r"\autocites[see][p.~3]{a}[cf.]{b, c}", {"a", "b", "c"}),
                (r"\parencites{a}{b}{c}", {"a", "b", "c"}),
                (r"\textcites{a}[p.~2]{b}", {"a", "b"}),
                (r"\footcites{a}{b}", {"a", "b"}),
                (r"\Cites(see)(end){a}{b}", {"a", "b"})):
            with self.subTest(tex=tex):
                self.assertEqual(cited_keys(tex), want)

    def test_optional_arguments_may_be_separated_by_white_space(self):
        self.assertEqual(cited_keys(r"\citep[see] [p.~3]{k}"), {"k"})
        self.assertEqual(cited_keys("\\citep [see]\n [p.~3] {k}"), {"k"})

    def test_a_group_after_a_single_cite_is_not_a_key(self):
        self.assertEqual(cited_keys(r"\cite{a}{not a key}"), {"a"})


class TestDoi(unittest.TestCase):
    def test_normalise(self):
        for raw in ("https://doi.org/10.1016/J.X", "doi:10.1016/j.x", " 10.1016/J.X ",
                    "http://dx.doi.org/10.1016/j.x"):
            self.assertEqual(normalise_doi(raw), "10.1016/j.x")


E = parse_bib(GOOD)
RECORD = {"title": "Daylight in deep rooms", "year": 2020, "first_author_family": "Able",
          "notices": []}


def stub(**changes):
    return lambda doi: dict(RECORD, **changes)


class TestOnline(unittest.TestCase):
    def test_matching_record_has_no_findings(self):
        self.assertEqual(online_checks(E, stub()), [])

    def test_title_mismatch(self):
        f = online_checks(E, stub(title="Glare in classrooms: a field survey"))
        self.assertEqual([(x["code"], x["key"]) for x in f], [("DOI_IDENTITY_MISMATCH", "a2020")])

    def test_small_title_differences_are_tolerated(self):
        self.assertEqual(online_checks(E, stub(title="Daylight in Deep Rooms.")), [])

    def test_retracted_prefix_in_record_title_is_ignored_for_identity(self):
        f = online_checks(E, stub(title="RETRACTED: Daylight in deep rooms", notices=["retraction"]))
        self.assertEqual(codes(f), {"NOTICE_RETRACTION"})

    def test_year_off_by_one_is_tolerated(self):
        self.assertEqual(online_checks(E, stub(year=2021)), [])

    def test_year_off_by_two_is_a_mismatch(self):
        self.assertIn("DOI_IDENTITY_MISMATCH", codes(online_checks(E, stub(year=2022))))

    def test_first_author_mismatch(self):
        self.assertIn("DOI_IDENTITY_MISMATCH", codes(online_checks(E, stub(first_author_family="Baker"))))

    def test_accented_author_matches_ascii(self):
        e = parse_bib(GOOD.replace("Able, Ann", 'M\\"uller, Ann'))
        self.assertEqual(online_checks(e, stub(first_author_family="M\u00fcller")), [])

    def test_retraction_notice(self):
        self.assertIn("NOTICE_RETRACTION", codes(online_checks(E, stub(notices=["retraction"]))))

    def test_correction_and_concern_notices(self):
        f = online_checks(E, stub(notices=["correction", "expression_of_concern"]))
        self.assertEqual(codes(f), {"NOTICE_CORRECTION", "NOTICE_CONCERN"})

    def test_removal_is_treated_like_a_retraction(self):
        f = online_checks(E, stub(notices=["removal"]))
        self.assertEqual(codes(f), {"NOTICE_RETRACTION"})
        self.assertIn("removal", f[0]["message"])

    def test_new_version_and_new_edition_are_information_not_a_finding(self):
        from bib_check import INFO_CODES
        f = online_checks(E, stub(notices=["new_version", "new_edition"]))
        self.assertEqual(codes(f), {"NOTICE_NEW_VERSION"})
        self.assertLessEqual(codes(f), INFO_CODES)
        self.assertIn("new_edition", " ".join(x["message"] for x in f))

    def test_a_longer_title_that_only_starts_the_same_is_a_mismatch(self):
        e = parse_bib(GOOD.replace("Daylight in deep rooms",
                                   "Daylight in deep rooms of northern hemisphere office buildings"))
        self.assertIn("DOI_IDENTITY_MISMATCH", codes(online_checks(e, stub())))

    def test_subtitle_after_a_dash_or_question_mark_is_still_the_same_work(self):
        for title in ("Daylight in deep rooms - a new metric for annual daylight",
                      "Daylight in deep rooms? a new metric for annual daylight",
                      "Daylight in deep rooms \u2014 a new metric"):
            with self.subTest(title=title):
                e = parse_bib(GOOD.replace("Daylight in deep rooms", title))
                self.assertEqual(online_checks(e, stub()), [])

    def test_doi_that_does_not_resolve(self):
        self.assertEqual(codes(online_checks(E, lambda d: {"resolved": False})), {"DOI_NOT_RESOLVED"})

    def test_network_failure_is_not_checked(self):
        self.assertEqual(codes(online_checks(E, lambda d: None)), {"ONLINE_NOT_CHECKED"})

    def test_notice_lookup_failure_is_not_checked_not_clean(self):
        self.assertEqual(codes(online_checks(E, stub(notices_checked=False))), {"ONLINE_NOT_CHECKED"})

    def test_entry_without_doi_is_not_checked(self):
        e = parse_bib(GOOD.replace(", doi = {10.5555/a.2020}", ""))
        self.assertEqual(codes(online_checks(e, stub())), {"ONLINE_NOT_CHECKED"})

    def test_arxiv_datacite_doi_is_normalised(self):
        seen = []
        e = parse_bib(GOOD.replace("10.5555/a.2020", "https://doi.org/10.48550/ARXIV.2301.07041"))
        online_checks(e, lambda d: seen.append(d) or dict(RECORD))
        self.assertEqual(seen, ["10.48550/arxiv.2301.07041"])

    def test_seeded_title_defect_is_found_with_a_stub_record(self):
        bib = parse_bib((SEEDED / "defective" / "refs.bib").read_text(encoding="utf-8"))
        clean = {normalise_doi(e["fields"]["doi"]): e for e in parse_bib(CLEAN_BIB) if "doi" in e["fields"]}

        def fetch(doi):
            f = clean[doi]["fields"]
            return {"title": f["title"], "year": int(f["year"]),
                    "first_author_family": f["author"].split(",")[0], "notices": []}

        f = [x for x in online_checks(bib, fetch) if x["code"] != "ONLINE_NOT_CHECKED"]
        self.assertEqual([(x["code"], x["key"]) for x in f], [("DOI_IDENTITY_MISMATCH", "lee2022")])

    def test_subtitle_missing_from_the_record_is_not_a_mismatch(self):
        e = parse_bib(GOOD.replace("Daylight in deep rooms",
                                   "Daylight in deep rooms: a new metric for annual daylight"))
        self.assertEqual(online_checks(e, stub()), [])

    def test_compound_family_name_matches_its_first_part(self):
        e = parse_bib(GOOD.replace("Able, Ann", "Able-Jones, Ann"))
        self.assertEqual(online_checks(e, stub()), [])

    def test_one_notice_source_failing_is_reported(self):
        f = online_checks(E, stub(sources_failed=["OpenAlex"]))
        self.assertEqual(codes(f), {"ONLINE_NOT_CHECKED"})
        self.assertIn("OpenAlex", f[0]["message"])

    def test_summary_counts_three_states(self):
        from bib_check import summarise
        e = parse_bib(GOOD + GOOD.replace("a2020", "b2020").replace("10.5555/a.2020", "10.5555/b")
                      + GOOD.replace("a2020", "c2020").replace(", doi = {10.5555/a.2020}", ""))
        recs = {"10.5555/a.2020": dict(RECORD, notices=["retraction"]), "10.5555/b": dict(RECORD)}
        s = summarise(e, online_checks(e, lambda d: recs.get(d)))
        self.assertEqual(s, {"notice found": 1, "no notice found in the sources checked": 1,
                             "not checked": 1})


class TestDoiForms(unittest.TestCase):
    def test_braces_and_latex_escapes_are_removed(self):
        self.assertEqual(normalise_doi("{10.1016/j.x\\_y}"), "10.1016/j.x_y")
        self.assertEqual(normalise_doi("https://www.doi.org/10.1016/J.X"), "10.1016/j.x")


class TestRealFetch(unittest.TestCase):
    """The HTTP layer, with the network replaced by a table of canned replies."""

    def fetch_with(self, replies):
        import bib_check

        def fake(url, accept, agent):
            for needle, reply in replies.items():
                if needle in url:
                    if isinstance(reply, Exception):
                        raise reply
                    return reply
            raise AssertionError(url)

        from unittest import mock
        with mock.patch.object(bib_check, "_get_json", side_effect=fake):
            return bib_check.make_fetch(pause=0)("10.5555/a.2020")

    CSL = (200, {"title": ["Daylight in deep rooms"], "issued": {"date-parts": [[2020, 3]]},
                 "author": [{"family": "Able"}]})

    def test_404_is_not_resolved(self):
        self.assertEqual(self.fetch_with({"doi.org": (404, None)}), {"resolved": False})

    def test_network_error_is_none(self):
        self.assertIsNone(self.fetch_with({"doi.org": OSError("down")}))

    def test_http_protocol_error_is_none(self):
        import http.client
        self.assertIsNone(self.fetch_with({"doi.org": http.client.IncompleteRead(b"")}))

    def test_record_and_notices(self):
        rec = self.fetch_with({
            "doi.org": self.CSL,
            "crossref": (200, {"message": {"updated-by": [{"type": "retraction"}]}}),
            "openalex": (200, {"is_retracted": True})})
        self.assertEqual((rec["title"], rec["year"], rec["first_author_family"], rec["notices"],
                          rec["notices_checked"], rec["sources_failed"]),
                         ("Daylight in deep rooms", 2020, "Able", ["retraction"], True, []))

    def test_one_source_down_is_recorded(self):
        rec = self.fetch_with({"doi.org": self.CSL, "crossref": (200, {"message": {}}),
                               "openalex": OSError("down")})
        self.assertEqual((rec["notices_checked"], rec["sources_failed"]), (True, ["OpenAlex"]))

    def test_both_sources_down_means_notices_not_checked(self):
        rec = self.fetch_with({"doi.org": self.CSL, "crossref": OSError("x"), "openalex": (503, None)})
        self.assertFalse(rec["notices_checked"])


class TestMailto(unittest.TestCase):
    def test_email_goes_to_crossref_only(self):
        import bib_check
        from unittest import mock
        seen = []

        def fake(url, accept, agent):
            seen.append((url, agent))
            if "doi.org/" in url and "api." not in url:
                return 200, {"title": ["T"], "issued": {"date-parts": [[2020]]},
                             "author": [{"family": "A"}]}
            return 200, {"message": {}}

        with mock.patch.object(bib_check, "_get_json", side_effect=fake):
            bib_check.make_fetch("me@example.org", pause=0)("10.5555/a")
        by_host = {u.split("/")[2]: (u, a) for u, a in seen}
        for host in ("api.openalex.org", "doi.org"):
            self.assertNotIn("me@example.org", " ".join(by_host[host]), host)
            self.assertNotIn("me%40example.org", " ".join(by_host[host]), host)
        self.assertIn("me%40example.org", by_host["api.crossref.org"][0])

    def test_docs_do_not_claim_openalex_polite_pool(self):
        import bib_check
        self.assertNotIn("Crossref and OpenAlex for their polite pool", SCRIPT.read_text(encoding="utf-8"))
        self.assertNotIn("polite-pool convention of Crossref and OpenAlex", bib_check.__doc__)


class TestCli(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True)

    def test_empty_bib_is_not_clean(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            bib = Path(d) / "empty.bib"
            bib.write_text("% nothing here\n", encoding="utf-8")
            p = self.run_cli(str(bib))
        self.assertEqual(p.returncode, 2)
        self.assertIn("no entries", p.stdout + p.stderr)

    def test_missing_include_in_tex_is_reported(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            tex = Path(d) / "m.tex"
            tex.write_text("\\cite{a2020}\n\\input{gone}\n", encoding="utf-8")
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            p = self.run_cli(str(bib), "--tex", str(tex))
        self.assertIn("not checked", p.stdout)
        self.assertIn("gone", p.stdout)
        self.assertEqual(p.returncode, 3)

    def test_missing_include_does_not_hide_a_real_finding(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            tex = Path(d) / "m.tex"
            tex.write_text("\\cite{a2020,nokey}\n\\input{gone}\n", encoding="utf-8")
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            p = self.run_cli(str(bib), "--tex", str(tex))
        self.assertEqual(p.returncode, 1)

    def test_type_without_rules_exits_3_not_0(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD + "@artwork{o, title = {T}}\n", encoding="utf-8")
            p = self.run_cli(str(bib))
        self.assertIn("not checked: no field rules for @artwork (1 entries)", p.stdout)
        self.assertEqual(p.returncode, 3)

    def test_keyless_finding_is_printed_without_a_none_prefix(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD + "@artwork{o, title = {T}}\n", encoding="utf-8")
            p = self.run_cli(str(bib))
        self.assertNotIn("None", p.stdout)
        self.assertIn("BIB_TYPE_NOT_CHECKED", p.stdout)

    def test_exit_3_without_findings_says_the_result_is_not_clean(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD + "@artwork{o, title = {T}}\n", encoding="utf-8")
            p = self.run_cli(str(bib))
        self.assertEqual(p.returncode, 3)
        self.assertIn("NOT a clean result", p.stdout)

    def test_clean_run_does_not_claim_a_gap(self):
        import tempfile
        with tempfile.TemporaryDirectory() as d:
            from pathlib import Path
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            p = self.run_cli(str(bib))
        self.assertEqual(p.returncode, 0)
        self.assertNotIn("NOT a clean result", p.stdout)

    def test_compiles_and_helps_on_python39(self):
        import os
        py = "/usr/bin/python3"
        if not os.path.exists(py):
            self.skipTest("no /usr/bin/python3")
        for cmd in ([py, "-m", "py_compile", str(SCRIPT)], [py, str(SCRIPT), "--help"]):
            p = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(p.returncode, 0, p.stderr)

    def test_offline_cli_on_defective_pair(self):
        d = SEEDED / "defective"
        p = subprocess.run([sys.executable, str(SCRIPT), str(d / "refs.bib"), "--tex",
                            str(d / "manuscript.tex")], capture_output=True, text=True)
        self.assertEqual(p.returncode, 1)
        self.assertIn("nowak2019", p.stdout)
        self.assertIn("online checks: not run", p.stdout)


if __name__ == "__main__":
    unittest.main()


# --------------------------------------------------------------------------- verified list
# A citation is a fact. The writer may cite only a key whose entry was checked against a real
# record. `--online --record` writes that list; `--tex --verified` checks a draft against it.

import contextlib
import io
import json
import tempfile
from pathlib import Path
from unittest import mock

import bib_check

try:
    import yaml
except ImportError:                                           # pragma: no cover
    yaml = None

TEX = r"As shown by \cite{a2020}, deep rooms are dark."
TWO = GOOD + """
@book{b2019, author = {Baker, Bea}, title = {Glare}, publisher = {P}, year = {2019}}
"""


def run_main(argv, fetch=None):
    """Run bib_check in-process with a fake network. Returns (exit code, stdout)."""
    out = io.StringIO()
    patches = [mock.patch("sys.argv", ["bib_check.py", *argv])]
    if fetch is not None:
        patches.append(mock.patch.object(bib_check, "make_fetch", lambda *a, **k: fetch))
    with contextlib.ExitStack() as stack:
        for p in patches:
            stack.enter_context(p)
        stack.enter_context(contextlib.redirect_stdout(out))
        stack.enter_context(contextlib.redirect_stderr(io.StringIO()))
        code = bib_check.main()
    return code, out.getvalue()


class TestIdentityVerified(unittest.TestCase):
    def test_matching_record_marks_the_entry_verified(self):
        ok = set()
        self.assertEqual(online_checks(E, stub(), ok), [])
        self.assertEqual(ok, {"a2020"})

    def test_mismatch_unresolved_or_failed_is_not_verified(self):
        for fetch in (stub(title="Glare in classrooms: a field survey"),
                      lambda d: {"resolved": False}, lambda d: None):
            with self.subTest(fetch=fetch):
                ok = set()
                online_checks(E, fetch, ok)
                self.assertEqual(ok, set())


class TestTooLittleToCompare(unittest.TestCase):
    def run_check(self, bib, **record):
        ok, ev = set(), {}
        found = online_checks(parse_bib(bib), stub(**record), ok, ev)
        return found, ok, ev

    def test_entry_with_only_a_doi_is_not_verified(self):
        found, ok, _ = self.run_check("@article{bare, doi = {10.5555/a.2020}}",
                                      title="A different work", year=2001)
        self.assertEqual(ok, set())
        msg = [f for f in found if f["code"] == "RECORD_NOT_WRITTEN"]
        self.assertEqual(len(msg), 1)
        self.assertIn("not checked: too little metadata to compare", msg[0]["message"])
        self.assertEqual(msg[0]["reason"], "too_little_metadata")

    def test_record_without_year_and_author_is_not_verified(self):
        found, ok, _ = self.run_check(GOOD, year=None, first_author_family=None)
        self.assertEqual(ok, set())
        self.assertIn("RECORD_NOT_WRITTEN", codes(found))

    def test_title_and_year_alone_are_enough_and_the_evidence_is_named(self):
        found, ok, ev = self.run_check(GOOD, first_author_family=None)
        self.assertEqual(ok, {"a2020"})
        self.assertEqual(ev["a2020"], {"first_author": False, "year": True})
        self.assertEqual(found, [])

    def test_year_and_author_without_a_title_are_not_enough(self):
        found, ok, _ = self.run_check(GOOD.replace("title = {Daylight in deep rooms}, ", ""))
        self.assertEqual(ok, set())

    def test_a_work_with_a_retraction_or_concern_is_not_recorded(self):
        for notice in ("retraction", "withdrawal", "removal", "expression_of_concern"):
            with self.subTest(notice=notice):
                found, ok, _ = self.run_check(GOOD, notices=[notice])
                self.assertEqual(ok, set())
                skipped = [f for f in found if f["code"] == "RECORD_NOT_WRITTEN"]
                self.assertIn("not recorded: carries a notice", skipped[0]["message"])

    def test_a_correction_does_not_block_the_record(self):
        _, ok, _ = self.run_check(GOOD, notices=["correction"])
        self.assertEqual(ok, {"a2020"})


@unittest.skipIf(yaml is None, "pyyaml not installed")
class TestRecordAndVerify(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.bib = self.dir / "refs.bib"
        self.bib.write_text(TWO, encoding="utf-8")
        self.tex = self.dir / "main.tex"
        self.tex.write_text(TEX, encoding="utf-8")
        (self.dir / ".paper").mkdir()
        self.record = self.dir / ".paper" / "verified-refs.yml"

    def tearDown(self):
        self._tmp.cleanup()

    def rows(self):
        return {r["key"]: r for r in yaml.safe_load(self.record.read_text(encoding="utf-8"))["references"]}

    def test_record_writes_each_verified_entry(self):
        code, _ = run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        row = self.rows()["a2020"]
        self.assertEqual((row["method"], row["doi"]), ("doi", "10.5555/a.2020"))
        self.assertNotIn("b2019", self.rows())            # no DOI: not verified online

    def test_record_needs_online(self):
        code, _ = run_main([str(self.bib), "--record", str(self.record)])
        self.assertEqual(code, 2)
        self.assertFalse(self.record.exists())

    def test_record_keeps_a_manual_row_the_author_wrote(self):
        self.record.write_text(
            'version: 1\nreferences:\n  - key: "b2019"\n    method: manual\n'
            '    title: "Glare"\n    checked_on: "2026-11-01"\n'
            '    note: "read the printed book, library copy"\n', encoding="utf-8")
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        self.assertEqual(self.rows()["b2019"]["method"], "manual")
        self.assertIn("a2020", self.rows())

    def test_record_drops_a_row_whose_doi_no_longer_matches(self):
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        run_main([str(self.bib), "--online", "--record", str(self.record)],
                 stub(title="Glare in classrooms: a field survey"))
        self.assertNotIn("a2020", self.rows())

    def test_record_keeps_an_earlier_row_when_the_request_failed(self):
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        run_main([str(self.bib), "--online", "--record", str(self.record)], lambda d: None)
        self.assertIn("a2020", self.rows())

    def test_record_refuses_to_overwrite_a_file_it_cannot_read(self):
        self.record.write_text("references: [unclosed\n", encoding="utf-8")
        before = self.record.read_bytes()
        code, _ = run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        self.assertEqual(code, 2)
        self.assertEqual(self.record.read_bytes(), before)

    def test_any_character_reads_back_unchanged(self):
        odd = ('Glare "quoted" \\ back, café, line sep, tab\there, del\x7f, '
               'nel\x85, bom﻿, colon: #hash, null, yes, 1e3')
        self.assertEqual(yaml.safe_load("v: " + bib_check._yaml_str(odd))["v"], odd)

    def test_record_keeps_the_title_the_entry_holds(self):
        title = 'Glare "quoted", café: #1'
        self.bib.write_text(GOOD.replace("Daylight in deep rooms", title), encoding="utf-8")
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub(title=title))
        self.assertEqual(self.rows()["a2020"]["title"], title)

    def test_an_empty_list_is_still_a_list(self):
        run_main([str(self.bib), "--online", "--record", str(self.record)],
                 lambda d: {"resolved": False})
        self.assertEqual(yaml.safe_load(self.record.read_text(encoding="utf-8"))["references"], [])

    def test_draft_citing_only_verified_keys_passes(self):
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertNotIn("CITE_NOT_VERIFIED", out)
        self.assertNotIn("CITE_VERIFICATION_STALE", out)

    def test_cited_key_with_no_row_is_a_finding(self):
        self.tex.write_text(TEX + r" See also \cite{b2019}.", encoding="utf-8")
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertEqual(code, 1)
        self.assertIn("CITE_NOT_VERIFIED", out)
        self.assertIn("b2019", out)

    def test_entry_changed_after_verification_is_stale(self):
        run_main([str(self.bib), "--online", "--record", str(self.record)], stub())
        self.bib.write_text(TWO.replace("10.5555/a.2020", "10.5555/a.2021"), encoding="utf-8")
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertEqual(code, 1)
        self.assertIn("CITE_VERIFICATION_STALE", out)

    def test_manual_row_needs_a_note(self):
        self.tex.write_text(r"\cite{b2019}", encoding="utf-8")
        self.record.write_text('version: 1\nreferences:\n  - key: "b2019"\n    method: manual\n'
                               '    title: "Glare"\n    checked_on: "2026-11-01"\n', encoding="utf-8")
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertEqual(code, 1)
        self.assertIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_manual_row_with_a_note_is_accepted(self):
        self.tex.write_text(r"\cite{b2019}", encoding="utf-8")
        self.record.write_text('version: 1\nreferences:\n  - key: "b2019"\n    method: manual\n'
                               '    title: "Glare"\n    checked_on: "2026-11-01"\n'
                               '    note: "read the printed book"\n', encoding="utf-8")
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertNotIn("CITE_NOT_VERIFIED", out)
        self.assertNotIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_verified_needs_tex(self):
        code, _ = run_main([str(self.bib), "--verified", str(self.record)])
        self.assertEqual(code, 2)

    def test_missing_verified_file_is_not_checked_never_clean(self):
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])
        self.assertEqual(code, 3)
        self.assertIn("not checked", out)


MANUAL = ('version: 1\nreferences:\n  - key: "b2019"\n    method: manual\n'
          '    title: "Glare"\n    checked_on: "2026-11-01"\n'
          '    note: "read the printed book, library copy"\n')


@unittest.skipIf(yaml is None, "pyyaml not installed")
class TestVerifiedListRows(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.bib = self.dir / "refs.bib"
        self.bib.write_text(TWO, encoding="utf-8")
        self.tex = self.dir / "main.tex"
        self.tex.write_text(r"\cite{a2020}", encoding="utf-8")
        self.record = self.dir / "verified-refs.yml"

    def tearDown(self):
        self._tmp.cleanup()

    def rows(self):
        return {r["key"]: r for r in yaml.safe_load(self.record.read_text(encoding="utf-8"))["references"]}

    def record_run(self, fetch=None):
        return run_main([str(self.bib), "--online", "--record", str(self.record)], fetch or stub())

    def verify(self, cited=r"\cite{a2020}"):
        self.tex.write_text(cited, encoding="utf-8")
        return run_main([str(self.bib), "--tex", str(self.tex), "--verified", str(self.record)])

    # record: what is written
    def test_doi_row_holds_first_author_and_year(self):
        self.record_run()
        row = self.rows()["a2020"]
        self.assertEqual((row["first_author"], row["year"], row["title"]),
                         ("Able", 2020, "Daylight in deep rooms"))
        self.assertRegex(str(row["checked_on"]), r"^\d{4}-\d{2}-\d{2}$")

    def test_bare_doi_entry_writes_no_row_and_says_why(self):
        self.bib.write_text("@article{bare, doi = {10.5555/a.2020}}", encoding="utf-8")
        code, out = self.record_run(stub(title="Another work"))
        self.assertEqual(self.rows(), {})
        self.assertIn("RECORD_NOT_WRITTEN", out)
        self.assertIn("too little metadata", out)
        self.assertNotEqual(code, 0)

    def test_retracted_work_writes_no_row_and_the_run_has_a_finding(self):
        code, out = self.record_run(stub(notices=["retraction"]))
        self.assertNotIn("a2020", self.rows())
        self.assertIn("not recorded: carries a notice", out)
        self.assertEqual(code, 1)

    def test_an_earlier_row_of_a_work_that_is_retracted_now_is_dropped(self):
        self.record_run()
        self.record_run(stub(notices=["retraction"]))
        self.assertNotIn("a2020", self.rows())

    # record: manual rows
    def test_manual_row_for_a_key_not_in_the_bib_is_kept_and_reported(self):
        self.record.write_text(MANUAL.replace("b2019", "en17037"), encoding="utf-8")
        code, out = self.record_run()
        self.assertIn("en17037", self.rows())
        self.assertIn("VERIFIED_ROW_ORPHAN", out)
        self.assertIn("kept", out)

    def test_manual_row_is_never_replaced_by_a_doi_row(self):
        self.bib.write_text(GOOD, encoding="utf-8")
        self.record.write_text(MANUAL.replace("b2019", "a2020").replace('"Glare"', '"Daylight in deep rooms"'),
                               encoding="utf-8")
        self.record_run()
        row = self.rows()["a2020"]
        self.assertEqual(row["method"], "manual")
        self.assertEqual(row["note"], "read the printed book, library copy")
        self.assertEqual((row["doi"], row["first_author"], row["year"]),
                         ("10.5555/a.2020", "Able", 2020))

    def test_manual_row_is_kept_and_reported_when_its_doi_did_not_match(self):
        self.bib.write_text(GOOD, encoding="utf-8")
        self.record.write_text(MANUAL.replace("b2019", "a2020"), encoding="utf-8")
        code, out = self.record_run(stub(title="Glare in classrooms: a field survey"))
        self.assertEqual(self.rows()["a2020"]["method"], "manual")
        self.assertIn("DOI_IDENTITY_MISMATCH", out)
        self.assertIn("VERIFIED_ROW_KEPT_MISMATCH", out)

    # verify: stale
    def stale(self, edit):
        self.record_run()
        self.bib.write_text(edit(TWO), encoding="utf-8")
        code, out = self.verify()
        return code, out

    def test_changed_first_author_is_stale(self):
        code, out = self.stale(lambda t: t.replace("Able, Ann", "Baker, Ann"))
        self.assertEqual(code, 1)
        self.assertIn("CITE_VERIFICATION_STALE", out)

    def test_changed_year_is_stale(self):
        code, out = self.stale(lambda t: t.replace("year = {2020}", "year = {2021}"))
        self.assertIn("CITE_VERIFICATION_STALE", out)

    def test_a_lengthened_title_is_stale(self):
        code, out = self.stale(lambda t: t.replace("Daylight in deep rooms",
                                                   "Daylight in deep rooms: a new metric"))
        self.assertIn("CITE_VERIFICATION_STALE", out)

    def test_a_case_or_punctuation_change_of_the_title_is_not_stale(self):
        code, out = self.stale(lambda t: t.replace("Daylight in deep rooms", "Daylight in Deep Rooms."))
        self.assertNotIn("CITE_VERIFICATION_STALE", out)

    def test_manual_row_is_compared_too(self):
        self.record.write_text(MANUAL, encoding="utf-8")
        self.bib.write_text(TWO.replace("{Glare}", "{Glare and its control}"), encoding="utf-8")
        code, out = self.verify(r"\cite{b2019}")
        self.assertIn("CITE_VERIFICATION_STALE", out)

    def test_manual_row_that_matches_is_accepted(self):
        self.record.write_text(MANUAL, encoding="utf-8")
        code, out = self.verify(r"\cite{b2019}")
        self.assertEqual(code, 0)

    # verify: complete rows
    def test_manual_row_without_a_title_is_incomplete(self):
        self.record.write_text(MANUAL.replace('    title: "Glare"\n', ""), encoding="utf-8")
        code, out = self.verify(r"\cite{b2019}")
        self.assertIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_manual_note_without_content_is_incomplete(self):
        for note in (".", "ok", "done checked"):
            with self.subTest(note=note):
                self.record.write_text(MANUAL.replace("read the printed book, library copy", note),
                                       encoding="utf-8")
                code, out = self.verify(r"\cite{b2019}")
                self.assertIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_checked_on_must_be_an_iso_date(self):
        for value in ('"x"', '"2026-13-45"', '"19 November 2026"'):
            with self.subTest(value=value):
                self.record.write_text(MANUAL.replace('"2026-11-01"', value), encoding="utf-8")
                code, out = self.verify(r"\cite{b2019}")
                self.assertIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_an_unquoted_yaml_date_is_accepted(self):
        self.record.write_text(MANUAL.replace('"2026-11-01"', "2026-11-01"), encoding="utf-8")
        code, out = self.verify(r"\cite{b2019}")
        self.assertNotIn("VERIFIED_ROW_INCOMPLETE", out)

    def test_doi_row_in_the_old_format_is_incomplete(self):
        self.record.write_text('version: 1\nreferences:\n  - key: "a2020"\n    method: doi\n'
                               '    doi: "10.5555/a.2020"\n    title: "Daylight in deep rooms"\n'
                               '    checked_on: "2026-11-01"\n', encoding="utf-8")
        code, out = self.verify()
        self.assertIn("VERIFIED_ROW_INCOMPLETE", out)

    # nocite
    def test_nocite_star_checks_every_entry_in_the_bib(self):
        self.record_run()
        code, out = self.verify(r"\nocite{*}")
        self.assertEqual(code, 1)
        self.assertIn("CITE_NOT_VERIFIED", out)
        self.assertIn("b2019", out)

    def test_multicite_second_key_is_checked(self):
        self.record_run()
        code, out = self.verify(r"\cites{a2020}{b2019}")
        self.assertIn("CITE_NOT_VERIFIED", out)
        self.assertIn("b2019", out)

    # C-1
    def test_tex_that_is_not_a_tex_file_exits_2_and_points_to_the_export_route(self):
        docx = self.dir / "paper.docx"
        docx.write_bytes(b"PK")
        code, out = run_main([str(self.bib), "--tex", str(docx), "--verified", str(self.record)])
        self.assertEqual(code, 2)
        err = io.StringIO()
        with mock.patch("sys.argv", ["bib_check.py", str(self.bib), "--tex", str(docx)]), \
                contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
            bib_check.main()
        self.assertIn("LaTeX sources only", err.getvalue())
        self.assertIn("export", err.getvalue())

    def test_verified_with_no_cited_key_is_not_checked_and_exits_3(self):
        self.record_run()
        code, out = self.verify("No citation here.")
        self.assertEqual(code, 3)
        self.assertIn("citation coverage: not checked", out)


class TestSetupCommandsAreNotKeys(unittest.TestCase):
    def test_natbib_and_biblatex_setup_commands_give_no_key(self):
        for tex in (r"\setcitestyle{authoryear,round}", r"\citestyle{plain}",
                    r"\citetext{see}", r"\citeindextrue", r"\citeindexfalse",
                    r"\DeclareCiteCommand{\mycite}{}{}{}{}", r"\bibcite{k}{1}",
                    r"\citation{k}"):
            with self.subTest(tex=tex):
                self.assertEqual(cited_keys(tex), set())

    def test_defcitealias_first_argument_is_the_only_key(self):
        self.assertEqual(cited_keys(r"\defcitealias{k}{Paper I}"), {"k"})

    def test_real_cites_still_work_next_to_setup_commands(self):
        tex = r"\setcitestyle{authoryear} \citep{a} \citet[p.~2]{b,c}"
        self.assertEqual(cited_keys(tex), {"a", "b", "c"})


class TestFamilyNameMatch(unittest.TestCase):
    def mismatch(self, author, record_family):
        bib = GOOD.replace("Able, Ann", author)
        return "DOI_IDENTITY_MISMATCH" in codes(
            online_checks(parse_bib(bib), stub(first_author_family=record_family)))

    def test_a_substring_is_not_a_match(self):
        self.assertTrue(self.mismatch("Li, X.", "Williams"))
        self.assertTrue(self.mismatch("Williams, X.", "Li"))

    def test_whole_names_match_after_folding(self):
        self.assertFalse(self.mismatch("M\\\"uller, A.", "MULLER"))
        self.assertFalse(self.mismatch("Smith-Jones, A.", "Smith Jones"))

    def test_a_particle_family_matches_its_last_word(self):
        self.assertFalse(self.mismatch("van der Berg, J.", "Berg"))
        self.assertFalse(self.mismatch("Berg, J.", "van der Berg"))
        self.assertTrue(self.mismatch("van der Berg, J.", "Bergmann"))


class TestNoNoticeSourceNoRow(unittest.TestCase):
    def test_unread_notices_write_no_row(self):
        ok = set()
        found = online_checks(E, stub(notices_checked=False), ok)
        self.assertEqual(ok, set())
        skipped = [f for f in found if f["code"] == "RECORD_NOT_WRITTEN"]
        self.assertEqual(len(skipped), 1)
        self.assertIn("not checked: the notices could not be read", skipped[0]["message"])
        self.assertEqual(skipped[0]["reason"], "request_failed")

    def test_one_notice_source_answering_is_enough(self):
        ok = set()
        online_checks(E, stub(notices_checked=True, sources_failed=["Crossref"]), ok)
        self.assertEqual(ok, {"a2020"})

    def test_cli_exits_3_and_keeps_an_earlier_doi_row(self):
        with tempfile.TemporaryDirectory() as d:
            bib, rec = Path(d) / "r.bib", Path(d) / "v.yml"
            bib.write_text(GOOD, encoding="utf-8")
            run_main([str(bib), "--online", "--record", str(rec)], stub())
            code, out = run_main([str(bib), "--online", "--record", str(rec)],
                                 stub(notices_checked=False))
            self.assertEqual(code, 3)
            self.assertIn("RECORD_NOT_WRITTEN", out)
            if yaml is not None:
                keys = [r["key"] for r in yaml.safe_load(rec.read_text())["references"]]
                self.assertEqual(keys, ["a2020"])

    def test_cli_writes_nothing_when_notices_were_never_read(self):
        with tempfile.TemporaryDirectory() as d:
            bib, rec = Path(d) / "r.bib", Path(d) / "v.yml"
            bib.write_text(GOOD, encoding="utf-8")
            code, _ = run_main([str(bib), "--online", "--record", str(rec)],
                               stub(notices_checked=False))
            self.assertEqual(code, 3)
            if rec.exists() and yaml is not None:
                self.assertEqual(yaml.safe_load(rec.read_text())["references"], [])


class TestJsonPath(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), *args],
                              capture_output=True, text=True)

    def test_unwritable_json_path_exits_2_before_the_run_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as d:
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            p = self.run_cli(str(bib), "--json", "/nonexistent/x.json")
        self.assertEqual(p.returncode, 2)
        self.assertIn("x.json", p.stderr)
        self.assertNotIn("Traceback", p.stderr)
        self.assertNotIn("entries", p.stdout)             # refused before the run

    def test_json_path_that_is_a_folder_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            p = self.run_cli(str(bib), "--json", d)
        self.assertEqual(p.returncode, 2)
        self.assertNotIn("Traceback", p.stderr)

    def test_a_write_error_at_the_end_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bib = Path(d) / "r.bib"
            bib.write_text(GOOD, encoding="utf-8")
            with mock.patch.object(Path, "write_text", side_effect=OSError("disk full")), \
                    mock.patch("sys.argv", ["bib_check.py", str(bib), "--json", d + "/o.json"]), \
                    contextlib.redirect_stdout(io.StringIO()), \
                    contextlib.redirect_stderr(io.StringIO()) as err:
                code = bib_check.main()
        self.assertEqual(code, 2)
        self.assertIn("disk full", err.getvalue())

    def test_help_names_both_files_it_can_write(self):
        p = self.run_cli("--help")
        self.assertIn("--json", p.stdout)
        self.assertNotIn("writes one file", p.stdout)
        self.assertIn("comments", p.stdout)


class TestNoCitationFound(unittest.TestCase):
    def test_tex_with_no_citation_is_not_checked_with_or_without_verified(self):
        with tempfile.TemporaryDirectory() as d:
            bib, tex = Path(d) / "r.bib", Path(d) / "m.tex"
            bib.write_text(GOOD, encoding="utf-8")
            tex.write_text("No citations here.\n", encoding="utf-8")
            code, out = run_main([str(bib), "--tex", str(tex)])
            self.assertEqual(code, 3)
            self.assertIn("citation coverage: not checked: no citation command was found in "
                          + str(tex), out)
            code, out = run_main([str(bib), "--tex", str(tex), "--verified",
                                  str(Path(d) / "none.yml")])
            self.assertEqual(code, 3)
            self.assertIn("no citation command was found", out)


@unittest.skipIf(yaml is None, "pyyaml not installed")
class TestRecordNeverDeletesAuthorRows(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.bib = self.dir / "refs.bib"
        self.bib.write_text(TWO, encoding="utf-8")
        self.tex = self.dir / "main.tex"
        self.tex.write_text(r"\cite{a2020,b2019}", encoding="utf-8")
        self.record = self.dir / "v.yml"

    def tearDown(self):
        self._tmp.cleanup()

    def record_run(self):
        return run_main([str(self.bib), "--online", "--record", str(self.record)], stub())

    def refused(self, text):
        self.record.write_text(text, encoding="utf-8")
        before = self.record.read_bytes()
        code, _ = self.record_run()
        self.assertEqual(code, 2)
        self.assertEqual(self.record.read_bytes(), before)
        code, out = run_main([str(self.bib), "--tex", str(self.tex), "--verified",
                              str(self.record)])
        self.assertEqual(code, 3)
        self.assertIn("VERIFIED_LIST_NOT_CHECKED", out)

    def test_misspelt_top_key_is_refused(self):
        self.refused('version: 1\nrefrences:\n  - key: "b2019"\n    method: manual\n'
                     '    title: "Glare"\n    checked_on: "2026-11-01"\n    note: "read it twice"\n')

    def test_references_that_is_not_a_list_is_refused(self):
        self.refused('version: 1\nreferences: "b2019"\n')

    def test_a_scalar_row_is_refused(self):
        self.refused('version: 1\nreferences:\n  - "b2019"\n')

    def test_a_row_without_a_key_is_refused(self):
        self.refused('version: 1\nreferences:\n  - Key: "b2019"\n    method: manual\n')

    def test_a_row_with_an_unknown_method_is_kept_and_reported(self):
        for method in ('method: Manual\n    ', ''):
            with self.subTest(method=method):
                self.record.write_text(
                    'version: 1\nreferences:\n  - key: "b2019"\n    ' + method +
                    'title: "Glare"\n    checked_on: "2026-11-01"\n    note: "read it twice"\n',
                    encoding="utf-8")
                code, out = self.record_run()
                rows = yaml.safe_load(self.record.read_text())["references"]
                self.assertEqual([r["key"] for r in rows if r["key"] == "b2019"], ["b2019"])
                self.assertEqual(len([r for r in rows if r["key"] == "b2019"]), 1)
                self.assertIn("VERIFIED_ROW_INCOMPLETE", out)
                self.assertEqual(code, 1)

    def test_extra_fields_keep_their_type(self):
        self.record.write_text(
            'version: 1\nreferences:\n  - key: "b2019"\n    method: manual\n'
            '    title: "Glare"\n    checked_on: "2026-11-01"\n    note: "read it twice"\n'
            '    sections: [5, 6]\n    online_copy: false\n    pages: 12\n', encoding="utf-8")
        self.record_run()
        row = {r["key"]: r for r in yaml.safe_load(self.record.read_text())["references"]}["b2019"]
        self.assertEqual(row["sections"], [5, 6])
        self.assertIs(row["online_copy"], False)
        self.assertEqual(row["pages"], 12)

