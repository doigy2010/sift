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
A: build_descriptions.py runs after
   build_entry_points.py. For each cluster:
   read first + last 20 lines of every file.
   Extract imports, function names, docstrings,
   comments, headings, file names. Map imports
   to purpose labels via lookup table. Extract
   domain nouns from function names. Run
   connected-components on connection map to
   find sub-projects. Assemble evidence package.
   Write all packages to SIFT_descriptions.json.
   No LLM calls at this stage — pure Python.
STATUS: Answered — intelligence layer design
RAISED: June 2026

Q: How does Python detect sub-projects
   within a cluster?
A: Load SIFT_connection_map.json. Filter to
   edges between files within this cluster only.
   Run connected-components (DFS/BFS). Each
   component with 2+ files = one sub-project.
   Single files with no edges = standalone.
   Files imported by multiple components =
   shared utilities, labelled separately.
   CRITICAL GAP: SIFT_clusters.json contains
   only file path lists — no connection edges.
   The connection map is built in memory by
   build_connection_map() in sift.py and then
   discarded. sift.py must be modified to save
   it as SIFT_connection_map.json before
   build_descriptions.py can use it.
STATUS: Gap identified — prerequisite required
RAISED: June 2026

Q: What is the minimum evidence package
   that can prompt an LLM to write a
   plain English project description?
A: Max 500 tokens. Plain key-value text format.
   Fields: cluster_name, file_count, languages,
   purpose_signals (top 5), domain_vocabulary
   (top 10, sensitive nouns stripped),
   readme_summary (200 chars prose only),
   sub_projects (label/count/signals/entry/
   connection per part), connection_summary,
   last_touched, incomplete_signals (max 3),
   content_hash (MD5 for cache invalidation).
   ~243 tokens for a 3-sub-project cluster.
   LLM never sees raw files or file paths.
STATUS: Answered — intelligence layer design
RAISED: June 2026

Q: What gaps remain that the design
   session did not resolve?
A: Connection map not persisted — must save
   SIFT_connection_map.json before building.
   Description quality drift as models change —
   no version tag on cached descriptions (v2).
   User cannot correct a wrong description (v2).
   Two clusters that are the same project in
   two folders seen as separate (no fix in v1).
   Data-only clusters cannot be described
   without violating privacy constraint.
   Network-mounted drive speed not tested.
   Non-English domain vocabulary not handled.
STATUS: Deferred to v2 unless critical
RAISED: June 2026
