# Installing CSM Advisor in Cowork

**CSM Advisor** helps CSMs, account teams, MTTMs, and MTTs turn customer materials - Word, PDF, text,
PowerPoint, and Excel files, emails, usage reports, notes, and (if you ask) Teams meeting recaps -
into an evidence-based, role-based skilling plan. No technical setup is needed - just download the
plugin and add it in Cowork.

It runs five stages in one go and does not stop to ask you questions:

1. **Collect artifacts** - reads your files and optional Teams meeting recaps.
2. **Detect signals and summarize** - extracts the customer outcome, adoption and usage signals, audiences, readiness, non-skilling blockers, and missing information into a *Signals Summary* Word document. Every signal records its source, date, and confidence (Confirmed, Probable, or Unconfirmed).
3. **Select the path** - recommends Activate, Deepen, Protect, or Convert and Extend (alone or combined) from confirmed signals.
4. **Map required skills** - maps every required training skill to Microsoft Learn modules and learning paths from a catalog bundled with the plugin (a snapshot refreshed with each release). The result is a separate *Skills Map* Word document with the catalog links.
5. **Build the skilling plan** - gives you a *Skilling Paths proposal* Word document: an executive summary and a full internal MTT review by audience, with a measurement plan and a 60-to-90-day review.

Anything missing is listed as missing information or an assumption in the documents instead of being asked about. Debug logging is off by default; add "with debug" to your request to get a debug block with each stage's message and a debug log at the end of each document.

The result is always a **proposal** for MTT and account-stakeholder validation - never an approved plan.

## 1. Download

Download the plugin ZIP using the link below. It always points to the newest version - you don't
need to build or unzip anything yourself:

[**Download CSM Advisor**](https://github.com/true-while/CSM-advisor/releases/latest/download/CSM-advisor.zip)

<!-- latest-version:start -->
Latest published version: **v1.1.19** (released 2026-11-13) - [release notes](https://github.com/true-while/CSM-advisor/releases/tag/v1.1.19)
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

Start a new Cowork conversation and paste in the prompt below (attach the customer materials first -
files in Word, PDF, text, PowerPoint, or Excel format, plus anything else you have, such as email
threads, usage reports, and renewal notes):

```text
Use CSM Advisor to analyze this customer's materials, extract signals and readiness, and
recommend a skilling path: <attach/select the customer files>.
Include my Teams meeting recaps for <customer> from the last 2 weeks.
```

CSM Advisor runs all five stages without stopping to ask questions. Each stage posts a short message
(2-3 sentences). You get three Word documents: the Signals Summary (Stage 2), the Skills Map (Stage 4,
required skills mapped to Microsoft Learn catalog items with links), and the Skilling Paths proposal
(Stage 5). Add "with debug" to the prompt if you also want a debug block and a debug log. If the customer outcome is
missing, or the main blocker is not a skilling gap, it still finishes and states clearly what is
missing instead of forcing a recommendation.

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
   `SKILL.md`, downloads a fresh Microsoft Learn catalog into the skill
   (`scripts/build_learn_catalog.py` writes `skills/csm-advisor/ms-learn-catalog.json`, bundled in
   the ZIP but not committed), builds the ZIP, publishes it as a new GitHub Release tagged
   `v<version>`, and updates
   the "Latest published version" line above - the download link always serves the newest release.
   (You can also trigger the workflow manually from the **Actions** tab.)

You don't need to edit the version by hand. To start a new major/minor line, set `version` in
`manifest.json` to e.g. `1.2.0` (with no existing `v1.2.0` tag) and push; later pushes continue from
there. Run `git pull` after a push to get the bot's version-bump commit.

To package locally, run `python scripts/build_learn_catalog.py` first, then `./scripts/package.ps1`.
The catalog is a snapshot of the public Learn catalog API: it is refreshed only when a release is
built, and the build fails rather than shipping an empty or oversized file (Cowork limits each
companion file to 5 MB).

Keep the same `id` (GUID) in `manifest.json` across updates so Cowork treats it as an update to the
existing plugin rather than a new installation. The release workflow never overwrites or replaces an
already-published version.
