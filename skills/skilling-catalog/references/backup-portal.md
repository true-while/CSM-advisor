# skilling-catalog — backup portal

**Purpose:** The tpm-cheat-sheets fallback: its code index, per-technology table pages, the
retired/ARB URL convention, and when (and how) to use it instead of esiadmin.
**Loaded by:** `skilling-catalog` on demand (see SKILL.md → Additional resources)

---

## What it is

[https://true-while.github.io/tpm-cheat-sheets/](https://true-while.github.io/tpm-cheat-sheets/)
("CSM Cheat sheets — supporting materials for delivery selection") is a **public, static Jekyll
site**, maintained outside Dynamics, that carries current catalog information: per-technology
course-comparison tables and retired-class tables. Read-only, no login, no write capability of any
kind exists against it.

**It is a secondary, community-maintained reference, not the system of record.** Use it only:
- after an esiadmin `read_query` fails, is denied, or the Dynamics 365 Plugin reports unavailable, or
- on an explicit user request to check the backup portal.

Never query it first, and never present its data as if it came from Dynamics — always label the
source (see `references/output-spec.md` → *Catalog-item card (single match, backup portal)*).

## What it does NOT have

The portal carries no MTT indicator, no PD eligibility flag or credit value, no modality capacity
fields, and no solution-area classification. **Never infer any of these from a portal result.** A
consuming skill that needs an authoritative PD = Yes gate must not use the portal at all for that
decision (see SKILL.md → Guardrails).

## Fetch workflow

1. **Resolve the code/keyword via the index.** Fetch
   `https://true-while.github.io/tpm-cheat-sheets/assets/list.json` — a flat JSON array of
   `{ "number": "<code>", "title": "<title>", "url": "<table page>" }`. Match the requested code
   exactly against `number`, or the requested keyword against `number`/`title` (client-side substring
   match — the portal has no server-side search). This gives the exact table page to fetch next, and
   also already tells you the item's status (see *Retired and ARB URL convention* below). Treat a
   stale/unreachable `list.json` the same as any other portal-read failure — report it, don't guess.
2. **Fetch the resolved table page** (e.g. `docs/copilot-table.html`). Each page renders one HTML
   table with courses as **columns** and attributes as **rows**. Observed row labels include: Course
   (code), Title, Desc, Duration, Audience, Pre-req class, Pre-req knowledge, Intersect classes,
   Agenda (a Microsoft Learn path link, when present), Labs (a lab count/link, when present), Applied
   Skills (Yes/No). **The exact row set is not fixed — read whatever rows the fetched page actually
   has for that code's column; never assume a row exists or invent one that wasn't returned.**
3. **Read only the one column** matching the requested code; ignore the other columns on the page
   unless the user asked for a broader comparison across that technology.
4. If the index match or the page fetch fails, report the failure plainly — do not fall back further
   (there is no tertiary source); suggest retrying esiadmin once its outage clears.

## Retired and ARB URL convention

`list.json`'s `url` field (and the portal's own navigation) encodes status in the page name, which
you can rely on **without opening the page**:

- **`*-table-r.html`** → the item is on a **retired** table (e.g. `ai-table-r.html`,
  `copilot-table-r.html`, `dp-table-r.html`). Report `Status: Retired` for that code.
- **`*-table-arb.html`** → the item is on an **ARB** (role-based / certification-track) comparison
  table rather than the standard one-day course tables (e.g. `ai-table-arb.html` for `AI-901`,
  `AI-103`, `AI-200`, `AI-500`). Report it as found, noting it came from the ARB table rather than
  the standard course table.
- **Any other `*-table.html`** → the item is on the standard active/current table for that
  technology. Report `Status: Active (unconfirmed — portal does not track retirement
  independently)`, since the portal's "active" is only "not on a retired page", not an independent
  confirmation.

## Per-technology landing pages (for a browse, not a lookup)

If the user wants to browse a whole technology area rather than look up one code, the portal's
landing page links to one table per area: AI, ML, Data, Copilot, Infra, Dev, DevOps, Security, Power,
Fabric, Modern — plus separate "Retired" links per area. **Always fetch the landing page fresh to
get the current link list** rather than hard-coding a page map here; the site's navigation can change
and a stale local map could point at the wrong or a removed page.
