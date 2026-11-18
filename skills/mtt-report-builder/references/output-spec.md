# mtt-report-builder — `info` Delivery Summary output contract

**Purpose:** the info report's data-model→placeholder map, fill rules, and planned enhancements.
**Loaded by:** `mtt-report-builder` on demand (see SKILL.md → Additional resources)

---

### Data model → template placeholders
Nearly everything comes from `mtt-esiadmin-lookup` (`mode:roster` + `includeOrgIndustry`); supply it and fill:

| Placeholder(s) | Source (resolver / sibling) |
|---|---|
| `DELIVERY_ID`, `COURSE_CODE`, `COURSE_TITLE`, `TYPE`, `MODALITY` | `delivery.*` |
| `PHASE` | `delivery.phase` (resolver-derived) → display label **Upcoming** (future) / **In progress** (present) / **Completed** (past) / **Canceled**. Read it directly — do NOT recompute from dates |
| `START`, `END` | `delivery.officialStart` / `officialEnd`, **`YYYY-MM-DD H:MM AM/PM`** (never `M/D/YYYY`) |
| `DURATION` | a **generic span** — **Single-day** when `delivery.dayCount` = 1, else **N days**. **Never a "Day M of N today" label** (wrong for a multi-delivery day; no day-math needed) — the past/present/future read is `PHASE` / `delivery.phase`. Fall back to the `officialStart`→`officialEnd` day span only if `dayCount` is null |
| `TIMEZONE` | work-order event timezone (`_esi_timezonenew_value` FormattedValue) |
| `LOCATION` | ILT address; `Virtual` for VILT/BLXP |
| `REG`, `CAP`, `CAP_LABEL`, `REG_PCT` | `roster.activeCount` / `delivery.capacity.value`; `CAP_LABEL` from `delivery.capacity.basis` (`delivery-max`→"Capacity"; `expected-headcount`→"Expected headcount"; `catalog-default`→"Catalog capacity"); `REG_PCT = min(100, REG/CAP*100)` |
| `REG_HEALTH` | `delivery.registrationHealth` (Green/Yellow/Red) — badge `b-green`/`b-yellow`/`b-red`; **omit the whole field when null** |
| Check-in bullet (checked-in / not-yet / no-show) | `roster.checkinCounts` (authoritative; never use WO mirrors as authoritative) |
| `LAB_CODE` | `delivery.studentLabCode` (else `Not assigned yet` — drop the Copy button) |
| `SURVEY_URL` | `delivery.surveyUrl` (always resolved by the resolver — use directly) |
| `TRAINER`, `CO_TRAINER` | resolver all-trainers + `esi_deliveryrole` |
| `CUSTOMER` | `delivery.customer.name` when present; fallback to `delivery.customer.tpid`; else `Customer not provided` — **always rendered** |
| `TPM_TPC` | `delivery.support.tpm` / `.tpc` — **one combined field on a single line**; compose "TPM <name>" and/or "TPC <name>" joined by " · "; **omit the whole field when both are null** |
| Summary bullets (Enrolment · Check-in · Top role families · Reach), ROLE FAMILIES / REGION / LANGUAGE bars, `LEARNER_COUNT` | `mode:roster` composition — family bars from `roster.roleFamilies.registered` (never individual `role` values) |
| INDUSTRY bars, ORGANISATION bars, `ORG_COUNT` | `roster.orgs` (`includeOrgIndustry`) |
| `TPM_INSTRUCTIONS` | `delivery.tpmInstruction` — **omit the whole Notes field when null**; and **omit the entire Notes card** when it holds no note fields at all (conditional, like TPM/TPC). The raw `msdyn_instructions` field is intentionally not rendered (stale free-text holdover) |
| `SOURCES` | footer data provenance — the resolver/esiadmin entities read (delivery, event registrations, roster) + any web/other sources, each dated |
| `GENERATED_AT` | the current **local** datetime (trainer's zone, from runtime context) — the report's generated time. Rendered **top-right of the summary header** as **"Generated: <datetime>"** **and** in the footer — fill both |

### Fill rules
1. Copy the template for the `reportType` — **info** → `references/delivery-info-template.html`; **adhoc / any other or novel type that matches no template** → `references/base-template.html` (fill `{{CONTENT}}` from the component classes). **There is no author-from-scratch path** — a report that fits no template still starts from `base-template.html`, so it inherits the theme, dark-mode, and footer. Substitute `{{PLACEHOLDER}}` scalars; **escape HTML** (`&`, `<`, `>`). On the ad-hoc path, gather inputs in cheap-first order: confirm the delivery exists and estimate scale before any heavy roster + industry pass.
2. **Summary card (top)** — **statistics bullets** (`<ul class="summary-list">`), not a paragraph: *Enrolment*,
   *Check-in*, *Top role families*, *Reach*. **Only cite a breakdown group whose learner count is `> 3`** — the 1–3
   tail stays out of the summary but remains in the charts below. Percentages are of the active-registered
   total. **Language rule:** if one language covers **≥90%** of learners, **omit language from the summary
   entirely**; surface language + the `esi_language` portal-tag caveat only when it's genuinely mixed (the
  LANGUAGE bar chart still renders). Draw the **Check-in** bullet with fixed precedence: roster first,
  fallback counts caveated as system-lagging; for an Upcoming (pre-start) class where nobody has checked in, state
  "not started."
3. **TPM / TPC / TPM Instructions / Registration Health / Customer fallback** — render the field **only if present**; **omit the
   whole field/note div** when null (never "— (none)"). **TPM / TPC render as ONE combined field on a single line** (`{{TPM_TPC}}`) — "TPM <name>" and/or "TPC <name>" joined by " · "; omit the whole field when both are null. **Notes card:** it no longer renders the raw
   `msdyn_instructions` field; render the whole Notes card **only when ≥1 note field has content** and **omit
   the entire card** when empty (it's TPM-Instructions-only today, but extensible). **Registration Health** is a badge colored by value
  (`b-green` / `b-yellow` / `b-red`). **Customer always renders** using `delivery.customer.name`, else `delivery.customer.tpid`, else `Customer not provided`. Account-enriched customer fields (`accountId`, `city`, `country`) are conditional and appear only when callers opted into `includeCustomerAccount`; never require them for rendering. **Capacity:** `CAP` = `delivery.capacity.value`
   and the field label = `CAP_LABEL` from `delivery.capacity.basis` — never label an expected-headcount or
   catalog value as a plain "Capacity".
4. **Learner Background categories** (ROLE FAMILIES, INDUSTRY, ORGANISATION, REGION, LANGUAGE) — each a bar chart, count
   desc. **ROLE FAMILIES** comes straight from `roster.roleFamilies.registered` (the canonical role→family
   rollup — see *Role families are the ROLE chart* below); render the family buckets, **never individual job
   roles** (a lone job title + employer can de-anonymise one learner — families are the PII-appropriate view). **Provenance is internal — do NOT narrate employer/role resolution methodology in the end-user report** (no "resolved via CRM link / email domain / job title" line, no before/after progression; the resolver's `employerSource` / `roleSource` tags are for QA, not the deliverable). The report shows the composition, not how it was derived. The **one** end-user-facing inference marker is on **INDUSTRY**: suffix any bar that includes an agentic (map-inferred) classification with a trailing ` *`, and render a single short caveat (`{{INDUSTRY_CAVEAT}}` — e.g. "* Includes an agentic classification for agencies without a CRM account record — not authoritative; confirm with your TPM.") **directly below the INDUSTRY chart**, never at the top. **AI disclosure — Microsoft-standard, footer-only:** the current Microsoft standard (the M365 Copilot AI disclaimer) is a single **subtle footer** line, *not* per-section tags — so do **not** add inline AI tags to sections. The only AI disclosure is the footer line (rule 7). The INDUSTRY `*` stays a plain data-inference caveat (`Inferred classification … not authoritative; confirm with your TPM`), independent of the AI disclaimer.
   **Top-4 + tail rule:** render the top 4 rows inline; if **more than 3** rows remain, wrap the rest in
   `<details class="moredetails">` ("Show N more <category>"); if **3 or fewer** remain, render them inline (no
   toggle). **INDUSTRY and ORGANISATION are two separate subsections** — INDUSTRY groups learners by employer
   `esi_industry` (where `industry` is null, classify agentically and **label** the bucket, e.g.
   "Other/unclassified"); ORGANISATION lists individual employers. **Both are resolved domain-first by the resolver** (email domain → account, else CRM link, else a domain-only label), so on a multi-account cohort the ORGANISATION chart is near-complete (few/no "unlinked") while INDUSTRY often stays partial (many smaller agencies have no account/industry record) — render the residual honestly (`Unclassified` bucket) and never invent an industry. **INDUSTRY / ORGANISATION visibility:** render
   each of these subsections **only when it has ≥3 distinct categories** (≥3 industries / ≥3 employers) — with
   fewer than 3 (e.g. a single-customer Private delivery, or a multi-account delivery sharing one industry),
   **omit that whole subsection** (the Customer field and the remaining categories already carry the signal).
   `{{ORG_COUNT}}` = number of distinct orgs. Add `cat-last` to the final rendered
   category's `.chart`.
5. **Bar charts** — `width% = value / (max in that chart) * 100`; block-level `.bar-fill`; `width:0%` for 0.
6. **Badges** — modality `b-vilt`/`b-ilt`; phase `b-phase` (or `b-canceled`). **Copy buttons** only for real values.
7. **Footer (always, every report type)** — end with the **Sources / Privacy / Generated** footer card, followed by a single subtle **AI disclaimer** line — the Microsoft-standard phrase *"AI-generated content may be inaccurate. Check for accuracy."* (Microsoft turned this footer off-by-default in its own chat UI in late 2025, with an opt-in bold 'Heightened Awareness' variant; keep it subtle and plain by default — upgrade to bold + a link to the org's AI policy only on request). **No inline per-section AI tags** — this one footer line is the whole disclosure. `SOURCES` = data provenance (resolver/esiadmin entities read + any web/other sources, each dated); the **Privacy** line is the fixed default (aggregate-only, no learner PII, lab code / internal fields for the trainer's use, do-not-distribute); `GENERATED_AT` = the current **local** datetime. Applies to ad-hoc reports too. Resolve `{{GLYPH_PRIVACY}}` (and any other `{{GLYPH_*}}`) via `references/glyphs.md` — inline the bundled monochrome shield by default; a report never fails for a missing glyph (omit).
8. **Theme self-check → save → validate → gate.** Before saving, confirm the `<style>` carries the FY27 `:root` tokens **and** the dark `@media :root` (both with `--head-grad`), the header reads `background:var(--head-grad)` (no `@media .head` override), headings use `--fh` (Segoe UI Semibold), and the Sources/Privacy/Generated footer is present — if any is missing it didn't start from the theme, so rebuild from `base-template.html`. Then save to `output/delivery-<id>-<type>.html`, validate (`status: success`, zero external refs), pass the delivery gate, return the handle.

### Enhancements & planned
- **Role families ARE the ROLE chart (`roster.roleFamilies.registered`):** the resolver returns a
  pre-bucketed family rollup (`{attended, registered}`) built from the **canonical** role→family map
  (`mtt-esiadmin-lookup` → *Role → family taxonomy*). The Delivery Summary's learner-background chart renders
  **role families over active-registered** (`roleFamilies.registered`, matching the active-registered
  denominator) — coarser than individual job roles and therefore **more PII-appropriate** (a single job
  title paired with the employer/org already shown can de-anonymise a lone learner; a family bucket does
  not). Apply the resolver's rollup **directly** — never re-implement the map or fall back to individual
  `role` values.
- **INDUSTRY** (its own subsection) and **ORGANISATION** are data-driven by **`esi_industry`** / employer
  (opt-in `includeOrgIndustry`); **each is hidden below 3 distinct categories** (≥3 industries / ≥3 employers).
  Both use the top-4 + collapse pattern (tail hidden only when >3 rows remain).
- **TPM/TPC** conditional; **Customer** always shown.
- **Planned (v2):** returning-learner line (`includeHistory`), Catalog block (`delivery.catalog`), fuller
  support/escalation block (support desk + SLAs).
