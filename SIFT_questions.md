# SIFT — The Questions
*The most important file in this repository.*
*Every question that shaped SIFT. Always open. Always growing.*
*Add questions as they arise. Never delete old ones.*
*The questions matter as much as the answers.*

---

## How to use this file

When a new question arises — add it here first.
Before writing any code. Before making any decision.
The question comes before the answer.
Always.

Format:
```
Q: The question
A: The answer (if known)
STATUS: Open / Answered / Deferred
RAISED: Date
```

---

## The founding questions
*The questions that built SIFT from nothing*

---

Q: If you were handed a laptop with an unknown project and could not speak to the owner — what would you do?
A: Scan first. Ask nothing. Let the evidence speak.
STATUS: Answered
RAISED: June 2026

---

Q: If you ask the owner what the project is before looking — what happens?
A: You inherit their blind spots. Their confusion becomes your confusion. Their optimism becomes your bias.
STATUS: Answered
RAISED: June 2026

---

Q: How do you stop the LLM being biased by its own memory from previous sessions?
A: Fresh incognito window. No memory. No context. Clean slate every time. Claude Code has memory — do not use it for discovery.
STATUS: Answered
RAISED: June 2026

---

Q: How do you protect the laptop from the script doing damage?
A: Read only. No write permission given. No execution of anything found. LLM never touches the machine. Only receives plain text.
STATUS: Answered
RAISED: June 2026

---

Q: How do you send data to the LLM without an API?
A: Human in the loop. Python produces the file with prompt already at top. Human pastes it. Human pastes reply back. Total control. Zero black box.
STATUS: Answered
RAISED: June 2026

---

Q: How do you protect sensitive data before it leaves the machine?
A: Redact before anything is written to output. Show context without showing value. Bank accounts last 3 digits. Emails domain and last 2 characters. API keys name only value fully gone. Passwords fully gone.
STATUS: Answered
RAISED: June 2026

---

Q: What if one LLM gets it wrong?
A: Use multiple LLMs independently. Compare results. The ensemble analysis finds the truth across all models. Agreement builds confidence. Disagreement reveals ambiguity.
STATUS: Answered
RAISED: June 2026

---

Q: What about files it cannot read?
A: Log everything. Skip nothing silently. Binary files get a full index entry — name, size, date, type. Everything accounted for. Nothing hidden.
STATUS: Answered
RAISED: June 2026

---

Q: What about system files — Windows, Python installations, Adobe?
A: Skip known system folders professionally. Called deNISTing in forensic practice. Standard installation files add zero discovery value. Log that they were skipped. Nothing hidden. Just set aside.
STATUS: Answered
RAISED: June 2026

---

Q: What about the size of the output — too big for an LLM to read?
A: Split into summary and full index. LLM reads summary first. Asks for specific files if needed. Only targeted content retrieved. No overload.
STATUS: Answered
RAISED: June 2026

---

Q: What about memory crashing on large machines with millions of files?
A: Write to disk as you scan. Never hold file content in RAM. Crash safe — partial output better than nothing.
STATUS: Answered
RAISED: June 2026

---

Q: What about machine speed while scanning — everything freezes?
A: Throttle. Small pause between files. Machine stays responsive. Configurable at top of script.
STATUS: Answered
RAISED: June 2026

---

Q: What about different types of users — coders vs non-coders?
A: Two modes. Builder mode produces plain English output no jargon. Developer mode produces full technical detail.
STATUS: Answered
RAISED: June 2026

---

Q: What if you do not know which folder to scan — you are handed an unknown laptop?
A: Scan the whole machine. SIFT detects all drives automatically. No knowledge of the machine needed.
STATUS: Answered
RAISED: June 2026

---

Q: What about Google Drive and cloud storage synced locally?
A: Treat as any other folder. Scan separately from local files for cleaner results. First run local. Second run Drive. Compare the two.
STATUS: Answered
RAISED: June 2026

---

Q: What if all five projects are genuinely unrecoverable?
A: Say so clearly. Then list what the user learned from building them. The knowledge does not disappear because the files are not worth keeping. Graduate. Start fresh with what you know.
STATUS: Answered
RAISED: June 2026

---

Q: How do you get the LLM to return honest output not positive spin?
A: Four rules baked into every prompt. Forbid encouragement. Require uncertainty to be named. Require evidence for every claim. Forbid the word should. Add adversarial instruction — make the strongest case it is not worth continuing before making the case it is.
STATUS: Answered
RAISED: June 2026

---

Q: How do you calculate real completion percentage without assumption?
A: Measure what exists against what should exist for that project type. Every project type has a known anatomy. Inventory check against known standard. Logic not opinion.
STATUS: Answered
RAISED: June 2026

---

Q: How do you pick which project to focus on first?
A: Four factors scored 1 to 5. Completion, connection, momentum, value. Highest score first. If tied — ask which one would make the user happiest to finish. Evidence decides. Human breaks the tie.
STATUS: Answered
RAISED: June 2026

---

Q: How do you flag anomalies without making assumptions?
A: Logic flags. Human decides. SIFT never acts alone. Flag the observation. State it as fact. Offer a bat file to move to review folder — never delete. Human confirms before anything happens.
STATUS: Answered
RAISED: June 2026

---

Q: What is the real product SIFT is building toward?
A: A pipeline from invisible to complete. Scan — Map — Story — Triage — Brief — Build — Complete. From scattered mess to working product without writing a single line of code.
STATUS: Answered
RAISED: June 2026

---

Q: How do you present information to someone overwhelmed who does not speak tech?
A: One card. One project. Three things only. What it is in one sentence. How far as one real percentage. Honest verdict as one of four words. Finish. Decide. Learn From. Start Fresh. Nothing else on the card.
STATUS: Answered
RAISED: June 2026

---

Q: What is SIFT really?
A: A mirror for your digital work life. A thinking tool disguised as a file scanner. A witness — never a judge.
STATUS: Answered
RAISED: June 2026

---

## The design questions
*Questions about how SIFT is built*

---

Q: Should the prompts be treated as engineering not decoration?
A: Yes. Prompts are versioned, documented, and tested like code. Every prompt has a record of what it does, why it is worded that way, what bias it prevents, when it was last tested.
STATUS: Answered
RAISED: June 2026

---

Q: What is the minimum viable version to prove the concept?
A: Phase 1 only — scan and index. Prove it works reliably on different machines before building the visual map or triage board.
STATUS: Answered
RAISED: June 2026

---

Q: What does nothing goes to GitHub without passing tests first mean in practice?
A: Automated test script runs before every push. Known input. Known output. Pass or fail. No exceptions.
STATUS: Answered
RAISED: June 2026

---

Q: What is the zip password bug?
A: Standard Python zipfile silently ignores passwords on write. Not actually encrypted. Fixed in v2.2 using pyzipper.
STATUS: Answered
RAISED: June 2026

---

Q: What is the Mode 2 store search bug?
A: Script was searching from current working directory not script directory. Fails silently when run from different location. Fixed in v2.2.
STATUS: Answered
RAISED: June 2026

---

## The open questions
*Not yet answered. The frontier of SIFT.*

---

Q: How do we version control the prompts as they evolve?
A: Unknown. Needs design.
STATUS: Open
RAISED: June 2026

---

Q: How do we test prompt quality without bias in the testing itself?
A: Unknown. Circular problem. Needs design.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT tune its prompts per LLM — Claude vs GPT vs Gemini behave differently?
A: Unknown. Needs research.
STATUS: Open
RAISED: June 2026

---

Q: Can SIFT become predictive — not just what you have but what you need to complete it?
A: Possible in Phase 4. Requires pattern recognition across many machines not just one. Deferred.
STATUS: Deferred
RAISED: June 2026

---

Q: What is the minimum evidence threshold before SIFT flags an anomaly?
A: Unknown. Needs testing on real machines to calibrate.
STATUS: Open
RAISED: June 2026

---

Q: What does SIFT DRIVE look like — scanning Google Drive via API not synced files?
A: Separate project. Same methodology. Different data source. Needs Google Drive API integration.
STATUS: Deferred
RAISED: June 2026

---

Q: What does the visual map look like and what tools build it?
A: Designed — NetworkX for connections, D3.js for rendering, Timeline.js for time dimension. Not yet built.
STATUS: Deferred — Phase 2
RAISED: June 2026

---

Q: How do we make honest output feel human not clinical?
A: Unknown. Balance between removing spin and removing warmth is not yet solved.
STATUS: Open
RAISED: June 2026

---

Q: What happens when SIFT runs on a machine with malware?
A: Reading malware files as text should be safe. Not fully verified. Needs security review before SIFT is used on unknown machines in the wild.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT run from a USB stick so nothing needs installing on the scanned machine?
A: Possible. Would remove the Python installation requirement. Significant improvement for cold unknown laptop use case.
STATUS: Open
RAISED: June 2026

---

Q: What does SIFT GIT look like — scanning GitHub repositories?
A: Same methodology. Different data source. Repository contents plus commit history plus issues plus PRs. Rich data for discovery.
STATUS: Deferred
RAISED: June 2026

---

Q: How does SIFT compare two scans of the same machine over time — what changed?
A: Scan ID and fingerprint system exists. Diff logic not yet built. High value feature.
STATUS: Open
RAISED: June 2026

---

Q: What is the right community testing process — how do we collect real machine results at scale?
A: Unknown. Needs design. GitHub issues? A simple form? Discord?
STATUS: Open
RAISED: June 2026

---

Q: How do we know if SIFT is getting better or worse with each version?
A: No measurement system exists yet. Needs baseline metrics. What does good output look like quantitatively?
STATUS: Open
RAISED: June 2026

---

## Add new questions below this line

---

Q: Should SIFT show a progress bar during scanning?
A: Yes. Users need feedback. Currently no progress bar shows during scan. Machine appears frozen.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT show total file count before scanning starts?
A: Yes. User needs to know scale of what is being scanned.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT show current file number and name during scan?
A: Yes. Shows the scan is alive and progressing.
STATUS: Open
RAISED: June 2026

---

*Last updated: June 2026*
*This file is never finished. Every new question is progress.*
*The questions are the product.*

