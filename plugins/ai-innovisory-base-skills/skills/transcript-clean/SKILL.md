---
name: transcript-clean
description: Cleans up a raw meeting transcript — especially one with no speaker labels, from tools like Granola, Otter, Fireflies, Zoom, or Teams — into a readable markdown file with speakers inferred from context, content organized by topic, and a dated filename that describes what's inside. Use this whenever the user has a messy or unlabelled transcript and wants clean notes or minutes out of it. Trigger even if they don't say "transcript" explicitly — e.g. "clean this up", "turn this into minutes", "who said what in this call", "make this readable", or they paste in a wall of unlabelled dialogue from a recording tool.
---

# Transcript clean

## What this does

Takes a raw meeting transcript — often unlabelled or badly labelled, dumped out of a tool like Granola, Otter, Fireflies, or a Zoom/Teams recording — and produces **two** separate markdown files: a cleaned, fully attributed transcript, and a meeting summary. These serve different purposes and neither substitutes for the other — the transcript is the record of what was actually said, the summary is what someone reads if they only have thirty seconds. Always produce both, never just one.

## Step 1: Get the transcript, and use whatever metadata it already has

Accept it however it arrives — pasted text, an uploaded file, or a path. Many exports (Granola in particular) already put a title, date, and participant list at the top of the file. Use that directly rather than re-deriving it from the dialogue — it's more reliable than inference.

If it's a long call, skim first to get a sense of structure and topics before rewriting; for very long transcripts, work through it in sections rather than trying to hold the whole thing in your head at once.

## Step 2: Work out who's speaking

Some tools don't label speakers at all, or use generic tags like "Speaker 1" / "Speaker 2". Granola specifically tends to produce a two-party export — "Me" for the account owner and "Them" for everyone else — even when there were three or four other people in the room. That second case is the harder one: it's not just a missing label, it's multiple real people collapsed into one, and a single "Them:" block can silently contain a handoff between two or three different speakers with no marker at all.

Work through this in two passes:

1. **Attribute "Me"**: this is almost always the account owner — cross-check against the participant list if one exists.
2. **Split "Them"**: look for the clues that reveal a handoff or an identity within a merged block:
   - Self-introductions ("it's Sarah from Ops")
   - Being addressed directly by name ("So Dave, what do you think?", "James, can you share...")
   - One person naming another mid-block ("thanks Justin", "Ben's points first") — this is often the clearest evidence of exactly where a handoff happened
   - Role-specific language and topic ownership — the same person consistently owns the same subject or responsibility across the call
   - A clear first-person claim that only fits one participant (e.g. someone describing a technical build that another speaker later credits to them by name)

When a "Them" block contains more than one speaker, split it into separate attributed turns at the point the evidence indicates, rather than leaving a long block under one name or under "Them" — that's the whole value of this step, and skipping it produces a transcript no more useful than the original.

Confidence matters more than completeness. If you can identify someone with reasonable confidence, use their name. If you can't, don't guess a specific name — a wrong name misattributes what someone actually said, which is worse than no name at all. Use a clearly-marked placeholder instead, such as "**[Speaker — unconfirmed]**", and note in the transcript's header that these need a human check.

The same caution applies to anything else in the source that's unclear — a garbled proper noun, a place name, a product name that doesn't quite parse. Don't quietly "fix" it into something that sounds plausible; that's inventing a fact. Preserve what was actually transcribed and flag it, e.g. `Taron [unclear — possibly mis-transcribed]`.

## Step 3: Write the cleaned transcript

This is the full record, not a condensed version. Preserve every turn and everything that was substantively said — the cleanup is about readability, not compression:

- Replace speaker labels with real names (or the placeholder from Step 2).
- Fix false starts, filler, and stutters into readable sentences without changing what was meant ("Bit dazed and confused after a whirlwind trip" not "Bit. Dazed and. Confused after a. Whirlwind trip").
- Where a merged block contains a handoff, break it into separate attributed paragraphs at that point.
- Keep chronological order and keep it as dialogue — this is not the place to summarize.

```markdown
# [Topic] — cleaned transcript

*[Meeting date]. Speakers: [list, from metadata or inferred]. Speaker names and a few unclear terms are inferred or flagged where the source wasn't explicit — check items marked [unconfirmed] or [unclear] before treating this as a final record.*

**[Speaker name]:** [cleaned dialogue]

**[Speaker name]:** [cleaned dialogue]

[... continues for the full conversation ...]
```

## Step 4: Write the summary

A distillation of the transcript above, for someone who wasn't there or doesn't have time to read the whole thing:

```markdown
# [Topic] — summary

*[Meeting date]*

## Attendees
[Names or roles identified, one line each. Mark any low-confidence names clearly.]

## Discussion
[The substantive content, organized by topic — whichever grouping makes the conversation clearest, not necessarily chronological order.]

## Decisions
[Anything explicitly decided, if applicable.]

## Action items
[Owner and task, if applicable.]
```

Adapt this to what the transcript actually contains — don't force "Decisions" or "Action items" sections when the conversation didn't have any; an empty section is worse than no section.

## Step 5: Name and save the files

Save both as markdown, sharing the same date and topic slug so they're obviously a pair:

- `YYMMDD-topic-slug-transcript.md`
- `YYMMDD-topic-slug-summary.md`

Use the meeting date from the transcript or its metadata if available; otherwise today's date. The topic slug is a short, kebab-case version of the discussion topic (three to five words) — e.g. `260714-ai-os-implementation-transcript.md`, not `260714-meeting-notes.md`. The point of the filename is that it tells you what's inside without opening it.

Present both finished files, and call out anything flagged as an unconfirmed speaker or unclear term so the person knows what to check before relying on either one or sharing them further.

## Batch mode: a folder of transcripts

If given a folder of many raw transcripts rather than one, process them in parallel rather than working through them one at a time in the main conversation. A single transcript already runs to several thousand words once cleaned; holding 40 of them in one context window is both wasteful and unnecessary, since the files don't depend on each other.

- **Dispatch one subagent per transcript**, batched together so they run concurrently rather than queued one after another. Give each subagent the skill's instructions plus one explicit file path, so there's no ambiguity about which transcript it owns.
- **Batch the dispatch in groups** (e.g. 8–10 at a time) rather than firing all of them at once, and let each group finish before starting the next.
- **Write outputs to a `cleaned/` subfolder** alongside the source folder rather than mixing them in with the raw transcripts — keeps input and output clearly separated, and makes the batch safe to re-run later without confusion about what's already been processed.
- Filenames follow the same `YYMMDD-topic-slug-transcript.md` / `-summary.md` pattern as single-file mode. The date prefix should keep two same-topic meetings from colliding; if it somehow doesn't, fall back to a short suffix from the source filename.
- **Collect a short manifest once the batch finishes** — which files processed cleanly, and which have `[unconfirmed]` speakers or `[unclear]` terms worth a manual check. Surface that in one place rather than making the person open all 40 files to find out where the uncertainty is.
