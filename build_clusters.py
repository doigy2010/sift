import os, sys, json, re, datetime, hashlib, collections
from pathlib import Path

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
MIN_CLUSTER_FILES = 2

# Folders that are software installations — not user work.
# Skipped entirely when building clusters.
# Files inside are dropped — not moved to loose files.
SKIP_CLUSTER_FOLDERS = {
    'Microsoft VS Code',
    'Smart File Tagger',
    '.vscode',
    'extensions',
    'node_modules',
    'resources',
    'AppData',
    'Local',
    'Roaming',
}

VERSION_SUFFIX_RE = re.compile(
    r'[-_\s]*(v\d+|version\d+|final|backup|old|new|copy|\d+|revised|updated|archive|bak)\s*$',
    re.IGNORECASE
)

DATA_FOLDER_THRESHOLD = 0.90
# Matches files like rcpt_2026..., log_001..., backup_20250101...
# Prefix is alpha-only so rcpt_2026-05-20T10-42-59Z_921b2346 always gives prefix 'rcpt', not a timestamp
DATA_PREFIX_RE = re.compile(r'^([A-Za-z]+)[_\-](\d{3,})', re.IGNORECASE)


def relative_time(mtime_str):
    """Convert 'DD Mon YYYY HH:MM' to relative string. Returns 'unknown' on failure."""
    for fmt in ('%d %b %Y %H:%M', '%d %b %Y'):
        try:
            dt = datetime.datetime.strptime(mtime_str.strip(), fmt)
            break
        except ValueError:
            continue
    else:
        return 'unknown'
    d = (datetime.datetime.now() - dt).days
    if d <= 0:  return 'today'
    if d == 1:  return 'yesterday'
    if d < 7:   return f'{d} days ago'
    if d < 14:  return '1 week ago'
    if d < 30:  return f'{d // 7} weeks ago'
    if d < 60:  return '1 month ago'
    if d < 365: return f'{d // 30} months ago'
    return 'over a year ago'


def folder_name_to_plain_english(folder_name):
    """Tier 1 name: strip version suffix, replace separators, title case, max 5 words."""
    name = VERSION_SUFFIX_RE.sub('', folder_name).strip()
    name = re.sub(r'[-_.]', ' ', name).title()
    words = name.split()[:5]
    return ' '.join(words) if words else folder_name


def parse_index_full(index_full_path):
    """Parse SIFT_index_full.txt. Returns list of dicts with 'path' and 'modified'."""
    files = []
    current = {}
    with open(index_full_path, 'r', encoding='utf-8', errors='replace') as f:
        for raw in f:
            line = raw.rstrip('\n')
            if line.startswith('FILE: '):
                if current.get('path'):
                    files.append(current)
                current = {'path': line[6:].strip()}
            elif line.startswith('MODIFIED: ') and current.get('path'):
                current['modified'] = line[10:].strip()
            elif line == '-' * 50:
                if current.get('path'):
                    files.append(current)
                current = {}
    if current.get('path'):
        files.append(current)
    seen = set()
    out = []
    for f in files:
        if f['path'] not in seen:
            seen.add(f['path'])
            out.append(f)
    return out


def find_scan_roots(index_summary_path):
    """Extract scan roots from 'Scanned:' line in SIFT_index_summary.txt."""
    if not Path(index_summary_path).exists():
        return []
    with open(index_summary_path, 'r', encoding='utf-8', errors='replace') as f:
        for line in f:
            if line.startswith('Scanned:'):
                val = line.split(':', 1)[1].strip()
                return [r.strip() for r in val.split(',')]
    return []


def get_cluster_root(file_path, scan_roots):
    """
    Return folder one level below the matching scan root.
    Returns None when file is directly in the scan root (becomes loose file).
    Falls back to immediate parent when path is under no known scan root.
    """
    p = Path(file_path)
    for root_str in scan_roots:
        try:
            rel = p.relative_to(Path(root_str))
            parts = rel.parts
            if len(parts) >= 2:
                return str(Path(root_str) / parts[0])
            return None
        except ValueError:
            continue
    return str(p.parent)


def detect_version_groups(cluster_list):
    """
    Group clusters by base name (version suffix stripped).
    Returns dict of base_name -> [cluster_id, ...] for groups with 2+ members.
    """
    base_map = collections.defaultdict(list)
    for c in cluster_list:
        raw = VERSION_SUFFIX_RE.sub('', Path(c['folder']).name).strip()
        base = re.sub(r'[-_.]', ' ', raw).strip().lower()
        if base:
            base_map[base].append(c['id'])
    return {b: ids for b, ids in base_map.items() if len(ids) >= 2}


def detect_data_folder(file_paths):
    """
    Returns (True, prefix) if >= 90% of files share the same numbered prefix.
    Pattern: <alpha-prefix>_<3+ digits>  e.g. rcpt_2026..., log_001...
    Returns (False, '') otherwise.
    """
    if not file_paths:
        return False, ''
    prefix_counts = collections.Counter()
    for fp in file_paths:
        m = DATA_PREFIX_RE.match(Path(fp).stem)
        if m:
            prefix_counts[m.group(1).lower()] += 1
    if not prefix_counts:
        return False, ''
    top_prefix, top_count = prefix_counts.most_common(1)[0]
    if top_count / len(file_paths) >= DATA_FOLDER_THRESHOLD:
        return True, top_prefix
    return False, ''


def build_fragment_clusters(loose_raw, connection_map):
    """
    Group loose files that reference each other (via connection_map) into fragment clusters.
    Returns (fragment_cluster_list, remaining_raw).
    """
    if not connection_map or not loose_raw:
        return [], loose_raw

    loose_paths = {f['path'] for f in loose_raw}

    # Build undirected adjacency from connection_map
    adjacency = collections.defaultdict(set)
    for fp in loose_paths:
        refs = connection_map.get(fp, {})
        for ref_path in (refs if isinstance(refs, dict) else {}):
            if ref_path in loose_paths and ref_path != fp:
                adjacency[fp].add(ref_path)
                adjacency[ref_path].add(fp)

    # Union-find connected components
    parent = {f['path']: f['path'] for f in loose_raw}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[ra] = rb

    for fp, neighbors in adjacency.items():
        for nb in neighbors:
            union(fp, nb)

    components = collections.defaultdict(list)
    for f in loose_raw:
        components[find(f['path'])].append(f)

    fragment_clusters = []
    remaining_raw = []

    for root, members in components.items():
        if len(members) < 2:
            remaining_raw.extend(members)
            continue
        cid = 'frag_' + hashlib.md5(root.encode()).hexdigest()[:12]
        latest_dt = None
        for f in members:
            for fmt in ('%d %b %Y %H:%M', '%d %b %Y'):
                try:
                    dt = datetime.datetime.strptime(f.get('modified', '').strip(), fmt)
                    if latest_dt is None or dt > latest_dt:
                        latest_dt = dt
                    break
                except ValueError:
                    continue
        last_touched = (
            relative_time(latest_dt.strftime('%d %b %Y %H:%M')) if latest_dt else 'unknown'
        )
        folders = {str(Path(f['path']).parent) for f in members}
        if len(folders) == 1:
            folder = folders.pop()
            frag_name = 'Fragment: ' + folder_name_to_plain_english(Path(folder).name)
        else:
            frag_name = 'Fragment: ' + Path(members[0]['path']).stem
            folder = str(Path(members[0]['path']).parent)
        fragment_clusters.append({
            'id':               cid,
            'folder':           folder,
            'name':             frag_name,
            'file_count':       len(members),
            'last_touched':     last_touched,
            'is_version_group': False,
            'is_fragment':      True,
            'versions':         [],
            'files':            [f['path'] for f in members],
        })

    return fragment_clusters, remaining_raw


def build_clusters(output_dir):
    """
    Read SIFT_index_full.txt from output_dir.
    Group files into clusters by folder.
    Detect version groups.
    Write SIFT_clusters.json to output_dir.
    Return result dict.
    """
    output_dir    = Path(output_dir)
    index_full    = output_dir / 'SIFT_index_full.txt'
    index_summary = output_dir / 'SIFT_index_summary.txt'

    if not index_full.exists():
        print(f'ERROR: {index_full} not found.')
        sys.exit(1)

    # Load connection map for fragment clustering (optional — graceful if missing)
    conn_map_path = output_dir / 'SIFT_connection_map.json'
    connection_map = {}
    if conn_map_path.exists():
        try:
            with open(conn_map_path, encoding='utf-8') as _f:
                connection_map = json.load(_f)
        except Exception:
            pass

    print('Parsing index...')
    files = parse_index_full(index_full)
    print(f'  {len(files)} file records loaded')

    scan_roots = find_scan_roots(index_summary)
    print(f'  Scan roots: {scan_roots or "(none — using immediate parent folders)"}')

    cluster_files = collections.defaultdict(list)
    loose_raw     = []

    for f in files:
        root = get_cluster_root(f['path'], scan_roots)
        if root is None:
            loose_raw.append(f)
        else:
            cluster_files[root].append(f)

    # Drop software installation folders entirely — not user work, not loose files
    for folder in list(cluster_files.keys()):
        if Path(folder).name in SKIP_CLUSTER_FOLDERS:
            cluster_files.pop(folder)

    # Data folder detection: folder dominated by repetitively-named files (e.g. receipts)
    # Excluded entirely — not moved to loose files
    data_folder_info = {}
    for folder in list(cluster_files.keys()):
        is_data, prefix = detect_data_folder([f['path'] for f in cluster_files[folder]])
        if is_data:
            n = len(cluster_files[folder])
            data_folder_info[folder] = {'prefix': prefix, 'file_count': n}
            cluster_files.pop(folder)
            print(f'  Data folder excluded: {Path(folder).name!r} ({n} files, prefix "{prefix}_*")')

    for folder in list(cluster_files.keys()):
        if len(cluster_files[folder]) < MIN_CLUSTER_FILES:
            loose_raw.extend(cluster_files.pop(folder))

    cluster_list = []
    for folder, flist in sorted(cluster_files.items()):
        cid = 'cluster_' + hashlib.md5(folder.encode()).hexdigest()[:12]
        latest_dt = None
        for f in flist:
            for fmt in ('%d %b %Y %H:%M', '%d %b %Y'):
                try:
                    dt = datetime.datetime.strptime(f.get('modified', '').strip(), fmt)
                    if latest_dt is None or dt > latest_dt:
                        latest_dt = dt
                    break
                except ValueError:
                    continue
        last_touched = (
            relative_time(latest_dt.strftime('%d %b %Y %H:%M')) if latest_dt else 'unknown'
        )
        cluster_list.append({
            'id':               cid,
            'folder':           folder,
            'name':             folder_name_to_plain_english(Path(folder).name),
            'file_count':       len(flist),
            'last_touched':     last_touched,
            'is_version_group': False,
            'versions':         [],
            'files':            [f['path'] for f in flist],
        })

    version_groups = detect_version_groups(cluster_list)
    group_ids = {i for ids in version_groups.values() for i in ids}
    for c in cluster_list:
        if c['id'] in group_ids:
            c['is_version_group'] = True
            for ids in version_groups.values():
                if c['id'] in ids:
                    c['versions'] = [i for i in ids if i != c['id']]
                    break

    # Deduplicate loose_raw before fragment clustering
    seen_loose = set()
    dedup_loose = []
    for f in loose_raw:
        if f['path'] not in seen_loose:
            seen_loose.add(f['path'])
            dedup_loose.append(f)

    # Fragment clustering: loose files that reference each other become a cluster
    fragment_clusters, remaining_raw = build_fragment_clusters(dedup_loose, connection_map)
    if fragment_clusters:
        print(f'  {len(fragment_clusters)} fragment cluster(s) built from loose files')

    # Add fragment clusters after version-group detection (they are never version groups)
    cluster_list.extend(fragment_clusters)

    loose_files = [
        {
            'path':         f['path'],
            'name':         Path(f['path']).name,
            'last_touched': relative_time(f['modified']) if f.get('modified') else 'unknown',
        }
        for f in remaining_raw
    ]

    result = {
        'generated':    datetime.datetime.now().isoformat(),
        'scan_folder':  output_dir.name,
        'clusters':     cluster_list,
        'loose_files':  loose_files,
        'data_folders': [
            {'folder': f, 'prefix': v['prefix'], 'file_count': v['file_count']}
            for f, v in data_folder_info.items()
        ],
    }

    out_path = output_dir / 'SIFT_clusters.json'
    tmp_path = out_path.with_suffix('.tmp')
    with open(tmp_path, 'w', encoding='utf-8') as fout:
        json.dump(result, fout, indent=2)
    tmp_path.replace(out_path)

    n_fragment = len(fragment_clusters)
    n_data     = len(data_folder_info)
    print(f'  {len(cluster_list)} clusters written ({n_fragment} fragment)')
    print(f'  {len(loose_files)} loose files')
    print(f'  {n_data} data folder(s) excluded')
    print(f'  Output: {out_path}')
    return result


def find_latest_output_dir():
    candidates = sorted(SCRIPT_DIR.glob('SIFT_output_*/SIFT_index_full.txt'))
    return candidates[-1].parent if candidates else None


def main():
    output_dir = find_latest_output_dir()
    if not output_dir:
        print('No SIFT output found. Run sift.py Mode 1 first.')
        sys.exit(1)
    print(f'Using scan: {output_dir.name}')
    build_clusters(output_dir)
    print('Done.')


if __name__ == '__main__':
    main()
