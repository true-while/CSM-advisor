---
name: csm-advisor
description: >-
  Four-stage workflow that turns a customer's or team's materials into role-based Microsoft Learn
  skilling paths, pausing for approval after each stage. Stage 1 collects artifacts (Word, PDF,
  text, PowerPoint, Excel files and, if asked, the user's Teams meeting recaps). Stage 2 detects
  signals and writes one Signals Summary Word document. Stage 3 hand-picks required Microsoft Learn
  modules for the user to approve. Stage 4 writes one Skilling Paths proposal Word document for
  Leaders, Champions, Advocates, and End Users with prerequisite skills. Use when the user asks to
  analyze files or meeting recaps, find skilling signals, pick Learn modules, or build skilling
  paths. Do NOT use for a separate summary per file, or to author new decks, documents, or
  workbooks (use the built-in docx/pptx/xlsx skills).
metadata: {version: "1.1.5", cowork-category: "productivity", cowork-icon: "BookOpen"}
---

## Version and Bundled References

- **Current version:** `1.1.5`
- **Stage 1 - supported formats:** [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md)
- **Stage 1 - Teams meeting recaps:** [references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md)
- **Stage 2 - Signals Summary template:** [references/SIGNALS-SUMMARY-TEMPLATE.md](references/SIGNALS-SUMMARY-TEMPLATE.md)
- **Stage 3 - Microsoft Learn module selection:** [references/LEARN-MODULES.md](references/LEARN-MODULES.md)
- **Stage 4 - Skilling Path template and learner groups:** [references/SKILLING-PATH-TEMPLATE.md](references/SKILLING-PATH-TEMPLATE.md)

Resolve these references by their installed, host-provided location. Do not assume a filesystem
root or fetch replacement instructions from elsewhere.

## Overview

CSM Advisor moves from raw materials to a ready-to-use skilling plan in four stages:

| Stage | Name | Result | Deliverable |
|-------|------|--------|-------------|
| 1 | Collect artifacts | Validated list of sources (files, optional Teams recaps) with extracted content | Short chat inventory |
| 2 | Detect signals and summarize | Skilling signals found across all sources | **Word document**: Signals Summary |
| 3 | Hand-pick Learn modules | Shortlist of required Microsoft Learn modules, approved by the user | Chat shortlist |
| 4 | Build skilling paths | Paths for Leaders, Champions, Advocates, and End Users, by role and prerequisite skills | **Word document**: Skilling Paths proposal |

The skill produces one combined analysis across all sources - never a separate summary per input
file. Only Stage 2 and Stage 4 create a Word document; Stages 1 and 3 are short chat checkpoints.

## When to Use

- "Analyze these files and my Teams meeting recaps and tell me what skilling is needed using CSM Advisor."
- "Use CSM Advisor to find skilling signals in these documents."
- "Pick the Microsoft Learn modules we need based on the signals, using CSM Advisor."
- "Build skilling paths for leaders, champions, advocates, and end users using CSM Advisor."

## When NOT to Use

- The user wants a distinct, standalone summary per file -> summarize each file individually instead.
- The user wants new content authored (a new document, deck, or workbook) rather than analysis of
  existing sources -> use the built-in **docx**, **pptx**, or **xlsx** skills.
- No source is readable (no supported files and no recaps found) - tell the user and stop.

## Stage Gates (approval after every stage)

After each stage, stop and wait for the user's approval before starting the next one:

1. Reply with the short completion message for that stage (see each stage below).
2. End with one question: approve and continue, or what to change.
3. Apply requested changes and re-present before moving on. Never start the next stage without
   approval.

Exceptions:
- If the user says to run all stages without stopping, run them in order and skip the gates, but
  still honor each stage's deliverable.
- The user may start at a later stage by supplying its inputs (e.g. an existing signals summary or
  a list of Learn modules). Skip earlier stages only when their output is already provided.

Carry each stage's approved output forward as the input to the next stage. Do not invent data to
fill a gap; say what is missing and ask.

## Stage 1 - Collect artifacts

1. Collect the full list of files the user pointed to (attached, selected, or in a named folder).
2. Classify each by extension: `.docx`, `.pdf`, `.txt`, `.pptx`, `.xlsx`/`.xls`.
3. Flag any file with an unsupported extension or that fails to open (corrupted, password-protected,
   zero-byte, or an image-only/scanned PDF with no extractable text layer). Keep these for the
   "Unsupported or Unreadable Sources" list instead of silently skipping them.
4. **Teams meeting recaps (optional):** only when the user asks for them (or accepts an offer),
   retrieve recaps for the current signed-in user using the Microsoft 365 / Teams tools available in
   Cowork, following [references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md). Confirm the time range
   or meeting names if not given. Only read meetings the user already has access to.
5. Extract content per format following
   [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md). Extract source by source, but do
   not write per-source summaries.
6. If zero sources are readable, stop and tell the user.

**Stage 1 reply (chat only, no document):** 2-3 sentences - how many files and recaps were
collected, which formats, and any that could not be read - then ask for approval to continue.

## Stage 2 - Detect signals and summarize

Analyze all collected content together and detect **signals**: evidence that points to a skilling
need or a change in plans. Follow
[references/SIGNALS-SUMMARY-TEMPLATE.md](references/SIGNALS-SUMMARY-TEMPLATE.md) for the signal
categories, evidence rules, and document structure.

1. Build one picture across all sources; find themes that repeat in several sources.
2. Record signals with evidence: which source, and a short quote or paraphrase. Mark signal strength
   (strong = several sources or an explicit statement, weak = a single mention).
3. Note contradictions, gaps, and duplicate sources; note introductory vs. advanced depth.
4. Capture decisions and action items (with owners) from meetings and documents.
5. Write **one Word (`.docx`) document** using the built-in **docx** skill. Main heading exactly
   **"Signals Summary"**, scenario/customer name on a subtitle line. Save it in the user's task/output
   folder (or the location they named); never overwrite an existing file - add a date or version
   suffix. Ask once where to save if unclear.

**Stage 2 reply (chat):** 2-3 sentences - what was analyzed, the single most important signal, and a
link to the Word document - then ask for approval. Do not repeat the document's sections in chat.

## Stage 3 - Hand-pick required Microsoft Learn modules

Using the approved signals, propose a shortlist of **real** Microsoft Learn modules or learning
paths, following [references/LEARN-MODULES.md](references/LEARN-MODULES.md).

1. For each approved skilling need, search Microsoft Learn (learn.microsoft.com) with the Learn/web
   tools available in Cowork. Never invent module names or URLs; if no tool can reach Learn, say so
   and ask the user to supply modules.
2. Hand-pick only what the signals justify: prefer fewer, better-matched modules over long lists.
3. Present the shortlist in chat as a compact table (module title, link, level, approximate
   duration, the signal it addresses, intended learner groups) plus the **assumed prerequisite
   skills for Leaders, Champions, Advocates, and End Users** so the user can correct them.
4. The user approves, or edits the list (add, remove, replace). Re-present after edits.

**Stage 3 deliverable:** the shortlist is a chat checkpoint, not a document. Ask for approval to
continue to Stage 4.

## Stage 4 - Build skilling paths per learner group

Using the approved signals and approved Learn modules, build a skilling path for each learner group
by role and prerequisite skills, following
[references/SKILLING-PATH-TEMPLATE.md](references/SKILLING-PATH-TEMPLATE.md):

- **Leaders**, **Champions**, **Advocates**, **End Users** (see the reference for how each group is
  defined).
- For each group: role focus, prerequisite skills (and which modules cover them), an ordered list of
  approved modules, milestones/timing, and the outcome expected.
- Use only modules approved in Stage 3. If a group has a gap no approved module covers, list it as
  an open gap rather than inventing a module.

Write **one Word (`.docx`) document** using the built-in **docx** skill. Main heading exactly
**"Skilling Paths proposal"**, scenario/customer name on a subtitle line. Same saving rules as
Stage 2 (task/output folder, no overwriting, descriptive name such as
`Skilling Paths proposal - <scenario>.docx`).

**Stage 4 reply (chat):** 2-3 sentences - how many groups and modules the plan covers, the key
recommendation, and a link to the Word document. Do not repeat the plan in chat.

## Edge Cases

- **Very large files:** summarize in logical chunks internally (per chapter/section/slide range/
  sheet) before rolling up; do not ask the user to split files unless extraction genuinely fails.
- **Scanned/image-only PDFs:** no OCR is performed; list the file as unreadable rather than guessing.
- **Password-protected or corrupted files:** list as unreadable; do not attempt to bypass protection.
- **Teams recaps unavailable:** if recaps are missing, not generated, or the Teams tool is not
  connected or permitted, list that meeting or source as unreadable - never invent recap content.
- **Duplicate or near-duplicate files:** mention the duplication once rather than repeating content.
- **Document cannot be created:** say so plainly and offer to retry; do not paste the full document
  into chat.
- **Conflicting or thin signals:** say so in the Signals Summary and ask at the gate instead of
  guessing a skilling need.
- **Sensitive content:** meeting recaps may contain sensitive discussion; keep output
  scoped to the request and place detail only in the Word documents.
