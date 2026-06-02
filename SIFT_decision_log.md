# SIFT — Decision Log
*Every question asked. Every decision made. Every what if considered.*

---

## Why this file exists

Every decision made while building SIFT is recorded here.
So future versions never repeat questions already answered.
So anyone picking this up understands why it was built this way.
So we always know what SIFT was built on.

---

## Core design decisions

---

### Should we ask the owner what the project is before scanning?

**Decision: No. Never. Scan first.**

Reason: If you ask first you inherit their bias. Their blind spots become your blind spots. You will find what they expect you to find — not what is actually there.

Rule: Go in cold. Let the work speak for itself.

---

### Should we use Claude Code to run the discovery?

**Decision: No. Not for discovery.**

Reason: Claude Code has memory of previous sessions. That memory is bias. It will interpret what it finds through the lens of what it has seen before.

Rule: Discovery uses a fresh incognito LLM session every time. No memory. No context. Clean slate.

Claude Code only comes in at the build stage — after discovery is complete.

---

### Single LLM or multiple LLMs for analysis?

**Decision: Multiple LLMs. Independent. Blind to each other.**

Reason: One LLM can be wrong. Multiple LLMs reading the same content independently — and then compared — surfaces where the truth is clear and where it is ambiguous.

Rule: Each LLM gets the same file. Same prompt. Fresh window. No model sees another's answer before forming its own.

The disagreements between models are as valuable as the agreements.

This is called ensemble analysis.

---

### Should the LLM connect directly to the laptop via API?

**Decision: No. Human in the loop.**

Reason: Direct API connection removes human oversight. Output files go directly to the LLM without the human seeing what is being sent.

Rule: Python produces output files. Human reads them. Human pastes to LLM manually. Human pastes reply back. Python continues.

The human sees everything going in and everything coming back. No black box.

---

### Should SIFT have write permission on the laptop?

**Decision: No. Read only. Always.**

Reason: Write permission creates risk. SIFT has no reason to change anything on the laptop being scanned.

Rule: Python opens every file read only. Nothing is written to the scanned laptop except the output folder which is clearly named and dated.

---

### What operating system should SIFT support?

**Decision: All of them. Auto detect.**

Reason: The scope is any laptop. We cannot assume the OS.

Rule: Script detects OS at runtime and adjusts file path handling accordingly. Windows, Mac and Linux all supported.

---

### Where should output files be saved?

**Decision: Same folder the script is run from. Dated folder name.**

Reason: Always findable. No assumptions about folder structure on the scanned laptop.

Rule: Output folder named SIFT_output_YYYY_MM_DD. Created automatically. Printed to screen at end so user knows exactly where to find it.

---

### One output file or multiple chunks?

**Decision: Multiple chunks. One contents file first.**

Reason: Projects can be large. LLMs have size limits per upload. Single file approach breaks on large projects.

Rule: First file is always SIFT_contents.txt — summary of everything found. Then SIFT_chunk_01.txt, SIFT_chunk_02.txt etc. Each chunk labelled with total — Chunk 1 of 7. Discovery prompt auto added to top of every chunk.

---

### Should SIFT redact sensitive data?

**Decision: Yes. Always. Before anything is written to output.**

Reason: Output files may be emailed or uploaded to LLMs. Sensitive data must never leave the laptop in readable form.

Rule: Python scans every file for sensitive patterns before writing to output. Redaction happens at extraction stage — not after.

---

### How much context to show in redacted data?

**Decision: Enough to understand what it is. Never enough to reconstruct it.**

Rules by type:
- Bank account numbers: last 3 digits visible — XXXXXXX234
- Sort codes: last segment visible — XX-XX-45
- Credit cards: last 4 digits visible — XXXXXXXXXXXX4242
- Email addresses: domain and last 2 chars of name — lu**@gmail.com
- Phone numbers: last 3 digits visible — XXXXXXX789
- API keys: name shown, value fully redacted — STRIPE_API_KEY: [REDACTED]
- Passwords: fully redacted — PASSWORD: [REDACTED]
- Private keys and tokens: fully redacted

Rule: Functional data gets context. Security credentials get name only. Value always gone.

---

### Should SIFT handle files it cannot read?

**Decision: Yes. Log and skip. Never crash.**

Reason: Any laptop will have files Python cannot open — corrupted files, binary files, password protected files, files with unusual encoding.

Rule: Try to read. If it fails — log the filename and reason in the contents file. Skip cleanly. Keep going. Never stop.

---

### Should SIFT skip its own script file?

**Decision: Yes. Automatically.**

Reason: If SIFT reads itself its own code ends up in the chunks. That is noise and could confuse the LLM analysis.

Rule: Script detects its own filename at startup and adds it to the skip list.

---

### Should SIFT read Git history if present?

**Decision: Yes.**

Reason: Git history often reveals more than current code. Shows every change ever made, when, and why. Shows where the project went wrong. Shows original intent.

Rule: If a .git folder is found — read the commit log and include as a separate chunk labelled SIFT_git_history.txt.

---

### Should SIFT warn about sensitive data before starting?

**Decision: Yes. Consent required before scan begins.**

Reason: User must understand what SIFT does before it does it.

Rule: SIFT prints a warning at startup:
"This script will read all text on this laptop. That may include passwords and personal data. That text will appear in the output files in redacted form. You are responsible for handling output files safely. Continue? Y/N"

If N — script exits cleanly.

---

### How should output be protected?

**Decision: Encrypted zip. Password set by user.**

Reason: Output files may contain redacted but still sensitive context. Should be protected at rest.

Rule: After scan completes — SIFT zips all output files and password protects the zip. User sets the password. SIFT never stores or transmits the password. Reminder printed to screen to email output to yourself.

---

### Should SIFT show progress while running?

**Decision: Yes. Progress bar and status messages.**

Reason: On large laptops the scan may take minutes. Without feedback user cannot tell if it has frozen.

Rule: Progress bar shows files scanned. Current file name shown. Estimated time remaining shown. All printed to terminal in real time.

---

### Should SIFT be resumable if interrupted?

**Decision: Yes.**

Reason: Large scans on slow laptops may be interrupted. Starting again wastes time and risks missing files.

Rule: SIFT writes a checkpoint file as it goes. If interrupted and restarted — detects checkpoint and resumes from last completed file.

---

### Should SIFT produce a fingerprint of the scan?

**Decision: Yes.**

Reason: Proves this scan was done on this machine on this date. Useful for audit trail.

Rule: SIFT generates a unique scan ID — machine name, date, time, file count, total size. Written to contents file and to a separate SIFT_fingerprint.txt.

---

## What we decided not to include in version 1

- Following internet links found in files — too risky, out of scope
- Reading files on connected network drives — out of scope, laptop only
- Reading files on connected external drives — version 2 feature
- Automatic emailing of output — user stays in control of where output goes
- Multi-laptop projects — version 2 feature

---

