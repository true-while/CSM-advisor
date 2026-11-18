# mtt-report-builder — glyphs

**Purpose:** Glyph lookup and resolution rules for FY27 Learning Lab report accents, including dynamic SharePoint fetch and bundled fallbacks.
**Loaded by:** `mtt-report-builder` on demand (see SKILL.md → Additional resources)

---

FY27 reports may use the **Learning Lab glyph library** as accents. Two visual registers:

- **FY27 multicolour 3-D glyphs** — gradient-filled, ~16–37 KB SVG. For **prominent** accents (KPI tiles,
  section headers, hero). Loud and on-brand; use **sparingly** — never one on every row.
- **Monochrome line glyphs** — `currentColor`, ~1 KB. For **subtle** placements (the footer privacy line,
  inline labels). They tint to the surrounding text colour. This is what `{{GLYPH_PRIVACY}}` uses.

Match the register to the placement: a small muted footer wants a monochrome glyph, not a 3-D tile.

## Resolution chain (dynamic → bundled → omit)

1. **Dynamic (preferred for the full library / latest asset):** fetch from SharePoint (below). Use when a
   caller wants a specific FY27 glyph as a prominent accent and SharePoint is reachable.
2. **Bundled fallback (offline-safe):** inlined as text in supported files — no separate `.svg` asset files (that extension isn't packageable):
   - the **monochrome set** in *Bundled monochrome set* below — `{{GLYPH_PRIVACY}}` uses the **privacy** block (the footer default).
  - the real FY27 multicolour shield in *Bundled FY27 multicolour set* below (brand-accurate offline, PNG-free).
3. **Omit gracefully:** if no glyph resolves, leave the `{{GLYPH_*}}` placeholder **empty**. The report stays valid.

**`{{GLYPH_PRIVACY}}` default:** inline the **privacy** block from *Bundled monochrome set* below (bundled monochrome shield), so the
footer renders even with no network. Swap to the FY27 multicolour shield from *Bundled FY27 multicolour set* below (or a dynamic fetch) only if a caller wants
the full-colour brand mark.

## Dynamic fetch (Learning Lab SharePoint)

- **Site** `TheLearningLab`: `microsoft.sharepoint.com,425f3e43-be21-4a03-87a9-210e56d17e7e,7f056c50-df01-42ef-9e72-94b7d56ea6ea`
- **Drive** (default document library): resolve fresh with `GetDefaultDrive(site_id=<above>)` (it returned a
  `drive_1` alias / drive id `b!Qz5fQiG-A0qHqSEOVtF-flBsBX8B3-9CnnKUt9Vupupde120kVO8RZCJzMg-ZWNd`).
- **Library path:**
  `Learning Lab Teamwide (FTE ALL)/Content Development Resources/ILT Trainer File Templates/ILT PPT Template/Glyph icon library/<GlyphName>/_SVG/<GlyphName> - {32|128} px -- Flat.svg`

**Flow:**
1. `SearchDrive(drive_id, query="<GlyphName>")` → the glyph folder (and its `_SVG` subfolder).
2. `GetDriveChildren(drive_id, item_id=<_SVG folder id>)` → the 32 px / 128 px SVG file ids.
3. `ReadFileContent(drive_id, item_id=<svg file id>)` → downloads the SVG; inline its `<svg>…</svg>`.

Use **32 px** for inline accents, **128 px** for hero/large. If SharePoint is unreachable / the site moves / a
403 or empty result comes back, **do not retry blindly** — drop to the bundled fallback (step 2) and note nothing
to the user (a glyph is decorative).

**Concept → glyph folder** (verified names in the library):

| Report concept | Glyph folder |
|---|---|
| privacy / data protection | `Shield_Privacy` |
| results / analytics / KPIs | `Results` |
| trainer / instructor | `Instructor` |
| schedule / duration / time | `Time` |
| support / escalation | `Support` |
| achievement / certification / follow-on | `Trophy` · `Trophy_CSC` |
| learning path / Learn | `Learn` |
| link / URL | `Link` |
| resources / files | `Folder_Resources` · `Resources_Details` |
| tools / setup | `Tools` |
| process / workflow | `Process` |
| speed / performance | `Speed` |
| network / connectivity | `Network` |
| architecture | `Architecture` |
| research | `Research` |

Browse `SearchDrive(drive_id, "Glyph icon library")` for the full set (the library grows).

## Inlining rules

- Inline the raw `<svg>` element (keeps the report **self-contained — zero external refs**, which the validator
  requires). Data-URI textures *inside* an FY27 glyph are inline, not external — they pass.
- **Size via CSS**, not the SVG's own width/height (e.g. `.report-footer svg{width:16px;height:16px}`).
- **Multicolour FY27 glyphs reuse internal ids** (`pattern0`, `image0_…`, clip ids). If you inline **more than
  one** on a page, **suffix each glyph's ids uniquely** (e.g. `pattern0` → `pattern0_time`) or SVGs will
  cross-reference and render wrong. Monochrome glyphs below have no ids — safe to repeat.
- Monochrome glyphs use `currentColor` → they inherit text colour; set the colour on the parent element.

## Bundled monochrome set (copy inline; `currentColor`, 24×24)

**privacy** — the footer default for `{{GLYPH_PRIVACY}}`
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M12 2 4 5v6c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V5l-8-3Z" fill="currentColor" opacity=".16"/><path d="M12 2 4 5v6c0 5 3.4 8.3 8 10 4.6-1.7 8-5 8-10V5l-8-3Z" stroke="currentColor" stroke-width="1.4" stroke-linejoin="round"/><path d="m8.7 11.7 2.2 2.2 4.4-4.6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
```
**time** — clock
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="12" r="9" stroke="currentColor" stroke-width="1.5"/><path d="M12 7v5l3.5 2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
```
**results** — trend chart
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M4 4v16h16" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M7 15l3-4 3 2 4-6" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/></svg>
```
**instructor** — person
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><circle cx="12" cy="8" r="3.2" stroke="currentColor" stroke-width="1.5"/><path d="M5.5 19a6.5 6.5 0 0 1 13 0" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>
```
**trophy** — achievement
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M7 4h10v4a5 5 0 0 1-10 0V4Z" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/><path d="M7 6H4v1a3 3 0 0 0 3 3M17 6h3v1a3 3 0 0 1-3 3M10 15h4M9 20h6M12 15v5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
```
**link**
```svg
<svg viewBox="0 0 24 24" fill="none" aria-hidden="true"><path d="M9.5 14.5l5-5M8.5 12H7a3.5 3.5 0 0 1 0-7h2M15.5 12H17a3.5 3.5 0 0 1 0 7h-2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
```

## Bundled FY27 multicolour set (copy inline)

**privacy_fy27** — brand multicolour privacy shield (PNG-free)
```svg
<svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <path d="M10.2338 26.8738L14.8048 29.352C15.5501 29.7561 16.4493 29.7549 17.1935 29.349L21.7885 26.8426C25.0011 25.0903 27 21.7231 27 18.0637V8.33403C27 7.34311 26.4147 6.44571 25.5079 6.04621L16.6196 2.13044C16.4244 2.04442 16.2133 2 16 2C15.7867 2 15.5756 2.04442 15.3804 2.13044L6.49209 6.04621C5.58527 6.44571 5 7.34311 5 8.33403V18.0827C5 21.7512 7.00874 25.1252 10.2338 26.8738Z" fill="#8DC8E8"/>
  <path d="M11.1465 25.2719L15.265 27.5869C15.7214 27.8435 16.2786 27.8435 16.735 27.5869L20.8535 25.2719C23.4148 23.8322 25 21.1226 25 18.1844V9.01646C25 8.40519 24.6291 7.85506 24.0624 7.62588L16.6039 4.60948C16.4252 4.53721 16.2342 4.50006 16.0415 4.50006H15.9585C15.7658 4.50006 15.5748 4.53721 15.3961 4.60948L7.93761 7.62588C7.37093 7.85506 7 8.40519 7 9.01646V18.1844C7 21.1226 8.58524 23.8322 11.1465 25.2719Z" fill="url(#fy27ShieldGradient)"/>
  <path d="M11.1465 25.2719L15.265 27.5869C15.7214 27.8435 16.2786 27.8435 16.735 27.5869L20.8535 25.2719C23.4148 23.8322 25 21.1226 25 18.1844V9.01646C25 8.40519 24.6291 7.85506 24.0624 7.62588L16.6039 4.60948C16.4252 4.53721 16.2342 4.50006 16.0415 4.50006H15.9585C15.7658 4.50006 15.5748 4.53721 15.3961 4.60948L7.93761 7.62588C7.37093 7.85506 7 8.40519 7 9.01646V18.1844C7 21.1226 8.58524 23.8322 11.1465 25.2719Z" fill="white" fill-opacity="0.08" style="mix-blend-mode:soft-light"/>
  <path fill-rule="evenodd" clip-rule="evenodd" d="M16 15.5C17.933 15.5 19.5 13.933 19.5 12C19.5 10.067 17.933 8.5 16 8.5C14.067 8.5 12.5 10.067 12.5 12C12.5 13.933 14.067 15.5 16 15.5ZM11.292 16.8656C11.5041 16.6327 11.8045 16.5 12.1195 16.5H19.8805C20.1955 16.5 20.4959 16.6327 20.708 16.8656C20.8959 17.0717 21 17.3406 21 17.6195V18.4464C21 19.1243 20.747 19.7777 20.2905 20.2788L20.1836 20.3961C19.4949 21.1521 18.5886 21.6758 17.5897 21.8951C16.5424 22.125 15.4576 22.125 14.4103 21.8951C13.4114 21.6758 12.5051 21.1521 11.8164 20.3961L11.7095 20.2788C11.253 19.7777 11 19.1243 11 18.4464V17.6195C11 17.3406 11.1041 17.0717 11.292 16.8656Z" fill="white"/>
  <defs>
    <linearGradient id="fy27ShieldGradient" x1="7" y1="4.5" x2="25" y2="27.8" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#0A8BE0"/>
      <stop offset="1" stop-color="#0069C2"/>
    </linearGradient>
  </defs>
</svg>
```
