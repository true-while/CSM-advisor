# Supported Formats and Extraction Guidance

This skill only reads existing files; it never writes back to them. For each supported format,
extract the content below before moving to consolidation.

## Word (`.docx`)

- All paragraph text, in document order.
- Heading text, tagged with its heading level (Heading 1/2/3...) so the summary can reflect
  document structure.
- Table cell text, read row by row.
- Ignore headers/footers and tracked-changes metadata unless the user asks about revision history.

## PDF (`.pdf`)

- Extract the text layer in reading order (page by page).
- If a page (or the whole document) has no extractable text layer - i.e. it is a scanned image -
  do not guess its contents. Note that page/file as unreadable (no OCR is performed by this skill).
- Preserve page numbers when citing where a point came from, if the user asks for sourcing.

## Plain text (`.txt`)

- Read the raw file content. Detect encoding (UTF-8 by default; fall back to the platform default
  if decoding fails) rather than assuming a single fixed encoding.
- Treat blank-line-separated blocks as informal paragraphs/sections.

## PowerPoint (`.pptx`)

- Slide title and body text frames, per slide, in slide order.
- Speaker notes for each slide, kept separate from the on-slide text but still part of that file's
  content.
- Table and chart title/axis text when present; raw chart data points are optional and only needed
  if the user asks about specific numbers.

## Excel (`.xlsx` / `.xls`)

- Sheet names, and for each sheet, header row(s) plus cell values.
- Treat each sheet as a labeled section of that file rather than flattening all sheets together.
- For very large sheets, summarize structure (column headers, row count, value ranges) rather than
  enumerating every cell.
- Note formulas only by their resulting value unless the user explicitly asks about formulas.

## Unsupported inputs

Any other extension (e.g. `.csv` is allowed if the user includes it as supplementary data, but
`.zip`, `.png`, `.mp4`, etc. are not analyzed). List unsupported files separately in the final
summary rather than silently ignoring them.
