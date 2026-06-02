# SIFT — What We Did Not Ask
*Open questions. Known unknowns. Things to revisit.*

---

## Why this file exists

No design process asks every question first time.
This file captures what we know we did not fully think through.
So future versions of SIFT start here — not from scratch.

---

## Open questions — not yet answered

**What if the laptop has malware on it?**
Reading malware files as text should be safe — Python is not executing them.
But this has not been fully verified.
Needs a security review before SIFT is used on unknown machines in the wild.

**What if the project spans cloud storage?**
Dropbox, Google Drive, OneDrive folders that sync locally will be picked up.
But files that exist only in the cloud and are not synced will be missed.
SIFT will not know they exist.
This needs a warning in the output — "cloud storage detected, unsynced files may be missing."

**What if there are multiple projects on the same laptop?**
SIFT currently treats everything as one project.
A laptop might have three unrelated projects in three folders.
Should SIFT detect project boundaries and report separately?
Not solved in version 1.

**What if SIFT finds another SIFT output on the laptop?**
A previous scan might exist.
SIFT should detect its own output folders and skip them.
Or flag them — "previous SIFT scan found, dated X."
Not fully handled yet.

**What about very large individual files?**
A single log file or database export could be gigabytes.
Current chunking handles this but very large single files need specific testing.

**What about files that are code but in unusual languages?**
SIFT reads all text. But the LLM prompt does not currently tell the LLM what languages to expect.
An unusual language — COBOL, Fortran, Assembly — might confuse the analysis.
Should the contents file include a language inventory first?

**What about the LLM analysis quality on very old or unusual codebases?**
SIFT has been designed assuming modern code.
Very old legacy systems may produce poor LLM analysis.
No solution yet. Known limitation.

**What if the person running SIFT does not have Python installed?**
Currently SIFT assumes Python is available.
Should there be a pre-check and a plain English error message if not?
Version 2 feature — but worth noting.

**What about accessibility of the output?**
Output files are plain text.
Should there be a formatted version — colour coded, structured — for people who find plain text hard to read?
Dyslexia friendly output format not yet considered.

**What about the legal position?**
Is it legal to scan a laptop you have been given but do not own?
SIFT assumes the person running it has permission.
Should the consent screen make this more explicit?
Not a technical question — but an important one.

---

## Things that felt right but were not fully tested

- Redaction patterns cover common formats but regional variations exist
  - International bank account formats differ from UK ones
  - Phone number formats vary by country
  - Not all of these are covered in version 1

- Git history reading assumes standard Git
  - Other version control systems — SVN, Mercurial — not handled
  - Will be skipped and logged but not read

- Encrypted zip assumes the user remembers their password
  - No password recovery built in
  - If password is lost — output is gone
  - Should SIFT warn about this explicitly?

---

## Questions for version 2

- Should SIFT have a GUI — a visual interface — for non-technical users?
- Should SIFT run on a USB stick so nothing needs installing on the scanned laptop?
- Should there be a SIFT service — you send the laptop, we run SIFT, you get the report?
- Should SIFT compare two scans of the same laptop over time — what changed?
- Should SIFT integrate directly with Obsidian for saving reports?

---

## The question we almost did not ask

**What if the project is exactly what the owner said it was?**

SIFT is built on the assumption that owners do not fully understand what they have.
But sometimes they do.
SIFT should still run blind — but the ensemble comparison step should flag when all models agree with the owner's description.
That agreement is itself a useful signal.
It means the owner has clear self-knowledge of their project — which is rare and valuable information.

---

*Last updated: June 2026*
*Add to this file whenever a new question is raised.*
*Never delete old questions — even answered ones belong here.*

