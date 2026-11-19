# Designing a Simulation Study

**Load when:** the results will come from a simulation or a model: daylight, lighting, thermal, energy, airflow. Load after `study-design.md`.

**Contents:** Goal · Choosing Climates · Choosing Geometries and Buildings · Covering a Parameter Space · Convergence Before Production · Random Variation Between Runs · The Validation Plan · Uncertain Inputs · Simulation Runs Are Not a Sample · The Compute Budget · Decisions to Fix Before the First Run · Checklist

## Goal

Make the design choices that a simulation study cannot repair afterwards: which cases, which
numerical settings, and what the model is checked against. `study-design.md` holds the general
steps; this guide adds what is specific to simulation. The reporting side is
`simulation-reporting.md` in `research-paper-writing`. What is decided here is what that guide
will ask the Methods to state.

## Choosing Climates

1. **Choose by what drives the outcome.** For daylight that is latitude, which sets solar
   altitude and day length, and how often the sky is clear or overcast. For thermal and energy
   studies it is temperature, solar radiation and humidity. A climate classification built on
   temperature and rainfall does not, on its own, describe daylight.
2. **Decide between spanning and contrasting.** To claim that a result holds across climates,
   span the range of the driver. To claim that climate matters, or does not, include climates
   that differ strongly in the driver. Climates that are alike in the driver cannot show an
   effect of it.
3. **Record the weather file as an input**: its source, its type, its period of record and its
   file hash. Its source goes with the climate, in `cases` `members` in `design.yml`. A typical-year file represents average conditions; it says nothing about a
   particular year or about extremes.
4. **Write the limit.** The climates run are the climates the claim holds for.

## Choosing Geometries and Buildings

1. Vary what the question is about. Hold the rest constant, and record each constant with its
   value and source.
2. Say where the set comes from: a survey of a building stock, a reference room from a
   standard, or a parametric space with stated ranges and steps. "Typical" needs a source.
3. State how many cases the set has and how they were generated, so that another group could
   generate the same set.
4. A single case study is a legitimate design. It is named as one, and its claim is about that
   building.

## Covering a Parameter Space

| Situation | Design | Runs |
|---|---|---|
| Few factors, cheap runs | Full factorial: every combination | the product of the numbers of levels |
| Many factors, unknown which matter | Screening first, for example the Morris method, to rank factors and drop the inert ones | r × (k + 1) for k factors and r trajectories |
| Many factors, an estimate over the whole space | A space-filling sample: Latin hypercube or a Sobol sequence | chosen, then checked for convergence |
| Variance-based sensitivity indices | A design made for them, such as the Saltelli scheme | N × (k + 2) for first-order and total indices, or N × (2k + 2) when second-order indices are also computed; N is the base sample |

Rules:

1. Record the design by name, the number of samples, the seed, and the software and version
   that generated the sample.
2. No sample size is right in general. Increase the sample until the statistic that will be
   reported stops changing, and keep that check.
3. Changing one factor at a time from a base case is cheap and shows no interactions. Say so if
   it is the design.
4. Sensitivity indices are valid only for the ranges and distributions given to the inputs.
   Record each range with its source.

## Convergence Before Production

A numerical setting that is too coarse gives an answer that looks like a result.

1. **List the settings the outcome is sensitive to.** For ray tracing: the number of ambient
   bounces and the ambient sampling settings. For an annual matrix method: the sky subdivision,
   and how direct sun is represented. For any spatial result: the sensor grid spacing. For any
   time series: the time step. For a thermal model: the warm-up period and the time step.
2. **Test on the hardest case, not the average one.** For the ambient settings this is the
   deepest room, the darkest sensor, the path with most reflections. It is a stringent first
   test, not proof for every case. Each setting has its own hardest case: for grid spacing and
   a boundary outcome, also test a room where the boundary falls in the middle of the grid.
3. **Refine until the outcome changes by less than the difference the study cares about.**
   Record the settings tried, the outcome at each, and the one chosen.
4. **Know the direction of the error.** With the default ambient value (`-av 0 0 0`), too few
   ambient bounces make deep and low-light points too dark; a non-zero `-av` can make them
   too bright. Where the outcome falls steadily with depth, a boundary read at the last passing
   grid point can fall short of the true boundary by up to one grid spacing.
5. Do this before production. Found afterwards, it means every run again.

## Random Variation Between Runs

A Monte Carlo engine can give different results for the same case. Some repeat exactly when
nothing changes, such as a single-process Radiance `rtrace` with no reused ambient file.

1. Run one case twice with nothing changed. Identical outputs show only that the run-to-run
   spread is zero, and that spread is no floor for the margin. The sampling error remains: the
   ambient-parameter convergence test measures it. Then repeat with what can vary, such as the
   seed where the engine has one, and record the spread of the outcome.
2. A difference between two cases that is smaller than the uncertainty of the difference is
   not a result. The spread of repeated runs is one candidate floor for the no-difference
   margin in `design.yml`; the grid spacing and the smallest effect of interest are others.
   The researcher chooses, with the reason.
3. Record the seed of each production run where the engine allows one to be set.

## The Validation Plan

Decide what the model is checked against, before the production run.

1. **Against measurement**: in the room modelled, or in a comparable one. State what was
   measured, with which instrument, and over which period.
2. **Against an analytical case or a published test suite**, where no measurement exists. CIE
   171:2006 gives test cases for lighting programs; check each case against the published
   corrections. ANSI/ASHRAE Standard 140 gives a test method
   for building energy programs; use its current edition. Such cases test the engine on simple
   scenes. They do not validate an annual climate-based result or a spectral one.
3. **Against another engine.** Agreement between two engines shows consistency. It is not
   validation against reality, and it is named as a comparison.
4. **Fix the acceptance margin first**: the bias and the scatter that will count as agreement,
   and where that margin comes from. A margin chosen after the comparison always passes.
5. **If no validation is possible, record it now** as an accepted threat. Every result is then
   a model output and is worded as one.

## Uncertain Inputs

1. List the inputs that are assumed and not measured: surface reflectances, glazing
   transmittance, ground reflectance, occupancy hours, internal gains.
2. For each, record the value, its source, and a plausible range with its source, in
   `held_constant` in `design.yml`.
3. Plan at least one sensitivity run per influential input, at the ends of its range, and say
   how the result will be reported: as a range on the headline number.
4. A default is an input. Record it as a default, with the program version it came from.

## Simulation Runs Are Not a Sample

1. A simulation with fixed inputs, settings and seed gives the same output each time.
   Twenty-four geometries chosen by the researcher are 24 cases, not a random sample of
   offices.
2. An inferential test across such cases treats them as a sample of a population. Put the two
   options to the researcher. One: name the population and the rule by which the cases were
   drawn from it, and plan a test. Two: report differences, ranges and the no-difference
   margin, with no test. The first needs a sampling rule that most case sets do not have.
3. Hours within a run and points within a grid are never the n.

## The Compute Budget

1. Time one run on the smallest case and on the hardest case.
2. Multiply by the number of runs, and add the convergence tests, the repeats and the
   sensitivity runs.
3. If the total does not fit, decide now what is cut: a factor level, a case set, or the
   sensitivity runs. Record the cut and what it costs the claim.

## Decisions to Fix Before the First Run

These change the result and are easy to change quietly later. Each goes in `design.yml`.

1. The exact quantity. For a melanopic study: melanopic EDI under CIE S 026, or equivalent
   melanopic lux (EML). EML is larger by a constant factor of about 1.10. Use the quantity
   the threshold was defined in, and name it.
2. The threshold and its source, and the hours it applies to.
3. The plane and the position: horizontal workplane, or vertical at eye height, and the view
   direction convention.
4. How spectral information is carried: full spectra, more than three channels, or a fixed
   ratio applied to a photopic result. A three-channel calculation does not carry a full
   spectrum, so a melanopic result from it rests on an assumption. Record the assumption and
   how its error will be checked.
5. The sky model and its inputs.

## Checklist

1. Is each climate chosen for a stated reason tied to what drives the outcome?
2. Is each weather file recorded with source, type, period and hash?
3. Is the geometry set described so that another group could generate it?
4. Is the parameter-space design named, with its sample count and seed?
5. Was convergence tested on the hardest case, before production, for each sensitive setting?
6. Is the run-to-run spread known (zero for an engine that repeats exactly), and is it a floor
   of the no-difference margin?
7. Is the validation target named, with a margin fixed in advance, or recorded as not possible?
8. Does each assumed input have a source and a range?
9. Is any planned test tied to a named population, or is "no test" stated?
10. Does the compute budget fit, and is each cut recorded?
