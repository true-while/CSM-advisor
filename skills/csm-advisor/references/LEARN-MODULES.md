# Mapping Required Skills to the Microsoft Learn Catalog (Stage 4)

Goal: turn the skill gaps found in Stages 1-3 into a list of required training skills, and map each
skill to Microsoft Learn modules or learning paths. The result goes into the Skills Map document
(see [SKILLS-MAP-TEMPLATE.md](SKILLS-MAP-TEMPLATE.md)). Nothing here waits for user approval.

Instructor-led classes and courses are out of scope for this version: do not search for them, map
to them, or list them.

## Source order

1. **Live Microsoft Learn catalog API (default).** The deployed `scm-advisor` service
   (`https://scm-advisor.azurewebsites.net`) mirrors the public Microsoft Learn catalog and is
   refreshed at least daily. Search it only with `scripts/search_catalog.py`, which calls the
   service's `/search` endpoint; do not call the API directly. It reports `generated_at`: state
   that date in the Skills Map.
2. **Bundled snapshot, automatic fallback.** If the live service cannot be reached,
   `scripts/search_catalog.py` falls back automatically to `ms-learn-catalog.json` in the skill
   folder (a snapshot rebuilt at every plugin release) and marks the output `"source":
   "bundled-snapshot"`. No separate action is needed; just read the script's output.
3. **Live Microsoft Learn web search**, only if the script fails entirely (service unreachable
   and no bundled snapshot) or a skill has no usable match from either source. Use whatever Learn,
   documentation, or web-search tool Cowork provides and log that the fallback was used.
4. **No source works:** list the skill under Open Gaps with the reason and continue. Never guess.

## Rules

- **Never invent** module titles, learning paths, links, levels, or durations. Use only values
  returned by the catalog script or a live Learn search, and copy links exactly.
- **Verify fit:** a match's title, summary, level, and roles must fit the skill and the audience.
  Catalog filters and the script's `strength` label are heuristics, so reject look-alikes and
  anything `weak` unless the title clearly fits.
- Prefer a short, well-matched list over an exhaustive one: at most 3 catalog items per skill.
- Skip content the signals show an audience already completed.
- The catalog is a snapshot; links can change. State the snapshot date in the document.

## How to analyze the skill set

1. **Derive the required skills.** From the Stage 2 Signals Summary and the Stage 3 path, extract each skill gap,
   capability need, priority workflow, and selected-path focus, grouped by audience. Give each an
   id (S1, S2, ...), a short name, why it matters to this customer, the audiences, the signal
   evidence, a priority, and current -> target level when known.
2. **Write search phrases.** One to three short phrases per skill, using the product and the skill
   (for example "copilot readiness rollout", "build agents copilot studio", "prompt engineering
   business users"). Check the available product, role, and level ids with
   `python scripts/search_catalog.py --facets`.
3. **Search every skill**, in one call where possible:

   ```text
   python scripts/search_catalog.py "<skill 1 phrase>" "<skill 2 phrase>" --level beginner --level intermediate --limit 5
   ```

   Filters: `--product <id>`, `--role <id>`, `--level <id>`, `--type module|path`. Use the ids shown
   by `--facets`; drop a filter if it removes good matches (note it in the log when debug is on). The
   output lists each match's title, link, level, minutes, a `strength` label, and a `debug` object
   (copy it into the log only when debug is on). A learning path match also lists the uids of its
   modules; to resolve a module uid to its title, or to see which paths a module belongs to, run
   `python scripts/search_catalog.py --item <uid> --expand` on the chosen candidate.
4. **Go over the whole skill set**, not one skill at a time:
   - Choose the best match for each skill; prefer a learning path when several of a skill's best
     matches are modules of the same path.
   - Merge duplicates: an item that serves several skills or audiences is listed once.
   - Match level to the audience's current skill level from the Signals Summary.
   - Record coverage per skill: Covered, Partly covered, or Not covered.
5. Put any skill without a fitting match under **Open Gaps** with the phrases tried. Do not pad.
6. Only when debug logging is on, log every search and decision as described in
   [DEBUG-LOG.md](DEBUG-LOG.md). Then write the Skills Map document and continue to Stage 5.
