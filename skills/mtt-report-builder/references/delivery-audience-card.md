# mtt-report-builder — delivery-audience-card

**Purpose:** The reusable `render_ui` Adaptive Card fragment that shows a delivery's
**panel + attendance figures + role-family composition**. Rendered inline by the MTT skills
that work with a delivery and its roster, so the visual is identical wherever it appears.

**Loaded by:** `mtt-report-builder` on demand (see SKILL.md → Additional resources)

---

**Mirror.** This is a mirrored copy of the canonical fragment at
`mtt-class-lookup/references/delivery-audience-card.md`. Keep in sync when the canonical
changes (per SKILL-DESIGN.md §7 shared-card convention). The body content below is
intentionally kept aligned with the canonical copy so the shared delivery card stays
consistent across the bundle.

**Consumers wrap it with their own sections + menu — the fragment itself carries no menu:**
- `mtt-report-builder` — follows the card with the saved-file pointer / handle and an optional
  next-step line; the fragment itself stays card-only.
- `mtt-delivery-debrief` — appends the per-field summary + a paste-source pointer (saved markdown file) + the
  **copy-from-file / edit** next-step menu (read-only to Dynamics — no submit/write option).
- `mtt-class-lookup` — appends the class links (join / lab code, kept in text) + its
  read-only **phase-aware next steps** (≤3, led by `delivery.phase`). **Never** a
  submit/write menu — class-lookup is read-only to Dynamics.

## Data source
- **Delivery panel** ← `mtt-esiadmin-lookup` `mode:delivery` (`delivery.*`).
- **Attendance + composition** ← `mtt-esiadmin-lookup` `mode:roster` (`roster.checkinCounts`,
  `roster.activeCount`, `roster.students[].role`). For a panel-only path with no roster, live
  counts may come from `mode:delivery` `includeCheckin` (`delivery.liveCheckin`).

Attendance metric precedence: roster counts first (`roster.checkinCounts` + `roster.activeCount`),
`delivery.liveCheckin` second for fast counts-only paths, work-order/envelope mirrors last as caveated fallback.

## The fragment (render in this order)
Invoke the **render-ui** skill first, then `render_ui` (one call). Build these three elements:

1. **Delivery panel** — an emphasised `Container` + `FactSet`: course code + title, Delivery ID,
   customer, **official** date/time, **phase** (`delivery.phase` → Upcoming / In progress / Completed / Canceled), session #, type + modality. **Timing comes from `delivery.phase` (past/present/future) — never a computed "Day N of M" label** (it's wrong for a multi-delivery day and needs no day-math). Render official date/time as
   `YYYY-MM-DD H:MM AM/PM`. If `delivery.isCanceled`, flag it in the panel (never present a
   cancelled class as live).
2. **Attendance figures** — a `ColumnSet` of three KPI columns: **Attended / Registered /
   Cancelled** (from `roster.checkinCounts` + `roster.activeCount`, else `delivery.liveCheckin`).
   Omit the whole row when no counts are available (a `mode:delivery` answer without
   `includeCheckin`).
3. **Role-family bar chart** — a `Chart.HorizontalBar` (or `Chart.VerticalBar`) built directly
   from the resolver's pre-computed **`roster.roleFamilies`** (count-descending). Use
   **`.attended`** for a post-delivery / attended view (mtt-delivery-debrief, and class-lookup once a
   class has run) or **`.registered`** for an enrolment / pre-delivery view — both are already
   bucketed by the **canonical role→family map** in `mtt-esiadmin-lookup`, so **no local mapping is
   applied here**. **Mandatory whenever a roster resolved;** omit it (and say so in the card) when
   no roster was fetched.

## Rules
- **Content/roster-gated:** render only from resolved data; never fabricate a panel value, count,
  or composition. If the roster is unavailable, drop item 3 and note it — don't invent a chart.
- **Aggregate only** — composition is counts by role family, **never a named-learner list**
  (test/admin accounts are already excluded by the resolver).
- **Official date/time is the single source of truth** (`delivery.officialStart`/`officialEnd`);
  never render booking `starttime` or other stale fields.
- Apply attendance precedence for all attendance figures and caveats: roster first, live-checkin second,
  mirror counts fallback-only ("system count, may lag").
- **One `render_ui` call; fall back to text on error** — the consuming skill's text output
  carries the same facts, so a card failure never loses data.
- **Whole-number scales by default.** For count-based charts and KPIs, use whole-number axes,
  tick marks, and value labels; use decimals only when source data is genuinely fractional.
- **Chart colours — omit by default.** Don't set a per-point `color` (or a chart `colorSet`) unless there's
  a reason to — the default palette renders safely and can never raise an "unsupported color palette" error.
  If you must colour, use **only** documented render-ui `ChartColor` enum values (`categoricalBlue` /
  `categoricalTeal` / `neutral`, etc.) — never a bare hue (`blue` / `teal`), a hex, `accent`, or an invented
  `categorical*` name — and set a whole-chart palette only via `colorSet` with one of the six `ChartColorSet`
  values (`categorical`, `sequential`, `diverging`, `sequentialRed/Green/Yellow`).
- **The fragment carries no menu.** The consuming skill appends its own next-step block
  (report-builder: saved-file pointer / handle; mtt-delivery-debrief: copy-paste / edit menu; class-lookup:
  read-only phase-aware next steps). **None writes to Dynamics.**
