# Stage 2 - Signals Summary Template

Produce exactly one Word (`.docx`) document using this structure, regardless of how many sources
were analyzed. Omit a section only if it genuinely does not apply.

The main heading must be exactly **"Signals Summary"**. Put the customer/scenario name on a subtitle
line underneath, not in the main heading.

What to extract, the signal record fields, and the readiness and blocker rules are defined in
[SIGNAL-COLLECTION.md](SIGNAL-COLLECTION.md). Follow them; never invent values.

## Chat reply (separate from the document)

The detail goes ONLY into the Word document. In chat reply with 2-3 sentences (what was analyzed,
the single most important finding, and a link to the document) and the stage status. If debug
logging is on (the request asked for it), add the `Debug - Stage 1` and `Debug - Stage 2` blocks from
[DEBUG-LOG.md](DEBUG-LOG.md). Do not ask for approval or more information - continue straight to
Stage 3:

> I analyzed 5 files and 3 Teams meeting recaps for <customer>. The customer outcome is <outcome>;
> readiness is <Ready with conditions> and <N> items of information are still missing. Full details:
> [Signals Summary](<link to the .docx>). Status: <status>.

Stage 2 status (one of): **Ready for path selection**, **More customer information required**,
**Not ready for path selection** (customer outcome missing), **Non-skilling blocker identified**.
Whatever the status, state what is missing or what blocks, and continue to Stage 3.

## Document structure

```text
# Signals Summary
<Customer / Scenario Name> (subtitle line)

Generated: <date>
Sources analyzed: <count> (<formats present, e.g. "2 Word, 1 PDF, 3 PowerPoint, 1 Excel">)
Teams meeting recaps included: <count, or omit if none>
Status: <Stage 2 status>

## Sources
- <file name> (.docx) - <one-line description>
- <meeting title> (Teams recap, <date>) - <one-line description>
- ... one line per analyzed file, recap, or provided link

## Executive Overview
<3-6 sentences across ALL sources: the customer outcome, what the signals say, the readiness, and
what is missing.>

## 1. Customer Outcome
- Stated business priority / desired outcome:
- Priority workflows or scenarios:
- Business deadline:
- Success measure / metric owner / evidence location:
- Named customer sponsor / skilling champion:
(Mark "Not provided" for anything missing. If the outcome is missing: **Not ready for path selection**.)

## 2. Signal Inventory
| ID | Signal | Value or finding | Source | Source date | Confidence | Validation required |
|----|--------|------------------|--------|-------------|------------|---------------------|
| Sig-1 | <signal> | <value> | <source> | <date or n/a> | Confirmed / Probable / Unconfirmed | Yes / No |

Give every signal a unique id (Sig-1, Sig-2, ...). The Skills Map and the Skilling Paths proposal cite
signals by these ids.

### Adoption and usage
- Licenses purchased / assigned / activated; active and inactive users:
- Adoption percentage (only with a reliable denominator, else "not calculated"):
- Applications and features used; frequency and depth; repeat workflows; priority workflows not yet
  supported:
- Baseline, baseline date, data source, metric definition:
- Usage pattern: <No/very low activation | Initial or occasional | Active but shallow | Repeatable
  workflow usage | Advanced / agents>

## 3. Audiences and Capability Gaps
For each audience group found in the sources:
- <Audience> - role/persona; population; current skill level; required capabilities; priority
  applications and workflows; delivery format; availability; cloud/environment; accessibility,
  location, language; customer-owned reinforcement

## 4. Sponsorship and Readiness
- Checklist: sponsor named; champion named; outcome agreed; audiences can participate; time for
  practice; licensing and access; feature/cloud availability; security and compliance understood;
  labs/demos/recordings/data usable; Microsoft and customer capacity - each Yes / No / Unknown
- Readiness: <Ready | Ready with conditions | Not ready | Unknown>
- Conditions to resolve before delivery is committed: <list>

## 5. Cause Confirmation and Non-Skilling Blockers
- Primary cause: <skills/awareness, scenarios, sponsorship/reinforcement, licensing/access, technical
  configuration, security/compliance, feature/cloud availability, procurement, customer capacity,
  Microsoft capacity, other>
- Is skilling the primary intervention? <Yes / No / Partly>
- If No or Partly: blocker, accountable team to route to, and what must change before skilling is
  reconsidered

## 6. Missing Information
- <Item to request> - from whom (CSM / customer / account team)

## 7. Contradictions and Gaps
- <Conflicting values or dates between sources; topics covered by only one source; duplicates>

## 8. Decisions and Action Items
- <Decision or action item> - <owner if known> (<source, date>)

## Per-Source Highlights
- <source name>: <2-4 bullets specific to that source> (short - not a second full summary)

## Unsupported or Unreadable Sources
- <file name> - <reason, e.g. "scanned PDF with no text layer", "unsupported extension">
- <meeting title> (Teams recap) - <reason, e.g. "no recap generated", "access denied">
- Input types not supplied (from the list in SIGNAL-COLLECTION.md)

## Appendix - Debug Log
<Include ONLY when debug logging is on; otherwise omit this whole section. Stage 1 - Collection log
and Stage 2 - Signal detection log, as step tables per DEBUG-LOG.md:
every source with its read result, the Teams recap scope and result, the outcome of Steps 1-5,
counts by category and confidence, and the document creation result.>
```

Keep "Per-Source Highlights" short - it exists so readers can trace signals to a source. The
"Executive Overview" and "Signal Inventory" are what make this one combined document rather than a
collection of per-file summaries. Treat the document as a proposal input, not a validated finding.
