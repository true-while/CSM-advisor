---
name: mtt-class-lookup
description: |
  Read-only Microsoft Technical Trainer (MTT) class/delivery lookups from the esiadmin Dynamics 365
  environment: class details, roster, attendance/no-shows, Teams join link & invite, student lab code,
  the trainer's today/this-week classes, and the trainers on a delivery.
  Use when an MTT asks: "details for my class today", "who's enrolled in ClassID <ClassID>", "Teams join
  link for my class", "student lab code for delivery X", "how many registered / attended /
  no-showed", "what are my classes this week", "what's my next delivery".
  Do NOT use for: post-delivery feedback (use mtt-skilling-insights), student link recaps (use
  mtt-class-recap), run-of-show / pacing (use mtt-class-timeline), meeting
  recaps (use meeting-intel), or sales pipeline (use the dynamics-365-sales plugin).
metadata:
  version: "1.1.0"
  category: productivity
  icon: BookInformation
---

# Class Lookup (MTT class/delivery data)

Answers an MTT's questions about their training classes by reading the **esiadmin** Dynamics 365
(Dataverse) environment. **Read-only to Dynamics** — it never creates or edits Dynamics records.

## When to Use

Trigger when the trainer asks about a class/delivery's data, e.g.:
- "Get me the details for my class today" / "what are my classes this week"
- "What's my next delivery?" / "brief deliveries 100230, 100231" / "upcoming MS-4019 deliveries" (course-wide list)
- "Who's enrolled in ClassID `<ClassID>`?" / "is `<student>` in both classes?"
- "Have I taught `<student>` before?" / "What courses has `<student>` done?" (learner history — Roster & attendance)
- "What's the Teams join link / invite for my class?"
- "What's the student lab code for delivery `<X>`?"
- "How many registered / attended / no-showed for `<X>`?"
- "List the trainers on delivery `<X>`"
- "What's my **trainer profile** / what's my **teach utilization**?" (self-scoped — My trainer profile lookup)
- "Build a **class recap** for my class" (end-of-class link summary — hands off to the **mtt-class-recap** skill)

## When NOT to Use

| If the ask is… | Use instead |
|---|---|
| Capture / prepare post-delivery feedback, "MTT feedback", "Dynamics entry for my delivery" | **mtt-skilling-insights** |
| Student-facing class **link recap** post | **mtt-class-recap** |
| **Run-of-show**, pacing sheet, demo blow-by-blow, transcript→deck alignment | **mtt-class-timeline** |
| Sales **accounts / opportunities / leads / pipeline / deals** (MSX org) | **dynamics-365-sales** plugin |
| Summarise or recap a **meeting you attended** (standup, 1:1, work meeting), extract action items / decisions / notes | **meeting-intel** |
| **Send / post a class message** to the meeting chat (lab-access, course resources, a worded post) | **mtt-teams-message** |

## Before you start

**You'll need:** read access to the **esiadmin** Dynamics 365 environment (the Dataverse tools must be
available in your session). Lookups need nothing else.

**Plain-language glossary:**
- **ClassID / Delivery ID** — the delivery's number (`msdyn_name` on the work order). The anchor for every lookup. (The "ClassID" a trainer says and the canonical Delivery ID are the same number — confirm via the work order, not a booking's trailing number.)
- **Work order** — the delivery record itself in Dynamics; carries course, dates, type, counts, lab code.
- **Booking** — a trainer's assignment to a delivery (who's teaching, in what role).
- **Student lab code** — the key students redeem for their hands-on lab environment. Sensitive — treat with care.

## Quick start

```
User: "Get the details for my class today"
1. Invoke mtt-esiadmin-lookup (mode:delivery, ref:today) → read the delivery anchor from its JSON envelope
2. Off that anchor: all-trainers + roles, join link (Class details); counts/roster only if asked
3. Emit the cheap answer first: render the delivery panel + copyable links block (lab code, if present, and survey) from `mode:delivery` before any roster fan-out. The role-family chart + attendance KPIs (from `mode:roster`) populate after and must never delay or drop the lab-code line.
4. When the delivery resolves to a course code, invoke all four courseware skills before the final answer: `mtt-courseware-leads`, `mtt-courseware-slides-status`, `mtt-courseware-lab-status`, and `mtt-courseware-teams`. Include each result, or name the skill and state why it could not run.
5. Close with **phase-aware next steps** — read `delivery.phase` and offer ≤3, led by the most logical (see *Next steps & loop-back* in `procedure.md`)
```

## Access & environment (esiadmin)

Identity + delivery-anchor resolution is delegated to the **`mtt-esiadmin-lookup`** resolver (next section). The notes below govern this skill's **own downstream reads** (roster, sessions, all-trainers).

- Use the Dataverse tools with `orgName: "esiadmin"`: `read_query` only; never `fetch`, `create_record`, or `update_record` here.
- **Relevance Search is OFF** → use `read_query` with structured filters, not `search`.
- **Metadata is blocked** (`list_tables`/`describe_table` → 400) → learn columns by reading one record.
- `esi_class` / `esi_classparticipant` are **403** → the roster comes from `mtt-esiadmin-lookup` `mode:roster` (work-order → event → registration → contact), not from these tables.
- **Lookup `_value` filters require `valueType:"string"`** (a `guid` valueType → HTTP 400). Try string first; only pivot to a text field if it genuinely 400s.

## Resolve the signed-in trainer & delivery (via mtt-esiadmin-lookup)

Identity and the delivery anchor come from the shared **`mtt-esiadmin-lookup`** resolver — invoke it via the Skill tool and read its JSON envelope; don't re-implement the lookups here.

- **"Me/my", no ClassID** → invoke `mtt-esiadmin-lookup` `mode:identity` → read `identity` (`systemuserid`, `bookableresourceid`).
- **A specific class** (today / a date / a ClassID / course+date) → invoke `mode:delivery`, `fieldset:trainer` → read the `delivery` anchor (`classId`, `workOrderId`, course, `customer`, dates, `deliveryType`, `studentLabCode`, `lxpUrl`, `readableEventId`, `booking`). The resolver owns the booking→work-order confirmation (incl. "never trust the booking name's trailing number").
- **Who's enrolled** (roster, attendance detail, learner backgrounds, "is X in both classes") → invoke `mode:roster` with the same `ref`; it returns the `delivery` anchor **and** a name-suppressed `roster.students` array (learnerId, `displayLabel`, role, employer, language, country, check-in status). **Render learners by `displayLabel`, not by name.** Only set `includeNames:true` for a trainer-initiated, name-anchored ask (see the Privacy guardrail). Opt-in — only when who's-enrolled is actually asked; class details alone stay on `mode:delivery`. Add `includeHistory` (+ `studentRef` to scope to one learner) for "have I taught them before / what courses have they done" — heavier, opt-in (see *Roster & attendance*).
- Branch on `status`: **`ambiguous`** → present the returned `candidates` and ask which; **`not_found`** → say so and offer the calendar fallback; **`unavailable`** → surface `diagnostics.message` + `diagnostics.recommendation` verbatim (for `diagnostics.code = D365_PLUGIN_UNAVAILABLE`), or if diagnostics are absent use the fallback message "Dynamics 365 Plugin read was unavailable. Verify the Dynamics 365 Plugin is enabled in Cowork Customisations, then retry." Then stop.
- **Resolve once, reuse across the branch-menu loop** — cache the envelope; never re-invoke per branch unless the trainer switches to a different class.

## Workflows

Two groups — **🔎 Lookups** (read-only retrieval) and **🔁 Class recap** handoff. **Full step-by-step detail is in `references/procedure.md`; adjustable defaults in `references/customisation.md`.** Load `procedure.md` before executing any branch.

- **🔎 Lookups** — find my class(es) (single via `mode:delivery`, list via `mode:identity` + booking query), deliveries by course code, my trainer profile / utilization (`includeProfile`), support & escalation (`delivery.support`), class details (all-trainers + join link + schedule), roster & attendance (`mode:roster`; `includeHistory` for learner backgrounds), real-time check-in (`includeCheckin` → `delivery.liveCheckin`), **live enrollment & check-in tracking** across today's deliveries (shape-aware: single · multi-class · multi-day retention; cheap enrolled + check-in by default, opt-in unique/overlap aggregates with refresh deltas), and the full Teams invite.
- **🔁 Class recap** — hand off to **mtt-class-recap** with clean inputs (join URL / thread id, ClassID, course code + title, any scope), then step aside.
- **Next steps** — Course information (class details) is the default first action; after it and each branch, offer **phase-aware next steps** (read `delivery.phase`; ≤3, led by the most logical for the phase — see *Next steps & loop-back* in `procedure.md`), and keep the resolved delivery in context.

## Output — presenting class details

**The delivery + audience card IS the class-details output — render it first, every time, not as an add-on.** The `render_ui` "delivery + audience" card (see *Class-details report card* below) is the primary format; it replaces the old text-first layout. Follow the card with a compact **copyable links** block in text, then the phase-aware next steps. Only the links live in text now — everything else (course code · name, official schedule, type, modality, language, trainer + role, registration health, Reg/Cap labelled by `capacity.basis`, customer for Private, and a canceled flag when `isCanceled`) is carried by the card's delivery panel. Emit the delivery panel + links from the cheap `mode:delivery` anchor first, never gated on roster fan-out.

**Links block (in text, directly under the card).** Each link on its own line, each with its **unique fixed emoji**: **🧪 lab code** — `delivery.studentLabCode`, raw copyable text, only when present · **🗣️ student survey** — `delivery.surveyUrl`, raw copyable text, **always include**. **📹 Teams join is on request only** — source it from the trainer's **calendar** first (`ListCalendarView` → the event whose subject carries the ClassID → `onlineMeeting.joinUrl`); if that fails and `delivery.booking.sessionId` is present, use a primary-key `read_query` on `msevtmgt_sessions`; render it as a **short clickable link**, never the raw URL. **Student-paste links stay raw copyable text; trainer-action links are short clickable links** (a hyperlink hides the URL a student must paste).

**The shared card fragment is in `references/delivery-audience-card.md`; the full per-link rendering rules, the 11-rule text fallback, and a worked example are in `references/output-spec.md`.**

### Class-details report card (default) — delivery + audience

Present the **shared "delivery + audience" `render_ui` fragment** (delivery panel + attendance KPIs + role-family bar chart) defined in `references/delivery-audience-card.md` — the same fragment `mtt-skilling-insights` renders, so the two skills look consistent. Invoke the **render-ui** skill first, then make **one** `render_ui` call.
- **Default render branch:** for a class-details answer, make that **one** `render_ui` call with the delivery panel only (plus live check-in counts via `includeCheckin` when asked), then render the links block and phase-aware next steps. If no roster resolved yet, omit the chart/KPIs and note in the card that they require a roster fetch/retry.
- **Roster render branch:** if the ask includes roster and `mode:roster` resolves before rendering, include the attendance KPIs + role-family bar chart in that **same single** `render_ui` call.
- **Final-answer courseware gate:** when the delivery resolves a valid course code, invoke all four courseware skills before completing the final answer: `mtt-courseware-leads`, `mtt-courseware-slides-status`, `mtt-courseware-lab-status`, and `mtt-courseware-teams` (Teams courseware status). Run them independently so one failure does not prevent the remaining checks. For each skill, include its Adaptive Card or explicit empty/unavailable result; if it could not run, name it and state why. Never omit a check silently. Keep the delivery card first, followed by Courseware leads, Slides status, Lab status, and Teams. The class-details card remains the primary artifact; the courseware cards are supplemental analysis that enrich the same course context.
- Run `mode:delivery` and `mode:roster` in parallel when both are needed, but **do not issue a second `render_ui` call for the class-details card in the same turn**. If roster is late/errors/times out, keep the default panel-only render from the delivery anchor, then render the links block and offer retry.
- **After the card, render the links block** (above) — lab code (when present) and the **student survey link every time** as raw copyable text (📹 Teams join is on request, sourced from the calendar) — then the four courseware outcomes in the fixed gate order, then close with **phase-aware next steps** (read `delivery.phase`; ≤3, led by the most logical for the phase — see *Next steps & loop-back*), **never a submit/write menu** (this skill is read-only to Dynamics).
- **On a `render_ui` error, fall back to the full text format** in `references/output-spec.md` so the links and details are never lost — the survey link stays in the fallback too. Partial-result rule: if roster fan-out errors/times out or card rendering fails, still return delivery panel details plus lab code/survey from `mode:delivery`, note what failed, and offer retry.

### What the output looks like

```
[delivery + audience card rendered inline]

🧪 Student lab code
<raw lab code>

🗣️ Student survey
<raw survey URL>

[Courseware leads Adaptive Card, or: Unavailable — <reason>]
[Slides status Adaptive Card, or: Unavailable — <reason>]
[Lab status Adaptive Card, or: Unavailable — <reason>]
[Teams courseware status Adaptive Card, or: Unavailable — <reason>]

Next (Upcoming) — want the class report (role mix + enrolment), the roster, or to post the day plan to the chat?
```

## Guardrails

- **Keep in-line chat output concise.** Lead with the artifact or answer (the delivery + audience card, a file pointer, or the direct result) plus a one-line follow-up; detailed reasoning belongs in the thought process, not the reply. Don't recap what the card, a table, or a generated file already shows, offer phase-aware next steps as one short closing line (≤3, led by the most logical for `delivery.phase`), not a reprinted menu, and fold follow-up offers into a single closing line. Brevity, not omission — never drop a needed caveat (privacy, stale/lagging counts, canceled delivery) to save space.
- **Render class details in the canonical order, cheap-first.** Emit delivery panel + links block (lab code when present, survey always, Teams join on request) from `mode:delivery` first; roster-derived chart/KPIs fill in after and must never block or drop the lab-code line.
- **Ground every value in a tool result.** Never fabricate a ClassID, lab code, link, name, or count. If a lookup returns nothing, say so and suggest the calendar fallback.
- **Resolve "me/my" at runtime** — never hard-code a trainer's IDs; keep all examples generic (placeholders for course / ClassID / timezone, never a real trainer's class or identity).
- **Match learners across classes by `esi_learnerid`**, not by name.
- **Privacy — names off by default.** The roster is name-suppressed (`includeNames` off); render learners by their `learnerId`-derived `displayLabel` (`Learner-392e`), never a personal name and never a positional "Learner 1/2/3" counter (positional labels drift when the roster re-resolves or the cohort changes). Surface only what was asked; don't dump a full roster unless the request calls for it. **Names are opt-in and trainer-initiated only:** when the trainer supplies a name ("is <name> enrolled?", "have I taught <name>?"), you may resolve that one learner with `includeNames:true` (prefer `studentRef` scope) and answer as a **match / no-match** on `learnerId` + role/employer — do not echo other learners' names.
- **Learner history is opt-in and ESI-class-only** — request `mode:roster` `includeHistory` (prefer `studentRef` for one learner) only when the trainer asks who they've taught / what a learner has done. It's the learner's ESI instructor-led attendance, not their full Microsoft Learn journey; count attendance (Checked-In) separately from no-shows, keep it as audience-prep, and never use it to rank or evaluate a learner.
- **Can't resolve a ClassID?** Fall back to the trainer's Outlook calendar — class events embed the ESI link/ClassID in the subject (`"<course> Day <n> - <ClassID>"`).
- **Don't trust the booking name's trailing number** for the Delivery ID — confirm via the work order.
- **Flag canceled deliveries.** If `delivery.isCanceled` (resolver-derived from `msdyn_systemstatus` 690970005), say so prominently — never present a canceled class as live.
- **Counts: live roster wins.** Prefer `roster.checkinCounts` / `roster.activeCount` (authoritative) over the work-order count fields; when you use the cheap WO counts without a roster, caveat them as "system count, may lag."
- **Live tracking is shape-aware and cheap by default.** Detect the delivery shape (one-class · multi-class · multi-day) before rendering — never print a 1×1 overlap matrix or a "unique vs total" line for a single class. Default and every refresh stay on the cheap enrolled + check-in read; the unique / overlap / retention aggregates need a full roster fan-out, so they're opt-in (offer once, remember the choice) and recomputed only when an enrolled count moved.
- **Class recap is delegated, not rebuilt.** Hand off to **mtt-class-recap** with clean inputs and step aside.
- **"Post to class" is student-facing MESSAGES only — never internal reports.** The post-to-class branch (hands off to **mtt-teams-message**) sends student-facing messages to the class meeting chat: lab access, learning resources, day plan, icebreaker, break, closing wrap-up, or a worded post. It is **not** a channel for the internal Delivery Summary or any trainer-internal report (**mtt-report-builder**) — those are trainer-facing artifacts. Never route a report through this branch, and never offer — or act on a request — to post/send a Delivery Summary to the class (student) chat; it stays internal (the trainer's own self-chat, a colleague/TPM, print to PDF).
- **If the Teams-send connector is unavailable, be explicit and non-destructive.** When hand-off to **mtt-teams-message** cannot post due to tool/connector unavailability, say posting was unavailable right now, provide/retain copyable message text, and offer retry; never claim a send succeeded and never auto-reroute to a different chat.
- **v2 envelope fields are best-effort** — `catalog`, the enriched `customer`, `support`, `status`, `modality`, `language`, and the extra counts may be null for a given delivery; show only non-null values, never fabricate. Support info is **on-request** (the branch-menu item), not inline in class details.
- **"My trainer profile / utilization" is self-scoped** — the signed-in trainer's own data only; never rank or compare trainers (that's performance evaluation).

## Additional resources

Load on demand for detail:
- `references/procedure.md` — full step-by-step for every Lookup, the messaging & recap hand-offs, and the phase-aware next steps
- `references/data-model.md` — esiadmin tables & the v2 envelope fields consumed here
- `references/output-spec.md` — the class-details presentation format + worked example
- `references/delivery-audience-card.md` — the canonical shared delivery + audience `render_ui` card fragment
- `references/customisation.md` — adjustable defaults (date windows, session cache refresh, break wording, auto-offer)
