import os, sys, re, time, json, platform, zipfile, hashlib, datetime, mimetypes
from pathlib import Path

# ── Version ───────────────────────────────────────────────────────────────────
VERSION = "2.2"

# ── Configuration ─────────────────────────────────────────────────────────────
SCRIPT_NAME     = os.path.basename(__file__)
SCRIPT_DIR      = Path(os.path.dirname(os.path.abspath(__file__)))
STORE_FILENAME  = 'sift_content_store.txt'   # plain text — no pickle, no memory spike

# Throttle: pause between files so the machine stays responsive
# 0.003 = 3ms per file. On 10,000 files = 30 seconds added. Safe for slow drives.
THROTTLE_DELAY  = 0.003

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

# Pass 2 filter — parent folder names excluded from content scan
SKIP_DIRS = {
    '.obsidian',
    '.claude',
    'worktrees',
    '.trash',
    '.sync',
    'plugins',
    'node_modules',
    '__pycache__',
    '.git',
}


# ── Time estimate ─────────────────────────────────────────────────────────────
def time_estimate(n_files):
    """Return plain English scan time estimate based on file count."""
    if n_files < 500:
        return "About 1 minute"
    if n_files < 2000:
        return "About 2-5 minutes"
    if n_files < 5000:
        return "About 5-15 minutes"
    return ("This may take a while. Your machine will slow slightly. "
            "Leave it running.")


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


# ── Language detection ────────────────────────────────────────────────────────
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


# ── Index entry builder ───────────────────────────────────────────────────────
def build_index_entry(fpath, readable, content=None, error=None):
    try:
        stat       = fpath.stat()
        size_bytes = stat.st_size
        modified   = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y %H:%M')
        created    = datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%d %b %Y %H:%M')
        size_label = (f"{size_bytes}b" if size_bytes < 1024
                      else f"{size_bytes//1024}kb" if size_bytes < 1024*1024
                      else f"{size_bytes//1024//1024}mb")
    except Exception:
        size_bytes, modified, created, size_label = 0, 'unavailable', 'unavailable', 'unavailable'

    entry = [
        f"\nFILE: {fpath}",
        f"TYPE: {detect_language(fpath)} | {fpath.suffix.lower() or 'no extension'}",
        f"SIZE: {size_label}",
        f"CREATED:  {created}",
        f"MODIFIED: {modified}",
        f"READABLE: {'Yes' if readable else 'No'}",
    ]

    if not readable:
        entry.append(f"REASON: {error or 'binary or unsupported format'}")
        entry.append("NOTE: File exists and is indexed. Content not available.")
    elif content:
        lines      = content.splitlines()
        todos      = len(re.findall(r'\b(TODO|FIXME|HACK|BUG|XXX)\b', content, re.IGNORECASE))
        imports    = re.findall(r'^(?:import|from|require|include)\s+(\S+)', content, re.MULTILINE)
        has_keys   = bool(re.search(r'(?:api[_-]?key|password|secret|token)', content, re.IGNORECASE))
        first_line = next((l.strip() for l in lines if l.strip() and not l.strip().startswith('#')), '')

        entry.append(f"LINES: {len(lines)} | WORDS: {len(content.split())}")
        if first_line:
            entry.append(f"FIRST LINE: {first_line[:120]}")
        if imports:
            entry.append(f"IMPORTS: {', '.join(imports[:8])}" + (' ...' if len(imports) > 8 else ''))
        if todos:
            entry.append(f"UNFINISHED NOTES: {todos} TODO/FIXME found")
        if has_keys:
            entry.append("SENSITIVE: Contains credential patterns (will be redacted in content)")
    else:
        entry.append("NOTE: Empty file")

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


# ── Content store — streaming write, no RAM spike ────────────────────────────
# Files are written to disk immediately as scanned.
# Mode 2 reads back specific files by searching the store.
# No pickle. No dict in memory. Safe on any size machine.

STORE_MARKER_START = "===SIFT_FILE_START==="
STORE_MARKER_END   = "===SIFT_FILE_END==="

def write_to_store(store_file, fpath, content):
    store_file.write(f"{STORE_MARKER_START}\n")
    store_file.write(f"PATH: {fpath}\n")
    store_file.write(f"{STORE_MARKER_END_HEADER}\n")
    store_file.write(content)
    store_file.write(f"\n{STORE_MARKER_END}\n")

STORE_MARKER_END_HEADER = "===SIFT_CONTENT_START==="

def read_from_store(store_path, requested_paths):
    """Read specific file contents from the text store. No full load into RAM."""
    found     = {}
    not_found = list(requested_paths)

    if not store_path.exists():
        return found, not_found

    req_lower = {p.lower(): p for p in requested_paths}
    req_names = {Path(p).name.lower(): p for p in requested_paths}

    with open(store_path, 'r', encoding='utf-8', errors='replace') as f:
        current_path   = None
        in_content     = False
        content_lines  = []

        for line in f:
            line_stripped = line.rstrip('\n')

            if line_stripped == STORE_MARKER_START:
                current_path  = None
                in_content    = False
                content_lines = []
                continue

            if line_stripped.startswith("PATH: ") and not in_content:
                current_path = line_stripped[6:].strip()
                continue

            if line_stripped == STORE_MARKER_END_HEADER:
                in_content = True
                continue

            if line_stripped == STORE_MARKER_END:
                if current_path and in_content:
                    # Check if this path was requested
                    cp_lower = current_path.lower()
                    cp_name  = Path(current_path).name.lower()

                    matched_req = None
                    if current_path in requested_paths:
                        matched_req = current_path
                    elif cp_lower in req_lower:
                        matched_req = req_lower[cp_lower]
                    elif cp_name in req_names:
                        matched_req = req_names[cp_name]

                    if matched_req and matched_req not in found:
                        found[matched_req] = '\n'.join(content_lines)
                        if matched_req in not_found:
                            not_found.remove(matched_req)

                current_path  = None
                in_content    = False
                content_lines = []
                continue

            if in_content:
                content_lines.append(line_stripped)

    return found, not_found


# ── Pass 1: metadata collection ───────────────────────────────────────────────
def collect_metadata(scan_roots, output_dir):
    """Walk all files using os.scandir. Collect metadata only — no file opens.
    Writes one JSON record per line to SIFT_metadata.json. Returns total file count."""
    if isinstance(scan_roots, str):
        scan_roots = [scan_roots]

    meta_path = output_dir / 'SIFT_metadata.json'
    total = 0

    with open(meta_path, 'w', encoding='utf-8') as meta_file:
        for scan_root in scan_roots:
            dirs_to_visit = [Path(scan_root)]
            while dirs_to_visit:
                current_dir = dirs_to_visit.pop()
                try:
                    entries = list(os.scandir(current_dir))
                except Exception:
                    continue
                for entry in entries:
                    if entry.is_dir(follow_symlinks=False):
                        if (entry.name not in SYSTEM_DIRS
                                and not entry.name.startswith('SIFT_output_')):
                            dirs_to_visit.append(Path(entry.path))
                    elif entry.is_file(follow_symlinks=False):
                        try:
                            stat = entry.stat()
                            record = {
                                'path':   entry.path,
                                'size':   stat.st_size,
                                'mtime':  stat.st_mtime,
                                'ext':    Path(entry.name).suffix.lower(),
                                'parent': Path(entry.path).parent.name,
                            }
                            meta_file.write(json.dumps(record) + '\n')
                            total += 1
                            if total % 1000 == 0:
                                print(f"  Pass 1: {total} files found...")
                        except Exception:
                            continue

    return total


# ── Pass 2: filter metadata to scan targets ────────────────────────────────────
def filter_for_scan(output_dir):
    """Read SIFT_metadata.json. Return list of paths passing all three rules:
    extension in TEXT_EXTENSIONS, size 100–5000000 bytes, parent not in SKIP_DIRS."""
    meta_path = output_dir / 'SIFT_metadata.json'
    selected = []

    with open(meta_path, 'r', encoding='utf-8') as meta_file:
        for line in meta_file:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except Exception:
                continue
            if record['ext'] not in TEXT_EXTENSIONS:
                continue
            if not (100 <= record['size'] <= 5000000):
                continue
            if record['parent'] in SKIP_DIRS:
                continue
            selected.append(record['path'])

    return selected


# ── Walk and index — streaming, throttled ─────────────────────────────────────
def walk_and_index(scan_roots, output_dir):
    """
    Walk all files. Write content to disk as we go — no RAM accumulation.
    Returns stats only, not file contents.
    """
    if isinstance(scan_roots, str):
        scan_roots = [scan_roots]

    store_path = output_dir / STORE_FILENAME
    now        = datetime.datetime.now()
    cutoff     = now - datetime.timedelta(days=90)

    # Stats accumulators — lightweight
    n_readable  = 0
    n_binary    = 0
    n_skipped   = 0
    lang_counts = {}
    flagged     = []    # (fpath, [signals]) — only metadata, not content
    unreadable  = []    # (fpath, ext, size_label, mtime, error)
    folder_set  = set()

    total = collect_metadata(scan_roots, output_dir)
    print(f"Pass 1 complete: {total} files found")

    target_files = filter_for_scan(output_dir)
    n_targets    = len(target_files)
    print(f"Pass 2 scanning: {n_targets} files selected")
    print(f"Time estimate:   {time_estimate(n_targets)}")

    meta_path = output_dir / 'SIFT_metadata.json'
    if meta_path.exists():
        meta_path.unlink()

    try:
        from tqdm import tqdm as _tqdm
        _use_tqdm = True
    except ImportError:
        _use_tqdm = False

    print("Scanning files...")
    scan_count = 0

    _iter = (
        _tqdm(target_files, desc='Scanning', unit='file', ncols=72)
        if _use_tqdm else target_files
    )

    with open(store_path, 'w', encoding='utf-8') as store_file:
        for file_path_str in _iter:
            fpath = Path(file_path_str)
            fname = fpath.name

            if fname in {SCRIPT_NAME, 'run_sift.bat', STORE_FILENAME}:
                continue

            folder_set.add(str(fpath.parent))
            scan_count += 1

            # Progress — tqdm bar or ASCII fallback every 50 files
            if _use_tqdm:
                _iter.set_postfix_str(fname[:40], refresh=False)
            elif scan_count % 50 == 0:
                pct    = scan_count / max(n_targets, 1)
                filled = int(30 * pct)
                bar    = '#' * filled + '-' * (30 - filled)
                print(f'\r  [{bar}] {scan_count}/{n_targets}  {fname[:40]:<40}',
                      end='', flush=True)

            ext = fpath.suffix.lower()

            # Binary — index metadata only, no content
            if ext in BINARY_EXTENSIONS:
                n_binary += 1
                try:
                    stat       = fpath.stat()
                    size_bytes = stat.st_size
                    mtime      = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%d %b %Y')
                    size_label = (f"{size_bytes//1024}kb" if size_bytes >= 1024 else f"{size_bytes}b")
                except Exception:
                    size_label, mtime = 'unknown', 'unknown'
                unreadable.append((fpath, ext, size_label, mtime, 'binary format'))
                time.sleep(THROTTLE_DELAY)
                continue

            # Skip unknown extensions unless they look like text
            if ext not in TEXT_EXTENSIONS and ext != '':
                # Try to read anyway — some files have no or unusual extensions
                pass

            # Read content
            content = read_file(fpath)

            if content is None:
                n_binary += 1
                try:
                    mtime = datetime.datetime.fromtimestamp(fpath.stat().st_mtime).strftime('%d %b %Y')
                except Exception:
                    mtime = 'unknown'
                unreadable.append((fpath, ext, 'unknown', mtime, 'could not read'))
                time.sleep(THROTTLE_DELAY)
                continue

            # Readable — redact and write to store immediately
            safe_content = redact(content)
            n_readable  += 1

            store_file.write(f"{STORE_MARKER_START}\n")
            store_file.write(f"PATH: {fpath}\n")
            store_file.write(f"{STORE_MARKER_END_HEADER}\n")
            store_file.write(safe_content)
            store_file.write(f"\n{STORE_MARKER_END}\n")

            # Collect stats — no content held in RAM after this point
            lang = detect_language(fpath)
            if lang != 'Unknown':
                lang_counts[lang] = lang_counts.get(lang, 0) + 1

            try:
                mtime_dt = datetime.datetime.fromtimestamp(fpath.stat().st_mtime)
                mtime_str = mtime_dt.strftime('%d %b %Y')
                recent = mtime_dt > cutoff
            except Exception:
                mtime_str, recent = 'unknown', False

            signals = []
            todos   = len(re.findall(r'\b(TODO|FIXME|HACK|BUG)\b', content, re.IGNORECASE))
            has_keys = bool(re.search(r'(?:api[_-]?key|password|secret|token)', content, re.IGNORECASE))
            if todos:
                signals.append(f"{todos} TODO/FIXME")
            if has_keys:
                signals.append("credential patterns")
            if recent:
                signals.append("modified last 90 days")
            if signals:
                flagged.append((fpath, signals, mtime_str))

            # content goes out of scope here — RAM freed
            del content, safe_content

            time.sleep(THROTTLE_DELAY)

    if not _use_tqdm:
        print(f'\r  {scan_count} files scanned.{" " * 50}')
    return total, n_readable, n_binary, lang_counts, flagged, unreadable, list(folder_set)


# ── Mode 1: Full scan and index ───────────────────────────────────────────────
def mode_scan(output_dir, scan_root, plain_english=False):
    date_str   = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    scan_id    = hashlib.md5(f"{platform.node()}{date_str}".encode()).hexdigest()[:12].upper()
    scan_label = ', '.join(str(r) for r in scan_root) if isinstance(scan_root, list) else str(scan_root)
    now_str    = datetime.datetime.now().strftime('%d %B %Y %H:%M')

    total, n_readable, n_binary, lang_counts, flagged, unreadable, folders = \
        walk_and_index(scan_root, output_dir)

    print(f"\nTotal files found:  {total}")
    print(f"Readable as text:   {n_readable}")
    print(f"Binary/unreadable:  {n_binary}")

    # ── Summary file ─────────────────────────────────────────────────────────
    summary_lines = [
        "=" * 60,
        "SIFT v2 INDEX SUMMARY",
        "=" * 60,
        f"Scan ID:      {scan_id}",
        f"Date:         {now_str}",
        f"Machine:      {platform.node()}",
        f"OS:           {platform.system()} {platform.release()}",
        f"Scanned:      {scan_label}",
        f"Total files:  {total}",
        f"Readable:     {n_readable}",
        f"Unreadable:   {n_binary}",
        f"Folders:      {len(folders)}",
        "",
        "TECHNOLOGIES DETECTED:",
    ]
    for lang, count in sorted(lang_counts.items(), key=lambda x: -x[1]):
        summary_lines.append(f"  {lang}: {count} files")

    summary_lines += [
        "",
        "FOLDER STRUCTURE:",
    ]
    for folder in sorted(folders):
        summary_lines.append(f"  {folder}")

    summary_lines += [
        "",
        "=" * 60,
        f"FLAGGED FILES ({len(flagged)} files with signals)",
        "TODOs, credentials, or recent changes.",
        "=" * 60,
    ]
    for fpath, signals, mtime in flagged:
        summary_lines.append(f"\nFILE: {fpath}")
        summary_lines.append(f"SIGNALS: {', '.join(signals)}")
        summary_lines.append(f"MODIFIED: {mtime}")
        summary_lines.append("-" * 50)

    summary_lines += [
        "",
        "=" * 60,
        "UNREADABLE FILES (binary/unsupported)",
        "=" * 60,
    ]
    for fpath, ext, size_label, mtime, error in unreadable:
        summary_lines.append(f"  {fpath}  [{ext}]  {size_label}  {mtime}")

    summary_lines += [
        "",
        "NOTE: Full file content is in sift_content_store.txt",
        "SIFT Mode 2 uses this to retrieve specific files on demand.",
    ]

    # Apply builder mode substitutions
    if plain_english:
        active_prompt = (INDEX_PROMPT
            .replace("PROJECT TYPE:", "WHAT TYPE OF PROJECT IS THIS:")
            .replace("WHAT IT DOES:", "WHAT DOES IT DO IN PLAIN ENGLISH:")
            .replace("AGE AND ACTIVITY:", "HOW OLD IS IT AND IS IT STILL BEING WORKED ON:")
            .replace("WHAT IS BROKEN OR MISSING:", "WHAT LOOKS BROKEN, UNFINISHED OR MISSING:")
            .replace("FILES I NEED TO READ:", "FILES YOU NEED TO SEE TO FINISH YOUR ANSWER:")
            .replace("WHAT I AM GUESSING:", "WHAT ARE YOU UNSURE ABOUT:")
        ) + "\nIMPORTANT: Reply in plain English. No technical jargon.\n"
    else:
        active_prompt = INDEX_PROMPT

    summary_path = output_dir / 'SIFT_index_summary.txt'
    with open(summary_path, 'w', encoding='utf-8') as f:
        f.write(active_prompt)
        f.write('\n'.join(summary_lines))

    # ── Full index file — built from store, not from memory ──────────────────
    # Read back from store to build the full index — never held in RAM all at once
    full_path = output_dir / 'SIFT_index_full.txt'
    store_path = output_dir / STORE_FILENAME

    with open(full_path, 'w', encoding='utf-8') as out:
        out.write("=" * 60 + "\n")
        out.write("SIFT v2 FULL INDEX\n")
        out.write(f"Scan ID: {scan_id}  |  {now_str}\n")
        out.write("Every file. Nothing removed.\n")
        out.write("=" * 60 + "\n\n")

        # Stream through store, write one entry at a time — no memory spike
        if store_path.exists():
            current_path  = None
            in_content    = False
            content_lines = []

            with open(store_path, 'r', encoding='utf-8', errors='replace') as store:
                for line in store:
                    ls = line.rstrip('\n')
                    if ls == STORE_MARKER_START:
                        current_path, in_content, content_lines = None, False, []
                    elif ls.startswith("PATH: ") and not in_content:
                        current_path = ls[6:].strip()
                    elif ls == STORE_MARKER_END_HEADER:
                        in_content = True
                    elif ls == STORE_MARKER_END:
                        if current_path and in_content:
                            fpath   = Path(current_path)
                            content = '\n'.join(content_lines)
                            out.write(build_index_entry(fpath, True, content))
                            out.write('\n')
                        current_path, in_content, content_lines = None, False, []
                    elif in_content:
                        content_lines.append(ls)

        # Append unreadable files to full index
        for fpath, ext, size_label, mtime, error in unreadable:
            out.write(build_index_entry(fpath, False, error=error))
            out.write('\n')

    # ── Ensemble prompt ───────────────────────────────────────────────────────
    ensemble_path = output_dir / 'SIFT_ensemble_prompt.txt'
    with open(ensemble_path, 'w', encoding='utf-8') as f:
        f.write(ENSEMBLE_PROMPT)
        f.write("\n[PASTE MODEL REPLIES BELOW — LABEL EACH ONE]\n")
        f.write("\n--- CLAUDE ---\n[paste here]\n")
        f.write("\n--- GPT ---\n[paste here]\n")
        f.write("\n--- GEMINI ---\n[paste here]\n")
        f.write("\n--- GROQ ---\n[paste here]\n")

    print(f"\nSummary:   SIFT_index_summary.txt  ← start here")
    print(f"Full:      SIFT_index_full.txt     ← only if needed")
    print(f"Store:     {STORE_FILENAME}  ← used by Mode 2")
    print(f"Ensemble:  SIFT_ensemble_prompt.txt")

    generate_machine_context(scan_id, scan_root, total, n_readable, folders)

    # ── Connection mapping ────────────────────────────────────────────────────
    print("\nBuilding connection map...")
    scanned_file_list = []
    if store_path.exists():
        with open(store_path, 'r', encoding='utf-8', errors='replace') as _sf:
            for _line in _sf:
                if _line.startswith("PATH: "):
                    scanned_file_list.append(_line[6:].strip())

    connection_map = build_connection_map(scanned_file_list, store_path)
    conn_map_path = output_dir / 'SIFT_connection_map.json'
    with open(conn_map_path, 'w', encoding='utf-8') as _f:
        json.dump(connection_map, _f, indent=2)
    cluster_map    = detect_clusters(connection_map, output_dir)
    entry_points   = find_entry_points(cluster_map, connection_map)

    entry_path = output_dir / 'SIFT_entry_points.json'
    with open(entry_path, 'w', encoding='utf-8') as f:
        json.dump(entry_points, f, indent=2)

    print(f"Clusters:      SIFT_clusters.json     ({len(cluster_map)} clusters)")
    print(f"Entry points:  SIFT_entry_points.json  ({len(entry_points)} found)")

    return scan_id, output_dir, total, n_readable, len(cluster_map)


# ── Machine context generator ─────────────────────────────────────────────────
def generate_machine_context(scan_id, scan_root, total, n_readable, folders):
    import json as _json
    import socket as _socket
    import subprocess as _subprocess

    output_path = SCRIPT_DIR / 'MACHINE_CONTEXT.md'
    now = datetime.datetime.now()
    out = []

    # SECTION 1 — PYTHON ENVIRONMENT
    out.append("PYTHON ENVIRONMENT")
    out.append("Python version: " + sys.version.replace("\n", " "))
    out.append("")
    out.append("Installed packages:")
    try:
        proc = _subprocess.run(
            ['pip', 'list', '--format=json'],
            capture_output=True, text=True, timeout=30
        )
        if proc.returncode == 0:
            pkgs = _json.loads(proc.stdout)
            for p in sorted(pkgs, key=lambda x: x['name'].lower()):
                out.append(p['name'] + ": " + p['version'])
        else:
            out.append("pip list failed: " + proc.stderr.strip())
    except Exception as e:
        out.append("Could not retrieve package list: " + str(e))

    out.append("")

    # SECTION 2 — MACHINE
    out.append("MACHINE")
    out.append("Machine name: " + platform.node())
    out.append("OS: " + platform.system())
    out.append("OS version: " + platform.release())
    out.append("Generated: " + now.strftime('%d %B %Y %H:%M'))

    out.append("")

    # Compute top-level folder stats — used in sections 3 and 5
    scan_roots = scan_root if isinstance(scan_root, list) else [scan_root]
    cluster_data = []
    for root in scan_roots:
        root_path = Path(str(root))
        try:
            entries = sorted(root_path.iterdir(), key=lambda x: x.name.lower())
        except Exception:
            entries = []
        for item in entries:
            if not item.is_dir():
                continue
            if item.name in SYSTEM_DIRS or item.name.startswith('SIFT_output_'):
                continue
            file_count = 0
            ext_counts = {}
            last_mod = None
            try:
                for dp, dns, fns in os.walk(str(item)):
                    dns[:] = [
                        d for d in dns
                        if d not in SYSTEM_DIRS and not d.startswith('SIFT_output_')
                    ]
                    for fn in fns:
                        fp = Path(dp) / fn
                        file_count += 1
                        ext = fp.suffix.lower()
                        if ext:
                            ext_counts[ext] = ext_counts.get(ext, 0) + 1
                        try:
                            mt = fp.stat().st_mtime
                            if last_mod is None or mt > last_mod:
                                last_mod = mt
                        except Exception:
                            pass
            except Exception:
                pass
            primary_ext = max(ext_counts, key=ext_counts.get) if ext_counts else 'none'
            last_mod_str = (
                datetime.datetime.fromtimestamp(last_mod).strftime('%d %b %Y')
                if last_mod else 'unknown'
            )
            cluster_data.append({
                'name': item.name,
                'path': str(item),
                'file_count': file_count,
                'primary_ext': primary_ext,
                'last_modified': last_mod_str,
            })

    # SECTION 3 — ACTIVE PROJECTS
    out.append("ACTIVE PROJECTS")
    if cluster_data:
        for c in cluster_data:
            out.append("Folder: " + c['name'])
            out.append("Path: " + c['path'])
            out.append("Files: " + str(c['file_count']))
            out.append("Primary extension: " + c['primary_ext'])
            out.append("Last modified: " + c['last_modified'])
            out.append("")
    else:
        out.append("No top-level folders found in scan root")
        out.append("")

    # SECTION 4 — PORT CHECK
    out.append("PORT CHECK")
    PORTS_TO_CHECK = [8080, 8088, 3000, 5000, 8000, 8001, 6006, 11434]
    for port in PORTS_TO_CHECK:
        try:
            sock = _socket.socket(_socket.AF_INET, _socket.SOCK_STREAM)
            sock.settimeout(0.5)
            res = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            status = "IN USE" if res == 0 else "FREE"
        except Exception:
            status = "FREE"
        out.append("PORT " + str(port) + " — " + status)

    out.append("")

    # SECTION 5 — FOLDER MAP
    out.append("FOLDER MAP")
    for c in sorted(cluster_data, key=lambda x: -x['file_count']):
        out.append(c['name'] + " — " + str(c['file_count']))

    out.append("")

    # SECTION 6 — SIFT SCAN REFERENCE
    out.append("SIFT SCAN REFERENCE")
    out.append("Scan ID: " + scan_id)
    out.append("Date: " + now.strftime('%d %B %Y %H:%M'))
    out.append("Scanned: " + ', '.join(str(r) for r in scan_roots))
    out.append("Total files found: " + str(total))
    out.append("Readable files: " + str(n_readable))

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))
        f.write('\n')

    print(f"Machine context: MACHINE_CONTEXT.md")


# ── Connection mapping ────────────────────────────────────────────────────────
def build_connection_map(scanned_files, store_path):
    """
    Streams through the content store. For each readable file, searches
    its content for the filenames of all other scanned files (filename only,
    not full path). Records how many times each filename appears.
    Returns {filepath_str: {other_filepath_str: mention_count}}
    """
    store_path = Path(store_path)

    # filename (lowercase) -> full path string
    name_to_path = {}
    for fp in scanned_files:
        fname = Path(fp).name.lower()
        if fname not in name_to_path:
            name_to_path[fname] = fp

    name_set = set(name_to_path.keys())

    # Pre-compile a targeted regex for no-extension filenames (Dockerfile, Makefile, etc.)
    # Built once here — avoids re-compiling inside the per-file loop
    no_ext_names = [n for n in name_set if '.' not in n]
    no_ext_re = (
        re.compile(r'\b(' + '|'.join(re.escape(n) for n in no_ext_names) + r')\b')
        if no_ext_names else None
    )

    connection_map = {fp: {} for fp in scanned_files}

    if not store_path.exists():
        return connection_map

    current_path  = None
    in_content    = False
    content_lines = []

    with open(store_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            ls = line.rstrip('\n')

            if ls == STORE_MARKER_START:
                current_path, in_content, content_lines = None, False, []

            elif ls.startswith("PATH: ") and not in_content:
                current_path = ls[6:].strip()

            elif ls == STORE_MARKER_END_HEADER:
                in_content = True

            elif ls == STORE_MARKER_END:
                if current_path and in_content and current_path in connection_map:
                    content_lower = '\n'.join(content_lines).lower()
                    counts = {}

                    # One pass: find filename-like tokens — covers all files with extensions
                    for c in re.findall(r'[\w.-]+\.[a-zA-Z0-9]{1,10}', content_lower):
                        if c in name_set and name_to_path[c] != current_path:
                            counts[c] = counts.get(c, 0) + 1

                    # Second pass: targeted scan for no-extension filenames only
                    if no_ext_re:
                        for m in no_ext_re.finditer(content_lower):
                            fname = m.group(1)
                            if name_to_path[fname] != current_path:
                                counts[fname] = counts.get(fname, 0) + 1

                    for fname, count in counts.items():
                        connection_map[current_path][name_to_path[fname]] = count

                current_path, in_content, content_lines = None, False, []

            elif in_content:
                content_lines.append(ls)

    return connection_map


def detect_clusters(connection_map, output_dir):
    """
    Groups files with mutual connections into clusters.
    Mutual = file A references file B AND file B references file A.
    A cluster requires 2 or more mutually connected files.
    Files with no mutual connections are orphans.
    Writes SIFT_clusters.json to output_dir.
    Returns {cluster_id: [filepath, ...]}
    """
    parent = {}

    def find(x):
        if x not in parent:
            parent[x] = x
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for path_a, targets in connection_map.items():
        for path_b in targets:
            if path_b in connection_map and path_a in connection_map[path_b]:
                union(path_a, path_b)

    # Group paths by their union-find root
    groups = {}
    for path in connection_map:
        root = find(path) if path in parent else path
        groups.setdefault(root, []).append(path)

    cluster_map = {}
    orphans     = []
    cluster_idx = 0

    for root, members in groups.items():
        if len(members) >= 2:
            cid = f"cluster_{cluster_idx:03d}"
            cluster_map[cid] = members
            cluster_idx += 1
        else:
            orphans.extend(members)

    result = {
        "clusters":      cluster_map,
        "orphans":       orphans,
        "cluster_count": len(cluster_map),
        "orphan_count":  len(orphans),
    }

    out_path = Path(output_dir) / 'SIFT_clusters.json'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2)

    return cluster_map


def find_entry_points(cluster_map, connection_map):
    """
    Within each cluster, finds files that are referenced by other cluster
    members but do not reference back to any of them.
    Returns list of {"cluster_id": ..., "entry_point": ...}
    """
    # Reverse index: which source files point at each target file
    referenced_by = {}
    for source, targets in connection_map.items():
        for target in targets:
            referenced_by.setdefault(target, [])
            referenced_by[target].append(source)

    entry_points = []

    for cluster_id, members in cluster_map.items():
        member_set = set(members)
        for filepath in members:
            inbound  = set(referenced_by.get(filepath, [])) & member_set
            outbound = set(connection_map.get(filepath, {}).keys()) & member_set
            if inbound and not outbound:
                entry_points.append({
                    "cluster_id":  cluster_id,
                    "entry_point": filepath,
                })

    return entry_points


# ── Mode 2: Retrieve specific files ──────────────────────────────────────────
def mode_retrieve():
    """
    Find the most recent content store and retrieve specific files from it.
    Searches from SCRIPT_DIR — reliable regardless of where user runs from.
    """
    # Search from script directory — not cwd (fixes original bug)
    stores = sorted(SCRIPT_DIR.glob('SIFT_output_*/' + STORE_FILENAME))

    if not stores:
        print("No previous scan found.")
        print(f"Run Mode 1 first. Output goes to SIFT_output_[date] folder.")
        print(f"Searched in: {SCRIPT_DIR}")
        return

    # Show available scans if more than one
    if len(stores) > 1:
        print(f"Found {len(stores)} previous scans:")
        for i, s in enumerate(stores, 1):
            print(f"  {i}. {s.parent.name}")
        choice = input("Which scan? (Enter number, or press Enter for most recent): ").strip()
        try:
            idx = int(choice) - 1
            store_path = stores[idx]
        except (ValueError, IndexError):
            store_path = stores[-1]
    else:
        store_path = stores[0]

    print(f"\nUsing scan: {store_path.parent.name}")

    # Count available files without loading content
    file_count = 0
    with open(store_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith("PATH: "):
                file_count += 1
    print(f"Files available: {file_count}")
    print()
    print("Paste the file paths the LLM requested.")
    print("One path per line. Press Enter twice when done.")
    print()

    lines = []
    while True:
        try:
            line = input()
        except EOFError:
            break
        if line == '':
            if lines:
                break
        else:
            lines.append(line.strip())

    # Clean paths — strip bullet points, dashes, numbers
    requested = [
        re.sub(r'^[\s\-\*\d\.\)]+', '', l).strip()
        for l in lines if re.sub(r'^[\s\-\*\d\.\)]+', '', l).strip()
    ]

    if not requested:
        print("No paths entered.")
        return

    print(f"\nLooking for {len(requested)} files...")
    found, not_found = read_from_store(store_path, requested)

    print(f"Found: {len(found)} | Not found: {len(not_found)}")
    if not_found:
        print("\nCould not find:")
        for nf in not_found:
            print(f"  {nf}")

    if not found:
        print("No files retrieved. Check paths match exactly what the LLM listed.")
        return

    date_str      = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    retrieve_path = SCRIPT_DIR / f"SIFT_retrieved_{date_str}.txt"

    with open(retrieve_path, 'w', encoding='utf-8') as f:
        f.write(CONTENT_PROMPT)
        f.write(f"Files retrieved: {len(found)}\n\n")
        for fpath, content in found.items():
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
    print(f"  SIFT v{VERSION} - Find the truth in any codebase")
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
        retrieve_path = mode_retrieve()
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

    # Mode 1 — get user type
    print()
    print("Who is running SIFT today?")
    print()
    print("  1 -- I am a builder or tinkerer")
    print("       Plain English output. No technical terms.")
    print()
    print("  2 -- I am a developer")
    print("       Full technical detail included.")
    print()
    user_type     = input("Enter 1 or 2: ").strip()
    plain_english = (user_type == "1")

    print()
    print("What do you want to scan?")
    print()
    print("  1 -- My whole machine")
    print("       Finds everything. Takes longer.")
    print("       Best for: I have no idea what I have.")
    print()
    print("  2 -- One specific folder")
    print("       Faster. Focused.")
    print("       Best for: I know roughly where things are.")
    print()
    scan_choice = input("Enter 1 or 2: ").strip()

    if scan_choice == '1':
        if platform.system() == 'Windows':
            import string
            drives    = [f"{d}:\\" for d in string.ascii_uppercase if os.path.exists(f"{d}:\\")]
            scan_root = drives
            print(f"\nDrives found: {', '.join(drives)}")
        else:
            scan_root = ['/']
        print("Scanning whole machine. May take several minutes on large drives.")
    else:
        # Try tkinter folder picker popup; fall back to text input if unavailable
        path_input = None
        try:
            import tkinter as tk
            from tkinter import filedialog
            _root = tk.Tk()
            _root.withdraw()
            _root.attributes('-topmost', True)
            path_input = filedialog.askdirectory(title='Choose a folder to scan')
            _root.destroy()
        except Exception:
            pass
        if not path_input:
            # Fallback: tkinter unavailable or user cancelled the dialog
            path_input = input("\nFolder to scan (type the path): ").strip()
        if not path_input or not os.path.exists(path_input):
            print(f"Path not found: {path_input}")
            sys.exit(1)
        print(f"\nFolder selected: {path_input}")
        scan_root = [path_input]

    # Final confirmation
    print()
    print("=" * 50)
    print("READY TO SCAN")
    print("=" * 50)
    print(f"Scanning:  {', '.join(str(r) for r in scan_root)}")
    print(f"Output:    {'Plain English' if plain_english else 'Technical'}")
    print()
    print("This script reads all text files in the scanned location.")
    print("Sensitive data is redacted before anything is written.")
    print("Nothing on the laptop will be changed or deleted.")
    print()
    if input("Start scan? (Y/N): ").strip().upper() != 'Y':
        print("Scan cancelled.")
        sys.exit(0)

    date_str   = datetime.datetime.now().strftime('%Y_%m_%d_%H%M')
    output_dir = SCRIPT_DIR / f"SIFT_output_{date_str}"
    output_dir.mkdir(exist_ok=True)
    print(f"\nOutput folder: {output_dir}\n")

    scan_id, output_dir, total_files, readable_files, cluster_count = \
        mode_scan(output_dir, scan_root, plain_english)

    # Zip output — uses pyzipper for real AES encryption if available
    print()
    zip_password = input("Password to protect output zip (or Enter to skip): ").strip()
    zip_path = SCRIPT_DIR / f"SIFT_output_{date_str}.zip"

    try:
        import pyzipper
        with pyzipper.AESZipFile(zip_path, 'w',
                                  compression=pyzipper.ZIP_DEFLATED,
                                  encryption=pyzipper.WZ_AES if zip_password else None) as zf:
            if zip_password:
                zf.setpassword(zip_password.encode())
            for f in output_dir.iterdir():
                if f.name != STORE_FILENAME:
                    zf.write(f, f.name)
        if zip_password:
            print(f"Encrypted zip saved: {zip_path.name}")
            print("IMPORTANT: SIFT does not store your password. Do not lose it.")
        else:
            print(f"Zip saved (no password): {zip_path.name}")
    except ImportError:
        # pyzipper not installed — use standard zip (no encryption)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            for f in output_dir.iterdir():
                if f.name != STORE_FILENAME:
                    zf.write(f, f.name)
        if zip_password:
            print("Note: pyzipper not installed — zip saved WITHOUT encryption.")
            print("Run: pip install pyzipper — then re-run SIFT to get encrypted output.")
        else:
            print(f"Zip saved: {zip_path.name}")

    print()
    print("=" * 60)
    print("SIFT SCAN COMPLETE")
    print("=" * 60)
    print(f"Files found:    {total_files}")
    print(f"Files scanned:  {readable_files}")
    print(f"Projects found: {cluster_count}")
    print("=" * 60)
    print()
    print("Your report is opening in your browser now.")
    print()
    print("If the browser did not open automatically:")
    print("  sift_report.py will show you the URL when it starts.")
    print()
    print("=" * 60)


if __name__ == '__main__':
    main()
