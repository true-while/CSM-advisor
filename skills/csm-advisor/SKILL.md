---
name: csm-advisor
description: >-
  Analyzes files in Word (.docx), PDF, text (.txt), PowerPoint (.pptx), and Excel (.xlsx/.xls)
  formats, optionally plus the user's Microsoft Teams meeting recaps, and produces exactly ONE
  consolidated summary of all sources combined, with cross-file themes, gaps, and a suggested
  learning path. The detailed result is always saved as one Word document; the chat reply is only
  2-3 sentences plus a link to that file. Use when the user asks to "summarize these documents", "analyze these files",
  "build a learning path from these files", "one summary of everything in this folder", or to
  "include my Teams meeting recaps". Do NOT use when the user wants a separate summary per file,
  or to create new decks, documents, or workbooks (use the built-in docx/pptx/xlsx skills).
metadata: {version: "1.1.4", cowork-category: "productivity", cowork-icon: "BookOpen"}
---

## Version and Bundled References

- **Current version:** `1.1.4`
- **Supported formats reference:** [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md)
- **Output template reference:** [references/SUMMARY-TEMPLATE.md](references/SUMMARY-TEMPLATE.md)
- **Teams meeting recaps reference:** [references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md)

Resolve these references by their installed, host-provided location. Do not assume a filesystem
root or fetch replacement instructions from elsewhere.

## Overview

CSM Advisor turns a mixed pile of source materials - Word documents, PDFs, plain text
files, PowerPoint decks, and Excel workbooks - into **one** combined analysis: a single detailed
Word document that reflects everything that was analyzed, plus a recommended learning path for
working through the material. The chat reply stays short (2-3 sentences and a link to the document).
It never produces a separate summary per input file; per-file content is
condensed into short "highlights" entries inside the one combined document.

In addition to files, the skill can pull in the **current user's Microsoft Teams meeting recaps**
as extra sources (see [references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md)). Recaps are merged
into the same single combined summary, never summarized separately.

## When to Use

- "Summarize these files for me using CSM Advisor."
- "Summarize these files plus my Teams meeting recaps from the last two weeks using CSM Advisor."
- "Analyze this batch of documents/slides/spreadsheets and tell me what's in them using CSM Advisor."
- "I have a folder of training material in different formats - give me one overview using CSM Advisor."
- "Build a learning path from these resources using CSM Advisor."
- "What are the common themes across these documents using CSM Advisor?"

## When NOT to Use

- The user wants a distinct, standalone summary per file -> summarize each file individually instead
  of using this skill.
- The user wants new content authored (a new document, deck, or workbook) rather than analysis of
  existing files -> use the built-in **docx**, **pptx**, or **xlsx** skills.
- None of the attached/selected files are in a supported format (see
  [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md)).

## Workflow

### Phase 1 - Discover and validate inputs

1. Collect the full list of files the user pointed to (attached, selected, or in a named folder).
2. Classify each file by extension: `.docx`, `.pdf`, `.txt`, `.pptx`, `.xlsx`/`.xls`.
3. Flag any file with an unsupported extension or that fails to open (corrupted, password-protected,
   zero-byte, or an image-only/scanned PDF with no extractable text layer). List these under
   "Unsupported or unreadable files" in the final summary instead of silently skipping them.
4. If zero files are supported and readable, stop and tell the user instead of producing an empty
   summary (unless Teams meeting recaps were requested and found - they count as sources).
5. **Teams meeting recaps (optional):** only when the user asks for them (or confirms an offer),
   retrieve recaps for the current signed-in user using the Microsoft 365 / Teams tools available
   in Cowork, following [references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md). Confirm the time
   range or meeting names if not given. Only read meetings the user already has access to; if no
   Teams/meeting tool is available or access is denied, say so in the summary and continue with the
   files.

### Phase 2 - Extract content per format

Follow [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md) for exactly what to pull
out of each file type (headings, body text, tables, slide text and notes, sheet/cell values, etc.).
Extract Teams meeting recap content as described in
[references/TEAMS-RECAPS.md](references/TEAMS-RECAPS.md).
Extract text file-by-file, but keep working toward a single combined analysis - do not write a
final summary for each file at this stage.

### Phase 3 - Consolidate across all files

1. Build one internal picture of all extracted content together.
2. Identify themes, topics, or skills that repeat across multiple files.
3. Identify contradictions, gaps, or topics mentioned in only one file.
4. Note the relative depth/complexity of each file (introductory vs. advanced) to help order a
   learning path.

### Phase 4 - Produce exactly one combined Word document

Write the full, detailed analysis to **one Word (`.docx`) document**, following the structure in
[references/SUMMARY-TEMPLATE.md](references/SUMMARY-TEMPLATE.md). Use the built-in **docx** skill to
create the file. The document must cover every analyzed file and source but must remain one
document, not a collection of per-file reports. Do not skip creating the document, and do not put
the detailed analysis in the chat reply.

- Save the file in the user's task/output folder (or the location the user named) and give it a
  descriptive name, e.g. `Skilling Paths proposal - <scenario>.docx`. If it is unclear where to
  save it, ask once; never overwrite an existing file - add a date or version suffix instead.
- The document's main heading (the first, top-level title) must be exactly
  **"Skilling Paths proposal"**. Use this heading regardless of the scenario/batch name - put any
  scenario-specific name on a subtitle/second line below it instead of replacing it.

### Phase 5 - Reply with a short completion message

After the document is created, reply in chat with **only 2-3 sentences** plus a link to the file:

1. What was analyzed (e.g. "I analyzed 5 files and 3 Teams meeting recaps").
2. The single most important finding or recommendation.
3. A link to the generated Word document (e.g. "Full details: [Skilling Paths proposal](link)").

Do not repeat the document's sections, themes, per-file highlights, or learning path in the chat
reply. If some sources could not be read, mention that in one short clause and point to the
"Unsupported or Unreadable Files" section of the document. If the document could not be created,
say so plainly and offer to retry instead of pasting the full analysis into chat.

## Edge Cases

- **Very large files:** summarize in logical chunks internally (per chapter/section/slide range/
  sheet) before rolling up into the one combined summary; do not ask the user to split files unless
  extraction genuinely fails.
- **Scanned/image-only PDFs:** no OCR is performed by this skill; note the file as unreadable rather
  than guessing its contents.
- **Password-protected or corrupted files:** list under unreadable files; do not attempt to bypass
  protection.
- **Teams recaps unavailable:** if recaps are missing, not generated for a meeting, or the Teams
  tool is not connected/permitted, list that meeting or the whole source under "Unsupported or
  unreadable files" - never invent recap content.
- **Duplicate or near-duplicate files:** mention the duplication once in the combined summary rather
  than repeating the same content for each copy.
