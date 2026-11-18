---
name: mtt-esiadmin-lookup
description: |
  INTERNAL LIBRARY SKILL — not user-triggered. Invoked by sibling MTT skills via the Skill tool to resolve trainer identity, delivery anchors, rosters, and schedules against esiadmin Dynamics 365. It returns a strict JSON envelope; it never posts, writes, or prompts the user. Do NOT route a user request directly here.
metadata:
  version: "0.10.10"
  category: productivity
  icon: DatabaseSearch
---

# MTT esiadmin Lookup (internal resolver)

A shared sub-routine for the MTT skill bundle. It owns the one piece every esiadmin skill repeats:
the environment contract, **identity resolution** (who is the signed-in trainer), **delivery-anchor
resolution** (which work order is this class, confirmed canonically), and — on request — **roster
resolution** (the enrolled learners with per-learner role, employer, and language). Callers invoke it
via the Skill tool, read the JSON envelope it returns, and then do their own work (presentation, posts,
NDT lookups, feedback prep, recaps) off the resolved values. **No caller writes to Dynamics — the bundle is read-only to esiadmin.**

**This skill is read-only and silent:** it only `read_query`s esiadmin; it never
`create_record`/`update_record`, never posts to Teams, and **never asks the user a question** — on
ambiguity it returns candidates as data and lets the calling skill decide.

## When NOT to use (this is a library callee, not a destination)

A user request is always handled by a sibling skill, which then calls this resolver as a sub-step.
Never route a user-facing task here — delegate:

- Class details / roster / attendance / Teams invite / lab-access or break posts → use mtt-class-lookup.
- Trainer schedule / non-delivery checks (PTO, prep, holidays, open days, duplicate bookings) → use mtt-time-intel.
- Capture / prepare MTT Post Delivery Feedback → use mtt-delivery-debrief *(if available; otherwise state that feedback drafting is unavailable in this package, retain any resolved data, and do not emulate it here)*.
- Build a student-facing class link recap → use mtt-class-recap.
- Run-of-show / pacing / demo blow-by-blow → use mtt-class-timeline.
- Sales accounts / opportunities / pipeline → use the dynamics-365-sales plugin.

This skill only resolves identity + the delivery anchor and returns the JSON envelope; every outward
action and user interaction belongs to the calling skill.

## How a caller invokes me

Invoke via the Skill tool with a short instruction naming the parameters:

- `mode`: `identity` | `delivery` | `roster` | `schedule`
- `ref` (delivery + roster): a `classId` (msdyn_name), a `workOrderId` (GUID), `"today"` / a date, or `course + date`
- `fieldset` (delivery only): `trainer` (default) | `learner`
- `trainer` (optional): resolve on behalf of a named trainer instead of the signed-in user

The optional opt-in flags each carry cost / PII / caching nuance — **full per-flag semantics (when to set, cost, PII, caching, edge cases) are in `references/procedure.md` → _Invocation parameters_**. At a glance:

| Flag | Mode | Adds | Key note |
|---|---|---|---|
| `includeProfile` | identity | `identity.profile` (utilization) | fresh, never cached; used only by callers that need profile basics; `mtt-time-intel` v1.0.0 does not request it |
| `mode:roster` | roster | `roster.students[]` (+ `roleFamilies` in `full`) | opt-in, name-suppressed, fresh/never cached |
| `rosterDetail` | roster | `light` skips the per-learner contact fan-out | default **`full`** (roles/employers/languages via one contact read per learner — the latency-dominating fan-out; authoritative composition counts + `roleFamilies`); set **`light`** for a labels-only roster (`learnerId` + `displayLabel` + check-in status from the single registrations read) — the fast path for a bare "who's enrolled", with reduced registration-derived counts and no `roleFamilies` |
| `includeNames` | roster | per-learner `firstName`/`lastName` | default **false**; explicit name-anchored asks only |
| `includeHistory` (+ `studentRef`) | roster | per-learner `history` | opt-in, heavier, ESI instructor-led only, fresh |
| `includeOrgIndustry` | roster | `roster.orgs` (employer → industry, **domain-first**) | one account read per distinct employer key |
| `includeCheckin` | delivery | `delivery.liveCheckin` | one event read, no per-learner walk; excludes `esi_attendancecount` |
| `includeCustomerAccount` | delivery / roster | enriched `delivery.customer` (city/country/id) | default **false**; one account read |
| `includeCatalog` | delivery | `delivery.catalog` | default **false**; recap + course-resources set it |
| `mode:schedule` | schedule | `schedule` block (deliveries + NDTs + counts) | one bookings query, excludes Canceled; self-scoped |
| `includeDeliveryType` | schedule | `deliveryType` + `registrationHealth` (+ `workOrderId`) on each `schedule.deliveries[]` | opt-in; one work-order read per delivery; used by callers such as the mtt-delivery-debrief feedback audit, not by `mtt-time-intel` v1.0.0 |
| `includeFeedbackStatus` | schedule | `workOrderId` + `feedback` (`{exists, feedbackId, createdOn}`) on each `schedule.deliveries[]` | opt-in; one Post Delivery Feedback read per delivery; pairs with `includeDeliveryType` for the mtt-delivery-debrief feedback audit |

**Identity is resolved in every case EXCEPT** an explicit `classId`/`workOrderId` with
`fieldset:learner` — that one path resolves the work order directly with no identity lookup (it's the
mtt-class-recap case).

Example invocations (plain language is fine): *"resolve identity"* · *"resolve delivery for my class
today, trainer fieldset"* · *"resolve delivery for ClassID `<ClassID>`, learner fieldset"* · *"resolve
delivery for course `<course-code>` on a given date"*.

## Environment contract (esiadmin)

- Dataverse tools with `orgName: "esiadmin"`, **read-only** here: `read_query`.
- **Relevance Search is OFF** → always `read_query` with structured filters, never the `search` tool.
- **Metadata is blocked** (`list_tables`/`describe_table` → 400) → rely on the fields in `references/data-model.md`.
- **Lookup `_value` filters require `valueType:"string"`** (a `guid` valueType → HTTP 400).
- `esi_class` / `esi_classparticipant` are **403** — never use them.
- **Fetch-by-ID is failing on this connection** → resolve records by primary-key filtered `read_query` (`<table>id eq "<guid>"`, `valueType:"string"`), never `fetch`, and never fall back to filtering on `msdyn_name`.

## Procedure

Resolve identity, the delivery anchor, the roster, and the schedule from `mode` + `ref` + flags, then read the
enrichment blocks off the confirmed work order. **Full step detail — identity / delivery-anchor / roster /
schedule / learner-history resolution, the canonical role→family taxonomy, field projection, and the
ambiguity / not-found / unavailable handling — is in `references/procedure.md`; load it before formatting the
envelope.**

- **Identity** (all modes except explicit `classId`/`workOrderId` + `fieldset:learner`) — take the trainer's
  email / region / IANA timezone from the **session user context** when present (skip the `GetMyDetails`
  round-trip; fall back to `GetMyDetails` only when the context lacks a field, or for a `trainer` override);
  `systemusers` → `systemuserid`; `bookableresources` → `bookableresourceid`. **Re-derived fresh each
  session, never cached.** `includeProfile` adds the profile / utilization block.
- **Delivery anchor** — resolve the work order from `ref` (`classId` / `workOrderId` / `today`-or-date /
  `course + date`); confirm the canonical Delivery ID from `msdyn_workorders.msdyn_name` (never a booking's
  trailing number); read the enrichment blocks (catalog, enriched customer, support, status / modality /
  language / counts, booking) — all best-effort. Also derive `delivery.phase` (past/present/future/canceled —
  window-based, no day-index math) from now vs the official window in the event timezone.
- **Roster** (`mode:roster`, opt-in, list-shaped) — event → registrations → contacts; **name-suppressed by
  default** (`displayLabel`; names only on `includeNames`). `rosterDetail:full` returns the pre-computed
  `roleFamilies` rollup and the authoritative composition counts; `rosterDetail:light` stays on the
  registration-only fast path and omits `roleFamilies`. `includeHistory` / `includeOrgIndustry` /
  `includeCheckin` are opt-in.
- **Schedule** (`mode:schedule`, self-scoped) — **one** bookings query over the window, **excluding Canceled
  bookings** (via `_bookingstatus_value`, since `statecode`/`statuscode` stay Active on cancel); non-null-work-order
  rows are deliveries, null rows are NDTs (category parsed from `esi_bookingdescription`) → the `schedule`
  block. No separate `esi_nondeliverytimeentries` read (trim).
- **Ambiguity / not-found / unavailable** — return `status` + `candidates` / `diagnostics`; never guess, never ask.

## Output

Emit exactly **one** fenced ```json block as the LAST thing in your response — callers parse this block; prose around it is ignored. Include only the sections the mode/fieldset populate; set the others to `null`. `status` is one of `ok` | `ambiguous` | `not_found` | `unavailable`, and the envelope is emitted **even on `not_found` / `unavailable`** so callers can parse a result deterministically.

The full annotated schema, an illustrative example, and every per-field rule live in `references/output-spec.md` — **load it before formatting the envelope.**

## Additional resources

Load on demand for detail:
- `references/data-model.md` — esiadmin tables, fields, IDs, and the A–F field groups the Procedure references
- `references/output-spec.md` — the JSON envelope: annotated schema, example, and per-field rules
- `references/procedure.md` — the full resolution procedure (identity / delivery / roster / schedule / history), the role→family taxonomy, field projection, and ambiguity handling, and full invocation-parameter semantics
- `references/maintenance.md` — operational notes for generic, on-the-fly, uncached domain-to-account resolution (websiteurl match -> CRM link -> domain-only)

## Guardrails

- **Read-only and silent resolver.** Only `read_query` in esiadmin; never `fetch`, never write/post/schedule, and never prompt the user. Return ambiguity/failure as `status` + `candidates`/`diagnostics`.
- **Identity is re-derived each session, never cached.** Resolve fresh from `systemusers` + `bookableresources`; never persist identity or PII.
- **Ground every value in tool data.** Never fabricate ClassIDs, GUIDs, dates, customer/support fields, or counts; return `null`/non-`ok` status when unresolved.
- **Canonical IDs and times are strict.** Delivery ID is always `msdyn_workorders.msdyn_name`; canonical delivery times come only from `esi_officialstartdatetime` / `esi_officialenddatetime`.
- **Schedule excludes canceled bookings server-side.** Filter by `_bookingstatus_value ne <Canceled>` (with formatted-value backstop), not by `statecode`/`statuscode`.
- **`rosterDetail:full` remains authoritative for attendance/composition.** Use its roster-derived `activeCount`/`checkinCounts`, exclude test/admin accounts there, and reconcile lagging work-order counters in `diagnostics`. Treat `rosterDetail:light` as a reduced registration-derived fast path, not as the authoritative composition contract.
- **Always emit `surveyUrl` and derived `isCanceled`.** Consumers should not reconstruct survey links or cancellation logic.
- **Never use `esi_attendancecount` as live check-in truth.** Use event check-in (`msevtmgt_checkincount`) and surface waitlist only when non-zero.
- **`fieldset:learner` is a hard projection.** Exclude trainer-internal fields; keep `surveyUrl`, and include `catalog` only when the caller requests `includeCatalog`.
- **Roster/history privacy rules are mandatory.** Keep names off by default, strip contact lookup name annotations from emitted data, treat history as opt-in and expensive, and never cache learner PII.
- **Canonical unavailable diagnostics are mandatory.** On `status: "unavailable"`, set `diagnostics.code = "D365_PLUGIN_UNAVAILABLE"`, `diagnostics.message = "The mtt-esiadmin-lookup resolver could not reach the Dynamics 365 Plugin for this read."`, and `diagnostics.recommendation = "Verify the Dynamics 365 Plugin is enabled in Cowork Customisations, then retry."` Callers should surface these diagnostics verbatim.
- **For person-lookup caveats and polymorphic lookup handling, follow `references/procedure.md` exactly.**
- **Emit the JSON envelope last, always** (including `not_found` / `unavailable`) so callers can parse deterministically.
- **Note for auditors:** this skill intentionally has no user-facing trigger phrases (library callee); low Trigger Clarity is expected.
