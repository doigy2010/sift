import os, sys, re, platform, zipfile, hashlib, datetime, pickle, mimetypes
from pathlib import Path

# ── Version ──────────────────────────────────────────────────────────────────
VERSION = "2.0"

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_NAME     = os.path.basename(__file__)
CHECKPOINT_FILE = "sift_checkpoint.pkl"

# Extensions Python can read as plain text
TEXT_EXTENSIONS = {
    '.py','.js','.ts','.jsx','.tsx','.html','.htm','.css','.scss',
    '.json','.yaml','.yml','.toml','.ini','.cfg','.conf','.env',
    '.txt','.md','.rst','.csv','.xml','.sql','.sh','.bat','.ps1',
    '.rb','.php','.java','.c','.cpp','.h','.cs','.go','.rs',
    '.log','.gitignore','.dockerfile','dockerfile','.htaccess',
    '.env.example','.env.local','.env.production',
}

# Extensions that exist but cannot be read as text — still indexed
BINARY_EXTENSIONS = {
    '.exe','.dll','.so','.dylib','.bin','.pyc','.pyo','.class','.o',
    '.jpg','.jpeg','.png','.gif','.bmp','.ico','.webp','.tiff',
    '.mp3','.mp4','.wav','.avi','.mov','.mkv','.flac',
    '.zip','.tar','.gz','.rar','.7z','.bz2',
    '.pdf','.docx','.xlsx','.pptx','.doc','.xls','.ppt',
    '.sqlite','.sqlite3','.db',
    '.ttf','.woff','.woff2','.eot','.otf',
    '.DS_Store','.lock',
}

# System folders skipped — professional practice (deNISTing equivalent)
# All skipped folders are logged — nothing hidden, just set aside
SYSTEM_DIRS = {
    'Windows','WinSxS','System32','SysWOW64','MININT',
    '$Recycle.Bin','$WINDOWS.~BT','Recovery',
    'Program Files','Program Files (x86)','ProgramData','AppData',
    'Python313','Python312','Python311','Python310','Python39','Python38',
    'site-packages','dist-packages',
    'node_modules','__pycache__','.git','venv','.venv','env','.env',
    'dist','build','.idea','.vscode','.next','.cache',
    '.pytest_cache','.mypy_cache',
    'Adobe','.tmp.driveupload','.tmp.drivedownload',
}

SKIP_DIRS = SYSTEM_DIRS

# ── Redaction patterns ────────────────────────────────────────────────────────
REDACT_PATTERNS = [
    (re.compile(r'((?:api[_-]?key|api[_-]?secret|access[_-]?token|auth[_-]?token|secret[_-]?key|private[_-]?key)\s*[:=]\s*)([^\s\n\r]{8,})', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'((?:password|passwd|pwd)\s*[:=]\s*)([^\s\n\r]{3,})', re.IGNORECASE), r'\1[REDACTED]'),
    (re.compile(r'\b(\d{5})(\d{3})\b'), lambda m: 'X'*5 + m.group(2)),
    (re.compile(r'\b(\d{2}-\d{2}-)(\d{2})\b'), lambda m: 'XX-XX-' + m.group(2)),
    (re.compile(r'\b(\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?)(\d{4})\b'), lambda m: 'XXXX-XXXX-XXXX-' + m.group(2)),
    (re.compile(r'\b([a-zA-Z0-9._%+-]{3,})(@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})\b'), lambda m: m.group(1)[-2:].rjust(len(m.group(1)), '*') + m.group(2)),
    (re.compile(r'\b((?:\+44|0)[\s-]?(?:\d[\s-]?){6,8})(\d{3})\b'), lambda m: 'X'*8 + m.group(2)),
    (re.compile(r'(-----BEGIN [A-Z ]+-----)[\s\S]+?(-----END [A-Z ]+-----)', re.MULTILINE), r'\1\n[REDACTED]\n\2'),
]

def redact(text):
    for pattern, replacement in REDACT_PATTERNS:
        try:
            text = pattern.sub(replacement, text)
        except Exception:
            pass
    return text

# ── Detect language from extension ───────────────────────────────────────────
LANG_MAP = {
    '.py':'Python', '.js':'JavaScript', '.ts':'TypeScript',
    '.jsx':'React/JSX', '.tsx':'React/TSX', '.html':'HTML',
    '.css':'CSS', '.scss':'SCSS', '.json':'JSON', '.sql':'SQL',
    '.rb':'Ruby', '.php':'PHP', '.java':'Java', '.cs':'C#',
    '.go':'Go', '.rs':'Rust', '.sh':'Shell', '.bat':'Batch',
    '.md':'Markdown', '.yaml':'YAML', '.yml':'YAML',
    '.toml':'TOML', '.xml':'XML', '.csv':'CSV',
}

def detect_language(path):
    return LANG_MAP.get(Path(path).suffix.lower(), 'Unknown')

# ── File reader ───────────────────────────────────────────────────────────────
def read_file(path):
    for enc in ['utf-8', 'latin-1', 'cp1252', 'utf-16']:
        try:
            with open(path, 'r', encoding=enc, errors='replace') as f:
                return f.read()
        except Exception:
            continue
    return None

# ── Build index entry for every file ─────────────────────────────────────────
def build_index_entry(fpath, readable, content=None, error=None):
    try:
        stat       = fpath.stat()
        size_bytes = stat.st_size
        modified   = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y %H:%M')
        created    = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%d %b %Y %H:%M')
        size_label = f"{size_bytes}b" if size_bytes < 1024 else f"{size_bytes//1024}kb" if size_bytes < 1024*1024 else f"{size_bytes//1024//1024}mb"
    except Exception:
        size_bytes = 0
        modified   = 'unavailable'
        created    = 'unavailable'
        size_label = 'unavailable'

    entry = []
    entry.append(f"\nFILE: {fpath}")
    entry.append(f"TYPE: {detect_language(fpath)} | {fpath.suffix.lower() or 'no extension'}")
    entry.append(f"SIZE: {size_label}")
    entry.append(f"CREATED:  {created}")
    entry.append(f"MODIFIED: {modified}")
    entry.append(f"READABLE: {'Yes' if readable else 'No'}")

    if not readable:
        entry.append(f"REASON: {error or 'binary or unsupported format'}")
        entry.append(f"NOTE: File exists and is indexed. Content not available.")
    else:
        if content:
            lines = content.splitlines()
            line_count = len(lines)
            word_count = len(content.split())
            # First meaningful line
            first_line = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('#')), '')
            if first_line:
                first_line = first_line[:120]
            # Key signals
            todos    = len(re.findall(r'\b(TODO|FIXME|HACK|BUG|XXX)\b', content, re.IGNORECASE))
            imports  = re.findall(r'^(?:import|from|require|include)\s+(\S+)', content, re.MULTILINE)
            has_keys = bool(re.search(r'(?:api[_-]?key|password|secret|token)', content, re.IGNORECASE))

            entry.append(f"LINES: {line_count} | WORDS: {word_count}")
            if first_line:
                entry.append(f"FIRST LINE: {first_line}")
            if imports:
                entry.append(f"IMPORTS: {', '.join(imports[:8])}" + (' ...' if len(imports) > 8 else ''))
            if todos > 0:
                entry.append(f"UNFINISHED NOTES: {todos} TODO/FIXME found")
            if has_keys:
                entry.append(f"SENSITIVE: Contains credential patterns (will be redacted in content)")
        else:
            entry.append(f"NOTE: Empty file")

    entry.append("-" * 50)
    return '\n'.join(entry)

# ── Prompts ───────────────────────────────────────────────────────────────────
INDEX_PROMPT = """
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

"""

CONTENT_PROMPT = """
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

"""

ENSEMBLE_PROMPT = """
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

"""

# ── Walk all files — index everything ────────────────────────────────────────
def walk_and_index(scan_roots):
    if isinstance(scan_roots, str):
        scan_roots = [scan_roots]

    scan_root = Path(scan_roots[0])
    all_entries  = []
    
    print("Scanning all files...")
    found = []
    for root in scan_roots:
        found.extend(list(Path(root).rglob('*')))
    files = [f for f in found if f.is_file()]
    total = len(files)
    
    for i, fpath in enumerate(files):
        # Skip system and SIFT files
        if fpath.name in {SCRIPT_NAME, 'run_sift.bat', CHECKPOINT_FILE}:
            continue
        if any(skip in fpath.parts for skip in SKIP_DIRS):
            continue
        if any(part.startswith('SIFT_output_') for part in fpath.parts):
            continue

        pct = int((i+1)/total*40)
        bar = '#'*pct + '-'*(40-pct)
        print(f"\r[{bar}] {i+1}/{total} {fpath.name[:35]:<35}", end='', flush=True)

        ext = fpath.suffix.lower()

        if ext in BINARY_EXTENSIONS:
            all_entries.append((fpath, False, None, 'binary format'))
            continue

        content = read_file(fpath)
        if content is None:
            all_entries.append((fpath, False, None, 'could not read'))
        else:
            content = redact(content)
            all_entries.append((fpath, True, content, None))

    print()
    return all_entries, total

# ── Mode 1: Full scan and index ───────────────────────────────────────────────
def mode_scan(output_dir, scan_root, plain_english=False):
    date_str = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    scan_id  = hashlib.md5(f"{platform.node()}{date_str}".encode()).hexdigest()[:12].upper()

    scan_label = ', '.join(str(r) for r in scan_root) if isinstance(scan_root, list) else str(scan_root)

    all_entries, total = walk_and_index(scan_root)

    readable   = [(f,r,c,e) for f,r,c,e in all_entries if r]
    unreadable = [(f,r,c,e) for f,r,c,e in all_entries if not r]

    print(f"\nTotal files found:    {total}")
    print(f"Readable as text:     {len(readable)}")
    print(f"Binary/unreadable:    {len(unreadable)}")

    # ── Shared header block ───────────────────────────────────────────────────
    now_str = datetime.datetime.now().strftime('%d %B %Y %H:%M')
    cutoff  = datetime.datetime.now() - datetime.timedelta(days=90)

    # Folder structure
    folders = sorted(set(str(f.parent) for f,r,c,e in all_entries))
    folder_lines = []
    for folder in folders:
        count = sum(1 for f,r,c,e in all_entries if str(f.parent) == folder)
        folder_lines.append(f"  {folder}  ({count} files)")

    # Technology summary
    lang_counts = {}
    for fpath, readable_flag, content, error in all_entries:
        lang = detect_language(fpath)
        if lang != 'Unknown':
            lang_counts[lang] = lang_counts.get(lang, 0) + 1

    # Signals — files with TODOs, sensitive patterns, recently modified
    flagged = []
    for fpath, readable_flag, content, error in all_entries:
        if not readable_flag or not content:
            continue
        signals = []
        todos = len(re.findall(r'\b(TODO|FIXME|HACK|BUG)\b', content, re.IGNORECASE))
        has_keys = bool(re.search(r'(?:api[_-]?key|password|secret|token)', content, re.IGNORECASE))
        try:
            mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime)
            recent = mtime > cutoff
        except Exception:
            recent = False
        if todos > 0:
            signals.append(f"{todos} TODO/FIXME")
        if has_keys:
            signals.append("credential patterns")
        if recent:
            signals.append("modified in last 90 days")
        if signals:
            flagged.append((fpath, signals))

    # ── BUILD SUMMARY FILE ────────────────────────────────────────────────────
    summary_lines = []
    summary_lines.append("=" * 60)
    summary_lines.append("SIFT v2 INDEX SUMMARY")
    summary_lines.append("=" * 60)
    summary_lines.append(f"Scan ID:      {scan_id}")
    summary_lines.append(f"Date:         {now_str}")
    summary_lines.append(f"Machine:      {platform.node()}")
    summary_lines.append(f"OS:           {platform.system()} {platform.release()}")
    summary_lines.append(f"Scanned:      {scan_label}")
    summary_lines.append(f"Total files:  {total}")
    summary_lines.append(f"Readable:     {len(readable)}")
    summary_lines.append(f"Unreadable:   {len(unreadable)}")
    summary_lines.append(f"Folders:      {len(folders)}")
    summary_lines.append("")

    summary_lines.append("TECHNOLOGIES DETECTED:")
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        summary_lines.append(f"  {lang}: {count} files")
    summary_lines.append("")

    summary_lines.append("FOLDER STRUCTURE (all folders):")
    summary_lines.extend(folder_lines)
    summary_lines.append("")

    summary_lines.append("=" * 60)
    summary_lines.append(f"FLAGGED FILES ({len(flagged)} files with signals)")
    summary_lines.append("These files have TODOs, credentials, or recent changes.")
    summary_lines.append("=" * 60)
    for fpath, signals in flagged:
        try:
            mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).strftime('%d %b %Y')
        except Exception:
            mtime = 'unknown'
        summary_lines.append(f"\nFILE: {fpath}")
        summary_lines.append(f"SIGNALS: {', '.join(signals)}")
        summary_lines.append(f"MODIFIED: {mtime}")
        summary_lines.append("-" * 50)

    summary_lines.append("")
    summary_lines.append("=" * 60)
    summary_lines.append("UNREADABLE FILES (binary/unsupported)")
    summary_lines.append("These exist but cannot be read as text.")
    summary_lines.append("=" * 60)
    for fpath, r, c, error in unreadable:
        try:
            size  = fpath.stat().st_size
            mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).strftime('%d %b %Y')
            size_label = f"{size//1024}kb" if size >= 1024 else f"{size}b"
        except Exception:
            size_label = 'unknown'
            mtime = 'unknown'
        summary_lines.append(f"  {fpath}  [{fpath.suffix}]  {size_label}  {mtime}")

    summary_lines.append("")
    summary_lines.append("NOTE: Full file-by-file index is in SIFT_index_full.txt")
    summary_lines.append("Request it only if this summary is not enough.")

    summary_text = '\n'.join(summary_lines)

    # Choose prompt language based on user type
    if plain_english:
        active_prompt = INDEX_PROMPT.replace(
            "PROJECT TYPE:",
            "WHAT TYPE OF PROJECT IS THIS:"
        ).replace(
            "WHAT IT DOES:",
            "WHAT DOES IT DO IN PLAIN ENGLISH:"
        ).replace(
            "AGE AND ACTIVITY:",
            "HOW OLD IS IT AND IS IT STILL BEING WORKED ON:"
        ).replace(
            "WHAT IS BROKEN OR MISSING:",
            "WHAT LOOKS BROKEN, UNFINISHED OR MISSING:"
        ).replace(
            "FILES I NEED TO READ:",
            "FILES YOU NEED TO SEE TO FINISH YOUR ANSWER:"
        ).replace(
            "WHAT I AM GUESSING:",
            "WHAT ARE YOU UNSURE ABOUT:"
        ).replace(
            "No technical jargon.",
            ""
        ) + "
IMPORTANT: Reply in plain English. No technical jargon. Write as if explaining to someone who has never coded. Avoid terms like codebase, repository, dependencies, or stack.
"
    else:
        active_prompt = INDEX_PROMPT

    summary_path = output_dir / 'SIFT_index_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(active_prompt)
        f.write(summary_text)

    # ── BUILD FULL INDEX FILE ─────────────────────────────────────────────────
    full_lines = []
    full_lines.append("=" * 60)
    full_lines.append("SIFT v2 FULL INDEX")
    full_lines.append(f"Scan ID: {scan_id}  |  {now_str}")
    full_lines.append("Every file. Nothing removed.")
    full_lines.append("=" * 60)
    full_lines.append("")

    for fpath, readable_flag, content, error in all_entries:
        full_lines.append(build_index_entry(fpath, readable_flag, content, error))

    full_path = output_dir / 'SIFT_index_full.txt'
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(full_lines))

    # ── Ensemble prompt ───────────────────────────────────────────────────────
    ensemble_path = output_dir / 'SIFT_ensemble_prompt.txt'
    with open(ensemble_path, 'w', encoding='utf-8') as f:
        f.write(ENSEMBLE_PROMPT)
        f.write("\n[PASTE MODEL REPLIES BELOW — LABEL EACH ONE]\n")
        f.write("\n--- CLAUDE ---\n[paste here]\n")
        f.write("\n--- GPT ---\n[paste here]\n")
        f.write("\n--- GEMINI ---\n[paste here]\n")
        f.write("\n--- GROQ ---\n[paste here]\n")

    # ── Content store for mode 2 ──────────────────────────────────────────────
    content_store = {str(fpath): content for fpath,r,content,e in all_entries if r and content}
    store_path = output_dir / 'sift_store.pkl'
    with open(store_path, 'wb') as f:
        pickle.dump({'scan_id': scan_id, 'scan_root': str(scan_root), 'store': content_store}, f)

    print(f"\nSummary index: SIFT_index_summary.txt  (use this first)")
    print(f"Full index:    SIFT_index_full.txt     (use only if needed)")
    print(f"Store:         sift_store.pkl           (used by mode 2)")
    print(f"Ensemble:      SIFT_ensemble_prompt.txt")

    return scan_id, output_dir

# ── Mode 2: Retrieve specific files ──────────────────────────────────────────
def mode_retrieve(output_dir):
    # Find most recent store
    stores = sorted(Path('.').glob('SIFT_output_**/sift_store.pkl'))
    if not stores:
        stores = sorted(Path(output_dir).glob('sift_store.pkl'))

    if not stores:
        print("No previous scan found. Run Mode 1 first.")
        return

    store_path = stores[-1]
    print(f"Loading scan from: {store_path.parent.name}")

    with open(store_path, 'rb') as f:
        data = pickle.load(f)

    scan_id = data['scan_id']
    store   = data['store']

    print(f"Scan ID: {scan_id}")
    print(f"Files available: {len(store)}")
    print()
    print("Paste the file paths the LLM requested.")
    print("One path per line. Press Enter twice when done.")
    print()

    lines = []
    while True:
        line = input()
        if line == '':
            if lines:
                break
        else:
            lines.append(line.strip())

    # Clean paths — remove bullet points, dashes, numbers etc
    requested = []
    for line in lines:
        clean = re.sub(r'^[\s\-\*\d\.\)]+', '', line).strip()
        if clean:
            requested.append(clean)

    print(f"\nLooking for {len(requested)} files...")

    found     = []
    not_found = []

    for req in requested:
        # Try exact match first
        if req in store:
            found.append((req, store[req]))
            continue
        # Try case-insensitive match
        req_lower = req.lower()
        match = next((k for k in store if k.lower() == req_lower), None)
        if match:
            found.append((match, store[match]))
            continue
        # Try filename only match
        req_name = Path(req).name.lower()
        match = next((k for k in store if Path(k).name.lower() == req_name), None)
        if match:
            found.append((match, store[match]))
            continue
        not_found.append(req)

    print(f"Found: {len(found)} | Not found: {len(not_found)}")

    if not_found:
        print("\nCould not find:")
        for nf in not_found:
            print(f"  {nf}")

    if not found:
        print("No files retrieved. Check the paths and try again.")
        return

    # Write retrieved content file
    date_str     = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    retrieve_path = Path(os.path.dirname(os.path.abspath(__file__))) / f"SIFT_retrieved_{date_str}.txt"

    with open(retrieve_path, 'w', encoding='utf-8') as f:
        f.write(CONTENT_PROMPT)
        f.write(f"Scan ID: {scan_id}\n")
        f.write(f"Files retrieved: {len(found)}\n\n")
        for fpath, content in found:
            f.write(f"\n{'='*50}\n")
            f.write(f"FILE: {fpath}\n")
            f.write(f"{'='*50}\n")
            f.write(content)
            f.write("\n")

    print(f"\nRetrieved file saved: {retrieve_path.name}")
    return retrieve_path

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    print("=" * 60)
    print("  SIFT v2 - Find the truth in any codebase")
    print("  Sifting through shit to get to paradise")
    print("=" * 60)
    print()
    print("What would you like to do?")
    print()
    print("  1 - Full scan and build index")
    print("      Run this first on the laptop to investigate.")
    print()
    print("  2 - Retrieve files the LLM requested")
    print("      Run this after pasting the index to the LLM.")
    print()
    mode = input("Enter 1 or 2: ").strip()

    if mode == '2':
        output_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        retrieve_path = mode_retrieve(output_dir)
        if retrieve_path:
            print()
            print("NEXT STEPS:")
            print(f"1. Open {retrieve_path.name}")
            print(f"2. Paste it into the SAME LLM conversation")
            print(f"3. The LLM will complete its analysis")
            print(f"4. Repeat for each LLM independently")
            print(f"5. Then use SIFT_ensemble_prompt.txt to compare")
        print()
        input("Press Enter to close.")
        return

    # Mode 1 — get user type first
    print()
    print("Who is using SIFT today?")
    print()
    print("  1 - Builder or tinkerer (plain English output, no jargon)")
    print("  2 - Developer or technical professional (full technical detail)")
    print()
    user_type = input("Enter 1 or 2: ").strip()
    plain_english = (user_type == "1")

    print()
    print("What do you want to scan?")
    print()
    print("  1 - Whole machine (recommended — finds everything, use on unknown laptops)")
    print("  2 - Specific folder (if you know where the project lives)")
    print()
    scan_choice = input("Enter 1 or 2: ").strip()

    if scan_choice == '1':
        # Detect all drives on Windows, or use root on Mac/Linux
        if platform.system() == 'Windows':
            import string
            drives = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            print(f"\nDrives found: {', '.join(drives)}")
            scan_root = drives  # list of roots
        else:
            scan_root = ['/']
        print("Scanning whole machine. This may take several minutes on large drives.")
    else:
        scan_root_input = input("\nFolder to scan: ").strip()
        if not scan_root_input:
            print("No folder entered. Cancelled.")
            sys.exit(1)
        if not os.path.exists(scan_root_input):
            print(f"Path not found: {scan_root_input}")
            sys.exit(1)
        scan_root = [scan_root_input]

    # Final warning — all choices made, last chance to cancel
    print()
    print("=" * 50)
    print("READY TO SCAN")
    print("=" * 50)
    if isinstance(scan_root, list):
        print(f"Scanning:  All drives ({', '.join(str(r) for r in scan_root)})")
    else:
        print(f"Scanning:  {scan_root[0]}")
    print(f"User type: {'Builder / plain English output' if plain_english else 'Developer / technical output'}")
    print()
    print("This script will read all text files in the scanned location.")
    print("Sensitive data is redacted before anything is written.")
    print("Nothing on the laptop will be changed or deleted.")
    print()
    go = input("Start scan? (Y/N): ").strip().upper()
    if go != 'Y':
        print("Scan cancelled.")
        sys.exit(0)

    date_str   = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    output_dir = Path(os.path.dirname(os.path.abspath(__file__))) / f"SIFT_output_{date_str}"
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput folder: {output_dir}\n")

    scan_id, output_dir = mode_scan(output_dir, scan_root, plain_english)

    # Zip output
    print()
    zip_password = input("Password to protect output zip (or Enter to skip): ").strip()
    zip_path = output_dir.parent / f"SIFT_output_{date_str}.zip"
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
        if zip_password:
            zf.setpassword(zip_password.encode())
        for f in output_dir.iterdir():
            if f.name != 'sift_store.pkl':
                zf.write(f, f.name)

    print()
    print("=" * 60)
    print("SIFT SCAN COMPLETE")
    print("=" * 60)
    print(f"Scan ID:  {scan_id}")
    print(f"Output:   {output_dir}")
    print()
    print("NEXT STEPS:")
    print("1. Open SIFT_index_summary.txt — start here")
    print("2. Upload to Claude in a FRESH INCOGNITO window")
    print("3. LLM replies with what it found and files it needs")
    print("4. Run SIFT again, choose option 2, paste the file list")
    print("5. Upload SIFT_retrieved file back to same LLM conversation")
    print("6. Repeat steps 2-5 for GPT, Gemini, Groq independently")
    print("7. Use SIFT_ensemble_prompt.txt to compare all results")
    print("8. If LLM needs more depth — upload SIFT_index_full.txt")
    print()
    print(f"Email {zip_path} to yourself NOW")
    print()
    input("Press Enter to close.")

if __name__ == '__main__':
    main()
