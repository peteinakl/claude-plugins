---
name: research-review
description: "Runs a full readiness review of research (pasted text, a document, or a URL) against a nine-criterion rubric: fact-check's seven (source quality, evidence separation, currency, coverage, traceability, contradictions, decision value) plus argument quality (does the reasoning support the conclusion) and insight depth (specific implications vs generic filler). Runs a full claim-by-claim web verification like fact-check, plus an argument and insight assessment. Returns a markdown scorecard with a Ready / Use with caution / Draft only verdict. Use whenever someone asks if research is good enough to act on or decide with, not just whether facts check out. Trigger on 'is this good enough to act on', 'does this help me decide X', 'is the thinking sound', 'can I take this to the board or client', 'is this ready', or when handed research, a market scan, competitor analysis, board paper, or brief to review before use. Default for a full review; use fact-check only if the user wants just the facts checked."
---

# Research review

A full readiness review of a research artefact: are the facts right, does the reasoning hold, and is the thinking actually useful. The output is a scorecard the user can act on — where the piece is safe to rely on, where it isn't, and whether it's worth building a decision on.

This skill extends fact-check's seven-criterion rubric with two further criteria aimed specifically at decision-readiness: **argument quality** (the reasoning itself, not just the evidence behind it) and **insight depth** (whether the conclusions are specific and non-obvious, or generic filler). Fact-check answers "is this true?". Research review answers "is this true, sound, and actually useful?" — the fuller question most people are really asking when they hand over a piece of research before acting on it.

## When to use this skill

Trigger this skill whenever the user wants a research artefact reviewed before they rely on it, not when they want one written. The artefact might arrive as:

- Text pasted into chat
- A file in the uploads folder (.docx, .md, .pdf, .txt)
- A URL to a published piece

This is the default choice for a full review. Reach for the narrower fact-check skill instead only when the user is explicit that they want facts checked alone, with no view on the argument or the insight.

If the user asks for both a review and a rewrite ("check this and then fix it"), do the review first and present the scorecard. Fixes follow once the user has seen the findings.

## The nine criteria

The first seven are the standard fact-check rubric. The last two are specific to this skill. Each criterion is scored **Pass / Partial / Fail** with a short justification.

| # | Criterion | Pass standard |
|---|---|---|
| 1 | Source quality | Uses primary, official or reputable sources where possible |
| 2 | Evidence separation | Clearly distinguishes facts, assumptions and judgement |
| 3 | Currency | Uses current sources and names publication dates where relevant |
| 4 | Coverage | Does not cherry-pick only convenient evidence |
| 5 | Traceability | Important claims can be traced back to sources |
| 6 | Contradictions | Flags uncertainty or conflict rather than smoothing it over |
| 7 | Decision value | Ends with implications, trade-offs or next questions |
| 8 | Argument quality | Conclusions follow from the stated evidence, with no logical gaps or unsupported leaps |
| 9 | Insight depth | Implications are specific and non-obvious, not generic restatement |

**Pass rule.** If **Source quality**, **Traceability**, or **Argument quality** is **Fail**, the overall verdict is **Draft only**, regardless of how the other criteria score. Weak sourcing, unverifiable claims, or reasoning that doesn't actually support its conclusion are each independently disqualifying — a piece can't be decision-ready if any one of these is broken, no matter how good the rest of it is.

For the full scoring guidance — what counts as Pass, Partial, or Fail on each criterion, with examples — read `references/rubric.md`. This is especially important for criteria 8 and 9, which are easy to score too generously on a fast read.

## Workflow

Work through these steps in order. Do not skip ahead to the scorecard, and do not skip the argument and insight assessment because the facts checked out — a piece can be fully sourced and still reason badly, or reason well and still land on nothing useful.

### 1. Ingest the input

- **Pasted text** — work with it directly.
- **File** — read it from the uploads folder. For .pdf, use the pdf skill if extraction is non-trivial. For .docx, read with python-docx via the Bash sandbox.
- **URL** — fetch with `mcp__workspace__web_fetch` first. If the response is a JavaScript shell with no body (a sign the page is client-rendered), escalate to `mcp__Claude_in_Chrome__navigate` + `get_page_text`. If web fetch fails, stop and tell the user — do not retry through bash or curl.

If the input is unusually long (more than ~4,000 words), tell the user that a full review will take time and ask whether they want to scope down to a section or accept the wait. The user chose a full review knowing the cost, so honour it unless they say otherwise.

### 2. Structure what you read

Before scoring, build a mental (and explicit) map of the piece:

- **Claims** — atomic factual assertions. Numbers, dates, named entities, attributions, causal statements, comparative claims. Strip these out as a list.
- **Sources** — every URL, citation, quotation attribution, "according to…", footnote, or bibliographic entry.
- **Structural shape** — how the piece is organised. Where does it gather evidence, where does it interpret, where does it conclude.
- **The argument chain** — the actual line of reasoning from evidence to conclusion. What premises does the piece rely on (stated or unstated), and what inference connects them to the recommendation or conclusion? Write this out as a short chain: "because A and B, therefore C". You need this to score criterion 8.

The map is for your reasoning — do not paste it into the final scorecard. But you cannot score the rubric well without it.

### 3. Verify the claims

For every claim in the list, classify it as:

- **Verifiable** — a number, date, named fact, direct quote, or specific attribution that can be checked against a source.
- **Interpretive** — judgement, opinion, framing, prediction, or analysis. Not verifiable in the factual sense, but assessable for whether it's flagged as opinion (criterion 2) and whether opposing views are acknowledged (criterion 4 / 6).

For each verifiable claim, search for a primary or reputable source using `WebSearch` and then `mcp__workspace__web_fetch` on the most promising result. Where possible, prefer:

1. **Primary sources** — the original report, statute, dataset, filing, press release, paper.
2. **Official sources** — government, regulator, standards body, the named organisation itself.
3. **Reputable secondary** — quality press, recognised research bodies, established trade press.

Avoid relying on aggregators, anonymous blog posts, or content farms as the verification source — that just moves the problem one click downstream.

Assign each verifiable claim one of:

- **Confirmed** — primary or reputable source supports the claim as stated.
- **Partial** — claim is roughly right but with material imprecision (wrong year, wrong magnitude, paraphrased in a misleading way).
- **Unverified** — could not find a source either way within reasonable effort. Note what you searched.
- **Contradicted** — a credible source says something different. Quote the contradiction.
- **Outdated** — claim was once correct but is no longer current. Give the current position.

For interpretive statements, no verification is required, but flag whether they are clearly marked as judgement (criterion 2) and whether the piece engages with opposing views (criterion 6).

Be honest about what you couldn't verify. "Unverified" is a legitimate outcome — do not promote it to "Confirmed" through wishful reading.

### 4. Assess the argument

This is the step fact-check doesn't do. A piece can pass every sourcing criterion and still reach a conclusion its evidence doesn't support — that's an argument failure, not a factual one, and it's just as disqualifying.

Using the argument chain you mapped in step 2, check for:

- **Non-sequiturs** — the conclusion doesn't follow from the stated evidence, even if the evidence itself is accurate.
- **Unsupported leaps** — a step in the reasoning that isn't backed by anything in the piece ("adoption is growing, therefore incumbents will lose the market" skips several steps).
- **False dichotomies** — the piece frames a choice as binary when other options exist.
- **Correlation presented as causation** — two things move together and the piece asserts one causes the other without ruling out alternatives.
- **Motivated framing** — the evidence selected and the way it's sequenced seem chosen to reach a predetermined conclusion rather than follow the evidence where it leads. This overlaps with Coverage (criterion 4) but is about the *reasoning*, not just the evidence set.

Quote the specific sentence or passage where the argument breaks, and state plainly what step is missing or unsupported. "The conclusion that banks will lose the customer relationship requires an assumption — that fintechs will out-execute on retention — that the piece never states or supports" is useful. "The argument could be tighter" is not.

### 5. Assess insight depth

Also new relative to fact-check. Decision value (criterion 7) checks whether the piece has a "so what" section at all. Insight depth checks whether that section is actually worth reading.

Ask, for each implication or recommendation the piece offers: would a reasonably informed person already know this without reading the piece? Generic implications are a well-known AI-research tell — "organisations should consider the risks", "stakeholders should monitor developments closely", "this presents both opportunities and challenges". These are true of nearly anything and guide no one.

Real insight depth looks like: a specific trade-off named between two named options, a concrete threshold or trigger for action ("if adoption crosses X, the economics flip"), a named blind spot the reader wouldn't have thought of, or a next question that couldn't have been asked without doing the research. If the piece's conclusions could be swapped into an unrelated report on a different topic with a find-and-replace, that's a Fail.

### 6. Apply the rubric

Score each of the nine criteria **Pass / Partial / Fail** with one or two sentences of evidence, referencing the claims, argument chain, and implications you mapped in the earlier steps — not abstract impressions.

Then apply the pass rule. If Source quality, Traceability, or Argument quality is Fail, the overall verdict is **Draft only**, even if every other criterion passes.

Overall verdict bands:

- **Ready** — all nine criteria Pass, or at most one Partial in a non-blocking criterion.
- **Use with caution** — multiple Partials, or one Fail in a non-blocking criterion. The piece has value but the user should know the gaps before they act on it.
- **Draft only** — Fail on Source quality, Traceability, or Argument quality, or three or more Fails overall. The piece is not safe to build a decision on as it stands.

### 7. Produce the scorecard

Use the exact template in `references/scorecard-template.md`. Do not improvise the structure — the user is calibrated on this format.

The scorecard is rendered inline in markdown. It is not a Word document unless the user explicitly asks for one.

## Tone and standard

- **Plain and exact.** Name what's wrong. "The recommendation to expand into the segment relies on a growth figure that's never sourced" is useful. "The reasoning could be stronger" is not.
- **Do not smooth over.** If the piece fails, say so. The user explicitly does not want reassurance over accuracy.
- **No hedging by default.** Use "it depends" or "this is unclear" when warranted, but not as a way to avoid judgement when the pattern is clear.
- **UK English.** "Organisation" not "organization". "Analyse" not "analyze".
- **No motivational framing.** No "great start!" or "with a few tweaks this will be excellent!". The verdict is the verdict.

## What this skill does not do

- It does not rewrite the research. If asked, do that as a separate step after presenting the scorecard.
- It does not produce a Word document by default. Only if the user asks.
- It does not refuse to verify because the topic is contested. It verifies what can be verified and flags the rest under Contradictions (criterion 6).
- It does not assess style, prose quality, or design. The rubric is about epistemic and reasoning quality, not craft.
- It does not treat "the facts all checked out" as sufficient. A well-sourced piece with a broken argument or hollow conclusions still fails overall.

## Worked example

A full end-to-end example — input research, verification work, argument and insight assessment, and final scorecard — is in `references/worked-example.md`. Read it once before scoring your first real piece so the calibration on Pass / Partial / Fail lands correctly, especially for the two new criteria.
