import os
import ssl
import unittest
import urllib.error
from unittest import mock

from tests import _paths  # noqa: F401
import fetch_oa_pdf

SYSTEM_BUNDLES = ("/etc/ssl/cert.pem", "/etc/ssl/certs/ca-certificates.crt",
                  "/etc/pki/tls/certs/ca-bundle.crt")


class TestBibtexReply(unittest.TestCase):
    def reply(self, body):
        return mock.patch.object(fetch_oa_pdf, "get", return_value=(body, "https://x", "text/html"))

    def test_bibtex_reply_is_returned(self):
        with self.reply(b"  @article{a, title={T}}\n"):
            self.assertEqual(fetch_oa_pdf.crossref_bibtex("10.5555/a"), "@article{a, title={T}}")

    def test_non_bibtex_reply_is_rejected(self):
        with self.reply(b"<html><body>Not found</body></html>"):
            self.assertIsNone(fetch_oa_pdf.crossref_bibtex("10.5555/a"))

    def test_rejected_reply_is_recorded_as_an_error(self):
        fetch_oa_pdf.ERRORS.clear()
        with self.reply(b"<html></html>"):
            fetch_oa_pdf.crossref_bibtex("10.5555/a")
        self.assertTrue(any("not BibTeX" in e for e in fetch_oa_pdf.ERRORS))


class TestFailedLookupIsNotAFinding(unittest.TestCase):
    """A request that failed is 'not checked', never a statement about the paper."""

    def run_main(self, argv, get_side_effect):
        """Run the command with a fake network. Output files go to a temporary folder unless
        the test names one, so no test writes into the working directory."""
        import contextlib
        import io
        import tempfile
        err = io.StringIO()
        with tempfile.TemporaryDirectory() as scratch:
            if "--out" not in argv:
                argv = [*argv, "--out", scratch]
            with mock.patch.object(fetch_oa_pdf, "get", side_effect=get_side_effect), \
                    mock.patch.object(fetch_oa_pdf.time, "sleep"), \
                    mock.patch("sys.argv", ["fetch_oa_pdf.py", *argv]), \
                    contextlib.redirect_stderr(err):
                code = fetch_oa_pdf.main()
        return code, err.getvalue()

    def test_bibtex_only_with_network_down_is_not_checked(self):
        import tempfile
        down = urllib.error.URLError("network is down")
        with tempfile.TemporaryDirectory() as d:
            code, log = self.run_main(["10.5555/a", "--bibtex-only", "--json", d + "/r.json"], down)
            import json
            status = json.load(open(d + "/r.json"))[0]["status"]
        self.assertEqual(status, "not checked")
        self.assertNotIn("metadata only", log)
        self.assertIn("not checked:", log)
        self.assertEqual(code, 3)

    def test_download_network_error_is_not_called_open_access(self):
        import tempfile
        down = urllib.error.URLError("network is down")
        with tempfile.TemporaryDirectory() as d:
            code, log = self.run_main(["2301.07041", "--out", d, "--json", d + "/r.json"], down)
            import json
            status = json.load(open(d + "/r.json"))[0]["status"]
        self.assertEqual(status, "not checked")
        self.assertNotIn("IS open access", log)
        self.assertNotIn("manual download", log)
        self.assertIn("not checked:", log)
        self.assertEqual(code, 3)

    def test_host_refusal_keeps_the_manual_download_answer_and_exit_0(self):
        import tempfile
        refuse = urllib.error.HTTPError("https://x", 403, "Forbidden", {}, None)
        with tempfile.TemporaryDirectory() as d:
            code, log = self.run_main(["2301.07041", "--out", d], refuse)
        self.assertEqual(code, 0)
        self.assertIn("refuse", log)

    def test_no_open_access_found_after_clean_lookups_exits_0(self):
        with mock.patch.object(fetch_oa_pdf, "crossref_bibtex", return_value="@a{b}"):
            code, log = self.run_main(["10.5555/a", "--email", "x@example.org"],
                                      lambda *a, **k: {})
        self.assertIn("NO open-access copy found", log)
        self.assertEqual(code, 0)

    def test_failed_lookups_with_no_candidates_exit_3(self):
        down = urllib.error.URLError("network is down")
        code, log = self.run_main(["10.5555/a", "--email", "x@example.org"], down)
        self.assertEqual(code, 3)
        self.assertNotIn("NO open-access copy found", log)

    def test_bibtex_failure_alone_does_not_turn_a_clean_oa_answer_into_not_checked(self):
        with mock.patch.object(fetch_oa_pdf, "crossref_bibtex",
                               side_effect=lambda d: fetch_oa_pdf.ERRORS.append("BibTeX: down")):
            code, log = self.run_main(["10.5555/a", "--email", "x@example.org"],
                                      lambda *a, **k: {})
        self.assertIn("NO open-access copy found", log)
        self.assertEqual(code, 3)          # the BibTeX record was not fetched: still reported


class TestUnrecognisedAndBatch(unittest.TestCase):
    run_main = TestFailedLookupIsNotAFinding.run_main

    def test_unrecognised_identifier_among_good_ones_exits_3(self):
        with mock.patch.object(fetch_oa_pdf, "crossref_bibtex", return_value="@a{b}"):
            code, log = self.run_main(["10.5555/a", "notanidentifier", "--email", "x@example.org"],
                                      lambda *a, **k: {})
        self.assertEqual(code, 3)
        self.assertIn("unrecognised", log)

    def test_only_unrecognised_identifiers_exit_2(self):
        code, log = self.run_main(["notanidentifier"], lambda *a, **k: {})
        self.assertEqual(code, 2)

    def test_missing_batch_file_exits_2_without_a_traceback(self):
        code, log = self.run_main(["--batch", "/nonexistent/dois.txt"], lambda *a, **k: {})
        self.assertEqual(code, 2)
        self.assertIn("dois.txt", log)
        self.assertNotIn("Traceback", log)


class TestPmid(unittest.TestCase):
    def test_bare_numbers_are_pubmed_ids_only_with_7_or_8_digits(self):
        n = fetch_oa_pdf.normalise
        self.assertEqual(n("1234567"), ("pmid", "1234567"))
        self.assertEqual(n("31452104"), ("pmid", "31452104"))
        for stray in ("2021", "7", "123456"):
            self.assertEqual(n(stray)[0], "unknown", stray)

    def test_prefixed_pubmed_ids_may_be_short(self):
        n = fetch_oa_pdf.normalise
        self.assertEqual(n("PMID:31452104"), ("pmid", "31452104"))
        self.assertEqual(n("pmid: 12345"), ("pmid", "12345"))
        self.assertEqual(n("PMID:7"), ("pmid", "7"))

    def test_other_patterns_keep_priority(self):
        n = fetch_oa_pdf.normalise
        self.assertEqual(n("2301.07041")[0], "arxiv")
        self.assertEqual(n("PMC7906746")[0], "pmc")
        self.assertEqual(n("10.1016/j.x.1")[0], "doi")
        self.assertEqual(n("123456789")[0], "unknown")


class TestEuropePmcAddress(unittest.TestCase):
    def search(self, **result):
        base = {"pmcid": "PMC7906746", "isOpenAccess": "Y", "license": "cc by"}
        base.update(result)
        return {"resultList": {"result": [base]}}

    def candidates(self, js):
        with mock.patch.object(fetch_oa_pdf, "get", return_value=js):
            return fetch_oa_pdf.via_europepmc("PMC7906746", "pmc")

    def test_pdf_address_comes_from_the_search_result(self):
        js = self.search(fullTextUrlList={"fullTextUrl": [
            {"documentStyle": "html", "url": "https://example.org/page"},
            {"documentStyle": "pdf", "url": "https://europepmc.org/articles/PMC7906746?pdf=render"}]})
        out = self.candidates(js)
        self.assertEqual([c["url"] for c in out],
                         ["https://europepmc.org/articles/PMC7906746?pdf=render"])

    def test_no_pdf_address_means_no_candidate_and_no_fulltextpdf_guess(self):
        js = self.search(fullTextUrlList={"fullTextUrl": [
            {"documentStyle": "html", "url": "https://example.org/page"}]})
        self.assertEqual(self.candidates(js), [])
        self.assertEqual(self.candidates(self.search()), [])


class TestEuropePmcLinkChoice(TestEuropePmcAddress):
    def link(self, url, code=None, style="pdf"):
        d = {"documentStyle": style, "url": url}
        if code:
            d["availabilityCode"] = code
        return d

    def urls(self, *links):
        js = self.search(fullTextUrlList={"fullTextUrl": list(links)})
        return [c["url"] for c in self.candidates(js)]

    def test_open_link_beats_a_paywalled_one_listed_first(self):
        self.assertEqual(
            self.urls(self.link("https://publisher.example/p.pdf", "S"),
                      self.link("https://europepmc.org/a.pdf", "OA")),
            ["https://europepmc.org/a.pdf"])

    def test_free_code_f_counts_as_open(self):
        self.assertEqual(self.urls(self.link("https://publisher.example/p.pdf", "F")),
                         ["https://publisher.example/p.pdf"])

    def test_europepmc_host_is_next_best(self):
        self.assertEqual(
            self.urls(self.link("https://publisher.example/p.pdf"),
                      self.link("https://europepmc.org/a.pdf")),
            ["https://europepmc.org/a.pdf"])

    def test_other_links_are_skipped(self):
        self.assertEqual(self.urls(self.link("https://publisher.example/p.pdf", "S"),
                                   self.link("https://publisher.example/q.pdf")), [])
        self.assertEqual(self.urls(self.link("https://evil.example/europepmc.org/a.pdf")), [])


class TestOpenAlexGetsNoEmail(unittest.TestCase):
    def test_openalex_url_holds_no_email(self):
        urls = []
        with mock.patch.object(fetch_oa_pdf, "get", side_effect=lambda u, *a, **k: urls.append(u) or {}):
            fetch_oa_pdf.via_openalex("10.5555/a", "me@example.org")
        self.assertEqual(len(urls), 1)
        self.assertNotIn("example.org", urls[0])
        self.assertNotIn("mailto", urls[0])


class TestPython39(unittest.TestCase):
    @unittest.skipUnless(os.path.exists("/usr/bin/python3"), "no /usr/bin/python3")
    def test_compiles_and_helps_on_python39(self):
        import subprocess
        from tests import _paths as p
        script = str(p.SCRIPTS / "fetch_oa_pdf.py")
        for cmd in (["-m", "py_compile", script], [script, "--help"]):
            r = subprocess.run(["/usr/bin/python3", *cmd], capture_output=True, text=True)
            self.assertEqual(r.returncode, 0, r.stderr)


class TestTls(unittest.TestCase):
    @unittest.skipUnless(
        ssl.create_default_context().cert_store_stats()["x509_ca"] == 0
        and any(os.path.isfile(p) for p in SYSTEM_BUNDLES),
        "only meaningful where Python has no CA store but the system has a bundle")
    def test_context_falls_back_to_the_system_bundle(self):
        self.assertGreater(fetch_oa_pdf._ssl_context().cert_store_stats()["x509_ca"], 0)


if __name__ == "__main__":
    unittest.main()
