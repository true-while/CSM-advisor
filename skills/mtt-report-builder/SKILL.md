---
name: mtt-report-builder
description: |
  INTERNAL render library for the MTT bundle. Converts structured delivery data into a
  self-contained HTML report and returns a file handle. Usually called by sibling mtt-* skills;
  direct requests are secondary. Outputs HTML only and never posts, emails, or writes to Dynamics.
  Primary report type is Delivery Summary.
  Use only for explicit HTML report asks such as: "make an HTML report for delivery <id>",
  "build the delivery summary", "pre-delivery report for my class", or "render class info as HTML"
  (legacy "dashboard" accepted).
  Do NOT use for data retrieval (use mtt-class-lookup or mtt-esiadmin-lookup), student recap posts
  (use mtt-class-recap), post-delivery feedback (use mtt-delivery-debrief *(if available)*), run-of-show pacing
  (use mtt-class-timeline), trainer schedule checks (use mtt-time-intel), or non-HTML docs
  (use docx/pdf/pptx).
metadata:
  version: "0.2.14"
  category: productivity
  icon: ChartMultiple
---

# MTT Report Builder (HTML render layer)

Given **structured delivery data + a report type**, render a **self-contained HTML report** and return
it. Posture mirrors `mtt-esiadmin-lookup`: **a callee, not a destination.** The difference: the resolver
is a bottom-layer read service, whereas this is a **render layer** that can also *call* sibling skills to
gather data on the ad-hoc path.

## Intent — library-first
- **Primary:** a sibling MTT skill has already gathered the data and calls this skill to render it.
- **Secondary (extension):** a trainer asks directly for an HTML report; if data is missing, this skill
  gathers it via the other MTT skills, then renders.
- **HTML only for the report file.** The report artifact is HTML; this skill never writes a prose *text
  version* of it. The **one** in-line accompaniment it drives is the standard **delivery + audience card**
  plus a one-line file pointer (see *Presenting the report in chat*) — never a bespoke prose recap.
- **No follow-on actions.** It writes the report and hands it back. Any onward sharing belongs to the calling
  skill (or the user) and — because the Delivery Summary is **internal, trainer-facing** — stays internal (the
  trainer's own Teams self-chat, a colleague/TPM, print to PDF), **never the class (student) meeting chat**;
  **no MTT skill writes to Dynamics — the bundle is read-only there.**

## When NOT to Use

| If the ask is… | Use instead |
|---|---|
| Look up delivery / roster / attendance / class data | **mtt-class-lookup** / **mtt-esiadmin-lookup** |
| A student-facing **text** link recap | **mtt-class-recap** |
| Post-delivery feedback (paste-ready) | **mtt-delivery-debrief** *(if available; otherwise state that feedback drafting is unavailable in this package and retain the report data)* |
| Query, summarize, or analyze existing post-delivery feedback records by date/account/course/country/custom format | **the external Skilling Insights skill** *(if available; otherwise state that existing-record analysis is unavailable and do not emulate it)* |
| Run-of-show / pacing / demo guide | **mtt-class-timeline** |
| Trainer schedule, open-day, or duplicate-booking checks | **mtt-time-intel** |
| A Word document | use **docx** |
| A PDF or PowerPoint document | use **pdf** / **pptx** |

## Two modes

- **Delegated (primary).** Caller invokes with `{ reportType, data, meta }`. **Render only — do not
  re-fetch.** The caller is the data source.
- **Ad-hoc (extension).** Direct user request. If the data isn't in hand, **gather it via the MTT data
  skills** — but **fail fast, spend last**: first resolve the delivery on the cheap (`mode:delivery`, and
  `includeCheckin` when counts matter) to confirm the class exists and the request can succeed before any
  roster fan-out. Only then, for a delivery report, request `mtt-esiadmin-lookup` `mode:roster` (a superset
  that returns the `delivery` anchor *and* the registered roster; **leave `includeNames` off** — the
  Delivery Summary is aggregate-only, so names must never be fetched). If the enrolled count is materially
  above the modeled class size (roughly >30 learners), warn before the heavier roster + industry pass and
  offer a lighter first answer or explicit confirmation to continue.
- **Loop-safe:** data-gathering fires **only** in ad-hoc mode. When a sibling calls this skill, that
  sibling already provides the data, so this skill never re-enters it.

## Interface (the contract)

**Input:**
- `reportType` — a catalog key (below), or `adhoc`.
- `data` — the structured payload to render (per-type shape below).
- `meta` — header context: course · ClassID · customer · date · trainer.
- `style` — optional; defaults to the house style.
- `spec` — ad-hoc only; a loose section/layout description.

**Output:**
- Writes `output/delivery-<id>-<reportType>.html` (or `output/<slug>.html` for ad-hoc).
- Returns a handle: `{ path, reportType, title, summary }` for the caller's follow-on.
- **Delivery gate:** confirm the file exists in `output/` before telling anyone it's ready.

### Presenting the report in chat (in-line accompaniment)

When the finished report is surfaced to the trainer — the **ad-hoc path**, or a caller relaying the
handle — the chat accompaniment is the **pre-canned delivery + audience card**, **not** a bespoke prose
recap of the report body:

1. Render the shared **delivery + audience `render_ui` card** — the mirrored local fragment in
  `references/delivery-audience-card.md` (canonical source: `mtt-class-lookup/references/delivery-audience-card.md`)
  — from the already-resolved `delivery` + `roster`: delivery panel
   + attendance KPIs + **role-family** bar chart (`roster.roleFamilies.registered`). Invoke the
   **render-ui** skill first, then **one** `render_ui` call.
2. Follow the card with a **single-line pointer** to the saved file (e.g. "Saved
   `delivery-<id>-info.html` — open in any browser, or print to PDF"). The Delivery Summary is an
   **internal, trainer-facing** artifact (it carries trainer-internal fields — lab code, TPM instructions,
   registration health — and is **not** a student deliverable). Any next step you offer must stay internal:
   share it to the trainer's **own** Teams self-chat, send it to a **colleague/TPM**, print to PDF, or move on
   to a recap / live check-in. **Never offer — or agree — to post or send it to the class (student) meeting
   chat.** A student-facing post is the `mtt-class-recap` / `mtt-teams-message` job, not this report. Keep next steps to **≤3 and phase-aware** (read `delivery.phase`): **Upcoming** → roster / post the day plan (`mtt-teams-message`); **In progress** → live check-in / lab-access post; **Completed** → class recap (`mtt-class-recap`) / delivery-debrief feedback (`mtt-delivery-debrief`) — the report file itself always shared internally only.
3. **Do NOT** re-derive the report's contents as chat prose (role / industry / org bullet lists) — the
   HTML file and the card already carry them; a hand-written recap duplicates them and drifts from the
   standard. The card is the family-level view; the HTML Delivery Summary carries the same role-family chart
   **plus** the finer INDUSTRY / ORGANISATION / REGION detail and the copyable links.

## HTML foundation (house style — shared by every report type)

The shared foundation is the **FY27 Learning Lab skin** — warm `#FFF8F3` base, deep navy `#091F2E` ink,
accents **purple `#8661C5`** / **teal `#389A91`** / **blue `#0078D4`**, **Segoe UI Semibold** headings, a soft
warm-gradient header band, and a system **dark-mode** (navy) override. It lives as `:root` CSS variables +
**logical properties** (RTL/i18n-safe) + reusable component classes: `.card`, `.head`, `.badge`
(`.b-vilt`/`.b-ilt` on info; `.b-accent`/`.b-teal`/`.b-blue`/`.b-good`/`.b-warn`/`.b-bad`/`.b-neutral` on base),
`.kpis`/`.kpi` (KPI strip), `.grid`/`.field`, `.chart`/`.bar-row`/`.bar-fill` (pure-CSS bar charts),
`.copyfield`, `.callout`, `.report-footer`, print styles.

- **`references/base-template.html`** — the neutral FY27 **base**: header + `{{CONTENT}}` region + footer + every
  component class. **This is the template for `adhoc` reports** (fill `{{EYEBROW}}`/`{{TITLE}}`/`{{SUBTITLE}}`/
  `{{BADGES}}`/`{{CONTENT}}` + footer scalars).
- **`references/delivery-info-template.html`** — the `info` report, a **specialisation** on the same theme.
  Both stay visually identical because they share the FY27 tokens.
- **`references/theme-css.md`** — the **canonical theme core** (palette tokens light+dark with `--head-grad`, Segoe
  Semibold, and the `.card`/`.head`/footer chrome). Both templates embed it verbatim; it is the **single source
  of truth** for the skin. Change the theme HERE, then re-sync both templates.

**Glyphs (optional accents):** resolve `{{GLYPH_*}}` via **`references/glyphs.md`** — dynamic Learning Lab
SharePoint fetch → bundled fallback (inline SVGs in `references/glyphs.md`) → omit. `{{GLYPH_PRIVACY}}` (footer) defaults to the
bundled monochrome shield, so it always renders. FY27 multicolour glyphs are loud — use sparingly, as accents.

**Non-negotiable output rules (all report types):**
- A **single self-contained `.html`** — inline `<style>` only, **zero external references** (no CDN,
  fonts, images, or assets).
- **No JavaScript** except the tiny inline copy-button script already in the template — and **no `on*`
  handler attributes** (CSP-safe).
- `<html lang="en" dir="ltr">`, `<meta name="color-scheme" content="light dark">`, a
  `@media (prefers-color-scheme: dark)` override, CSS variables + logical properties.
- Build via the **html** skill (or write directly); **validate with the html validator (default mode)** —
  it must report `status: success` with **zero external references**. Then pass the delivery gate.
- **Every report ends with a Sources / Privacy / Generated-datetime footer** — data provenance, an
  aggregate-only privacy note, and the local generated time. House style for **all** report types.
- **The FY27 theme is mandatory for EVERY report — including a novel/unlisted type that matches no template.**
  The `<style>` MUST embed the CSS from `references/theme-css.md` (its fenced `css` block) **verbatim** (report-specific component CSS goes *after* it).
  Never hand-author theme CSS, never hardcode palette hexes — use the `:root` tokens. Default path for anything
  that isn't `info`: **start from `base-template.html`** (it already embeds the theme + footer). Only build a
  fresh document if the base shell truly can't express the report — and even then, paste the `theme-css.md` CSS verbatim.
- **Dark-mode invariant:** theme-varying backgrounds (gradients, tints) are driven by **per-`:root` variables**
  (e.g. `--head-grad`), **never** a `@media(prefers-color-scheme:dark){ .selector{…} }` override — it loses to
  source order and shows the light value in dark mode. Confirm light **and** dark before the delivery gate.

## Report catalog

| reportType | Renders | Data source | Template |
|---|---|---|---|
| **info** | Delivery Summary (summary, general, delivery, learner background, notes *(when present)*) | `mtt-esiadmin-lookup` `mode:roster` + `includeOrgIndustry` | `references/delivery-info-template.html` |
| _adhoc_ | House-styled report from `data` + `spec` | caller-supplied | `references/base-template.html` |

New pre-defined types are added as new rows + (if needed) a new template that reuses the foundation.

---

## Report type: `info` (the Delivery Summary)

A delivery snapshot for **any point in the delivery's life** — the `{{PHASE}}` badge reads `delivery.phase`
(resolver-derived, **past/present/future**): Upcoming / In progress / Completed / Canceled. It is window-based,
not day-indexed, so it's correct for single-day, multi-day, and multi-delivery-day deliveries alike.
Composition is over the **deduped active registered** learners (unique `esi_learnerid`).

The full **data-model → placeholder map**, the **fill rules** (statistics-bullet summary, the conditional TPM/TPC/Notes/Registration-Health fields, the learner-background bar charts with the top-4-plus-tail and ≥3-category visibility rules, badges, the mandatory Sources/Privacy/Generated footer, and the theme self-check → save → validate → gate sequence), and the **enhancements / planned** notes live in `references/output-spec.md` — load it before filling the template.

## Additional resources

The render assets this skill loads on demand:
- `references/base-template.html` — the neutral FY27 base shell (adhoc + any novel type)
- `references/delivery-info-template.html` — the `info` Delivery Summary template
- `references/theme-css.md` — the canonical FY27 theme core CSS, fenced `css` block (single source of truth for the skin)
- `references/glyphs.md` — glyph resolution (dynamic → bundled inline SVG sets, including FY27 multicolour privacy shield → omit)
- `references/output-spec.md` — the `info` Delivery Summary output contract: data-model → placeholder map, fill rules, and enhancements
- `references/maintenance.md` — field-experience data notes (cancellation · official-date staleness · survey URL · test-account exclusion)

## Guardrails

- **Keep in-line chat output concise.** Lead with the artifact or answer (the delivery + audience card + a one-line file pointer) — detailed reasoning belongs in the thought process, not the reply. Don't recap what the card or the generated report already shows, don't reprint the full menu each turn, and fold follow-up offers into a single closing line (see *Presenting the report in chat*). Brevity, not omission — never drop a needed caveat (privacy, stale/lagging counts, canceled delivery) to save space.
- **Render-only when called; gather-then-render only in ad-hoc** (loop-safe — never re-enter the caller).
- **HTML only** — never produce the text version (that's the gathering skill's job).
- **Delegate all data access** to the MTT skills — this skill never queries Dynamics or Graph itself.
- **No follow-on actions** — no posting, emailing, or Dynamics writes; return the report and stop.
- **Fail fast, spend last.** In ad-hoc mode, confirm prerequisites and rough scale before heavy roster
  enrichment. Prefer cheap delivery/check-in reads first; only pay for roster + industry fan-out when the
  trainer confirms the heavier pass is warranted.
- **Aggregate learner data only.** The Delivery Summary shows composition counts (test/admin excluded) — **never
  an individual named roster** in the report. Reports land in `output/` (syncs to OneDrive) and are
  **trainer-facing**; don't embed learner PII beyond aggregate composition, and never rank/evaluate a learner.
- **The Delivery Summary is INTERNAL — never send it to the class chat.** It is a trainer-facing operations
  artifact (lab code, TPM instructions, registration health, composition), **not** a student deliverable. Do not
  offer — or act on a request — to post/send it to the class (student) meeting chat; onward sharing stays internal
  only (the trainer's own self-chat, a colleague/TPM, print to PDF). Student-facing posting belongs to
  `mtt-class-recap` / `mtt-teams-message`.
- **Language caveat when it matters** — `esi_language` is a portal tag. It's mentioned in the summary only when genuinely mixed (no single language ≥90%); when it is, carry the caveat and don't assert a spoken preference. The LANGUAGE chart always shows the distribution.
- **Preferences** — read `mtt-skill-preferences` only if this skill gains a governing key (none in v1;
  candidate: a default report `style`). Don't fetch it otherwise.
- **Never fabricate** — render only what the data provides; use the documented fallbacks (`none`,
  `Not assigned yet`) for missing fields.
- **Delivery gate** — `Glob output/**/*` (or equivalent) to confirm the file exists before saying it's ready.

*Field-experience data notes (cancellation, official-date staleness, survey URL, test-account exclusion) live in `references/maintenance.md`.*
