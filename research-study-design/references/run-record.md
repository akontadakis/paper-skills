# The Run Record

**Load when:** the work is running or about to run: setting up the pipeline, recording a run, or tracing a figure or a number back to its code and inputs.

**Contents:** Goal · The Minimum · One Command Per Result · Folder Layout · What a Run Row Records · Recording a Run · Runs That Failed or Were Replaced · Linking Figures to Runs · Before a Result Is Believed · When the Record Is Missing · Before Submission · Checklist

## Goal

Make every number in the paper traceable to the run that produced it: which code, which
inputs, which tool versions, on which date. The record is `.paper/runs.yml`; its fields are in
`study-memory.md`.

Six months after the runs, a reviewer asks for one more case. The record decides whether that
takes a day or a rerun of everything.

## The Minimum

For a study run by one person, three habits are enough. Do these before adding anything else.

1. **A result comes from a script, never from a hand edit.** A number typed or changed by hand
   has no source.
2. **Each run gets a row**, written when the run finishes, by `record_run.py`.
3. **Each figure names its run**, in `figures.yml`.

A workflow manager, a container or a data-version tool can come later. None is needed to meet
this guide.

## One Command Per Result

1. One command produces the data: it reads a configuration file and writes the outputs.
2. One command produces each figure and table from those outputs.
3. Settings live in a configuration file that is an input of the run. A setting changed inside
   the code between runs leaves no trace.
4. Nothing in the chain needs a step by hand. A cell edited in a spreadsheet, or a value copied
   from a screen, breaks it.

## Folder Layout

Keep four things apart. The names are free; the separation is the rule.

```
<project>/
  inputs/      weather files, geometry, measured data. Read-only once the study starts.
  code/        scripts and configuration files. Under version control where possible.
  results/     what the runs write. Never edited by hand.
  figures/     what the plotting scripts write.
  .paper/      the records.
```

Raw measured data is never overwritten. A cleaned version is a new file, made by a script.

## What a Run Row Records

| Field | Records | Why |
|---|---|---|
| `id`, `date`, `kind`, `purpose` | which run this is: `pilot`, `check` or `production` | the design freeze comes on or before the first production run |
| `command` | what started it | so it can be started again |
| `code` | the commit, and whether files had changed since (`dirty: null` when no code path was given: the script did not look); or each code file with its hash | the same script name is not the same script |
| `inputs` | each input file with its hash | a weather file or a configuration that changed is a different study |
| `tools` | each tool with the version string it prints | results can change between versions |
| `seed` | the random seed, where one can be set; one seed per row | to repeat a stochastic run |
| `hardware`, `wall_time` | the machine, and the elapsed time of the run | to cost a rerun, and to answer a reviewer who asks for the run time |
| `outputs` | each output file with its hash | to see later whether a file is still the one the run wrote |
| `status` | `valid`, `superseded`, `failed` or `excluded` | only a valid run supports a figure |

A hash is a short fingerprint of a file's content. If one byte changes, the hash changes.

## Recording a Run

After a run finishes:

```bash
python3 <skill folder>/scripts/record_run.py --paper .paper --id R3 --kind production \
    --purpose "production run, 0.5 m grid" \
    --command "<the command that started the run>" \
    --inputs configs/main_500mm.yml inputs/weather/*.epw \
    --code code/ \
    --outputs results/annual.csv \
    --tool "Radiance=<the version string the tool prints>"
```

1. The script computes the hashes, reads the commit when the project is under version control,
   and appends one row to `.paper/runs.yml`. It runs nothing and changes no other file.
2. Give the tool version as the tool printed it. Run the tool's own version command and copy
   the line. A version from memory is a bracket in the record.
3. An id is used once. Recording a second run under an existing id is refused.
4. Record a run that failed, too, with `--status failed --reason "..."`.
5. `--hardware` and `--wall-time` take the machine and the elapsed time as text. A production
   run recorded with no `--tool` prints a warning. A folder the script cannot read is a
   refusal, not a gap in the record. Record one row per seed.

## Runs That Failed or Were Replaced

1. **Never delete a row.** A run that was replaced becomes `superseded`, with `superseded_by`
   and the reason. Record the replacing run first, then run
   `python3 <skill folder>/scripts/record_run.py --paper .paper --supersede R1 --by R3 --reason "..."`.
   It changes only `status`, `superseded_by` and `reason` of the old row. It refuses when the
   replacing run is not `valid`, and when the old row already has a `reason`.
2. **Never merge** the outputs of a superseded run with those of its replacement. Decide which
   population the paper reports, and say so.
3. **Count the failures.** A run that crashed, or was excluded, stays in the record with its
   reason. The paper reports the count; an unreported failure is unknown, never zero.
4. A run repeated because an input changed is a new row. If a result had already been seen,
   the change that caused it is a `post hoc` amendment in `design.yml`.

## Linking Figures to Runs

`figures.yml`, and the `final` status of a row in it, are defined in the `paper-memory.md`
reference of `research-paper-writing`. Each figure and table row there has a `runs` list beside
its `source`:

```yaml
  - id: "Fig4"
    source: "scripts/plot_depth.py"
    runs: ["R3"]
```

Then check the whole chain:

```bash
python3 <skill folder>/scripts/check_provenance.py .
```

It reports a `final` figure with no run, a figure that rests on a run that is not `valid`, and
any recorded file whose content has changed since the run. For a run a `final` figure rests on,
a recorded file it cannot find or read, and a row with no hash, are findings; a run with no
inputs, or with neither code files nor a commit, is reported as not checked. For any other
run, a file it cannot find or read is reported as not checked. A top-level `release:` block is
ignored. Its rules are in `study-memory.md`, Consistency Rules.

## Before a Result Is Believed

A run that finished is not a result yet. Check it before it is plotted, and before anyone is
told. Check a result that matches the expected answer as hard as one that does not.

1. **Count.** The number of runs, rows and time steps is the number planned. A typical-year file
   has 8,760 hours; a leap-year file has 8,784. A case that is missing was not run, or it failed without saying so.
2. **Limits.** A value outside what is physically possible is a fault in the model or the
   script: a negative illuminance, a daylight factor above 100%, a fraction of hours above 1,
   an energy balance that does not close.
3. **One known case.** Reproduce one number that can be obtained another way: a hand
   calculation for a simple case, the pilot run, or a published benchmark case.
4. **Direction and size.** Compare the result with the expected answer in `question.yml`. A
   surprise is checked before it is believed: first the inputs, then the units, then the
   analysis script.
5. **The raw output before the summary.** Plot one case and one day. A mean can hide a file of
   zeros.
6. **Repeat.** For a stochastic engine or a trained model, the difference of interest is
   larger than the run-to-run spread recorded in `design.yml`.

Write what was checked, and what it showed, in `.paper/reviews/<date>-results-check.md`. A
check that found a fault and led to a rerun is a new row in `runs.yml`; the old run becomes
`superseded`, with `--supersede`.

## When the Record Is Missing

The runs are done and nothing was recorded. Do not rebuild a record from memory.

1. Record only what can be shown: a file that exists is hashed as it is today; a version is
   recorded only if the tool can still print it.
2. Mark the rest as unknown, in the record and in the reply. "The script was probably
   the plotting script" is not provenance.
3. Say what a rerun would cost, and what it would recover. A figure whose inputs were
   overwritten cannot be traced; it can only be regenerated and recorded.
4. If the regenerated figure differs from the old one, find out why before choosing which one
   to publish, and record the reason. Only the regenerated one can be traced.

## Before Submission

1. Regenerate one headline figure from a clean copy of the project, using only the recorded
   command, code and inputs. If it does not come out the same, find out why before submitting.
2. Run `check_provenance.py` and paste its output.
3. Decide what is released: code, configuration, inputs, results. For anything that cannot be
   shared, record what and why, in `withheld`. `research-paper-writing` writes the availability
   statement from the `release:` block.
4. Deposit released code and data where they receive a permanent identifier, and record it in
   the `release:` block of `runs.yml`: `repository`, `identifier`, `licence`, `withheld`. Write
   the block by hand above `runs:`; the scripts keep it as it is.

## Checklist

1. Does every result come from a script, with settings in a configuration file?
2. Are inputs, code, results and figures in separate folders, and is raw data read-only?
3. Does each run have a row, with code version, input hashes, tool versions and status?
4. Are failed and superseded runs still in the record, with reasons?
5. Does each final figure name a valid run?
6. Does `check_provenance.py` pass, with nothing reported as not checked and no rule listed as
   not run?
7. Was one headline figure regenerated from a clean copy?
