# Installing Learn Path Adviser in Cowork


This folder is the source for the **Learn Path Adviser** plugin. Cowork installs plugins from a
ZIP archive containing `manifest.json`, the icon PNGs, and the `skills/` folder - you do not
install this source folder directly.

## Download (always the latest version)

A GitHub Actions workflow ([.github/workflows/release.yml](.github/workflows/release.yml)) builds
and publishes the ZIP automatically, so you don't need to build it yourself. The link below always
resolves to the newest published version:

```text
https://github.com/true-while/Learn-Path-Adviser/releases/latest/download/learn-path-adviser.zip
```

<!-- latest-version:start -->
Latest published version: **v1.0.3** (released 2026-11-04) - [release notes](https://github.com/true-while/Learn-Path-Adviser/releases/tag/v1.0.3)
<!-- latest-version:end -->

Every version is also kept as its own release (tagged `v<version>`) on the
[Releases page](https://github.com/true-while/Learn-Path-Adviser/releases), so you can install an
older version if needed.

## 1. Build the ZIP (manual/local alternative)

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

1. Download `learn-path-adviser.zip` (from the stable link above, a specific release, or your own
   local build) to a machine with access to Cowork.
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
3. Push to `main`. The release workflow detects the version bump, builds the ZIP, and publishes it
   as a new GitHub Release tagged `v<version>` - the stable "latest" link then points at it
   automatically. (You can also build locally with `./scripts/package.ps1`, or trigger the workflow
   manually from the **Actions** tab.)
4. In Cowork, open **Customize > Plugins**, select Learn Path Adviser, and upload the new ZIP to
   update it in place.

Keep the same `id` (GUID) in `manifest.json` across updates so Cowork treats it as an update to the
existing plugin rather than a new installation. The release workflow never overwrites or replaces an
already-published version - it only publishes a new release when the version actually changes.
