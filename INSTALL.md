# Installing Learn Path Adviser in Cowork


This folder is the source for the **Learn Path Adviser** plugin. Cowork installs plugins from a
ZIP archive containing `manifest.json`, the icon PNGs, and the `skills/` folder - you do not
install this source folder directly.

## 1. Build the ZIP

From this folder, run the packaging script:

```powershell
./scripts/package.ps1
```

This produces `dist/learn-path-adviser.zip` containing exactly:

```text
manifest.json
color.png
outline.png
skills/
  learn-path-adviser/
    SKILL.md
    references/
      SUPPORTED-FORMATS.md
      SUMMARY-TEMPLATE.md
```

## 2. Install in Cowork

1. Download/copy `dist/learn-path-adviser.zip` to a machine with access to Cowork.
2. Open **Cowork > Customize > Plugins > Add plugin**.
3. Select **choose a file** and pick `learn-path-adviser.zip`, or drag and drop it into the dialog.
4. Follow the on-screen installation and consent steps.
5. Confirm **Learn Path Adviser** appears in the installed plugins list.

Tenant policy must permit plugin installation. If installation is blocked, contact your
administrator - this package does not bypass any policy.

## 3. Verify

Start a new Cowork conversation and try:

```text
Summarize these files into one combined summary using Learn Path Adviser: <attach/select 2+ files
in Word, PDF, text, PowerPoint, and/or Excel format>.
```

Confirm the response is a single combined summary (not one summary per file) and that it follows
the structure in `skills/learn-path-adviser/references/SUMMARY-TEMPLATE.md`.

## 4. Updating

To ship an update:

1. Make your changes under `skills/learn-path-adviser/`.
2. Bump `version` in `manifest.json` and the `metadata.version` field in `SKILL.md`.
3. Re-run `./scripts/package.ps1` to produce a new `dist/learn-path-adviser.zip`.
4. In Cowork, open **Customize > Plugins**, select Learn Path Adviser, and upload the new ZIP to
   update it in place.

Keep the same `id` (GUID) in `manifest.json` across updates so Cowork treats it as an update to the
existing plugin rather than a new installation.
