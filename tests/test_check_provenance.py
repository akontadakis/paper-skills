import hashlib
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

SCRIPT = _paths.STUDY_SCRIPTS / "check_provenance.py"
SYSTEM_PYTHON = "/usr/bin/python3"
RECORD = _paths.STUDY_SCRIPTS / "record_run.py"


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


FILES = {"configs/main.yml": "grid: 0.5\n", "code/run_all.py": "print('run')\n",
         "results/annual.csv": "x,y\n1,2\n"}


def run_block(rid, status="valid", kind="production", date="2026-08-12", extra="", files=None):
    f = files or FILES
    return f'''  - id: {rid}
    date: "{date}"
    kind: {kind}
    purpose: "p"
    command: "c"
    code:
      commit: null
      dirty: null
      files:
        - path: "code/run_all.py"
          sha256: "{sha(f['code/run_all.py'])}"
    inputs:
      - path: "configs/main.yml"
        sha256: "{sha(f['configs/main.yml'])}"
    tools:
      - name: "Radiance"
        version: "5.4a"
    seed: null
    outputs:
      - path: "results/annual.csv"
        sha256: "{sha(f['results/annual.csv'])}"
    status: {status}
{extra}'''


def figure(fid="Fig4", status="final", runs='["R3"]'):
    r = "" if runs is None else f"    runs: {runs}\n"
    return f'  - id: "{fid}"\n    kind: figure\n    status: {status}\n{r}'


DESIGN = '''version: 1
updated: "2026-08-08"
frozen_on: "2026-03-02"
amendments:
  - id: A1
    date: "2026-08-13"
    what: "x"
    timing: post hoc
'''

SUPERSEDED = '    superseded_by: "R4"\n    reason: "r"\n'


class Proj(unittest.TestCase):
    def setUp(self):
        import check_provenance
        self.mod = check_provenance
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name).resolve() / "proj"
        self.root.mkdir()
        self.paper = self.root / ".paper"
        self.paper.mkdir()
        for rel, text in FILES.items():
            self.put(rel, text)
        self.runs(run_block("R3"))
        self.figs(figure())
        self.put(".paper/design.yml", DESIGN)

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, text):
        p = self.root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding="utf-8")

    def runs(self, *blocks):
        self.put(".paper/runs.yml", 'version: 1\nupdated: "2026-08-12"\nruns:\n' + "".join(blocks))

    def figs(self, *blocks):
        self.put(".paper/figures.yml", "version: 1\nfigures:\n" + "".join(blocks))

    def audit(self):
        return self.mod.audit(self.paper)

    def codes(self):
        return {f["code"] for f in self.audit()["findings"]}

    def cli(self, *args, target=None):
        return subprocess.run([sys.executable, "-B", str(SCRIPT), str(target or self.root), *args],
                              capture_output=True, text=True)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestClean(Proj):
    def test_consistent_project_has_no_findings_and_exit_0(self):
        self.assertEqual(self.audit()["findings"], [])
        r = self.cli()
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("no findings", r.stdout.strip().splitlines()[-1])

    def test_accepts_the_paper_folder_itself(self):
        self.assertEqual(self.cli(target=self.paper).returncode, 0)

    def test_plain_date_values_not_only_quoted_strings(self):
        self.put(".paper/design.yml", DESIGN.replace('"2026-03-02"', "2026-03-02")
                 .replace('"2026-08-13"', "2026-08-13"))
        self.assertEqual(self.audit()["findings"], [])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule1(Proj):
    def test_final_figure_without_runs_is_reported(self):
        self.figs(figure(runs=None))
        self.assertIn("FIGURE_NO_RUN", self.codes())

    def test_final_figure_with_empty_runs_list_is_reported(self):
        self.figs(figure(runs="[]"))
        self.assertIn("FIGURE_NO_RUN", self.codes())

    def test_unknown_run_is_reported(self):
        self.figs(figure(runs='["R3", "R99"]'))
        f = [x for x in self.audit()["findings"] if x["code"] == "FIGURE_RUN_UNKNOWN"]
        self.assertEqual(len(f), 1)
        self.assertIn("R99", f[0]["message"])
        self.assertEqual(f[0]["id"], "Fig4")
        self.assertEqual(f[0]["file"], "figures.yml")

    def test_draft_figure_without_runs_is_not_reported(self):
        self.figs(figure(status="draft", runs=None))
        self.assertEqual(self.audit()["findings"], [])

    def test_runs_as_plain_string_is_field_not_list_and_still_read_as_one_id(self):
        self.figs(figure(runs='"R3"'))
        self.assertEqual(self.codes(), {"FIELD_NOT_LIST"})
        self.figs(figure(runs='"R99"'))
        self.assertEqual(self.codes(), {"FIELD_NOT_LIST", "FIGURE_RUN_UNKNOWN"})


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule2(Proj):
    def test_final_figure_on_superseded_run_names_the_status(self):
        self.runs(run_block("R3", status="superseded", extra=SUPERSEDED), run_block("R4"))
        f = [x for x in self.audit()["findings"] if x["code"] == "FIGURE_RUN_NOT_VALID"]
        self.assertEqual(len(f), 1)
        self.assertIn("superseded", f[0]["message"])

    def test_draft_figure_on_failed_run_is_fine(self):
        self.runs(run_block("R3", status="failed", extra='    reason: "crash"\n'))
        self.figs(figure(status="draft"))
        self.assertEqual(self.audit()["findings"], [])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule3(Proj):
    def test_changed_output_is_file_changed_naming_run_and_path(self):
        self.put("results/annual.csv", "x,y\n9,9\n")
        f = [x for x in self.audit()["findings"] if x["code"] == "FILE_CHANGED"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["id"], "R3")
        self.assertIn("results/annual.csv", f[0]["message"])
        r = self.cli()
        self.assertEqual(r.returncode, 1)
        self.assertIn("FILE_CHANGED", r.stdout)

    def test_changed_input_and_code_are_both_found(self):
        self.put("configs/main.yml", "grid: 1\n")
        self.put("code/run_all.py", "print('x')\n")
        n = [x for x in self.audit()["findings"] if x["code"] == "FILE_CHANGED"]
        self.assertEqual(len(n), 2)

    def test_missing_file_behind_a_final_figure_is_a_finding(self):
        (self.root / "results" / "annual.csv").unlink()
        res = self.audit()
        f = [x for x in res["findings"] if x["code"] == "FILE_NOT_FOUND"]
        self.assertEqual(len(f), 1)
        self.assertEqual(f[0]["id"], "R3")
        self.assertIn("results/annual.csv", f[0]["message"])
        r = self.cli()
        self.assertEqual(r.returncode, 1)
        self.assertIn("FILE_NOT_FOUND", r.stdout)

    def test_missing_file_of_a_run_no_final_figure_rests_on_is_not_checked(self):
        (self.root / "results" / "annual.csv").unlink()
        self.figs(figure(status="draft"))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertTrue(any("file not found" in n and "results/annual.csv" in n
                            for n in res["not_checked"]))
        r = self.cli()
        self.assertEqual(r.returncode, 3)
        self.assertIn("not checked: file not found", r.stdout)
        self.assertIn("not a clean result", r.stdout.strip().splitlines()[-1])

    def test_placeholder_hash_behind_a_final_figure_is_a_finding(self):
        text = (self.paper / "runs.yml").read_text(encoding="utf-8")
        self.put(".paper/runs.yml", text.replace(sha(FILES["results/annual.csv"]), "<hash>"))
        f = [x for x in self.audit()["findings"] if x["code"] == "HASH_MISSING"]
        self.assertEqual(len(f), 1)
        self.assertIn("no hash recorded", f[0]["message"])
        self.assertEqual(self.cli().returncode, 1)

    def test_placeholder_hash_of_a_run_no_final_figure_rests_on_is_not_checked(self):
        text = (self.paper / "runs.yml").read_text(encoding="utf-8")
        self.put(".paper/runs.yml", text.replace(sha(FILES["results/annual.csv"]), "<hash>"))
        self.figs(figure(status="draft"))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertTrue(any("no hash recorded" in n for n in res["not_checked"]))
        self.assertEqual(self.cli().returncode, 3)

    def test_uppercase_hex_hash_is_accepted(self):
        text = (self.paper / "runs.yml").read_text(encoding="utf-8")
        h = sha(FILES["results/annual.csv"])
        self.put(".paper/runs.yml", text.replace(h, h.upper()))
        self.assertEqual(self.audit()["not_checked"], [])
        self.assertEqual(self.audit()["findings"], [])

    def test_superseded_failed_excluded_runs_are_not_rehashed(self):
        changed = dict(FILES, **{"results/annual.csv": "changed\n"})
        self.put("results/annual.csv", "changed\n")
        self.runs(run_block("R3", status="superseded", extra=SUPERSEDED),
                  run_block("R5", status="failed", extra='    reason: "r"\n'),
                  run_block("R6", status="excluded", extra='    reason: "r"\n'),
                  run_block("R4", files=changed))
        self.figs(figure(runs='["R4"]'))
        self.assertEqual(self.audit()["findings"], [])
        self.assertEqual(self.audit()["not_checked"], [])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule4(Proj):
    def test_failed_without_reason(self):
        self.runs(run_block("R3", status="failed"))
        self.figs(figure(status="draft"))
        self.assertEqual(self.codes(), {"RUN_NO_REASON"})

    def test_blank_reason_counts_as_missing(self):
        self.runs(run_block("R3", status="excluded", extra='    reason: "  "\n'))
        self.figs(figure(status="draft"))
        self.assertIn("RUN_NO_REASON", self.codes())

    def test_superseded_without_superseded_by_or_with_unknown_run(self):
        self.figs(figure(status="draft"))
        self.runs(run_block("R3", status="superseded", extra='    reason: "r"\n'))
        self.assertIn("RUN_SUPERSEDED_BY_UNKNOWN", self.codes())
        self.runs(run_block("R3", status="superseded", extra='    reason: "r"\n    superseded_by: "R77"\n'))
        self.assertIn("RUN_SUPERSEDED_BY_UNKNOWN", self.codes())

    def test_status_outside_the_four_values(self):
        self.runs(run_block("R3", status="done"))
        self.figs(figure(status="draft"))
        self.assertIn("RUN_STATUS_INVALID", self.codes())

    def test_kind_outside_the_three_values(self):
        self.runs(run_block("R3", kind="final"))
        self.assertIn("RUN_KIND_INVALID", self.codes())

    def test_duplicate_run_id(self):
        self.runs(run_block("R3"), run_block("R3"))
        self.assertIn("RUN_DUPLICATE_ID", self.codes())


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestRule5And6(Proj):
    def test_frozen_after_first_production_run(self):
        self.put(".paper/design.yml", DESIGN.replace("2026-03-02", "2026-09-01"))
        self.assertIn("FREEZE_AFTER_FIRST_RUN", self.codes())

    def test_frozen_on_the_day_of_the_first_run_is_allowed(self):
        self.put(".paper/design.yml", DESIGN.replace("2026-03-02", "2026-08-12"))
        self.assertEqual(self.audit()["findings"], [])

    def test_earliest_production_run_decides_and_pilots_do_not_count(self):
        self.runs(run_block("R1", kind="pilot", date="2026-01-01"), run_block("R3"))
        self.assertEqual(self.audit()["findings"], [])
        self.runs(run_block("R1", kind="pilot", date="2026-01-01"),
                  run_block("R2", kind="production", date="2026-02-01"), run_block("R3"))
        self.assertIn("FREEZE_AFTER_FIRST_RUN", self.codes())

    def test_no_frozen_on_with_a_production_run(self):
        self.put(".paper/design.yml", DESIGN.replace('frozen_on: "2026-03-02"\n', ""))
        self.assertEqual(self.codes(), {"DESIGN_NOT_FROZEN"})

    def test_no_frozen_on_and_no_production_run_is_fine(self):
        self.put(".paper/design.yml", DESIGN.replace('frozen_on: "2026-03-02"\n', ""))
        self.runs(run_block("R3", kind="pilot"))
        self.assertEqual(self.audit()["findings"], [])

    def test_amendment_after_first_production_run_must_be_post_hoc(self):
        self.put(".paper/design.yml", DESIGN.replace("post hoc", "changed before analysis"))
        self.assertIn("AMENDMENT_NOT_POST_HOC", self.codes())

    def test_amendment_after_the_first_run_may_record_that_no_result_was_seen(self):
        """Data can be collected and not yet opened. The amendment then says so, in a field,
        and may keep `changed before analysis`."""
        changed = DESIGN.replace("timing: post hoc", "timing: changed before analysis\n    results_seen: false")
        self.assertNotEqual(changed, DESIGN)
        self.put(".paper/design.yml", changed)
        self.assertNotIn("AMENDMENT_NOT_POST_HOC", self.codes())

    def test_amendment_kind_outside_the_two_values_is_reported(self):
        self.put(".paper/design.yml", DESIGN.replace("timing: post hoc", "timing: post hoc\n    kind: tidy-up"))
        self.assertIn("AMENDMENT_KIND_INVALID", self.codes())

    def test_correction_must_name_the_check_that_forced_it(self):
        self.put(".paper/design.yml", DESIGN.replace("timing: post hoc", "timing: post hoc\n    kind: correction"))
        self.assertIn("AMENDMENT_CORRECTION_NO_CHECK", self.codes())

    def test_correction_with_its_check_and_a_choice_are_both_accepted(self):
        for extra in ('kind: correction\n    forced_by: "grid-convergence test, 6.9% change"', "kind: choice"):
            with self.subTest(extra=extra):
                self.put(".paper/design.yml", DESIGN.replace("timing: post hoc", "timing: post hoc\n    " + extra))
                self.assertFalse(self.codes() & {"AMENDMENT_KIND_INVALID", "AMENDMENT_CORRECTION_NO_CHECK"})

    def test_results_seen_true_does_not_excuse_the_timing(self):
        changed = DESIGN.replace("timing: post hoc", "timing: changed before analysis\n    results_seen: true")
        self.put(".paper/design.yml", changed)
        self.assertIn("AMENDMENT_NOT_POST_HOC", self.codes())

    def test_amendment_before_first_production_run_may_be_either(self):
        self.put(".paper/design.yml", DESIGN.replace("2026-08-13", "2026-04-01")
                 .replace("post hoc", "changed before analysis"))
        self.assertEqual(self.audit()["findings"], [])

    def test_amendment_timing_outside_the_two_values(self):
        self.put(".paper/design.yml", DESIGN.replace("post hoc", "later"))
        self.assertIn("AMENDMENT_TIMING_INVALID", self.codes())

    def test_amendment_with_no_date(self):
        self.put(".paper/design.yml", DESIGN.replace('    date: "2026-08-13"\n', ""))
        self.assertIn("AMENDMENT_NO_DATE", self.codes())


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestAbsentAndBroken(Proj):
    def test_no_runs_yml_is_not_checked_exit_3(self):
        (self.paper / "runs.yml").unlink()
        r = self.cli()
        self.assertEqual(r.returncode, 3)
        self.assertIn("not checked: no runs.yml", r.stdout)

    def test_absent_design_lists_rules_5_and_6_and_keeps_exit_0(self):
        (self.paper / "design.yml").unlink()
        out = Path(self.tmp.name) / "f.json"
        r = self.cli("--json", str(out))
        self.assertEqual(r.returncode, 0, r.stdout)
        self.assertIn("rules 5, 6", r.stdout)
        data = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(data["rules_not_run"], {"design.yml": [5, 6]})
        self.assertEqual(data["findings"], [])

    def test_absent_figures_lists_rules_1_and_2(self):
        (self.paper / "figures.yml").unlink()
        r = self.cli()
        self.assertIn("rules 1, 2", r.stdout)
        self.assertEqual(self.audit()["rules_not_run"], {"figures.yml": [1, 2]})

    def test_json_has_findings_with_code_file_id_message(self):
        self.put("results/annual.csv", "changed")
        out = Path(self.tmp.name) / "f.json"
        self.cli("--json", str(out))
        f = json.loads(out.read_text(encoding="utf-8"))["findings"][0]
        self.assertEqual(set(f), {"code", "file", "id", "message"})

    def test_unparseable_runs_yml_is_not_checked_not_a_crash(self):
        self.put(".paper/runs.yml", "runs: [unclosed\n  - : :\n")
        r = self.cli()
        self.assertEqual(r.returncode, 3)
        self.assertIn("not checked", r.stdout)
        self.assertNotIn("Traceback", r.stderr)

    def test_empty_runs_yml_and_missing_runs_key_are_not_checked(self):
        for text in ("", "version: 1\n", "- a\n- b\n", "just a string\n"):
            self.put(".paper/runs.yml", text)
            r = self.cli()
            self.assertEqual(r.returncode, 3, text)
            self.assertNotIn("Traceback", r.stderr)

    def test_unparseable_figures_yml_counts_nothing_as_checked(self):
        self.put(".paper/figures.yml", "figures: [oops\n")
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertIn("figures.yml", res["rules_not_run"])
        self.assertEqual(self.cli().returncode, 3)

    def test_figures_without_figures_key_or_design_as_a_list(self):
        self.put(".paper/figures.yml", "version: 1\n")
        self.put(".paper/design.yml", "- a\n")
        res = self.audit()
        self.assertEqual(set(res["rules_not_run"]), {"figures.yml", "design.yml"})
        self.assertEqual(self.cli().returncode, 3)

    def test_rows_that_are_not_mappings_never_crash(self):
        self.put(".paper/runs.yml", "version: 1\nruns:\n  - just text\n  - 5\n  -\n"
                 "  - id: R3\n    code: \"scalar\"\n    inputs: oops\n    outputs:\n      - nope\n"
                 "    status: valid\n    kind: production\n    date: \"2026-08-12\"\n")
        self.put(".paper/figures.yml", "version: 1\nfigures:\n  - text\n  - id: F\n    status: final\n"
                 "    runs: [R3, {a: 1}, 4]\n")
        self.put(".paper/design.yml",
                 "frozen_on: [1]\namendments:\n  - x\n  - {id: A, date: [1], timing: 3}\n")
        r = self.cli()
        self.assertIn(r.returncode, (1, 3))
        self.assertNotIn("Traceback", r.stderr)

    def test_scalar_top_level_in_design_never_crashes(self):
        self.put(".paper/design.yml", "just a string\n")
        r = self.cli()
        self.assertEqual(r.returncode, 3)
        self.assertNotIn("Traceback", r.stderr)

    def test_unreadable_date_on_a_production_run_is_not_checked(self):
        self.runs(run_block("R3", date="soon"))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertTrue(res["not_checked"])


class TestNoYaml(unittest.TestCase):
    def test_without_pyyaml_prints_install_message_and_exits_3(self):
        d = tempfile.TemporaryDirectory()
        self.addCleanup(d.cleanup)
        Path(d.name, "yaml.py").write_text("raise ImportError('blocked')\n")
        env = dict(os.environ, PYTHONPATH=d.name)
        r = subprocess.run([sys.executable, "-B", str(SCRIPT), d.name], capture_output=True,
                           text=True, env=env)
        self.assertEqual(r.returncode, 3)
        self.assertIn("not checked: install pyyaml", r.stdout)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestEndToEnd(Proj):
    def test_record_a_run_then_check_it_is_clean(self):
        shutil.rmtree(self.paper)
        r = subprocess.run([sys.executable, "-B", str(RECORD), "--paper", ".paper", "--id", "R3",
                            "--kind", "production", "--purpose", "p", "--command", "c",
                            "--inputs", "configs/main.yml", "--code", "code",
                            "--outputs", "results/annual.csv", "--tool", "Radiance=5.4a",
                            "--date", "2026-08-12"],
                           cwd=str(self.root), capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.figs(figure())
        self.put(".paper/design.yml", DESIGN)
        c = self.cli()
        self.assertEqual(c.returncode, 0, c.stdout)
        self.put("results/annual.csv", "tampered\n")
        self.assertEqual(self.cli().returncode, 1)


@unittest.skipUnless(os.path.exists(SYSTEM_PYTHON), "no /usr/bin/python3")
class TestSystemPython(unittest.TestCase):
    def test_compiles_and_shows_help_on_system_python(self):
        r = subprocess.run([SYSTEM_PYTHON, "-B", "-c",
                            "import sys; compile(open(sys.argv[1]).read(), sys.argv[1], 'exec')",
                            str(SCRIPT)], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        r = subprocess.run([SYSTEM_PYTHON, "-B", str(SCRIPT), "--help"], capture_output=True, text=True)
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn("--json", r.stdout)


class TestScriptFile(unittest.TestCase):
    def test_is_executable_with_env_shebang_and_docstring(self):
        self.assertTrue(os.access(SCRIPT, os.X_OK))
        text = SCRIPT.read_text(encoding="utf-8")
        self.assertTrue(text.startswith("#!/usr/bin/env python3\n"))
        doc = text.split('"""')[1]
        self.assertIn("manuscript", doc)
        self.assertIn("Exit code", doc)


# ---- review findings P1 to P6 and regression cases -------------------------------------------

import contextlib  # noqa: E402
import io  # noqa: E402


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP1Normalisation(Proj):
    def test_figure_status_in_other_case_or_with_spaces_is_still_checked(self):
        for written in ("Final", '"final "', '" FINAL"'):
            with self.subTest(status=written):
                self.figs(figure(status=written, runs=None))
                self.assertIn("FIGURE_NO_RUN", self.codes())

    def test_figure_with_missing_status_is_invalid(self):
        self.figs('  - id: "Fig4"\n    kind: figure\n    runs: ["R3"]\n')
        self.assertIn("FIGURE_STATUS_INVALID", self.codes())

    def test_figure_status_outside_draft_final_regenerate_is_invalid(self):
        self.figs(figure(status="done"))
        self.assertIn("FIGURE_STATUS_INVALID", self.codes())

    def test_draft_and_regenerate_are_valid_statuses(self):
        self.figs(figure("A", status="draft", runs=None), figure("B", status="Regenerate", runs=None))
        self.assertEqual(self.audit()["findings"], [])

    def test_run_status_and_kind_are_normalised_before_validation(self):
        self.runs(run_block("R3", status='"Valid "', kind='"Production"'))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertEqual(res["not_checked"], [])
        self.put("results/annual.csv", "changed\n")
        self.assertIn("FILE_CHANGED", self.codes())

    def test_invalid_run_status_is_reported_as_written(self):
        self.runs(run_block("R3", status='"Bogus"'))
        msgs = [f["message"] for f in self.audit()["findings"] if f["code"] == "RUN_STATUS_INVALID"]
        self.assertTrue(msgs and "Bogus" in msgs[0])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP2NoFiles(Proj):
    def test_valid_run_with_no_files_is_not_checked_and_exits_3(self):
        bare = ('  - id: R3\n    date: "2026-08-12"\n    kind: production\n    purpose: "p"\n'
                '    command: "c"\n    status: valid\n')
        self.runs(bare)
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertIn("RUN_NO_FILES", [n["code"] for n in res["not_checked_items"]])
        self.assertIn("run R3 records no files, so nothing about it could be verified", res["not_checked"][0])
        self.assertEqual(self.cli().returncode, 3)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP3Crashes(Proj):
    def test_impossible_unquoted_date_is_unparseable_not_a_traceback(self):
        self.put(".paper/runs.yml", 'version: 1\nruns:\n  - id: R3\n    date: 2026-02-30\n')
        r = self.cli()
        self.assertEqual(r.returncode, 3)
        self.assertNotIn("Traceback", r.stderr)
        self.assertIn("FILE_UNPARSEABLE", [n["code"] for n in self.audit()["not_checked_items"]])

    def test_impossible_date_in_design_yml_is_unparseable(self):
        self.put(".paper/design.yml", DESIGN.replace('"2026-03-02"', "2026-02-30"))
        res = self.audit()
        self.assertIn("FILE_UNPARSEABLE", [n["code"] for n in res["not_checked_items"]])
        self.assertEqual(res["rules_not_run"], {"design.yml": [5, 6]})

    def test_unexpected_error_prints_one_line_and_exits_3(self):
        saved = self.mod.audit
        def boom(paper):
            raise RuntimeError("boom")
        self.mod.audit = boom
        out = io.StringIO()
        try:
            with contextlib.redirect_stdout(out):
                rc = self.mod.main([str(self.root)])
        finally:
            self.mod.audit = saved
        self.assertEqual(rc, 3)
        self.assertEqual(out.getvalue().strip(), "not checked: internal error: RuntimeError: boom")


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP4JsonTarget(Proj):
    def test_json_inside_a_paper_folder_is_refused_and_nothing_is_written(self):
        before = (self.paper / "runs.yml").read_bytes()
        r = self.cli("--json", str(self.paper / "runs.yml"))
        self.assertEqual(r.returncode, 2)
        self.assertEqual((self.paper / "runs.yml").read_bytes(), before)
        r = self.cli("--json", str(self.paper / "sub" / "out.json"))
        self.assertEqual(r.returncode, 2)
        self.assertFalse((self.paper / "sub").exists())

    def test_json_to_an_existing_path_is_refused_and_unchanged(self):
        out = self.root / "findings.json"
        out.write_text("keep")
        self.assertEqual(self.cli("--json", str(out)).returncode, 2)
        self.assertEqual(out.read_text(), "keep")

    def test_json_to_a_new_path_still_works_and_help_says_what_is_refused(self):
        out = self.root / "new.json"
        self.assertEqual(self.cli("--json", str(out)).returncode, 0)
        self.assertTrue(out.exists())
        helptext = subprocess.run([sys.executable, "-B", str(SCRIPT), "--help"], capture_output=True,
                                  text=True).stdout
        self.assertIn(".paper", helptext)
        self.assertIn("only file", helptext)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP5PathsOutsideProject(Proj):
    def test_absolute_and_parent_paths_are_not_read(self):
        outside = Path(self.tmp.name) / "outside.csv"
        outside.write_text("x,y\n1,2\n")
        wrong = "0" * 64
        text = (self.paper / "runs.yml").read_text(encoding="utf-8")
        for bad in (str(outside), "../outside.csv", "results/../../outside.csv"):
            with self.subTest(path=bad):
                self.runs(text.split("runs:\n")[1].replace("results/annual.csv", bad)
                          .replace(sha(FILES["results/annual.csv"]), wrong))
                res = self.audit()
                self.assertEqual(res["findings"], [])
                self.assertIn("PATH_OUTSIDE_PROJECT", [n["code"] for n in res["not_checked_items"]])


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestP6AmendmentReason(Proj):
    NO_SEEN = DESIGN.replace("timing: post hoc", "timing: changed before analysis\n    results_seen: false")

    def test_results_seen_false_without_a_reason_is_reported(self):
        self.put(".paper/design.yml", self.NO_SEEN)
        self.assertIn("AMENDMENT_NO_REASON", self.codes())
        self.put(".paper/design.yml", self.NO_SEEN.replace("results_seen: false",
                                                           'results_seen: false\n    reason: "  "'))
        self.assertIn("AMENDMENT_NO_REASON", self.codes())

    def test_a_reason_field_satisfies_it(self):
        self.put(".paper/design.yml", self.NO_SEEN.replace(
            "results_seen: false", 'results_seen: false\n    reason: "data collected, not opened"'))
        self.assertEqual(self.audit()["findings"], [])

    def test_the_ordinary_why_field_does_not_satisfy_it(self):
        self.put(".paper/design.yml", self.NO_SEEN.replace(
            "results_seen: false", 'results_seen: false\n    why: "data collected, not opened"'))
        self.assertIn("AMENDMENT_NO_REASON", self.codes())


def bare_block(rid, inputs=True, code=True, commit="null"):
    lines = [f'  - id: {rid}', '    date: "2026-08-12"', '    kind: production', '    purpose: "p"',
             '    command: "c"', '    code:', f'      commit: {commit}', '      dirty: null']
    if code:
        lines += ['      files:', '        - path: "code/run_all.py"',
                  f'          sha256: "{sha(FILES["code/run_all.py"])}"']
    if inputs:
        lines += ['    inputs:', '      - path: "configs/main.yml"',
                  f'        sha256: "{sha(FILES["configs/main.yml"])}"']
    lines += ['    outputs:', '      - path: "results/annual.csv"',
              f'        sha256: "{sha(FILES["results/annual.csv"])}"', '    status: valid']
    return "\n".join(lines) + "\n"


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestChainIsComplete(Proj):
    def codes_not_checked(self):
        return [n["code"] for n in self.audit()["not_checked_items"]]

    def test_final_figure_on_a_run_with_no_inputs_is_not_checked_and_exits_3(self):
        self.runs(bare_block("R3", inputs=False))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertIn("RUN_NO_INPUTS", self.codes_not_checked())
        self.assertEqual(self.cli().returncode, 3)

    def test_final_figure_on_a_run_with_neither_code_files_nor_a_commit_is_not_checked(self):
        self.runs(bare_block("R3", code=False))
        self.assertEqual(self.audit()["findings"], [])
        self.assertIn("RUN_NO_CODE", self.codes_not_checked())
        self.assertEqual(self.cli().returncode, 3)

    def test_a_commit_alone_identifies_the_code(self):
        self.runs(bare_block("R3", code=False, commit='"abc1234"'))
        self.assertNotIn("RUN_NO_CODE", self.codes_not_checked())
        self.assertEqual(self.cli().returncode, 0)

    def test_the_same_runs_behind_a_draft_figure_raise_nothing(self):
        self.runs(bare_block("R3", inputs=False, code=False))
        self.figs(figure(status="draft"))
        self.assertEqual(self.codes_not_checked(), [])
        self.assertEqual(self.cli().returncode, 0)


@unittest.skipUnless(HAVE_YAML, "PyYAML not installed")
class TestReleaseBlockTolerated(Proj):
    def test_a_top_level_release_block_changes_nothing(self):
        self.put(".paper/runs.yml", 'version: 1\nupdated: "2026-08-12"\nrelease:\n'
                 '  repository: "[insert the repository]"\n  identifier: "[insert the DOI]"\n\n'
                 'runs:\n' + run_block("R3"))
        res = self.audit()
        self.assertEqual(res["findings"], [])
        self.assertEqual(res["not_checked"], [])
        self.assertEqual(self.cli().returncode, 0)
