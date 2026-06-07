# PORT: none
# DEPENDS-ON: SIFT_clusters.json, SIFT_connection_map.json (in SIFT_output_* folder)
# TRIGGERS: nothing
# OUTPUTS-TO: SIFT_descriptions.json (same output folder)

import os, sys, re, json, hashlib, collections, time
from pathlib import Path

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

THROTTLE_DELAY = 0.05

LANG_MAP = {
    '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
    '.jsx': 'React/JSX', '.tsx': 'React/TSX', '.html': 'HTML',
    '.css': 'CSS', '.scss': 'SCSS', '.json': 'JSON', '.sql': 'SQL',
    '.rb': 'Ruby', '.php': 'PHP', '.java': 'Java', '.cs': 'C#',
    '.go': 'Go', '.rs': 'Rust', '.sh': 'Shell', '.bat': 'Batch',
    '.md': 'Markdown', '.yaml': 'YAML', '.yml': 'YAML',
    '.toml': 'TOML', '.xml': 'XML', '.csv': 'CSV',
}

LICENSE_PAT = re.compile(
    r'(MIT|Apache|GPL|BSD|Copyright|Permission is hereby granted)',
    re.IGNORECASE,
)

# import base-name -> plain English purpose label
IMPORT_LABEL_MAP = {
    'flask': 'serves web pages or an API',
    'fastapi': 'serves web pages or an API',
    'django': 'serves web pages or an API',
    'smtplib': 'sends emails',
    'sendgrid': 'sends emails',
    'mailgun': 'sends emails',
    'yagmail': 'sends emails',
    'twilio': 'makes phone calls or sends text messages',
    'telegram': 'sends or receives Telegram messages',
    'telebot': 'sends or receives Telegram messages',
    'selenium': 'reads websites automatically',
    'playwright': 'reads websites automatically',
    'beautifulsoup': 'reads websites automatically',
    'bs4': 'reads websites automatically',
    'scrapy': 'reads websites automatically',
    'pandas': 'processes or analyses data',
    'numpy': 'processes or analyses data',
    'polars': 'processes or analyses data',
    'scipy': 'processes or analyses data',
    'openpyxl': 'reads or writes spreadsheets',
    'xlrd': 'reads or writes spreadsheets',
    'xlwt': 'reads or writes spreadsheets',
    'xlsxwriter': 'reads or writes spreadsheets',
    'sqlite3': 'stores or retrieves data',
    'sqlalchemy': 'stores or retrieves data',
    'pymongo': 'stores or retrieves data',
    'psycopg2': 'stores or retrieves data',
    'anthropic': 'uses an AI to generate text',
    'openai': 'uses an AI to generate text',
    'groq': 'uses an AI to generate text',
    'cohere': 'uses an AI to generate text',
    'replicate': 'uses an AI to generate text',
    'stripe': 'handles payments',
    'paypalrestsdk': 'handles payments',
    'braintree': 'handles payments',
    'schedule': 'runs tasks automatically on a timer',
    'apscheduler': 'runs tasks automatically on a timer',
    'celery': 'runs tasks automatically on a timer',
    'rq': 'runs tasks automatically on a timer',
    'faster_whisper': 'converts speech to text',
    'whisper': 'converts speech to text',
    'speech_recognition': 'converts speech to text',
    'pytest': 'tests other code',
    'unittest': 'tests other code',
    'nose': 'tests other code',
    'click': 'runs from the command line',
    'argparse': 'runs from the command line',
    'typer': 'runs from the command line',
    'requests': 'gets data from the internet',
    'httpx': 'gets data from the internet',
    'aiohttp': 'gets data from the internet',
    'urllib': 'gets data from the internet',
    'pillow': 'works with images',
    'PIL': 'works with images',
    'cv2': 'works with images',
    'skimage': 'works with images',
    'pydub': 'works with audio',
    'librosa': 'works with audio',
    'sounddevice': 'works with audio',
}

# Higher = more specific; used to break frequency ties
LABEL_SPECIFICITY = {
    'makes phone calls or sends text messages': 6,
    'sends or receives Telegram messages': 6,
    'uses an AI to generate text': 5,
    'serves web pages or an API': 4,
    'reads websites automatically': 4,
    'processes or analyses data': 3,
    'stores or retrieves data': 3,
    'sends emails': 3,
    'handles payments': 3,
    'runs tasks automatically on a timer': 3,
    'converts speech to text': 3,
    'reads or writes spreadsheets': 2,
    'works with images': 2,
    'works with audio': 2,
    'tests other code': 1,
    'runs from the command line': 1,
    'gets data from the internet': 1,
}

VERB_PREFIXES = {
    'send', 'get', 'fetch', 'load', 'create', 'build', 'make', 'run', 'call',
    'process', 'transform', 'parse', 'generate', 'render', 'display', 'show',
    'track', 'log', 'save', 'calculate', 'compute', 'estimate', 'delete',
    'remove', 'find', 'check', 'validate', 'update', 'set',
}

STOPWORDS = {
    'data', 'file', 'info', 'item', 'list', 'text', 'value', 'result', 'output',
    'input', 'config', 'util', 'helper', 'main', 'base', 'core', 'test', 'type',
    'name', 'time', 'date', 'path',
}

SENSITIVE_SUBSTRINGS = {
    'password', 'token', 'secret', 'key', 'credential', 'decrypt', 'encrypt',
    'auth', 'hash', 'sign', 'salt', 'private', 'cert',
}

_PATH_PAT = re.compile(r'[/\\][a-zA-Z0-9]')


# ── Component 1: signal extraction ───────────────────────────────────────────

def extract_signals(filepath):
    """
    Read first 20 + last 20 lines of a file and extract structural signals.
    Returns dict with keys: imports, function_names, class_names, comments,
    docstring, heading, title_tag, entry_point, language, export_type.
    """
    filepath = Path(filepath)
    language = LANG_MAP.get(filepath.suffix.lower(), 'Unknown')

    signals = {
        'imports': [],
        'function_names': [],
        'class_names': [],
        'comments': [],
        'docstring': None,
        'heading': None,
        'title_tag': None,
        'entry_point': 'no',
        'language': language,
        'export_type': 'none',
    }

    try:
        file_size = os.path.getsize(filepath)
        with open(filepath, 'r', encoding='utf-8', errors='replace') as fh:
            all_lines = fh.readlines()
    except Exception as exc:
        print(f'  [signals] Could not open {filepath}: {exc}', file=sys.stderr)
        return signals

    # Minified: any single line > 5000 chars → language only, no extraction
    for line in all_lines:
        if len(line) > 5000:
            return signals

    # Tiered reading: full / first+last 100 / first+last 20 based on file size
    if file_size < 51200:
        combined = all_lines
        top_lines = all_lines
    elif file_size < 512000:
        top_lines = all_lines[:100]
        combined = top_lines + (all_lines[-100:] if len(all_lines) > 100 else [])
    else:
        first_20 = all_lines[:20]
        license_hits = sum(1 for ln in first_20 if LICENSE_PAT.search(ln))
        top_lines = all_lines[:40] if license_hits > 10 else first_20
        last_20 = all_lines[-20:] if len(all_lines) > 20 else all_lines
        combined = top_lines + last_20
    combined_text = ''.join(combined)

    seen_imports = set()

    for line in combined:
        s = line.strip()

        # Python: import X  /  from X import Y
        m = re.match(r'^(?:import|from)\s+([\w\.]+)', s)
        if m:
            base = m.group(1).split('.')[0]
            if base and base not in seen_imports:
                signals['imports'].append(base)
                seen_imports.add(base)

        # JS: require('mod')
        m = re.match(r"^(?:const|var|let)\s+\w+\s*=\s*require\(['\"]([^'\"]+)['\"]\)", s)
        if m:
            raw = m.group(1)
            base = raw.lstrip('@').split('/')[0] if not raw.startswith('@') else '/'.join(raw.split('/')[:2])
            if base and base not in seen_imports:
                signals['imports'].append(base)
                seen_imports.add(base)

        # JS/TS: import ... from 'mod'
        m = re.match(r"^import\b.*\bfrom\s+['\"]([^'\"]+)['\"]", s)
        if m:
            raw = m.group(1)
            base = raw.lstrip('@').split('/')[0] if not raw.startswith('@') else '/'.join(raw.split('/')[:2])
            if base and base not in seen_imports:
                signals['imports'].append(base)
                seen_imports.add(base)

        # Python function definitions
        m = re.match(r'^(?:async\s+)?def\s+([a-zA-Z_]\w*)\s*\(', s)
        if m:
            signals['function_names'].append(m.group(1))

        # Python class definitions
        m = re.match(r'^class\s+([a-zA-Z_]\w*)\s*[\(:]', s)
        if m:
            signals['class_names'].append(m.group(1))

        # JS/TS function keyword
        m = re.match(r'^(?:export\s+)?(?:async\s+)?function\s+([a-zA-Z_]\w*)\s*\(', s)
        if m:
            signals['function_names'].append(m.group(1))

        # JS/TS arrow / assigned function
        m = re.match(r'^(?:export\s+)?(?:const|let|var)\s+([a-zA-Z_]\w*)\s*=\s*(?:async\s+)?\(?', s)
        if m and '=>' in line:
            signals['function_names'].append(m.group(1))

        # Comments
        if s.startswith('#') or s.startswith('//') or s.startswith('--'):
            signals['comments'].append(s)

    # Docstring: first triple-quoted string near top
    doc_m = re.search(r'^("""|\'\'\')([\s\S]*?)\1', combined_text, re.MULTILINE)
    if doc_m:
        signals['docstring'] = doc_m.group(2).strip()[:200]

    # Markdown heading on line 1 or 2
    for ln in top_lines[:2]:
        if ln.startswith('#'):
            signals['heading'] = ln.strip().lstrip('#').strip()[:100]
            break

    # HTML <title> tag
    title_m = re.search(r'<title>([^<]+)</title>', combined_text, re.IGNORECASE)
    if title_m:
        signals['title_tag'] = title_m.group(1).strip()[:100]

    # YAML frontmatter keys
    if all_lines and all_lines[0].strip() == '---':
        fm_keys = []
        for ln in all_lines[1:20]:
            if ln.strip() == '---':
                break
            if ':' in ln:
                fm_keys.append(ln.split(':')[0].strip())
        if fm_keys:
            signals['frontmatter_keys'] = fm_keys

    # if __name__ == '__main__':
    if re.search(r"if\s+__name__\s*==\s*['\"]__main__['\"]", combined_text):
        signals['entry_point'] = 'yes'

    # module.exports / export default
    if 'module.exports' in combined_text or re.search(r'\bexports\.', combined_text):
        signals['export_type'] = 'module.exports'
    elif re.search(r'\bexport\s+default\b', combined_text):
        signals['export_type'] = 'export default'

    # Flask/FastAPI app.run()
    app_m = re.search(r'app\.run\(([^)]*)\)', combined_text)
    if app_m:
        port_m = re.search(r'port\s*=\s*(\d+)', app_m.group(1))
        signals['app_run_port'] = port_m.group(1) if port_m else 'yes'

    return signals


# ── Component 2: signal → purpose labels & domain nouns ──────────────────────

def signals_to_purpose_labels(signals_dict):
    """
    Map import names to plain English purpose labels.
    Deduplicates. Returns top 5 sorted by (specificity DESC, frequency DESC).
    """
    label_counts = collections.Counter()
    for imp in signals_dict.get('imports', []):
        label = IMPORT_LABEL_MAP.get(imp) or IMPORT_LABEL_MAP.get(imp.lower())
        if label:
            label_counts[label] += 1

    # Sort: highest specificity first, then highest frequency
    labels = sorted(
        label_counts.keys(),
        key=lambda lb: (LABEL_SPECIFICITY.get(lb, 0), label_counts[lb]),
        reverse=True,
    )
    return labels[:5]


def _split_name(name):
    """Split function/class name on underscores and camelCase boundaries."""
    parts = []
    for segment in name.split('_'):
        if not segment:
            continue
        camel = re.findall(r'[A-Z][a-z]*|[a-z]+|[A-Z]+(?=[A-Z]|$)', segment)
        if camel:
            parts.extend(camel)
        else:
            parts.append(segment)
    return [p.lower() for p in parts if p]


def extract_domain_nouns(signals_dict):
    """
    Extract domain nouns from function and class names.
    Strips verb prefixes, stopwords, and sensitive substrings.
    Returns top 10 most frequent nouns.
    """
    noun_counts = collections.Counter()
    all_names = (
        signals_dict.get('function_names', [])
        + signals_dict.get('class_names', [])
    )

    for name in all_names:
        parts = _split_name(name)

        # Strip leading verb prefixes
        while parts and parts[0] in VERB_PREFIXES:
            parts = parts[1:]

        for part in parts:
            if len(part) < 3:
                continue
            if part in STOPWORDS:
                continue
            if any(s in part for s in SENSITIVE_SUBSTRINGS):
                continue
            noun_counts[part] += 1

    return [noun for noun, _ in noun_counts.most_common(10)]


# ── Component 3: sub-project detection ───────────────────────────────────────

def detect_sub_projects(cluster_files, connection_map):
    """
    Detect connected sub-projects within a cluster using mutual-edge
    union-find.  Files referenced by 2+ sub-projects = shared utilities.
    Returns dict: {sub_projects, standalone, shared_utilities}.
    """
    cluster_set = set(str(f) for f in cluster_files)

    # Filter connection_map: keep only edges where both endpoints are in cluster
    filtered = {}
    for src, targets in connection_map.items():
        if str(src) not in cluster_set:
            continue
        for tgt, count in targets.items():
            if str(tgt) in cluster_set and str(src) != str(tgt):
                filtered.setdefault(str(src), {})[str(tgt)] = count

    # Union-find on MUTUAL edges only (A→B and B→A)
    parent = {str(f): str(f) for f in cluster_files}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        px, py = find(x), find(y)
        if px != py:
            parent[px] = py

    for src, targets in filtered.items():
        for tgt in targets:
            if tgt in filtered and src in filtered.get(tgt, {}):
                union(src, tgt)

    # Group by root
    groups = collections.defaultdict(list)
    for fp in (str(f) for f in cluster_files):
        groups[find(fp)].append(fp)

    sub_projects = [members for members in groups.values() if len(members) >= 2]
    isolates = [members[0] for members in groups.values() if len(members) == 1]

    # Build map: filepath -> sub_project index
    comp_map = {}
    for i, sp in enumerate(sub_projects):
        for fp in sp:
            comp_map[fp] = i

    # Classify isolates: shared_utility if referenced by 2+ distinct sub-projects
    shared_utilities = []
    standalone = []
    for fp in isolates:
        referencing = set()
        for src, targets in filtered.items():
            if fp in targets and src in comp_map:
                referencing.add(comp_map[src])
        if len(referencing) >= 2:
            shared_utilities.append(fp)
        else:
            standalone.append(fp)

    return {
        'sub_projects': sub_projects,
        'standalone': standalone,
        'shared_utilities': shared_utilities,
    }


def label_sub_project(file_list, all_signals):
    """
    Return top 3 domain nouns from a sub-project's files joined as a label.
    """
    noun_counts = collections.Counter()
    for fp in file_list:
        sigs = all_signals.get(str(fp), {})
        for noun in extract_domain_nouns(sigs):
            noun_counts[noun] += 1

    top = [noun for noun, _ in noun_counts.most_common(3)]
    return ' '.join(top) if top else 'unknown purpose'


# ── Component 4: evidence package assembly ───────────────────────────────────

def _compute_content_hash(cluster_files):
    sorted_fps = sorted(str(f) for f in cluster_files)
    mtimes = [
        str(os.path.getmtime(f))
        for f in sorted_fps
        if os.path.exists(f)
    ]
    raw = '|'.join(sorted_fps) + '|' + '|'.join(mtimes)
    return hashlib.md5(raw.encode('utf-8')).hexdigest()


def _sanitise_readme(folder):
    """Read first 300 chars of README, strip paths/code/markdown. Return prose or 'none'."""
    for name in ('README.md', 'README.txt', 'readme.md', 'readme.txt'):
        path = Path(folder) / name
        if not path.exists():
            continue
        try:
            raw = path.read_text(encoding='utf-8', errors='replace')[:300]
            clean = []
            for line in raw.split('\n'):
                stripped = line.strip()
                if not stripped:
                    continue
                if _PATH_PAT.search(stripped):
                    continue
                if stripped.startswith('$'):
                    continue
                if re.match(r'^#+\s*[a-zA-Z_]\w*\s*[\(\{=]', stripped):
                    continue
                if '`' in stripped:
                    continue
                clean.append(stripped)
            result = ' '.join(clean)[:200]
            if result:
                return result
        except Exception:
            pass
    return 'none'


def build_evidence_package(cluster, all_signals, sub_project_result, output_dir):
    """
    Assemble a plain key-value evidence package string for one cluster.
    Total length capped at 2400 chars; truncates sub_project lines first,
    then readme_summary, then domain_vocabulary.
    """
    # Collect languages
    langs = set()
    for fp in cluster.get('files', []):
        lang = LANG_MAP.get(Path(str(fp)).suffix.lower(), 'Unknown')
        if lang != 'Unknown':
            langs.add(lang)
    languages_str = ', '.join(sorted(langs)) if langs else 'none'

    # Purpose signals: aggregate across all files
    all_labels = []
    for fp in cluster.get('files', []):
        sigs = all_signals.get(str(fp), {})
        all_labels.extend(signals_to_purpose_labels(sigs))
    label_counts = collections.Counter(all_labels)
    top_labels = sorted(
        label_counts.keys(),
        key=lambda lb: (LABEL_SPECIFICITY.get(lb, 0), label_counts[lb]),
        reverse=True,
    )[:5]
    purpose_str = ', '.join(top_labels) if top_labels else 'none'

    # Domain vocabulary: aggregate across all files
    all_nouns = []
    for fp in cluster.get('files', []):
        sigs = all_signals.get(str(fp), {})
        all_nouns.extend(extract_domain_nouns(sigs))
    noun_counts = collections.Counter(all_nouns)
    top_nouns = [n for n, _ in noun_counts.most_common(10)]
    vocab_str = ', '.join(top_nouns) if top_nouns else 'none'

    # README summary
    readme_str = _sanitise_readme(cluster.get('folder', ''))

    # Incomplete signals from comments
    incomplete_snippets = []
    for fp in cluster.get('files', []):
        sigs = all_signals.get(str(fp), {})
        for comment in sigs.get('comments', []):
            if re.search(r'\b(TODO|FIXME|BROKEN)\b', comment, re.IGNORECASE):
                snippet = comment[:50].strip()
                if not _PATH_PAT.search(snippet) and snippet not in incomplete_snippets:
                    incomplete_snippets.append(snippet)
            if len(incomplete_snippets) >= 3:
                break
        if len(incomplete_snippets) >= 3:
            break
    incomplete_str = ', '.join(incomplete_snippets) if incomplete_snippets else 'none'

    # Connection classification
    n_sp = len(sub_project_result.get('sub_projects', []))
    has_shared = len(sub_project_result.get('shared_utilities', [])) > 0
    if n_sp == 0:
        connection_str = 'single project'
    elif n_sp == 1:
        connection_str = 'all parts work together'
    elif has_shared:
        connection_str = 'mixed'
    else:
        connection_str = 'parts are separate tools in the same folder'

    # Content hash
    content_hash = _compute_content_hash(cluster.get('files', []))

    # Sub-project lines (may be truncated later)
    sp_lines = []
    for sp_files in sub_project_result.get('sub_projects', []):
        sp_label = label_sub_project(sp_files, all_signals)
        sp_purpose_labels = []
        for fp in sp_files:
            sigs = all_signals.get(str(fp), {})
            sp_purpose_labels.extend(signals_to_purpose_labels(sigs))
        seen = set()
        unique_sp = []
        for lb in sp_purpose_labels:
            if lb not in seen:
                seen.add(lb)
                unique_sp.append(lb)
        sp_purpose_str = ', '.join(unique_sp[:3]) or 'unknown purpose'
        sp_lines.append(f'- {sp_label}: {len(sp_files)} files, {sp_purpose_str}')

    # Assemble package
    def _build(sp_lines_in, readme_in, vocab_in):
        lines = [
            f'cluster_name: {cluster.get("name", "unknown")}',
            f'file_count: {cluster.get("file_count", 0)}',
            f'languages: {languages_str}',
            f'purpose_signals: {purpose_str}',
            f'domain_vocabulary: {vocab_in}',
            f'readme_summary: {readme_in}',
            f'sub_projects: {n_sp}',
        ]
        lines.extend(sp_lines_in)
        lines += [
            f'connection: {connection_str}',
            f'last_touched: {cluster.get("last_touched", "unknown")}',
            f'incomplete: {incomplete_str}',
            f'content_hash: {content_hash}',
        ]
        return '\n'.join(lines)

    pkg = _build(sp_lines, readme_str, vocab_str)

    if len(pkg) <= 2400:
        return pkg

    # Truncate: sub_project lines first
    truncated_sp = list(sp_lines)
    while len(truncated_sp) > 0 and len(_build(truncated_sp, readme_str, vocab_str)) > 2400:
        truncated_sp.pop()
    pkg = _build(truncated_sp, readme_str, vocab_str)
    if len(pkg) <= 2400:
        return pkg

    # Truncate readme_summary
    short_readme = readme_str[:100] if readme_str != 'none' else 'none'
    pkg = _build(truncated_sp, short_readme, vocab_str)
    if len(pkg) <= 2400:
        return pkg

    # Truncate domain_vocabulary
    nouns = top_nouns[:5]
    short_vocab = ', '.join(nouns) if nouns else 'none'
    return _build(truncated_sp, short_readme, short_vocab)


def assemble_all_packages(clusters, output_dir):
    """
    For each cluster: extract signals, detect sub-projects, build evidence package.
    Writes SIFT_descriptions.json to output_dir.
    Prints one line per cluster.
    """
    output_dir = Path(output_dir)

    # Load connection map (required for sub-project detection)
    conn_map_path = output_dir / 'SIFT_connection_map.json'
    connection_map = {}
    if conn_map_path.exists():
        try:
            with open(conn_map_path, encoding='utf-8') as fh:
                connection_map = json.load(fh)
        except Exception as exc:
            print(f'  [descriptions] Could not load connection map: {exc}', file=sys.stderr)

    descriptions = {}

    for cluster in clusters:
        cid = cluster.get('id', '')
        name = cluster.get('name', 'Unknown')
        try:
            all_signals = {}
            for fp in cluster.get('files', []):
                all_signals[str(fp)] = extract_signals(str(fp))

            sub_result = detect_sub_projects(cluster.get('files', []), connection_map)
            pkg = build_evidence_package(cluster, all_signals, sub_result, output_dir)
            ch = _compute_content_hash(cluster.get('files', []))

            descriptions[cid] = {
                'evidence_package': pkg,
                'description': None,
                'tier': None,
                'content_hash': ch,
            }
            print(f'  {name} -- done')
        except Exception as exc:
            print(f'  {name} -- ERROR: {exc}')
        time.sleep(THROTTLE_DELAY)

    desc_path = output_dir / 'SIFT_descriptions.json'
    tmp_path = desc_path.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as fh:
        json.dump(descriptions, fh, indent=2)
    tmp_path.replace(desc_path)

    return descriptions


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    candidates = sorted(
        d for d in SCRIPT_DIR.glob('SIFT_output_*')
        if (d / 'SIFT_clusters.json').exists()
    )
    if not candidates:
        print('No SIFT output folder found. Run sift.py first.')
        sys.exit(1)

    output_dir = candidates[-1]
    clusters_path = output_dir / 'SIFT_clusters.json'

    with open(clusters_path, encoding='utf-8') as fh:
        clusters_data = json.load(fh)

    clusters = clusters_data.get('clusters', [])
    if not clusters:
        print('No clusters found in SIFT_clusters.json.')
        sys.exit(0)

    print(f'Building descriptions for {len(clusters)} clusters...')
    assemble_all_packages(clusters, output_dir)
    print(f'\nDescriptions saved to {output_dir / "SIFT_descriptions.json"}')


if __name__ == '__main__':
    main()
