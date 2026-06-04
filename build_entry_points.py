import os, sys, json, re, datetime, hashlib
from pathlib import Path

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

# Known entry point filenames — ordered by precedence
ENTRY_POINT_NAMES = [
    'main.py', 'app.py', 'server.py', 'run.py', 'index.py', 'start.py',
    'index.html', 'index.htm',
]

# .bat files are the tinkerer's entry point (per SIFT questions doc)
BAT_EXTENSION = '.bat'

# Regex to find local import targets from IMPORTS: line in index_full
# Matches bare names like "utils", "config", "helpers" (not dotted package paths)
LOCAL_IMPORT_RE = re.compile(r'\b([a-zA-Z_][a-zA-Z0-9_]*)\b')

# Status definitions (from build plan)
STATUS_CAN_RUN   = 'CAN RUN NOW'
STATUS_NEARLY    = 'NEARLY THERE'
STATUS_BROKEN    = 'BROKEN'
STATUS_UNKNOWN   = 'UNKNOWN'

MISSING_NEARLY   = 2   # 1–2 missing imports = NEARLY THERE
# 3+ missing imports = BROKEN


def parse_imports_from_index(index_full_path, file_paths_set):
    """
    Parse SIFT_index_full.txt.
    For each file in file_paths_set, collect its IMPORTS line.
    Returns dict: file_path -> imports_string
    """
    result = {}
    current_path = None
    with open(index_full_path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if line.startswith('FILE: '):
                current_path = line[6:].strip()
            elif line.startswith('IMPORTS: ') and current_path in file_paths_set:
                result[current_path] = line[9:].strip()
            elif line == '-' * 50:
                current_path = None
    return result


def find_entry_point(cluster_files):
    """
    Return the best entry point path from a list of file path strings.
    Priority: known names first, then any .bat file, then None.
    """
    lower_map = {Path(p).name.lower(): p for p in cluster_files}

    for name in ENTRY_POINT_NAMES:
        if name in lower_map:
            return lower_map[name]

    for p in cluster_files:
        if Path(p).suffix.lower() == BAT_EXTENSION:
            return p

    return None


def count_missing_local_imports(entry_path, imports_str, cluster_files_set):
    """
    From the imports string, extract bare module names.
    Check how many do NOT exist as .py files in cluster_files_set.
    Returns count of missing local imports.
    Ignores stdlib and third-party names (cannot distinguish — counts only
    names that look like local modules: no dots, short names).
    """
    if not imports_str:
        return 0

    # Strip commas/dots before checking — raw token may be 'utils,' from CSV format
    candidates = []
    for tok in imports_str.split():
        clean = tok.strip().rstrip(',').rstrip('.')
        if clean and '.' not in clean and clean.isidentifier():
            candidates.append(clean)

    cluster_stems = {Path(p).stem.lower() for p in cluster_files_set}
    missing = 0
    for name in candidates:
        if name.lower() not in cluster_stems:
            missing += 1
    return missing


def determine_status(entry_point, missing_count):
    """Apply status rules from the build plan."""
    if entry_point is None:
        return STATUS_UNKNOWN, 'No entry point file found in cluster.'
    if missing_count == 0:
        return STATUS_CAN_RUN, f'Has {Path(entry_point).name}. No missing local imports detected.'
    if missing_count <= MISSING_NEARLY:
        return STATUS_NEARLY, f'Has {Path(entry_point).name}. {missing_count} local import(s) not found in cluster.'
    return STATUS_BROKEN, f'Has {Path(entry_point).name}. {missing_count} local import(s) missing — likely broken.'


def build_entry_points(output_dir):
    """
    Read SIFT_clusters.json and SIFT_index_full.txt from output_dir.
    Detect entry points and status for each cluster.
    Write SIFT_entry_points.json to output_dir.
    Return result dict.
    """
    output_dir     = Path(output_dir)
    clusters_path  = output_dir / 'SIFT_clusters.json'
    index_full     = output_dir / 'SIFT_index_full.txt'

    if not clusters_path.exists():
        print(f'ERROR: {clusters_path} not found. Run build_clusters.py first.')
        sys.exit(1)
    if not index_full.exists():
        print(f'ERROR: {index_full} not found.')
        sys.exit(1)

    with open(clusters_path, 'r', encoding='utf-8') as f:
        clusters_data = json.load(f)

    clusters = clusters_data.get('clusters', [])
    print(f'Processing {len(clusters)} clusters...')

    # Collect all file paths that are entry point candidates across all clusters
    all_entry_candidates = set()
    for c in clusters:
        ep = find_entry_point(c['files'])
        if ep:
            all_entry_candidates.add(ep)

    imports_map = parse_imports_from_index(index_full, all_entry_candidates)

    result_clusters = {}
    for c in clusters:
        cid          = c['id']
        files_set    = set(c['files'])
        entry_point  = find_entry_point(c['files'])
        imports_str  = imports_map.get(entry_point, '') if entry_point else ''
        missing      = count_missing_local_imports(entry_point, imports_str, files_set)
        status, basis = determine_status(entry_point, missing)

        result_clusters[cid] = {
            'entry_point':  entry_point,
            'status':       status,
            'status_basis': basis,
        }
        print(f'  {c["name"]:30s}  {status}')

    result = {
        'generated': datetime.datetime.now().isoformat(),
        'clusters':  result_clusters,
    }

    out_path = output_dir / 'SIFT_entry_points.json'
    with open(out_path, 'w', encoding='utf-8') as fout:
        json.dump(result, fout, indent=2)

    print(f'  Output: {out_path}')
    return result


def find_latest_output_dir():
    candidates = sorted(SCRIPT_DIR.glob('SIFT_output_*/SIFT_clusters.json'))
    return candidates[-1].parent if candidates else None


def main():
    output_dir = find_latest_output_dir()
    if not output_dir:
        print('No SIFT_clusters.json found. Run build_clusters.py first.')
        sys.exit(1)
    print(f'Using scan: {output_dir.name}')
    build_entry_points(output_dir)
    print('Done.')


if __name__ == '__main__':
    main()
