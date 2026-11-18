# Input, Evidence and Capability Contracts

## Contract purpose

This reference defines a typed logical business contract, not a tool schema, plugin manifest or deployed database. An adapter may implement these records in an approved platform later. Until then, use the same field names in a controlled draft document. Store personal membership data separately from aggregate plans.

### Type notation

`string` is nonempty text. `id` is an opaque source identifier or explicitly draft-local identifier. `date` is ISO 8601 YYYY-MM-DD. `datetime` is ISO 8601 with offset or Z. `month` is YYYY-MM in the authoritative delivery-month convention. `integer` is a whole number. `decimal` is a finite number, never NaN. `T?` allows null. `T[]` is a list. Enums contain exactly the named values. Never use an empty string, zero or false to mean missing.

Required means that the field must exist in the run record. Null remains valid when paired with a reason, affected gate and next action. No schema field alone creates an approval or source-system record.

## Run envelope

| Field | Type and requirement | Validation and missing-data behavior |
| --- | --- | --- |
| schema_version | string, required; `skilling-input/1.0` | Version the contract separately from the skill and package versions. |
| run_id | id, required | Unique draft-local identifier for this execution. Do not imply a CRM case was created. |
| initiative_id | id, required | Reuse a verified initiative ID when supplied. Otherwise prefix a local identifier with `draft-`; disclose its status. |
| case_id | id?, optional | Preserve an authorized related case reference, without opening or changing that case. |
| parent_plan_version | string?, optional | Identify the prior plan when revising. Its approvals do not automatically transfer. |
| run_at | datetime, required | Obtain the actual runtime timestamp. Do not copy the source-document date or a test fixture into a real run. |
| run_timezone | string, required | Use a verified requester zone; otherwise use UTC for report generation only and disclose it. |
| requested_view | enum, required | `internal`, `customer` or `both`. Default internal only for an authorized internal planner. Unknown audience means no restricted annex. |
| customer_scope | Evidence<string>, required | Account or approved alias, allowed environment/tenant and initiative boundary. Do not search across unrelated accounts. |
| business_outcome | Evidence<string>, required | Process, desired behavior and success concept. If absent, produce an intake draft rather than select a final package. |
| decision_requested | string, required | Example: route selection, wave comparison or value review. Keep one bounded decision chain. |
| delivery_constraints | DeliveryConstraints, required | Fields may be unknown. Missing teaching zone blocks exact local times, not relative planning. |
| cohorts | Cohort[], required | At least one bounded cohort for a definitive recommendation; otherwise return discovery only. |
| evidence | Evidence[], required | Include supplied evidence and source limitations. An empty list means an assumptions-only result. |
| approvals | ApprovalEvidence[], required | Empty by default. Never infer acceptance from silence or a role title. |
| privacy | PrivacyContract, required | Purpose, allowed audience, minimum aggregation, retention and access owner; unknown limits prevent sensitive-data collection. |

### Reusable evidence wrapper

Every decision-bearing value uses the following logical structure. Lists may share an envelope only when all entries have identical provenance and scope.

```text
Evidence<T> {
  evidence_id: id
  value: T?
  unit: string?
  evidence_class: verified_source_fact | customer_confirmed_input | proposed_assumption
  validation: verified | supplied_unverified | proposed | unknown | stale | denied | conflicting | not_applicable
  confidence: high | medium | low | not_assessable
  confidence_reason: string
  source_id: id?
  source_locator: string?
  source_section_or_record: string?
  source_owner_role: string?
  observed_at: datetime?
  observation_start: date?
  observation_end: date?
  retrieved_at: datetime?
  source_modified_at: datetime?
  dataset_refreshed_at: datetime?
  effective_from: date?
  valid_until: datetime?
  recheck_trigger: string?
  scope_and_filters: string?
  sharing_classification: string
  missing_or_conflict_reason: string?
  affected_gates: string[]
}
```

`verified` means that the relevant authorized source was actually read and the field was checked in this run or is still valid under an explicit owner-approved freshness rule. A timestamp alone does not prove current applicability. A customer statement can be customer-confirmed without independently verifying program policy, catalog eligibility or booking authority. Label a calculation as derived and preserve every input evidence ID plus the formula.

High confidence requires relevant, current, attributable evidence and no material unresolved contradiction. Medium means a supported but bounded limitation remains. Low means the recommendation is provisional because important evidence is missing, stale or indirect. Use not-assessable when no defensible conclusion exists. Confidence never overrides an unknown or failed hard gate.

## Cohort and outcome contract

| Record or field group | Required content | Interpretation |
| --- | --- | --- |
| Cohort identity | cohort_id, role description, eligibility definition, inclusion/exclusion rules, owner role | Separate materially different audiences rather than averaging their needs. |
| Participant counts | eligible_unique, assessed, invited, registered and attended, each Evidence<integer?> | Nonnegative; counts represent different populations. Do not use invited as registered. |
| Ring membership | subset of leaders_champions, technical_leads, advocates, end_users; overlap known/unknown | Keep leaders and champions distinct roles within the first ring. Use approved stable pseudonymous IDs only if necessary and permitted for deduplication. |
| Readiness | access, prerequisites, environment, governance, lab compatibility and practice, each ready/conditional/blocked/unknown with evidence | Do not aggregate away a hard blocker. License purchase alone does not prove feature access. |
| Product context | product/capability, exact environment, relevant version, permitted scenario and data, license/access evidence | Do not infer commercial and government environment parity. |
| Metric | metric_id, category, definition/version, numerator, denominator, unit, cohort, window, exclusions, source/refresh, baseline, target, method | Category is readiness, learning, behavior, business_outcome or operational. Missing denominators block a rate. |
| Qualitative signal | dated theme or statement, method, sample/coverage, owner, consent/sharing basis, direct statement or inference | One anecdote is not a population finding. Omit unnecessary names and verbatim sensitive content. |
| Outcome contract | customer process owner, task rubric/version, evidence of useful application, baseline period, target rationale, confounders, review anchor | Business benefit is not the training price or attendance count. |

## Delivery and feasibility contracts

`DeliveryConstraints` includes preferred date windows, fixed versus preferred milestones, named teaching time zone, local start/end limits, teaching language, modality, location if needed, accessibility, blackout dates, applicable business calendar and customer practice capacity. Each decision-bearing item is an Evidence value. Do not infer a teaching zone from a trainer home country. Resolve ambiguous and nonexistent daylight-saving local times before offering a precise schedule.

`CatalogMapping` includes mapping_id, package_id/version, objective, catalog_id, official_title/version, explicit_pd_flag, active_status, official_duration_value/unit, standard_format, language, modality, audience, prerequisites, supported_environment and field-level source evidence. Its state is pending, eligible, ineligible or quarantined. Proposed topics and block lengths occupy separate fields.

`CapacityOption` includes option_id, cohort/wave IDs, time window, mapping_id, qualification evidence, language, teaching zone, modality, live conflict-check evidence, prep/travel dependencies, backup status and capacity state. A report-only option has no invented resource ID. An external hold additionally requires source record, authorized owner and explicit expiry; a confirmed record requires operational booking evidence and approval scope.

`MonthlyBudget` includes region, CSL, CSD, account anchor, submitting program-role mapping, delivery month, source-ledger definitions, authorized allocation, commitments/allocations/utilization/returns/losses as defined by that ledger, available position, adjustment authority, source time and approver. Unknown is not zero. Never subtract overlapping ledger categories without a verified reconciliation definition.

`ApprovalEvidence` includes approval_id, authority role, scope, initiative and plan/package versions, delivery/month, decision, decision_at, expiry or recheck trigger, conditions and source reference. A user statement of approval remains supplied-unverified until the relevant authority and scope can be validated. The skill records evidence; it does not grant approval.

## Intake checklist input contract

`IntakeChecklist` is an optional input contract for runs that start from a scoping call, intake notes or a curated delivery request. Its fields, customer prompts, requirement levels and mapping to skill decisions are defined in reference 08 [S-INTAKE]. Each field carries one state: captured, customer-confirmed, unknown, not applicable or conflicting, and each captured value uses the `Evidence<T>` wrapper above. Intake answers populate `business_outcome`, `delivery_constraints`, `cohorts` and readiness evidence; they never create approvals. Part 3 people and Skilling Insights hub data are internal evidence only and stay out of any customer view.

## Required by decision, not by form length

1. **Intake draft:** require run identity and requested scope; expose absent outcome or cohort. When a scoping intake is in play, return the reference 08 intake gap list for every missing Part 1 essential.
2. **Provisional route:** require outcome, cohort, addressable need and at least dated customer evidence. If uncertain, propose conditional options rather than a definitive classification.
3. **Specific learning mapping:** require the authorized catalog fields and environment/prerequisite compatibility. Without them, keep theme-level package design.
4. **Matched delivery scenario:** additionally require exact qualified content, teaching language/zone, modality, valid date window and current operational checks. Budget is assessed separately and can still block feasibility.
5. **Externally confirmed status:** require actual booking and relevant approvals. Never create this state locally.
6. **Value conclusion:** require a relevant actual exposure/completion anchor, comparable baseline and follow-up, denominators where applicable, and privacy permission. Otherwise produce a measurement plan or a limited qualitative review.

## Source priority and freshness

Apply authority, exact subject, applicability/effective date and scope before recency. A newer file timestamp alone does not supersede governing policy.

- Catalog facts come from the authorized catalog and the authoritative owner for fields it does not contain.
- Credits, allocations and approvals come from the approved program systems and governing policy owners.
- Bookings and holds come from Delivery Ops or the authorized operational booking source.
- Qualifications come from current MTTM-approved qualification evidence for the exact content/version.
- Business outcomes and permitted use come from the customer sponsor, process, technical, data and policy owners within their authority.
- Reports support only the measures, filters, populations and periods actually returned. A visual, metadata timestamp and dataset refresh are different evidence.
- The operating plan is design context and a historical policy summary. It is not live catalog, budget, capacity or approval evidence.
- Public learning resources may support permitted preparatory learning. They do not establish private-delivery eligibility or sovereign environment support.

At each run, record source retrieval time and source effective scope. Ask the owner to define freshness for metrics, qualitative insights and qualifications. Without a freshness rule, disclose age and revalidate decision-critical facts before treating them as current. Recheck catalog on retirement/version changes, budget on a month or scope change, capacity before any operational decision, environment before affected practice, and policy before a commitment handoff. Do not inherit the old plan's proposed 28-day windows, 30-day reconfirmation, percentage thresholds or 48-hour hold default.

## Capability dependency map

The names below are roles, not invented callable tools. Discover the available implementation and permission before use. No dependency is assumed connected.

| Capability role | Minimum authorized result | Safe fallback |
| --- | --- | --- |
| Document read | Label-aware content with title, locator and section/record anchors | Approved readable extract; mark inaccessible sections unread. |
| Catalog read | Explicit PD field and required mapping fields, with refresh/scope | Authorized export with owner attestations for missing fields. |
| Policy read | Governing sections, versions, effective scope and conflicts | Historical snapshot plus an unresolved policy gate. |
| Metrics read | Approved cohort aggregates, definitions, windows and filters | Customer-confirmed evidence and a proposed baseline plan. |
| Qualification/capacity read | Exact qualification and operational candidate checks | Indicative report signal, not a matched resource. |
| Budget read | Monthly authoritative position and approval evidence | Unknown feasibility and conditional demand scenario. |
| Date arithmetic | Current timestamp, named zone and applicable business calendar | Relative windows; no invented business-day cutoff. |
| Draft artifact creation | New requested draft, approved storage and protection | In-chat draft or source text for the document capability. No sharing. |

Preserve tenant security, row-level security, report/page/visual filters and authorized scope. Resolve current filter definitions rather than blindly inheriting FY27 or a named team. Log a user-authorized scope change before comparing results. Batch scoped reads where practical. Do not enumerate whole tenants or retrieve individual records when aggregates suffice.
