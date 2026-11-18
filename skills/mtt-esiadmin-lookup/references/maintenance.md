# mtt-esiadmin-lookup — maintenance notes

**Purpose:** Operational notes for `includeOrgIndustry` domain-first employer resolution, including privacy/safety constraints and deterministic fallback behavior.
**Loaded by:** `mtt-esiadmin-lookup` on demand (see SKILL.md -> Additional resources), used by *Roster resolution* step 8.

---

## Privacy and data policy

- This reference is intentionally generic and must contain no real customer data.
- Do not include real domains, organisation names, TPIDs, or tenant-specific examples.
- Resolution is on-the-fly per run and uncached (no persistent map, no session cache, no hardcoded fallback table).

## Domain-first org resolution notes

Use this deterministic chain per distinct `emailDomain` when `includeOrgIndustry` is enabled:

1. Normalize domain key from `emailaddress1` (lowercase host, strip leading `www.`).
2. Query `accounts` where `websiteurl contains <emailDomain>`.
3. If multiple candidates return, apply deterministic best-match ranking.
4. If unresolved, fallback to learner `_parentcustomerid_value` account (`source: "crm-link"`).
5. If still unresolved, emit domain label only (`source: "domain-only"`, null `industry`/`tpid`).

No guessing of `industry` or `tpid` is allowed.

## Output/source expectations

- Emit `roster.orgs` items as `{ employer, count, industry, tpid, source }`.
- Allowed `source` values: `domain-account` | `crm-link` | `domain-only`.
- Unresolved `industry` is expected and should remain null.

## Operational cautions

- Domain matching is partial by nature; some organisational domains will not have an account match.
- Keep this file generic and non-identifying at all times.
- If future behavior changes, update both this file and the includeOrgIndustry branch in `references/procedure.md`.
