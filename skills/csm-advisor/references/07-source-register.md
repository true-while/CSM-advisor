# Source Register and Transformation Notes

## Authoring source

**S-PLAN:** Signal-led Customer Skilling - Detailed Program and Operating Plan.docx, proposed operating design version 0.2. This specification uses the authorized read-only normalized extraction of the saved source at **2026-11-11T16:07:16Z**, containing 18 sections and 30 tables. The incorrect native table of contents was omitted from the extraction. Source content was not changed, and its document package is not a template for the new document.

The source is design authority for this transformation, not proof of present-day catalog eligibility, budget, staffing or policy approval. The identifiers and snapshot date above are provenance, not runtime parameters.

**S-INTAKE:** CSM-Curated-Delivery-Intake-Checklist.docx, owner Gauthier Choquet, supplied in chat on 2026-11-11 from his OneDrive. It is a collaboration aid for curated delivery scoping calls, optional, tuned for Public Sector and Education engagements. Its wording was normalized (no contractions or em dashes) with meaning preserved, and it is used for reference 08. It is design input, not evidence of any customer answer, feature availability or approval.

## Traceability map

| Proposed file | Governing source sections | Transformation |
| --- | --- | --- |
| SKILL.md | 1, 3, 4, 11, 14, 15 | Convert narrative intent into bounded trigger, workflow and read-only guardrails. |
| references/01-contracts-and-evidence.md | 2, 3, 11, 13, 16 | Define typed fields, evidence states, freshness and capability fallbacks. |
| references/02-decisions-and-journeys.md | 4, 5, 8, 11 | Make route/ring choices and relative journey dependencies explicit. |
| references/03-package-library.md | 6, 7 | Preserve eight outcomes, entry/exit gates and exclusions without fabricated catalog mappings. |
| references/04-delivery-and-policy.md | 6, 9, 10, 12, 17, 18 | Convert policy summaries into runtime-validation gates and state rules. |
| references/05-output-contracts.md | 11, 13, 16 | Separate internal and customer views; define reusable output records. |
| references/06-validation-and-handoff.md | 14, 15, 16 | Add observable planned tests and a future installation checklist. |
| references/08-intake-checklist.md | S-INTAKE Parts 1 to 4 | Convert the checklist into a typed intake contract with field states, a minimum-to-start rule, an intake gap list and sector gates. |

The contract names, explicit unknown/effective-status fields, capability adapters and test IDs are proposed authoring designs. They are not current Microsoft APIs or policy terminology. The read-only execution boundary is deliberately tighter than the broader operating plan.

## Upstream references recorded by the operating plan

These internal addresses are traceability pointers, not fresh retrievals performed during this conversion. Reopen them only through permitted access. Do not place them in the customer-view draft.

**S-PDC:** PDc FAQ. The source recorded last-saved metadata of 22 October 2026 and relevant PDc 2.0 updates dated 15 October. Relevant sections include the rate card, planning, Days and Quantity, prep/travel, moderator, second resource, delivery statuses, cancellation, monthly budget and transfer scenarios. Both cancellation conflict and inconsistent launch-day references require owner review.

https://microsoft.sharepoint.com/teams/TrainingProgramManager/Shared%20Documents/General/Field%20Resources/TPM%20FAQs/PDc%20FAQ.docx

**S-POLICY:** FY26 ESI Program Policies.docx. The source reported an FY23 internal title, ambiguous opening date 03/06/2026 and last-saved metadata of 14 May 2026. Relevant sections are private-delivery scheduling/rescheduling/cancellation, low-attended classes, learner cancellation/no-shows, walk-ins, bulk enrollment, unauthorized content, class limits and confidentiality. Preserve the naming/date ambiguity; do not infer a definitive revision from the filename.

https://microsoft.sharepoint.com/teams/EnterpriseSkillsInitiative600/Shared%20Documents/ESI%20GTM/FY24%20GTM%20Resources/MPF%20and%20Policies/Policies/FY25/FY26%20ESI%20Program%20Policies.docx

Owner follow-up references recorded in that source: https://aka.ms/esislas and https://aka.ms/ESIClassCapacities

**S-CATALOG:** ESI catalog. As of November 2026 the authoritative runtime source is the esiadmin Dataverse environment, table `msdyn_incidenttype` (Catalog Items), read-only through a SQL SELECT against target `esiadmin`, filtered to statecode = 0, statuscode Active and esi_isattindicator = true. Authoritative fields: msdyn_name, esi_title, statuscode, esi_isattindicator, esi_pdceligible (the PD = Yes gate), esi_standardduration and msdyn_estimatedduration (minutes), esi_viltminimumcapacity and esi_viltmaximumcapacity, esi_deliverytypessupported, esi_catalogitemtype, esi_externalurl, msdyn_description and esi_audienceprofile. Example facts were verified on November 11, 2026 (see reference 04); they are examples only and must be revalidated on each run. PD = Yes remains the user-defined authoritative eligibility gate for this design. If the esiadmin read is denied or fails, mappings stay pending with no permission escalation.

Secondary source: the Power BI "ESI Catalog - Report" below. It was resolved during the earlier plan work, but metadata/model reads were denied under Read-only access, and the user can only read it without Build permission. Use it only when the esiadmin read is unavailable and an authorized export exposes the required fields.

https://msit.powerbi.com/groups/me/reports/70feecbd-3e22-4ad6-8025-b125088db249/bdf9dfc74090d905a945?experience=power-bi

**S-CAPACITY:** MTTM-Dashboard, Trainer Team workspace, Booking Year View. Earlier reads were filtered unaccounted-day signals; dataset refresh was not verified. They were not qualified slots, holds, PDc or employee-performance measures.

https://msit.powerbi.com/groups/me/reports/5b42a6b6-e7ef-4686-876d-96df4f991dc8/71140f1e27448172e1bc?experience=power-bi

**S-AVAILABILITY:** AMS MTT trainer bench and calendar free/busy. The bench is resolved at run time from the org chart under Erin Jacobsen (erinj@microsoft.com); at the November 2026 baseline it held about 35 trainers across the teams of Renato Strianese, Peter O'Keefe, Tracey Carisch and Gauthier Choquet. Free/busy reads are indicative availability only, not qualification, holds or bookings. Trainer names and calendar classifications are internal only.

**S-PDCRULE:** PDc estimating rule supplied and approved by the skill owner, Gauthier Choquet, on November 11, 2026: 1 PDc per trainer delivery day, plus 1 prep PDc per virtual delivery line, plus 2 travel PDc per in-person delivery, with worked examples of 5 PDc for a 3-day in-person CIE immersion and 4 PDc for a 2-day on-site immersion. It is a planning estimate rule, not an approved system calculation.

**S-DECK:** User-linked presentation. Content and title were not read because sensitivity-label verification failed. No slide content is reconstructed or attributed in this specification. A future authorized readable copy may be reconciled as a separately logged change.

## Historical data exclusion

The operating plan's November 2026 and January-to-March 2027 capacity snapshots, named-team counts, fixed pilot launch/wave dates, proposed percentage triggers, fixed freshness intervals, hold-expiry suggestion and illustrative teaching-day estimates are not installed as defaults. Its missing April rows support an unknown-coverage test only. No capacity totals are copied into the package library. The November 11, 2026 catalog example facts, the AMS bench size and team list are recorded as dated examples and a search scope, not defaults. Fresh runtime scope, dates, filters, definitions, budgets and operational records must govern every actual recommendation.

## Authoring standard

The core uses the Agent Skills specification at https://agentskills.io/specification: name and description required; only name, description, license, compatibility, metadata and allowed-tools are permitted top-level keys. This draft uses only name, description and a flat string-valued metadata map. The directory matches the lowercase hyphenated name. The description is kept below the hard 1,024 UTF-16-unit limit. No allowed-tools field is supplied because tool availability and permission have not been bound. Omission is not a permission grant.
