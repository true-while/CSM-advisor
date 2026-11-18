# skilling-catalog — procedure

**Purpose:** The full search-mode recipes, the default scope filter, row-cap handling, and the
single-item-vs-list rendering decision.
**Loaded by:** `skilling-catalog` on demand (see SKILL.md → Additional resources)

---

## 1. Decide the search mode from the ask

| The ask names… | Search mode | Default scope applies? |
|---|---|---|
| An exact code (`AI-3016`, `MS-4018.S01`) | **By code** | No — report the item as found, whatever its status |
| A topic/product keyword ("Copilot Studio", "Azure AI") | **By keyword/title** | Yes |
| "Is `<code>` PD eligible" alone (no other filter) | **By code**, then read `esi_pdceligible` off that one row | No |
| "List PD-eligible courses about `<topic>`" | **By keyword** + `esi_pdceligible eq true` | Yes |
| "What's in solution area `<area>`" / "courses for `<role>`" | **By solution area** or **by audience/role** | Yes |
| "What delivery types support virtual / in-person" | **By delivery type** | Yes |
| "Is `<code>` retired?" | **By code**, read `statecode`/`esi_retirementdate` directly | No |
| "Include retired items too" | Any of the above + `includeRetired` | Scope widened explicitly |
| "Include Applied Skills / exams / other item types" | Any of the above + `includeAllItemTypes` | Scope widened explicitly |
| "esiadmin is down / unavailable" | Fall back to the **backup portal** | See `backup-portal.md` |

## 2. By exact code (the fast path)

```
read_query msdyn_incidenttypes
filter: msdyn_name eq "<code>"
top: 1
```

If nothing returns, retry with `contains(msdyn_name,'<code>')` in case the user gave a partial code
(e.g. a base code without a suffix like `.S01`). If several rows return (a code family, e.g.
`MS-4018.S01`–`.S07`), render the **list table** (below) rather than guessing which suffix was meant.

## 3. By keyword or title

```
read_query msdyn_incidenttypes
filter: statecode eq 0 and statuscode eq <Active value> and esi_isattindicator eq true
        and (contains(esi_title,'<keyword>') or contains(msdyn_description,'<keyword>'))
top: 50
```

Run the title and description `contains` as an `or` when the tool supports it; if a combined filter
is refused, run two separate queries and de-duplicate by `msdyn_name`. Keep the Active Catalog Items
default scope (`statecode`/`statuscode`/`esi_isattindicator`) unless the user asked to include
retired items, and **filter the returned rows to `esi_catalogitemtype` = MOC Courseware** (client-side
on `@…FormattedValue`, see *Catalog item type* below) unless the user asked to include other item
types.

## 4. By PD eligibility

```
read_query msdyn_incidenttypes
filter: statecode eq 0 and statuscode eq <Active value> and esi_isattindicator eq true
        and esi_pdceligible eq true
top: 50
```

Combine with a keyword filter when the ask names both a topic and PD eligibility.

## 5. Catalog item type (MOC Courseware default) and delivery type

`esi_catalogitemtype` and `esi_deliverytypessupported` are picklist/option-set fields. Select the
**base** field (never the `…name` virtual field — see *Data model* → Access notes) and read the label
from its `@…FormattedValue`.

- **Catalog item type defaults to MOC Courseware.** Since its raw option-set value isn't
  independently confirmed (see *Data model* → Access notes), the safe default is: read the candidate
  rows with whatever other filters apply, then **keep only rows whose `esi_catalogitemtype`
  `@…FormattedValue` equals `"MOC Courseware"`**, client-side. Once the raw numeric value has been
  confirmed in a given environment, an `esi_catalogitemtype eq <value>` server-side filter is a valid
  optimization — but never guess it.
- **Delivery type.** If `esi_deliverytypessupported` proves to be a multi-select field that rejects a
  plain `eq` filter, fall back to reading a small candidate set (by keyword or code family) and
  filtering client-side on the returned `@…FormattedValue` labels instead of guessing the raw
  option-set numeric values.

## 6. Including other catalog item types (opt-in)

Default scope is MOC Courseware only. Only widen it when the user explicitly asks to include other
catalog item types (e.g. "also show Applied Skills items") — drop the client-side `esi_catalogitemtype`
filter and **label each result's actual item type** in the output rather than presenting it as if it
were MOC Courseware.

## 7. By solution area or audience/role

- **Solution area** — `_esi_catalogitemsolutionarea_value eq "<guid>"` (`valueType:"string"`). This
  needs the Solution Area's GUID, which is rarely known up front. In practice, resolve it
  opportunistically: read one known catalog item in that area (by code or keyword) first, take its
  `_esi_catalogitemsolutionarea_value` FormattedValue + underlying value, and reuse the GUID for the
  broader filter. If no anchor item is known, fall back to a keyword/title search instead of
  guessing a GUID.
- **Audience/role** — prefer a free-text `contains(esi_audienceprofile,'<role>')` filter first (the
  primary field). Only fall back to `_esi_targetedroleid_value eq "<guid>"` (`valueType:"string"`,
  same GUID-resolution caveat as solution area) when `esi_audienceprofile` is null on the candidate
  rows.

## 8. Including retired items

Default scope excludes retired items (`statecode eq 0`, Active `statuscode`). Only widen the scope
when the user explicitly asks to include retired/inactive items — drop the `statecode`/`statuscode`
filter, keep any other filters, and **label every retired result clearly** in the output (status =
Retired, with `esi_retirementdate` if present) rather than mixing it in unmarked.

## 9. Row-cap handling

`read_query` caps at roughly 50 rows with no next-page token. If a query returns exactly the cap
size (or very close to it), treat the result as **likely truncated**:
- Say so plainly ("showing the first ~50 matches; narrow by solution area, role, or a longer
  keyword to see the rest").
- Suggest the narrowing filter most likely to help, based on what the user already gave.
- Never claim the list is exhaustive when the cap was hit.

## 10. Falling back to the backup portal

Only after an esiadmin `read_query` fails, is denied, or the Dynamics 365 Plugin reports unavailable
— or on an explicit user request — fall back to the public backup portal
(https://true-while.github.io/tpm-cheat-sheets/). Its full fetch workflow, code index, and
retired/ARB URL convention are in `references/backup-portal.md`. Never query the portal first, and
always label its results as coming from the backup portal, not Dynamics.

## 11. Single item vs. list — the rendering decision

- **Exactly one row returned** (or the user named one exact code) → render the full **catalog-item
  card** (see `references/output-spec.md`).
- **More than one row returned** → render the **compact list table** (code, title, MTT indicator, PD
  eligible, status, duration, solution area) and invite the user to name a code for the full card.
  Never render more than one full card unprompted — if the user wants full detail on several items,
  render the table first and let them pick, or confirm "full detail on all N?" before expanding.
- **Zero rows returned** → say so plainly, state the filter that was tried, and suggest loosening it
  (drop a filter, try a keyword instead of an exact code, widen to include retired items or other
  catalog item types, or fall back to the backup portal).
