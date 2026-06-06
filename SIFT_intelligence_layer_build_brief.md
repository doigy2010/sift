SIFT INTELLIGENCE LAYER — BUILD BRIEF
File: build_descriptions.py + modifications to sift.py + sift_report.py + run_sift.bat + test_sift_report.py

READ THESE BEFORE WRITING A SINGLE LINE:
1. SIFT_intelligence_layer_design.md — full design session. Every decision is in there.
2. SIFT_questions.md — open gaps, especially the connection map gap (Q: How does Python detect sub-projects).
3. sift.py — to understand build_connection_map() and the output directory pattern.
4. sift_report.py — to understand load_report_data(), render_card(), and the existing derive_description() call you are replacing.
5. test_sift_report.py — to understand the test format before adding new tests.

---

ANTI-BIAS RULES — READ BEFORE WRITING

You do not have opinions about what is better.
You do not suggest alternatives not asked for.
You do not make decisions — you flag and stop.
Every line of code traces to a specific numbered step in the build spec.
If it cannot — do not write it.
If a step is ambiguous — flag the ambiguity and stop. Do not fill the gap with an assumption.
If a prerequisite is missing — stop. Do not build around it.

---

PYTHON IS KING

Python does the extraction. Python does the tagging. Python does the fallback.
LLM only writes plain English from structured evidence Python prepared.
LLM never reads raw files. Never sees file paths. Never sees code.
If Python can do it without an LLM — Python does it.

---

APPROVED LIBRARIES ONLY

os, pathlib, sys, json, datetime, re, collections, hashlib, webbrowser,
urllib.request, flask, tqdm, socket, subprocess, platform, tkinter

No new libraries. No pip installs beyond what is in requirements.txt.
The LLM cascade uses urllib.request only — no requests, no httpx, no aiohttp.

---

DO NOT TOUCH

MACHINE_CONTEXT.md
SIFT_decisions.json
Any SIFT_output_* folder or its contents
mode_retrieve(), read_from_store(), build_connection_map(), find_entry_points()
Mode 2 (retrieve mode) of sift.py
Any existing test that currently passes

---

BUILD ORDER — numbered. Do each in order. Verify tests pass before moving to next.

PREREQUISITE — sift.py: save connection map to disk

Step 0 (prerequisite — do this first, before anything else):
Locate the point in sift.py Mode 1 where build_connection_map() returns.
Immediately after that return, add one json.dump call:
  - Filename: SIFT_connection_map.json
  - Location: same output directory as SIFT_clusters.json
  - Content: the connection_map dict as-is
  - Encoding: utf-8
  - Indent: 2
Do NOT modify build_connection_map() itself.
Do NOT modify any other part of sift.py.

Verify: run sift.py Mode 1 on a small test folder (3-5 files).
Confirm SIFT_connection_map.json appears in the output directory.
Confirm it is valid JSON.
If not: stop and report.

---

COMPONENT 1 — build_descriptions.py: signal extraction per file

Build the function extract_signals(filepath). It must:
- Open the file in UTF-8 with errors='replace'
- On any open failure: log to stderr, return empty signals dict, continue
- Read first 20 lines and last 20 lines only — never the full file
- Detect license text: if more than 10 of the first 20 lines match the pattern
  r'(MIT|Apache|GPL|BSD|Copyright|Permission is hereby granted)' (case-insensitive)
  then extend the read window to 40 lines from the top (skip the license)
- Detect minified: if any single line is longer than 5000 characters,
  record language from extension only and return — no further extraction
- Extract from first+last lines:
  - All import statements (Python: import/from...import; JS: require/import; skip if minified)
  - All function and class definition names (Python: def/class; JS: function keyword or arrow)
  - All comment lines (lines starting with #, //, --)
  - First string that appears to be a docstring (triple-quoted string at file top)
  - Markdown heading on line 1 or 2 (starts with #)
  - HTML <title> tag content
  - YAML frontmatter keys and values (lines between --- at file top)
  - if __name__ == '__main__': presence (yes/no)
  - module.exports or export default presence (yes/no)
  - Flask/FastAPI app.run() presence with port if visible
- Also extract from filename alone (zero file reading): extension -> language
- Return: dict with keys: imports, function_names, class_names, comments,
  docstring, heading, title_tag, entry_point, language, export_type

Test gate 1A: fake file with 5 known imports -> extract_signals returns all 5 in imports list
Test gate 1B: minified file (one line >5000 chars) -> only language returned, no imports
Test gate 1C: file with license in first 20 lines -> window extended, real imports found below
Test gate 1D: file open failure -> empty dict returned, no exception raised

---

COMPONENT 2 — build_descriptions.py: map signals to purpose labels

Build the function signals_to_purpose_labels(signals_dict). It must:
- Map each import to a plain English purpose label using this exact lookup table:
  flask / fastapi / django -> "serves web pages or an API"
  smtplib / sendgrid / mailgun / yagmail -> "sends emails"
  twilio -> "makes phone calls or sends text messages"
  telegram / telebot / python-telegram-bot -> "sends or receives Telegram messages"
  selenium / playwright / beautifulsoup / scrapy -> "reads websites automatically"
  pandas / numpy / polars / scipy -> "processes or analyses data"
  openpyxl / xlrd / xlwt / xlsxwriter -> "reads or writes spreadsheets"
  sqlite3 / sqlalchemy / pymongo / psycopg2 -> "stores or retrieves data"
  anthropic / openai / groq / cohere / replicate -> "uses an AI to generate text"
  stripe / paypalrestsdk / braintree -> "handles payments"
  schedule / apscheduler / celery / rq -> "runs tasks automatically on a timer"
  faster_whisper / whisper / speech_recognition -> "converts speech to text"
  pytest / unittest / nose -> "tests other code"
  click / argparse / typer -> "runs from the command line"
  requests / httpx / aiohttp / urllib -> "gets data from the internet"
  pillow / cv2 / skimage -> "works with images"
  pydub / librosa / sounddevice -> "works with audio"
- If import matches nothing in the table: discard it (do not include as a label)
- Deduplicate. Return top 5 most frequent labels.
- Conflict resolution: if multiple labels from different rows, specificity wins:
  telephony > AI > web serving > data processing > file I/O > utilities

Build the function extract_domain_nouns(signals_dict). It must:
- Take function_names and class_names from signals_dict
- For each name: split on underscores and camelCase boundaries
- Strip verb prefixes: send, get, fetch, load, create, build, make, run, call,
  process, transform, parse, generate, render, display, show, track, log, save,
  calculate, compute, estimate, delete, remove, find, check, validate, update, set
- Keep only noun parts: 3+ characters, not a stopword
  Stopwords to strip: data, file, info, item, list, text, value, result, output,
  input, config, util, helper, main, base, core, test, type, name, time, date, path
- Strip any noun containing these substrings: password, token, secret, key,
  credential, decrypt, encrypt, auth, hash, sign, salt, private, cert
- Deduplicate. Return top 10 most frequent nouns.

Test gate 2A: signals_dict with flask + pandas imports -> labels list contains both mapped labels
Test gate 2B: signals_dict with flask + twilio -> telephony wins conflict, telephony label first
Test gate 2C: signals_dict with unrecognised import "mylib" -> discarded, not in labels
Test gate 2D: function names ["send_vendor_email", "fetch_property_data"] -> nouns include "vendor" and "property"
Test gate 2E: function name "get_secret_key" -> "secret" stripped, "key" stripped, result empty for this name

---

COMPONENT 3 — build_descriptions.py: sub-project detection

Build the function detect_sub_projects(cluster_files, connection_map). It must:
- Input: list of absolute file paths for this cluster; full connection_map dict
- Filter connection_map to keep only edges where BOTH endpoints are in cluster_files
- Run depth-first search to find connected components
- Each component with 2+ files = one sub-project
- Each isolated file (no edges, or only edges to outside-cluster files) = standalone
- Files that appear in edges from MORE than one component = shared utilities
- Return: dict with keys:
  - sub_projects: list of lists of file paths (one list per component)
  - standalone: list of file paths
  - shared_utilities: list of file paths

Build the function label_sub_project(file_list, all_signals). It must:
- Take a list of file paths and the signals extracted for each
- Collect all domain nouns from those files' signals
- Return the top 3 most frequent domain nouns joined as a plain English label
  e.g. ["vendor", "call", "campaign"] -> "vendor call campaign"
- If no domain nouns found: return "unknown purpose"

Test gate 3A: cluster with two disconnected groups of files -> detect_sub_projects returns 2 sub_projects
Test gate 3B: file imported by both groups -> appears in shared_utilities not in either sub_project
Test gate 3C: single file with no edges -> appears in standalone
Test gate 3D: connection_map contains edges to files outside cluster -> those edges filtered out
Test gate 3E: empty connection_map -> all files in standalone

---

COMPONENT 4 — build_descriptions.py: evidence package assembly

Build the function build_evidence_package(cluster, all_signals, sub_project_result, output_dir). It must:
- Input: one cluster dict from SIFT_clusters.json; signals per file (dict keyed by filepath);
  result from detect_sub_projects; output_dir path
- Build the package as a plain-text string in key: value format (NOT JSON)
- Fields to include (in this order):
  cluster_name: [cluster['name']]
  file_count: [cluster['file_count']]
  languages: [comma-separated sorted list of detected languages]
  purpose_signals: [comma-separated top 5 labels]
  domain_vocabulary: [comma-separated top 10 nouns]
  readme_summary: [first 200 chars of README prose — see sanitisation below]
  sub_projects: [N] (followed by one line per sub-project: "- [label]: [N files, purpose signals]")
  connection: [one of: "all parts work together" / "parts are separate tools in the same folder" / "mixed" / "single project"]
  last_touched: [cluster['last_touched']]
  incomplete: [comma-separated TODO/FIXME/BROKEN comment snippets, max 3, max 50 chars each]
  content_hash: [MD5 of sorted file paths + pipe-joined last-modified timestamps]
- README sanitisation: look for README.md or README.txt in cluster['folder'].
  Read first 300 chars. Strip: lines containing forward-slash + alphanumeric (paths);
  lines starting with $; lines starting with # followed by a word that looks like code;
  backtick characters. Keep prose only. If nothing remains after stripping: none.
- content_hash: MD5 of '|'.join(sorted(cluster['files'])) + '|' + '|'.join(str(os.path.getmtime(f)) for f in sorted(cluster['files']) if os.path.exists(f))
- If any field has no data: write the field name with value "none"
- Total package must not exceed 600 tokens (~2400 characters). If it does: truncate sub_project lines first, then readme_summary, then domain_vocabulary.

Build the function assemble_all_packages(clusters, output_dir). It must:
- For each cluster: run extract_signals on all files, collect signals_to_purpose_labels and extract_domain_nouns, run detect_sub_projects, run build_evidence_package
- Write result to SIFT_descriptions.json in output_dir
  Format: dict keyed by cluster['id']. Each value:
  {"evidence_package": "...", "description": null, "tier": null, "content_hash": "..."}
- Print one line per cluster: "  [cluster name] -- done" (no progress bar)
- Any cluster that fails: print "  [cluster name] -- ERROR: [message]", continue

Test gate 4A: evidence package for a known cluster -> all required fields present
Test gate 4B: evidence package -> content_hash is identical on second call with same files
Test gate 4C: evidence package -> no line contains a file path (forward-slash + alphanumeric pattern)
Test gate 4D: domain_vocabulary -> no noun containing "password", "token", "secret", "key", "credential", "decrypt"
Test gate 4E: evidence package longer than 2400 chars -> truncated, still valid

---

COMPONENT 5 — sift_report.py: load descriptions + Python fallback

Add to load_report_data():
- After loading SIFT_clusters.json and SIFT_entry_points.json:
  Look for SIFT_descriptions.json in the same output_dir
  If found: load it. For each cluster_id match: add 'evidence_package' and 'description' keys to the cluster dict.
  If not found: continue normally. All cards must still render.

Build the function python_fallback_description(evidence_package_str). It must:
- Parse the plain key-value text back into a dict (split on first ':' per line)
- Use this exact template:
  "[cluster_name] contains [file_count] files.
  [If sub_projects > 1]:
  It has [N] separate parts: [list each sub-project label on its own line with em dash]
  [connection line]
  [If sub_projects == 1 or 0]:
  It [purpose_signals joined with 'and'].
  [If entry point found in evidence]: It can be started from a [entry_point_type].
  Last touched [last_touched].
  [If incomplete not 'none']: Some parts appear unfinished."
- If purpose_signals is 'none' or empty: use "This project's files did not reveal enough information to describe what they do."
- Never include file paths or extensions in output.

Test gate 5A: known evidence package -> python_fallback_description output contains cluster_name
Test gate 5B: evidence package with 3 sub-projects -> output lists all 3 with em dashes
Test gate 5C: evidence package with empty purpose_signals -> "did not reveal enough information" message used
Test gate 5D: fallback output -> no forward-slash + alphanumeric pattern present

---

COMPONENT 6 — sift_report.py: on-demand LLM generation + cache

Build the function generate_description(evidence_package_str, output_dir, cluster_id). It must:
- Build this exact system instruction (no variation):
  "You are describing a software project to the person who built it. They have forgotten what it does. Write 3 to 5 plain English sentences. State what each part does. State whether the parts work together or are separate tools. Do not use file names, file paths, technical terms, or code. Do not say this looks like -- only state what the evidence shows. Do not recommend anything. Facts only."
- Append the evidence_package_str as the user message
- Try LLM cascade in this order:
  1. Groq: POST to https://api.groq.com/openai/v1/chat/completions
     Model: llama3-8b-8192. Max tokens: 150. Temperature: 0.3.
     Auth: env var GROQ_API_KEY. Timeout: 8 seconds.
     If key missing or request fails: skip to next tier.
  2. OpenRouter: POST to https://openrouter.ai/api/v1/chat/completions
     Model: mistralai/mistral-7b-instruct:free. Max tokens: 150. Temperature: 0.3.
     Auth: env var OPENROUTER_API_KEY. Timeout: 10 seconds.
     If key missing or request fails: skip to next tier.
  3. Ollama: POST to http://localhost:11434/api/generate
     Model: llama3. Max tokens: 150.
     If connection refused or any error: skip to fallback.
  4. Python fallback: call python_fallback_description(evidence_package_str). Tier name: "python".
- All HTTP calls via urllib.request only. No requests library.
- After receiving LLM response: validate it.
  Validation rule: if the response contains any string matching r'[a-zA-Z0-9_\-]+\.[a-zA-Z]{2,4}'
  (looks like a filename or path) OR contains a backtick OR contains r'[A-Za-z]:\\' OR contains '/'
  followed by alphanumeric: discard and use python_fallback_description() instead.
  Log "LLM response discarded -- contained file paths or code" to stderr.
- Return: tuple (description_text, tier_name) where tier_name is one of:
  "Groq", "OpenRouter", "Ollama", "python"

Build the function save_description_cache(output_dir, cluster_id, description_text, tier_name, content_hash). It must:
- Load SIFT_descriptions.json from output_dir
- Update the entry for cluster_id: set description, tier, content_hash
- Write back to file with indent=2
- On any write failure: log to stderr, do not raise

Modify render_card() to use descriptions:
- Check if card dict has 'description' key and it is not None
  If yes: use it as the description text (cache hit)
- Else if card dict has 'evidence_package' key:
  Call generate_description(card['evidence_package'], output_dir, card['id'])
  Call save_description_cache(...)
  Use the returned description_text
- Else: call existing derive_description(card) (unchanged fallback)
- In the evidence block (before the buttons): show the description text in a <p> tag with class "project-description"
- Below the description text, on a new line, if tier_name is not "python":
  <p class="description-tier">Described using [tier_name]</p>
- If tier_name is "python" or description came from cache with tier "python": no attribution line

Test gate 6A: generate_description with mocked Groq returning valid text -> returns ("text", "Groq")
Test gate 6B: generate_description with mocked Groq returning text containing ".py" -> discarded, returns python fallback
Test gate 6C: generate_description with all LLM tiers failing -> returns python fallback, tier "python"
Test gate 6D: save_description_cache writes description to SIFT_descriptions.json at correct cluster_id key
Test gate 6E: render_card with cluster that has cached description -> description appears before buttons in HTML

---

COMPONENT 7 — run_sift.bat and final wiring

Add to run_sift.bat between the build_entry_points.py step and sift_report.py step:
  echo [3b/4] Building project descriptions...
  python "%~dp0build_descriptions.py"
  if %errorlevel% neq 0 (
    echo ERROR: build_descriptions.py failed. Skipping descriptions.
  )
  (do NOT exit on failure -- descriptions are optional, report still opens)

Add build_descriptions.py to the SIFT folder.
Verify run_sift.bat still has exactly 4 echo steps numbered [1/4] through [4/4] with [3b/4] between steps 3 and 4.

Test gate 7A: run_sift.bat content contains "[3b/4] Building project descriptions"
Test gate 7B: build_descriptions.py exists as a file

---

FINAL CHECKS before declaring done:

1. Run test_sift_report.py -- all tests pass, 0 FAIL
2. Confirm SIFT_descriptions.json is created after build_descriptions.py runs on any SIFT output folder
3. Confirm a project card in sift_report.py shows a description (not empty) for a cluster that has an evidence package
4. Confirm the description shown contains no file paths, no extensions, no backticks
5. Confirm clicking a card a second time loads from cache -- no second LLM call
6. Confirm if SIFT_descriptions.json does not exist, the report opens and cards render normally

Report: total test count, any failures, and which LLM tier generated the test descriptions.
