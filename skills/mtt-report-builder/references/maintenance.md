# mtt-report-builder — maintenance

**Purpose:** Field-experience data notes & gotchas for the render layer — cancellation detection, official-date staleness, survey-URL resolution, and test-account exclusion.
**Loaded by:** `mtt-report-builder` on demand (see SKILL.md → Additional resources)

---

## Data notes (adopted from field experience — Kristen Chan's esi-delivery)

- **Cancellation:** read `delivery.isCanceled` (the resolver derives it from `msdyn_systemstatus` 690970005 —
  never from `statuscode`, which stays `Active`). If `isCanceled`, still render the report but set the phase
  badge to `Canceled` (`b-canceled`) and flag `[CANCELED]` in the header.
- **Dates — Official fields only:** `esi_officialstartdatetime`/`esi_officialenddatetime` are the **single
  source of truth**. `msdyn_datewindowstart/end`, booking `starttime`/`endtime`, and free-text
  `msdyn_instructions` may be **stale** (e.g. after a reschedule) — never use them for the reported date. Render
  Official as `YYYY-MM-DD H:MM AM/PM` (chat/clients mangle `M/D/YYYY`).
- **Survey URL:** use `delivery.surveyUrl` directly — the resolver **always resolves** it (the event field
  when present, else the constructed MTM URL). No local construction here.
- **Test/non-learner accounts** are already excluded from `roster` composition by the resolver (counted in its
  `diagnostics`) — render composition as-is; no re-filtering here.
