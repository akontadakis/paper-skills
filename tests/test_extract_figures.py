"""extract_figures.py, on PDFs built here with PyMuPDF. No binary fixtures, no network."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from argparse import Namespace
from unittest import mock
from pathlib import Path

from tests import _paths

try:
    import pymupdf as fitz
except ImportError:                                          # pragma: no cover
    try:
        import fitz
    except ImportError:
        fitz = None

SCRIPT = _paths.SCRIPTS / "extract_figures.py"
if fitz is not None:
    import extract_figures


def make_pdf(path, items):
    """items: ("text", y, str) or ("image", y0, y1, size). One A4 page, 72-dpi units."""
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    for n, it in enumerate(items):
        if it[0] == "text":
            page.insert_text((72, it[1]), it[2], fontsize=10)
        else:
            _, y0, y1, size = it
            pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, size, size), False)
            pix.set_rect(pix.irect, (40 * n % 255, 90, 200))
            page.insert_image(fitz.Rect(72, y0, 72 + (y1 - y0), y1), pixmap=pix)
    doc.save(str(path))
    doc.close()


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class TestCaptionPattern(unittest.TestCase):
    def labels(self, text, lead=""):
        with tempfile.TemporaryDirectory() as d:
            pdf = Path(d) / "c.pdf"
            make_pdf(pdf, [("text", 100, lead + text)])
            doc = fitz.open(str(pdf))
            try:
                return [c["label"] for c in extract_figures.find_captions(doc)]
            finally:
                doc.close()

    def test_caption_without_colon_or_full_stop(self):
        self.assertEqual(self.labels("Fig. 2 Mean illuminance by floor"), ["Fig. 2"])

    def test_caption_with_bar(self):
        self.assertEqual(self.labels("Figure 2 | Mean illuminance"), ["Figure 2"])

    def test_upper_case_caption_with_full_stop(self):
        self.assertEqual(self.labels("FIG. 2. Mean illuminance"), ["FIG. 2"])

    def test_caption_with_spaced_hyphen(self):
        self.assertEqual(self.labels("Figure 2 - Mean illuminance"), ["Figure 2"])

    def test_figure_range_is_not_a_caption(self):
        self.assertEqual(self.labels("Fig. 2-3 show the means"), [])

    def test_table_caption_without_punctuation(self):
        self.assertEqual(self.labels("Table 3 Summary of cases"), ["Table 3"])

    def test_in_text_reference_is_not_a_caption(self):
        self.assertEqual(self.labels("Fig. 2, the results show a gain"), [])
        self.assertEqual(self.labels("Figure 2 shows the mean illuminance"), [])
        self.assertEqual(self.labels("Fig. 2 and Fig. 3 give the means"), [])
        self.assertEqual(self.labels("as shown in Fig. 2, the gain is clear"), [])


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class TestNativeAssignment(unittest.TestCase):
    def run_extract(self, items, only=None):
        """(exit code, stdout, stderr, {label: [px]}) of a --native run."""
        with tempfile.TemporaryDirectory() as d:
            pdf = Path(d) / "p.pdf"
            make_pdf(pdf, items)
            args = Namespace(pdf=str(pdf), out=str(Path(d) / "o"), dpi=100, only=only,
                             kind=None, native=True)
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = extract_figures.cmd_extract(args)
            ip = Path(d) / "o" / "figure_index.json"
            got = {}
            if ip.exists():
                got = {r["label"]: [tuple(f["px"]) for f in r["files"]]
                       for r in json.loads(ip.read_text())}
            return code, out.getvalue(), err.getvalue(), got

    def extract(self, items, code=0):
        c, _, _, got = self.run_extract(items)
        self.assertEqual(c, code)
        return got

    def test_captions_below_figures_each_get_only_their_own_image(self):
        got = self.extract([("image", 100, 200, 40), ("text", 215, "Figure 1. First"),
                            ("image", 300, 430, 60), ("text", 445, "Figure 2. Second")])
        self.assertEqual(got, {"Figure 1": [(40, 40)], "Figure 2": [(60, 60)]})

    def test_captions_above_figures_fall_back_to_images_below(self):
        got = self.extract([("text", 100, "Figure 1. First"), ("image", 115, 215, 40),
                            ("text", 300, "Figure 2. Second"), ("image", 315, 445, 60)])
        self.assertEqual(got, {"Figure 1": [(40, 40)], "Figure 2": [(60, 60)]})

    def test_caption_with_no_image_in_its_region_gets_no_file(self):
        got = self.extract([("image", 100, 200, 40), ("text", 215, "Figure 1. First"),
                            ("text", 400, "Figure 2. Vector figure, no raster")], code=3)
        self.assertEqual(got, {"Figure 1": [(40, 40)], "Figure 2": []})

    def test_vector_figure_is_reported_not_checked_and_exits_3(self):
        code, out, _, _ = self.run_extract([("image", 100, 200, 40),
                                            ("text", 215, "Figure 1. First"),
                                            ("text", 400, "Figure 2. Vector figure")])
        self.assertEqual(code, 3)
        self.assertIn("not checked: no embedded raster for Figure 2", out)
        self.assertNotIn("(none)", out)

    def test_only_number_without_a_caption_is_reported_not_checked(self):
        code, out, err, got = self.run_extract([("image", 100, 200, 40),
                                                ("text", 215, "Figure 1. First")], only=[1, 9])
        self.assertEqual(code, 3)
        self.assertIn("not checked: no caption found for figure 9", out + err)
        self.assertEqual(got, {"Figure 1": [(40, 40)]})

    def test_clean_native_run_exits_0(self):
        code, out, _, _ = self.run_extract([("image", 100, 200, 40),
                                            ("text", 215, "Figure 1. First")])
        self.assertEqual(code, 0)
        self.assertNotIn("not checked", out)


def run_cli(*args):
    return subprocess.run([__import__("sys").executable, str(SCRIPT), *args],
                          capture_output=True, text=True)


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class TestStartupFailures(unittest.TestCase):
    """A run that cannot start exits 2 and says why on stderr; a run with no caption exits 3."""

    def test_missing_pdf_exits_2(self):
        for cmd in ("audit", "extract"):
            r = run_cli(cmd, "/nonexistent/none.pdf")
            self.assertEqual(r.returncode, 2, cmd)
            self.assertIn("not found", r.stderr)

    def test_unreadable_pdf_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            bad = Path(d) / "bad.pdf"
            bad.write_text("this is not a pdf", encoding="utf-8")
            r = run_cli("audit", str(bad))
            self.assertEqual(r.returncode, 2)
            self.assertIn("cannot open", r.stderr)
            self.assertNotIn("Traceback", r.stderr)

    def test_encrypted_pdf_exits_2(self):
        with tempfile.TemporaryDirectory() as d:
            plain, locked = Path(d) / "p.pdf", Path(d) / "l.pdf"
            make_pdf(plain, [("text", 100, "Figure 1. First")])
            doc = fitz.open(str(plain))
            doc.save(str(locked), encryption=fitz.PDF_ENCRYPT_AES_256, owner_pw="o", user_pw="u")
            doc.close()
            r = run_cli("extract", str(locked), "--out", str(Path(d) / "o"))
            self.assertEqual(r.returncode, 2)
            self.assertIn("password", r.stderr)

    def test_no_matching_caption_exits_3(self):
        with tempfile.TemporaryDirectory() as d:
            pdf = Path(d) / "n.pdf"
            make_pdf(pdf, [("text", 100, "Just a sentence with no caption.")])
            r = run_cli("extract", str(pdf), "--out", str(Path(d) / "o"))
            self.assertEqual(r.returncode, 3)
            self.assertIn("No captions matched", r.stderr)


class TestPython39(unittest.TestCase):
    @unittest.skipUnless(os.path.exists("/usr/bin/python3"), "no /usr/bin/python3")
    def test_compiles_on_python39(self):
        r = subprocess.run(["/usr/bin/python3", "-m", "py_compile", str(SCRIPT)],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)

    @unittest.skipUnless(os.path.exists("/usr/bin/python3"), "no /usr/bin/python3")
    @unittest.skipIf(fitz is None, "PyMuPDF not installed")
    def test_help_prints_no_library_warning(self):
        """A researcher who asks for help should not be shown a deprecation notice from a
        library the script chose to import by an old name."""
        import subprocess, sys
        result = subprocess.run([sys.executable, str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("Warning", result.stderr)

    @unittest.skipUnless(os.path.exists("/usr/bin/python3"), "no /usr/bin/python3")
    def test_help_runs_on_python39_even_without_pymupdf(self):
        v = subprocess.run(["/usr/bin/python3", "-c", "import sys;print(sys.version_info[:2])"],
                           capture_output=True, text=True).stdout.strip()
        if v != "(3, 9)":
            self.skipTest("system python is not 3.9")
        r = subprocess.run(["/usr/bin/python3", "-B", str(SCRIPT), "--help"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("audit", r.stdout)


def make_raster_pdf(path, placements):
    """One page per placement: (width_pt, height_pt, px_w, px_h, rotate)."""
    doc = fitz.open()
    for w, h, px_w, px_h, rot in placements:
        page = doc.new_page(width=595, height=842)
        pix = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, px_w, px_h), False)
        pix.set_rect(pix.irect, (200, 30, 30))
        page.insert_image(fitz.Rect(72, 100, 72 + w, 100 + h), pixmap=pix, rotate=rot)
        page.insert_text((72, 100 + h + 20), "Figure 1. A raster.", fontsize=10)
    doc.save(str(path))
    doc.close()


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class TestReviewRound2(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def audit_rows(self, placements, *extra):
        pdf = self.dir / "a.pdf"
        make_raster_pdf(pdf, placements)
        js = self.dir / "a.json"
        r = run_cli("audit", str(pdf), "--json", str(js), *extra)
        rows = json.loads(js.read_text(encoding="utf-8")) if js.exists() else None
        return r, rows

    # A-1
    def test_a_file_that_is_not_a_pdf_exits_2(self):
        for name in ("n.txt", "n.md", "n.svg"):
            f = self.dir / name
            f.write_text("Figure 1. A caption in a text file.\n", encoding="utf-8")
            for cmd in ("audit", "extract"):
                with self.subTest(name=name, cmd=cmd):
                    r = run_cli(cmd, str(f), *(["--out", str(self.dir / "o")]
                                               if cmd == "extract" else []))
                    self.assertEqual(r.returncode, 2, r.stdout + r.stderr)
                    self.assertTrue("not a PDF" in r.stderr or "cannot open" in r.stderr)
                    self.assertNotIn("nothing to audit", r.stdout)

    # A-11, A-12
    def test_dpi_verdicts_and_strict_exit(self):
        r, rows = self.audit_rows([(432, 216, 2160, 1080, 0),     # 360 dpi: ok
                                   (432, 216, 1200, 600, 0),      # 200 dpi: LOW
                                   (432, 216, 1600, 800, 0)])     # 267 dpi: LOW
        self.assertEqual(r.returncode, 0)
        self.assertEqual(sorted(x["dpi"] for x in rows), [200, 267, 360])
        verdicts = {x["dpi"]: x["verdict"] for x in rows}
        self.assertEqual(verdicts[360], "ok")
        self.assertTrue(verdicts[200].startswith("LOW"))
        self.assertIn("2 below 300 dpi", r.stdout)
        strict = run_cli("audit", str(self.dir / "a.pdf"), "--strict")
        self.assertEqual(strict.returncode, 1)

    def test_borderline_and_clean_strict(self):
        r, rows = self.audit_rows([(432, 216, 1900, 950, 0), (432, 216, 2700, 1350, 0)],
                                  "--strict")
        self.assertEqual(r.returncode, 0)
        self.assertEqual({x["verdict"] for x in rows}, {"borderline", "ok"})

    def test_a_rotated_image_has_its_true_dpi(self):
        # 1200x600 px shown 6 in x 3 in and turned a quarter: 200 dpi, not 100.
        _, rows = self.audit_rows([(216, 432, 1200, 600, 90)])
        self.assertEqual(rows[0]["dpi"], 200)

    def test_vector_only_says_nothing_to_audit(self):
        pdf = self.dir / "v.pdf"
        make_pdf(pdf, [("text", 100, "Figure 1. Vector.")])
        r = run_cli("audit", str(pdf))
        self.assertEqual(r.returncode, 0)
        self.assertIn("No raster images found", r.stdout)

    # A-27
    def test_small_rasters_are_counted_not_dropped_silently(self):
        r, rows = self.audit_rows([(14, 14, 600, 300, 0), (432, 216, 1800, 900, 0)])
        self.assertEqual(len(rows), 1)
        self.assertIn("1 raster image(s) under 0.3 in were not listed", r.stdout)

    # A-20
    def test_unwritable_json_exits_2_before_the_audit(self):
        pdf = self.dir / "a.pdf"
        make_raster_pdf(pdf, [(432, 216, 1800, 900, 0)])
        for target in ("/nonexistent/x.json", str(pdf), str(self.dir)):
            with self.subTest(target=target):
                before = pdf.read_bytes()
                r = run_cli("audit", str(pdf), "--json", target)
                self.assertEqual(r.returncode, 2)
                self.assertNotIn("Traceback", r.stderr)
                self.assertEqual(pdf.read_bytes(), before)

    # A-21
    def test_bad_dpi_and_out_exit_2_without_a_traceback(self):
        pdf = self.dir / "f.pdf"
        make_pdf(pdf, [("text", 100, "Figure 1. A.")])
        afile = self.dir / "afile"
        afile.write_text("x", encoding="utf-8")
        for args in (["--dpi", "0"], ["--dpi", "-5"], ["--out", str(afile)]):
            with self.subTest(args=args):
                r = run_cli("extract", str(pdf), *args)
                self.assertEqual(r.returncode, 2)
                self.assertNotIn("Traceback", r.stderr)

    def test_one_image_failing_is_not_a_complete_extraction(self):
        pdf = self.dir / "two.pdf"
        make_pdf(pdf, [("image", 100, 150, 40), ("image", 160, 210, 50),
                       ("text", 225, "Figure 1. Both")])
        real, calls = fitz.Pixmap.save, [0]

        def flaky(self_, *a, **k):
            calls[0] += 1
            if calls[0] == 2:
                raise RuntimeError("boom")
            return real(self_, *a, **k)
        args = Namespace(pdf=str(pdf), out=str(self.dir / "o"), dpi=100, only=None,
                         kind=None, native=True)
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(fitz.Pixmap, "save", flaky), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = extract_figures.cmd_extract(args)
        self.assertEqual(code, 3)
        self.assertIn("not checked", out.getvalue() + err.getvalue())

    # A-30
    def test_help_works_without_pymupdf_and_a_command_names_the_missing_library(self):
        hide = ("import sys, runpy; sys.modules['pymupdf'] = None; sys.modules['fitz'] = None; "
                "sys.argv = ['extract_figures.py'] + sys.argv[1:]; "
                "runpy.run_path(%r, run_name='__main__')" % str(SCRIPT))
        r = subprocess.run([__import__("sys").executable, "-c", hide, "--help"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("audit", r.stdout)
        r = subprocess.run([__import__("sys").executable, "-c", hide, "audit", "x.pdf"],
                           capture_output=True, text=True)
        self.assertEqual(r.returncode, 2)
        self.assertIn("PyMuPDF is required", r.stderr)


@unittest.skipIf(fitz is None, "PyMuPDF is not installed")
class TestRound3(unittest.TestCase):
    def test_a_read_only_out_folder_exits_2_without_a_traceback(self):
        with tempfile.TemporaryDirectory() as d:
            pdf = Path(d) / "f.pdf"
            make_pdf(pdf, [("text", 100, "Figure 1. A.")])
            ro = Path(d) / "ro"
            ro.mkdir()
            os.chmod(ro, 0o555)
            try:
                for out in (ro, ro / "sub"):
                    r = run_cli("extract", str(pdf), "--out", str(out))
                    self.assertEqual(r.returncode, 2, r.stderr)
                    self.assertNotIn("Traceback", r.stderr)
            finally:
                os.chmod(ro, 0o755)


if __name__ == "__main__":
    unittest.main()
