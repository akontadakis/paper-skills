# Figures and Tables Guide

**Load when:** designing or revising a figure, a table or a caption, or checking a figure against its data and the Methods.

**Contents:** Goal · Mechanical Check · Figure or Table · Self-Containment · Caption Anatomy · Error Bars and Uncertainty · Colour and Accessibility · Ink and Clarity · Honest Encoding · Check a Figure Against Its Source · Sizing and Legibility · Files and Resolution · Tables · Numbering and Referencing · Common Mistakes · Checklist

## Goal

Make display items that carry the argument on their own, and that survive greyscale, colour-blind
vision, and a reader who reads only the captions.

`Visual quality is core content, not decoration.`

For LaTeX table mechanics (`booktabs`, rules, highlighting, metric-direction arrows), see the
`Figure/Table Writing Rules` section of `experiments.md`. This guide does not repeat those.

That section is **shape-neutral** — load it for a journal paper too, if the paper has a table.
The rest of `experiments.md` is conference-only. Loading the one section is not a violation of
the shape rule in `SKILL.md`.


## Mechanical Check

Design is judged by reading. Resolution at printed size is not — it is arithmetic, and it is
the fault that survives every visual review because the figure looks correct on screen.

```bash
python3 scripts/extract_figures.py audit manuscript.pdf --min-dpi 300
```

It reports every embedded raster's pixel size, its printed size in millimetres, and the
effective dpi that follows. A manuscript whose figures are all vector correctly reports nothing
to audit, which is the right answer for plots and diagrams. Fix a low-dpi figure by exporting
it at the width it is placed at, never by resizing it on the page.

## Figure or Table

| Use a table | Use a figure |
|---|---|
| Exact values matter | Shape, trend, or pattern matters |
| Many variables, few points | Many points, few variables |
| Readers will look up a specific number | Readers will compare at a glance |
| Values differ by category with no ordering | Values vary continuously |
| Precision is the point | Magnitude of difference is the point |

Rules:

1. If the pattern is the message, a figure. If the number is the message, a table.
2. Fewer than about six numbers: put them in the sentence, not in a display item.
3. Never show the same data as both a figure and a table.

## Self-Containment

Every display item must be readable with the body text covered.

1. Caption states the message, not just the subject.
2. All axes labelled with quantity **and** unit.
3. All abbreviations in the item expanded in the caption or a footnote, even if defined in the text.
4. n stated, with its unit — points, sites, hours, timesteps — and the independent unit named where it differs: `n = 8,760 h, one room`. See `statistics-reporting.md`, What n Counts.
5. Error bars defined in the caption. Always say **what** they are.
6. Conditions that make the number reproducible: geometry, sky, engine settings, period.

## Caption Anatomy

Four parts, in this order:

1. **Label and title** — `Figure 4. Compliant plan depth by view direction and climate.`
2. **What is plotted** — quantity, units, sample, period.
3. **How to read it** — what the symbols, bands, shading, and dashed lines mean.
4. **What it shows** — one sentence naming the message. Not a discussion.

Rules:

1. Figure captions go below the figure; table captions go above the table.
2. Do not put interpretation in a caption beyond the one-sentence message.
3. Do not repeat the caption sentence verbatim in the body text.
4. Keep the caption's terminology identical to the text's.

## Error Bars and Uncertainty

1. **Always state in the caption what the bars are**: SD, SE, 95% CI, min–max, interquartile range. An undefined error bar is unreadable.
2. Do not mix bar types across panels of one figure.
3. SD describes the spread of the data. SE and CI describe uncertainty in the estimate. Pick the one that matches the claim.
4. For simulated results, shading that shows a parameter sweep is not an uncertainty interval. Label it as a sweep.
5. If there is no meaningful uncertainty, show none and say why.

## Colour and Accessibility

1. **Never encode meaning in colour alone.** Add shape, line style, direct labels, or hatching.
2. Avoid red–green pairs. Roughly 1 in 12 men cannot separate them.
3. Safe qualitative choices: blue / orange / grey, or a colour-blind-safe set (Okabe–Ito, viridis for sequential).
4. Sequential data gets a perceptually uniform ramp (viridis, cividis). Never use jet or rainbow — it invents boundaries that are not in the data.
5. Diverging data gets a diverging ramp with a meaningful, stated midpoint.
6. Test in greyscale. Many readers print in mono, and some journals still charge for colour.
7. Contrast: dark text on light background, minimum 4.5:1.
8. Do not use colour to make a figure look busy or expensive.
9. **Alt text**, where the journal or the portal asks for it: one or two sentences giving the
   chart type, the axes with units, the groups compared, and the main visible pattern. It
   states what the figure shows, adds no conclusion the caption does not carry, and does not
   repeat the caption word for word. Writing it is also a check: if the pattern cannot be
   said in two sentences, the figure has more than one message.

## Ink and Clarity

1. Remove anything that is not data or the minimum needed to read it: gridline clutter, 3-D effects, drop shadows, boxes around legends, background fills.
2. Direct-label lines where there are few enough series; drop the legend.
3. Bar charts start at zero. Line charts need not, but a truncated axis must be visibly marked.
4. Do not use a bar chart for a continuous variable.
5. Do not use a pie chart.
6. One figure, one message. If a figure has two messages, it is two figures.
7. Panels get letters (a), (b), (c) and are referenced individually in the text.

## Honest Encoding

A figure can be accurate in every value and still mislead through its scales. These are the
encodings a reviewer in this field checks.

1. **Compared panels share their scale.** Two false-colour luminance or illuminance maps set
   side by side for comparison use one colour scale with the same limits, and two plots of
   the same quantity use the same axis limits. Automatic scaling per panel makes a dim case
   and a bright case look alike. If the ranges differ too much for one scale, say so in the
   caption and give each panel's limits.
2. **Every colour bar carries its quantity and unit**, and states whether the scale is linear
   or logarithmic. A false-colour map with tick numbers and no unit is unreadable.
3. **Avoid dual y-axes.** Two quantities on two axes of one plot can be made to cross, track,
   or diverge by the choice of scales alone, and the reader sees a relation the data may not
   hold. Use two aligned panels with a shared x-axis. Keep a dual axis only where the two
   scales are a fixed conversion of each other, such as lux and foot-candles.
4. **A logarithmic axis says so**, with its base, in the axis label or the caption. State what
   was done with zero and negative values, which a log axis cannot show: dropped, clipped to
   a floor, or shifted. Do not use a log axis to make a small difference look large or a
   large one small without saying why the scale was chosen.
5. **A gap in the data is drawn as a gap.** Do not join the points on either side of a sensor
   dropout, a failed run, or a night-time interval with a straight line. Keep missing,
   zero, below-detection, and excluded visibly distinct, and give the count of each.
6. **Significance stars are not uncertainty.** Stars and brackets say a test was run. They do
   not replace the interval, and they do not belong on a figure whose samples are not
   independent — `statistics-reporting.md`, What n Counts.
7. **Area encodes value by area.** A circle or symbol scaled by radius exaggerates the
   quantity by its square.
8. **Aggregation is stated.** Say what each point or bar summarises — a mean over which hours
   and which points — and what was done before plotting: smoothing, binning, normalisation,
   outlier removal.

## Check a Figure Against Its Source

The rules above ask whether a figure is drawn well. This check asks whether it shows what the
paper did and found. Open the rendered figure, the image file or the page of the compiled PDF,
not only the script or the caption. Then read it against its source, item by item.

**Not checked.** If the figure image, the data file or the script behind it cannot be opened,
report the figure as **not checked** and name what was missing. Do the same for a plot whose
`transformation` is `null` or whose `source` is `manual`. Never report it clean. A diagram has no
data file: read it against the Methods, as below.

**A plot, against its data.** The data are the values that the figure's `transformation` in
`.paper/figures.yml` gives: the input file named there, after the filtering, averaging and
other steps it lists. `runs` names rows of `.paper/runs.yml`; it points to the code and the
inputs, and is not a data file.

1. Read every plotted value off the figure: bar heights, point positions, printed numbers. Each
   matches the value that the recorded `transformation` gives, within the reading precision of
   the axis, about half the smallest tick interval. On a log axis or a colour bar the precision
   is coarse: say so, and grade a difference inside it as minor, marked `within reading precision`. A value that is
   added, left out or changed beyond that precision is a fault.
2. Compare the figure with its `key_numbers`. Each number there can be found in the figure, at
   the same reading precision, and every number the prose quotes from the figure is in the row.
3. Each legend entry marks the series it names. Check colours and symbols against the data,
   not against the axis labels beside them.
4. Each axis names its quantity and unit as the text names them.

**A diagram, against the Methods.**

1. Each block and each arrow matches something the Methods describe. A block or a connection
   the Methods do not describe is a fault.
2. Walk the Methods sentence by sentence and find each step in the diagram. A step the diagram
   leaves out is a fault, as serious as one it adds.
3. The arrows follow the order the Methods give.

**Any figure.** The caption sits in the manuscript, not inside the image. No label is garbled,
cut off or misspelled. A box holds a short label, not a sentence copied from the text.

**Grading.** A figure that disagrees with its data or its Methods is **critical**: a reader takes
the figure as the result. That covers a wrong value, a swapped legend, an added step and a
missing step, beyond the reading precision. A difference inside the reading precision is
minor, marked `within reading precision`, and the faults under "Any figure" are minor.

**Do not decide which side is right.** When a figure and its source disagree, report both and ask
the author which is wrong. A step drawn in a diagram may be a step the Methods forgot, or a step
that was never done. Never complete the Methods from the figure, or the figure from the Methods.

Record each finding in the finding contract of `paper-review.md`, with the figure id and the
source it was compared with.

## Sizing and Legibility

1. Design at final print size. A figure shrunk to one column must still be readable.
2. Minimum font in the final figure, measured after scaling: 7 pt. Print the page and check.
3. Keep font sizes consistent across all figures in the paper. Figures made months apart drift.
4. Line weights heavy enough to survive downscaling.
5. Two-column papers: decide single- or double-column width **before** drawing, not after.
6. Column widths and the minimum lettering size are the journal's. Elsevier's general
   instructions give 90 mm, 140 mm, and 190 mm for single, one-and-a-half, and double column,
   and 7 pt lettering with sub- and superscripts no smaller than 6 pt, as a rule of thumb
   (checked 2026-11-15). The 7 pt minimum in rule 2 is the default where the guide is silent.

## Files and Resolution

1. Vector (PDF, EPS, SVG) for anything drawn: plots, diagrams, schematics.
2. Raster (PNG, TIFF) only for photographs, renderings, and false-colour images.
3. Raster resolution is set by the journal's artwork instructions, recorded in `.paper/venue.yml`,
   not by this file. Where the guide gives none, use 300 dpi for photographs and renderings and 500 dpi for
   combination images, with line art as vector, or at 1000 dpi where it must be raster. These are common publisher defaults, not a
   rule of every journal: check the journal's guide. Publishers differ: Elsevier's general artwork instructions ask for
   300 dpi halftones, 500 dpi combination art, and 1000 dpi line art, at final size (checked
   2026-11-15). Read the target journal's guide for authors, and record the values and the
   date checked in the `rules` block of `.paper/venue.yml` — see `venue-calibration.md`.
4. Never rasterise a plot you could ship as vector.
5. Never upscale a raster to meet a dpi requirement.
6. No lossy JPEG for figures with text or sharp edges.
7. Image manipulation: adjustments must be applied to the whole image and disclosed. Never move, splice, or selectively enhance a region.

## Tables

Layout mechanics — `booktabs` rules, `\multicolumn`/`\cmidrule` grouping, decimal alignment,
metric-direction arrows, restrained highlighting — are in the `Figure/Table Writing Rules`
section of `experiments.md` and are not repeated here. This section covers only what that
guide does not:

1. Row and column order must carry meaning: by magnitude, by time, or by the order the text uses. Never by the order you happened to compute them.
2. Units go in the column header, once, not in every cell.
3. If a table exceeds roughly 10 rows or 8 columns, ask whether it is really a figure, or supplementary material.
4. A table read aloud should sound like a sentence: row label, then values, then the comparison the reader is meant to make.
5. Where `experiments.md` says to highlight the best value with colour, that highlight is emphasis on a value the table already states in text — it is not the sole carrier of meaning, so it does not violate the colour rule above. Keep it to one or two cells.

## Numbering and Referencing

1. Number in order of first mention. Figures and tables number separately.
2. Every display item is referenced in the text at least once.
3. Reference by number, not by position: `Table 3`, never `the table below`.
4. Do not reference a figure before the one preceding it.

## Common Mistakes

1. Error bars with no stated meaning.
2. Rainbow or jet colour maps.
3. Meaning carried by colour alone.
4. Caption that names the subject but not the message.
5. The same data as both a figure and a table.
6. Text that reads out the table cell by cell.
7. Axis labels without units.
8. Figures built at screen size, then shrunk into illegibility.
9. Inconsistent fonts and line weights between figures made at different times.
10. A "teaser" figure that is decorative rather than informative.
11. Compared maps or plots on separate automatic scales.
12. A colour bar with no unit.
13. Two unrelated quantities on a dual y-axis.
14. A line drawn straight across missing data.
15. A resolution or width quoted from memory instead of from the journal's guide.

## Checklist

1. Is each display item readable with the body text covered?
2. Does every caption end with a one-sentence message?
3. Are all axes labelled with quantity and unit?
4. Is every error bar defined?
5. Is n stated?
6. Does the figure survive greyscale and colour-blind simulation?
7. Are fonts and line weights consistent across all figures?
8. Is anything shown twice, in a figure and a table, or in a display item and the prose?
9. Is every item referenced in the text, in order?
10. Are vector formats used everywhere they could be?
11. Do compared panels share one colour scale and one set of axis limits?
12. Does every colour bar carry a quantity, a unit, and its scale type?
13. Is every dual axis replaced by aligned panels, or justified as a fixed conversion?
14. Is every log axis labelled, with its treatment of zero and negative values stated?
15. Are gaps in the data drawn as gaps?
16. Were resolution, width, and lettering size checked against the journal's guide, with the
    date recorded?
