# mtt-esiadmin-lookup — output spec

**Purpose:** The JSON envelope this resolver emits — the annotated example and every per-field rule. Load before formatting the final output.
**Loaded by:** `mtt-esiadmin-lookup` on demand (see SKILL.md → Additional resources)

---

## Output — the JSON envelope (emit this as your final output)

Emit exactly one fenced ```json block as the LAST thing in your response. Callers parse this block;
prose around it is ignored. Include only the sections the mode/fieldset populate; set the others to `null`.

_All values below are illustrative placeholders — not real deliveries or identifiers._

```json
{
  "schemaVersion": "2",
  "status": "ok",
  "mode": "delivery",
  "identity": {
    "email": "trainer@contoso.com",
    "systemuserid": "<guid>",
    "bookableresourceid": "<guid>",
    "region": "ACT",
    "timezone": "Australia/Sydney",
    "profile": {
      "trainerType": "Azure Technical Trainer",
      "trainerTitle": null,
      "location": "Canberra",
      "recentTeachTimezone": null,
      "additionalTeachTimezones": "(GMT+10:00) Canberra... | (GMT+12:00) Auckland - 1 week per month",
      "monthlyTeachUtilizationPct": 64.29,
      "yearlyTeachUtilizationPct": 87.5,
      "totalQualifications": 32,
      "onboardingStatus": null,
      "onboardingDate": null,
      "mcpId": "<mcpId>",
      "manager": "Manager Name"
    }
  },
  "delivery": {
    "classId": "100230",
    "workOrderId": "<guid>",
    "courseCode": "PL-7008",
    "courseTitle": "Create agents in Microsoft Copilot Studio",
    "customer": { "name": "Contoso Ltd", "tpid": "1234567", "accountId": "<guid>", "city": "Sydney", "country": "Australia" },
    "officialStart": "2026-06-26T09:00:00Z",
    "officialEnd": "2026-06-26T17:00:00Z",
    "deliveryType": "Private",
    "dayCount": 4,
    "isCanceled": false,
    "phase": "future",
    "modality": "VILT",
    "primaryLanguage": "English",
    "studentLabCode": "XXXXXXXXXXXXXXXX",
    "lxpUrl": "https://esi.microsoft.com/Deliveryonly/?delid=100230",
    "registrationFormUrl": "https://.../?...",
    "readableEventId": "<readableEventId>",
    "surveyUrl": "https://www.metricsthatmatter.com/student/evaluation.asp?k=79335&i=100230",
    "status": { "systemStatus": "Open - Scheduled", "subStatus": "Confirmed", "lxpDeliveryState": "Planned", "period": "FY27" },
    "registrationHealth": "Green",
    "capacity": { "value": 30, "basis": "delivery-max" },
    "counts": { "students": 25, "registration": 25, "attendance": null, "noShow": null, "finalAttendee": null, "walkin": null, "cancelled": null, "waitlist": null },
    "tpmInstruction": null,
    "skillableClassId": "SK-000000",
    "liveCheckin": { "registered": 25, "checkedIn": 22, "waitlist": 0, "cancelled": 1 },
    "catalog": {
      "officialTitle": "Create agents in Microsoft Copilot Studio",
      "prerequisites": null,
      "audienceProfile": null,
      "standardDuration": null,
      "mslearnUrl": null,
      "certification": null,
      "catalogItemType": "Course"
    },
    "support": {
      "supportInfo": "For in-class escalations, contact the ESI Support Desk ...",
      "supportContact": "techskillssupport@microsoft.com",
      "tpm": "TPM Name",
      "tpc": "TPC Name",
      "onboardingPackageUrl": "https://...",
      "trainerReportUrl": "https://...",
      "labRegistrationInstructionsUrl": "https://..."
    },
    "booking": {
      "bookingId": "<guid>",
      "name": "PL-7008 Day 1 - 100230",
      "sessionNumber": "100230",
      "dayLabel": "Day 1",
      "deliveryRole": "Primary",
      "bookingStatus": "Hard Lock",
      "workOrderId": "<guid>",
      "sessionId": "<guid>"
    }
  },
  "roster": {
    "eventId": "<guid>",
    "readableEventId": "<readableEventId>",
    "activeCount": 25,
    "checkinCounts": { "checkedIn": 22, "registered": 3, "noShow": 0 },
    "roleFamilies": {
      "attended": [ { "family": "Development", "count": 8 }, { "family": "Architecture", "count": 6 } ],
      "registered": [ { "family": "Development", "count": 9 }, { "family": "Architecture", "count": 7 } ]
    },
    "orgs": [ { "employer": "Contoso Ltd", "count": 12, "industry": "Financial Services", "tpid": "1234567", "source": "domain-account" } ],
    "students": [
      {
        "learnerId": "<guid>",
        "displayLabel": "Learner-392e",
        "checkinStatus": "Checked-In",
        "role": "Data Engineer",
        "roleSource": "jobtitle",
        "employer": "Contoso Ltd",
        "employerSource": "domain",
        "country": "Australia",
        "language": "English",
        "history": {
          "taughtByYou": true,
          "taughtByYouClasses": [ { "classId": "99001", "courseCode": "DP-700", "date": "2026-03-31" } ],
          "priorClassCount": 4,
          "priorAttendedCount": 3,
          "priorNoShowCount": 1,
          "recentCourses": [ { "classId": "99001", "courseCode": "DP-700", "courseTitle": "Implement data engineering solutions using Microsoft Fabric", "date": "2026-03-31", "checkinStatus": "Checked-In" } ]
        }
      }
    ]
  },
  "schedule": {
    "window": { "start": "2026-07-01", "end": "2026-08-31", "timezone": "Australia/Sydney" },
    "deliveries": [
      { "classId": "100230", "courseCode": "PL-7008", "customer": "Contoso Ltd", "start": "2026-07-08T09:00:00Z", "end": "2026-07-08T17:00:00Z", "role": "Primary", "bookingStatus": "Hard Lock", "deliveryType": "Private Delivery", "registrationHealth": "Gray", "workOrderId": "<guid>", "feedback": { "exists": false, "feedbackId": null, "createdOn": null } }
    ],
    "ndts": [
      { "name": "Prep - PL-7008", "type": "Trainer Prep - Flexible", "start": "2026-07-06T23:00:00Z", "end": "2026-07-07T07:00:00Z", "active": true },
      { "name": "Public Holiday - King's Birthday-2026", "type": "Time Off", "start": "2026-06-07T23:00:00Z", "end": "2026-06-08T07:00:00Z", "active": true }
    ],
    "counts": { "teachingDays": 8, "ndtDays": 5, "byType": { "Trainer Prep - Flexible": 2, "Time Off": 2, "Professional Development": 1 } }
  },
  "candidates": null,
  "diagnostics": null
}
```

- `schemaVersion` is `"2"`. The v2 additions (`identity.profile`; and on `delivery`: `catalog`, the
  enriched `customer`, `support`, `status`, `modality`, `primaryLanguage`, `counts`, and the extra
  `booking` fields) are **additive and optional** — a caller that ignores them still works. Bump again on
  any breaking change.
- `identity.profile` is present only when `includeProfile` was set; otherwise omit it. **Never cached.**
- **`delivery.customer` is `{name, tpid}` by default** — derived from the booking's `CUSTOMER:` text (`esi_bookingdescription`) + `esi_tpid`, with **no `accounts` read**. Only with **`includeCustomerAccount`** is it enriched to `{name, tpid, accountId, city, country}` from the account. `name` may be `null` when no booking `CUSTOMER:` / `msdyn_instructions` value exists — opt into the account then.
- **`delivery.catalog` is present only when `includeCatalog` was set** (both fieldsets) — otherwise the `msdyn_incidenttypes` read is skipped and `catalog` is absent. Consumers that need `catalog.mslearnUrl` etc. (`mtt-class-recap`; `mtt-class-lookup`'s course-resources post) pass the flag.
- **`delivery.counts`** carries `students` + `registration` by default; the extra count fields (`attendance`, `noShow`, `finalAttendee`, `walkin`, `cancelled`, `waitlist`) are **omitted from the default WO select** — mostly null and rarely surfaced, so read them only when a caller asks. (`liveCheckin` via `includeCheckin` still resolves the real-time waitlist.)
- `roster` is populated only for `mode:roster` (an array of active learners alongside the `delivery` anchor); it is `null` for `mode:identity` / `mode:delivery`. Its exact shape depends on `rosterDetail`: `full` includes the enriched learner fields and `roleFamilies`; `light` is the reduced registration-derived shape. Student PII — returned **fresh, never cached**.
- **Names are suppressed by default.** Each `students[]` object carries `learnerId` + a derived `displayLabel` (`Learner-<last 4 hex of learnerId, or of the contact GUID when learnerId is null>`, extended to 6 hex on collision) and **no personal name**. `firstName`/`lastName` are present **only when the caller passed `includeNames:true`** for an explicit name-anchored request; with `includeNames` off, the name columns are never even selected. (Residual: the `_msevtmgt_contactid_value` lookup returns the contact name in its `@…FormattedValue` annotation, which `select` can't suppress; the resolver discards it, so it stays out of the envelope even though it transits the raw read.)
- Each `students[]` object carries a `history` block only when `includeHistory` was set; otherwise omit it. History is **ESI instructor-led classes only**, PII, **never cached**.
- `delivery.surveyUrl` (MTM student-evaluation link) is **always resolved** — the event's `esi_surveyinviteurl` when present, else constructed as `…/evaluation.asp?k=79335&i=<classId>` (deterministic from the Delivery ID, so non-null in every mode incl. `fieldset:learner`). Consumers use it directly — no local construction.
- `delivery.isCanceled` (**boolean**, from `msdyn_systemstatus` = 690970005 / Closed-Canceled) is always present on a resolved delivery; consumers flag/handle cancellation off this, never off `statuscode`.
- `delivery.phase` — a **quick past/present/future notation** for the delivery, one of `future` | `present` | `past` | `canceled`. Computed from **now vs the official window**, interpreting `officialStart`/`officialEnd` in the delivery's **event timezone** (`_esi_timezonenew_value`): `canceled` when `isCanceled` (overrides); else `future` when now < `officialStart`, `present` when `officialStart` ≤ now ≤ `officialEnd`, `past` when now > `officialEnd`. **Window-based, never day-indexed** — it needs no "Day N of M" math, so it reads correctly for a single-day delivery, a multi-day delivery (the whole official span is `present`), and a multi-delivery day (each delivery carries its own window, hence its own phase). Canonical display labels: `future` → **Upcoming**, `present` → **In progress**, `past` → **Completed**, `canceled` → **Canceled**. Always present on a resolved delivery.
- `delivery.dayCount` — number of **teaching** days (computed from per-day bookings / Official span / catalog). **Not** `esi_coursedeliverydurationindays` — that is the **lab-access window** (`delivery.labAccessDays`), which can be tens of days (61 verified for a 4-day class). `null` if indeterminable.
- `delivery.registrationHealth` (`esi_showregistrationhealth` — Gray/Green/Yellow/Red) and `delivery.capacity` (`{value, basis}`) are best-effort. `capacity.basis` is `delivery-max` | `expected-headcount` | `catalog-default` — consumers label the Reg/Cap denominator accordingly and never present an expected/catalog value as a hard maximum.
- `roster.checkinCounts` (`{checkedIn, registered, noShow}`) is present for `mode:roster`. With `rosterDetail:full`, it is tallied from the deduped, test/admin-excluded roster; `checkedIn` is reconciled against the event's **`msevtmgt_checkincount`** (authoritative), and the deduped roster wins on any gap (surfaced in `diagnostics`). With `rosterDetail:light`, it is the reduced registration-derived fast-path tally and should not be treated as the fully classified composition contract. PII path — fresh, never cached.
- `delivery.liveCheckin` (`{registered, checkedIn, waitlist, cancelled}`) is present only on `includeCheckin` — the **cheap** real-time path (one event read, no per-learner walk); `checkedIn` = the event's `msevtmgt_checkincount`. `esi_attendancecount` is **deliberately excluded** (unreliable).
- Cross-skill consumers should apply this precedence: roster-derived counts first, then `liveCheckin`, then caveated mirror counts.

### Counts hierarchy (authoritative → fallback)

Use this order whenever multiple count sources are present:

1. **Roster-derived counts (`mode:roster`, `rosterDetail:full`)** — `roster.activeCount` and `roster.checkinCounts` are authoritative for learner-facing registered/checked-in/no-show tallies.
2. **Live event aggregate (`includeCheckin`)** — `delivery.liveCheckin` is the fast counts-only path when callers do not need a roster walk.
3. **Mirrored/system counts (`delivery.counts`, raw WO/event mirrors)** — fallback only; may lag and should be caveated in consumer output.

Rules:
- On mismatch, roster-derived counts win and the gap is surfaced in `diagnostics`.
- `msevtmgt_checkincount` is the authoritative live checked-in aggregate used by resolver reconciliation.
- `esi_attendancecount` is never an authority source.

### Envelope field provenance bridge

| Envelope field | Source entity/field(s) | Procedure population point |
|---|---|---|
| `delivery.classId`, `delivery.workOrderId` | `msdyn_workorders.msdyn_name`, work-order GUID | Delivery-anchor resolution (work-order resolve + delivery block assembly) |
| `delivery.courseCode`, `delivery.courseTitle` | `esi_catalogitemidcalc`, `esi_catalogitemtitle` | Delivery-anchor resolution (delivery block assembly) |
| `delivery.customer` | Default: booking `CUSTOMER:` text + `esi_tpid`; Enriched: `accounts` via `_msdyn_serviceaccount_value` | Delivery-anchor resolution (enrichment blocks + delivery block assembly) |
| `delivery.catalog` | `msdyn_incidenttypes` via `_msdyn_primaryincidenttype_value` (opt-in) | Delivery-anchor resolution (`includeCatalog` branch) |
| `delivery.support` | Work-order support/escalation fields (trainer fieldset) | Delivery-anchor resolution (support block read) |
| `delivery.capacity` | Delivery max fields, `esi_numberofstudents`, catalog modality max (precedence) | Delivery-anchor resolution (capacity precedence logic) |
| `delivery.liveCheckin` | Event `msevtmgt_registrationcount`, `msevtmgt_checkincount`, `esi_cancelledcount`; WO waitlist | Delivery-anchor resolution (`includeCheckin` branch) |
| `delivery.surveyUrl` | Event `esi_surveyinviteurl` or deterministic fallback from classId | Delivery-anchor resolution (event read + survey fallback) |
| `roster.activeCount`, `roster.checkinCounts` | `full`: deduped non-test registrations + event reconciliation; `light`: reduced registration-derived tallies | Roster resolution (assemble/tally step) |
| `roster.roleFamilies` | Job-title-first `roleFamily` (role code overrides real roles only) via canonical role→family taxonomy (`full` only) | Roster resolution (role-family rollup step) |
| `roster.orgs` | Email domain -> account (`websiteurl`) -> `esi_industry`/`esi_tpid`, else CRM link (opt-in) | Roster resolution (`includeOrgIndustry` branch) |
| `schedule.window`, `schedule.deliveries`, `schedule.ndts`, `schedule.counts` | Booking query split by work-order presence | Schedule resolution (`mode:schedule`) |
| `schedule.deliveries[].deliveryType`, `…registrationHealth` | Work order `esi_deliverytype` / `esi_showregistrationhealth` (opt-in) | Schedule resolution (`includeDeliveryType` branch) |
| `schedule.deliveries[].workOrderId`, `…feedback` | Work order GUID (`_msdyn_workorder_value`); `esi_mttpostdeliveryfeedback` filtered by `_esi_delivery_value` + `statecode` (opt-in) | Schedule resolution (`includeFeedbackStatus` branch) |

This bridge is a maintenance map: when a field changes, update both the population logic in `references/procedure.md` and the envelope contract here.
- `delivery.tpmInstruction` / `delivery.skillableClassId` are best-effort — omit when null.
- `roster.roleFamilies` (`{attended:[{family,count}], registered:[{family,count}]}`) is present only for `mode:roster` with **`rosterDetail:full`** — a derived rollup grouping the deduped, test/admin-excluded learners by their **job-title-first `roleFamily`** (a valid role code overrides the title, skill-levels ignored, `Unspecified` when neither resolves) via the canonical **Role → family map** (references/procedure.md → *Role → family taxonomy*), count-desc. `attended` = Checked-In, `registered` = all active. No extra reads; PII path — fresh, never cached. Consumers render it directly instead of re-applying the map.
- `roster.students` / `activeCount` / composition **exclude test/admin accounts** for **`rosterDetail:full`** (counted separately in `diagnostics`); `rosterDetail:light` is the reduced registration-derived fast path and should not be described as a fully classified composition cut. Consumers should not re-filter either shape.
- `roster.orgs` (distinct employer -> `count`, `industry`, `tpid`, `source`) is present only when `includeOrgIndustry` was set; it groups **domain-first** (email domain -> account via `websiteurl`, else CRM link, else a domain-only label) and `industry` is `null` where no account resolves (expected, not an error). Present for the report's industry rollup.
- `schedule` is present only for `mode:schedule` — `{ window, deliveries[], ndts[], counts }` over the requested window, **self-scoped** (or a named `trainer`). `deliveries[]` carry the trainer's **teaching-booking** `start`/`end` (**not** a delivery's canonical `officialStart` — resolve that via `mode:delivery` if needed); `ndts[]` are typed Non-Delivery Time (`type` = Booking-Status FormattedValue); `counts` = `{teachingDays, ndtDays, byType}` (derived over blocks in hand, distinct local days). **Never cached** (bookings/NDTs move). The consuming skill computes open-days / balance / advisories — the resolver returns classified data only.
- `schedule.deliveries[].deliveryType` (`Open Enrollment` / `Private Delivery`) and `…registrationHealth` (`Gray` / `Green` / `Yellow` / `Red`) are present **only when `includeDeliveryType` was set** — each adds one work-order read per distinct delivery (dedup by `_msdyn_workorder_value`); omitted otherwise. `bookingStatus` (Booking-Status FormattedValue, e.g. `Hard Lock` / `Soft Lock`) is always carried on `schedule.deliveries[]`.
- `schedule.deliveries[].workOrderId` (the resolved work-order GUID) and `schedule.deliveries[].feedback` (`{exists, feedbackId, createdOn}` — whether an **Active MTT Post Delivery Feedback** entry exists for the delivery) are present **only when `includeFeedbackStatus` was set** — each adds one `esi_mttpostdeliveryfeedback` read per distinct delivery (dedup by `_msdyn_workorder_value`). `workOrderId` is **also** carried whenever `includeDeliveryType` resolved the work order. `feedback.exists` is **authorship-agnostic** (any trainer's entry counts). Omitted when neither flag is set.
- `status` is one of `ok` | `ambiguous` | `not_found` | `unavailable`.
- On `status: "unavailable"`, set `diagnostics.code` to `D365_PLUGIN_UNAVAILABLE`, `diagnostics.message` to "The mtt-esiadmin-lookup resolver could not reach the Dynamics 365 Plugin for this read.", and `diagnostics.recommendation` to "Verify the Dynamics 365 Plugin is enabled in Cowork Customisations, then retry." Callers should surface these diagnostics verbatim.
- Unavailable diagnostics shape (compact example):

```json
{
  "status": "unavailable",
  "diagnostics": {
    "code": "D365_PLUGIN_UNAVAILABLE",
    "message": "The mtt-esiadmin-lookup resolver could not reach the Dynamics 365 Plugin for this read.",
    "recommendation": "Verify the Dynamics 365 Plugin is enabled in Cowork Customisations, then retry."
  }
}
```

- `identity` is `null` only on the explicit-ref + `fieldset:learner` path; otherwise present.
- `delivery` is `null` for `mode:identity`. `candidates` is an array only when `status:ambiguous`.
- Every v2 field is **best-effort** — omit it (or set `null`) when the source field is null; never fabricate.
