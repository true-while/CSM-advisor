# Output Schemas and Reusable Templates

## Output contract

Use the logical contract version `skilling-advisory/1.0`. The following field lists are required record shapes, not a claim that an API or database exists. Render as concise Markdown or an explicitly requested new draft file. Null plus a reason is preferable to invented precision.

```text
AdvisoryResult {
  schema_version, run_id, initiative_id, case_id?, plan_version, skill_version,
  generated_at, run_timezone, requested_view,
  scope, decision_requested, result_state, executive_summary,
  evidence_coverage[], cohort_decisions[], package_designs[],
  delivery_scenarios[], monthly_ledger[], gates[], value_plan,
  next_actions[], sources[], change_log[], action_boundary,
  customer_draft?
}
```

`result_state` is `intake_only`, `proposed`, `conditional`, `blocked` or `reviewed`. Reviewed means evidence has been reviewed, not delivery approved. State the affected scope if one cohort is blocked and another remains designable. `action_boundary` always states that no delivery, hold, approval, registration, sending, submission, installation or automation was performed.

Empty scenarios or ledger arrays are permitted only when delivery is out of scope, with an explicit reason. If delivery is discussed but unknown, include rows with nulls and gates. Do not omit unfavorable results or unknowns.

### Required child records

| Record | Fields |
| --- | --- |
| CohortDecision | cohort_id, outcome, current_behavior, route or conditional_routes, route_status, evidence_ids, confidence/reason, alternative, rings, overlap_status, readiness_dependencies, transfer_conditions, learning_path_selection? |
| LearningPathSelection | primary_path or conditional_paths, priority_reason, evidence_ids, audience, intended_task, intended_outcome, assessment, prerequisite_if_needed, alternative_considered, transfer_condition, gate_ids |
| PackageDesign | package_id/version, cohort_id, outcome, objectives, entry_gates, proposed_sequence, customer_practice, assessment, mapping_ids, exclusions, exit_evidence, owner_role |
| DeliveryScenario | scenario_id, wave_id, cohort_id, package/mapping versions, proposed_topic, proposed_block_length, official_duration/unit, planned_hours, proposed_week, date/window, teaching_zone, language, modality, capacity_option_id/state/as_of, prep/travel/extras, assumptions, tradeoffs, classes_per_day?, official_class_length?, max_seats_per_class?, daily_seat_capacity?, core_team_assignment? |
| TrainerAvailability (internal only) | trainer, team/manager, home_timezone, local_teaching_window, late_window_flag, per_day_free_busy, classification (`clear_all_days`, `tentative_holds_only`, `partly_free` or `not_free`), already_supports_customer, proposed_role (`core_first_wave`, `core_scale_or_second_track` or `reserve`), qualification_status, read_at, source_id |
| Gate | gate_id, scope, domain, state, blocking_effect, evidence_ids, reason, owner_role, next_action, due_date or relative_checkpoint, closure_evidence_required |
| MonthlyLedgerLine | line_id, scenario_id, month, region/CSL/CSD/account anchor, line_type, mapping_id, Days, Quantity, estimate_basis, built_from, estimated_credits, approved_system_credits, extras, moderator_status, source_budget_position, feasibility, approval_ref, exclusions |
| NextAction | action_id, proposed_action, owner_role, dependency, deadline_basis, evidence_needed, execution_status=`not_performed` |
| Source | source_id, title, locator, section/record, evidence_class, scope/filters, observed/retrieved/refreshed/effective timestamps, currentness, limitation, permitted_audience |
| Change | version, prior_version, changed_fields, reason, evidence_ids, authoring_timestamp, review_owner, impacted_gates, approval_status |

### Learning-path detail and compatibility

The DeliveryScenario capacity fields, the TrainerAvailability record and the MonthlyLedgerLine built_from and moderator_status fields are additive in skill version 0.4.0-draft; the logical contract remains `skilling-advisory/1.0`.

Retain `skilling-advisory/1.0` and existing route/package identifiers. `learning_path_selection` is an additive optional child of `CohortDecision`, not a new root field or route. Include it for new recommendations. A legacy renderer that cannot accept it must preserve the same detail in the existing outcome, confidence/reason, alternative, readiness_dependencies and transfer_conditions fields, with the primary path visibly named. Do not silently drop the decision detail.

`primary_path` is `feature_based` or `persona_based`. If evidence is insufficient, leave it null with a reason and list the two conditional candidates. Mixed needs retain one primary path for each coherent cohort, with an evidenced prerequisite or separate cohort decisions, not a third path. A blocked activity may retain a provisional learning preference, but its failed/pending gates and required closure evidence remain visible. Cite internal evidence IDs and gate IDs; customer views use only permitted, plain-language evidence summaries and readiness conditions.

Gate domains include purpose/privacy, outcome/cohort, access/environment, catalog, official format, qualification, capacity, lead time, budget, registration, policy, content permission and approvals. Gate states are `passed`, `pending`, `failed`, `conflicting` or `not_applicable`. No absence of evidence can produce passed.

## Template A: Internal decision brief

**Draft advisory plan: {initiative_id}, version {plan_version}**

- As of: {generated_at}, report zone {run_timezone}. Teaching zone: {known value or unknown}.
- Decision: {bounded decision}; scope: {customer alias and cohorts}.
- Recommendation: {route/package or conditional options}, because {evidence-backed reason}.
- Learning-path priority: {feature/app or persona/role, or conditional}; audience: {role group}; task/outcome: {intended application}; reason/evidence: {observed gap and source anchors}.
- Assessment and alternative: {task or workflow rubric}; {alternative, targeted prerequisite if needed, transfer condition and gates}.
- Confidence: {level and limitation}. Delivery feasibility: {state and open gates}.
- Alternative considered: {option and tradeoff}.
- Next decision: {owner role, evidence needed and relative or verified date}.
- Actions performed: evidence review and draft preparation only. Nothing sent, booked, submitted or activated.

**Intake summary** (include when the run started from a scoping call, intake notes or a curated delivery request):

- Intake source: {scoping notes or checklist, date, who supplied it} [S-INTAKE field definitions].
- Part 1 essentials: {count captured or customer-confirmed} of 11; unknown with owner: {fields}; conflicting: {fields}.
- Part 2 recommended: {captured fields}; open: {fields}.
- Sector: {Public Sector or Education or other}; sector gates: {gate, state, effect on features, demos, hands-on activities, audiences or dates}.
- Minimum to start curation: {met or not met}; if not met, see the intake gap list (Template F).
- Part 3 routing: {roles only; internal}.

| Cohort | Outcome and signal | Route/package | Primary learning path and task | Ring handoff | Evidence/confidence | Alternative/transfer and gates |
| --- | --- | --- | --- | --- | --- | --- |
| {cohort_id} | {outcome; observed versus assumed} | {candidate and version} | {feature/app or persona/role; assessment} | {dependencies} | {source anchors; reason; limitations} | {alternative; condition; gate state; owner; next action} |

## Template B: Internal MTTM runbook

| Wave | Proposed topic/week/hours | Verified code/title/PD/active | Official duration and format | Environment and prerequisites | Language/teaching zone | Qualification and capacity evidence | Budget/approval gate |
| --- | --- | --- | --- | --- | --- | --- | --- |
| {wave_id} | {conceptual block, not course facts} | {values or Pending PD = Yes catalog validation} | {value/unit or unknown} | {evidence and blocker} | {values or unknown} | {source state, effective state, timestamp, backup} | {month, system total or unknown, provenance} |

**Trainer availability and continuity (internal only).** Render after the runbook table when delivery days are proposed:

- Bench searched: all AMS MTTs under Erin Jacobsen, resolved from the org chart at {read_at}; {count} trainers; teaching zone {zone}; proposed days {dates}.
- Proposed core team: {trainer A} (first wave, {reason, for example already supports the customer}); {trainer B, if any} (first wave); {trainer C} (scale or second-track trainer). One trainer per delivery day by default.
- Reserve: the wider AMS bench, listed by classification only as needed.

| Trainer | Team | Local window and late flag | Free/busy per proposed day | Classification | Proposed role | Qualification status |
| --- | --- | --- | --- | --- | --- | --- |
| {name} | {manager} | {local start and end; late or not late} | {day: free, tentative or busy} | {clear all days, tentative holds only, partly free or not free} | {core first wave, core scale or second track, reserve} | {unverified unless evidenced} |

Always add the gate "confirm course qualification and later-wave calendars" with an owner role. Free/busy is indicative only; it is not qualification, a hold or a booking.

Link each wave to its cohort learning-path decision and intended task/outcome. A generic learning theme is not a verified catalog title. Keep validated catalog mapping, official duration, time and monthly PDc internal; deduplicate overlapping learning across lenses.

Preserve separate detail for prep/travel, content permission, registration minimum and class cap, business-calendar checkpoints, approval scope and the actual completion anchor. Include hold owner/expiry or confirmation ID only when fresh authorized existing evidence permits it. Personnel data stays in the restricted internal record and is minimized.

## Template C: Monthly PDc scenario ledger

| Month and budget anchor | Line/wave and modality | Days | Quantity | Est. PDc | Built from | Moderator | Extras or unresolved calculation | Approved system total | Source budget/feasibility | Approval source |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| {month; region/CSL/CSD} | {wave; virtual or in person} | {trainer delivery days or unknown} | {audience links} | {whole-credit estimate or unknown} | {for example "3 deliver + 1 prep" or "2 deliver + 2 travel"} | {not included, or selected: +1 per trainer delivery day} | {other dependencies or none} | {value or unknown} | {source-defined position or unknown} | {record or pending} |
| **{month} subtotal** | | {days} | | {Est. PDc} | | | | | | |
| **Grand total (estimate)** | | {days} | | {Est. PDc} | | | | | | |

Apply the reference 04 estimating rule: 1 PDc per trainer delivery day, plus 1 prep PDc per virtual delivery line, plus 2 travel PDc per in-person delivery. If prep was added to an in-person line, note that the user confirmed it. Keep each budget month separate with its own subtotal; the grand total is a planning sum, not fungible or transferable monthly credit. Reconcile every source category and show exclusions. Every value is an estimate; a hypothetical estimate is not a commitment or system total.

## Template D: Customer-view draft

Generate this as a separate allowlisted view, not as a redacted copy of an internal attachment. Do not include an internal source annex, hidden notes, comments, tracked text or metadata containing restricted fields. Label it **Draft for review; delivery arrangements subject to confirmation** unless the particular external confirmation is evidenced.

1. **Your objective:** {business process, desired improvement, agreed success concept}.
2. **Recommended journey:** {primary app-focused or role-focused learning theme, audience, evidence-backed reason and intended task/outcome; conditional options when the gap is unknown}. Use generic proposed learning labels, not course codes or claims that an illustrative label is an official class.
3. **People and readiness:** {customer role groups, prerequisites, access and customer commitments}.
4. **Learning and application:** {permitted themes, customer-owned practice, task/workflow assessment, expected outputs and support boundaries; a small prerequisite only when justified}.
5. **Milestones:** {proposed dates or verified external confirmation, named local time zone, readiness and decision checkpoints}.
   **Proposed delivery days and capacity:** frame each day as a proposed day set aside for the customer, not a booking. For each day, state the number of classes, the official class length from the catalog and the maximum seats per class (for example "2 classes, 1 hr each, up to 200 seats"), then a daily capacity line (for example "200 seats per class, each run twice, so up to 400 people per day"). Scale-out waves also show class length and seat limits. Use only catalog-evidenced lengths and seat limits; otherwise write "class length and seat limit to be confirmed".
   **Please confirm by {stated date}:** which classes to keep, expected seats per class, program contact, champions lead, licenses and dates to avoid.
6. **Participation:** {individual-registration process or future confirmation, practice time and accessibility support}.
7. **Success measures:** {approved cohort-level measures, baseline and completion-relative reviews}.
8. **Next decision:** {alternative learning focus, evidence-based transfer condition, customer action and readiness gates needed to continue, adjust, broaden or close}. Neither path is a compulsory stage.

Exclude course codes, internal PD flags/mapping discussions, PDc estimates, credit balances and internal budgets, trainer names and other personnel data, qualification records, internal policy language/links, restricted source IDs and unapproved claims. Replace an internal operational blocker with neutral truthful wording such as "Delivery details remain subject to confirmation." Do not conceal a customer-facing readiness issue. Include only customer-shareable citations that support a claim. If the source cannot be shared, restate the conclusion without exposing it and seek review; do not invent a public citation. No message or document is distributed by this skill.

## Template F: Intake gap list

Use this when one or more reference 08 Part 1 essentials, or required sector fields, are missing. A gap list replaces a guessed value; it does not stop the design work that does not depend on the missing field.

**Internal version** (for the CSM and trainer; may name roles and decisions):

| Field | Part | State | Why it matters (decision fed and what stays blocked) | Exact customer prompt | Owner | Due or checkpoint |
| --- | --- | --- | --- | --- | --- | --- |
| {field} | {1, 2 or 4} | {unknown or conflicting} | {decision fed; blocked activity} | "{prompt from reference 08}" | {internal role} | {relative checkpoint or verified date} |

**Customer-safe version** (prompts only):

Title it **Questions to confirm before we finalize your session**. List the exact customer prompts as a numbered list, grouped by topic if helpful. Do not include owners, internal decisions, account team or stakeholder names, Skilling Insights hub data, course codes, budgets or internal gate language. This skill drafts the list only; it does not send it.

## Template E: Value review

| Field | Required entry |
| --- | --- |
| Exposure | Cohort, package version, actual relevant delivery or multi-day completion, later exposures and anchor source |
| Baseline/follow-up | Definition/version, window, numerator/denominator, sample and exclusions, source refresh |
| Results | Readiness, learning, behavior and business outcome reported separately; missing evidence explicit |
| Comparability | Population, license, product, process, seasonality, instrumentation and concurrent intervention changes |
| Interpretation | Observed difference, uncertainty, qualitative corroboration and alternative explanations |
| Decision | Continue, route transfer, pause or close, with owner and evidence required |

Set 60-day and 90-day observation anchors as calendar-day offsets from actual relevant completion. A proposed meeting can move to a suitable business day without changing the observation window. Do not book it. With multiple waves, keep distinct exposure cohorts; do not grant a later wave the earlier wave's maturity.

If a rate is valid, calculate numerator divided by denominator; disclose the denominator and missing assessments. Do not divide by zero. A baseline-to-follow-up difference is directional evidence, not proof of causation. Time potentially released is not cash realized without customer-validated redeployment or avoided-cost assumptions. Training list price is never customer value. Do not assess individual employee or trainer performance.

## Citation and final-review rules

For every operational fact, numeric claim, constraint and decision-critical assertion, cite the source title/record and section, observation period and as-of time. Use local evidence IDs such as [S-01, section 9] in the internal draft and provide the resolving source register. Label source summaries as source summaries, not fresh direct verification. Never invent a page number, slide, refresh time, denied query result or approval citation.

Before returning, check that the primary learning path follows the evidenced gap, the audience/task/assessment and alternative/transfer/gates are explicit, no automatic route-to-lens mapping or mandatory double path was introduced, and no illustrative label became a catalog or availability claim. Then check proposed versus verified wording, no inherited old dates or budget, eligibility and duration, month/day arithmetic, duplicate populations/snapshots, privacy, citation resolution and the action-boundary statement. Write no contractions or em dashes. A file output remains a new review draft; source material and personal skills remain unchanged.
