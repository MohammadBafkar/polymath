---
name: editorial-pass
description: Tighten prose in a markdown artifact for a target tone (terse, formal, friendly) without dropping information; preserve quotations and load-bearing constraints.
---

# editorial-pass

> Make prose shorter, clearer, and consistent in tone — but never at the cost of dropping a constraint, contradicting the source, or smoothing over an honest "I don't know."

## When to use

- A draft of a PR description, RFC, runbook, postmortem, ADR, or release-notes block needs to be tightened before publishing.
- The user says "tighten this," "make this shorter," "edit for tone."
- A workflow step invokes `polymath-writing:editorial-pass`.

## When **not** to use

- The input is fundamentally wrong (factual errors, missing sections). Editorial-pass tightens prose; it does not authoring-pass.
- The input is a quotation or a verbatim user statement. Mark and skip.
- The text is already at the target tone and ≤ 15% over its budget. Diminishing returns; return unchanged with a one-line note.

## Inputs

- **Artifact path** (markdown file or inline snippet).
- **Target tone**: `terse` (default) | `formal` | `friendly`.
- **Length budget** (optional): max words, max sentences, or a percentage of the original (e.g. `target_length: 70%`).
- **Sections to preserve**: list of section headings (or frontmatter keys) that must round-trip unchanged.

## Procedure

1. **Read** the source artifact end-to-end. Note any sections in `preserve_sections` and any block quotations (`> ...`).
2. **Classify each paragraph** by intent: *claim*, *evidence*, *recommendation*, *quotation*, *aside*. Quotations and asides are out of scope.
3. **For each claim or recommendation paragraph**:
   - Strip filler ("In order to" → "To", "It is the case that X" → "X is").
   - Collapse parallel sentences with a shared subject ("X is fast. X is small." → "X is fast and small.").
   - Replace nominalisations with verbs ("perform a review of" → "review").
   - Cut hedges that don't add information ("It might be the case that arguably possibly" → "Possibly").
   - Stop when the next cut would drop a load-bearing constraint, qualification, or named entity.
4. **For each evidence paragraph**: keep numbers, dates, identifiers, and citations verbatim. Cut only connective tissue.
5. **Apply the tone**:
   - `terse` — drop adverbs, prefer the active voice, prefer concrete nouns over abstract ones.
   - `formal` — keep full sentences, no contractions, no parenthetical asides.
   - `friendly` — keep contractions, allow one rhetorical question per ~500 words, keep "we" / "you."
6. **Diff the result against the source.** For every cut, mark whether the cut dropped (a) nothing of meaning, (b) a qualification, (c) a constraint. Cuts in category (c) MUST be reversed.
7. **Emit a one-line note** per paragraph documenting what was cut and why (e.g. "Paragraph 3: -40% length; dropped 3 adverbs, no information lost").
8. **Save the edited artifact** alongside the original (do not overwrite) at `<path>.edited.md` unless the user explicitly asks for in-place replacement.

## Quality bar

- **Length** stays at or under the declared budget (or 15% reduction if no budget).
- **Section count** is identical between source and output unless `preserve_sections` was empty.
- **No quotation is rewritten.** Block quotations (`> …`) and `code blocks` survive byte-for-byte.
- **No new claims.** Editorial-pass does not introduce facts, numbers, names, or recommendations the source did not contain.
- **No silent removal of a hedge that carried information.** "Approximately 80%" stays "approximately 80%"; "approximately" is not filler when the number is approximate.
- **Frontmatter is preserved.** Editorial-pass does not touch YAML frontmatter.

## Anti-patterns to refuse

- **"Tightening" that loses information.** Cutting "the rate limit fires after 10 attempts per minute" to "rate limit fires" drops the load-bearing numeric.
- **Rewriting a quotation.** A quoted user voice survives verbatim. If you can't keep it verbatim, leave it.
- **Inventing a recommendation.** If the source says "we should consider X," the output cannot say "we should X." That's authoring, not editorial.
- **Smoothing over an honest unknown.** "We don't know whether X is safe" stays a statement of unknowing; do not edit to "X requires further analysis."
- **Tone-shifting load-bearing safety language.** A runbook step "Do NOT restart the database without paging the DBA" stays that emphatic; `formal` tone does not lower the urgency.

## Output

- File: `<path>.edited.md` (default) or `<path>` (in-place) per user request.
- One-line summary: "edited <path>.edited.md (source N lines, output M lines, Δ -X%)."
- Per-paragraph cut report.

## Workflow validation

```yaml
mustPass:
  - id: editorial-pass-produced-shorter-output
    type: diffConstraint
    filesChanged:
      min: 1
      max: 2
    linesChanged:
      min: 1
  - id: editorial-pass-preserved-quotes
    type: stepSummaryMatches
    severity: advisory
    step: editorial-pass
    pattern: "(quotation(s)?|verbatim|preserved)"
```
