# SIFT — Prompt Library
*Every prompt, every rule, every design decision behind the words.*
*Use this to rebuild, extend, or adapt SIFT for any context.*

---

## Why this document exists

The prompts inside SIFT are not decoration. They are the methodology made operational.

Every word was chosen for a reason. Every rule exists because a previous version without it produced a wrong answer. This document records what the prompts say, why they say it, and what breaks if you change it.

---

## The three core prompts

---

### Prompt 1 — Phase 1: Index Analysis

**When it runs:** After Mode 1 scan. Prepended to `SIFT_index_summary.txt`.

**What it does:** Tells the LLM it is receiving a map, not the content. Forces it to work from signals before asking for full files.

**The prompt:**

```
=============================================================
SIFT v2 - PHASE 1: INDEX ANALYSIS
=============================================================

You are receiving a structured index of every file found on
a laptop. This is NOT the file contents. This is the map.

Every file is listed — readable or not. You can see file
names, types, sizes, dates, and key signals from each file.

YOUR JOB IN THIS PHASE:

1. What does this project appear to be?
2. What does it appear to do?
3. What technologies and languages are used?
4. How old is it? Is it actively worked on?
5. What appears broken, missing or unfinished?
6. What does NOT exist that should?
7. List the EXACT file paths you need to read in full
   to complete your analysis. Be specific. Be minimal.
   Only ask for files that will genuinely change your answer.

RULES:
- Say what you see. Not what you think it should be.
- If guessing — say so explicitly.
- Uncertainty is more valuable than a wrong answer.
- Do not assume anything not shown in the index.
- Your file request list must use exact paths as shown.

STRUCTURED REPLY FORMAT — use these exact headings:

PROJECT TYPE:
WHAT IT DOES:
TECHNOLOGIES:
AGE AND ACTIVITY:
WHAT WORKS:
WHAT IS BROKEN OR MISSING:
CONFIDENCE: [high / medium / low]
FILES I NEED TO READ:
- [exact path]
- [exact path]
WHAT I AM GUESSING:

=============================================================
INDEX BELOW THIS LINE
=============================================================
```

**Why it is written this way:**

- "This is NOT the file contents. This is the map." — LLMs default to treating everything as content. This reframes it as cartography. The LLM approaches it differently.
- "Only ask for files that will genuinely change your answer." — Without this, LLMs request every file. This forces minimal, targeted retrieval.
- "Uncertainty is more valuable than a wrong answer." — LLMs are trained to be helpful. Helpful feels like confidence. Confidence without evidence is bias. This permission to be uncertain is essential.
- "Your file request list must use exact paths as shown." — LLMs paraphrase. SIFT's Mode 2 does exact path matching. Paraphrased paths break the lookup.
- Structured reply format — without headings, LLMs write essays. SIFT needs comparable output across multiple models for ensemble analysis. Fixed headings make comparison possible.

**Builder mode variant:**
When user selects plain English output, these substitutions are applied:
- `PROJECT TYPE:` → `WHAT TYPE OF PROJECT IS THIS:`
- `WHAT IT DOES:` → `WHAT DOES IT DO IN PLAIN ENGLISH:`
- `AGE AND ACTIVITY:` → `HOW OLD IS IT AND IS IT STILL BEING WORKED ON:`
- `WHAT IS BROKEN OR MISSING:` → `WHAT LOOKS BROKEN, UNFINISHED OR MISSING:`
- `FILES I NEED TO READ:` → `FILES YOU NEED TO SEE TO FINISH YOUR ANSWER:`
- `WHAT I AM GUESSING:` → `WHAT ARE YOU UNSURE ABOUT:`
- Plus appended instruction: "Reply in plain English. No technical jargon. Write as if explaining to someone who has never coded."

---

### Prompt 2 — Phase 2: Content Analysis

**When it runs:** After Mode 2 retrieval. Prepended to `SIFT_retrieved_[date].txt`.

**What it does:** Tells the LLM it is now seeing the specific files it asked for, and instructs it to complete its analysis.

**The prompt:**

```
=============================================================
SIFT v2 - PHASE 2: CONTENT ANALYSIS
=============================================================

You already received the index in Phase 1.
These are the specific files you requested.

Read them and complete your analysis.

STRUCTURED REPLY FORMAT — use these exact headings:

PROJECT TYPE:
WHAT IT DOES:
WHAT WORKS:
WHAT IS BROKEN:
WHAT IS MISSING:
WHAT SHOULD BE BUILT NEXT:
CONFIDENCE: [high / medium / low]
REMAINING UNKNOWNS:

=============================================================
REQUESTED FILE CONTENTS BELOW
=============================================================
```

**Why it is written this way:**

- "You already received the index in Phase 1." — LLMs in a continuing session retain context. This reminder anchors Phase 2 to Phase 1 without repeating everything.
- "These are the specific files you requested." — Reinforces that the LLM is in control of what it sees. It asked. SIFT retrieved. This builds trust in the process.
- Shorter format than Phase 1 — by Phase 2 the LLM has already established context. The headings narrow to decision-relevant outputs.

---

### Prompt 3 — Ensemble Comparison

**When it runs:** After all LLMs have completed Phase 1 and Phase 2 independently. Used with `SIFT_ensemble_prompt.txt`.

**What it does:** Takes multiple independent LLM analyses of the same project and finds where they agree, where they disagree, and what the disagreements mean.

**The prompt:**

```
=============================================================
SIFT v2 - ENSEMBLE COMPARISON
=============================================================

Below are independent analyses of the same project from
different AI models. Each model worked alone in a fresh
session with no knowledge of the others.

YOUR JOB:

1. Where do all models agree?
2. Where do they disagree?
3. What does each disagreement tell us?
4. What is the most likely truth?
5. What remains genuinely unknown?

RULES:
- Agreement = confidence. Trust it.
- Disagreement = signal. Investigate it.
- Do not average the answers. Find the truth.

STRUCTURED REPLY FORMAT:

AGREED ON:
DISAGREED ON:
MOST LIKELY TRUTH:
REMAINING UNKNOWNS:
RECOMMENDED NEXT ACTION:

=============================================================
MODEL ANALYSES BELOW
=============================================================

[PASTE MODEL REPLIES BELOW — LABEL EACH ONE]

--- CLAUDE ---
[paste here]

--- GPT ---
[paste here]

--- GEMINI ---
[paste here]

--- GROQ ---
[paste here]
```

**Why it is written this way:**

- "Each model worked alone in a fresh session with no knowledge of the others." — Establishes the independence of the inputs. The comparison LLM knows these are not echoes of each other.
- "Do not average the answers. Find the truth." — Without this, LLMs produce a diplomatic average. The average is useless. The disagreements are the signal.
- "Disagreement = signal. Investigate it." — This is the methodological core of ensemble analysis. Where models disagree is where the project is genuinely ambiguous. That ambiguity is the most valuable output.
- Four models (Claude, GPT, Gemini, Groq) — chosen for diversity of training, not consensus. Each has different blind spots. The ensemble covers what any single model misses.

---

## The rules behind the prompts

These rules govern every prompt in SIFT. Violating any of them degrades the output.

**Rule 1 — Cold first.**
No context before the scan. No owner description. No brief. The prompt gives the LLM nothing to confirm — only evidence to read.

**Rule 2 — Uncertainty over confidence.**
Every prompt explicitly permits uncertainty. "If guessing — say so." This is the opposite of what LLMs are trained to do by default.

**Rule 3 — Structure over prose.**
Fixed headings in every prompt. Prose is uncomparable. Structured outputs can be compared across models, across time, across projects.

**Rule 4 — Minimal retrieval.**
Phase 1 asks the LLM to request only files that will change its answer. This is not efficiency — it is methodology. A LLM that reads everything produces confident noise. A LLM that reads only what it needs produces targeted signal.

**Rule 5 — Fresh session every time.**
Each LLM receives the same files in a fresh incognito window. No memory. No context from previous sessions. Contaminated sessions produce contaminated analysis.

**Rule 6 — Human in the loop.**
SIFT produces files. The human pastes them. The LLM never connects to the machine. This is not a limitation — it is a design principle. The human sees everything going in and everything coming back.

**Rule 7 — Disagreement is data.**
When two LLMs reach different conclusions about the same code, that disagreement is more valuable than either answer alone. The ensemble prompt exists to surface and analyse the disagreement, not resolve it prematurely.

---

## Design decisions that shaped the prompts

These decisions were made explicitly. They are recorded here so future versions never unknowingly reverse them.

**Why not ask the owner first?**
Asking the owner introduces their bias before the evidence is examined. If they say "it's a booking system" you look for a booking system. You stop looking for everything else. The prompt assumes nothing about project type.

**Why not let the LLM connect to the laptop via API?**
Direct API connection removes human oversight. The human cannot see what is being sent or what the LLM is doing with it. SIFT's file-based approach means the human sees every input and every output. Total visibility. Zero black box.

**Why structured reply format?**
SIFT's ensemble step compares outputs across multiple models. If every model replies in different prose formats, comparison is subjective. Fixed headings make comparison objective. "WHAT IS BROKEN" in three different model outputs can be read side by side and compared directly.

**Why "CONFIDENCE: [high / medium / low]"?**
Without this, LLMs produce uniformly confident output. Forcing a confidence declaration makes the LLM acknowledge what it does not know. Low confidence answers are as useful as high confidence answers — they show where more investigation is needed.

**Why four specific LLMs?**
Claude, GPT, Gemini, and Groq were chosen for maximum diversity of training data and architecture. Using four models from the same provider would produce correlated errors. Cross-provider ensemble catches what same-provider comparison misses.

**Why plain English mode?**
SIFT's fourth audience is non-coders overwhelmed by their own digital life. Technical output alienates them and produces no action. Plain English mode is not a dumbed-down version — it is an appropriately calibrated version.

---

## How to use these prompts outside SIFT

These prompts can be used manually without running the Python script.

**Manual Phase 1:**
1. Open a fresh incognito window
2. Start a new chat with any LLM
3. Paste the INDEX_PROMPT above
4. Then paste a directory listing of the project (from `tree` or `ls -R`)
5. The LLM will reply with its analysis and file requests

**Manual Phase 2:**
1. In the SAME chat session
2. Paste the CONTENT_PROMPT above
3. Then paste the content of the files the LLM requested
4. The LLM will complete its analysis

**Manual Ensemble:**
1. Repeat Phase 1 and Phase 2 with 2–4 different LLMs independently
2. Open a NEW chat with any LLM
3. Paste the ENSEMBLE_PROMPT above
4. Paste each model's Phase 2 output under its label
5. The LLM will compare and synthesise

---

## What goes where

| Document | GitHub | Obsidian |
|---|---|---|
| SIFT_prompt_library.md | Yes | Yes |
| SIFT_methodology.md | Yes | Yes |
| SIFT_decision_log.md | Yes | Yes |
| SIFT_what_we_missed.md | Yes | Yes |
| SIFT_evolution_document.md | Yes | Yes |
| SIFT_README.md | Yes | Yes |
| SIFT_business_plan.md | **Never** | Yes |

---

*SIFT. Born June 2026.*
*Add to this document as prompts evolve. Never delete old versions — record what changed and why.*
