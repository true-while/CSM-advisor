# Selecting Microsoft Learn Resources (Stage 3)

Goal: after the path(s) are chosen (see [PATH-SELECTION.md](PATH-SELECTION.md)), find the Microsoft
Learn content that the required training skills detected in Stage 1-2 call for, and have the user
approve it before the skilling plan is written. This stage produces a chat checkpoint, not a
document.

## Source order

1. **Bundled Learn catalog (default).** `ms-learn-catalog.json` in the skill folder is a snapshot of
   the public Microsoft Learn catalog (modules, learning paths, instructor-led courses), refreshed
   at every plugin release. Search it only with `scripts/search_catalog.py`; do not open the JSON
   file directly - it is several MB. It records `generated_at`: state that date when presenting results.
2. **Live Microsoft Learn search**, only if the catalog file is missing, the script cannot run, or a
   skill has no match. Use whatever Learn, documentation, or web-search tool Cowork provides.
3. **Ask the user** for modules or links if neither works. Never fall back to guessing.

## Rules

- **Never invent** module titles, learning paths, links, course codes, availability, or durations.
  Use only values returned by the catalog script or a live Learn search. Leave level and duration
  blank if they are not shown.
- **Verify fit:** each pick's title, summary, level, and roles must match the skill need and the
  intended audience. Catalog filters are loose, so reject unrelated matches (for example a product
  with a similar name) instead of padding the list.
- Prefer a short, well-matched list over an exhaustive one. Each module must trace to a confirmed
  signal and to a selected path. Prefer learning paths for broad needs and single modules for narrow
  ones.
- Skip content the signals show an audience already completed.
- The catalog is a snapshot; links can change. Tell the user the snapshot date and that the
  shortlist should be spot-checked before it goes to the customer.
- Do not promise instructor-led course availability, dates, delivery capacity, or cloud support. A
  course shown in the catalog (code, title, hours) means the course exists on Microsoft Learn, not
  that it can be delivered; list it as "requires MTT validation".

## How to analyze the skill set

1. **List the required training skills.** From the approved Stage 2 Signals Summary, extract each
   skill gap, capability need, priority workflow, and selected-path focus, grouped by audience.
   Phrase each as a short search phrase (for example "copilot readiness rollout", "build agents in
   copilot studio", "prompt engineering for business users"). Check which products, roles, and levels
   are available with `python scripts/search_catalog.py --facets`.
2. **Search every skill**, in one call where possible:

   ```text
   python scripts/search_catalog.py "<skill 1>" "<skill 2>" --level beginner --level intermediate --limit 5
   ```

   Useful filters: `--product <id>`, `--role <id>`, `--level <id>`, `--type module|path|course`.
   Use the product, role, and level ids shown by `--facets`; omit a filter if it removes good matches.
   The result lists, for each match, its link, level, duration, the related learning paths and
   modules, and any instructor-led course the catalog links to it.
3. **Go over the whole skill set**, not one skill at a time:
   - Choose the best match for each skill, and prefer a learning path when several of the skills map
     to the modules of the same path.
   - Merge duplicates: one module that serves several skills or audiences appears once.
   - Match level to the audience's current skill level from the Signals Summary.
   - Record coverage: which skills are fully covered, partly covered, or not covered.
4. Capture title, link, level, duration, the signal it addresses, and why it fits. Note any skill with
   no good match as an **open gap** instead of padding the list.

## Shortlist format (chat)

| # | Module / learning path | Link | Level | Duration | Skill / signal addressed | Related instructor-led course | Intended audiences |
|---|------------------------|------|-------|----------|--------------------------|-------------------------------|--------------------|
| 1 | <title> | <Learn URL> | <level or blank> | <minutes or blank> | <skill; signal; path> | <code and title, or "none in catalog"> | <Leaders / Champions / Advocates / End Users / ...> |

Then add:

- **Skill coverage summary:** each required skill with Covered / Partly covered / Not covered and the
  module(s) that cover it.
- **Catalog snapshot date** (`generated_at`) and a reminder to spot-check links.
- **Open gaps:** skills with no matching Learn content.
- **Assumed prerequisite skills per audience** (at least Leaders, Champions, Advocates, End Users),
  inferred from the signals - state them as assumptions so the user can correct them.
- **Instructor-led or other non-Learn items** that would need MTT validation.

Finish with one question: approve the path(s) and list, or what to add, remove, or replace.
Re-present after each edit. Only move to Stage 4 after approval.
