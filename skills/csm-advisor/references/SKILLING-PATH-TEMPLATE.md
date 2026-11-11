# Stage 4 - Skilling Paths Proposal Template

Goal: turn the Signals Summary and the Skills Map into an evidence-based skilling plan for MTT
review. Produce exactly one Word (`.docx`) document.

The main heading must be exactly **"Skilling Paths proposal"**. Put the customer/scenario name on a
subtitle line underneath, not in the main heading.

The plan is a **proposal**. Never present it as approved until the MTT and the appropriate account
stakeholders have validated it. Do not promise delivery dates, delivery capacity, or cloud support
until validated. Use outcome-based language, not a list of unrelated items.

Do not stop to ask the user anything. Anything uncertain goes under "Missing information",
"Assumptions", or "Items requiring MTT validation".

## Rules

- **Resources come from the Skills Map.** Use only the paths, modules, and links listed in the Skills
  Map (which come from the bundled Microsoft Learn catalog). Copy titles and URLs exactly; never add
  an item or a link of your own. If an audience has a skill no Skills Map item covers, list it under
  "Risks, blockers, and dependencies" and "Items requiring MTT validation".
- **Classes are out of scope.** This version does not map instructor-led classes or courses. Where
  the plan needs workshops, cohorts, or other facilitated activities, describe them as proposed
  activities and list them under "Items requiring MTT validation".
- **Size and delivery** follow the customer's audiences, readiness, capacity, PDC allocation,
  deadlines, and delivery constraints. Do not use size as a diagnosis; a larger package does not
  guarantee more impact. Cover: proposed path(s); target audiences; learning activities; sequence;
  elapsed delivery window; number of cohorts (if known); customer-led practice and reinforcement;
  microlearning opportunities; in-person, virtual, recorded, or blended delivery; dependencies;
  assumptions; items requiring MTT validation.
- **Audiences:** always include a path for Leaders, Champions, Advocates, and End Users, and add the
  other audience groups identified in the Signals Summary (technical leads and administrators;
  security, governance, and finance stakeholders; process owners; makers and developers). Give each
  its role focus, prerequisite skills (and which Skills Map item covers each), ordered items, pacing,
  and expected outcome. Do not assume all audiences need the same activities.
- **Pacing:** use sequence/phases (Phase 1, Phase 2) unless the sources or the user give real dates.
- **Measurement:** before finalizing, identify the agreed customer outcome; baseline metric; metric
  definition; denominator (where relevant); baseline date; metric owner; evidence location;
  delivery-completion date; proposed review date; customer feedback method; and external factors
  that could affect the result. Missing fields are listed, not guessed.
- **Review:** schedule the outcome review 60 to 90 days after actual delivery completion unless a
  different validated business deadline requires an earlier review. At review, recommend one of:
  **Continue**, **Adapt**, **Expand**, **Exit or escalate**. Do not claim skilling alone caused an
  observed change; report its contribution together with other relevant factors.
- **No path selected:** if the Skills Map says no path was selected (customer outcome missing, or a
  non-skilling blocker), do not fabricate a plan. Still produce the document: Part A and sections 6-11
  explain why no path is recommended and what must change, and the final status says so.

## Chat reply (separate from the document)

The detailed plan goes ONLY into the Word document. This is the final message of the run. Reply with
2-3 sentences (the recommended path(s) and audiences covered, the key recommendation, and the final
status), then links to all three documents, then the `Debug - Stage 4` block and a one-line run
summary from [DEBUG-LOG.md](DEBUG-LOG.md):

> I built a proposed skilling plan for <customer> using <primary path> with <supporting path>, covering
> 4 audience groups and 11 Microsoft Learn catalog items. The key recommendation is <one point>.
> Status: Ready for MTT review.
> Documents: [Signals Summary](<link>) | [Skills Map](<link>) | [Skilling Paths proposal](<link>)

## Document structure

The document has two views. Start with the executive view, then the full 16-section internal view,
then the debug appendix.

```text
# Skilling Paths proposal
<Customer / Scenario Name> (subtitle line)

Generated: <date>
Based on: <Signals Summary name/date>; <Skills Map name/date>; selected path(s); <count> catalog items
Status: <Ready for MTT review | More customer information required | Non-skilling blocker
identified | Not ready for delivery planning>
Note: This is a proposal. It is not approved until the MTT and the appropriate account stakeholders
have validated it.

# Part A - Executive CSM Summary
- Customer outcome
- Confirmed signals
- Recommended path or paths (primary and supporting) and why
- Target audiences
- Proposed sequence and expected elapsed window
- Customer responsibilities
- Microsoft responsibilities
- Success measures
- Review timing
- Key risks and dependencies

# Part B - Internal MTT Review
## 1. Customer outcome
## 2. Signal summary
(Detailed signal inventory with evidence, sources, and confidence for each finding; cite Sig ids.)
## 3. Missing information
## 4. Cause confirmation
(Is skilling the primary intervention? Any non-skilling blockers and routing.)
## 5. Readiness assessment
(Ready / Ready with conditions / Not ready / Unknown, with every condition to resolve.)
## 6. Recommended pre-packaged path
(Activate, Deepen, Protect, Convert and Extend - primary, supporting, run sequentially, in parallel,
or by audience.)
## 7. Reason for path selection
(The confirmed signal behind each path.)
## 8. Audience and capability map
(Per audience: role, population, current level, required skills (S ids from the Skills Map),
prerequisite skills, covering catalog items, delivery format, constraints.)
## 9. Proposed skilling plan
(Per audience, ordered learning activities; size and delivery design; sequence; elapsed window;
cohorts; delivery mode; dependencies; assumptions.)
## 10. Microsoft Learn resources
(Catalog items from the Skills Map with links, level, duration, audience, and the skills each
supports; open gaps carried over from the Skills Map.)
## 11. Customer-owned practice and reinforcement
## 12. Risks, blockers, and dependencies
(Including PDC or capacity considerations and technical prerequisites.)
## 13. Measurement plan
(Outcome, baseline metric and definition, denominator, baseline date, metric owner, evidence
location, delivery-completion date, feedback method, external factors.)
## 14. 60-to-90-day review plan
(Proposed review date; decision options Continue / Adapt / Expand / Exit or escalate.)
## 15. Items requiring MTT validation
(Workshops or facilitated activities, cloud validation, delivery capacity, dates, approvals or
corrections.)
## 16. Confidence and assumptions
(Confidence for each key finding; every assumption.)

## Final Status
<One of: Ready for MTT review | More customer information required | Non-skilling blocker
identified | Not ready for delivery planning>

## Appendix - Debug Log
<Stage 4 step table per DEBUG-LOG.md: inputs used, audiences built, items used per audience,
missing measurement fields, validation items raised, and the document creation result.>
```
