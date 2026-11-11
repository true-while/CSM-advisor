# Microsoft Teams Meeting Recaps

Optional additional source. Recaps are treated like any other input: extracted, then merged into
the ONE combined analysis. This skill only reads recaps; it never posts to Teams, edits meetings, or
shares content.

## Access and permissions

- Use only the Microsoft 365 / Teams capabilities that Cowork already exposes for the **current
  signed-in user**. This skill cannot grant itself access.
- Read only meetings the user can already open (organizer, attendee, or shared recap). Never
  attempt to access other users' meetings or bypass permissions or sensitivity labels.
- If no Teams/meeting tool is available, or access is denied, log it, note it in the Signals Summary,
  and continue with the remaining files.

## When to retrieve

- Only when the user asked for recaps in the request (for example "include my meeting recaps" or "add
  last week's Teams meetings"). Do not pull recaps silently, and do not ask whether to include them.
- Scope: use the time range, meeting names, or attendees the user gave. If none were given, use the
  last 14 days and the customer or scenario name from the request, and log that the default was used.
  Keep the scope as narrow as the request allows.

## What to extract per meeting

- Meeting title, date, and organizer.
- Recap/AI notes: summary, key topics, decisions, and action items (with owners if listed).
- Transcript excerpts only when the recap has no summary.
- Linked or shared files are NOT analyzed automatically; list them under "Missing information" as
  files that could add evidence.

## How to represent them in the Signals Summary (Stage 2)

- List each meeting under **Sources** as `<Meeting title> (Teams recap, <date>)`.
- Fold signals, themes, decisions, and action items into the combined Signals Summary.
- In **Per-Source Highlights**, keep a short entry per meeting (2-4 bullets).
- Use the **Decisions and Action Items** section for any found in meetings.

## Unavailable recaps

- Meetings with no recap (recording/transcription was off, still processing, or retention expired)
  go under **Unsupported or Unreadable Sources** with the reason. Do not infer content from the
  title or attendees.

## Privacy

- Recaps may contain sensitive discussion. Keep output scoped to what the user asked for. Detailed
  content goes only into the generated Word documents; chat replies stay short.
