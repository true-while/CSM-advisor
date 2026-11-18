# mtt-class-lookup — data model

**Purpose:** The esiadmin tables and key fields this skill reads, and the v2 envelope fields it consumes from `mtt-esiadmin-lookup`.
**Loaded by:** `mtt-class-lookup` on demand (see SKILL.md → Additional resources)

---

## Data model

This skill consumes the resolver envelope from `mtt-esiadmin-lookup` and should avoid direct table walks.

For the full table relationships and lookup procedure, see:
- `mtt-esiadmin-lookup/references/data-model.md`
- `mtt-esiadmin-lookup/references/procedure.md`

### Envelope fields consumed by class-lookup

| Envelope block | Fields used |
|---|---|
| `delivery` | `classId`, `workOrderId`, `courseCode`, `courseTitle`, `customer`, `officialStart`, `officialEnd`, `deliveryType`, `studentLabCode`, `skillableClassId`, `lxpUrl`, `registrationFormUrl`, `readableEventId`, `surveyUrl`, `catalog`, `support`, `tpmInstruction`, `status`, `modality`, `primaryLanguage`, `counts`, `isCanceled`, `dayCount`, `registrationHealth`, `capacity`, `booking`, `liveCheckin` |
| `roster` | `students`, `activeCount`, `checkinCounts`, `roleFamilies`, `orgs` |
| `identity` | `profile` (for the self-scoped trainer profile basics branch) |

> **v2 envelope enrichment (from `mtt-esiadmin-lookup`):** the delivery anchor now also carries
> `delivery.catalog` (course title / prerequisites / MS Learn URL — **opt-in via `includeCatalog`**), a
> `delivery.customer` (**`{name, tpid}` by default from the booking's `CUSTOMER:` text; enriched with account
> city/country only via `includeCustomerAccount`**), `delivery.support` (support desk + SLAs, TPM/TPC, trainer-report /
> onboarding / lab-registration links), `delivery.status` + `delivery.modality` +
> `delivery.primaryLanguage` + extra `delivery.counts`, `delivery.isCanceled` (canceled-delivery boolean),
> `delivery.dayCount` (number of delivery days), `delivery.registrationHealth` (Green/Yellow/Red), `delivery.capacity` (`{value, basis}`), and `delivery.booking.{bookingStatus, workOrderId,
> sessionId}`; `mode:roster` also returns `roster.checkinCounts` (the authoritative attendance tally) over a
> test/admin-excluded roster. **Consume these from the envelope — don't re-query their source tables here.**
> All are best-effort: show only non-null values.
>
> **Lab status (has-lab):** `delivery.studentLabCode` / `delivery.skillableClassId` are **frequently null** (null on all upcoming AI-3016 deliveries) — do **not** infer "no labs" from their absence. The delivery-independent source of truth is the catalog-level **Lab Series** (`esi_labseries.esi_provider` / `esi_enabled`, keyed to the catalog item) surfaced by `mtt-esiadmin-lookup`. That table is currently **read-restricted (HTTP 403)**, so treat has-lab as *unknown* (not *no*) when it can't be read.
