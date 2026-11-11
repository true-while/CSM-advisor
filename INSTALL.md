# Installing CSM Advisor in Cowork

**CSM Advisor** turns your Word, PDF, text, PowerPoint, and Excel files (and, if you ask, your
Teams meeting recaps) into role-based Microsoft Learn skilling paths. No technical setup is needed -
just download the plugin and add it in Cowork.

It works in four stages and pauses for your approval after each one:

1. **Collect artifacts** - reads your files and optional Teams meeting recaps.
2. **Detect signals and summarize** - finds the skilling signals and gives you a *Signals Summary* Word document.
3. **Hand-pick Microsoft Learn modules** - proposes a shortlist for you to approve or edit.
4. **Build skilling paths** - gives you a *Skilling Paths proposal* Word document for Leaders, Champions, Advocates, and End Users, based on role and prerequisite skills.

## 1. Download

Download the plugin ZIP using the link below. It always points to the newest version - you don't
need to build or unzip anything yourself:

[**Download CSM Advisor**](https://github.com/true-while/CSM-advisor/releases/latest/download/CSM-advisor.zip)

<!-- latest-version:start -->
Latest published version: **v1.1.5** (released 2026-11-11) - [release notes](https://github.com/true-while/CSM-advisor/releases/tag/v1.1.5)
<!-- latest-version:end -->

Keep the downloaded `CSM-advisor.zip` file intact - don't unzip it or edit its contents.
(Every past version also stays available on the [Releases page](https://github.com/true-while/CSM-advisor/releases) if you ever need an older one.)

## 2. Install in Cowork

1. Open **Cowork > Customize > Add > Upload**.
2. Select **choose a file** and pick the `CSM-advisor.zip` you downloaded, or drag and drop it into the dialog.
   
![Add plugin](addplugin.png)

1. Follow the on-screen installation and consent steps.
2. Confirm **CSM Advisor** appears in your installed plugins list.




## 3. Try it out

Start a new Cowork conversation and paste in the prompt below (attach 2 or more files first - any
mix of Word, PDF, text, PowerPoint, and Excel):

```text
Use CSM Advisor to find skilling signals in these files and build skilling paths:
<attach/select 2+ files in Word, PDF, text, PowerPoint, and/or Excel format>.
Include my Teams meeting recaps from the last 2 weeks.
```

CSM Advisor replies after each stage with a short message (2-3 sentences) and waits for you to say
"approve" or request changes. You get a Word document after Stage 2 (Signals Summary) and after
Stage 4 (Skilling Paths proposal); Stage 3 is a shortlist in chat. Say "run all stages without
stopping" if you don't want the approval pauses.

## Updating to a newer version

When a new version is published, repeat the install steps above with the same download link -
Cowork will update the existing plugin in place rather than installing a second copy.

---

## For maintainers

To ship a change to this plugin:

1. Make your changes under `skills/csm-advisor/`.
2. Push to `main`. Every push triggers the release workflow
   ([.github/workflows/release.yml](.github/workflows/release.yml)), which automatically
   increments the patch version (e.g. `1.1.3` -> `1.1.4`), updates `version` in `manifest.json` and
   `SKILL.md`, builds the ZIP, publishes it as a new GitHub Release tagged `v<version>`, and updates
   the "Latest published version" line above - the download link always serves the newest release.
   (You can also trigger the workflow manually from the **Actions** tab.)

You don't need to edit the version by hand. To start a new major/minor line, set `version` in
`manifest.json` to e.g. `1.2.0` (with no existing `v1.2.0` tag) and push; later pushes continue from
there. Run `git pull` after a push to get the bot's version-bump commit.

Keep the same `id` (GUID) in `manifest.json` across updates so Cowork treats it as an update to the
existing plugin rather than a new installation. The release workflow never overwrites or replaces an
already-published version.
