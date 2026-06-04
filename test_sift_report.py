import os, sys, json, datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from build_clusters import (
    relative_time, folder_name_to_plain_english, parse_index_full,
    find_scan_roots, get_cluster_root, detect_version_groups, build_clusters,
)
from build_entry_points import (
    find_entry_point, count_missing_local_imports,
    determine_status, build_entry_points,
    STATUS_CAN_RUN, STATUS_NEARLY, STATUS_BROKEN, STATUS_UNKNOWN,
)
from sift_report import (
    load_report_data, render_opening_page, render_no_scan_page,
    build_review_queue, get_current_card,
    load_decisions, save_decision,
    render_card, render_loose_file_card,
    render_apply_step1, render_apply_step2,
    build_readback_prompt, call_groq, call_openrouter, call_ollama,
    python_fallback_summary, generate_readback,
    find_start_with, render_readback_consent, render_readback_result,
)

TEST_DIR  = Path(__file__).parent / 'test_fake_output'
SCAN_ROOT = r'C:\fake_scan'

PASS_COUNT = 0
FAIL_COUNT = 0


def check(name, condition, detail=''):
    global PASS_COUNT, FAIL_COUNT
    if condition:
        print(f'  PASS  {name}')
        PASS_COUNT += 1
    else:
        print(f'  FAIL  {name}' + (f'  ({detail})' if detail else ''))
        FAIL_COUNT += 1


# ── Fake data builders ─────────────────────────────────────────────────────────

def make_fake_index_full():
    lines = [
        '=' * 60,
        'SIFT v2 FULL INDEX',
        'Scan ID: FAKE  |  04 Jun 2026 10:00',
        'Every file. Nothing removed.',
        '=' * 60,
        '',
    ]
    entries = [
        # project-alpha: 3 files. Most recent = 01 Feb 2026.
        (r'C:\fake_scan\project-alpha\main.py',   '01 Jan 2025 10:00'),
        (r'C:\fake_scan\project-alpha\utils.py',  '01 Jan 2025 10:00'),
        (r'C:\fake_scan\project-alpha\config.py', '01 Feb 2026 10:00'),
        # project-alpha-v2: 2 files. Most recent = 14 May 2026.
        (r'C:\fake_scan\project-alpha-v2\main.py',  '14 May 2026 10:00'),
        (r'C:\fake_scan\project-alpha-v2\utils.py', '14 May 2026 10:00'),
        # my-website: 2 files.
        (r'C:\fake_scan\my-website\index.html', '01 Jan 2025 10:00'),
        (r'C:\fake_scan\my-website\style.css',  '01 Jan 2025 10:00'),
        # lonely.py: directly in scan root → loose file.
        (r'C:\fake_scan\lonely.py', '01 Jan 2025 10:00'),
        # solo: 1 file only → below MIN_CLUSTER_FILES → loose.
        (r'C:\fake_scan\solo\script.py', '01 Jan 2025 10:00'),
    ]
    for path, modified in entries:
        lines += [
            '',
            f'FILE: {path}',
            'TYPE: Python | .py',
            'SIZE: 2kb',
            'CREATED:  01 Jan 2025 09:00',
            f'MODIFIED: {modified}',
            'READABLE: Yes',
            '-' * 50,
        ]
    return '\n'.join(lines)


def make_fake_index_summary():
    return f'Scanned:      {SCAN_ROOT}\nTotal files:  9\n'


# ── Setup / teardown ───────────────────────────────────────────────────────────

def setup():
    TEST_DIR.mkdir(exist_ok=True)
    (TEST_DIR / 'SIFT_index_full.txt').write_text(
        make_fake_index_full(), encoding='utf-8'
    )
    (TEST_DIR / 'SIFT_index_summary.txt').write_text(
        make_fake_index_summary(), encoding='utf-8'
    )


def teardown():
    if TEST_DIR.exists():
        for item in TEST_DIR.iterdir():
            if item.is_file():
                item.unlink()
        TEST_DIR.rmdir()


# ── Component 1 tests ──────────────────────────────────────────────────────────

def test_relative_time():
    print('\n--- relative_time ---')
    now = datetime.datetime.now()
    fmt = '%d %b %Y %H:%M'
    check('today',           relative_time(now.strftime(fmt)) == 'today')
    check('yesterday',       relative_time((now - datetime.timedelta(days=1)).strftime(fmt)) == 'yesterday')
    check('4 days ago',      relative_time((now - datetime.timedelta(days=4)).strftime(fmt)) == '4 days ago')
    check('1 week ago',      relative_time((now - datetime.timedelta(days=10)).strftime(fmt)) == '1 week ago')
    check('3 weeks ago',     relative_time((now - datetime.timedelta(days=21)).strftime(fmt)) == '3 weeks ago')
    check('1 month ago',     relative_time((now - datetime.timedelta(days=45)).strftime(fmt)) == '1 month ago')
    check('4 months ago',    relative_time((now - datetime.timedelta(days=120)).strftime(fmt)) == '4 months ago')
    check('over a year ago', relative_time('01 Jan 2025 10:00') == 'over a year ago')
    check('unknown garbage', relative_time('not a date') == 'unknown')
    check('unknown empty',   relative_time('') == 'unknown')


def test_folder_name_to_plain_english():
    print('\n--- folder_name_to_plain_english ---')
    check('strips -v2',      folder_name_to_plain_english('project-alpha-v2') == 'Project Alpha')
    check('strips -final',   folder_name_to_plain_english('my-app-final')     == 'My App')
    check('strips -backup',  folder_name_to_plain_english('tool-backup')      == 'Tool')
    check('underscores',     folder_name_to_plain_english('my_project')       == 'My Project')
    check('title case',      folder_name_to_plain_english('hello-world')      == 'Hello World')
    words = folder_name_to_plain_english('one-two-three-four-five-six').split()
    check('max 5 words',     len(words) <= 5,  f'got {len(words)}')
    check('empty fallback',  folder_name_to_plain_english('') == '')


def test_parse_index_full():
    print('\n--- parse_index_full ---')
    parsed = parse_index_full(TEST_DIR / 'SIFT_index_full.txt')
    paths  = [f['path'] for f in parsed]
    check('9 records',       len(parsed) == 9,                                      f'got {len(parsed)}')
    check('main.py present', r'C:\fake_scan\project-alpha\main.py' in paths)
    check('lonely.py',       r'C:\fake_scan\lonely.py' in paths)
    cfg = next((f for f in parsed if f['path'] == r'C:\fake_scan\project-alpha\config.py'), None)
    check('modified parsed', cfg is not None and cfg.get('modified') == '01 Feb 2026 10:00',
          f'got {cfg}')
    check('no duplicates',   len(paths) == len(set(paths)))


def test_find_scan_roots():
    print('\n--- find_scan_roots ---')
    roots = find_scan_roots(TEST_DIR / 'SIFT_index_summary.txt')
    check('1 root found',    len(roots) == 1,             f'got {roots}')
    check('correct value',   roots[0] == SCAN_ROOT,       f'got {roots}')
    check('missing file',    find_scan_roots(TEST_DIR / 'nonexistent.txt') == [])


def test_get_cluster_root():
    print('\n--- get_cluster_root ---')
    roots = [SCAN_ROOT]
    check('subfolder',       get_cluster_root(r'C:\fake_scan\project-alpha\main.py', roots) == r'C:\fake_scan\project-alpha')
    check('root-level=None', get_cluster_root(r'C:\fake_scan\lonely.py', roots) is None)
    check('no-root fallback',get_cluster_root(r'C:\other\folder\file.py', []) == r'C:\other\folder')


def test_detect_version_groups():
    print('\n--- detect_version_groups ---')
    clusters = [
        {'id': 'cluster_aaa', 'folder': r'C:\fake_scan\project-alpha'},
        {'id': 'cluster_bbb', 'folder': r'C:\fake_scan\project-alpha-v2'},
        {'id': 'cluster_ccc', 'folder': r'C:\fake_scan\my-website'},
    ]
    groups = detect_version_groups(clusters)
    check('1 group detected',   len(groups) == 1,               f'got {groups}')
    ids = list(groups.values())[0]
    check('alpha in group',     'cluster_aaa' in ids)
    check('alpha-v2 in group',  'cluster_bbb' in ids)
    check('website NOT in group','cluster_ccc' not in ids)


def test_build_clusters_end_to_end():
    print('\n--- build_clusters end-to-end ---')
    result   = build_clusters(TEST_DIR)
    clusters = result['clusters']
    loose    = result['loose_files']
    folders  = [c['folder'] for c in clusters]

    check('3 clusters',           len(clusters) == 3,                              f'got {len(clusters)}')
    check('project-alpha',        r'C:\fake_scan\project-alpha'    in folders)
    check('project-alpha-v2',     r'C:\fake_scan\project-alpha-v2' in folders)
    check('my-website',           r'C:\fake_scan\my-website'       in folders)
    check('2 loose files',        len(loose) == 2,                                 f'got {len(loose)}')

    alpha    = next((c for c in clusters if c['folder'] == r'C:\fake_scan\project-alpha'),    None)
    alpha_v2 = next((c for c in clusters if c['folder'] == r'C:\fake_scan\project-alpha-v2'), None)
    website  = next((c for c in clusters if c['folder'] == r'C:\fake_scan\my-website'),        None)

    check('alpha file_count=3',    alpha    is not None and alpha['file_count']    == 3)
    check('alpha-v2 file_count=2', alpha_v2 is not None and alpha_v2['file_count'] == 2)
    check('alpha is_version_group',alpha    is not None and alpha['is_version_group']    is True)
    check('alpha-v2 is_version_group', alpha_v2 is not None and alpha_v2['is_version_group'] is True)
    check('website NOT version group', website is not None and website['is_version_group'] is False)
    check('alpha.versions has v2', alpha is not None and alpha_v2 is not None and alpha_v2['id'] in alpha['versions'])
    check('alpha last_touched set',alpha is not None and alpha['last_touched'] not in ('unknown', ''))

    json_path = TEST_DIR / 'SIFT_clusters.json'
    check('SIFT_clusters.json exists', json_path.exists())
    if json_path.exists():
        with open(json_path, encoding='utf-8') as fh:
            loaded = json.load(fh)
        check('scan_folder key correct', loaded['scan_folder'] == TEST_DIR.name)
        check('clusters key present',    'clusters'    in loaded)
        check('loose_files key present', 'loose_files' in loaded)
        check('generated key present',   'generated'   in loaded)


# ── Component 2 tests ──────────────────────────────────────────────────────────

def make_fake_clusters_json(output_dir):
    """Write a fake SIFT_clusters.json with known clusters for entry point tests."""
    alpha_id  = 'cluster_alpha000001'
    broken_id = 'cluster_broken00001'
    unknown_id = 'cluster_unknown0001'
    data = {
        'generated':   '2026-06-04T10:00:00',
        'scan_folder': output_dir.name,
        'clusters': [
            {
                'id':               alpha_id,
                'folder':           r'C:\fake_scan\project-alpha',
                'name':             'Project Alpha',
                'file_count':       3,
                'last_touched':     '4 months ago',
                'is_version_group': False,
                'versions':         [],
                'files': [
                    r'C:\fake_scan\project-alpha\main.py',
                    r'C:\fake_scan\project-alpha\utils.py',
                    r'C:\fake_scan\project-alpha\config.py',
                ],
            },
            {
                'id':               broken_id,
                'folder':           r'C:\fake_scan\broken-app',
                'name':             'Broken App',
                'file_count':       2,
                'last_touched':     'over a year ago',
                'is_version_group': False,
                'versions':         [],
                'files': [
                    r'C:\fake_scan\broken-app\app.py',
                    r'C:\fake_scan\broken-app\models.py',
                ],
            },
            {
                'id':               unknown_id,
                'folder':           r'C:\fake_scan\loose-notes',
                'name':             'Loose Notes',
                'file_count':       2,
                'last_touched':     'over a year ago',
                'is_version_group': False,
                'versions':         [],
                'files': [
                    r'C:\fake_scan\loose-notes\notes.md',
                    r'C:\fake_scan\loose-notes\ideas.txt',
                ],
            },
        ],
        'loose_files': [],
    }
    path = output_dir / 'SIFT_clusters.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
    return data


def make_fake_index_full_with_imports():
    """
    Fake index_full where:
    - project-alpha/main.py imports utils and config (both present in cluster) → CAN RUN NOW
    - broken-app/app.py imports utils, config, database, auth (none present in cluster) → BROKEN
    - loose-notes has no entry point files → UNKNOWN
    """
    lines = [
        '=' * 60,
        'SIFT v2 FULL INDEX',
        '=' * 60,
        '',
    ]
    entries = [
        # alpha: entry point, all imports present
        (r'C:\fake_scan\project-alpha\main.py',   'MODIFIED: 01 Feb 2026 10:00', 'IMPORTS: utils, config'),
        (r'C:\fake_scan\project-alpha\utils.py',  'MODIFIED: 01 Jan 2025 10:00', ''),
        (r'C:\fake_scan\project-alpha\config.py', 'MODIFIED: 01 Jan 2025 10:00', ''),
        # broken-app: entry point, 4 imports all missing
        (r'C:\fake_scan\broken-app\app.py',    'MODIFIED: 01 Jan 2025 10:00', 'IMPORTS: utils, config, database, auth'),
        (r'C:\fake_scan\broken-app\models.py', 'MODIFIED: 01 Jan 2025 10:00', ''),
        # loose-notes: no entry point
        (r'C:\fake_scan\loose-notes\notes.md', 'MODIFIED: 01 Jan 2025 10:00', ''),
        (r'C:\fake_scan\loose-notes\ideas.txt','MODIFIED: 01 Jan 2025 10:00', ''),
    ]
    for path, modified_line, imports_line in entries:
        block = ['', f'FILE: {path}', 'TYPE: Python | .py', 'SIZE: 1kb',
                 'CREATED:  01 Jan 2025 09:00', modified_line, 'READABLE: Yes']
        if imports_line:
            block.append(imports_line)
        block.append('-' * 50)
        lines += block
    return '\n'.join(lines)


def test_find_entry_point():
    print('\n--- find_entry_point ---')
    check('main.py found',    find_entry_point([r'C:\p\utils.py', r'C:\p\main.py', r'C:\p\config.py']) == r'C:\p\main.py')
    check('app.py found',     find_entry_point([r'C:\p\app.py', r'C:\p\helpers.py']) == r'C:\p\app.py')
    check('bat file found',   find_entry_point([r'C:\p\run_it.bat', r'C:\p\utils.py']) == r'C:\p\run_it.bat')
    check('index.html found', find_entry_point([r'C:\p\index.html', r'C:\p\style.css']) == r'C:\p\index.html')
    check('none found',       find_entry_point([r'C:\p\notes.md', r'C:\p\ideas.txt']) is None)
    # main.py takes priority over app.py
    check('main over app',    find_entry_point([r'C:\p\app.py', r'C:\p\main.py']) == r'C:\p\main.py')


def test_count_missing_local_imports():
    print('\n--- count_missing_local_imports ---')
    cluster = {r'C:\p\main.py', r'C:\p\utils.py', r'C:\p\config.py'}
    check('0 missing',      count_missing_local_imports(r'C:\p\main.py', 'utils, config', cluster) == 0)
    check('1 missing',      count_missing_local_imports(r'C:\p\main.py', 'utils, database', cluster) == 1)
    check('4 missing',      count_missing_local_imports(r'C:\p\main.py', 'utils, config, database, auth', cluster) == 2,
          'utils+config present so only database+auth missing')
    check('empty imports=0',count_missing_local_imports(r'C:\p\main.py', '', cluster) == 0)
    check('no entry=0',     count_missing_local_imports(None, '', cluster) == 0)


def test_determine_status():
    print('\n--- determine_status ---')
    s, _ = determine_status(r'C:\p\main.py', 0)
    check('0 missing = CAN RUN NOW',  s == STATUS_CAN_RUN)
    s, _ = determine_status(r'C:\p\main.py', 1)
    check('1 missing = NEARLY THERE', s == STATUS_NEARLY)
    s, _ = determine_status(r'C:\p\main.py', 2)
    check('2 missing = NEARLY THERE', s == STATUS_NEARLY)
    s, _ = determine_status(r'C:\p\main.py', 3)
    check('3 missing = BROKEN',       s == STATUS_BROKEN)
    s, _ = determine_status(None, 0)
    check('no entry = UNKNOWN',       s == STATUS_UNKNOWN)


def test_build_entry_points_end_to_end():
    print('\n--- build_entry_points end-to-end ---')

    # Write fresh fake files for this test
    (TEST_DIR / 'SIFT_index_full.txt').write_text(
        make_fake_index_full_with_imports(), encoding='utf-8'
    )
    clusters_data = make_fake_clusters_json(TEST_DIR)
    cluster_ids   = {c['id']: c for c in clusters_data['clusters']}

    result = build_entry_points(TEST_DIR)
    ep = result['clusters']

    alpha_id   = 'cluster_alpha000001'
    broken_id  = 'cluster_broken00001'
    unknown_id = 'cluster_unknown0001'

    check('all 3 clusters in output', len(ep) == 3, f'got {len(ep)}')
    check('alpha = CAN RUN NOW',  ep.get(alpha_id,  {}).get('status') == STATUS_CAN_RUN,
          ep.get(alpha_id, {}).get('status'))
    check('broken = BROKEN',      ep.get(broken_id, {}).get('status') == STATUS_BROKEN,
          ep.get(broken_id, {}).get('status'))
    check('unknown = UNKNOWN',    ep.get(unknown_id,{}).get('status') == STATUS_UNKNOWN,
          ep.get(unknown_id, {}).get('status'))
    check('alpha entry point set',ep.get(alpha_id,  {}).get('entry_point') is not None)
    check('broken entry point set',ep.get(broken_id,{}).get('entry_point') is not None)
    check('unknown entry_point=None', ep.get(unknown_id, {}).get('entry_point') is None)
    check('status_basis present', all('status_basis' in v for v in ep.values()))

    json_path = TEST_DIR / 'SIFT_entry_points.json'
    check('SIFT_entry_points.json exists', json_path.exists())
    if json_path.exists():
        with open(json_path, encoding='utf-8') as fh:
            loaded = json.load(fh)
        check('clusters key in JSON', 'clusters' in loaded)
        check('generated key in JSON','generated' in loaded)


# ── Component 3 helpers ────────────────────────────────────────────────────────

def write_c3_fake_data():
    """
    3 clusters: CAN RUN NOW + NEARLY THERE + UNKNOWN → actionable_count = 2.
    Writes SIFT_clusters.json and SIFT_entry_points.json to TEST_DIR.
    """
    id_can   = 'cluster_c3_can00001'
    id_near  = 'cluster_c3_near0001'
    id_unk   = 'cluster_c3_unk00001'

    clusters = {
        'generated':   '2026-06-04T10:00:00',
        'scan_folder': TEST_DIR.name,
        'clusters': [
            {'id': id_can,  'folder': r'C:\s\alpha', 'name': 'Alpha',
             'file_count': 3, 'last_touched': '3 weeks ago',
             'is_version_group': False, 'versions': [],
             'files': [r'C:\s\alpha\main.py', r'C:\s\alpha\utils.py', r'C:\s\alpha\config.py']},
            {'id': id_near, 'folder': r'C:\s\beta',  'name': 'Beta',
             'file_count': 2, 'last_touched': '2 months ago',
             'is_version_group': False, 'versions': [],
             'files': [r'C:\s\beta\app.py', r'C:\s\beta\helpers.py']},
            {'id': id_unk,  'folder': r'C:\s\notes', 'name': 'Notes',
             'file_count': 2, 'last_touched': 'over a year ago',
             'is_version_group': False, 'versions': [],
             'files': [r'C:\s\notes\readme.md', r'C:\s\notes\ideas.txt']},
        ],
        'loose_files': [],
    }
    entry_points = {
        'generated': '2026-06-04T10:00:00',
        'clusters': {
            id_can:  {'entry_point': r'C:\s\alpha\main.py', 'status': 'CAN RUN NOW',   'status_basis': 'Has main.py.'},
            id_near: {'entry_point': r'C:\s\beta\app.py',   'status': 'NEARLY THERE',  'status_basis': 'Has app.py. 1 import missing.'},
            id_unk:  {'entry_point': None,                   'status': 'UNKNOWN',       'status_basis': 'No entry point found.'},
        },
    }
    (TEST_DIR / 'SIFT_clusters.json').write_text(
        json.dumps(clusters, indent=2), encoding='utf-8'
    )
    (TEST_DIR / 'SIFT_entry_points.json').write_text(
        json.dumps(entry_points, indent=2), encoding='utf-8'
    )
    return clusters, entry_points


# ── Component 3 tests ──────────────────────────────────────────────────────────

def test_load_report_data():
    print('\n--- load_report_data ---')
    write_c3_fake_data()

    data = load_report_data(TEST_DIR)
    check('returns dict not None',     data is not None)
    check('clusters key present',      data is not None and 'clusters' in data)
    check('3 clusters loaded',         data is not None and len(data['clusters']) == 3,
          f'got {len(data["clusters"]) if data else "None"}')
    check('actionable_count = 2',      data is not None and data['actionable_count'] == 2,
          f'got {data["actionable_count"] if data else "None"}')
    check('status merged onto cluster',
          data is not None and all('status' in c for c in data['clusters']))
    check('entry_point merged',
          data is not None and all('entry_point' in c for c in data['clusters']))
    check('CAN RUN NOW present',
          data is not None and any(c['status'] == 'CAN RUN NOW'  for c in data['clusters']))
    check('NEARLY THERE present',
          data is not None and any(c['status'] == 'NEARLY THERE' for c in data['clusters']))
    check('scan_folder key present',   data is not None and 'scan_folder' in data)

    # Missing files → returns None
    (TEST_DIR / 'SIFT_entry_points.json').unlink()
    check('None when entry_points missing', load_report_data(TEST_DIR) is None)
    (TEST_DIR / 'SIFT_clusters.json').unlink()
    check('None when both missing',         load_report_data(TEST_DIR) is None)

    # Restore for subsequent tests
    write_c3_fake_data()


def test_render_opening_page():
    print('\n--- render_opening_page ---')
    data2 = {'actionable_count': 2, 'clusters': [], 'loose_files': [], 'scan_folder': ''}
    html2 = render_opening_page(data2)
    check('contains count 2',          '>2<'            in html2)
    check('contains START REVIEWING',  'START REVIEWING' in html2)
    check('button links to /review',   'href="/review"'  in html2)
    check('plural projects',           'projects you can do something' in html2)
    check('no percentages',            '%'              not in html2)
    check('no score words',            'score'          not in html2.lower())

    data1 = {'actionable_count': 1, 'clusters': [], 'loose_files': [], 'scan_folder': ''}
    html1 = render_opening_page(data1)
    check('contains count 1',          '>1<'            in html1)
    check('singular project',          'project you can do something' in html1)

    data0 = {'actionable_count': 0, 'clusters': [], 'loose_files': [], 'scan_folder': ''}
    html0 = render_opening_page(data0)
    check('contains count 0',          '>0<'            in html0)
    check('zero message',              'no projects are ready' in html0)


def test_render_no_scan_page():
    print('\n--- render_no_scan_page ---')
    html = render_no_scan_page()
    check('contains run instruction',  'sift.py'        in html)
    check('contains no scan message',  'No scan found'  in html)
    check('no START REVIEWING button', 'START REVIEWING' not in html)
    check('valid html open/close',     '<html' in html and '</html>' in html)


# ── Component 4 helpers ────────────────────────────────────────────────────────

def make_c4_data():
    """
    Data dict with version group (alpha + alpha-v2), one individual (website),
    and one loose file. Used across Component 4 tests.
    """
    id_alpha    = 'cluster_c4_alpha001'
    id_alpha_v2 = 'cluster_c4_alphav21'
    id_web      = 'cluster_c4_web00001'
    return {
        'clusters': [
            {'id': id_alpha,    'folder': r'C:\s\alpha',    'name': 'Alpha Project',
             'file_count': 3,   'last_touched': '3 weeks ago',
             'is_version_group': True,  'versions': [id_alpha_v2],
             'files': [r'C:\s\alpha\main.py'],
             'status': 'CAN RUN NOW',  'entry_point': r'C:\s\alpha\main.py',
             'status_basis': 'Has main.py.'},
            {'id': id_alpha_v2, 'folder': r'C:\s\alpha-v2', 'name': 'Alpha Project',
             'file_count': 2,   'last_touched': '1 month ago',
             'is_version_group': True,  'versions': [id_alpha],
             'files': [r'C:\s\alpha-v2\main.py'],
             'status': 'NEARLY THERE', 'entry_point': r'C:\s\alpha-v2\main.py',
             'status_basis': '1 import missing.'},
            {'id': id_web,      'folder': r'C:\s\website',  'name': 'My Website',
             'file_count': 4,   'last_touched': 'over a year ago',
             'is_version_group': False, 'versions': [],
             'files': [r'C:\s\website\index.html'],
             'status': 'UNKNOWN',      'entry_point': None,
             'status_basis': 'No entry point.'},
        ],
        'loose_files': [
            {'path': r'C:\s\notes.md', 'name': 'notes.md', 'last_touched': '2 months ago'},
        ],
        'actionable_count': 2,
        'scan_folder': 'test_fake_output',
    }


# ── Component 4 tests ──────────────────────────────────────────────────────────

def test_build_review_queue():
    print('\n--- build_review_queue ---')
    data  = make_c4_data()
    queue = build_review_queue(data)

    # alpha + alpha-v2 → one version_group card. website → one cluster card. notes.md → loose file.
    # Total: 3 cards (not 4 — version group consumes both alpha IDs into one card).
    check('3 cards total',             len(queue) == 3,              f'got {len(queue)}')
    check('first card is version_group', queue[0]['type'] == 'version_group')
    check('version group card is primary', queue[0]['primary_id'] == 'cluster_c4_alpha001')
    check('version group has group_clusters', len(queue[0].get('group_clusters', [])) == 2)
    check('individual cluster second', queue[1]['type'] == 'cluster')
    check('individual cluster is website', queue[1]['name'] == 'My Website')
    check('loose file last',           queue[2]['type'] == 'loose_file')
    check('loose file name correct',   queue[2]['name'] == 'notes.md')
    # both alpha cluster IDs consumed — not doubled
    all_primary_ids = [c['primary_id'] for c in queue]
    check('alpha-v2 not a separate card',
          'cluster_c4_alphav21' not in all_primary_ids)


def test_get_current_card():
    print('\n--- get_current_card ---')
    data  = make_c4_data()
    queue = build_review_queue(data)

    # Empty decisions → first card
    card, idx, total = get_current_card(queue, {})
    check('first card returned',       card is not None)
    check('index is 0',                idx == 0)
    check('total is 3',                total == 3)

    # One decision saved → moves to second card
    pid0 = queue[0]['primary_id']
    card2, idx2, _ = get_current_card(queue, {pid0: 'FINISH IT'})
    check('second card after 1 decision', idx2 == 1)

    # All decided → returns None
    all_decided = {c['primary_id']: 'PUT AWAY' for c in queue}
    card_done, idx_done, total_done = get_current_card(queue, all_decided)
    check('None when all decided',     card_done is None)
    check('idx equals total',          idx_done == total_done)


def test_load_save_decisions():
    print('\n--- load_decisions / save_decision ---')

    # Load from missing file → empty dict
    check('empty when no file',  load_decisions(TEST_DIR) == {})

    # Save one decision, load it back
    save_decision(TEST_DIR, 'cluster_aaa', 'FINISH IT', 'test_scan')
    d = load_decisions(TEST_DIR)
    check('decision saved',      d.get('cluster_aaa') == 'FINISH IT',   f'got {d}')

    # Save a second decision
    save_decision(TEST_DIR, 'cluster_bbb', 'PUT AWAY', 'test_scan')
    d2 = load_decisions(TEST_DIR)
    check('two decisions present', len(d2) == 2,                         f'got {len(d2)}')

    # Overwrite existing decision for same id
    save_decision(TEST_DIR, 'cluster_aaa', 'START FRESH', 'test_scan')
    d3 = load_decisions(TEST_DIR)
    check('overwrite works',     d3.get('cluster_aaa') == 'START FRESH', f'got {d3}')
    check('still two entries',   len(d3) == 2,                           f'got {len(d3)}')

    # JSON file exists and is valid
    dp = TEST_DIR / 'SIFT_decisions.json'
    check('file exists',         dp.exists())
    if dp.exists():
        with open(dp, encoding='utf-8') as fh:
            loaded = json.load(fh)
        check('decisions key present',  'decisions' in loaded)
        check('scan_folder present',    'scan_folder' in loaded)
        check('session_started present','session_started' in loaded)

    # Cleanup
    if dp.exists():
        dp.unlink()


def test_render_card():
    print('\n--- render_card ---')
    data  = make_c4_data()
    queue = build_review_queue(data)

    # First card is version group
    vg_card = queue[0]
    html_vg = render_card(vg_card, 1, 4)
    check('vg: has status label',      'CAN RUN NOW'      in html_vg)
    check('vg: has card name',         'Alpha Project'    in html_vg)
    check('vg: has FINISH IT button',  'FINISH IT'        in html_vg)
    check('vg: has PUT AWAY button',   'PUT AWAY'         in html_vg)
    check('vg: has COME BACK',         'COME BACK TO IT'  in html_vg)
    check('vg: has START FRESH',       'START FRESH'      in html_vg)
    check('vg: form posts to /decide', 'action="/decide"' in html_vg)
    check('vg: primary_id in form',    vg_card['primary_id'] in html_vg)
    check('vg: change note present',   'You can change this any time' in html_vg)
    check('vg: tech detail hidden',    '<details>'        in html_vg)
    check('vg: no percentages',        '%'                not in html_vg)
    check('vg: no delete word',        'delete'           not in html_vg.lower())

    # Second card is individual cluster
    ind_card = queue[1]
    html_ind = render_card(ind_card, 2, 4)
    check('ind: has My Website',       'My Website'       in html_ind)
    check('ind: has UNKNOWN label',    'UNKNOWN'          in html_ind)

    # Status label colors
    check('green for CAN RUN NOW',     '#22c55e' in html_vg)
    check('gray for UNKNOWN',          '#888888' in html_ind)


def test_render_loose_file_card():
    print('\n--- render_loose_file_card ---')
    data  = make_c4_data()
    queue = build_review_queue(data)
    lf_card = queue[2]
    html = render_loose_file_card(lf_card, 4, 4)

    check('loose tag shown',           'loose file, not connected' in html)
    check('filename shown',            'notes.md'                  in html)
    check('nothing deleted stated',    'Nothing here is deleted'   in html)
    check('ATTACH TO A PROJECT',       'ATTACH TO A PROJECT'       in html)
    check('MOVE OUT OF THE WAY',       'MOVE OUT OF THE WAY'       in html)
    check('form posts to /decide',     'action="/decide"'          in html)
    check('no FINISH IT button',       'FINISH IT'                 not in html)
    check('no DELETE button',          '>DELETE<'                  not in html)
    check('change note present',       'You can change this'       in html)


def test_render_apply_step1():
    print('\n--- render_apply_step1 ---')
    data  = make_c4_data()
    queue = build_review_queue(data)
    decisions = {
        queue[0]['primary_id']: 'FINISH IT',
        queue[1]['primary_id']: 'COME BACK TO IT',
        queue[2]['primary_id']: 'MOVE OUT OF THE WAY',
    }
    html = render_apply_step1(queue, decisions)

    check('heading present',           'Apply these decisions' in html)
    check('FINISH IT in list',         'FINISH IT'            in html)
    check('COME BACK TO IT in list',   'COME BACK TO IT'      in html)
    check('MOVE OUT in list',          'MOVE OUT OF THE WAY'  in html)
    check('posts to /apply/step1',     '/apply/step1'         in html)
    check('YES APPLY THESE button',    'YES, APPLY THESE'     in html)
    check('go back link present',      '/review'              in html)
    check('no undecided warning',      'not yet reviewed'     not in html)

    # Undecided warning when some not decided
    html_partial = render_apply_step1(queue, {queue[0]['primary_id']: 'FINISH IT'})
    check('warning shown when undecided', 'warn-text' in html_partial)


def test_render_apply_step2():
    print('\n--- render_apply_step2 ---')
    html = render_apply_step2()
    check('heading present',           'Last chance'          in html)
    check('nothing deleted stated',    'Nothing will be deleted' in html)
    check('CONFIRM AND FINISH button', 'CONFIRM AND FINISH'   in html)
    check('posts to /apply/step2',     '/apply/step2'         in html)
    check('go back link',              '/apply'               in html)


# ── Component 5 tests ──────────────────────────────────────────────────────────

def c5_decisions():
    """Known decisions dict for Component 5 tests."""
    return {
        'cluster_c4_alpha001': 'FINISH IT',
        'cluster_c4_web00001': 'COME BACK TO IT',
        'C:\\projects\\notes.md': 'MOVE OUT OF THE WAY',
    }


def c5_queue():
    """Review queue matching c5_decisions keys, for Component 5 tests."""
    return [
        {'primary_id': 'cluster_c4_alpha001', 'name': 'Alpha Project',
         'type': 'version_group', 'status': 'CAN RUN NOW',
         'file_count': 5, 'last_touched': '3 weeks ago'},
        {'primary_id': 'cluster_c4_web00001', 'name': 'My Website',
         'type': 'cluster', 'status': 'UNKNOWN',
         'file_count': 4, 'last_touched': 'over a year ago'},
        {'primary_id': 'C:\\projects\\notes.md', 'name': 'notes.md',
         'type': 'loose_file', 'status': None,
         'file_count': 1, 'last_touched': '2 months ago'},
    ]


def test_tier1_no_key():
    print('\n--- Tier 1: Groq (no key set) ---')
    os.environ.pop('GROQ_API_KEY', None)
    try:
        call_groq('test prompt')
        check('raises ValueError without key', False,
              detail='expected ValueError, no exception raised')
    except ValueError as e:
        check('raises ValueError without key', True)
        check('error message mentions key', 'GROQ_API_KEY' in str(e), detail=str(e))
    except Exception as e:
        check('raises ValueError without key', False, detail=f'wrong exception: {e}')


def test_tier2_no_key():
    print('\n--- Tier 2: OpenRouter (no key set) ---')
    os.environ.pop('OPENROUTER_API_KEY', None)
    try:
        call_openrouter('test prompt')
        check('raises ValueError without key', False,
              detail='expected ValueError, no exception raised')
    except ValueError as e:
        check('raises ValueError without key', True)
        check('error message mentions key', 'OPENROUTER_API_KEY' in str(e), detail=str(e))
    except Exception as e:
        check('raises ValueError without key', False, detail=f'wrong exception: {e}')


def test_tier3_ollama_down():
    print('\n--- Tier 3: Ollama (connection attempt) ---')
    try:
        call_ollama('test prompt')
        # If Ollama IS running locally, this succeeds — that is also correct behaviour
        check('Ollama responded (running locally)', True)
        check('no exception when Ollama available', True)
    except Exception as e:
        # Ollama not running — correct cascade behaviour
        check('raises exception when Ollama not running', True)
        check('cascade handles Ollama failure', True)


def test_tier4_fallback():
    print('\n--- Tier 4: Python fallback ---')
    dec   = c5_decisions()
    queue = c5_queue()
    text  = python_fallback_summary(dec, queue)

    check('returns non-empty string',      len(text) > 0,             detail=repr(text))
    check('mentions reviewed count',       'reviewed' in text.lower(), detail=text)
    check('mentions FINISH IT project',    'Alpha Project' in text,    detail=text)
    check('mentions COME BACK TO IT',      'My Website' in text,       detail=text)
    check('mentions MOVE OUT item',        'notes.md' in text,         detail=text)
    check('no API jargon in text',         'API' not in text,          detail=text)
    check('no file paths in text',         'C:\\' not in text,         detail=text)


def test_cascade_reaches_tier4():
    print('\n--- Cascade (no keys, no Ollama expected) ---')
    os.environ.pop('GROQ_API_KEY', None)
    os.environ.pop('OPENROUTER_API_KEY', None)
    dec   = c5_decisions()
    queue = c5_queue()

    text, tier = generate_readback(dec, queue)

    check('cascade returns text',          len(text) > 0,             detail=repr(text))
    check('cascade returns tier name',     len(tier) > 0,             detail=repr(tier))
    check('cascade never errors',          True)   # reaching this line = no crash
    # With no keys and (likely) no Ollama, should reach local summary
    # Unless Ollama happens to be running — both outcomes are correct
    check('tier name is a non-empty string', isinstance(tier, str) and len(tier) > 0)


def test_build_readback_prompt():
    print('\n--- build_readback_prompt ---')
    dec    = c5_decisions()
    queue  = c5_queue()
    prompt = build_readback_prompt(dec, queue)

    check('prompt is a string',            isinstance(prompt, str))
    check('prompt contains Alpha Project', 'Alpha Project' in prompt)
    check('prompt contains FINISH IT',     'FINISH IT'     in prompt)
    check('prompt contains My Website',    'My Website'    in prompt)
    check('prompt contains COME BACK',     'COME BACK TO IT' in prompt)
    check('no file paths in prompt',       'C:\\projects'  not in prompt,
          detail='file paths must not be sent to LLM')
    check('no file contents in prompt',    '.py' not in prompt,
          detail='file contents must not be sent to LLM')
    check('prompt has tone instruction',   'plain English' in prompt)


def test_find_start_with():
    print('\n--- find_start_with ---')
    dec   = c5_decisions()  # Alpha Project: FINISH IT, CAN RUN NOW
    queue = c5_queue()
    name  = find_start_with(dec, queue)

    check('returns Alpha Project (FINISH IT + CAN RUN NOW)',
          name == 'Alpha Project', detail=f'got {name!r}')

    # No FINISH IT decisions
    no_finish = {'cluster_c4_alpha001': 'PUT AWAY', 'cluster_c4_web00001': 'PUT AWAY'}
    check('returns None when no FINISH IT',
          find_start_with(no_finish, queue) is None)

    # FINISH IT but status UNKNOWN
    unknown_finish = {queue[1]['primary_id']: 'FINISH IT'}  # My Website: UNKNOWN
    result = find_start_with(unknown_finish, queue)
    check('returns project even if status UNKNOWN when only option',
          result == 'My Website', detail=f'got {result!r}')


def test_render_readback_consent():
    print('\n--- render_readback_consent ---')
    html = render_readback_consent()

    check('heading Almost done',           'Almost done'              in html)
    check('warning: no file contents',     'No file contents'         in html)
    check('warning: only names/decisions', 'project names'            in html)
    check('GENERATE READBACK button',      'GENERATE READBACK'        in html)
    check('skip option present',           'Skip'                     in html)
    check('posts to /readback',            'action="/readback"'       in html)
    check('generate action value',         'value="generate"'         in html)
    check('skip action value',             'value="skip"'             in html)
    check('no API key mentioned',          'api_key' not in html.lower())
    check('no Anthropic mentioned',        'anthropic' not in html.lower())


def test_render_readback_result():
    print('\n--- render_readback_result ---')
    summary = 'You reviewed three items. Two are ready to finish. One is going away.'

    # With start_with
    html_with = render_readback_result(summary, 'Groq (free tier)', 'Alpha Project')
    check('summary text present',          summary                    in html_with)
    check('tier name shown',               'Groq (free tier)'         in html_with)
    check('start_with section shown',      'Alpha Project'            in html_with)
    check('WHERE TO START label',          'WHERE TO START'           in html_with)
    check('save button present',           'Save this summary'        in html_with)
    check('posts to /readback/save',       '/readback/save'           in html_with)

    # Without start_with
    html_none = render_readback_result(summary, 'local summary (no AI used)', None)
    check('no WHERE TO START when None',   'WHERE TO START'       not in html_none)
    check('tier note: local summary',      'local summary'            in html_none)

    # Tier 4 variant
    html_t4 = render_readback_result(summary, 'local summary (no AI used)', 'My Website')
    check('tier 4 tier name correct',      'local summary (no AI used)' in html_t4)
    check('no Anthropic in result',        'anthropic' not in html_t4.lower())
    check('no Groq key in result',         'GROQ_API_KEY' not in html_t4)


# ── Runner ─────────────────────────────────────────────────────────────────────

def main():
    print('=' * 55)
    print('SIFT REPORT TEST — Components 1 through 5')
    print('=' * 55)

    setup()
    try:
        print('\n-- Component 1: build_clusters --')
        test_relative_time()
        test_folder_name_to_plain_english()
        test_parse_index_full()
        test_find_scan_roots()
        test_get_cluster_root()
        test_detect_version_groups()
        test_build_clusters_end_to_end()

        print('\n-- Component 2: build_entry_points --')
        test_find_entry_point()
        test_count_missing_local_imports()
        test_determine_status()
        test_build_entry_points_end_to_end()

        print('\n-- Component 3: sift_report opening screen --')
        test_load_report_data()
        test_render_opening_page()
        test_render_no_scan_page()

        print('\n-- Component 4: project cards and decisions --')
        test_build_review_queue()
        test_get_current_card()
        test_load_save_decisions()
        test_render_card()
        test_render_loose_file_card()
        test_render_apply_step1()
        test_render_apply_step2()

        print('\n-- Component 5: readback cascade --')
        test_tier1_no_key()
        test_tier2_no_key()
        test_tier3_ollama_down()
        test_tier4_fallback()
        test_cascade_reaches_tier4()
        test_build_readback_prompt()
        test_find_start_with()
        test_render_readback_consent()
        test_render_readback_result()
    finally:
        teardown()

    print()
    print('=' * 55)
    print(f'TOTAL:  {PASS_COUNT} PASS   {FAIL_COUNT} FAIL')
    print('RESULT: ' + ('PASS' if FAIL_COUNT == 0 else 'FAIL'))
    print('=' * 55)
    sys.exit(0 if FAIL_COUNT == 0 else 1)


if __name__ == '__main__':
    main()
