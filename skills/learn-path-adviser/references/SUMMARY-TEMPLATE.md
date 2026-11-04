# Combined Summary Output Template

Produce exactly one summary using this structure, regardless of how many files were analyzed.
Omit a section only if it genuinely does not apply (e.g. no unreadable files).

```text
# <Scenario/Batch Name> - Combined Analysis

Generated: <date>
Files analyzed: <count> (<formats present, e.g. "2 Word, 1 PDF, 3 PowerPoint, 1 Excel">)

## Sources
- <file name 1> (.docx) - <one-line description>
- <file name 2> (.pdf) - <one-line description>
- ... one line per analyzed file

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

## Gaps, Overlaps, or Contradictions
- <Note any topic covered by only one file, duplicated across files, or inconsistent between files>

## Suggested Learning Path
1. <Recommended first file/topic and why>
2. <Next step>
3. <...>

## Unsupported or Unreadable Files
- <file name> - <reason, e.g. "scanned PDF with no text layer", "unsupported extension">
```

Keep the "Per-File Highlights" section short - it exists so readers can trace themes back to a
source, not to recreate a full per-file summary. The "Executive Overview" and "Key Themes" sections
are what make this a single combined summary rather than a stitched-together collection of
individual ones.
