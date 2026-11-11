# Debug Logging (all stages)

Every step of every stage is logged so a CSM or MTT can see what the agent read, did, decided, and
skipped. Log facts only - never guess - and keep going after warnings or errors.

## Where the log goes

1. **Chat:** after each stage, add a compact `Debug - Stage N` block (at most ~8 lines) under that
   stage's short message.
2. **Word documents:** the Signals Summary, Skills Map, and Skilling Paths proposal each end with an
   **"Appendix - Debug Log"** section holding the full step table for that stage. Stage 1 has no
   document of its own, so its full log goes into the Signals Summary appendix under "Stage 1 -
   Collection log".

## What never goes in a log

- Secrets, tokens, or credentials.
- Raw customer text, quotes, or personal data. Log names, counts, labels, and ids only.

## Step table format (documents)

| Step | Action | Input | Result | Status | Note |
|------|--------|-------|--------|--------|------|
| 1.1 | <what was done> | <what it used> | <count or outcome> | OK / WARN / ERROR / SKIPPED | <reason, fallback, or retry> |

Status meanings: **OK** done as intended; **WARN** done with a gap or fallback; **ERROR** failed and a
fallback was used or the item was skipped; **SKIPPED** deliberately not done (say why).

## What to log per stage

**Stage 1 - Collect artifacts**
- Each source: name, type, how much was extracted (pages, slides, sheets, messages), and status
  (read, partial, unreadable) with the reason.
- Teams recaps: whether a Teams tool was available, the time range used (and whether it was the
  default), meetings found, with and without a recap, and any access errors.
- Input types from the SIGNAL-COLLECTION.md list that were not supplied.

**Stage 2 - Detect signals**
- Result of each of Steps 1-5: customer outcome found or not; which adoption fields were found or
  missing; audiences found; readiness classification and checks answered Yes / No / Unknown; main
  cause and whether skilling is the primary intervention.
- Counts: signals by category and by confidence (Confirmed / Probable / Unconfirmed); missing
  information items; contradictions.
- The Stage 2 status, and the document file name and save location, including any retry.

**Stage 3 - Path selection and skills map**
- Path selection: for each of Activate, Deepen, Protect, Convert and Extend - matched or not, with
  the signal ids behind the match - and the final decision (or "no path selected" and why).
- The catalog: file present, `generated_at`, and counts. If the catalog or script failed: the error
  and the fallback used.
- Every required skill: id, name, the search phrase(s), the exact `search_catalog.py` command or the
  live search used, filters, and from the script's own `debug` object - items considered, items
  matched, strong matches. Then the chosen catalog items and the coverage result (Covered / Partly
  covered / Not covered).
- Totals: skills derived, skills covered, partly covered, not covered, distinct catalog items used.
- The document file name and save location, including any retry.

**Stage 4 - Skilling plan**
- Inputs used (Signals Summary and Skills Map file names).
- Audiences built, items used per audience, measurement fields that are missing, and any validation
  items raised.
- The final status, and the document file name and save location, including any retry.

## Chat block format

```text
Debug - Stage 3
- Input: Signals Summary (14 signals); catalog snapshot 2026-11-11 (3458 modules, 834 paths)
- Path: Deepen (primary), Protect (supporting) - rules matched on S-04, S-07, S-11
- Skills: 9 derived; 6 covered, 2 partly, 1 not covered; 11 distinct catalog items
- Search: 9 script calls, 0 errors; no live-search fallback
- Warnings: skill S9 "<name>" had no strong match
- Output: Skills Map - <customer> - <date>.docx
```

Keep the block short; the full table lives in the document appendix.
