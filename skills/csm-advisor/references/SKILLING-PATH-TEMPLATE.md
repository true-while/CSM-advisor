# Stage 4 - Skilling Paths Template and Learner Groups

Goal: for each learner group, build an ordered skilling path from the **approved** Microsoft Learn
modules, based on the group's role and prerequisite skills. Produce exactly one Word (`.docx`)
document.

The main heading must be exactly **"Skilling Paths proposal"**. Put the scenario/customer name on a
subtitle line underneath, not in the main heading.

## Learner groups

Build one path for each of these groups (omit a group only if the user says to):

| Group | Role focus | Typical emphasis |
|-------|-----------|------------------|
| **Leaders** | Executive and management sponsors who set direction and remove blockers | Strategy, value and ROI, governance and risk, sponsoring adoption |
| **Champions** | Hands-on internal experts who drive adoption and support peers | Deep product skills, administration, scenarios, coaching others |
| **Advocates** | People who promote and share best practices across the organization | Core skills, success stories, communicating value, community |
| **End Users** | Day-to-day users of the tools | Getting started, everyday tasks, safe and effective use |

Adjust the emphasis to what the signals say (e.g. a group that is already trained can start at a
higher level).

## Rules

- Use only modules approved in Stage 3. Do not add new modules at this stage; if a group has a need
  no approved module covers, list it under "Open gaps" and offer to go back to Stage 3.
- **Prerequisite skills:** for each group, list the skills someone should have before starting and
  which approved module (if any) covers each. Base them on the signals and the prerequisites the user
  confirmed in Stage 3. Mark inferred ones as assumptions.
- **Order modules** so prerequisites come first, then core skills, then advanced or role-specific
  topics. A module may appear in several groups' paths.
- Add milestones or pacing (e.g. weeks or phases) only when the sources or the user give a timeline;
  otherwise use relative phases (Phase 1, Phase 2) without invented dates.
- Skip content the signals show a group already completed.

## Chat reply (separate from the document)

The detailed plan goes ONLY into the Word document. In chat reply with 2-3 sentences (how many
groups and modules the plan covers, the key recommendation, and a link to the document):

> I built skilling paths for 4 learner groups using 12 approved Microsoft Learn modules. The main
> recommendation is <one key point>. Full details: [Skilling Paths proposal](<link to the .docx>)

## Document structure

```text
# Skilling Paths proposal
<Scenario/Customer Name> (subtitle line)

Generated: <date>
Based on: <Signals Summary name/date>; <count> approved Microsoft Learn modules

## Overview
<3-5 sentences: the skilling need, who is covered, and the overall approach.>

## Key Signals Driving This Plan
- <Signal> - <why it matters for skilling>

## Skilling Path - Leaders
- Role focus: <what this group does and needs>
- Prerequisite skills: <skill> (covered by: <module or "assumed / not covered">)
- Path:
  1. <Module title> - <link> - <level, duration> - <why this, why now>
  2. ...
- Milestones / pacing: <phases or timeline from the sources, if any>
- Expected outcome: <what the group can do after completing the path>

## Skilling Path - Champions
<same structure>

## Skilling Path - Advocates
<same structure>

## Skilling Path - End Users
<same structure>

## Module Summary
| Module | Link | Level | Duration | Leaders | Champions | Advocates | End Users |
|--------|------|-------|----------|---------|-----------|-----------|-----------|
| <title> | <URL> | <level> | <approx.> | x | x | | x |

## Open Gaps and Assumptions
- <Need not covered by an approved module>
- <Assumption (e.g. an inferred prerequisite) the user should confirm>

## Next Steps
- <Concrete follow-up actions and owners, if known from the sources>
```
