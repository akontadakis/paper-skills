import os
import ssl
import unittest
import urllib.error
from pathlib import Path
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


class TestReviewRound2(unittest.TestCase):
    """Findings A-6, A-13 to A-16, A-28, A-29 and the arXiv delay of the second review."""

    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.urls = []

    def tearDown(self):
        self._tmp.cleanup()

    def fake_get(self, url, accept="application/json", raw=False):
        self.urls.append(url)
        if raw:
            return b"@misc{x, title={T}}", url, "text/plain"
        if "openalex" in url:
            return {"best_oa_location": None, "locations": []}
        if "europepmc" in url:
            return {"resultList": {"result": []}}
        return {"is_oa": False}

    def run_main(self, argv, get=None):
        import contextlib
        import io
        err = io.StringIO()
        with mock.patch.object(fetch_oa_pdf, "get", side_effect=get or self.fake_get), \
                mock.patch.object(fetch_oa_pdf.time, "sleep"), \
                mock.patch("sys.argv", ["fetch_oa_pdf.py", *argv]), \
                contextlib.redirect_stderr(err):
            code = fetch_oa_pdf.main()
        return code, err.getvalue()

    def results(self, name="r.json"):
        import json
        return json.loads((self.dir / name).read_text(encoding="utf-8"))

    # A-6
    def test_bibtex_only_on_an_arxiv_id_asks_doi_org_for_the_arxiv_doi(self):
        code, _ = self.run_main(["2301.07041v2", "--bibtex-only", "--out", str(self.dir),
                                 "--json", str(self.dir / "r.json")])
        self.assertTrue(any("doi.org/10.48550/arXiv.2301.07041" in u and "v2" not in u
                            for u in self.urls), self.urls)
        self.assertEqual(self.results()[0]["status"], "metadata only")
        self.assertEqual(code, 0)

    def test_bibtex_only_on_pmc_or_pubmed_is_not_checked(self):
        code, log = self.run_main(["PMC7906746", "12345678", "--bibtex-only", "--out",
                                   str(self.dir), "--json", str(self.dir / "r.json")])
        self.assertEqual([r["status"] for r in self.results()], ["not checked"] * 2)
        self.assertIn("no BibTeX source for this kind of identifier", log)
        self.assertEqual(self.urls, [])
        self.assertEqual(code, 3)

    # A-13
    def test_a_reply_of_the_wrong_shape_is_an_error_not_a_traceback(self):
        for fn, args in ((fetch_oa_pdf.via_unpaywall, ("10.5/a", "x@y.org")),
                         (fetch_oa_pdf.via_openalex, ("10.5/a",)),
                         (fetch_oa_pdf.via_europepmc, ("10.5/a", "doi"))):
            for body in (["a", "list"], {"resultList": None, "is_oa": True,
                                         "best_oa_location": "str",
                                         "locations": [{"is_oa": True, "source": "str",
                                                        "pdf_url": "https://x"}]}):
                with self.subTest(fn=fn.__name__):
                    fetch_oa_pdf.ERRORS.clear()
                    with mock.patch.object(fetch_oa_pdf, "get", return_value=body):
                        self.assertEqual(fn(*args), [])
                    self.assertTrue(fetch_oa_pdf.ERRORS)
        fetch_oa_pdf.ERRORS.clear()

    # A-14
    def test_unusable_out_or_json_exits_2_before_any_request(self):
        a_file = self.dir / "afile"
        a_file.write_text("x", encoding="utf-8")
        for argv in (["10.5555/a", "--out", str(a_file)],
                     ["10.5555/a", "--json", "/nonexistent/folder/r.json"],
                     ["10.5555/a", "--json", str(self.dir)]):
            with self.subTest(argv=argv):
                code, _ = self.run_main(argv)
                self.assertEqual(code, 2)
        self.assertEqual(self.urls, [])

    def test_json_that_is_the_batch_file_is_refused(self):
        batch = self.dir / "b.txt"
        batch.write_text("10.5555/a\n", encoding="utf-8")
        code, _ = self.run_main(["--batch", str(batch), "--json", str(batch)])
        self.assertEqual(code, 2)
        self.assertEqual(batch.read_text(encoding="utf-8"), "10.5555/a\n")

    # A-15
    def test_no_open_access_without_unpaywall_names_the_sources_and_the_gap(self):
        import os
        with mock.patch.dict(os.environ, {}, clear=False):
            os.environ.pop("UNPAYWALL_EMAIL", None)
            code, log = self.run_main(["10.5555/a", "--out", str(self.dir)])
        self.assertIn("Unpaywall was not asked", log)
        self.assertIn("OpenAlex", log)
        self.assertNotIn("NO open-access copy found. The paper may be paywalled", log)
        self.assertEqual(code, 0)

    # A-16
    def test_only_http_and_https_addresses_are_downloaded(self):
        local = self.dir / "local.pdf"
        local.write_bytes(b"%PDF-1.4\n" + b"x" * 20000)
        for url in (local.as_uri(), "ftp://example.org/a.pdf"):
            with self.subTest(url=url):
                ok, msg = fetch_oa_pdf.download(url, self.dir / "out.pdf")
                self.assertFalse(ok)
                self.assertIn("http", msg)
                self.assertFalse((self.dir / "out.pdf").exists())

    # A-28
    def test_batch_file_with_a_bom_and_a_hash_inside_a_doi(self):
        batch = self.dir / "b.txt"
        batch.write_bytes("\ufeff2301.07041  # first\n10.1234/abc#frag\n# note\n"
                          .encode("utf-8"))
        self.run_main(["--batch", str(batch), "--bibtex-only", "--out", str(self.dir),
                       "--json", str(self.dir / "r.json")])
        self.assertEqual([r["input"] for r in self.results()],
                         ["2301.07041", "10.1234/abc#frag"])
        self.assertEqual(self.results()[0]["kind"], "arxiv")

    # A-29
    def test_list_only_writes_no_file(self):
        out = self.dir / "o"
        self.run_main(["10.5555/a", "--list-only", "--out", str(out), "--email", "x@example.org"])
        self.assertFalse(out.exists() and any(out.iterdir()))

    # F-9
    def test_two_arxiv_requests_are_three_seconds_apart(self):
        class Reply:
            headers = {"Content-Type": "application/pdf"}
            def __enter__(self): return self
            def __exit__(self, *a): return False
            def read(self): return b"%PDF"
            def geturl(self): return "https://arxiv.org/pdf/1"
        fetch_oa_pdf._LAST_ARXIV[0] = None
        with mock.patch.object(fetch_oa_pdf, "_open", return_value=Reply()), \
                mock.patch.object(fetch_oa_pdf.time, "sleep") as sleep, \
                mock.patch.object(fetch_oa_pdf.time, "monotonic", return_value=100.0):
            fetch_oa_pdf.get("https://arxiv.org/pdf/1", raw=True)
            sleep.assert_not_called()
            fetch_oa_pdf.get("https://arxiv.org/pdf/2", raw=True)
            sleep.assert_called_once()
            self.assertGreaterEqual(sleep.call_args[0][0], 3.0)
            sleep.reset_mock()
            fetch_oa_pdf.get("https://doi.org/10.1/x", raw=True)
            sleep.assert_not_called()
        fetch_oa_pdf._LAST_ARXIV[0] = None


class TestRound3(unittest.TestCase):
    def setUp(self):
        import tempfile
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        import os
        for p in self.dir.rglob("*"):
            if p.is_dir():
                os.chmod(p, 0o755)
        self._tmp.cleanup()

    def run_main(self, argv, get=None):
        import contextlib
        import io
        err = io.StringIO()
        calls = []

        def fake(url, accept="application/json", raw=False):
            calls.append(url)
            if raw:
                return b"@misc{x, title={T}}", url, "text/plain"
            return {"is_oa": False, "best_oa_location": None, "locations": [],
                    "resultList": {"result": []}}
        with mock.patch.object(fetch_oa_pdf, "get", side_effect=get or fake), \
                mock.patch.object(fetch_oa_pdf.time, "sleep"), \
                mock.patch("sys.argv", ["fetch_oa_pdf.py", *argv]), \
                contextlib.redirect_stderr(err):
            code = fetch_oa_pdf.main()
        return code, err.getvalue(), calls

    # C-2
    def test_a_redirect_to_a_scheme_that_is_not_http_is_refused(self):
        import http.server
        import threading

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(302)
                self.send_header("Location", Path(__file__).resolve().as_uri())
                self.end_headers()

            def log_message(self, *a):
                pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        t = threading.Thread(target=srv.serve_forever, daemon=True)
        t.start()
        try:
            with mock.patch.dict(os.environ, {"NO_PROXY": "127.0.0.1", "no_proxy": "127.0.0.1"}):
                ok, msg = fetch_oa_pdf.download(f"http://127.0.0.1:{srv.server_port}/x",
                                                self.dir / "o.pdf")
        finally:
            srv.shutdown()
        self.assertFalse(ok)
        self.assertIn("not downloaded: redirected to an address that is not http or https", msg)
        self.assertEqual(fetch_oa_pdf.DOWNLOAD_ERRORS, [])
        self.assertFalse((self.dir / "o.pdf").exists())

    # C-4
    def test_an_out_folder_that_cannot_be_used_exits_2_before_any_request(self):
        import os
        ro = self.dir / "ro"
        ro.mkdir()
        os.chmod(ro, 0o555)
        for out in (ro, ro / "sub"):
            with self.subTest(out=str(out)):
                code, log, calls = self.run_main(["10.5555/a", "--out", str(out)])
                self.assertEqual(code, 2)
                self.assertEqual(calls, [])
                self.assertNotIn("Traceback", log)

    def test_a_write_error_is_reported_not_a_traceback(self):
        out = self.dir / "o"
        out.mkdir()
        real = Path.write_text

        def boom(self_, *a, **k):
            if self_.suffix in (".bib", ".json"):
                raise OSError(28, "No space left on device")
            return real(self_, *a, **k)
        with mock.patch.object(Path, "write_text", boom):
            code, log, _ = self.run_main(["10.5555/a", "--email", "x@example.org",
                                          "--out", str(out), "--json", str(self.dir / "r.json")])
        self.assertIn("No space left", log)
        self.assertNotEqual(code, 0)

    # C-6
    def test_old_style_arxiv_id_with_a_v_in_the_archive_name(self):
        c = fetch_oa_pdf.via_arxiv("solv-int/9901001v2")
        self.assertEqual(c[0]["url"], "https://arxiv.org/pdf/solv-int/9901001")
        c = fetch_oa_pdf.via_arxiv("2301.07041v3")
        self.assertEqual(c[0]["url"], "https://arxiv.org/pdf/2301.07041")

    def test_bibtex_only_on_an_old_style_arxiv_id(self):
        code, _, calls = self.run_main(["arXiv:hep-th/9901001v2", "--bibtex-only",
                                        "--out", str(self.dir)])
        self.assertTrue(any("10.48550/arXiv.hep-th/9901001" in u and "v2" not in u
                            for u in calls), calls)
        self.assertEqual(code, 0)

    # test gap
    def test_list_only_with_bibtex_only_writes_no_file_and_no_folder(self):
        out = self.dir / "never"
        code, _, calls = self.run_main(["10.5555/a", "--list-only", "--bibtex-only",
                                        "--out", str(out)])
        self.assertFalse(out.exists())
        self.assertEqual(code, 0)


if __name__ == "__main__":
    unittest.main()
