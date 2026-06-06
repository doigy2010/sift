# SIFT — Open Design Questions

This file tracks unresolved design questions, answered questions, and decisions made.
Questions are added in chronological order. Do not delete answered questions — mark STATUS only.

---

## Add new questions below this line

Q: How does SIFT build a plain English description
   of what each project does?
A: Python extracts signals from files — imports,
   function names, headings, comments, first and
   last 20 lines. Builds a structured evidence
   package. LLM reads only the evidence package
   not the raw files. LLM writes plain English
   description from evidence only.
   If no LLM — Python writes simpler version
   from same evidence package.
   LLM never reads raw files. Never sees file paths.
   Never sees code. Only sees structured evidence
   Python prepared.
STATUS: In design — intelligence layer session
RAISED: June 2026

Q: What is the gold standard description SIFT
   must produce for each project?
A: Plain English. States what each sub-part does.
   States whether parts are connected or separate.
   No assumptions — only states what evidence shows.
   Jogs memory without leading the user.
   No technical file names or paths visible.
   No "this looks like" without evidence.
   Target example: "This is a business toolkit
   with multiple parts. The parts include a vendor
   call script, a property valuation map, a case
   progression tracker, and an investor campaign.
   These appear to be separate tools for the
   same business."
STATUS: In design
RAISED: June 2026

Q: What is the Python extraction pipeline
   that feeds the LLM evidence package?
A: Not yet designed. Intelligence layer session
   will produce the build specification.
STATUS: Open
RAISED: June 2026
