# skilling-catalog — output spec

**Purpose:** The catalog-item card fields (esiadmin and backup-portal variants), the multi-result
table format, worked examples, and the exact MTT-indicator/PD-eligible caveat wording.
**Loaded by:** `skilling-catalog` on demand (see SKILL.md → Additional resources)

---

## Catalog-item card (single match, esiadmin)

Render as a labelled block, one field per line, **omitting any field with no returned value** (never
show an empty field or guess one). Field order:

0. **Source** — `esiadmin (Dynamics 365)`. Always first, so the reader knows which system the card
   came from before reading anything else.
1. **Heading** — `<code> · <official title>` (`msdyn_name` · `esi_title`).
2. **Status** — `Active` or `Retired` (from `statecode`/`statuscode`; if retired, add
   `esi_retirementdate` when present).
3. **MTT indicator** — Yes/No (`esi_isattindicator`), **immediately followed by the caveat line**
   (see *Caveat wording* below) whenever both this and PD eligible are shown — which is the default.
4. **PD eligible** — Yes/No/Unknown (`esi_pdceligible`); add the credit value (`esi_creditvalue`)
   when present.
5. **Official duration** — a readable length converted from minutes (e.g. "1 hr", "3 days"), from
   `esi_standardduration` (preferred) or `msdyn_estimatedduration`. If the two disagree, show both
   and flag the mismatch for owner validation. **Never show or imply a PDc figure here.**
6. **Capacity by modality** — only the populated fields among VILT / BILT / HILT / BLXP maximum
   capacity; omit a modality entirely if its field is null.
7. **Delivery types supported** — the FormattedValue label(s) from `esi_deliverytypessupported`.
8. **Catalog item type** — the FormattedValue label from `esi_catalogitemtype` (default scope is
   **MOC Courseware**; label any other type plainly when `includeAllItemTypes` widened the search).
9. **Solution area** — the FormattedValue label from `_esi_catalogitemsolutionarea_value`.
10. **Audience** — `esi_audienceprofile` if present, else the Default Role FormattedValue
    (`_esi_targetedroleid_value`), labelled "(default role)" when the fallback is used.
11. **Prerequisites** — `esi_courseprerequisites`, if present.
12. **Certification** — the linked certification, if `_esi_microsoftcertification_value` is present.
13. **Description** — `msdyn_description`, trimmed to a short paragraph if long.
14. **Link** — `esi_externalurl` (preferred) or `esi_mslearnurl` (fallback), rendered as a short
    clickable link, not a raw pasted URL.

### Caveat wording (use verbatim, adapted only for Yes/No)

> MTT indicator shows this item is MTT/CAIP-delivered; it is **not** proof of PD eligibility. PD
> eligibility is reported separately above (`PD eligible`).

### Worked example

```
Source: esiadmin (Dynamics 365)
AI-3016 · Introduction to Generative AI Solutions
Status: Active
MTT indicator: Yes — MTT indicator is not proof of PD eligibility; PD eligibility is reported
separately below.
PD eligible: Yes (credit value: 1)
Official duration: 1 day
Capacity by modality: VILT up to 40 seats
Delivery types supported: VILT, Private
Catalog item type: MOC Courseware
Solution area: Cloud & AI Platforms
Audience: Business users, Developers
Prerequisites: Basic familiarity with Microsoft 365
Description: Introduces generative AI concepts and Microsoft's responsible AI approach, with
hands-on exercises in Copilot and Azure AI Studio.
Link: [Course page on Microsoft Learn](https://learn.microsoft.com/...)
```

## Catalog-item card (single match, backup portal)

The backup portal carries a **different, smaller field set** — never pad it with esiadmin-only
fields (MTT indicator, PD eligible, capacity, solution area) that the portal does not have. Full
field discovery and the fetch workflow are in `references/backup-portal.md`. Card field order:

0. **Source** — `backup portal (tpm-cheat-sheets) — static reference, not the system of record`.
1. **Heading** — `<code> · <title>`.
2. **Status** — `Retired` if the resolved page URL matched the retired-table convention, else
   `Active (unconfirmed — portal does not track retirement independently)`.
3. **Description**, **Duration**, **Audience**, and any other populated row the resolved table page
   carries for that code (e.g. prerequisites, intersecting classes, Learn agenda link, labs) —
   render only the rows actually present on the page.
4. **Link** — the Microsoft Learn path link from the page's Agenda row, if present.

### Worked example

```
Source: backup portal (tpm-cheat-sheets) — static reference, not the system of record
MS-4018 · Draft, analyze, and present with Microsoft 365 Copilot
Status: Active (unconfirmed — portal does not track retirement independently)
Description: Provides a deep dive into MS365 Copilot, helping business users interact with
content and practice drafting docs and PPTs, enhancing Teams meetings, and improving email
workflows.
Duration: 1 day
Audience: Business user
Prerequisite knowledge: M365 (BYOS)
Link: [5 Labs](https://github.com/MicrosoftLearning/MS-4018-Draft-analyze-present-Microsoft-365-Copilot/tree/master/Instructions/Labs)
```

## Multi-result table (several matches)

| Source | Code | Title | MTT indicator | PD eligible | Status | Duration | Solution area |
|---|---|---|---|---|---|---|---|
| esiadmin / backup portal | `<code>` | `<title>` | Yes/No/— | Yes/No/Unknown/— | Active/Retired | `<duration>` | `<area>` |

Use `—` for MTT indicator / PD eligible / solution area on a backup-portal row — never leave the
cell blank in a way that could be misread as "No". Close with: *"Say a code to see the full catalog
item card."* If the row cap was hit, add the truncation disclosure (see `procedure.md` →
*Row-cap handling*) immediately after the table, before the closing invitation.

## Zero-result message

State the exact filter(s) tried (in plain language, not raw OData) and suggest one concrete next
step — a looser keyword, dropping a filter, including retired items or other catalog item types, or
falling back to the backup portal. Never imply the catalog is empty; state that nothing matched the
given filter.
