# Eligibility, Capacity, PDc and Policy Controls

## Status of this reference

The policy values below are the operating plan's **11 November 2026 baseline**, not permanent universal rules or a new independent policy verification. Revalidate applicable governing sections, effective dates and regional interpretation at runtime. If unavailable, retain a source-snapshot label and a policy gate. A newer modification date alone does not resolve conflicting authority.

## Catalog resolution

For each proposed learning objective:

1. Read the ESI catalog from the esiadmin Dataverse source described below, or, if that read is denied or fails, an authorized ESI Catalog export or query that explicitly exposes PD. Record exact scope, retrieval time, refresh if known and the evidence for each required field.
2. Require PD = Yes and active status, plus exact identifier/title/version, official duration/unit, format, audience, prerequisites, language, modality and supported environment. Validate fields absent from the catalog with their authoritative owner. Missing fields remain pending; known incompatible fields make the mapping ineligible.
3. Preserve official duration separately from conceptual learning blocks. Do not infer a day count from an hour value without an authorized delivery interpretation.
4. Match the package outcome and actual environment. Government environments require explicit support, not commercial parity assumptions.
5. Recheck on retirement, version, audience, environment, format or date changes. Quarantine affected mappings and propose reapproval.

**Resolver boundary:** `skilling-catalog`, if available, may enrich discovery only. Its MTT Indicator is not proof of PD = Yes. Its card-only presentation contract must not replace this skill's dual-view contract. If it cannot return the explicit PD field and required evidence, retain pending eligibility and use the esiadmin catalog read below, or an authorized catalog export/owner validation if that read is denied or fails. Never infer missing eligibility from a public Learn page, professional-development day metric or another report's course join.

### ESI catalog source (as of November 2026)

The authoring source originally reported denied catalog/model reads on the Power BI "ESI Catalog" report under Read-only permission. As of November 2026 the ESI catalog is directly readable, read-only, in the esiadmin Dataverse environment, table `msdyn_incidenttype` (Catalog Items). Read it with a SQL SELECT (`ExecuteSql`) against target `esiadmin`. Prefer this source over the Power BI "ESI Catalog" report, which the user can only read without Build permission.

**Filter:** statecode = 0, statuscode equal to the Active status reason, and esi_isattindicator = true. Confirm column names and the Active status value with `DESCRIBE msdyn_incidenttype` on the target if a query is refused.

| Field | Authoritative catalog evidence |
| --- | --- |
| msdyn_name | Catalog ID (exact identifier) |
| esi_title | Official title |
| statuscode | Status; must be Active |
| esi_isattindicator | MTT indicator; filter value, not PD proof on its own |
| esi_pdceligible | PDc eligible flag; treat true as the PD = Yes gate |
| esi_standardduration, msdyn_estimatedduration | Official duration in minutes; record both and flag a mismatch |
| esi_viltminimumcapacity, esi_viltmaximumcapacity | Virtual (VILT) seat limits per class |
| esi_deliverytypessupported | Supported delivery types, for example Private Only, or OE and Private |
| esi_catalogitemtype | Catalog item type, for example MOC Courseware |
| esi_externalurl | External course page (internal reference only) |
| msdyn_description | Official description |
| esi_audienceprofile | Audience profile |

Use these fields as authoritative catalog evidence for the current run. Seat limits apply to virtual delivery; for in-person delivery, record the in-person cap only from evidence and leave it pending otherwise. Convert minutes to the class length shown in plans (for example 60 minutes is 1 hr), but never convert minutes or hours into PDc.

**Example facts verified November 11, 2026 (examples only, revalidate on each run, never defaults):**

| Catalog items | Official length | Seat limits | Delivery |
| --- | --- | --- | --- |
| MS-4018.S01 to MS-4018.S07 | 1 hour each | 1 to 200 VILT seats | Private only |
| MS-4004.1 to MS-4004.10 | 1 hour each | 5 to 40 seats | As recorded at run time |
| MS-4021.01 to MS-4021.13 (CIE) | 1.5 hours each | 5 to 20 seats | In person |
| MS-4018 | 8 hours | 5 to 40 seats | As recorded at run time |

All of the above were active, MTT indicator and PDc eligible at that check.

**Fallback:** if the esiadmin read is denied or fails, record the denial or error, keep every affected mapping as pending, and fall back to the existing pending mapping behaviour (authorized export or owner validation request). Discover actual permissions on each run. A denial stops that access path; no alternate identity, permission escalation or protection downgrade is attempted.

## Capacity states

| State | Evidence required | What the advisor may do |
| --- | --- | --- |
| Unknown | No suitable returned evidence | State the gap and request the necessary scoped source. |
| Indicative | Dated aggregate signal or broad window with filters and coverage | Explore conditional timing; do not name a resource or available slot without evidence. |
| Matched | Exact content qualification, language, teaching zone, modality, environment, candidate window and current operational checks | Report a candidate match, with remaining gates. It is not a reservation. |
| Held | Fresh existing authorized hold record, owner, exact scope and explicit expiry | Report the external state as of the read. Never create, renew or extend it. |
| Confirmed | Fresh existing booking record plus required approvals for the same version and scope | Report verified external confirmation. Never create or modify the booking. |

An expired hold has `reported_state=held`, `effective_state=expired`, and is not described as reserved. Revalidate the match; do not silently promote or reuse it. Stale confirmation is historical until revalidated. The record retains both source state and effective state.

Check Ready and Validate qualification meanings with MTTM for the exact content/version. A combined measure is not bookability proof. In Progress is not delivery-ready evidence. Check live conflicts, leave, prep, travel and backup separately. Teaching-zone ability is not home country.

### Trainer availability search and continuity

Search availability across all AMS MTTs, not only the requesting manager's team.

1. **Resolve the bench at run time.** Read the org chart under Erin Jacobsen (erinj@microsoft.com), for example the `org_chart` relation with that root, and keep trainers only. At the November 2026 baseline this was about 35 trainers across the teams of Renato Strianese, Peter O'Keefe, Tracey Carisch and Gauthier Choquet; that count and team list are a baseline description, not a default. Record the retrieval time.
2. **Read free/busy for the proposed delivery days** in the customer teaching time zone, using a read-only calendar free/busy capability discovered at run time. Do not open event details beyond free/busy.
3. **Classify each trainer** as clear all days, tentative holds only, partly free or not free across the proposed days. Flag trainers whose local time makes the teaching window late (for example a trainer in Brazil for a late Pacific window) and record their home time zone and local window.
4. **Propose a continuity core team.** Name 2 or 3 trainers who stay across all waves. Assign 1 or 2 of them to the first wave, preferring a trainer already supporting the customer, and name the third as the scale or second-track trainer. Keep the wider AMS bench as reserve only. Assign one trainer per delivery day by default.
5. **Keep the gate open.** Calendar free/busy is indicative only. It is not course qualification, a hold or a booking. Always list "confirm course qualification and later-wave calendars" as a gate with an owner role. A free calendar never moves a capacity state above Indicative without the Matched evidence in the table above.

Trainer names, home time zones and free/busy classifications stay on the internal view only. Never rank trainers on performance; the classification describes calendar state only.

Unaccounted days are not qualified slots, PDc, free hours or learner reach. Preserve authorized filters. An availability-only filter yielding zero deployment does not prove zero deployment overall. Do not double-count a team within its region or sum overlapping snapshots. No rows, including missing April rows in the historical example, means unconfirmed coverage, not zero capacity or proof that the dataset ended. Offer alternate windows, eligible open enrollment, an authorized partner or approved asynchronous resources only with their own eligibility and scope checks.

## Day-based estimation

Use these baseline rules only with applicable current policy evidence. Keep `estimated_credits` separate from `approved_system_credits`.

| Baseline rule | Required planning treatment |
| --- | --- |
| One trainer delivery day equals one PDc; whole credits, minimum one per line | Count actual delivery days. No generic hours divided by eight, fractional-hour proration or invented rounding. |
| Days drives credits; Quantity represents delivery/audience links | A multi-day course can retain Quantity = 1. Three audience links do not necessarily mean three trainer days. |
| Three one-hour sessions on one day use one credit; on three days use three | This is a supported illustration, not permission to compress standard courses or pack unlimited sessions. |
| Prep: add 1 PDc per virtual delivery line | Estimate it on every virtual delivery line. Add prep to an in-person line only when the user confirms it, and say so in the internal notes. Prep and travel are still entered as their own approved lines and NDT records; nonstandard preparation goes through SWR where required. |
| Travel for in-person delivery: add 2 PDc | 1 PDc for the day before the first session day and 1 PDc for the day after the last session day. Non-consecutive in-person days need separate treatment and an explicit travel assumption. |
| Max-capacity setting 81 or above prompts moderator Yes/No | The prompt is not a mandatory moderator or universal class cap. Yes adds one credit per trainer delivery day. Show the moderator as "not included" unless the user selects it. |
| Double Capacity doubles the training-line credits while Days stays unchanged | Authorized operations must update resource count to two after approval and before Scheduling. This skill only identifies the dependency. |
| Combined moderator/second-resource arithmetic is undocumented | Do not combine standalone formulas into a presumed total. Use null for the unresolved combined total and request the official system calculation. |
| AER still requires a catalog item | Do not fabricate a combined code. Follow the authorized one-item-per-line and post-approval delivery-item process if still applicable. |

**Estimating rule (approved by the skill owner, November 11, 2026):** Est. PDc = trainer delivery days, plus 1 prep PDc for each virtual delivery line, plus 2 travel PDc for each in-person delivery, plus 1 moderator PDc per trainer delivery day only when a moderator is selected. Worked examples from the skill owner: a 3-day in-person CIE immersion = 3 deliver + 2 travel = 5 PDc; a 2-day on-site immersion = 2 deliver + 2 travel = 4 PDc. These in-person examples do not add prep. A 3-day virtual line would be 3 deliver + 1 prep = 4 PDc.

Show each forecast line with Days, Est. PDc and a "Built from" column (for example "3 deliver + 1 prep" or "2 deliver + 2 travel"), then a subtotal for each budget month and a grand total. Keep each budget month separate; the grand total is a planning sum, not transferable credit. These remain estimates with no approved system total; keep `estimated_credits` separate from `approved_system_credits`.

Estimate a simple base scenario only when the day pattern is evidenced or explicitly hypothetical. Unknown official duration allows a labeled hypothetical sensitivity case, not a course-backed estimate. Extras other than the prep, travel and selected moderator lines above remain unknown, which means an incomplete base estimate with exclusions, not an exact all-in total. No future automation release is assumed to reduce cost.

Group demand by actual delivery month and authoritative region/CSL/CSD/account mapping. Use separate month rows; month totals are not transferable credit. No rollover or cross-region/CSL transfer is assumed. Within-CSL CSD adjustments require authorized evidence. Cross-region teaching is not budget transfer. Unknown budget yields unknown feasibility even if the demand arithmetic is known.

Preserve ledger definitions: the baseline maps Draft to Committed, beyond Draft to Allocated and Completed to Utilized. A locally drafted recommendation is not a system Draft record or a commitment. Do not treat Credits Consumed from Budget as net utilization because it can include all statuses and omit cancellation effects. Reconcile actual completed utilization and returns/losses with the authoritative ledger.

## Scheduling and registration baseline

T means the relevant delivery start in the approved operational calendar. These are independent controls, not interchangeable deadlines.

| Baseline control | Implementation consequence |
| --- | --- |
| Standard PD request five to ten weeks before T | Derive each wave's window from its own current proposed date. A two-week QuickStart does not waive this window. |
| Approval within five business days; Scheduling handoff at least four weeks before T | Allow for the actual business calendar and approver capacity. Never promise approval timing. |
| Publication no earlier than 60 days before T | This skill does not publish. Include the limit in the authorized handoff checklist. |
| Rescheduling honors the five-week SLA; under six business days before original T cancels unless exception approved | Propose a human decision, not an automatic reschedule or cancellation. |
| Minimum five registered learners at T minus six business days for applicable standard PD | Count individually registered eligible learners, not invited or estimated attendees. A deficient cohort triggers the authorized exception/reschedule/cancellation review; do not pad it. |
| Two trainers require registrations at least equal to the first trainer's maximum at that checkpoint | Verify the selected class cap. Double Capacity payment alone does not preserve both resources. |
| OE conversion exception by T minus twelve business days | Custom/non-consecutive, in-person/hybrid and restricted cases do not automatically qualify. OE conversion can lose credits. |
| No bulk enrollment or walk-ins | Draft individual-registration instructions only. Do not register on behalf of others. |
| Learner cancellation no later than two business days before the event; ten recommended | Keep this separate from delivery cancellation and PDc recovery. |

Compute calendar-week offsets with current dates and named time zones. Business-day deadlines require a verified weekend/holiday calendar. If that calendar is unavailable, show the formula and a provisional cutoff, clearly unverified, or leave the date unset. Do not wait for a preceding wave to finish when a later wave's request deadline comes first.

## Cancellation conflict and change control

The source's newer PDc FAQ says eligible customer/low-enrollment cancellation at three or more weeks returns credits; the older program policy uses five weeks. Retain both citations and seek Program or REEL determination before a commitment or recovery promise. Do not silently select the favorable rule or reinterpret request lead time as cancellation recovery.

Other baseline distinctions: Draft deliveries and specified program/trainer/data-entry causes return credits; OE conversion loses them; cancellation of one audience on a shared line does not return the day unless all deliveries on that line cancel, subject to policy. Rescheduled credits move with delivery month, which requires new monthly feasibility review. Extra approved days need a new AER through authorized roles. The advisor never executes these changes.

Any material change to content, audience, language, time zone, modality, environment, month or dates reopens its dependent gates. Record old/new values, reason, evidence, owner and impacted approvals. No approval is silently carried to a new scope.
