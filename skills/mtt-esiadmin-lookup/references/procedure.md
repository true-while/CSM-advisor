# mtt-esiadmin-lookup — procedure

**Purpose:** The full resolution procedure — identity, delivery-anchor, roster, and schedule resolution, learner history, the canonical role→family taxonomy, field projection, and the ambiguity / not-found / unavailable handling. Load before formatting the JSON envelope.
**Loaded by:** `mtt-esiadmin-lookup` on demand (see SKILL.md → Additional resources)

---

## Rules that apply throughout

- **Grounded data only.** Never fabricate IDs, dates, counts, or lookup outcomes; return `null`/status signals when unresolved.
- **Omit null fields.** Emit only resolved values in envelope sections.
- **Fresh reads for identity and learner data.** Re-derive identity each session and never cache learner PII/history.

## Procedure

### Identity resolution

Identity IDs are immutable per trainer, but the built-in memory store is **session-scoped — verified not to persist across sessions** — so **do not cache identity there** (a cross-session cache written to memory is silently lost). Re-derive identity **fresh every session**; it's only two cheap reads.

1. **Prefer the session user context** for the trainer's email, office/**region**, and **time zone** — these
   already ride in the caller's session (name, email, timezone), so **skip the `GetMyDetails` round-trip** by
   default. Call `GetMyDetails` only as a fallback when the context is missing a field, or when a `trainer`
   override is given (resolve that person via the directory instead).
2. **Resolve the IDs fresh.** `read_query systemusers` filter `internalemailaddress eq <email>` → `systemuserid`; `read_query bookableresources` filter `_userid_value eq <systemuserid>` (`valueType:"string"`) → `bookableresourceid`. **No cache read, no cache write** — every session resolves fresh, so there is no stale-cache, account-switch, or cross-tenant hazard to guard against.
3. **Time zone must be returned as an IANA id** (e.g. `Australia/Sydney`), never a Windows name or an abbreviation — downstream DST maths depends on it: both `today`/date-ref resolution (trainer-local day to UTC query window) and NDT windows. If `GetMyDetails` yields a Windows zone (e.g. "AUS Eastern Standard Time"), map it to its IANA equivalent before returning.
4. **Profile / utilization (A) — only when `includeProfile` is set.** Off the resolved `bookableresourceid`, read the profile fields (table in `references/data-model.md`) and return them as `identity.profile`. These are **volatile** (utilization % moves), so read them **fresh every time**. Decode `esi_trainertype` to its label; take the manager name from `_esi_managerlookup_value`'s FormattedValue. Omit any field that's null — never fabricate. Always self-scoped to the resolved trainer. `mtt-time-intel` v1.0.0 intentionally does not set this flag; profile data remains available only for callers with an explicit profile contract, such as descriptive trainer-profile lookup.

### Delivery-anchor resolution
Resolve the **work order** from `ref`, then read the anchor fields. Identity is also resolved unless
this is the explicit-ref + `fieldset:learner` path.

- **`ref = workOrderId` (GUID):** `read_query msdyn_workorders` filter `msdyn_workorderid eq "<guid>"` (`valueType:"string"`, `top 1`).
- **`ref = classId`:** `read_query msdyn_workorders` filter `msdyn_name eq "<classId>"`.
- **`ref = "today"` / a date:** requires identity → `read_query bookableresourcebookings` filter
  `_resource_value eq <bookableresourceid>` (`valueType:"string"`), **ordered `starttime desc` or
  bounded by a date window** (an `asc`+`top` query can truncate and miss today's booking). Pick the
  booking whose day matches, then confirm the work order via the booking's
  **direct FK `_msdyn_workorder_value` (E)** — `read_query msdyn_workorders` filter
  `msdyn_workorderid eq "<guid>"` (`valueType:"string"`, `top 1`) — rather than re-querying by name.
  - **Timezone default — resolve relative refs in trainer-local time, then map to UTC for filtering.**
   "Today", "tomorrow", named weekdays, and relative dates mean that day in the trainer's resolved
   IANA timezone (never server/UTC day). Convert local `[00:00, 24:00)` to UTC using timezone-aware
   conversion (DST-safe), keep the widened edge window, then choose the booking whose converted local
   day matches the target day. This applies only to work-order discovery; reported delivery time still
   comes from `officialStart`/`officialEnd` (see Guardrails).
- **`ref = course + date`:** `read_query msdyn_workorders` filter `esi_catalogitemidcalc eq "<course>"`
  + an `esi_officialstartdatetime` window around the date.

**Always confirm the canonical Delivery ID from `msdyn_workorders.msdyn_name` — never derive it from a
booking name's trailing number** (that number is the session/recording number; its format varies).

**Then read the enrichment blocks off the confirmed work order** (all best-effort — omit any null field):
the catalog record via `_msdyn_primaryincidenttype_value` → `msdyn_incidenttypes` (B → `delivery.catalog`)
**only when `includeCatalog` is set** (else skip the read entirely — `delivery.catalog` is absent),
the customer account via `_msdyn_serviceaccount_value` → `accounts` (C → enriches `delivery.customer`)
**only when `includeCustomerAccount` is set** (else no account read — the default customer path is below),
the support/escalation fields (D → `delivery.support`, **trainer fieldset only**), and the
status/modality/language/count fields (F → `delivery.status`, `delivery.modality`,
`delivery.primaryLanguage`, `delivery.counts`).

Read into the `delivery` block: `classId` (msdyn_name), `workOrderId` (GUID), `courseCode`
(esi_catalogitemidcalc), `courseTitle` (esi_catalogitemtitle), `customer` — **by default `{name, tpid}`**
derived from the booking's `CUSTOMER:` text (`esi_bookingdescription`) + `esi_tpid`, with **no account read**
(`name` is null only when neither the booking `CUSTOMER:` nor `msdyn_instructions` yields one); **with
`includeCustomerAccount`**, instead read `_msdyn_serviceaccount_value` → `accounts` and return the enriched
`{name, tpid, accountId, city, country}`. Then `officialStart`/`officialEnd`, `deliveryType` (decode the option-set to `Private` /
`Open Enrollment`), `studentLabCode`, `lxpUrl`, `registrationFormUrl` and the `readableEventId` parsed
from it. **Plus the new blocks (all best-effort — omit null fields):** `catalog` (B — only with `includeCatalog`), `support`
(D — trainer fieldset only), `status` + `modality` + `primaryLanguage` + `counts` (F — the default select carries `students`/`registration` only; the extra count columns `esi_finalattendeecount`/`walkincount`/`cancelledcount`/`waitlistcount` are **trimmed from the default read** (mostly null, rarely surfaced) — read them only when a caller asks), `isCanceled`
(**boolean** — `true` when `msdyn_systemstatus` = 690970005 / Closed-Canceled; detect cancellation here,
never from `statuscode`, which stays `Active` on canceled deliveries), `dayCount` (number of **teaching** days
— the count of distinct per-day sessions/bookings, else the inclusive `officialStart`→`officialEnd` day span
cross-checked with catalog `standardDuration` / `estimatedDuration`; **do NOT use
`esi_coursedeliverydurationindays`** — that is the lab-access window, not teaching days (verified 61 for a
4-day class); `null` if indeterminable), `labAccessDays` (`esi_coursedeliverydurationindays` — days of student
lab access, a logistics window, **not** teaching days), `registrationHealth`
(`esi_showregistrationhealth` — Gray / Green / Yellow / Red), `capacity` (`{value, basis}` — resolve the denominator
by **precedence**: first non-null of delivery-level max fields `esi_maxenrollmentcount` / `esi_maxroomcapacity`
/ `esi_accountlimit` / `esi_totalavailableseatscount` → basis `delivery-max`; else `esi_numberofstudents` →
basis `expected-headcount`; else catalog modality max → basis `catalog-default`; consumers label the Reg/Cap
denominator by `basis` — never call an expected/catalog value a hard max), `tpmInstruction` (`esi_tpminstruction` — omit when null;
TPM-authored audience/objective guidance, usually only on customized enablement deliveries), `skillableClassId`
(`esi_skillableclassid`), and — **only on `includeCheckin`** — `liveCheckin` (`{registered, checkedIn,
waitlist, cancelled}` — `registered`/`checkedIn`/`cancelled` from the **event**
(`msevtmgt_registrationcount` / `msevtmgt_checkincount` / `esi_cancelledcount`), `waitlist` from the work
order (`esi_rtmwaitlistcounteventregistration`); the work-order `esi_cancelledcount` is usually null, so use
the event's. **Never `esi_attendancecount`** — junk on the event too).

**Delivery phase (`phase`) — computed, window-based, past/present/future.** Derive `delivery.phase` ∈ `future` |
`present` | `past` | `canceled`: `canceled` when `isCanceled`; else compare **now in the delivery's event
timezone** (`_esi_timezonenew_value` — the same zone as the operating wall-clock) against the official window —
`future` before `officialStart`, `present` within `[officialStart, officialEnd]`, `past` after `officialEnd`. It
is **window-based, never day-indexed** (no "Day N of M" math), so it reads correctly for a single-day delivery, a
multi-day delivery (the whole official span is `present`), and a **multi-delivery day** (each delivery has its own
window, hence its own phase — never conflate two same-day classes as "Day 1 of 2"). Canonical display labels for
consumers: Upcoming / In progress / Completed / Canceled.

**Booking sub-object (trainer fieldset only):** find the trainer's own booking for this delivery
(`bookableresourcebookings` `name` contains `<classId>`, scoped to their `_resource_value`) → `name`
(verbatim), `sessionNumber` (the trailing number — **NON-canonical**, matches the recording, NOT the
Delivery ID), `dayLabel`, `deliveryRole` (decode the option-set), `bookingId`, plus (E) `bookingStatus`
(`_bookingstatus_value` FormattedValue, e.g. Soft Lock / Hard Lock), `workOrderId` (`_msdyn_workorder_value`
— the direct FK used above to confirm the anchor) and `sessionId` (`_esi_sessionid_value` → the exact
`msevtmgt_session` for this booking's day, so consumers can join the session without name-matching).

### Roster resolution (`mode:roster`)
Opt-in and **list-shaped** — the one place the resolver returns a collection rather than a single anchor.
Callers use it only when the request needs who's enrolled (roster, attendance detail, "is X in both
classes", learner backgrounds); the class-details path stays on `mode:delivery`.

`rosterDetail` (default `full`) controls roster weight. `full` runs per-learner contact enrichment in step 4 (role/employer/language), which is the latency-heavy fan-out. `light` skips step 4 entirely and returns labels/check-in from registrations only (`learnerId`, `displayLabel`, `esi_checkinstaus`) plus reduced registration-derived `activeCount`/`checkinCounts`; no role/employer/language and no role-family rollup. Use `light` for bare "who's enrolled" asks and reserve `full` for learner-background asks or any authoritative composition/counting need.

1. **Resolve the delivery anchor first** for `ref` (reuse *Delivery-anchor resolution* — identity is
   resolved when `ref` is `today`/a date, skipped for an explicit `classId`/`workOrderId`). Keep the
   `delivery` block; the roster is returned **alongside** it.
2. **Event:** from the work order's `esi_registrationformurl`, take `readableEventId`;
   `read_query msevtmgt_events` filter `msevtmgt_readableeventid eq "<readableEventId>"` → `msevtmgt_eventid`
   (select `esi_surveyinviteurl`, **`msevtmgt_checkincount`**, `msevtmgt_registrationcount` in the same read).
   **`delivery.surveyUrl` is always resolved:** use
   `esi_surveyinviteurl` when present, else construct `https://www.metricsthatmatter.com/student/evaluation.asp?k=79335&i=<classId>`
   (deterministic from the Delivery ID — no event read needed, so it is filled in `mode:delivery` /
   `fieldset:learner` too).
3. **Registrations (roster):** `read_query msevtmgt_eventregistrations` filter
   `_msevtmgt_eventid_value eq "<eventid>"` (`valueType:"string"`) **and** `statecode eq 0` (active only).
   Select `esi_learnerid`, `esi_checkinstaus`, `_msevtmgt_contactid_value` — and **only when `includeNames:true`** also `esi_registrantfirstname`, `esi_registrantlastname` — a tight select keeps the result inline (a wide one
   spills to a file). **`read_query` caps at 50 rows and exposes no `next_link` / continuation cursor** — a registration read returning exactly 50 is **likely truncated**. Most classes sit well under 50; when one doesn't, **re-read partitioned by `esi_checkinstaus`** (its three disjoint values — Checked-In / Registered / No-Show — already in the select) and **merge + dedupe by `esi_learnerid`** (each status subset is very unlikely to exceed 50); note it in `diagnostics` if a single subset still returns 50. **Discard the `_msevtmgt_contactid_value@…FormattedValue` (the contact's name) — use only the GUID for the enrichment hop and never carry the name forward (see the annotation-strip guardrail).**
4. **Per-learner enrichment (full detail only; skip this step when `rosterDetail:light`):** for each registration's `_msevtmgt_contactid_value`, `read_query contacts` filter `contactid eq "<guid>"` (`valueType:"string"`)
   with the **tight select** from the table in `references/data-model.md` (`jobtitle, _esi_learnerrole_value, _parentcustomerid_value, _esi_language_value, _esi_countryid_value, emailaddress1` — and **only when `includeNames:true`** also `firstname, lastname`). Run these reads **in parallel
   batches** — they are the cost of this mode: no server-side `$expand` / `in` filter is exposed today, so
   a per-learner read is unavoidable. Decode `role` from `_esi_learnerrole_value` FormattedValue (fall
   back to `jobtitle`), `employer` from `_parentcustomerid_value` FormattedValue, `language` from
   `_esi_language_value` FormattedValue, `country` from `_esi_countryid_value` FormattedValue.
   **Field precedence — multi-account cohorts (the curated fields are sparse on externally-registered learners, so lead with the always-present raw field and demote the curated field to override/enrichment):** resolve **`employer` domain-first** — `emailDomain` = the lowercased host of `emailaddress1` minus a leading `www.`; an *organisational* domain (not in the personal set `gmail/outlook/hotmail/yahoo/live/icloud/proton/…`) is the grouping key and label, with a canonical account resolved best-effort in step 8; else fall to `_parentcustomerid_value` FormattedValue (CRM link), else a name-embedded org, else `null`. Resolve **`roleFamily` job-title-first** — map `jobtitle` via the keyword rules in *Role → family taxonomy*, and let `_esi_learnerrole_value` override **only when it is a real role** (ignore skill-*level* leakage such as `Fundamental Skills` / `Advanced`). Record `employerSource` (`domain`/`crm-link`/`name`/`null`) and `roleSource` (`jobtitle`/`role-code`/`null`) for provenance; when a domain-resolved account disagrees with `_parentcustomerid_value`, keep the domain and note the mismatch in `diagnostics`. **`emailaddress1` is read for the domain ONLY — never emit the full address** (discard it like the contact-name annotation).
5. **Assemble counts/students, then apply the `rosterDetail` contract.** In `full`, first **drop test / non-learner registrants** from
   composition — e.g. `_esi_learnerrole_value` = Administrator paired with a `jobtitle` / name / email of
   `test`, or an otherwise obviously non-learner account; count them separately in `diagnostics`, never fold
   them into `activeCount`, `checkinCounts`, or any composition tally. Then, a learner who registered more
   than once yields **multiple** registration records — **dedupe by `identityKey`** — the first non-null of `esi_learnerid` → normalised `emailaddress1` → `_msevtmgt_contactid_value` (on multi-account / externally-registered cohorts `esi_learnerid` is null for most learners, so a learnerId-only dedupe silently collapses every null-id learner into one; the identityKey chain keeps distinct people distinct while still collapsing a genuine double sign-up) — keep one per learner
   so composition counts **unique people**, not sign-ups. Set `activeCount` to the deduped unique-learner
   count, and tally **`checkinCounts`** = `{checkedIn, registered, noShow}` from each unique learner's
   `esi_checkinstaus` (859270000 / 859270001 / 859270002). **Reconcile** `activeCount` against
   `esi_registrationcountevent`, and `checkinCounts.checkedIn` against the event's **`msevtmgt_checkincount`**
   (the authoritative live check-in aggregate — **not** `esi_attendancecount`, whose definition is unreliable;
   see Guardrails); if they differ, **the deduped roster is authoritative** (the mirror fields can lag) —
   surface the gap in `diagnostics`. In `light`, skip the contact-based classification path and return the
   fast registration-derived `activeCount` / `checkinCounts` from the active registrations in hand, with no
   claim that test/admin exclusions or role-family composition were fully resolved. Assemble the `roster`
   block: `eventId`, `readableEventId`, `activeCount`, `checkinCounts`, a `students` array, and
   **`roleFamilies` only in `full`** (see step 6 and *Role → family taxonomy* below). **Each learner object
   carries `learnerId` and a derived `displayLabel`; it carries `firstName`/`lastName` ONLY when
   `includeNames:true`.** Compute `displayLabel = "Learner-" + <last 4 lowercase hex chars of `learnerId`, or of the contact GUID `_msevtmgt_contactid_value` when `learnerId` is null — both are GUIDs, so the label is always derivable>` (e.g. `…3a4cd852392e` → `Learner-392e`); on a 4-hex collision within this roster, extend both to 6 hex. `displayLabel` is deterministic — stable across turns/sessions, never positional, never name-derived. Emit **fresh every time — never cache** (student PII).
6. **Role-family rollup (`roleFamilies`, `full` only).** From the deduped, test/admin-excluded
   learners, group each learner's resolved `roleFamily` (job-title-first, from *Roster resolution* step 4) into a functional family using the canonical **Role → family map**
   (below) and return `roster.roleFamilies = { attended: [{family, count}], registered: [{family, count}] }` —
   `attended` counts **Checked-In** learners, `registered` counts **all active** learners; each list is
   count-descending. It is a **derived rollup over `students[]` already in hand — no extra reads**. Roles
   outside the map keep their own name as their family (never force-fit). Providing **both** cohorts lets
   the post-delivery card use `attended`, an enrollment/pre-delivery view use `registered`, and the HTML
   Delivery Summary adopt `registered` — all off one applied map.
7. **Cross-class matching** ("is this learner in both classes?"): the caller invokes `mode:roster` once
   per class and matches on `learnerId` (`esi_learnerid`) — never on name.
8. **Org rollup + industry (`includeOrgIndustry`) — domain-first, best-effort, on-the-fly.** Group the deduped learners by `employerKey` (step 4 — domain-first). For each **distinct** employer among the (deduped) learners,
   resolve a canonical account best-effort with no static map: (a) `read_query accounts` filter `websiteurl` **contains** the `emailDomain`; (b) if multiple candidates return, pick one deterministic best match (see `references/maintenance.md`); (c) if unresolved, `read_query accounts` filter `accountid eq "<guid>"` (`valueType:"string"`) on that learner's `_parentcustomerid_value` GUID (`crm-link`); (d) else no account (label = the cleaned domain). From the resolved account take the canonical `name` (it replaces the raw domain as the label), `esi_industry`, `esi_tpid`. Return
   `roster.orgs` = `[{ employer, count, industry, tpid, source }]` where `source` = `domain-account` | `crm-link` | `domain-only` (no account resolved → `employer` = the cleaned domain, `industry`/`tpid` null). **Domain-first coverage is partial in practice; unresolved `industry` is expected and not an error.** One read
   per distinct employer — opt-in; don't query when the flag is unset. **Never guess an industry** — leave
   it `null` if `esi_industry` is empty (the consuming skill may classify agentically, clearly labelled).

### Role → family taxonomy (canonical — single source for the MTT bundle)

esiadmin has **no functional role-family field** (`esi_microsoftrolegroup` is a skill *level* like
"Advanced", and `esi_roletype` is null), so the family grouping is a **maintained taxonomy, not a query**.
It lives **here** so every consumer — the shared delivery+audience card (`mtt-delivery-debrief`,
`mtt-class-lookup`), the `mtt-report-builder` Delivery Summary, and mtt-delivery-debrief Phase 1F — reads the same
pre-computed `roster.roleFamilies` instead of each re-applying the map. **Add or rename a role HERE**, and
every consumer picks it up automatically.

| Family | Roles |
|---|---|
| Data & Analytics | Data Analyst, Data Engineer, Data Scientist, Database Administrator |
| Development | Developer, DevOps Engineer |
| AI | AI Engineer |
| Security | Security Engineer, Security Architect |
| Architecture | Solutions Architect |
| Management / Business | Technology Manager, and other business / programme / management titles |
| IT Operations & Support | System / Server Administrator, Service Desk / Service Delivery Officer, Desktop / Infrastructure / Network support, DevOps / SRE |

Roles not in the map keep their own name as their family — **never force-fit**.

**Job-title keyword fallback — the PRIMARY role signal when `_esi_learnerrole_value` is null (most learners on multi-account cohorts).** Map `jobtitle` to a family by keyword: *security / cyber / infosec* → Security; *developer / software / application* → Development; *devops / sre / platform* → Development; *architect* → Architecture; *data / analyst / BI / database / DBA* → Data & Analytics; *AI / ML / machine-learning* → AI; *admin / administrator / operations / support / service desk / service delivery / desktop / infrastructure / network / systems* → IT Operations & Support; *manager / director / lead / head / chief* → Management / Business. A structured role code overrides the keyword guess **only when it is a real role** — ignore skill-*level* values (`Fundamental Skills`, `Advanced`, `Intermediate`). A learner with neither a valid role code nor a mappable title rolls up under **`Unspecified`**, so the family counts always sum to the active-registered total. If Microsoft adds a role,
extend this table (the one place), then let the rollup in *Roster resolution* step 6 carry it to every skill.

### Learner history (`includeHistory`, `mode:roster`)
Opt-in, PII, and the heaviest path — attach per-learner history only when the trainer asks who they've
taught before or what a learner has done. Two parts share one per-learner query:

1. **Broad ESI course history (Q2):** for each active learner (or just `studentRef`),
   `read_query msevtmgt_eventregistrations` filter `_msevtmgt_contactid_value eq <contactid>`
   (`valueType:"string"`), ordered `createdon desc`. Each row gives the **course code + title** (event
   FormattedValue, no hop), `esi_checkinstaus` (Checked-In / No-Show / Registered), `statecode`
   (Active / Cancelled), `_esi_deliveryid_value` (the delivery), and `createdon` (signup ≈ delivery date).
   Drop the current delivery; dedupe by course; split **attended** (Checked-In, active) from no-show / cancelled.
2. **Taught-by-you set (Q1):** fetch the signed-in trainer's taught deliveries **once** —
   `read_query bookableresourcebookings` filter `_resource_value eq <bookableresourceid>` (`valueType:"string"`),
   **keeping only rows with a non-null `_msdyn_workorder_value`** (null = Non-Delivery Time — holidays,
   learning days, PTO, travel — not a class). `read_query` caps at 50 rows with no cursor, so if the taught-set exceeds 50 (a long tenure), **split the read by `starttime` date-window** (e.g. per FY) and merge — the same window-split as `mode:schedule`. Dedupe to the set of taught
   work-order GUIDs, keeping each booking's `starttime` (real delivery date). Then per learner, **intersect**
   their attended deliveries (`_esi_deliveryid_value`, Checked-In) with that set — a match means you had them
   in a class before: `taughtByYou = true` + the matched `{classId, courseCode, date}` (date exact, from your
   booking's `starttime`).
3. **Assemble** a per-learner `history` block: `taughtByYou`, `taughtByYouClasses[]`, `priorClassCount`,
   `priorAttendedCount`, `priorNoShowCount`, and `recentCourses[]` (most-recent N distinct — **capped for the
   whole roster, uncapped when `studentRef` scopes to one learner**). Emit **fresh — never cache** (PII).

### Schedule resolution (`mode:schedule`)
Opt-in — the trainer's own **time picture** over a window (self-scoped, or a named `trainer` override).
Read-only; returns a `schedule` block alongside `identity`.

1. **Resolve identity** (systemuserid, bookableresourceid, IANA timezone) — as in *Identity resolution*.
   Pass `includeProfile` to also return `identity.profile` (utilization %, trainer type) for the caller's
   utilization framing.
2. **Window.** Resolve `ref` to a `[start, end]` date range in the trainer's IANA timezone (e.g.
   `"this month"`, `"next 6 weeks"`, an explicit range; **default = current month + next month**), then map
   to a UTC `starttime` / `esi_starttime` window using timezone-aware conversion from the IANA zone (DST-safe,
   no fixed offsets).
3. **Bookings query (teaching + NDT) — one `read_query` per ≤1-month sub-window.** `read_query bookableresourcebookings` filter
   `_resource_value eq <bookableresourceid>` (`valueType:"string"`) + a `starttime` window
   **+ `_bookingstatus_value ne "0adbf4e6-86cc-4db0-9dbb-51b7d1ed4020"`** (`valueType:"string"` — the esiadmin
   **Canceled** booking-status; see the exclusion bullet below), with a **tight select** — `name`,
   `esi_bookingdescription`, `starttime`, `endtime`, `_msdyn_workorder_value`, `_bookingstatus_value` only. Do
   **not** select `esi_deliveryrole` or `bookableresourcebookingid` for a time view (unused, and each lookup /
   option-set column adds repeated OData annotation lines per row). **`read_query` returns at most 50 rows and exposes no `next_link` / continuation cursor** (verified against esiadmin) — so there is **no cursor pagination here**: query **one ≤1-month sub-window at a time and merge client-side** (the default current-month-plus-next window is two calls). A single month is very unlikely to exceed 50 bookings; if any sub-window returns exactly 50 rows, treat it as **truncated** and narrow it further.
   Then **split on `_msdyn_workorder_value`:**
   - **Non-null → a delivery (teaching block).** Derive — with no work-order hop — `classId` + `courseCode`
     from `name` (`"<course> Day <n> - <ClassID>"`), `customer` from `esi_bookingdescription` (`CUSTOMER: …`),
     and `start` / `end` from the booking `starttime` / `endtime` (the trainer's actual booked block — the
     scheduling truth for a time view; a caller needing a delivery's canonical `officialStart` resolves it via
     `mode:delivery`).
   - **Null → an NDT (non-delivery block).** An NDT auto-generates a null-work-order booking whose
     `esi_bookingdescription` carries `Category: <type>` (e.g. `Reason:  Category:  Trainer Prep - Fixed`).
     Parse the text after `Category:` as the NDT **Type** (*Professional Development · Time Off · Trainer Prep -
     Fixed · Trainer Prep - Flexible · Public Holiday · …*) and take `start` / `end` from the booking
     `starttime` / `endtime`. `active` = the booking is present (cancelled bookings don't appear). **This
     replaces the separate `esi_nondeliverytimeentries` read** — one query now covers both teaching and NDT.
   - **Trim caveat (accepted).** Deriving NDTs from the mirrored booking (not `esi_nondeliverytimeentries`)
     drops the typed `_esi_typeid_value` lookup and the naive-local `esi_resourcestarttime` /
     `esi_resourceendtime` — the category comes from free-text `Category:` parsing instead. If a leave type ever
     fails to mirror a parseable `Category:` (unverified for PTO / Public Holiday / Learning in this org), fall
     back to a single `esi_nondeliverytimeentries` read for the window and reconcile. Note any unparseable NDT
     in `diagnostics`.
   - **Exclude canceled bookings (critical).** A booking's `statecode` / `statuscode` **both stay `Active`
     even after the booking / delivery is canceled** — cancellation lives **only** in `_bookingstatus_value`
     (FormattedValue `Canceled`; esiadmin GUID `0adbf4e6-86cc-4db0-9dbb-51b7d1ed4020`). Filtering on
     `statecode` / `statuscode` therefore lets canceled classes leak into the schedule — an entire canceled
     delivery's day-bookings still return under the trainer's `_resource_value` as `Primary` / `Active`
     (observed: a canceled AI-103 + AB-731.S surfaced beside the trainer's one real Hard Lock class on the same
     day). Exclude them with the server-side `_bookingstatus_value ne <Canceled GUID>` filter in step 3
     **and**, as a name-robust backstop, drop any row whose `_bookingstatus_value` FormattedValue is `Canceled`
     client-side (in case the GUID ever changes). **Keep** committed statuses — `Hard Lock`, `Soft Lock` — and
     the NDT-type statuses (Trainer Prep, Time Off, …). Carry each delivery's `bookingStatus` FormattedValue
     into `schedule.deliveries[]` so a consumer can flag a tentative (`Soft Lock`) block.
   - **Delivery type + health (opt-in, `includeDeliveryType`).** By default the schedule path takes **no work-order hop**. When `includeDeliveryType` is set, read each delivery's work order once — **dedupe by `_msdyn_workorder_value`** (a multi-day class shares one) — selecting `esi_deliverytype` + `esi_showregistrationhealth`, and carry their FormattedValues onto `schedule.deliveries[]` as `deliveryType` (`Open Enrollment` / `Private Delivery`) and `registrationHealth` (`Gray` / `Green` / `Yellow` / `Red`) — the same fields/decode as `mode:delivery`, and also carry `workOrderId` (the resolved WO GUID) onto each `schedule.deliveries[]`. Off keeps the schedule read cheap; on, it costs one work-order read per distinct delivery. Omit these fields when the flag is unset. `mtt-time-intel` v1.0.0 does not set this flag; callers such as the `mtt-delivery-debrief` feedback audit may still use it for their own delivery-status contract.
   - **Feedback status (opt-in, `includeFeedbackStatus`).** Detects whether each delivery already has an **MTT Post Delivery Feedback** entry — the primitive the `mtt-delivery-debrief` feedback audit consumes. For each **distinct** delivery (dedupe by `_msdyn_workorder_value` — reuse the `includeDeliveryType` work-order resolve so the GUID is already in hand; **this flag implies that WO hop, so `workOrderId` is always emitted with it**), run the **verified existence check**: `read_query esi_mttpostdeliveryfeedbacks` filter `_esi_delivery_value eq "<workOrderGUID>"` (`valueType:"string"`) **and** `statecode eq 0`, select `esi_mttpostdeliveryfeedbackid,createdon`, `top 1`. Carry onto `schedule.deliveries[]`: `feedback = {exists, feedbackId, createdOn}` — `exists` = a row returned, `feedbackId` / `createdOn` from it (else `null`). **Authorship-agnostic** — a co-trainer's entry counts, so **never** filter by `_createdby_value`. Off by default — one feedback read per distinct delivery; omit `feedback` when the flag is unset.
4. **Assemble + count.** Build `schedule.deliveries[]` and `schedule.ndts[]` (ordered by start) and a derived
   `schedule.counts` = `{ teachingDays, ndtDays, byType }` over the blocks already in hand (distinct local
   calendar days; `byType` sums NDT days per Type). **No open-day / balance / advisory logic here** — that is
   the consuming skill's job; the resolver returns the classified data only.

The `schedule` block is **self-scoped** and **not cached** (a trainer's bookings/NDTs move) — re-read fresh.

### Field projection
- `fieldset:trainer` (default) → the full `delivery` block above (`support`, `status`, `modality`,
  `primaryLanguage`, `counts`, `booking`, `tpmInstruction`, `skillableClassId`; `liveCheckin` when
  `includeCheckin`; `catalog` when `includeCatalog`; enriched `customer` when `includeCustomerAccount`,
  else the booking-derived `{name, tpid}`).
- `fieldset:learner` → `delivery` with ONLY `classId, courseCode, courseTitle, studentLabCode,
  officialStart, officialEnd, surveyUrl`, **plus the non-sensitive `catalog` block when `includeCatalog`
  is set** (B — `officialTitle`, `prerequisites`, `audienceProfile`, `mslearnUrl`; the recap passes the
  flag). `catalog` is no longer auto-included — a learner-fieldset caller that needs it requests
  `includeCatalog`. `surveyUrl` (the always-resolved MTM student-evaluation link — see Roster step 2) is
  student-facing and always present. Omit `lxpUrl`, `registrationFormUrl`, `readableEventId`, `customer`,
  `support`, `status`, and `booking` entirely — a student-facing caller must never receive trainer-internal
  fields.
- `mode:roster` → the `delivery` anchor (trainer fieldset) **plus** a `roster` block (event ids +
  `students[]`; `roleFamilies` only when `rosterDetail:full`). `identity` is populated when `ref` required it (`today`/a date), else `null`.
- `mode:roster` + `includeHistory` → each `students[]` object also carries a `history` block (see *Learner
  history*). With `studentRef`, only that one learner's block — and uncapped.
- `mode:schedule` → a `schedule` block (window + `deliveries[]` + `ndts[]` + derived `counts`) plus
  `identity` (self-scoped; `identity.profile` when `includeProfile`). `delivery` / `roster` are `null`.

### Ambiguity, not-found, unavailable
- More than one work order plausibly matches and you can't separate them → `status: "ambiguous"` and
  populate `candidates`. **Do not guess and do not ask the user** — return the data.
- No match → `status: "not_found"` with a short `diagnostics`.
- esiadmin unreachable / tools absent / auth error → `status: "unavailable"`; set `diagnostics.code = "D365_PLUGIN_UNAVAILABLE"`, `diagnostics.message = "The mtt-esiadmin-lookup resolver could not reach the Dynamics 365 Plugin for this read."`, and `diagnostics.recommendation = "Verify the Dynamics 365 Plugin is enabled in Cowork Customisations, then retry."`
- Otherwise → `status: "ok"`.

## Invocation parameters (full per-flag semantics)

- `includeProfile` (optional, identity resolution): when set, also return the trainer-profile / utilization block (`identity.profile`). Read **fresh** each time — **never cached** (utilization is volatile).
- `mode:roster` (opt-in — the one list-shaped return): resolves the delivery anchor for `ref`, then walks it to the enrolled learners and returns a name-suppressed `roster` array (learnerId, a derived `displayLabel`, role, employer, language, country, check-in status — **no personal name** unless `includeNames:true`) **alongside** the `delivery` block. With `rosterDetail:full`, it also returns a pre-computed **`roleFamilies`** composition rollup (attended + registered), bucketed by the canonical role→family map (see *Role → family taxonomy* below) — so every consumer renders the same families without re-applying the map. With `rosterDetail:light`, skip that rollup and treat `activeCount` / `checkinCounts` as the reduced registration-derived fast path only. Use only when a caller actually needs who's enrolled — the common class-details path stays on `mode:delivery` and never pays for the per-learner reads. Roster data is student PII: returned **fresh, never cached**.
- `includeNames` (optional, `mode:roster` only — default **false**): when set, each learner object additionally carries `firstName`/`lastName`. **Off by default:** the name columns aren't selected, and no name is returned in the `students[]` envelope or rendered anywhere (the one residual name-leak path — the required `_msevtmgt_contactid_value` FormattedValue annotation — is handled by the *Strip the contact-lookup name annotation* guardrail). Turn on ONLY for an explicit, trainer-initiated, name-anchored request (e.g. "have I taught <name>?"), ideally scoped to one learner via `studentRef`.
- `includeHistory` (optional, `mode:roster` only): attach a per-learner `history` block — (a) `taughtByYou`: has this learner attended a prior class *the signed-in trainer* taught, and which; (b) their broad prior ESI course history (counts + most-recent courses). **Opt-in and heavier** — it adds a per-learner history query plus a one-time fetch of the trainer's taught deliveries; set it only when who-have-I-taught / learner-backgrounds is actually asked. History is PII: **fresh, never cached**.
- `studentRef` (optional, with `includeHistory`): narrow the history to a single learner — a `learnerId`, a `displayLabel`, or `contactId`. Matching by **name** requires `includeNames:true` (names aren't loaded otherwise); prefer `learnerId`/`displayLabel`. With it, that one learner's **full** history is returned (cheap, targeted); without it, **every** active learner gets a **summarised** history (expensive on a full class).
- `includeOrgIndustry` (optional, `mode:roster`): also resolve each **distinct employer's industry** (the account's `esi_industry`) and return a `roster.orgs` rollup (`{employer, count, industry, tpid, source}`) resolved **domain-first** (email domain → account via `websiteurl`, else the CRM link, else a domain-only label — see *Roster resolution* step 8). Opt-in — one account read per distinct employer key; set it only when a caller needs the industry grouping (e.g. the report's collapsible org section).
- `includeCheckin` (optional, `mode:delivery` — the **cheap real-time path**): does **one** event read (parse `readableEventId` from the work order → `read_query msevtmgt_events` select `msevtmgt_checkincount`, `msevtmgt_registrationcount`, `esi_cancelledcount`) plus the work order's `esi_rtmwaitlistcounteventregistration`, and returns `delivery.liveCheckin` = `{registered, checkedIn, waitlist, cancelled}` — **no per-learner walk**. Use for "how many checked in right now?". Deliberately **excludes** `esi_attendancecount` (unreliable — see Guardrails). `mode:roster` resolves the same numbers off its event read.
- `includeCustomerAccount` (optional, `mode:delivery` / `mode:roster`; default **false**): read the customer `accounts` record (via `_msdyn_serviceaccount_value`) and return the **enriched** `delivery.customer` = `{name, tpid, accountId, city, country}`. **Off by default** — the resolver instead derives `delivery.customer = {name, tpid}` from the booking's `esi_bookingdescription` `CUSTOMER:` text + the work order's `esi_tpid`, with **no account read**. Set it only when a caller needs the account's city / country / accountId.
- `includeCatalog` (optional, `mode:delivery` — **both fieldsets**; default **false**): read the course-catalog master (`msdyn_incidenttypes` via `_msdyn_primaryincidenttype_value`) and return `delivery.catalog` (`officialTitle`, `prerequisites`, `audienceProfile`, `standardDuration`, `mslearnUrl`, `certification`, `catalogItemType`). **Off by default** (an extra read of mostly-null fields on the common path). Set it when a caller needs the catalog — `mtt-class-recap` (learning-path seed) and `mtt-class-lookup`'s course-resources post. The `fieldset:learner` catalog is now flag-gated too (previously auto-included).
- `mode:schedule` (opt-in — the trainer's own **time picture** over a window): resolves identity, then reads the trainer's **bookings** in **one** `bookableresourcebookings` query over a `starttime` window, **excluding Canceled bookings** (`_bookingstatus_value ne <Canceled>` — `statecode`/`statuscode` stay Active on cancel, so canceled classes otherwise leak in), and splits them by `_msdyn_workorder_value` — non-null rows are **deliveries** (teaching), null rows are **NDTs** (Non-Delivery Time), whose category is parsed from the booking's `esi_bookingdescription` (`Category: <type>`). Returns a `schedule` block (deliveries + NDTs + derived `counts`) alongside `identity`. Pair with `includeProfile` for utilization. **One booking query covers both teaching and NDT — no separate `esi_nondeliverytimeentries` read** (see the trim + Canceled-exclusion notes in *Schedule resolution*). **Self-scoped** (or a named `trainer` override), read-only.
- `includeDeliveryType` (optional, `mode:schedule`): also read each delivery's work order once (**dedupe by `_msdyn_workorder_value`**) to carry `deliveryType` (Open Enrollment / Private Delivery) + `registrationHealth` (Gray / Green / Yellow / Red) + `workOrderId` (the resolved WO GUID) onto `schedule.deliveries[]` — the same fields/decode as `mode:delivery`. **Opt-in** — one work-order read per distinct delivery; use it only when a caller needs delivery-type or registration-health fields, such as the `mtt-delivery-debrief` feedback audit. `mtt-time-intel` v1.0.0 does not set it. Off by default keeps the schedule read cheap (no work-order hop).
- `includeFeedbackStatus` (optional, `mode:schedule`): also detect, per delivery, whether an **Active MTT Post Delivery Feedback** entry exists in `esi_mttpostdeliveryfeedback` — carrying `feedback` (`{exists, feedbackId, createdOn}`) and the delivery's `workOrderId` onto `schedule.deliveries[]`. Reuses the `includeDeliveryType` work-order dedupe, then does **one** feedback `read_query` per distinct delivery (filter `_esi_delivery_value eq "<workOrderGUID>"` `valueType:"string"` + `statecode eq 0`, `top 1`). **Existence is authorship-agnostic** (any trainer's entry counts — never scope to `_createdby_value`). Opt-in — set it for the `mtt-delivery-debrief` feedback audit ("which Private deliveries have no entry?"); typically paired with `includeDeliveryType` so the caller can filter to Private first.
