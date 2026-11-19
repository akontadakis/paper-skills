# Simulation Reporting Guide

**Load when:** results come from a physics or simulation engine: while drafting Methods, and as a gate before submission.

**Contents:** Goal · The Two Failure Modes · Hard Rules · Reporting Block · Provenance Language · When This Gate Applies · Pre-Submission Gate

## Goal

Report a simulation study so a stranger can rebuild the number, and so no reader mistakes a
default for a measurement.

This is the simulation analogue of CONSORT/STROBE. Use it while drafting Methods, and again as a
gate before submission. It applies to daylight, radiative-transfer, spectral, energy, and
lighting-control studies.

## The Two Failure Modes

1. **Under-reporting** — the number cannot be reproduced because a setting was never stated. The reader cannot tell whether a discrepancy is physics or configuration.
2. **Provenance laundering** — a substituted default, an inferred value, or a model output is reported in language that implies it was measured. This is the more serious of the two.

## Hard Rules

1. Every reported quantity is named exactly. Not a family name, the quantity.
2. Every input value carries its provenance rank: **override > measured/file > documented default**.
3. A default that was silently substituted is disclosed as substituted, with its value.
4. Any convention with more than one accepted form is declared explicitly, with the form used.
5. A convergence-sensitive parameter is reported with the evidence that it converged.
6. If a run failed or was excluded, say so and say why.

## Reporting Block

Include this in Methods, as prose or a table. Every line is required or explicitly marked N/A.

### 1. Engine and version

1. Engine name and exact version (`rtrace` / Radiance 6.x, EnergyPlus x.y, SMARTS, SPECTRL2).
2. Build source if not the standard distribution, and any local patch applied.
3. Any wrapper, toolkit, or script layer, with version or commit.
4. Platform, if the engine is known to differ across them.

> A patched or non-standard build changes results. State it. A build that silently drops a
> multiplier will produce numbers no one can reproduce and no one can explain.

### 2. Simulation parameters

1. Rendering parameters in full: ambient (`-ab -ad -as -ar -aa -av -aw`), direct (`-dj -dt -dc -ds`) and limit (`-lr -lw`).
2. Justify the ambient bounce count with evidence, not habit. State the convergence test: what changed, by how much, when the parameter was raised.
3. Sampling counts and any stochastic seed.
4. Matrix method if used (two-, three-, five-phase), with basis (Klems, tensor tree) and resolution.
5. Any parameter that was swept: the range, the step, and the value used for headline results.
6. For a sweep that samples the parameter space rather than covering it: the sampling design by name (full factorial, Latin hypercube, Sobol sequence, random), the number of samples, the seed, and the software and version that generated it. If sensitivity indices are reported, say which design they were computed from. A reader cannot judge coverage, or regenerate the cases, without these four.

> Under-resolved ambient settings bias deep-plan and low-daylight cases hardest, and the bias has a
> direction. With the default ambient value (`-av 0 0 0`), too few ambient bounces make the result too dark; a non-zero `-av` can make it too bright. Under-sampling adds noise, not a bias in one direction. Report the convergence check or the reviewer is right to distrust the number.

### 3. Climate and sky

1. Weather file: name, station, WMO or site ID, coordinates, elevation.
2. Type and year: TMY, TMYx, AMY with the specific year, or measured campaign with dates.
3. Source and version of the dataset, and licence if it restricts redistribution.
4. Sky model (Perez all-weather, CIE clear/overcast, spectral; name the tool that generated it, for example `gendaymtx`) and its version.
5. Timestep and how sub-hourly values were derived, if they were.
6. Analysis period and occupied-hours definition, with the calendar and any holiday handling.
7. Direct/diffuse split: measured, or decomposed with a named model.

### 4. Ground and surroundings

1. **Ground albedo, explicitly, with its provenance.** State the value used.
2. If the weather file reported `0.000`, say whether that was treated as a real value or overridden, and to what. A zero albedo is physically implausible, so check it. In the EPW format the missing-value code for albedo is 999, and some engines, EnergyPlus among them, do not read the albedo field of the weather file at all.
3. Both sites in a comparison must use the same albedo unless the difference is the subject of study — and if they differ, say so.
4. Obstructions, context geometry, and their reflectances, or a statement that none were modelled.

### 5. Geometry and materials

1. Room or model dimensions, orientation, and how orientation is measured (azimuth convention, and what 0° means).
2. Every surface's reflectance or transmittance, and whether specular, diffuse, or measured BSDF.
3. Glazing: visible transmittance, spectral data source, number of panes, coatings, frame factor.
4. Source of material values: measured, manufacturer datasheet, standard table, or assumed.
5. Any simplification made to the geometry, and its expected effect.

### 6. Sensors and grid

1. Grid spacing and extent, and the offset from walls.
2. Reference plane: height above floor, and whether the workplane is horizontal, vertical, or view-directed.
3. For view-directed or gaze-based metrics: the view direction convention, field of view, and how the direction was chosen. A vertical plane at eye height is not the same measurement as a cone-weighted field of view — do not conflate them.
4. Number of sensor points, and how many were excluded and why.
5. **Whether the grid can resolve the answer.** A grid coarser than the effect being measured cannot resolve it. State the direction and the size of the resolution error for the statistic you report. A boundary read at the last passing grid point can fall short of the true boundary by up to one grid spacing, so it is a lower bound. Where the grid ends before the criterion fails, the depth is right-censored: the true depth is at least the reported one.

### 7. Reported quantity

1. Name the exact quantity, not the family. Melanopic EDI (CIE S 026, referenced to D65) is not equivalent melanopic lux (EML, referenced to illuminant E). They differ by a constant factor for every spectrum (EML ≈ 1.10 × melanopic EDI), so a threshold written in one and evaluated in the other shifts by about 10%.
2. State the action spectrum, standard, and version (e.g. CIE S 026).
3. For ratios such as mel-DER: state **where** it was evaluated. A luminaire datasheet quotes the value at the source; the ratio at the point differs where the spectrum changes on the way: by reflection from coloured surfaces, by transmission through glazing, or by mixing daylight with electric light. The point value is the one that governs compliance.
4. State how spectral information was carried: full SPD transported, or inferred from binned channels. Say which, because the second can be biased, in a direction that depends on the source spectrum and the channel boundaries.
5. Summary statistic: spatial mean, median, percentile, or point value, and over which points and which hours.

### 8. Conventions

Where more than one accepted convention exists, name the one used and cite it.

1. Weighting schemes, and their normalisation. State the sum of weights. Two common daylight-zone conventions differ by normalisation and can move a headline savings figure; a reader cannot tell which you used unless you say.
2. Compliance thresholds and the standard they come from, with edition and year.
3. Time-basis for annual metrics: all hours, daylit hours, or occupied hours.
4. Rounding and precision policy.
5. Any coordinate, azimuth, or sign convention that is not universal.

### 9. Validation

1. What the model was checked against: measurement, another engine, an analytical case, or a published benchmark.
2. The agreement achieved, with the error metrics named and their denominator: one metric for bias (MBE) and one for scatter (rRMSE). R² is not evidence of agreement; see `statistics-reporting.md`, Model Agreement and Calibration.
3. The domain over which validation holds, and where it was not tested.
4. If validation covers only part of the model (daylight but not electric, illuminance but not spectrum), say which part. An honest partial validation floor is worth more than an implied full one.
5. The acceptance margin, stated before the comparison, and its source. For a comparison of two methods, the mean difference and the limits of agreement. `statistics-reporting.md`, Model Agreement and Calibration, rules 8 and 9, has the detail.

### 10. Known bias and disclosure

1. Any bias found and not removed: its magnitude, its sign, and which results it touches.
2. Any known engine or toolchain defect that affects the results.
3. Any result that was superseded by a rerun, and which population the reported numbers belong to. Never merge a superseded run with its replacement.
4. An unreported runtime, failure count, or excluded run stays **unknown**. It never becomes zero, and it never becomes a blank cell the reader will read as zero. If runs failed or were excluded, give the count and the reason.

### 11. Availability

1. Model files, scripts, and analysis code: where, and under what licence.
2. Weather and measurement data: where, and any redistribution restriction. Attribution requirements may be per-site, not per-dataset.
3. If something cannot be shared, say what and why.
4. When `.paper/runs.yml` exists, take the engine version, the inputs and their hashes from the
   rows of the runs behind the reported figures. A version that is not in the record is a
   bracket, not a recollection.

### 12. LLM and stochastic-model studies

For a study whose results come from a large language model or other stochastic generator —
mark N/A when none is used. The same provenance rules apply: an unstated default is still a
default, and a cherry-picked run reported as typical is provenance laundering.

1. Exact model identifier and version, access route (API endpoint or local weights), and
   the access date — hosted models change silently under one name.
2. The prompts, verbatim: system and user, with any templating. Long prompts go to
   Supplementary with a pointer.
3. Decoding parameters: temperature, top-p/top-k, max tokens, stop sequences — and whether
   each was set or left at the provider default.
4. Number of runs, seeds where the platform supports them, and how runs were aggregated
   (mean, majority vote, best-of-N with the selection rule stated).
5. Output parsing and validation logic: what counted as a valid response, how failures and
   refusals were detected, their counts, and the retry rule.
6. Any post-selection: if some runs were excluded or one run is showcased, say which,
   how many, and by what rule.

## Provenance Language

| Provenance | Say this | Never say this |
|---|---|---|
| Measured on site | measured | — |
| From the weather file | taken from the EPW | measured |
| Manufacturer datasheet | manufacturer-reported | measured |
| Standard table | the standard value of | typical |
| Assumed by you | assumed | typical, standard |
| Engine default, knowingly kept | the engine default of X | — |
| Engine default, substituted for a missing input | substituted, X being unavailable | assumed, or silence |
| Model output | modelled, predicted | measured, observed |
| Classified by a model | model-classified | observed |

Rule: if a reader could reasonably read a modelled or defaulted value as a measured one, the
sentence is wrong. Rewrite it.

## When This Gate Applies

Run the gate before submission for any study whose results come from a physics or simulation
engine: Radiance, EnergyPlus, spectral or thermal models, CFD. Under-reported setup and
provenance laundering are Methods defects that no amount of Discussion can repair.

Training an ML model is **not** by itself such a study. Its reproducibility is governed by
`method.md`, `experiments.md` and the paper-review dimensions. A pipeline that embeds a physics
engine, for example rendering training data with Radiance, does trigger the gate for that
component.

## Pre-Submission Gate

Answer each. Any answer that is not the pass answer is a Methods edit, not a Discussion edit.

1. Is the engine version stated, including any local modification?
2. Are all ambient and sampling parameters listed?
3. Is there evidence that the convergence-sensitive parameters converged?
4. Is the weather file identified to the point where someone could obtain the same one?
5. Is ground albedo stated with its provenance, and is a `0.000` handled and disclosed?
6. Are all surface optical properties given with their sources?
7. Are grid spacing, reference plane, and view convention all stated?
8. Is the grid fine enough to resolve the effect, and is censoring disclosed with its direction?
9. Is the reported quantity named exactly, with its standard and action spectrum?
10. Is every point-versus-source distinction made explicit?
11. Is every non-universal convention declared, including weight normalisation?
12. Is the validation scope stated, including what was not validated?
13. Is every known bias disclosed with magnitude and sign?
14. Is every default, inference and model output described as one, and none as a measurement?
15. Could a competent stranger reproduce the headline number from the paper alone?
