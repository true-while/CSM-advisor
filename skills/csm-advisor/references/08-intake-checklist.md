# Curated Delivery Intake Checklist Contract

## Purpose and status

This reference turns the Curated Delivery CSM Intake Checklist [S-INTAKE] into a typed intake contract for this skill. The checklist is a collaboration aid. It is optional, it is intended to speed trainer curation and SWR approval and to reduce back-and-forth, and it is tuned for Public Sector and Education engagements. Using it does not create an approval, a booking, a curation commitment or a customer record.

Read this reference for every run that starts from a scoping call, intake notes or a curated delivery request. Use it to do three things:

1. Map captured answers into the skilling design and record a state for every field.
2. When Part 1 essentials are missing, return an intake gap list with the exact customer prompts to ask, never a guessed value.
3. Apply the Public Sector and Education constraints as gates on which Copilot features, demos, hands-on activities, audiences and dates are allowed.

## Field value states

Every intake field carries exactly one state. Each captured value also uses the `Evidence<T>` wrapper from reference 01, with the source anchor (for example, scoping call notes and date) and the person who stated it.

| State | Meaning | Effect |
| --- | --- | --- |
| captured | Recorded from scoping notes or an internal source, not yet confirmed by the customer | Usable as a proposed input; label it as captured, not confirmed. |
| customer-confirmed | Stated or confirmed by an authorized customer contact | Usable as a customer-confirmed input. It does not verify program policy, catalog eligibility or feature availability. |
| unknown | Not asked, not answered or not recorded | Name an owner and the exact prompt. A Part 1 unknown blocks curation unless it is explicitly marked unknown with an owner. |
| not applicable | Does not apply to this engagement (for example, Education fields for a Public Sector customer) | Record the reason. Never use it to hide a missing answer. |
| conflicting | Two sources or two contacts disagree | Show both values with sources. Do not pick one silently. Route to the owner for resolution. |

## Part 1: Essentials that trigger the curation

These fields feed the trainer Curation Prompt and decide which slides and demos make it into the deck. All are required.

| Field | Customer prompt | Requirement | Decision fed |
| --- | --- | --- | --- |
| Topics / skilling scope | "Which products and topics should the session focus on?" | Required | Scope, package selection (reference 03) |
| Delivery channel | "In person or Teams?" | Required | Delivery feasibility and format (workflow step 7) |
| Audience type | "Who is attending: executives, business users, IT pros, or end users?" | Required | Ring assignment: executives to sponsors and leaders, IT pros to technical, business users to champions and advocates or end users depending on role in the rollout, end users to end users |
| Persona / function | "Which teams are they from: Sales, Operations, Finance, HR?" | Required | Persona/role lens evidence (workflow step 5). Job responsibilities and workflows only, never protected traits |
| Industry | "What is your industry or segment?" (for example, Public Sector: federal, state, local; or Education: K-12, higher ed) | Required | Sector gates (Part 4 and the gate table below) |
| Session length | "How much time do we have: 60 or 90 minutes, half day, or full day?" | Required | Delivery format (step 7). Never compress or split an official course to fit; flag an exception instead |
| Copilot licensed | "Does the team already have Microsoft 365 Copilot licenses?" (Yes / No) | Required | Readiness state and feature/app lens evidence. No license means an access or readiness gap, not a skilling gap |
| Key objectives | "What should people be able to do when they walk out?" | Required | Scope, package selection, intended task and assessment |
| Engagement | "What type of engagement do you want during the delivery?" | Required | Delivery format and customer practice design (steps 5 and 7) |
| Out-of-scope topics | "Is there anything we should deliberately leave out?" | Required | Package exclusions |
| Session schedule | "What date, start and end time, and time zone, and any breaks?" | Required | Dates and feasibility (step 7), using the customer teaching time zone. A missing time zone blocks exact local times, not relative planning |

## Part 2: Recommended to sharpen the fit and speed sign-off

These fields are recommended. They are not required to start curation, but an unknown value is still recorded with its state.

| Field | Customer prompt | Requirement | Decision fed |
| --- | --- | --- | --- |
| Success criteria | "How will you measure success: adoption, a feedback score, a business outcome?" | Recommended | Baseline and value loop (step 8). Use it as the starting measurement definition, then agree the baseline, denominator and window |
| Constraints / sensitivities | "Any compliance, NDA, environment, or timing constraints we should respect?" | Recommended | Readiness gates |
| Prerequisites / assumptions | "What will attendees already have: accounts, tenant access, tools, labs ready?" | Recommended | Readiness state and feature/app lens evidence |
| Challenges / blockers | "Any known risks: access issues, technical blockers, tight timing?" | Recommended | Readiness gates |
| Follow-up expectations | "What should we answer or share afterward, and what are the next steps?" | Recommended | Next actions and the 60-day and 90-day review |

## Part 3: People and context

These fields help the trainer route the request and reference the right skilling data during approval. They are internal only.

| Field | Content | Requirement | Decision fed and handling |
| --- | --- | --- | --- |
| Customer stakeholders | Primary contact, decision maker, technical owner, sponsor, escalation contact | Recommended | Internal routing and gate owners. Record roles; keep names to the minimum needed. Never in the customer view |
| Account team | AE, CSA, SSP, CSM, and any partner contact supporting the workshop | Recommended | Internal routing only. Never in the customer view |
| Skilling Insight | Relevant data from the Skilling Insights hub (aka.ms/skillinginsightshub) | Recommended | Internal evidence for route, ring and lens decisions. Cite it in the internal register with retrieval time and scope. Keep it out of customer output |

Apply data minimization: record a role when a role is enough, and do not copy contact details into the design.

## Part 4: Sector focus

Most delivery-shaping constraints come from the cloud environment, compliance rules and who is allowed in the room. Ask the questions that apply. They often decide which Copilot features and demos can be used, so flagging them early avoids a curation redo. Mark the other sector as not applicable.

### Public Sector

| Field | Customer prompt | Requirement | Decision fed |
| --- | --- | --- | --- |
| Cloud environment | "Are you on commercial cloud, or GCC, GCC High, or DoD?" | Required when Industry is Public Sector | Sector gate: which Copilot features and demos are available |
| Copilot availability | "Is Microsoft 365 Copilot enabled in that environment yet?" | Required when Industry is Public Sector | Sector gate: availability differs across GCC High and DoD |
| Compliance frameworks | "Which frameworks apply: FedRAMP, CJIS, IRS 1075, or ITAR?" | Recommended | Customer-stated constraint on demo data and scenarios |
| Data residency / sovereignty | "Any data residency, sovereignty, or in-country hosting requirements?" | Recommended | Customer-stated constraint on demo data, labs and delivery location |
| Access and security to deliver | "Any badging, clearance, or network limits for joining in person or remotely?" | Recommended | Delivery channel feasibility |

### Education

| Field | Customer prompt | Requirement | Decision fed |
| --- | --- | --- | --- |
| Segment | "K-12, higher education, or vocational / community college?" | Required when Industry is Education | Sector gate: eligibility and audience |
| Audience | "Faculty, staff, IT, or students?" | Required when Industry is Education | Sector gate: drives Copilot eligibility; ring assignment |
| Copilot and learner age | "Will under-18 students attend, and which licenses are in place: A1, A3, or A5?" | Required when students may attend | Sector gate: hands-on Copilot activities |
| Student-data privacy | "Any FERPA or student-data rules that affect the demo data we can use?" | Required when student data could appear | Sector gate: demo data |
| Academic calendar | "Any term, exam, or semester timing that constrains the date?" | Recommended | Dates and feasibility (step 7) |

## Minimum to start curation

Curation can start only when every Part 1 essential is captured, customer-confirmed, or explicitly marked unknown with a named owner. The sector fields marked required for the stated industry follow the same rule.

When an essential is missing, do not guess a value. Return an intake gap list with one row per missing field:

| Column | Content |
| --- | --- |
| Field | The checklist field name |
| Why it matters | The decision it feeds and what stays blocked |
| Exact customer prompt | The prompt text from this reference, unchanged in meaning |
| Owner | The internal role who will ask it (usually the CSM) |

A gap list does not stop useful work. Continue with the parts of the design that do not depend on the missing field and label them provisional. Render the internal and customer-safe versions with reference 05.

## Sector gate table

Apply these gates before proposing features, demos, hands-on activities, audiences or dates. A gate that is unknown stays pending; it never becomes passed by default.

| Sector | Input | Gate rule | Effect when unknown or failed |
| --- | --- | --- | --- |
| Public Sector | Cloud environment (commercial, GCC, GCC High, DoD) | Decides which Copilot features and demos are allowed. Availability must come from current authorized evidence or customer confirmation for that exact environment. Never assume parity with commercial cloud | Feature-specific demos and hands-on activities stay conditional; keep theme-level design |
| Public Sector | Copilot enablement in that environment | Propose Copilot hands-on activities only when enablement is evidenced or customer-confirmed | Treat as an access or readiness gap, not a skilling gap |
| Public Sector | Compliance frameworks and data residency | Record as customer-stated constraints on demo data, scenarios, labs and location. The skill does not certify compliance | Use only synthetic or customer-approved demo content; route compliance questions to the owner |
| Public Sector | Badging, clearance, network limits | Affect delivery channel feasibility for in person or remote attendance | Delivery channel stays conditional |
| Education | Segment and audience | Drive Copilot eligibility and ring assignment | Keep audience-specific Copilot content conditional |
| Education | Under-18 student attendance and A1, A3 or A5 licensing | Confirm both before proposing any Copilot hands-on activity for students | No student hands-on Copilot activity; faculty, staff or IT design can continue |
| Education | FERPA or student-data rules | Demo data must be synthetic or customer-approved. Never use real student data | Default to synthetic demo data |
| Education | Academic calendar | Constrains proposed dates around terms, exams and semesters | Dates stay relative or provisional |

## Mapping summary

| Checklist input | Skill decision |
| --- | --- |
| Topics, key objectives, out-of-scope topics | Scope, package selection and exclusions |
| Audience type | Ring assignment: sponsors and leaders, technical, champions and advocates, end users |
| Persona / function | Persona/role lens evidence, based on job responsibilities and workflows only |
| Copilot licensed, prerequisites | Readiness state and feature/app lens evidence; no license is an access or readiness gap |
| Delivery channel, session length, session schedule, engagement type | Delivery feasibility, format and dates in the customer teaching time zone; official courses are never compressed or split |
| Success criteria | Starting measurement definition for the baseline and value loop |
| Constraints, challenges and blockers | Readiness gates |
| Follow-up expectations | Next actions and the 60-day and 90-day review |
| Industry and Part 4 | Sector gates |
| Part 3 people and Skilling Insight | Internal routing and internal evidence only |

## Guardrails for intake

- Intake answers are evidence, not approvals. A customer answer does not verify catalog eligibility, feature availability, capacity or policy.
- Do not fill a missing essential from an industry default, a prior engagement or a job title.
- Keep Part 3 contacts and Skilling Insights hub data internal. The customer-safe gap list contains prompts only.
- Never use real student data or regulated data in a proposed demo.
