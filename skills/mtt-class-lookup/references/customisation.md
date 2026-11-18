# mtt-class-lookup — customisation

**Purpose:** What the MTT can adjust in how this skill behaves — the knob, its shipped default, and the preference key. See `SKILL-DESIGN.md` → *Customisation policy* for the A/B/C tiers. Ask in plain language (e.g. "make my 'recent' window 30 days").
**Loaded by:** `mtt-class-lookup` on demand (see SKILL.md → Additional resources)

---

> **Canonical preamble (shared):** overrides are on-the-fly, session-scoped customisations (namespaced `class-lookup.<key>` in `mtt-skill-preferences`). Stated preferences apply for this session only; they are not persisted across sessions yet. Never written into the skill or repo files.

## Adjustable defaults (Tier A — personal ergonomics)

| Behaviour | Default | `mtt-skill-preferences` key | Notes |
|---|---|---|---|
| "recent" / "upcoming" window | today → +14 days | `class-lookup.recentWindowDays` | future-only |
| "past" / "my last N" window | today − 60 days | `class-lookup.pastWindowDays` | backward, newest first |
| "my next delivery" search | today → +60 days (widen +180 once if empty) | `class-lookup.nextDeliveryWindowDays` | picks the soonest |
| Course-assets cache | session-scoped — fetched once per session, re-fetched next session | `class-lookup.courseAssetsRefresh` | within a session it won't re-fetch; ask to force a re-fetch. No cross-session TTL (the store is session-scoped) |
| Break resume sanity window | ≤ 90 minutes ahead | `class-lookup.breakResumeMaxMin` | re-interprets timezone if outside |
| Live-tracking timezone | class operating TZ (from `delivery.officialStart`); trainer-local on request | `class-lookup.trackTimezone` | the students' frame; removes cross-TZ ambiguity |
| Live-tracking delta baseline | `first-pull` (deltas vs the day's first pull) | `class-lookup.trackDeltaBaseline` | set `last-refresh` to diff against the previous pull instead |
| Live-tracking Unique-students footer | off (opt-in — needs the roster fan-out) | `class-lookup.trackUnique` | **only offered/shown for a same-customer set spanning ≥ 2 distinct course codes**; set on to compute the deduped headcount (recomputed only when an enrolled count moved) |

## Fixed (not customisable — safety / consistency)

- **"Scale delivery" threshold is standardised** (`esi_numberofstudents ≥ 100`) — it drives a data-quality "verify" flag on the join link that must read the same for every MTT (Tier B, pinned).
- **Read-only to Dynamics** — no writes.
- **Official-source-only URLs** (`…github.io` labs, `learn.microsoft.com` paths, @MicrosoftLearn playlists); never fabricated.
- **Privacy** — no full roster dumps unless the ask calls for it; learner history is ESI-class-only and never used to evaluate a learner.
