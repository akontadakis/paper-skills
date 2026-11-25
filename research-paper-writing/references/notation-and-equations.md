# Notation and Equations

**Load when:** the paper carries equations or more than a few symbols.

**Contents:** Goal · Scope · Notation Budget · Symbol Hygiene · Explaining an Equation · Numbering and Reference · Units in Equations · Equation to Code Correspondence · Pseudocode · Nomenclature Table · Checklist

## Goal

Make the mathematics readable on first pass, and make it match the implementation.

## Scope

Symbol definition itself lives in `sentence-craft.md` (Numbers and Units, rule 8: define every
symbol at first use, never redefine it). This file covers how much notation a reader can
absorb, how an equation is explained, and how symbols map to code.

## Notation Budget

1. **At most two new symbols per sentence.** Beyond that the reader is holding more state than
   working memory allows, and will skip the equation.
2. Space new symbols across sentences with explanation between them, rather than defining a
   block of six in one line.
3. **Delete notation used once.** If a quantity appears in exactly one place, name it in words.
   `the sensor grid spacing` beats introducing `\delta_g` for a single mention.
4. Delete notation that adds no precision. A symbol that means exactly what its English name
   means, used twice, is usually not worth the reader's memory.
5. Keep a symbol table for any paper with more than about ten symbols, ordered as
   Nomenclature Table, rule 2, says, unless the journal sets another order.

## Symbol Hygiene

1. One symbol, one meaning, for the whole paper. Reusing `k` for a count and a coefficient is
   a defect even when the context disambiguates.
2. One meaning, one symbol. Do not switch between `E_v` and `E` for the same illuminance.
3. Follow the field's conventions. In lighting, `E` is illuminance and `L` is luminance;
   swapping them to free a letter is never worth it.
4. Distinguish scalars, vectors, and matrices typographically, and say which convention you
   use: `x` scalar, `\mathbf{x}` vector, `\mathbf{X}` matrix.
5. Subscripts carry meaning, so define them: `E_{mel}` versus `E_{v}` versus `E_{h}`.
6. Do not overload a symbol with both a subscript and a superscript that mean different kinds
   of thing without saying so.

## Explaining an Equation

Your core contribution gets all three of these. They must reinforce, not repeat.

1. **Words** — what the equation does and why, before it appears.
2. **The equation** — the precise statement.
3. **A figure** — the geometry or the flow, where it helps.

Rules:

1. Never drop an equation without a preceding sentence saying what it computes.
2. After the equation, define every new symbol in the order it appears in the equation.
3. Do not restate the equation in words afterwards. Say what it *means* or what follows from
   it.
4. An equation is part of the sentence. Punctuate it: comma or full stop after the display,
   and `where` on the following line lowercase.

Shape:

> Melanopic exposure at the eye depends on both the incident spectrum and the observer's
> orientation. The vertical melanopic EDI weights the spectral irradiance at the eye by the
> melanopic action spectrum:
>
> `E_v,mel,D65 = (1 / K_mel,v,D65) ∫ E_e,λ(λ) · s_mel(λ) dλ`   (1)
>
> where `K_mel,v,D65 = 1.3262 mW·lm⁻¹` is the melanopic efficacy of luminous radiation for
> standard illuminant D65 (CIE S 026), `E_e,λ(λ)` is the spectral irradiance at the eye
> (W·m⁻²·nm⁻¹), and `s_mel(λ)` is the melanopic action spectrum (dimensionless, normalised to
> 1 at its peak). The integral runs over 380–780 nm. Dividing by
> `K_mel,v,D65` expresses the result as melanopic equivalent daylight illuminance in lux, so
> that D65 at 100 lx gives `E_v,mel,D65 = 100 lx` by construction.

Note what the definition block does: every symbol gets its units, the integration limits are
given, the constant is named rather than left bare, and the last sentence states the check
that makes the normalisation verifiable. A reader can confirm the equation without the
source. That is the standard for an equation carrying a contribution.

## Numbering and Reference

1. Number every equation you refer to. Do not number ones you never cite.
2. Reference with `\eqref`, never a hardcoded number.
3. Refer to an equation as `Equation (1)` in prose, consistently — not `Eq. 1` in one place
   and `equation one` in another.
4. Long derivations go to an appendix. Keep the main text to the equations a reader must hold.

## Units in Equations

1. State the units of every symbol at definition, in the same place: `E_v (lx)`.
2. Check dimensional consistency across the equation. A reviewer will.
3. Keep constants' units explicit. A bare `1/1.3262` needs its basis stated.
4. Follow `sentence-craft.md` for unit formatting in the surrounding prose.

## Equation to Code Correspondence

The gap between the paper's symbols and the released implementation is a reproducibility
fault, and it is invisible unless you look for it.

1. **Map the names.** If the paper writes `\alpha` and `\beta` and the code uses `lr` and
   `momentum`, either rename in the code or state the mapping in the paper or the repository
   README.
2. **Check the loss definition.** A sign, a mean-versus-sum, or a missing normalisation
   constant between paper and code is the most common mismatch.
3. **Check dimension ordering.** Batch-first versus channel-first, row-major versus
   column-major, and index bases differing between the equation and the array.
4. **Check the defaults.** A hyperparameter stated in the paper must be the one the code
   actually uses when run as documented.
5. Where a paper equation is a simplification of what the code does, say so. Silent
   simplification is provenance laundering — see `simulation-reporting.md`.

For simulation studies, the same rule applies between the equation and the engine's
parameters: if the paper describes a weighting the engine applies differently, state the
engine's actual form.

## Pseudocode

1. Use it only where the procedure is not obvious from the equations.
2. Symbols in pseudocode match the symbols in the equations, exactly.
3. State the inputs and outputs with their types and units.
4. Do not put implementation detail in pseudocode. It is an argument, not a listing.

## Nomenclature Table

Many energy, building-physics, and lighting journals — *Energy and Buildings*, *Building and
Environment*, *Applied Energy*, *Solar Energy*, and others — print a Nomenclature block after
the abstract. Some make it mandatory. Check the journal's guide before deciding to omit one.

A nomenclature table does **not** replace defining a symbol at first use in the text. It is a
lookup for a reader who has jumped into the middle of the paper, and a reviewer treats a symbol
that appears only in the table as undefined.

1. **Three groups, in this order**: symbols, Greek symbols, then abbreviations and acronyms.
   Add a subscripts and superscripts group only if the paper carries enough of them to need one.
2. **Sort within each group** alphabetically, with uppercase before lowercase of the same
   letter.
3. **Three columns**: symbol, description, unit. Give the unit for every dimensional quantity
   and write dimensionless explicitly — a blank unit cell reads as an omission.
4. **Every symbol that appears in a numbered equation goes in the table.** So does every
   abbreviation used three or more times.
5. **Nothing goes in the table that is not in the paper.** A leftover symbol from an earlier
   draft is a visible error and is common, because the table is written once and the equations
   are revised afterwards.
6. **The description matches the text.** Not a paraphrase — the same words, so a reader
   searching for the term finds it.
7. **Units follow `sentence-craft.md`** formatting. The table is not exempt from those rules.
8. **Re-check the table last**, after the final round of equation edits. This is the one
   element in the manuscript that is almost never regenerated when the equations change.

Where a paper has no equations, the block is usually an abbreviations list only. Keep it, drop
the symbol groups, and keep the same rule: every abbreviation used three or more times appears.

## Checklist

1. Any sentence introducing more than two new symbols?
2. Any symbol used only once that could be words instead?
3. Does any symbol carry two meanings, or any quantity two symbols?
4. Does every equation have a preceding sentence saying what it computes?
5. Is every symbol defined in the order it appears, with its units?
6. Is the equation dimensionally consistent?
7. Is every numbered equation referenced, and every reference an `\eqref`?
8. Do the paper's symbols map onto the released code's variable names, or is the mapping
   stated?
9. Does the code's loss, normalisation, and default hyperparameters match the paper?
10. Does the journal require a Nomenclature block, and if so does it list every equation symbol
    and every repeated abbreviation, with units, and nothing the paper no longer uses?
