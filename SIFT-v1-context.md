# SIFT — Project Context Document
**Version:** v1  
**Status:** Design complete. No code written yet.  
**Last updated:** Session June 2026

---

## What SIFT Is

SIFT is an external brain for anyone who builds things and needs to understand what they have.

It scans a machine, maps what exists, and produces two outputs:
- One for the human (plain English report)
- One for the LLM (structured context file)

It is a local web app — Python starts it, browser opens, everything runs on the user's machine. No data leaves.

---

## The Problem It Solves

- Builders forget what they built
- AI loses context between sessions
- Files accumulate with no record of what is current
- 12 days into a project looks nothing like day 2 — more files, more unknowns
- Re-explaining everything to a new AI session wastes time and tokens
- Multiple versions of the same project with no clear record of which is current
- Fear of deleting anything because nothing is labelled

---

## Three Use Cases (All Solving The Same Problem)

### 1. The Report
Run once. Make decisions. Clean up.
- Shows every project found
- Plain English name and description per project
- Status: CAN RUN NOW / NEARLY THERE / BROKEN / UNKNOWN
- Four decisions per project: FINISH IT / PARK IT / ARCHIVE IT / START FRESH
- One-time purchase model

### 2. The Heartbeat
Runs nightly or on-demand in the background.
- Watches for file changes — additions, moves, modifications
- Only scans the delta — not a full rescan every time
- Keeps one living context file always current
- No human action needed once set up
- This is the subscription use case
- Delivers value silently every day

### 3. The Handoff File
One structured output file formatted to paste into any LLM at session start.
- "Here is what exists"
- "Here is what is working"
- "Here is where we stopped"
- Solves the AI memory problem directly
- Agency and freelancer use case — one-time per project

---

## Target Users

### Primary — The Tinkerer
- Dyslexic, no working memory, non-linear thinker
- Builds multiple things simultaneously
- Drifts between projects, forgets what they built
- Uses AI tools — not a developer
- Runs SIFT constantly: project start, mid-build, end, whenever AI loses context
- Cannot hold context between sessions
- Gave up on things they still care about
- Scared to delete anything
- Names files in ways that made sense only at the time

### Secondary — The Developer
- Handed an unknown codebase
- Needs a technical map fast
- Wants file paths, entry points, dependency lists
- Comfortable with technical detail

### Tertiary — The Agency
- Does rescue work on unknown codebases
- Uses SIFT once per client project
- High value, low frequency, willing to pay more per use

---

## Design Laws — Never Break These

1. No technical jargon. Ever.
2. No filenames shown without plain English description
3. No timestamps — always relative time ("3 months ago")
4. No percentages, progress bars, scores, or grades
5. No recommendations, assumptions, or positive spin — facts only, or UNKNOWN
6. No delete buttons — offer ARCHIVE or SAFE STORAGE instead
7. One project at a time — never show all at once
8. Most important thing first on every screen
9. Every decision saves immediately and automatically
10. Technical detail always opt-in — default view always minimal

---

## Report Structure

### Opening Screen
- Three numbers: projects found / can run now / need a decision
- One button: START REVIEWING
- Nothing else clickable

### Project Card Contains
- Plain English name (LLM-generated if needed)
- One sentence: what it does + how long since touched
- Status label (one of four)
- File count and version count only
- Four decision buttons
- Technical detail toggle (hidden by default)

### Status Labels
- CAN RUN NOW — working entry point, no missing dependencies
- NEARLY THERE — entry point exists, one or two files missing
- BROKEN — entry point exists, critical dependencies missing
- UNKNOWN — no clear entry point found

### Version Groups
- One card for the group — not multiple cards
- Plain English description of the difference
- States which version can run — no "recommended" language
- Decision applies to the group

### Loose Files (Orphans)
- Never called "orphans" — "loose file, not connected to any project"
- Two options only: ATTACH TO A PROJECT or MOVE TO SAFE STORAGE
- Must state explicitly: nothing is deleted

### Ending Screen
- Plain English summary of all decisions
- One action: SAVE SUMMARY
- No celebration, no score, no encouragement

---

## Pricing Model (Direction — Not Final)

### What the research confirmed
- Problem is real — multiple GitHub tools confirm it (Context-memo, Kioku, Signal Box)
- Nobody has built a plain-English version for non-technical users — gap is unoccupied
- Local-File-Organizer has 3,236 stars — strong demand signal for local AI file tools
- All context/memory tools have 0–2 stars — no solution has traction yet
- LLM cost per scan: under 25p using Haiku 4.5 — not the constraint
- Free tiers not appropriate for a product handling private file contents
- BYOK works for developers. Non-technical users will not use it.
- No pricing benchmarks exist — no paid comparable found

### Pricing Direction
| User | Model | Fit |
|---|---|---|
| Power user / tinkerer | Small flat monthly fee | Unlimited scans, always on |
| One-time user / agency | Single purchase per report | Per project, no subscription |
| Developer | BYOK toggle (optional) | Their API key, your software fee |

Exact prices need real user testing. No scrape data exists to set them.

### What Was Wrong With The Previous Model
- £9 per report assumed one-time use — wrong for the core user
- Agency tier was a guess — no evidence found
- Development time, hosting, and maintenance costs were not factored in

---

## Technical Decisions Locked

- Local web app — Python starts it, browser opens
- Runs on user's machine — no data leaves
- LLM generates plain English names and descriptions
- LLM input: filenames, folder structure, file contents (first 200 lines max)
- LLM output: name (max 5 words), description (max 20 words, past tense)
- Haiku 4.5 for cost efficiency on descriptions
- Delta scanning for Heartbeat mode — not full rescan every time
- Output: one living context file, always current

---

## Open Questions — Must Resolve Before Build

1. Is re-scanning manual or automatic? If automatic — what triggers it?
2. Does the report work on mobile? (single column, 48px buttons if yes)
3. What is the source for LLM descriptions — filenames only or file contents?
4. What happens to files the user chose to ARCHIVE — does SIFT move them or mark them?
5. Exact pricing — needs real user testing before setting

---

## Demand Evidence (Scraped June 2026)

- Local-File-Organizer: 3,236 GitHub stars — AI file organisation, local, privacy-first
- Context-memo: confirms the exact problem — "new AI agent has ZERO memory of the project"
- Kioku: "You waste 10–15 minutes every session re-explaining your architecture"
- Signal Box: "Developer context decays before it becomes useful" — BYOK, local-first
- agent-audit: 8 stars — forensic auditor for AI agents, closest tool but developer-facing
- All project memory tools combined: under 10 stars — no solution has traction

---

## What To Build Next

The Heartbeat is the killer feature.
The Report is the front door.
The Handoff File is what agencies pay for.

Build the Report first — it proves the concept and gets users in.
Build the Heartbeat second — it's what justifies a subscription.
Build the Handoff File as an output format toggle, not a separate product.

