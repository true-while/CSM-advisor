# skilling-catalog — data model

**Purpose:** The `msdyn_incidenttype` (catalog item) fields this skill reads, the "Active Catalog
Items" + MOC Courseware filter parity, and the Dataverse-MCP query gotchas that apply to this table.
**Loaded by:** `skilling-catalog` on demand (see SKILL.md → Additional resources)

---

## Source view

This skill's default scope mirrors the Dynamics 365 **"Active Catalog Items"** view
(`etn=msdyn_incidenttype`, `viewid=467a8f92-753b-485e-8ba9-13de8b7cb3a7`, `viewType=1039`): active,
MTT-indicator catalog items — **narrowed further to `esi_catalogitemtype` = MOC Courseware**, the
instructor-led format MTTs deliver. A direct lookup by exact code bypasses the default scope (a
trainer naming a specific code wants that item regardless of status or type — see *Including retired
items* and *Including other catalog item types* in `procedure.md`).

## Table and fields

| Table | Fields used |
|---|---|
| `msdyn_incidenttype` *(entity set `msdyn_incidenttypes`)* | **Identity:** `msdyn_name` (catalog/course code — the primary lookup key), `esi_title` (official title). **Status/scope:** `statecode` (0 Active / 1 Inactive — the retired-course filter), `statuscode` (status reason; confirm the exact Active value at runtime, see *Access notes* below), `esi_isattindicator` (**MTT indicator** — the canonical filter for the Active Catalog Items view; Yes/No, **not** PD proof on its own), `esi_retirementdate` (set once retired). **Eligibility:** `esi_pdceligible` (the actual PD = Yes gate) + `esi_creditvalue` (token / PD-credit value). **Duration:** `esi_standardduration` / `msdyn_estimatedduration` (minutes — record both and flag a mismatch; never convert to PDc). **Delivery and capacity:** `esi_deliverytypessupported` / `esi_deliveredby`, `esi_catalogitemtype`, `esi_viltmaximumcapacity` / `esi_biltmaximumcapacity` / `esi_hiltmaximumcapacity` / `esi_blxpmaximumcapacity` (best-effort — several are null depending on modality). **Audience/prerequisites:** `esi_audienceprofile` (primary, free-text), `_esi_targetedroleid_value` (**Default Role** — audience fallback when `esi_audienceprofile` is null, lookup; FormattedValue gives the label), `esi_courseprerequisites`. **Classification:** `_esi_catalogitemsolutionarea_value` (Solution Area, e.g. *Cloud & AI Platforms* — the ESI **parent** SA, not a CAIP sub-grouping), `_esi_microsoftcertification_value` (linked certification, if any). **Description and links:** `msdyn_description` (catalog description), `esi_externalurl` (prefer this — often a populated MS Learn path URL), `esi_mslearnurl` (fallback — frequently null). |

All fields are **best-effort**: omit a null field from the rendered card rather than showing it as
empty or guessing a value.

## Default "Active Catalog Items" + MOC Courseware parity filter

```
statecode eq 0
and statuscode eq <confirm the Active status-reason value at runtime>
and esi_isattindicator eq true
and esi_catalogitemtype @…FormattedValue eq "MOC Courseware"   (client-side — see Access notes)
```

Apply this as the default scope for keyword/topic/role/solution-area searches. An exact-code lookup
(`msdyn_name eq "<code>"`) does not apply this filter by default — report the item's actual status
and type instead of hiding it, since the user already named it specifically. Widening past MOC
Courseware to other catalog item types, or past active to include retired items, is opt-in only (see
`procedure.md` → *Including other catalog item types* / *Including retired items*).

## Access notes (inherited from the esiadmin environment contract)

- **Metadata is blocked** (`list_tables`/`describe_table` → 400). The exact `statuscode` value for
  "Active" is not independently confirmed in this reference — if a `statuscode eq <value>` filter is
  refused, confirm the column names and the Active status-reason value with `DESCRIBE
  msdyn_incidenttype` on the target first.
- **Dataverse-MCP `read_query` select gotcha.** Selecting a lookup's denormalized `…name` string
  field or a picklist/boolean virtual `…name` field (e.g. `esi_catalogitemtypename`,
  `esi_isattindicatorname`) returns **HTTP 400**. Select the **base** field instead — the lookup
  `_x_value` (e.g. `_esi_catalogitemsolutionarea_value`) or the raw picklist/boolean
  (`esi_catalogitemtype`, `esi_isattindicator`) — each returns its label in an `@…FormattedValue`.
- A `startswith` filter combined with `orderby` can also 400; prefer an `eq`/`contains` filter or
  drop the `orderby`.
- **MOC Courseware's raw option-set value is not independently confirmed either.** Filtering
  `esi_catalogitemtype eq <raw value>` is an optimization only once that value has been confirmed in
  the target environment (e.g. via `DESCRIBE msdyn_incidenttype`, or by observing it on a known MOC
  Courseware row such as the MS-4018 family). Until confirmed, select the base `esi_catalogitemtype`
  field and filter client-side on its `@…FormattedValue == "MOC Courseware"` instead of guessing the
  numeric value.
- **Lookup `_value` filters require `valueType:"string"`** (a `guid` valueType → HTTP 400) — this
  applies to `_esi_targetedroleid_value` and `_esi_catalogitemsolutionarea_value` filters.
- **Row cap.** `read_query` caps at roughly 50 rows with no next-page token. A broad keyword search
  that returns exactly the cap size is very likely truncated — narrow the filter and say so, rather
  than presenting it as a complete result set.
