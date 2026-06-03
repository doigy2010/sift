# SIFT — The Evolution Document
*How SIFT grew from a file scanner to a clarity and decision engine*
*Documented from the founding conversation. June 2026.*

---

## Where it started

A simple question: if you were handed a laptop with an unknown project on it and could not speak to the owner — what would you do?

The answer became SIFT.

The original outcome:

> A plain English picture of what exists on a laptop and what it was trying to do — produced without asking anyone anything.

---

## The founding insight

> If you are told where to look — you find what they expect.
> If you look at everything — you find the truth.

When you ask the owner what the project is before looking — you inherit their blind spots. Their confusion becomes your confusion. Their optimism becomes your bias.

SIFT looks first. Asks nothing. Lets the evidence speak.

---

## The methodology that emerged

**Cold discovery** — go in with no brief, no context, no expectations.

**Multi-model ensemble** — same evidence, multiple LLMs, independently. Agreement builds confidence. Disagreement reveals ambiguity. The disagreements are as valuable as the agreements.

**Python does the heavy lifting. LLM connects the dots.**

Python is good at reading everything, measuring everything, finding patterns, redacting sensitive data, never getting tired.

LLMs are good at understanding what things mean, spotting what should exist but does not, inferring intent from incomplete evidence, telling the story in plain English.

Perfect split of labour. Never reversed.

---

## The questions that built SIFT

Every design decision came from a question. Here they are in order.

**What if you cannot speak to the owner?**
Scan first. Ask nothing. Let evidence lead.

**How do you stop the LLM being biased by its own memory?**
Fresh incognito window. No memory. No context. Clean slate every time.

**How do you protect the laptop from the script?**
Read only. No write permission. No execution. LLM never touches the machine. Only receives plain text.

**How do you send data to the LLM without an API?**
Human in the loop. Python produces the file. Human pastes it. Human pastes the reply back. Total control. Zero black box.

**How do you protect sensitive data?**
Redact before anything leaves the machine. Show context without showing value. Bank accounts — last 3 digits. Emails — domain and last 2 characters. API keys — name only, value fully gone. Passwords — fully gone.

**What if one LLM gets it wrong?**
Use multiple LLMs independently. Compare results. The ensemble analysis finds the truth across all models.

**What about files it cannot read?**
Log everything. Skip nothing silently. Binary files get a full index entry — name, size, date, type. Everything is accounted for. Nothing is hidden.

**What about system files?**
Skip known system folders professionally. This is called deNISTing in forensic practice. Standard files from known software installations add zero discovery value. Log that they were skipped. Nothing hidden. Just set aside.

**What about the size of the output?**
Split into summary and full index. LLM reads the summary first. Asks for specific files if it needs more. Only targeted content retrieved. No overload.

**What about memory on large machines?**
Write to disk as you scan. Never hold file content in RAM. Crash safe — partial output better than nothing.

**What about machine speed while scanning?**
Throttle. Small pause between files. Machine stays responsive. User can still work while SIFT runs.

**What about different types of users?**
Two modes — builder and developer. Builder mode produces plain English output. No jargon. No technical terms. Developer mode produces full technical detail.

---

## The four audiences

**Developers handed a mystery codebase**
They inherit someone else's project. No handover. No docs. SIFT tells them what they have before they touch anything.

**Agencies and freelancers doing rescue work**
First tool on every inherited project. Cold. Unbiased. Fast.

**DIY builders and tinkerers**
Built things with AI tools. Have files everywhere. Do not know what connects to what. Scared to delete anything. SIFT unpicks the mess.

**Non-coders overwhelmed by their own digital life**
Twenty years of files. Half-built businesses. Templates never used. Names changed. Nothing finished. SIFT shows them what they actually have.

---

## The evolution of the outcome

**Original outcome:**
A plain English picture of what exists on a laptop and what it was trying to do — produced without asking anyone anything.

**Evolved outcome:**
SIFT turns your invisible digital work into a clear picture, a triage decision, and a build brief — so nothing you have ever built is wasted and nothing you want to finish stays unfinished.

**Final outcome:**
SIFT is a mirror for your digital work life. It shows you exactly what you have built — across your machine, your drives, your projects — mapped, connected, and told as a plain English story. No assumptions. No judgment. Just the truth of what exists. And then one clear next step.

---

## The problem with LLMs that SIFT solves

LLMs are trained to be helpful. Helpful feels like encouragement. Encouragement feels like spin. Spin feels like lying when you are exhausted and nothing is working.

LLMs are not dishonest. They just cannot see the whole picture. They only see what you show them. You show them the broken bit. They fix the broken bit. They never see the five other broken bits. They cannot tell you the truth about the whole because they have never seen the whole.

SIFT sees the whole. That is the difference.

---

## How SIFT calculates real completion

Not by asking anyone. By measuring what exists against what should exist.

Every project type has a known anatomy. A web app needs certain things. A script needs certain things. A business tool needs certain things.

SIFT looks at what exists and compares it to what that type of project needs to be complete.

Example:

```
Web app anatomy check:
  Frontend         — exists? Yes — 100%
  Backend logic    — exists? Partial — 40%
  Database         — exists? No — 0%
  Configuration    — exists? Yes — 100%
  Documentation    — exists? No — 0%
  Tests            — exists? No — 0%
  Deployment       — exists? No — 0%

Real completion: 34%
```

That is not an opinion. That is an inventory check against a known standard. Logic not assumption.

---

## The four honest verdicts

Every project gets one of four verdicts. Nothing softer. Nothing more complex.

```
FINISH      — this is worth completing
             Evidence: high completion, active, connected to live work

DECIDE      — this needs a human decision
             Evidence: medium completion, unclear value, dormant

LEARN FROM  — this taught you something, let it go
             Evidence: low completion, long dormant, disconnected

START FRESH — take what you learned, begin again
             Evidence: unrecoverable foundation, but demonstrable skills
```

---

## How SIFT picks which project to focus on first

Four factors. Scored 1 to 5 each. Added up. Ranked.

```
1. Completion    — how close is it to done?
2. Connection    — does it connect to something live or useful?
3. Momentum      — when was it last worked on?
4. Value         — what does finishing it actually give the user?
```

Highest score — focus first.

If two projects score the same — SIFT asks the one question evidence cannot answer:

> Which one would make you happiest to finish?

Because a project you are excited about gets finished. A project you dread does not. No matter what the score says.

---

## What SIFT says when all projects are unrecoverable

It says that clearly. And then adds:

```
This is not failure.
This is five projects worth of learning.
You now know more than when you started each one.

Here is what you know how to do now:
[list of actual skills demonstrated in the files]

Here is what a clean version of your best idea would need:
[brief for starting fresh]
```

The project gets an honest verdict. The person gets acknowledged for what they learned. The knowledge does not disappear because the files are not worth keeping.

---

## The pipeline SIFT enables

```
SCAN        — reads everything, indexes everything
MAP         — shows what connects to what
STORY       — plain English narrative of what was built
TRIAGE      — four decisions per project
BRIEF       — build brief for anything worth finishing
BUILD       — hand brief to Claude Code
COMPLETE    — project finished
```

From chaos to creation. Without writing a single line of code. Without explaining anything to anyone. Without starting from scratch.

---

## What SIFT is not

Not a project manager. Not a to-do list. Not a code reviewer. Not a cheerleader.

SIFT is a witness. Always the witness. Never the judge.

It presents evidence. The user makes decisions. The decisions are theirs. The truth is in the files.

---

## The deeper truth

SIFT is a thinking tool disguised as a file scanner.

The methodology applies to anything someone has built and lost faith in. A business. A creative project. A system. Any domain where someone has invested time and energy and lost the thread and needs to see clearly what is real and what is noise.

The question SIFT answers is always the same:

> What do I actually have? And what is it worth?

That question deserves an honest answer. SIFT gives one.

---

## The technical pipeline built so far

```
Phase 1 — Text index (built and tested)
  Python walks all files
  Reads all readable text
  Redacts sensitive data
  Builds structured index
  Splits into summary and full index
  Writes to disk as it goes — crash safe
  Two modes — builder and developer
  Whole machine or specific folder

Phase 2 — Visual map (designed, not yet built)
  Connection graph using NetworkX
  Timeline using D3.js
  Visual rendered in browser

Phase 3 — Plain English story (designed, not yet built)
  Claude reads the map
  Writes narrative in plain English
  No jargon. No assumptions.

Phase 4 — Triage board (designed, not yet built)
  One card per project
  Three things per card — what it is, how far, honest verdict
  Four decision buttons

Phase 5 — Build brief (designed, not yet built)
  Auto-generated from triage decision
  Handed to Claude Code
  Project completion automated
```

---

## What goes to GitHub

```
sift.py                  — the script
run_sift.bat             — double-click to run
requirements.txt         — dependencies
SIFT_README.md           — public facing
SIFT_methodology.md      — how it works
SIFT_decision_log.md     — every decision and why
SIFT_what_we_missed.md   — open questions
SIFT_evolution_document.md — this document
```

---

## What stays private

```
SIFT_business_plan.md    — never goes to GitHub
```

---

## The tagline

*Sifting through shit to get to paradise.*

Public version: *Know what you've got. Keep what matters. Build without fear.*

---

## Born

June 2026. In a single conversation. By a non-coder using AI.

The methodology, the questions, the design, the evolution — all human.

The code — AI assisted.

Proof that you do not need to know how to code to build something real.

---

*Add to this document as SIFT evolves. Never delete old thinking. The questions matter as much as the answers.*

