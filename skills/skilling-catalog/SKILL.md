---
name: skilling-catalog
description: |
  Read-only Microsoft Technical Trainer (MTT) catalog lookup, scoped to **MOC Courseware** catalog
  items only, from the esiadmin Dynamics 365 environment: course code and title, MTT indicator, PD
  eligibility, official duration, delivery types and capacity by modality, audience/prerequisites,
  solution area, and retirement status. Backed by the "Active Catalog Items" view
  (`msdyn_incidenttype`), with a public static backup portal
  (https://true-while.github.io/tpm-cheat-sheets/) for when esiadmin is unreachable.
  Use when an MTT or CSM asks: "look up catalog item <code>", "is <course> PD eligible", "is <course>
  MTT-delivered / CAIP supported", "what's the official duration / VILT capacity for <course>", "find
  active MOC Courseware items about <topic/product>", "what delivery types does <course> support",
  "is <course> retired", "what's the audience / prerequisites for <course>".
  Do NOT use for: a specific scheduled class/delivery/roster/attendance (use mtt-class-lookup),
  self-paced Microsoft Learn modules/learning paths (use the Learn catalog search service instead —
  this is the instructor-led ESI/MTT catalog, a different catalog), rendering an HTML report (use
  mtt-report-builder), or a full evidence-led customer skilling journey design with routes, packages,
  and budgets (use signal-led-customer-skilling — this skill only enriches its catalog-discovery
  step; its MTT indicator is never proof of PD = Yes).
metadata:
  version: "0.1.0"
  category: productivity
  icon: BookSearch
---

# Skilling Catalog Lookup (MTT/CAIP course catalog)

Answers "what is this course / which courses match" by reading **catalog items** (course types, not
scheduled deliveries) from the **esiadmin** Dynamics 365 (Dataverse) environment, table
`msdyn_incidenttype` (entity set `msdyn_incidenttypes`). **Read-only to Dynamics** — it never
creates, updates, or deletes records, and it never books, registers, or sends anything.

**Scope is MOC Courseware only.** This skill's default scope is catalog items whose
`esi_catalogitemtype` is **MOC Courseware** — the instructor-led Microsoft Official Courseware
format MTTs deliver. Other catalog item types (e.g. Applied Skills, exams, certifications) are out
of scope by default; see `references/procedure.md` for the opt-in to widen it.

A catalog item is the **course type** ("AI-3016 · Introduction to..."), not a specific class. For a
scheduled delivery, its roster, or its join link, use **mtt-class-lookup** instead.

## When to Use

- "Look up catalog item `<code>`" / "what's the official title / duration for `<code>`?"
- "Is `<code>` PD eligible?" / "is `<code>` MTT-delivered / CAIP supported?" (MTT indicator)
- "What delivery types does `<code>` support?" (VILT / BILT / HILT / BLXP) / "what's its VILT capacity?"
- "Find active MOC Courseware items about `<topic/product>`" (e.g. "Copilot Studio", "Azure AI")
- "What's the audience / prerequisites for `<code>`?" / "what solution area is `<code>` in?"
- "Is `<code>` retired?" / "list active catalog items for `<role>` / `<solution area>`"
- "esiadmin is down, check the backup portal for `<code>`" (or ask first, when a read fails)

## When NOT to Use

| If the ask is… | Use instead |
|---|---|
| A specific scheduled class/delivery: roster, attendance, Teams join link, lab code | **mtt-class-lookup** |
| Self-paced Microsoft Learn modules/learning paths (the public online catalog, not instructor-led) | the Learn catalog search service — a different catalog entirely |
| Render structured data as an HTML report | **mtt-report-builder** |
| Identity / delivery / roster / schedule resolution for another skill's own implementation | **mtt-esiadmin-lookup** (internal library callee, not user-facing) |
| A full evidence-led customer skilling journey: routes, rings, packages, delivery feasibility, PDc budgets | **signal-led-customer-skilling** — pass it this skill's card as discovery enrichment only; it must still independently validate PD = Yes before gating a decision |
| Sales accounts / opportunities / pipeline | the **dynamics-365-sales** plugin |

## Before you start

**You'll need:** read access to the **esiadmin** Dynamics 365 environment (the Dataverse tools must
be available in your session). No identity resolution is needed — catalog items are not
trainer-scoped or session-scoped, so this skill never calls `mtt-esiadmin-lookup`.

**Plain-language glossary:**
- **Catalog item** — one row in `msdyn_incidenttype`: a course *type* (e.g. `AI-3016`), not a
  scheduled class. The anchor for every lookup here.
- **MOC Courseware** (`esi_catalogitemtype`) — this skill's default scope. Microsoft Official
  Courseware, the instructor-led format MTTs deliver; other catalog item types (Applied Skills,
  exams, certifications) are excluded by default.
- **MTT indicator** (`esi_isattindicator`) — flags a catalog item as MTT/CAIP-delivered. It is the
  filter the "Active Catalog Items" view uses — **it is not proof of PD eligibility.**
- **PD eligible** (`esi_pdceligible`) — the actual professional-development/credit eligibility flag.
  Always report this separately from the MTT indicator; never imply one from the other.
- **Official duration** (`esi_standardduration` / `msdyn_estimatedduration`, in minutes) — convert to
  a readable length (e.g. "1 hr", "3 days"). **Never convert it into PDc** — that is a separate
  planning estimate owned by the calling workflow, not this skill.
- **Capacity by modality** — `esi_viltmaximumcapacity` / `esi_biltmaximumcapacity` /
  `esi_hiltmaximumcapacity` / `esi_blxpmaximumcapacity` (VILT/BILT/HILT/BLXP seat maximums).
- **Retired** — `esi_retirementdate` set, or `statecode`/`statuscode` off Active. Report plainly;
  never silently drop a retired item the user explicitly asked about.
- **Backup portal** — the public static site
  [tpm-cheat-sheets](https://true-while.github.io/tpm-cheat-sheets/), used only when esiadmin cannot
  be reached. It is a community-maintained reference, not the system of record — label its results
  as such and never blend them silently with an esiadmin result.

## Quick start

```
User: "Is AI-3016 PD eligible, and what's its official duration?"
1. read_query msdyn_incidenttypes, filter msdyn_name eq "AI-3016" (top 1)
2. Render the catalog-item card: MTT indicator, PD eligible (+ credit value), duration, capacity
   by modality, delivery types supported, audience/prerequisites, solution area, retirement status
3. State the caveat inline: the MTT indicator is not proof of PD = Yes; PD eligibility is
   `esi_pdceligible` alone.
```

## Access & environment (esiadmin)

- Dataverse tools with `orgName: "esiadmin"`, **read-only** here: `read_query` only — never `fetch`,
  `create_record`, `update_record`, or `search` (Relevance Search is OFF; always use structured
  `read_query` filters).
- Table: `read_query` target `msdyn_incidenttypes` (entity set; the logical name / view `etn` is the
  singular `msdyn_incidenttype`).
- **Default scope is Active Catalog Items AND MOC Courseware**: `statecode eq 0`, the Active
  `statuscode`, `esi_isattindicator eq true`, and `esi_catalogitemtype` = **MOC Courseware**. The raw
  option-set value for MOC Courseware isn't independently confirmed, so filter client-side on its
  `@…FormattedValue` unless that value has already been confirmed in this environment (see
  `references/procedure.md` → *Catalog item type*).
- **Metadata is blocked** (`list_tables`/`describe_table` → 400) → rely on the fields in
  `references/data-model.md`; if a filter is refused, confirm the exact `statuscode` Active value and
  column names with `DESCRIBE msdyn_incidenttype` on the target.
- **Lookup `_value` filters require `valueType:"string"`** (a `guid` valueType → HTTP 400).
- Selecting a lookup's denormalized `…name` string field or a picklist/boolean virtual `…name` field
  (e.g. `esi_catalogitemtypename`, `esi_isattindicatorname`) → HTTP 400. Select the **base** field
  instead (`esi_catalogitemtype`, `esi_isattindicator`) — its label comes back in `@…FormattedValue`.
- `read_query` caps at roughly 50 rows with no next-page token — narrow the filter rather than
  assuming a short result list is complete; disclose truncation when the cap is hit.

## Backup portal (when esiadmin is unreachable)

[tpm-cheat-sheets](https://true-while.github.io/tpm-cheat-sheets/) is a public, static, read-only
site that also carries current catalog information (per-technology one-day/ARB course tables, plus
retired-class tables), maintained outside Dynamics. Use it **only as a fallback** — when an esiadmin
`read_query` is denied, errors, or the Dynamics 365 Plugin is unavailable — or when the user
explicitly asks for it. It is never the primary source and never silently blended with an esiadmin
result. Full fetch workflow, its code index, and the retired/ARB URL convention are in
`references/backup-portal.md` — **load it before falling back to the portal.**

## Search modes

Full filter recipes, the default "Active Catalog Items" + MOC Courseware parity filter, row-cap
handling, and the single-item-vs-list rendering decision are in `references/procedure.md` — **load
it before running any search.**

- **By exact code** — `msdyn_name eq "<code>"`, the fastest and most common path.
- **By keyword/title** — `contains(esi_title,'<keyword>')` or `contains(msdyn_description,'<keyword>')`,
  scoped to active, MOC Courseware, MTT-indicator items by default.
- **By PD eligibility** — `esi_pdceligible eq true`.
- **By delivery type / solution area** — best-effort filters on the raw picklist/lookup fields; see
  `references/procedure.md` for the exact syntax and its caveats.
- **Including retired items** — opt-in only (`includeRetired`); default scope is active items.
- **Including other catalog item types** — opt-in only (`includeAllItemTypes`); default scope is MOC
  Courseware only.

## Output

A **single matched item renders as one catalog-item card**; **several matches render as a compact
table** (code, title, MTT indicator, PD eligible, status, duration, solution area) with an invitation
to name a code for the full card. Every card/row states its **source** — `esiadmin (Dynamics 365)` or
`backup portal (tpm-cheat-sheets)` — and the backup portal's result additionally carries a caveat
that it is a static, community-maintained reference, not the system of record. Field definitions,
the worked example, and the exact caveat wording are in `references/output-spec.md`.

## Guardrails

- **Read-only, silent on write.** Only `read_query` in esiadmin (or a plain GET fetch of the backup
  portal); never create, update, delete, book, register, or send anything, on either source.
- **Ground every value in a tool result.** Never fabricate a catalog code, title, duration, capacity,
  eligibility flag, or link. A field with no returned value is omitted, not guessed.
- **MTT indicator is never PD eligibility proof.** Whenever both are shown (which is the default),
  state them as two separate flags, and never claim one implies the other.
- **Never convert duration into PDc.** Report official duration as a readable length only; PDc
  estimation belongs to the calling workflow (e.g. `signal-led-customer-skilling`), not this skill.
- **No identity dependency.** Catalog items are global, not trainer-scoped — never ask who the user
  is, and never call `mtt-esiadmin-lookup` for identity on this skill's behalf.
- **MOC Courseware is the default scope.** Only widen to other catalog item types on an explicit
  opt-in; state the narrower default scope when a search returns nothing under it.
- **Retired items stay visible on request.** Flag retirement plainly rather than silently excluding
  an item the user explicitly asked about by code.
- **Disclose the row cap.** If a keyword/broad search hits the ~50-row cap, say so and suggest a
  narrower filter rather than presenting the list as exhaustive.
- **esiadmin is primary; the backup portal is secondary and must be labeled.** Only fall back to the
  portal after an esiadmin read fails, is denied, or on an explicit user request — never query it
  first, and never present its data as if it came from Dynamics.
- **On a failed or denied esiadmin read,** state plainly: "Could not reach the esiadmin Dynamics 365
  environment for catalog data. Verify the Dynamics 365 Plugin is enabled in Cowork Customisations,
  then retry." — then offer the backup portal as a secondary option. Never retry with an alternate
  identity or escalate permissions.
- **This skill is discovery-only for eligibility gating.** A consuming skill that needs an
  authoritative PD = Yes gate (not just a quick lookup) must independently validate the catalog
  fields itself rather than relying solely on this card — and never treat a backup-portal result as
  PD = Yes evidence at all, since the portal carries no PD/eligibility field.

## Additional resources

Load on demand for detail:
- `references/data-model.md` — the `msdyn_incidenttype` fields this skill reads, the "Active Catalog
  Items" + MOC Courseware filter parity, and the Dataverse-MCP query gotchas that apply to this table.
- `references/procedure.md` — the full search-mode recipes (by code, keyword, PD eligibility,
  delivery type, catalog item type, solution area, audience/role, retired toggle), row-cap handling,
  and the single-item-vs-list rendering decision.
- `references/output-spec.md` — the catalog-item card fields, the multi-result table format, a
  worked example of each, and the exact MTT-indicator/PD-eligible caveat wording.
- `references/backup-portal.md` — the tpm-cheat-sheets fallback: its code index, per-technology
  table pages, the retired/ARB URL convention, and when (and how) to use it instead of esiadmin.
