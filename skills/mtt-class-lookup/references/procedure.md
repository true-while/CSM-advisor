# mtt-class-lookup — procedure

**Purpose:** The full step-by-step for every Lookup, the class-recap hand-off, and the phase-aware next steps.
**Loaded by:** `mtt-class-lookup` on demand (see SKILL.md → Additional resources)

---

> **Context note:** all class data flows through the `mtt-esiadmin-lookup` resolver — work from the returned delivery envelope; don't re-query or re-fetch what the resolver already provides.

## Rules that apply throughout

- **Grounded output only.** Never fabricate ClassIDs, links, counts, or names; if data is missing, say so and use the documented fallback.
- **Keep privacy defaults.** Roster output is name-suppressed by default (`displayLabel` / `learnerId`); enable names only for trainer-initiated, name-anchored checks.

## Workflows

The skill has two workflow groups: **🔎 Lookups** (read-only data retrieval) and **🔁 Class recap** hand-off.

### 🔎 Lookups (read-only)

#### Find my class(es) — no ClassID given
- **A single class** ("my class today", a date) → `mtt-esiadmin-lookup` `mode:delivery` with that ref resolves and confirms the anchor; use the returned `delivery` block.
- **"My classes this week"** (a LIST — the resolver returns one anchor, not a list) → invoke `mode:identity` for `bookableresourceid`, then list the trainer's bookings yourself: `read_query bookableresourcebookings` filter `_resource_value eq <bookableresourceid>` (`valueType:"string"`) over the window, **ordered `starttime desc` or date-bounded** (an `asc`+`top` can truncate). For any class the trainer drills into, resolve its anchor via `mode:delivery`.
- **Date taxonomy for lists** — map the phrase to a window: `today` / `tomorrow` / a named weekday → that day; `this week` → today→Sunday; `next week` → next Mon–Sun; `recent` / `upcoming` (no explicit duration) → **future-only, today→+14d**; `next month` / `next N` → today→+Nd; `past` / `last` / `my last N` → **backward, today−60d→today** (order `starttime desc`); an explicit range → that range. `recent` / `upcoming` never includes past dates.
- **Calendar-first (cheap cross-check):** you can also read the trainer's Outlook calendar — `ListCalendarView` over the window, pull the ClassID / `delid=<id>` from each event's subject/body (`https://esi.microsoft.com/Deliveryonly/?delid=<id>`), then resolve each anchor via `mode:delivery`. Use it as a cheap primary or to cross-check the booking list; fall back to the booking query when the calendar is empty.
- **"My next delivery"** (singular, soonest upcoming) → list bookings today→+60d (widen to +180d once if empty), take the soonest by `starttime`, and render the **full class-details brief** for that one — not a table.
- **Several explicit IDs** ("brief 100230, 100231, 100240") → resolve each anchor in **parallel** (`mode:delivery` per ID) and show one compact row each; offer the full brief per ID on request.

#### Deliveries by course code (across trainers)
"All upcoming MS-4019 deliveries" — a course-wide list, **not** trainer-scoped. Query work orders directly: `read_query msdyn_workorders` filter `esi_catalogitemidcalc eq "<course>"` + an `esi_officialstartdatetime` window (same date taxonomy above) + **`msdyn_systemstatus ne 690970005`** (exclude canceled), `orderBy esi_officialstartdatetime asc` (forward) / `desc` (past). Render a compact table — **ID · Course · Modality · Type · Start · End · Trainer · Reg/Cap** — with Reg/Cap from `esi_registrationcountevent` / `esi_numberofstudents` and Trainer from the newest Active Primary booking (`bookableresourcebookings` `name` contains the ID, `statecode eq 0`). No Region column — customer-HQ overrides make `msdyn_country` unreliable; use the full brief if location is needed. Drill into any row via `mode:delivery`.

#### My trainer profile basics (A)
A self-scoped lookup for "what's my trainer profile?" — **not** class-scoped and never a utilization report.
1. Invoke `mtt-esiadmin-lookup` `mode:identity, includeProfile:true` → read `identity.profile`.
2. Present (omit any null line): trainer type + title, location, recent / additional teach timezones,
   qualification count, onboarding status / date, MCP ID, manager. **Omit monthly and yearly teach-utilization %** even if present in the profile payload.
3. It's the signed-in trainer's **own** operational data — never rank or compare against other trainers, and never turn profile fields into capacity or performance reporting.

#### Support & escalation (D) — on request
Surfaces the delivery's support context straight from the already-resolved envelope (`delivery.support`) —
**no new query**. Show (omit null lines): the in-class **support desk + SLAs** (`supportInfo` /
`supportContact`), the delivery's **TPM** and **TPC**, any **TPM Instructions** (`delivery.tpmInstruction` —
TPM-authored audience/objective guidance, usually only on customized enablement deliveries), and the
**trainer-report**, **onboarding-package**, and **lab-registration** links. Offered as a next step (on request);
present only what's non-null.

#### Class details — by ClassID / delivery
Decision chain (resolver-first vs calendar):
1. **Delivery anchor facts first (default):** resolve the class with `mtt-esiadmin-lookup` (`mode:delivery`) for course/title/customer/official schedule/lab/survey/support context.
2. **Calendar path only when the ask is meeting-access or invite-specific:** if the trainer asks for join link, invite payload, per-day session timing, or transcript/meeting artifact context, resolve from calendar first (`ListCalendarView` by ClassID in subject).
3. **Dynamics session fallback only when calendar cannot resolve:** if calendar lookup does not return the expected meeting occurrence, read `msevtmgt_sessions` by the booking's exact `sessionId` for `msevtmgt_attendeeurl` and session times.
4. **Never swap source of truth:** keep official delivery schedule fields from resolver (`officialStart`/`officialEnd`) and use calendar/session only for meeting-access artifacts.

1. The delivery anchor (course, title, dates, `deliveryType`, `studentLabCode`, `lxpUrl`, `customer`, `readableEventId`) comes from `mtt-esiadmin-lookup` (`mode:delivery`). Emit the delivery panel + links block from this cheap anchor first; if the ask also needs roster, run `mode:roster` in parallel so roster visuals can follow without delaying the lab-code line. Counts are read from the work order when needed (see Roster & attendance step 3).
2. **All trainers + roles** (the anchor's `booking` is only the signed-in trainer): `read_query bookableresourcebookings` filter `name` contains "<ClassID>" → RESOURCE + `esi_deliveryrole`.
3. **Teams join / invite / per-day schedule — on request only; skip on the default class-details pass.** The join link is rarely needed, so **don't read `msevtmgt_sessions` by default** — the official schedule already comes from the work order (`officialStart`/`officialEnd`). When the trainer asks for the join link / invite / per-day session times, prefer the **calendar** (cheaper, no Dynamics read): `ListCalendarView` over the class window → match the event whose subject carries the ClassID (`<course> Day <n> - <ClassID>`) → take `onlineMeeting.joinUrl` (== the session `attendeeurl`). Only if the calendar can't resolve it **and** `delivery.booking.sessionId` is present, `read_query msevtmgt_sessions` with a primary-key filter (`msevtmgt_sessionid eq "<sessionId>"`, `valueType:"string"`) → `msevtmgt_attendeeurl` + `msevtmgt_starttime/endtime`; decode `msevtmgt_teamsinvitationhtml` for passcode only if the full invite is asked for. If both calendar resolution and `sessionId` are unavailable, say the join details could not be resolved from the current delivery context and offer retry.

#### Roster & attendance — who's enrolled
1. **Who's enrolled** → invoke `mtt-esiadmin-lookup` `mode:roster` with the same `ref` as the class, and read the **name-suppressed** `roster.students` array from its envelope. Match roster weight to intent: for a bare "who's enrolled / give me roster", request `rosterDetail:light` (registrations-only, no per-learner contact fan-out); request full detail only when the ask needs learner backgrounds (roles/employers/languages). For counts-only asks, prefer `mode:delivery` + `includeCheckin` over a roster walk. The resolver owns the event → registration → contact walk, the tight-select / spill handling, and decode logic — **don't re-walk those tables here.** **Render each learner by `displayLabel`, never by name.** Obey the privacy guardrail (don't dump a full roster unless the ask calls for it). For a **name-anchored** ask the trainer initiated ("is <name> in this class?", "have I taught <name>?"), re-invoke scoped to that learner with `includeNames:true` + `studentRef` and answer as match / no-match — never expand it into a named listing of the whole room.
2. **Enrolled in two classes?** Invoke `mode:roster` once per class and **match on `learnerId`** (`esi_learnerid`) — names vary, the learnerId doesn't. The resolver already returns active learners only (`statecode = 0`).
3. **Counts** (registered/attended/no-shows): precedence is fixed. Use `roster.activeCount` + `roster.checkinCounts` as authoritative when roster is available. For counts-only asks, `delivery.liveCheckin` is the fast path. Work-order/envelope mirrors are fallback only and must be caveated as **"system count, may lag"**. Include extra counts (F) from `delivery.counts` only when asked or non-null.
4. **Learner history** ("have I taught them before?", "what courses has this student done?") → invoke `mode:roster` with `includeHistory` and read each student's `history` block: `taughtByYou` + `taughtByYouClasses` (have you had them in a prior class) and `priorClassCount` / `recentCourses` (their broad ESI course history). Add `studentRef` to scope to **one** learner — the cheap, targeted path for "have I taught `<name>`". **Opt-in and heavier** — only when actually asked; don't run it across the whole roster or dump full histories unprompted. Present as audience-prep / "welcome back", distinguish attended from no-show, note it's **ESI-class history only** (not their whole Microsoft Learn journey), and never use it to evaluate a learner.

#### Real-time check-in (live numbers, cheap)
"How many checked in for `<id>`?" — the fast path, **no roster walk**. Invoke `mtt-esiadmin-lookup` `mode:delivery` with **`includeCheckin`** and read `delivery.liveCheckin` = `{registered, checkedIn, waitlist, cancelled}` (one event read; `checkedIn` is the authoritative `msevtmgt_checkincount`). Render the **single-class one-liner** (formalised in `references/output-spec.md` → *Live check-in — tracking output* → *Single class*): `<ClassID> · <course code> · <topic> — <checkedIn> / <enrolled> checked in (<pct>%) <phase glyph>` (`⏳ upcoming` · `🔵 live` · `✅ done`, from `delivery.phase`) — or its one-row-table twin. **Never show "Attended" from `esi_attendancecount`** (unreliable). Surface **Waitlist / Cancelled only when > 0**, as a trailing footnote (never a grid column). No ID given ("check-in for my class now") → resolve today's class first, then run this; if several match, ask which.

#### Live enrollment & check-in tracking (multi-class / multi-day)
For "enrollment numbers for my classes today", live combined tracking across one or more of today's deliveries, and repeated **refreshes**. Shape-aware, cheap by default, the expensive parts opt-in.

1. **Detect the delivery shape first.** Group today's bookings by `_msdyn_workorder_value` (Canceled already excluded by the resolver) and inspect each work order's official day span:
   - **One class / day** (one work order, single official day) → a single delivery + audience card. **No overlap matrix and no "unique vs total" line** — unique == enrolled, so both are meaningless for one class.
   - **Multiple classes / day** (≥ 2 distinct work orders today) → the **tracking grid** (formalised columns + footer rows in `references/output-spec.md` → *Live check-in — tracking output*): one row per delivery, with **Total-enrolled** and **Total-checked-in** footers **always** (cheap), and the **Unique-students** footer + overlap matrix **(opt-in, offered only for a same-customer set spanning ≥ 2 distinct course codes)** behind the roster fan-out.
   - **Multi-day class** (one work order, `delivery.dayCount` > 1) → "today" is one occurrence; enrolled is stable across days, so replace the cross-class overlap matrix with a **Day-over-Day attendance-retention view** (who attended Day 1 and returned Day 2…), matched by `esi_learnerid` — the same match machinery as the overlap matrix, keyed on the day-sessions of the one delivery.
   - **Mixed** (a multi-day class *and* a separate one-off the same day) → render each work order in its own shape.

2. **Default = the cheap path (no roster walk).** Per delivery, read enrolled + live check-in only — `mode:delivery` + `includeCheckin` → enrolled + live both from `delivery.liveCheckin` (`registered` = enrolled, `checkedIn` = live — the authoritative fast-path counts, not the caveated work-order mirror); one event read per delivery, **no per-learner walk**. A bare "enrollment / check-in" ask **and every refresh** returns this.

3. **Opt-in aggregates — gate the roster fan-out.** The unique-across-classes count and the overlap / retention matrix are the ONLY parts needing the full per-delivery roster (`mode:roster` per delivery → `esi_learnerid` sets). Gate them behind explicit flags, default **off**:
   - `includeUnique` — union of `esi_learnerid` across deliveries → unique headcount.
   - `includeOverlap` — pairwise `esi_learnerid` intersection (multi-class) or the Day-over-Day retention matrix (multi-day); a superset of `includeUnique`.
   - `includeRoster` — per-learner detail.
   **Offer these ONLY when the tracked set holds ≥ 2 SAME-customer deliveries spanning ≥ 2 DISTINCT course codes** (customer matched on `delivery.customer.tpid` / account; codes on `delivery.courseCode`) — the one scenario where a deduped unique headcount (or cross-class overlap) is meaningful, since a learner can attend more than one *different* course under the same customer. **Suppress the offer entirely — omit the Unique / overlap rows, no muted placeholder** — for: a **single class** (unique == enrolled); a set spanning **different customers** (cross-customer overlap is ~nil → unique == total); OR a same-customer set that **shares one course code** (e.g. a large cohort split into morning/afternoon sessions of the *same* course — learners are partitioned across the sessions, so unique == total and the count adds nothing). When it *does* apply, **surface the tradeoff once** ("the unique count needs a full roster read across all classes — include it?"), then **remember the choice** for the rest of the conversation.
   - **Change-detected recompute:** when an aggregate is on, recompute it only when the cheap change-detector fires — **any delivery's enrolled count moved** since the last pull. If enrolled is unchanged, **reuse the prior aggregate and say so** rather than re-walking every roster. Reuse only the derived **counts**; learner PII is still read fresh and never cached.

4. **Conventions (defaults for the tracking view).**
   - **Output = the compact markdown tracking grid** (columns, phase glyphs `⏳`/`🔵`/`✅`, Total-enrolled / Total-checked-in / opt-in Unique footers) formalised in `references/output-spec.md` → *Live check-in — tracking output*. Never a `render_ui` card; **reprint the identical grid each refresh** so pulls diff line-for-line.
   - **Time in the class's operating timezone**, labelled, from `delivery.officialStart` / `officialEnd` (the TZ-independent operating wall-clock — the students' frame), trainer-local only on request. Matches the class-details Schedule rule and removes the cross-TZ (e.g. AEST vs NZST) ambiguity for a NZ/AU cohort.
   - **`(+x)` deltas on every changed count**, measured against the **first pull of the day** (baseline captured once, carried across refreshes).
   - **"Refresh" = re-pull all *enabled* fields** — the cheap enrolled + check-in always, the opt-in aggregates only when on (honouring the change-detector).
   - **Exclude Canceled deliveries and flag them** — never silently drop; if a whole delivery is canceled, name it.
   - **Match learners only by `esi_learnerid`**, name-suppressed throughout (the standing privacy default; render by `displayLabel`).
   - **Session-scoped:** the per-day baseline (first-pull counts) and the last aggregate live in the session only — re-based each new session, never persisted, never holding learner PII.

#### Teams invite (full)
- **Join link:** `msevtmgt_attendeeurl` as-is (final meetup-join URL). One per day.
- **Passcode / Meeting ID / dial-in:** only in `msevtmgt_teamsinvitationhtml` (a `data:text/html,…` blob) — **URL-decode, then HTML-entity-decode** (`&#35;` → `#`), then read the labelled values.
- The same meeting is on the trainer's Outlook calendar; for join link / dial-in / "when is it" / transcript, `ListCalendarView` is cheaper (`onlineMeeting.joinUrl` == `attendeeurl`).

### ✉️ Messaging delegation (hand off to the mtt-teams-message skill)

Message composition templates and Teams send orchestration live in the shared messaging framework skill, **not** here.

- This skill owns **lookup and recap handoff only**.
- **Scope — student-facing messages only, never internal reports.** This branch posts student-facing class messages (lab access, learning resources, day plan, icebreaker, break, closing, worded post) to the class meeting chat. It is **not** for the internal Delivery Summary or any `mtt-report-builder` report — never route a report through it, and never post/send a Delivery Summary to the class (student) chat (it's trainer-internal; keep it to self-chat, a colleague/TPM, or PDF).
- **Pass the already-resolved envelope so nothing is re-looked-up.** Hand off to `mtt-teams-message` with the resolved `chat_id` (from the calendar `onlineMeeting.joinUrl`, or the attached meeting), the **ClassID**, **course code + title**, and — when present — the **student lab code** and **survey URL**. It owns both templating and the confirm-first send; step aside once handed off — don't pre-compose or pre-send here.
- **High-value moments to offer the hand-off** (each maps to a `mtt-teams-message` template): right after showing the **lab code** → *post the Lab Access message*; at start of day → *post the Day plan* (run of show + breaks), an *Icebreaker*, or the joining details; for resources → *Learning Resources*; at class end → the *Closing wrap-up*; anytime → a *Break* ping or a *free-form* post. The envelope this skill already resolved covers every placeholder those templates need.
- **Connector-unavailable fallback.** If the delegated send path reports Teams-post tooling/connector unavailability, state clearly that posting is unavailable now, keep or return the copyable message text, and offer retry. Never imply a successful post and never auto-reroute to a different chat target.

### 🔁 Class recap (hand off to the mtt-class-recap skill)

For an end-of-class **link recap** post, this skill does **not** build the recap itself — it **hands off to the dedicated `mtt-class-recap` skill**, which owns that output end-to-end.

1. **Invoke `mtt-class-recap` directly** (via the skill system) — don't pre-build, summarise, or template the recap here.
2. **Pass only the inputs it needs**, grounded in the resolved delivery: the meeting / chat reference (the join URL or `19:meeting_…@thread.v2` thread id), the **ClassID**, the **course code + title**, and any scope the trainer stated (e.g. "Day 1 of 4 — only part of the learning paths covered").
3. **Do not shape its output with this conversation.** `mtt-class-recap` runs its own Fetch → Identify → Collect → Categorise → Format → Verify and produces its own file and posting flow. Once handed off, step aside — never reformat, re-scope, or post-process what it returns based on anything earlier in this chat. Your only job is to supply clean inputs.

### Next steps & loop-back (phase-aware — coach into the logical follow-up)

**Course information** (the class-details output) is the default first action when the skill triggers. After it, and after any other branch, **don't print a fixed menu** — read `delivery.phase` and offer **at most 3** next steps, **led by the single most logical one for that phase**, in one short closing line. Skip any step whose data you already showed. Keep the resolved delivery in context across the loop (never re-resolve unless the trainer switches class).

| `delivery.phase` | Lead (most logical) | Then (lighter alternates, pick ≤2) |
|---|---|---|
| **Upcoming** (future) | **Class report** — role/industry mix + enrolment health (hands off to **mtt-report-builder**) | roster & role mix · post joining details / day plan to the class chat (**mtt-teams-message**) |
| **In progress** (present) | **Live check-in** now (`includeCheckin`) | lab-access / resources post (**mtt-teams-message**) · Class report for the role mix |
| **Completed** (past) | **Class recap** links (hands off to **mtt-class-recap**) | post-delivery feedback (**mtt-delivery-debrief**, *if available; otherwise state that feedback drafting is unavailable in this package and retain the class details*) · Class report (final attendance / role mix) |
| **Canceled** | — state the cancellation; offer nothing delivery-specific | trainer schedule / open-day check (**mtt-time-intel**) only |

**Available any phase, but only when relevant / on request** (not part of the default ≤3): support & escalation · Teams join link / full invite · trainer schedule / open-day check (**mtt-time-intel**). **Never** a submit/write option — this skill is read-only to Dynamics. There's no "Done" item; the trainer ends the loop by moving on.
