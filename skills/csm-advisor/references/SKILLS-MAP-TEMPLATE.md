# Stage 3 - Skills Map Template

Goal: list the training skills the customer needs (detected from the Stage 2 signals) and map every
skill to items from the bundled Microsoft Learn catalog (`ms-learn-catalog.json`), with the links
that come from the catalog. Produce exactly one Word (`.docx`) document, separate from the Signals
Summary and the Skilling Paths proposal.

The main heading must be exactly **"Skills Map"**. Put the customer/scenario name on a subtitle line
underneath, not in the main heading.

This document maps skills to catalog modules and learning paths only. Instructor-led classes and
courses are out of scope for this version.

## Rules

- **Links come from the catalog only.** Copy each title and URL exactly as `scripts/search_catalog.py`
  returned it. Never write, shorten, repair, or guess a link, and never list an item that the
  catalog did not return. Make each title a hyperlink to its catalog URL and also show the URL text,
  so the link survives printing and copy-paste.
- **Skills come from evidence.** Every skill traces to at least one signal in the Signals Summary
  (use its source or signal reference). Do not add skills that no signal supports.
- **Cover the whole list.** Search every skill. One catalog item may serve several skills or
  audiences; list it once in the catalog table and reference it from each skill.
- **Judge each match.** The script's `strength` label is a heuristic. Read the title, summary, level,
  and roles before accepting a match; reject look-alikes (a product with a similar name). Prefer a
  learning path when several of the skill's best matches are modules of the same path.
- **Coverage:** **Covered** (a strong, fitting match for the whole skill), **Partly covered** (fits
  part of the skill, or the right topic at the wrong level), **Not covered** (no fitting match - list
  the phrases you tried; never pad with weak matches).
- Do not stop to ask the user anything. Anything uncertain goes under Assumptions.

## Chat reply (separate from the document)

The detail goes ONLY into the Word document. In chat reply with 2-3 sentences (how many skills were
identified, how many mapped to catalog items, the selected path, and a link to the document), followed
by the `Debug - Stage 3` block from [DEBUG-LOG.md](DEBUG-LOG.md). Then continue to Stage 4:

> I identified 9 required skills for <customer> and mapped 8 of them to 11 Microsoft Learn catalog
> items; the selected path is Deepen. Full list: [Skills Map](<link to the .docx>).

## Document structure

```text
# Skills Map
<Customer / Scenario Name> (subtitle line)

Generated: <date>
Based on: <Signals Summary file name/date>
Catalog snapshot: <generated_at> (<modules> modules, <paths> learning paths) - links come from this catalog
Status: <Ready | Ready with gaps | No skills detected>

## Summary
<2-4 sentences: the required skills found, how many are covered, partly covered, or not covered,
and the main gap.>
- Required skills: <n> | Covered: <n> | Partly covered: <n> | Not covered: <n>
- Distinct catalog items used: <n> (<modules> modules, <paths> learning paths)

## Selected Path(s)
- Primary path: <Activate | Deepen | Protect | Convert and Extend | None>
- Supporting path(s): <...>
- Reason: <the confirmed signals behind each choice, by signal reference>
- Run: <sequentially | in parallel | by audience>
(If no path can be selected - customer outcome missing, or a non-skilling blocker - write
"No path selected" and the reason. The skills list below is still produced.)

## Required Skills and Catalog Mapping
| ID | Skill | Audiences | Evidence (signal / source) | Priority | Coverage | Catalog items (title, type, level, duration, link) |
|----|-------|-----------|----------------------------|----------|----------|----------------------------------------------------|
| S1 | <skill> | <Leaders / Champions / Advocates / End Users / ...> | <signal ref, source> | High / Medium / Low | Covered / Partly covered / Not covered | <title> - <path or module> - <level> - <minutes> - <catalog URL> |

For each skill also give, below the table or as a sub-row: what it means for this customer (one
line), current level -> target level (or "Unknown"), and the search phrases used.

## Skills by Audience
| Skill | Leaders | Champions | Advocates | End Users | Other audiences |
|-------|---------|-----------|-----------|-----------|-----------------|
| S1 <skill> | x | x | | x | |

## Catalog Items Used
| Title | Type | Level | Duration (min) | Roles | Link | Skills covered |
|-------|------|-------|----------------|-------|------|----------------|
| <title> | module / path | <level> | <minutes> | <roles> | <catalog URL> | S1, S4 |

(For a learning path, add the titles of its modules in a short list under the row.)

## Open Gaps
- <Skill> - phrases tried: <...> - closest items found (if any) and why they were rejected

## Assumptions
- <Inferred skill, level, or audience the signals did not state outright>

## Appendix - Debug Log
<Stage 3 step table per DEBUG-LOG.md: path-selection checks, catalog file check, one row per search
(exact command, filters, items considered / matched / strong), coverage decisions, totals, and the
document creation result.>
```
