# mtt-class-lookup — output spec

**Purpose:** The default card-branch output shape, the **text fallback** class-details presentation format (11 rules), and a worked example. The default output is the `render_ui` "delivery + audience" card (see SKILL.md → *Class-details report card*); this text format is used only when that card errors, so a card failure never loses data — it carries the same facts, including the copyable links and the student survey link.
**Loaded by:** `mtt-class-lookup` on demand (see SKILL.md → Additional resources)

---

## Default card branch — what the output looks like

The default (non-fallback) answer is the `render_ui` delivery + audience card, then the links block, then the four courseware outcomes, then phase-aware next steps:

```
[delivery + audience card rendered inline]

🧪 Student lab code
<raw lab code>

🗣️ Student survey
<raw survey URL>

NOTE: links on the following adaptive cards should be a hyperlink ("URL"), not the raw URL. If the card is unavailable, the reason is shown instead.
[Courseware leads Adaptive Card, or: Unavailable — <reason>]
[Slides status Adaptive Card, or: Unavailable — <reason>]
[Lab status Adaptive Card, or: Unavailable — <reason>]
[Teams courseware status Adaptive Card, or: Unavailable — <reason>]

Next (Upcoming) — want the class report (role mix + enrolment), the roster, or to post the day plan to the chat?
```

## Text fallback format — presenting class details

1. Heading = **course code · name**.
2. **Customer(s):** line — list the customer(s), **only for Private / multi-customer private** deliveries (`esi_deliverytype` = Private). Use `delivery.customer.name` when present; if it is missing, fall back to the booking's `CUSTOMER:` value. Omit for Open Enrollment. Enrichment is conditional: account-enriched customer fields (`accountId`, `city`, `country`) are present only when the resolver call opts into `includeCustomerAccount`, so never require them for this line.
3. **Each link type keeps a unique, fixed emoji** — 📹 Teams join · 🧪 lab code · 🗣️ survey — never repeated across types.
4. **Schedule:** one row for the scheduled (delivery-local) time; add a **second row for the trainer's local time only if it differs**.
5. **Week / schedule tables:** render **one row per delivery**. If a day contains several deliveries, repeat the date/day across multiple rows or use a day heading with delivery sub-rows; never collapse several classes into one table line.
6. **Trainers:** show the trainer's role; if multiple, list each + role below "Your role".
7. **Join access — on request only.** Don't fetch or show the Teams join link by default (skip the `msevtmgt_sessions` read); when the trainer asks, source it from the **calendar** (`ListCalendarView` → `onlineMeeting.joinUrl`, matched by ClassID in the subject) and render as a **short clickable link** prefixed 📹 (e.g. `📹 [Join the Teams meeting](<join url>)`), **not the raw URL**; no passcode, Meeting ID, or dial-in (unless the full invite is explicitly requested).
8. **Student lab code & survey link:** include the **🧪 student lab code** if present (**skip the line if null**). **Always** include the **🗣️ student survey link** (`delivery.surveyUrl` — resolved by the resolver even in `mode:delivery`) on its own line, labelled as the **final survey for students** and ready to copy into the class chat.
9. Keep Delivery ID, type, class size; add a **Modality** and **Language** line (F — `delivery.modality` / `delivery.primaryLanguage`) only when present, a **Registration Health** line (`delivery.registrationHealth` — Green/Yellow/Red) when present, and a **Skillable Class ID** line (`delivery.skillableClassId`) when present. For **Registration / Capacity**, use `delivery.capacity.value` and label the denominator by `delivery.capacity.basis` — "Capacity" (delivery-max), "Expected headcount" (expected-headcount), or "Catalog capacity" (catalog-default); never present an expected/catalog value as a hard max. Don't inline the support block in class details — it's the separate **Support & escalation** branch (D). If `delivery.tpmInstruction` is present, surface it **verbatim** there, keep it trainer-only, dedupe identical wording across sibling deliveries, and if it conflicts with `delivery.officialStart` / `delivery.officialEnd` or duration, show both and name the discrepancy — canonical schedule fields win.
10. **Scale deliveries** (`esi_numberofstudents ≥ 100`, corroborated by `esi_benchmarkattendees`): there is no boolean "scale" flag, so use this capacity threshold. If scale **and** no alternate join field is set (`msevtmgt_webinarurl`/`msevtmgt_externalurl` null), **flag the join link as "verify" on its own new line** rather than guessing.
11. **For a resolved course code, complete the four-check courseware gate before closing:** Leads, Slides status, Lab status, then Teams courseware status. Include each result or an explicit empty/unavailable outcome; if a skill could not run, name it and state why. Then close with phase-aware next steps (see *Next steps & loop-back*) — read `delivery.phase` and offer **≤3**, led by the single most logical step for that phase, in one short line (not a fixed menu). Course information (the class details) is the default first action; after each branch, re-offer phase-appropriate next steps and keep looping — no "Done" item, the trainer ends it by moving on.

### Worked example (Private, single-day, two timezones)
Values below are illustrative.

```
PL-7008 · Create agents in Microsoft Copilot Studio
Customer(s): Contoso Ltd

| Delivery ID    | 10XXXX                                  |
| Type           | Private Delivery                        |
| Scheduled      | Fri 26 Jun 2026, 9:00 AM – 5:00 PM NZST |
| Your local time| 7:00 AM – 3:00 PM AEST                  |
| Your role      | Primary                                 |
| Class size     | 25                                      |

🧪 Student lab code: XXXXXXXXXXXXXXXX
🗣️ Final survey (share with students): https://www.metricsthatmatter.com/student/evaluation.asp?k=79335&i=10XXXX

[Courseware leads Adaptive Card, or: Unavailable — <reason>]
[Slides status Adaptive Card, or: Unavailable — <reason>]
[Lab status Adaptive Card, or: Unavailable — <reason>]
[Teams courseware status Adaptive Card, or: Unavailable — <reason>]

Next (Upcoming) — want the class report, roster, or day-plan post?
```

- "Your local time" row appears **only because** delivery-local (NZST) ≠ trainer-local (AEST). For an AEST delivery it's omitted.
- For **Open Enrollment**: drop the `Customer(s)` line.
- If `esi_studentlabcode` is null, omit the lab-code line. Add other trainers under "Your role" when present.

## Final-answer courseware gate

When `delivery.courseCode` resolves, the gate applies to both the default card branch and this text-fallback branch. Run all four checks independently and present their outcomes after the links in this fixed order: **Courseware leads → Slides status → Lab status → Teams courseware status**. A successful check returns its Adaptive Card or explicit empty result. If a check cannot run, name the skill and state why; never omit it silently, and never let one failure prevent the remaining checks.

## Links block — per-link rendering rules

Each link renders on its own line with a unique, fixed emoji. Full per-link detail:

- **📹 Teams join** — **not shown by default** (the join link is rarely needed, and its Dynamics session read is skipped on the common path). Provide it **on request**: prefer the trainer's **calendar** — `ListCalendarView` over the class window, match the event whose subject carries the ClassID (`<course> Day <n> - <ClassID>`), and use its `onlineMeeting.joinUrl` (identical to the session `attendeeurl`, with **no Dynamics session read**). Only if the calendar can't resolve it **and** `delivery.booking.sessionId` is present, fall back to a primary-key `read_query` on `msevtmgt_sessions` (`msevtmgt_sessionid eq "<sessionId>"`, `valueType:"string"`) for `msevtmgt_attendeeurl`. If neither source resolves, say join details are unavailable and offer retry. Render as a **short clickable link** (`📹 [Join the Teams meeting](<url>)`), **never the raw URL**; join only, no passcode unless asked.
- **🧪 Student lab code** (`delivery.studentLabCode`) — only when present; keep as **raw copyable text** (students redeem it).
- **🗣️ Student survey link** (`delivery.surveyUrl` — always resolved by the resolver, even in `mode:delivery`) — label it the **final survey for students** and keep it as **raw copyable text**, ready to paste into the class chat. **Always include it.**

## Live check-in — tracking output (multi-class / single / multi-day)

The live enrollment & check-in view is a **compact markdown table** (never a `render_ui` card) — chosen so it **reprints identically on every refresh**, diffs visually at a glance through the day, and pastes cleanly into a self-chat tracking note. Shape-adaptive (data logic in `references/procedure.md` → *Live enrollment & check-in tracking*). Every column is a **resolver field — nothing hard-coded** to a course, session, or timezone.

### Multi-class day (≥ 2 deliveries today) — the tracking grid
One row per delivery, ordered by start time:

| Time (`{TZ}`) | ClassID | Session | Topic | Enrolled | Checked in |
|---|---|---|---|---|---|

- **Time (`{TZ}`)** — `delivery.officialStart` wall-clock in the delivery's **operating timezone**; the header names the TZ **dynamically** (`Time (NZST)` / `Time (AEST)` …), trainer-local only on request (`class-lookup.trackTimezone`).
- **ClassID** — `delivery.classId` (canonical Delivery ID — the unique key when Session/Topic repeat across same-course sessions).
- **Session** — `delivery.courseCode` (+ any session suffix the code carries, e.g. `.S05`).
- **Topic** — short human title from `delivery.courseTitle` (trim to ~40 chars). **Never fabricate** — fall back to the course code if the title is null.
- **Enrolled** — `liveCheckin.registered`, with a `(+N)` **delta vs the day's baseline** (omit `(+0)`).
- **Checked in** — `{checkedIn} / {enrolled} ({pct}%)` + a **phase glyph + word** read from `delivery.phase` (never a static "done"): **⏳ upcoming · 🔵 live · ✅ done**. Append `(+N)` on the checked-in count when it moved vs baseline — this is the number the trainer watches all day. `pct = min(100, checkedIn / enrolled · 100)`.

**Footer rows** (bold label; figures in the Enrolled / Checked-in columns):
- **Total enrolled** — Σ enrolled `(+N)` — **always** (cheap; no roster read).
- **Total checked in** — Σ checkedIn / Σ enrolled (`{pct}%`) `(+N)` — **always** (cheap) — the single most useful running number.
- **Unique students** — deduped headcount by `esi_learnerid` across all deliveries `(+N)` — **opt-in, and shown ONLY when the grid holds ≥ 2 SAME-customer deliveries spanning ≥ 2 DISTINCT course codes** (customer on `delivery.customer.tpid`, codes on `delivery.courseCode`) — the one case where a distinct-people count is meaningful (a learner can attend two *different* courses under one customer). In that case render it muted (`— enable to compute`) until enabled, then recompute only when an enrolled count moves. **Omit the row and the offer entirely — no muted placeholder** — for a **single class**, a **cross-customer** set, or a same-customer set that **shares one course code** (cohort splits of the same course partition learners, so unique == total).

**Compactness / hygiene:**
- **Waitlist & Cancelled are OFF the grid** — surface as a one-line footnote only when non-zero (`⚠ 103482 — 4 cancelled`). Keeps the grid scannable.
- **Deltas are always vs the first pull of the day** (baseline captured once, carried across refreshes; `class-lookup.trackDeltaBaseline`).
- **Canceled deliveries are flagged, never silently dropped.**
- A **refresh reprints the identical grid** (same columns, same order) so two pulls diff line-for-line.

### Single class — the one-liner (no grid)
One delivery gets **no** grid, matrix, or unique/overlap line (unique == enrolled). Either a one-row table —

| ClassID | Session | Topic | Checked in |
|---|---|---|---|
| 103478 | MS-4018.S05 | Excel — Uncover data insights | 13 / 18 (72%) ✅ done |

— or the tighter **inline** form (default for a quick one-off check): `103478 · MS-4018.S05 · Excel — Uncover data insights — 13 / 18 checked in (72%) 🔵 live`. This **replaces** the old monospace `Registered/Checked in/Waitlist/Cancelled` block; waitlist/cancelled move to a footnote-when-non-zero.

### Multi-day class (one delivery, `dayCount` > 1)
Enrolled is stable across days, so instead of a cross-class grid, render the **Day-over-Day attendance-retention** view (who attended Day 1 and returned Day 2…), matched by `esi_learnerid` — same footer/delta conventions, keyed on the day-sessions of the one delivery.
