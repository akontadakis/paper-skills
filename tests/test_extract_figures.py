"""extract_figures.py, on PDFs built here with PyMuPDF. No binary fixtures, no network."""
import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from argparse import Namespace
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

    def test_help_runs_on_python39_or_names_the_missing_dependency(self):
        r = subprocess.run(["/usr/bin/python3", str(SCRIPT), "--help"],
                           capture_output=True, text=True)
        if r.returncode != 0:
            # System Python has no PyMuPDF: the script must say so, not crash.
            self.assertIn("PyMuPDF is required", r.stderr)
        else:
            self.assertIn("extract", r.stdout)


if __name__ == "__main__":
    unittest.main()
