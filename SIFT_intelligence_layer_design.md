# SIFT Intelligence Layer — Design Session
**Date:** June 2026  
**Status:** Design complete. Build spec ready. One prerequisite gap identified (connection map not persisted — see Q3 note).

---

## Team

- **Python architect (lead)** — pipeline structure, data flow, function boundaries
- **Signal analyst** — what a file reveals about its purpose before the LLM sees anything
- **Graph theorist** — sub-project detection as connected-components problem
- **Plain English writer** — what makes a description jog memory vs confuse
- **Failure analyst** — what breaks on unusual machines, 200 projects, empty files

---

## Gold Standard Target

The description SIFT must produce for each cluster:

> "This is a business toolkit with multiple parts. The parts include: a script for calling vendors to buy their property, a tool that maps and values properties, a case progression tracker for buying a house step by step, and an investor campaign with email flows and social media adverts. These three parts all sit under 66 Streets — they appear to be separate tools for the same business. You last touched this 1 week ago."

What makes this gold standard:
- Plain English. Zero jargon.
- States what each sub-part does
- States whether parts are connected or separate
- Does not assume — only states what evidence shows
- Jogs memory without leading the user
- No technical file names or paths visible
- No "this looks like" without evidence

---

## Architecture Rule

Python does the extraction and tagging.  
Python builds a structured evidence package.  
LLM reads only the evidence package — not the files.  
LLM writes the plain English description from evidence.  
If no LLM available — Python writes a simpler version from the same evidence package.

LLM never reads raw files.  
LLM never sees file paths.  
LLM never sees code.  
LLM only sees structured plain English evidence that Python prepared.

---

## Q1 — What can Python extract from a file without reading its full content?

Python reads only the first 20 lines and last 20 lines of each file.

**From first 20 lines:**
- Shebang line — identifies language and runtime
- Import statements — richest signal; nearly all imports live here
- Module docstring — author's own description; highest quality signal; prioritise above all others
- File-level constants (VERSION, BASE_URL, API_ENDPOINT, DATABASE_URL)
- First class/function declaration — often reveals primary purpose
- Markdown heading at line 1 or 2 — document's declared topic
- HTML `<title>` tag — page's declared purpose
- YAML frontmatter — structured metadata

**From last 20 lines:**
- `if __name__ == '__main__':` — confirms entry point
- Final function call — what script does when run
- `module.exports` / `export default` — what file exposes
- Flask/FastAPI `app.run()` — confirms web server, reveals port

**From comments (first and last 20 lines only):**
- Lines starting with `#`, `//`, `--` — author's plain English explanation
- Section dividers — heading text is a purpose signal
- TODO / FIXME / BROKEN — incomplete work signals

**From function and variable names:**
- Function names: verb + noun pattern reveals action and domain
- Class names: reveal domain objects
- Global variable names: reveal data the file works with

**From the file name itself (zero reading required):**
- File name → purpose (vendor_call_script.py, email_campaign.py)
- File extension → language
- File size → complexity proxy
- Directory name → grouping

**Loop resolutions:**
- License text in first 20 lines: detect by pattern (MIT, Apache, GPL). If >10 lines match, extend window by 20 lines. Maximum skip: 60 lines.
- Files with no extension: read first line, classify by shebang or content pattern. If unclassifiable: file name only.
- Minified JS: single line > 5000 chars = minified. Record language only, no further extraction.

---

## Q2 — What do signals tell us about what a file does?

**The mapping principle:** Signal → Category → Plain English label. Same signal always produces same label. This is a lookup table, not inference.

**Import → purpose label (selected):**
- flask / fastapi / django → "serves web pages or an API"
- smtplib / sendgrid / mailgun → "sends emails"
- twilio → "makes phone calls or sends text messages"
- telegram → "sends or receives Telegram messages"
- selenium / playwright / beautifulsoup → "reads websites automatically"
- pandas / numpy / polars → "processes or analyses data"
- openpyxl / xlrd → "reads or writes spreadsheets"
- sqlite3 / sqlalchemy / pymongo → "stores or retrieves data"
- anthropic / openai / groq → "uses an AI to generate text"
- stripe / paypalrestsdk → "handles payments"
- schedule / apscheduler / celery → "runs tasks automatically on a timer"
- faster-whisper / whisper → "converts speech to text"
- pytest / unittest → "tests other code"
- click / argparse → "runs from the command line"

**Function verb → action type:**
- send_ / deliver_ / dispatch_ → "sends something"
- fetch_ / get_ / retrieve_ / load_ → "gets data from somewhere"
- process_ / transform_ / parse_ → "changes data from one form to another"
- generate_ / create_ / build_ / make_ → "creates something new"
- call_ / phone_ / dial_ → "makes a phone call"
- track_ / log_ / record_ / save_ → "keeps a record"
- calculate_ / compute_ / estimate_ → "does a calculation"
- display_ / render_ / show_ → "shows something to the user"

**Function noun → domain vocabulary:**
Collected as raw words: vendor, property, investor, email, call, map, campaign, invoice, client, appointment. Not translated — used to label sub-projects and prompt the LLM.

**Loop resolutions:**
- Conflicting imports (flask AND pandas): specificity wins. Telephony > AI > web serving > data processing > file I/O > utilities.
- Generic function names (main, run, go): mark domain_vocabulary as empty for this file. File name and imports are the only signals.
- Non-Latin comments: include as-is. LLM handles multilingual. Python fallback marks as "comments in unrecognised language."

---

## Q3 — How does Python detect sub-projects within a cluster?

**Critical gap identified:** The connection map built by `build_connection_map()` in sift.py is NOT currently saved to disk. It exists only in memory during the scan and is discarded after. SIFT_clusters.json contains only file path lists — no connection edges.

**Resolution required before build:** sift.py must be modified to save the connection map as `SIFT_connection_map.json` in the output directory during Mode 1. One additional json.dump call at the point where the map is fully built. This is a prerequisite for build_descriptions.py.

**Sub-project detection algorithm (once connection map is available):**
1. Load SIFT_connection_map.json
2. Filter to edges between files within the current cluster only
3. Run connected-components analysis (depth-first or breadth-first search)
4. Each component with 2+ files = one sub-project
5. Single files with no internal edges = standalone
6. Files imported by more than one component = shared utilities (labelled separately)

**Connected vs co-located:**
- Connected: File A imports File B. Runtime dependency — remove B and A breaks.
- Co-located only: same folder, no import edges. Could be separated and neither would break.

**Loop resolutions:**
- Shared utility files: labelled as "shared support files used by multiple parts." Signals contribute to overall evidence but not assigned to any one sub-project.
- Missing connection map entries (dynamic imports): noted in evidence package as "connection analysis may be incomplete."

---

## Q4 — Minimum evidence package for LLM

Maximum 500 tokens. Plain key-value text format — not JSON (wastes tokens on brackets and quotes).

**Fields:**
- `cluster_name` — plain English from folder_name_to_plain_english() — already computed
- `file_count` — integer
- `languages` — list of detected languages e.g. ["Python", "Markdown"]
- `purpose_signals` — top 5 deduplicated plain-English purpose labels (most frequent first)
- `domain_vocabulary` — top 10 deduplicated domain nouns (stripped of sensitive words)
- `readme_summary` — first 200 chars of README, stripped of paths/code/markdown syntax, prose only; null if none
- `sub_projects` — list, each containing: label, file_count, top-3 purpose_signals, entry_point_type, connection ("standalone" or "shares files with other parts")
- `connection_summary` — one of: "all parts work together" / "parts are separate tools in the same folder" / "mixed"
- `last_touched` — relative time string, already computed
- `incomplete_signals` — TODO / FIXME / BROKEN found in comments, max 3
- `content_hash` — MD5 of sorted file paths + last-modified timestamps (for cache invalidation)

**Token count check:** ~243 tokens for a 3-sub-project cluster. Well within 500.

**README sanitisation:** Strip lines containing forward slashes + alphanumerics (paths), backticks, lines starting with `$`, `#` followed by code-like content. Keep prose only.

---

## Q5 — Python fallback description (no LLM)

**Template structure:**
```
[cluster_name] contains [file_count] files.

[If sub-projects]:
It has [N] separate parts:
— [label]: [purpose_signals joined with "and"]
[connection_summary in plain English]

[If single project]:
It [purpose_signals[0]] [and purpose_signals[1] if exists].

It can be started from a [entry_point_type]. / No clear starting point was found.
Last touched [last_touched].
[Some parts appear unfinished.] — only if incomplete_signals non-empty
```

**Limits:** Lists, does not narrate. Names what files do, not what the project is for. Cannot connect parts to a human purpose. Accurate but cold.

**When evidence is incomplete:**
- Empty purpose_signals: "This project's files did not reveal enough information to describe what they do."
- Single file: "A single [language] file that [purpose_signal]. Last touched [last_touched]."
- All generic signals: "A project with [file_count] files. No clear purpose could be determined from file names and structure alone. Last touched [last_touched]."

---

## Q6 — Full pipeline: raw cluster files → gold standard description

**Architecture decision:** Descriptions generated on demand (first card view), not pre-built for all clusters. Signal extraction runs offline (cheap — Python only). LLM call happens when user views the card. Result cached to SIFT_descriptions.json. Second view is instant.

**Step 1 — build_descriptions.py (new file, runs after build_entry_points.py)**
- Reads: SIFT_clusters.json, SIFT_entry_points.json, SIFT_connection_map.json (new — see Q3 gap)
- For each cluster: extracts signals from all files (first + last 20 lines)
- Builds evidence package for each cluster
- Writes all evidence packages to SIFT_descriptions.json
- No LLM calls at this stage — pure Python, fast

**Step 2 — sift_report.py loads descriptions**
- load_report_data() updated to also load SIFT_descriptions.json if it exists
- Each cluster dict gets: evidence_package (always), description (null initially)
- App works without SIFT_descriptions.json — graceful degradation

**Step 3 — User views a project card**
- render_card() checks: is cluster['description'] non-null?
- If yes: show it (cache hit)
- If no and evidence_package exists: call generate_description()

**Step 4 — generate_description(evidence_package)**
- Converts evidence package to plain key-value text
- Prepends instruction: "You are describing a software project to the person who built it. They have forgotten what it does. Write 3 to 5 plain English sentences. State what each part does. State whether the parts work together or are separate tools. Do not use file names, file paths, technical terms, or code. Do not say 'this looks like' — only state what the evidence shows. Do not recommend anything. Facts only."
- Tries cascade: Groq (llama3-8b-8192, max 150 tokens) → OpenRouter (mistral-7b-instruct free) → Ollama → Python fallback
- Validates LLM response: scan for forward slashes + alphanumerics, words ending .py/.js/.html, backticks. If found: discard, use Python fallback.

**Step 5 — Cache result**
- Save description + tier + content_hash timestamp to SIFT_descriptions.json immediately
- Next card load uses cache — no second LLM call

**Step 6 — render_card() shows description**
- Replaces current derive_description(card) call
- Shown in evidence block, before buttons (same position)
- LLM used: small line below "Described using [tier name]"
- Python fallback used: no attribution line

---

## Q7 — What did we not ask?

**Resolved in design:**
- LLM rate limits / 200 projects → on-demand with cache
- Minified files → detected and excluded
- License-only first 20 lines → extend window
- Shared utility files → labelled separately
- Missing connection map entries → noted as incomplete
- Sensitive function names → sanitised before package assembly
- Cache invalidation → content_hash per cluster

**Open / deferred:**
- Description quality drifts as LLM models change — no version tag on cached descriptions. Deferred to v2.
- User cannot correct a wrong description. v2 feature.
- Two clusters that are actually the same project in two folders — SIFT sees them as separate. No fix in v1.
- Cluster containing only data files (CSV, JSON, XML) — Python fallback says "files did not reveal enough information." Correct behaviour. No fix without violating privacy constraint.
- Non-Python projects — signal extraction partial for non-Python languages. Noted in evidence package.
- Description in English only — domain vocabulary may be in user's language. Not handled in v1.
- Network-mounted drives — signal extraction speed not tested on slow drives. Builder must test.

---

## Build Specification

**New file:** `build_descriptions.py`  
**Modified files:** `sift.py` (save connection map), `sift_report.py` (on-demand generation + cache), `run_sift.bat` (add step), `test_sift_report.py` (new tests)

### Prerequisite: sift.py — save connection map to disk

Before building anything else: modify sift.py to write SIFT_connection_map.json to the output directory immediately after build_connection_map() returns. Format: the connection map dict, JSON. This is a single json.dump call. Without this, sub-project detection in build_descriptions.py has no data to work with.

### build_descriptions.py — numbered steps

1. Read SIFT_clusters.json and SIFT_entry_points.json from output directory
2. Read SIFT_connection_map.json from output directory
3. For each cluster: run signal extraction on every file
   - Open file, read first 20 lines + last 20 lines only
   - Skip on open failure (log, continue)
   - Detect license text: if >10 of first 20 lines match license patterns, extend to 40 lines
   - Detect minified file: single line >5000 chars = minified, record language only
   - Extract: all import statements; function/class definitions (via regex); comment lines; first docstring; file name
4. Map imports to purpose labels via lookup table. Keep top 5 most frequent. Deduplicate.
5. Extract domain nouns from function names (noun after verb prefix). Keep top 10. Strip nouns containing: password, token, secret, key, credential, decrypt.
6. Filter connection map to edges within this cluster only. Run connected-components. Assign files to sub-projects. Identify shared utilities.
7. Label each sub-project using dominant domain nouns in that component.
8. Find README in cluster folder. Read first 300 chars. Strip paths, code, markdown. Keep prose only.
9. Compute content_hash: MD5 of sorted file paths joined with last-modified timestamps.
10. Assemble evidence package as plain key-value text block.
11. Write all evidence packages to SIFT_descriptions.json. Format: dict keyed by cluster ID. Each value: {evidence_package, description: null, content_hash, tier: null}.
12. Print one line per cluster. No progress bar needed.

### sift_report.py changes

13. load_report_data(): also load SIFT_descriptions.json if exists. Merge evidence_package and description fields into cluster dicts. Graceful if file absent.
14. New function generate_description(evidence_package, output_dir): build prompt, run LLM cascade, validate response (strip file paths/code if found), return (description_text, tier_name).
15. New function python_fallback_description(evidence_package): template-based from evidence package fields.
16. New function save_description_cache(output_dir, cluster_id, description_text, tier_name): update SIFT_descriptions.json.
17. render_card(): check description cache → if hit show it; if miss and evidence_package exists call generate_description() + save_description_cache(); if neither fall back to existing derive_description().

### run_sift.bat changes

18. Add step between build_entry_points.py and sift_report.py: echo [3b/4] Building project descriptions... / python build_descriptions.py / errorlevel check.

### test_sift_report.py additions

19. Test signal extraction: fake file with known imports → correct purpose labels extracted.
20. Test sub-project detection: fake cluster with two disconnected file groups → two sub-projects detected.
21. Test evidence package assembly: all required fields present, content_hash reproducible, sensitive nouns stripped.
22. Test Python fallback description: known evidence package → output matches expected template structure.
23. Test LLM output validation: fake LLM response containing a file path → discarded, Python fallback used.

---

## What We Did Not Consider

1. Description quality drift as LLM models change — no version tag on cached descriptions
2. User correction of wrong descriptions — no mechanism in v1
3. Cluster merging — two clusters that are the same project in two folders seen as separate
4. Data-only clusters — correct behaviour is "could not describe," no fix possible
5. Non-English projects — domain vocabulary may be in user's language, description will be English
6. Network-mounted drive performance — signal extraction speed not tested on slow drives
