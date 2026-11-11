# Combined Summary Output Template

Produce exactly one document using this structure, regardless of how many files were analyzed. It
is always delivered as a Word (`.docx`) file. Omit a section only if it genuinely does not apply
(e.g. no unreadable files).

The document's main heading must be exactly **"Skilling Paths proposal"** - put the
scenario/batch name on a subtitle line underneath instead of in the main heading. In the template
below, the first line shows that title and subtitle.

## Chat reply (separate from the document)

The detailed content below goes ONLY into the Word document. In chat, reply with 2-3 sentences (what
was analyzed, the key finding, and a link to the document) and nothing more:

> I analyzed 5 files and 3 Teams meeting recaps for <scenario>. The main takeaway is <one key
> finding or recommendation>. Full details: [Skilling Paths proposal](<link to the .docx>)

## Document structure

```text
# Skilling Paths proposal
<Scenario/Batch Name> - Combined Analysis (subtitle line)

Generated: <date>
Files analyzed: <count> (<formats present, e.g. "2 Word, 1 PDF, 3 PowerPoint, 1 Excel">)
Teams meeting recaps included: <count, or omit this line if none were requested>

## Sources
- <file name 1> (.docx) - <one-line description>
- <file name 2> (.pdf) - <one-line description>
- <meeting title> (Teams recap, <date>) - <one-line description>
- ... one line per analyzed file or meeting recap

## Executive Overview
<3-6 sentences describing, across ALL files together, what this material covers and why it matters.>

## Key Themes Across All Files
- <Theme 1>: appears in <which files>; <1-2 sentence synthesis>
- <Theme 2>: appears in <which files>; <1-2 sentence synthesis>
- ...

## Per-File Highlights
- <file name 1>: <2-4 bullet highlights specific to this file>
- <file name 2>: <2-4 bullet highlights specific to this file>
- ... (short - this is not a second full summary per file)

## Decisions and Action Items from Meetings
<Include only if Teams recaps were analyzed and contained any.>
- <Decision or action item> - <owner if known> (<meeting title, date>)

## Gaps, Overlaps, or Contradictions
- <Note any topic covered by only one file, duplicated across files, or inconsistent between files>

## Suggested Learning Path
1. <Recommended first file/topic and why>
2. <Next step>
3. <...>

## Unsupported or Unreadable Files
- <file name> - <reason, e.g. "scanned PDF with no text layer", "unsupported extension">
- <meeting title> (Teams recap) - <reason, e.g. "no recap generated", "access denied">
```

Keep the "Per-File Highlights" section short - it exists so readers can trace themes back to a
source, not to recreate a full per-file summary. The "Executive Overview" and "Key Themes" sections
are what make this a single combined summary rather than a stitched-together collection of
individual ones.
