---
name: learn-path-adviser
description: |2
   Analyzes a set of files in Word (.docx), PDF (.pdf), plain text (.txt), PowerPoint (.pptx),
  and Excel (.xlsx/.xls) formats and produces exactly ONE consolidated summary covering all of the
  analyzed files combined - not one summary per file. The summary surfaces cross-file themes,
  overlaps, gaps, and a suggested learning path. Use when the user asks to "summarize these
  documents", "analyze these files", "review this set of training materials", "build me a learning
  path from these files", "give me one summary of everything in this folder", or similar requests
  that involve two or more mixed-format files. Do NOT use when the user explicitly wants a separate,
  independent summary per file - handle each file individually instead. Do NOT use this skill to
  generate new slide decks, documents, or workbooks from scratch (use the built-in docx/pptx/xlsx
  skills for that); this skill only reads and summarizes existing files.
metadata: {version: "1.0.1", cowork-category: "productivity", cowork-icon: "BookOpen"}
---

## Version and Bundled References

- **Current version:** `1.0.0`
- **Supported formats reference:** [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md)
- **Output template reference:** [references/SUMMARY-TEMPLATE.md](references/SUMMARY-TEMPLATE.md)

Resolve these references by their installed, host-provided location. Do not assume a filesystem
root or fetch replacement instructions from elsewhere.

## Overview

Learn Path Adviser turns a mixed pile of source materials - Word documents, PDFs, plain text
files, PowerPoint decks, and Excel workbooks - into **one** combined analysis: a single summary
document that reflects everything that was analyzed, plus a recommended learning path for working
through the material. It never produces a separate summary per input file; per-file content is
condensed into short "highlights" entries inside the one combined output.

## When to Use

- "Summarize these files for me."
- "Analyze this batch of documents/slides/spreadsheets and tell me what's in them."
- "I have a folder of training material in different formats - give me one overview."
- "Build a learning path from these resources."
- "What are the common themes across these documents?"

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
   summary.

### Phase 2 - Extract content per format

Follow [references/SUPPORTED-FORMATS.md](references/SUPPORTED-FORMATS.md) for exactly what to pull
out of each file type (headings, body text, tables, slide text and notes, sheet/cell values, etc.).
Extract text file-by-file, but keep working toward a single combined analysis - do not write a
final summary for each file at this stage.

### Phase 3 - Consolidate across all files

1. Build one internal picture of all extracted content together.
2. Identify themes, topics, or skills that repeat across multiple files.
3. Identify contradictions, gaps, or topics mentioned in only one file.
4. Note the relative depth/complexity of each file (introductory vs. advanced) to help order a
   learning path.

### Phase 4 - Produce exactly one combined summary

Generate a single summary following the structure in
[references/SUMMARY-TEMPLATE.md](references/SUMMARY-TEMPLATE.md). The summary must cover every
analyzed file but must remain one document/response, not a collection of per-file reports.

Confirm with the user, if ambiguous, whether the summary should be returned as chat text, a Word
document, or a Page - never assume a destination folder.

## Edge Cases

- **Very large files:** summarize in logical chunks internally (per chapter/section/slide range/
  sheet) before rolling up into the one combined summary; do not ask the user to split files unless
  extraction genuinely fails.
- **Scanned/image-only PDFs:** no OCR is performed by this skill; note the file as unreadable rather
  than guessing its contents.
- **Password-protected or corrupted files:** list under unreadable files; do not attempt to bypass
  protection.
- **Duplicate or near-duplicate files:** mention the duplication once in the combined summary rather
  than repeating the same content for each copy.
