# mtt-report-builder — theme (canonical FY27 skin CSS)

**Purpose:** the canonical FY27 Learning Lab theme core — the single source of truth for the report skin. Both HTML templates embed this CSS verbatim; change it here, then re-sync both templates.
**Loaded by:** `mtt-report-builder` on demand (see SKILL.md → Additional resources)

---

Embed the CSS below (the fenced block contents) **verbatim** into the report `<style>`; report-specific component CSS goes *after* it.

```css
/* =============================================================================
   MTT REPORT — FY27 LEARNING LAB THEME  ·  CANONICAL SOURCE OF TRUTH
   -----------------------------------------------------------------------------
   EVERY report's <style> MUST embed this block VERBATIM — info, adhoc, and any
   novel / unlisted report type that matches no template. Add report-specific
   component CSS AFTER it. Never hand-author theme CSS, never hardcode palette
   hexes, never ship a report without it. base-template.html and
   delivery-info-template.html both embed this core; if the theme changes, edit
   it HERE and re-sync both templates.

   DARK-MODE INVARIANT (do not break): theme-varying backgrounds — e.g. the header
   gradient — are driven by CSS variables set per :root (--head-grad). NEVER
   override them with `@media (prefers-color-scheme:dark){ .selector{…} }`: an
   equal-specificity override loses to source order and renders the LIGHT value in
   dark mode. If a value differs between light and dark, add a token to each :root.
   ============================================================================= */
  /* FY27 Learning Lab palette — warm off-white base, deep navy ink, purple/teal/blue accents */
  :root{
    --bg:#fff8f3; --card:#ffffff; --ink:#091f2e; --muted:#5a6a77;
    --line:#eee6de; --accent:#8661c5; --accent-soft:#efeafb;
    --neutral:#f2ede6; --neutral-ink:#4a5560;
    --warn-ink:#8a6d00; --warn-soft:#fff4ce;
    --bar:#389a91; --bar-track:#efe8df; --field:#faf6f1;
    --head-grad:linear-gradient(135deg,#fff8f3 0%,#f3ecfb 55%,#e9f4f1 100%);
    --fh:'Segoe UI Semibold','Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;
  }
  @media (prefers-color-scheme: dark){
    :root{
      --bg:#091f2e; --card:#12293a; --ink:#fff8f3; --muted:#9fb2c0;
      --line:#22384a; --accent:#c5b4e3; --accent-soft:#20304a;
      --neutral:#1c3345; --neutral-ink:#d5e0ea;
      --warn-ink:#ffd95e; --warn-soft:#3d3413;
      --bar:#49c5b1; --bar-track:#1c3140; --field:#0e2536;
      --head-grad:linear-gradient(135deg,#132a3c,#1a2c48 55%,#123338);
    }
  }
  *{box-sizing:border-box}
  body{margin:0; background:var(--bg); color:var(--ink);
    font-family:'Segoe UI',-apple-system,BlinkMacSystemFont,Roboto,Helvetica,Arial,sans-serif;
    line-height:1.45; padding:24px}
  h1,h2,.eyebrow{font-family:var(--fh)}
  .wrap{max-width:960px; margin-inline:auto}
  .card{background:var(--card); border:1px solid var(--line); border-radius:10px;
    padding:20px 24px; margin-block-end:18px}
  .head{background:var(--head-grad); border-inline-start:5px solid var(--accent)}
  .eyebrow{font-size:12px; letter-spacing:.08em; text-transform:uppercase; color:var(--muted); margin:0}
  h1{font-size:26px; margin:.15em 0 .1em}
  .subtitle{font-size:16px; color:var(--muted); margin:0}
  h2{font-size:13px; letter-spacing:.06em; text-transform:uppercase; color:var(--muted);
     margin:0 0 14px; border-block-end:1px solid var(--line); padding-block-end:8px}
  .sub{font-size:12px; letter-spacing:.05em; color:var(--muted); margin:0 0 8px}
  .badge{font-size:12px; font-weight:600; padding:4px 10px; border-radius:999px; white-space:nowrap}
  .report-footer{font-size:12px; color:var(--muted); line-height:1.65}
  .report-footer p{margin:0 0 6px} .report-footer p:last-child{margin:0}
  .report-footer strong{color:var(--ink)}
  .report-footer svg{width:16px; height:16px; vertical-align:-3px; margin-inline-end:6px}
  @media print{ body{background:#fff; padding:0} .card{break-inside:avoid; border-color:#ccc} }
```
