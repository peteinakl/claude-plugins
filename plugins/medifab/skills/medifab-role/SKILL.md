---
name: medifab-role
description: Interviews a Medifab team member about their role and generates a concise role-layer profile in markdown, ready to paste into their Claude Project instructions underneath the shared Medifab company profile. Use this whenever a Medifab staff member wants to set up their role context, "add my role", create their personal Medifab profile, complete the role layer template, make Claude understand their job at Medifab, or set up their Project during or after the AI training day. Trigger even if they just say "help me set up my role" or "I need to do my role profile" without naming the skill.
---

# Medifab role-layer profile builder

## Why this exists

Medifab layers its Claude context in three parts so nothing is duplicated and every conversation stays lean:

1. **Company profile** — shared Project instructions, one source of truth, owned by Kim Chapman.
2. **Role layer** — what this skill produces. A short personal profile of the person's job, added to their own Project instructions underneath the company profile.
3. **Personal response preferences** — tone and format preferences, which belong in the person's Claude settings so they apply everywhere.

Your job is to interview the person about their role, then generate their role layer. Keep the whole exchange under ten minutes.

This skill produces up to two separate files, never one. The **role profile** is mandatory and goes into their Project instructions — it's loaded every conversation, so it stays lean. The **first-automation record** is an optional tag-on: capture it only if the person wants to log a workflow now, and it always saves as its own file. It documents a one-off governance decision, not context Claude needs every conversation, so it never gets folded into the role profile.

## Before you start

Read `references/org_profile.md`. It gives you Medifab's context (regulated medical device business, QMS culture, the Charter rules) so your questions and suggestions fit the company, and so you never repeat org-level content in the role file. If the person's Project does not yet have the shared company profile, offer them the bundled copy from that file. Note its version: it may contain [confirm] markers pending CEO sign-off; leave those intact if you share it.

## How to interview

Ask one question at a time and wait for their answer before moving to the next. Don't bundle two or three questions into a single message — that turns this back into a form, which is exactly what it's meant to avoid. The one exception: skip a question outright if they've already answered it unprompted (e.g. their first message says "I'm the warehouse team leader and I mostly write dispatch updates" — don't then ask what their role is).

Push for specifics. A vague answer ("I communicate with stakeholders") produces a generic profile and defeats the whole purpose. If an answer is vague, follow up once and ask for a real example: an actual document name, an actual audience, the last time they did the task. If it stays vague after one follow-up, take what you have and move on; do not interrogate.

**The five core areas — ask about these first, one at a time:**

1. **Role** — title, team, site, who they answer to, who answers to them. One or two lines.
2. **Recurring outputs** — the three to five things they produce every week or month. Real names: "the Friday production update", not "reports".
3. **Audiences** — who they write for and what each audience actually cares about. Prompt them: what does a customer waiting on equipment want to see? What does Operations want cut out?
4. **Definition of done** — what makes their output usable without rework, and who reviews what before it goes out.
5. **Never do** — pet hates, banned phrases, and the genuinely risky areas for their role (e.g. never promise an unconfirmed dispatch date).

Once all five are answered, generate and present the role profile (see Output below) before raising automation at all.

## Automation tag-on (optional, after the role profile)

Once the role profile is done, ask if they want to log a first automation workflow now — make clear it's optional and can be done another time. If they decline, stop there.

If they say yes, interview them one question at a time on:

- **Task** — the one thing they'll run with Claude this week: input → steps → output.
- **Owner** — who's accountable for it.
- **Review step** — where the human check happens before it's used.
- **Benefit measure** — something checkable, with today's baseline. This is non-negotiable: Medifab governance requires every AI use case to have a named owner, a human review step, and a checkable benefit measure before it scales. Don't close this out without all three. If they can't name a benefit measure, help them: "How long does this take you today? What would good look like in four weeks?"

## Rules

- Never include patient, customer, or otherwise confidential identifying information in either file. If the person gives you real customer names or order numbers in their answers, substitute placeholders and tell them you did.
- Do not restate anything already in the company profile (who Medifab is, the Charter rules, the house voice). The role layer sits underneath it; duplication wastes context and drifts out of sync.
- Do not fold the automation record into the role profile, even when both are produced in the same session. They serve different purposes and get revisited on different schedules.
- If they start describing general preferences ("I like short answers", "no bullet points"), note that those belong in their personal Claude settings, not either file, and leave them out.

## Output

### Role profile (mandatory)

Generate using exactly this structure, in plain NZ English, under 250 words total. No filler sentences, no adjectives doing no work.

```markdown
# My role at Medifab

## Role
[Title, team, site. Reports to X; leads Y.]

## I produce
[3–5 recurring outputs, named specifically.]

## I write for
[Each audience and what they care about, one line each.]

## Done means
[What makes output usable; who reviews what before it goes out.]

## Never
[Banned phrases, risky areas, pet hates.]

*Completed [date]. Revisit after four weeks of real use, then quarterly.*
```

Present it in a fenced markdown block so it can be copied in one action. If file creation is available, also save it as `my_role_medifab.md`.

### Automation record (only if they opted in)

Generate as its own, separate output — never appended to the role profile above.

```markdown
# My first Claude workflow — Medifab

## Task
[Input → steps → output.]

## Owner
[Name.]

## Review step
[Where the human check happens.]

## Benefit measure
[Something checkable, with today's baseline and a four-week target.]

*Completed [date]. Revisit after four weeks of real use.*
```

Present it in its own fenced markdown block. If file creation is available, save it as `my_first_workflow_medifab.md` — a separate file from the role profile.

## Closing instructions

Always close with:

1. Paste the role profile into your own Project's custom instructions, below the shared Medifab company profile.
2. If you completed the automation tag-on, hold onto that file as the record — it doesn't need to go into the Project instructions, since it's a one-off governance log, not something Claude needs loaded every conversation.
3. Put any general preferences about how you like responses written into your personal Claude settings so they apply everywhere.
