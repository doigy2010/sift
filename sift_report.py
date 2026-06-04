import os, sys, json, webbrowser, socket, datetime
import urllib.request, urllib.error
from pathlib import Path

SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))

try:
    from flask import Flask, Response, redirect, url_for, request
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


# ── Component 3: pure data + opening screen ───────────────────────────────────

def find_latest_output_dir():
    """Return most recent SIFT_output_* folder containing both JSON data files."""
    candidates = [
        d for d in sorted(SCRIPT_DIR.glob('SIFT_output_*'))
        if (d / 'SIFT_clusters.json').exists()
        and (d / 'SIFT_entry_points.json').exists()
    ]
    return candidates[-1] if candidates else None


def load_report_data(output_dir):
    """
    Load and merge SIFT_clusters.json and SIFT_entry_points.json.
    Returns data dict on success, None if either file is missing.
    Keys: clusters, loose_files, actionable_count, scan_folder.
    """
    output_dir        = Path(output_dir)
    clusters_path     = output_dir / 'SIFT_clusters.json'
    entry_points_path = output_dir / 'SIFT_entry_points.json'

    if not clusters_path.exists() or not entry_points_path.exists():
        return None

    with open(clusters_path, encoding='utf-8') as f:
        clusters_data = json.load(f)
    with open(entry_points_path, encoding='utf-8') as f:
        entry_data = json.load(f)

    entry_map = entry_data.get('clusters', {})
    clusters  = []
    for c in clusters_data.get('clusters', []):
        merged = dict(c)
        ep = entry_map.get(c['id'], {})
        merged['status']       = ep.get('status',       'UNKNOWN')
        merged['entry_point']  = ep.get('entry_point')
        merged['status_basis'] = ep.get('status_basis', '')
        clusters.append(merged)

    actionable_count = sum(
        1 for c in clusters if c['status'] in ('CAN RUN NOW', 'NEARLY THERE')
    )
    return {
        'clusters':         clusters,
        'loose_files':      clusters_data.get('loose_files', []),
        'actionable_count': actionable_count,
        'scan_folder':      clusters_data.get('scan_folder', ''),
    }


def render_no_scan_page():
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>SIFT</title>'
        '<style>'
        '* { box-sizing: border-box; margin: 0; padding: 0; }'
        'body { background: #0f0f0f; color: #f0f0f0; font-family: Georgia, serif;'
        '       min-height: 100vh; display: flex; flex-direction: column;'
        '       align-items: center; justify-content: center;'
        '       text-align: center; padding: 2rem; }'
        'h1   { font-size: 2rem; margin-bottom: 1.5rem; }'
        'p    { color: #888888; font-size: 1.1rem; line-height: 1.9; }'
        'code { background: #1e1e1e; padding: 0.2rem 0.6rem; font-family: monospace; }'
        '</style></head><body>'
        '<h1>No scan found</h1>'
        '<p>Run SIFT first, then come back here.<br>'
        'In your terminal: <code>python sift.py</code></p>'
        '</body></html>'
    )


def render_opening_page(data):
    count        = data['actionable_count']
    project_word = 'project' if count == 1 else 'projects'
    label        = ('no projects are ready to work on yet' if count == 0
                    else f'{project_word} you can do something with today')
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>SIFT</title>'
        '<style>'
        '* { box-sizing: border-box; margin: 0; padding: 0; }'
        'body { background: #0f0f0f; color: #f0f0f0; font-family: Georgia, serif;'
        '       min-height: 100vh; display: flex; flex-direction: column;'
        '       align-items: center; justify-content: center;'
        '       text-align: center; padding: 2rem; }'
        '.number { font-size: 8rem; font-weight: bold; color: #ffffff; line-height: 1; }'
        '.label  { font-size: 1.1rem; color: #888888; margin-top: 1rem;'
        '          margin-bottom: 3.5rem; max-width: 300px; line-height: 1.5; }'
        '.btn-start { background: #ffffff; color: #0f0f0f; border: none;'
        '             padding: 1.2rem 3.5rem; font-size: 1rem; font-family: Georgia, serif;'
        '             letter-spacing: 0.1em; cursor: pointer;'
        '             text-decoration: none; display: inline-block; }'
        '.btn-start:hover { background: #dddddd; }'
        '</style></head><body>'
        f'<div class="number">{count}</div>'
        f'<div class="label">{label}</div>'
        '<a href="/review" class="btn-start">START REVIEWING</a>'
        '</body></html>'
    )


# ── Components 4 + 5: shared page shell ──────────────────────────────────────

_BASE_CSS = (
    '* { box-sizing: border-box; margin: 0; padding: 0; }'
    'body { background: #0f0f0f; color: #f0f0f0; font-family: Georgia, serif;'
    '       min-height: 100vh; padding: 2rem; }'
    '.page { max-width: 640px; margin: 0 auto; }'
    '.status-label { display: inline-block; padding: 0.3rem 0.9rem;'
    '                font-size: 0.8rem; letter-spacing: 0.1em; margin-bottom: 1.5rem; }'
    '.card-name { font-size: 2.6rem; font-weight: bold; line-height: 1.1;'
    '             margin-bottom: 0.7rem; }'
    '.card-desc { color: #888888; font-size: 1rem; margin-bottom: 2rem; }'
    '.change-note { color: #555555; font-size: 0.85rem; margin-bottom: 1.2rem; }'
    '.btn-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 0.7rem; }'
    '.btn-decision { background: #1a1a1a; color: #f0f0f0; border: 1px solid #2e2e2e;'
    '                padding: 1rem 0.5rem; font-size: 0.85rem;'
    '                font-family: Georgia, serif; letter-spacing: 0.06em;'
    '                cursor: pointer; text-align: center; }'
    '.btn-decision:hover { background: #252525; }'
    '.btn-primary { background: #ffffff; color: #0f0f0f; border: none;'
    '               padding: 1rem 2.5rem; font-size: 1rem;'
    '               font-family: Georgia, serif; letter-spacing: 0.08em;'
    '               cursor: pointer; margin-top: 2rem; display: inline-block; }'
    '.btn-primary:hover { background: #dddddd; }'
    '.btn-secondary { background: transparent; color: #555555;'
    '                 border: 1px solid #333333; padding: 0.8rem 2rem;'
    '                 font-size: 0.9rem; font-family: Georgia, serif;'
    '                 cursor: pointer; margin-top: 1rem; display: inline-block; }'
    '.btn-secondary:hover { color: #888888; border-color: #555555; }'
    'details { margin-top: 2.5rem; }'
    'summary { color: #444444; font-size: 0.8rem; cursor: pointer;'
    '          letter-spacing: 0.05em; }'
    'summary:hover { color: #888888; }'
    '.tech-detail { margin-top: 1rem; color: #555555; font-size: 0.82rem;'
    '               line-height: 1.8; }'
    '.tech-detail code { background: #1a1a1a; padding: 0.1rem 0.4rem;'
    '                    font-family: monospace; font-size: 0.78rem;'
    '                    word-break: break-all; }'
    '.vg-info { background: #161616; padding: 1rem; margin-bottom: 1.5rem;'
    '           font-size: 0.9rem; line-height: 1.8; }'
    '.loose-tag { display: inline-block; color: #555555; font-size: 0.82rem;'
    '             letter-spacing: 0.08em; margin-bottom: 1.5rem; }'
    '.loose-note { color: #444444; font-size: 0.85rem; margin-bottom: 1.5rem; }'
    '.decision-list { margin: 1.5rem 0 2rem; }'
    '.decision-row { padding: 0.7rem 0; border-bottom: 1px solid #1a1a1a;'
    '                font-size: 0.95rem; }'
    '.dname  { color: #f0f0f0; }'
    '.darrow { color: #333333; margin: 0 0.5rem; }'
    '.dchoice { color: #888888; }'
    '.readback-text { font-size: 1.15rem; line-height: 1.9; color: #e0e0e0;'
    '                 margin-bottom: 2.5rem; }'
    '.start-with { background: #161616; padding: 1.2rem 1.5rem; margin-bottom: 2rem; }'
    '.sw-label { color: #555555; font-size: 0.78rem; letter-spacing: 0.1em;'
    '            margin-bottom: 0.4rem; }'
    '.sw-name { color: #f0f0f0; font-size: 1.1rem; }'
    '.tier-note { color: #333333; font-size: 0.78rem; margin-top: 2rem; }'
    '.consent-warning { color: #888888; font-size: 0.9rem; line-height: 1.8;'
    '                   margin-bottom: 2rem; border-left: 2px solid #333333;'
    '                   padding-left: 1rem; }'
    'h1 { font-size: 1.9rem; margin-bottom: 1rem; }'
    'p  { color: #888888; font-size: 0.95rem; line-height: 1.8; margin-bottom: 1rem; }'
    '.back-link { color: #444444; font-size: 0.82rem; text-decoration: none;'
    '             display: block; margin-top: 1.5rem; }'
    '.back-link:hover { color: #888888; }'
    '.warn-text { color: #ef4444; font-size: 0.9rem; margin-bottom: 1rem; }'
)

STATUS_COLORS = {
    'CAN RUN NOW':  '#22c55e',
    'NEARLY THERE': '#eab308',
    'BROKEN':       '#ef4444',
    'UNKNOWN':      '#888888',
}


def _page(body_html):
    return (
        '<!DOCTYPE html><html lang="en"><head><meta charset="UTF-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        '<title>SIFT</title>'
        '<style>' + _BASE_CSS + '</style>'
        '</head><body><div class="page">'
        + body_html
        + '</div></body></html>'
    )


# ── Component 4: review queue ─────────────────────────────────────────────────

def build_review_queue(data):
    clusters    = data['clusters']
    loose_files = data['loose_files']
    queue       = []
    consumed    = set()

    for c in clusters:
        if c['id'] in consumed:
            continue
        if c.get('is_version_group'):
            group_ids      = [c['id']] + c.get('versions', [])
            group_clusters = [x for x in clusters if x['id'] in group_ids]
            for gid in group_ids:
                consumed.add(gid)
            queue.append({
                'type':           'version_group',
                'cluster_ids':    group_ids,
                'primary_id':     c['id'],
                'name':           c['name'],
                'file_count':     sum(x['file_count'] for x in group_clusters),
                'last_touched':   c['last_touched'],
                'status':         c['status'],
                'group_clusters': group_clusters,
                'entry_point':    c.get('entry_point'),
                'status_basis':   c.get('status_basis', ''),
            })

    for c in clusters:
        if c['id'] in consumed:
            continue
        queue.append({
            'type':         'cluster',
            'cluster_ids':  [c['id']],
            'primary_id':   c['id'],
            'name':         c['name'],
            'file_count':   c['file_count'],
            'last_touched': c['last_touched'],
            'status':       c['status'],
            'files':        c.get('files', []),
            'entry_point':  c.get('entry_point'),
            'status_basis': c.get('status_basis', ''),
        })
        consumed.add(c['id'])

    for lf in loose_files:
        queue.append({
            'type':         'loose_file',
            'cluster_ids':  [],
            'primary_id':   lf['path'],
            'name':         lf['name'],
            'file_count':   1,
            'last_touched': lf['last_touched'],
            'path':         lf['path'],
        })

    return queue


def get_current_card(review_queue, decisions_dict):
    total = len(review_queue)
    for i, card in enumerate(review_queue):
        if card['primary_id'] not in decisions_dict:
            return card, i, total
    return None, total, total


# ── Component 4: decisions I/O ────────────────────────────────────────────────

def load_decisions(output_dir):
    decisions_path = Path(output_dir) / 'SIFT_decisions.json'
    if not decisions_path.exists():
        return {}
    with open(decisions_path, encoding='utf-8') as f:
        data = json.load(f)
    return {d['cluster_id']: d['decision'] for d in data.get('decisions', [])}


def save_decision(output_dir, primary_id, decision, scan_folder):
    decisions_path = Path(output_dir) / 'SIFT_decisions.json'
    if decisions_path.exists():
        with open(decisions_path, encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = {
            'session_started': datetime.datetime.now().isoformat(),
            'scan_folder':     scan_folder,
            'decisions':       [],
        }
    data['decisions'] = [d for d in data['decisions'] if d['cluster_id'] != primary_id]
    data['decisions'].append({
        'cluster_id': primary_id,
        'decision':   decision,
        'decided_at': datetime.datetime.now().isoformat(),
    })
    with open(decisions_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)


# ── Component 4: HTML renderers ───────────────────────────────────────────────

def render_card(card, card_num, total_cards):
    status       = card['status']
    color        = STATUS_COLORS.get(status, '#888888')
    name         = card['name']
    file_count   = card['file_count']
    last_touched = card['last_touched']
    primary_id   = card['primary_id']
    file_word    = 'file' if file_count == 1 else 'files'

    status_html = (
        '<div class="status-label" style="color:' + color
        + ';border:1px solid ' + color + ';">' + status + '</div>'
    )
    desc_html = (
        '<div class="card-desc">'
        + str(file_count) + ' ' + file_word + ', last touched ' + last_touched
        + '</div>'
    )
    vg_html = ''
    if card['type'] == 'version_group':
        rows = ''
        for vc in card.get('group_clusters', []):
            vs       = vc.get('status', 'UNKNOWN')
            vc_color = STATUS_COLORS.get(vs, '#888888')
            rows += (
                '<span style="color:' + vc_color + ';">' + vs + '</span>'
                ' &mdash; ' + vc['name']
                + ' (' + str(vc['file_count']) + ' files)<br>'
            )
        vg_html = '<div class="vg-info">' + rows + '</div>'

    ep       = card.get('entry_point') or 'none found'
    sb       = card.get('status_basis') or 'no detail available'
    tech_html = (
        '<details><summary>Show technical detail</summary>'
        '<div class="tech-detail">'
        'Entry point: <code>' + ep + '</code><br>'
        'Basis: ' + sb
        + '</div></details>'
    )
    form_html = (
        '<form action="/decide" method="POST">'
        '<input type="hidden" name="primary_id" value="' + primary_id + '">'
        '<p class="change-note">You can change this any time before you finish.</p>'
        '<div class="btn-grid">'
        '<button class="btn-decision" type="submit" name="decision" value="FINISH IT">FINISH IT</button>'
        '<button class="btn-decision" type="submit" name="decision" value="COME BACK TO IT">COME BACK TO IT</button>'
        '<button class="btn-decision" type="submit" name="decision" value="PUT AWAY">PUT AWAY</button>'
        '<button class="btn-decision" type="submit" name="decision" value="START FRESH">START FRESH</button>'
        '</div></form>'
    )
    body = (
        status_html
        + '<div class="card-name">' + name + '</div>'
        + desc_html + vg_html + form_html + tech_html
    )
    return _page(body)


def render_loose_file_card(card, card_num, total_cards):
    primary_id   = card['primary_id']
    name         = card['name']
    last_touched = card['last_touched']
    body = (
        '<div class="loose-tag">loose file, not connected to any project</div>'
        '<div class="card-name">' + name + '</div>'
        '<div class="card-desc">Last touched ' + last_touched + '</div>'
        '<p class="loose-note">Nothing here is deleted. These options only flag the file.</p>'
        '<form action="/decide" method="POST">'
        '<input type="hidden" name="primary_id" value="' + primary_id + '">'
        '<p class="change-note">You can change this any time before you finish.</p>'
        '<div class="btn-grid">'
        '<button class="btn-decision" type="submit" name="decision"'
        ' value="ATTACH TO A PROJECT">ATTACH TO A PROJECT</button>'
        '<button class="btn-decision" type="submit" name="decision"'
        ' value="MOVE OUT OF THE WAY">MOVE OUT OF THE WAY</button>'
        '</div></form>'
    )
    return _page(body)


def render_apply_step1(review_queue, decisions_dict):
    rows      = []
    undecided = 0
    for card in review_queue:
        pid = card['primary_id']
        if pid in decisions_dict:
            rows.append(
                '<div class="decision-row">'
                '<span class="dname">'   + card['name']           + '</span>'
                '<span class="darrow">&rarr;</span>'
                '<span class="dchoice">' + decisions_dict[pid]    + '</span>'
                '</div>'
            )
        else:
            undecided += 1

    warn_html = ''
    if undecided > 0:
        warn_html = (
            '<p class="warn-text">' + str(undecided)
            + ' item(s) not yet reviewed. '
            '<a href="/review" style="color:#ef4444;">Go back and review them first.</a></p>'
        )
    body = (
        '<h1>Apply these decisions?</h1>'
        + warn_html
        + '<div class="decision-list">' + ''.join(rows) + '</div>'
        '<form action="/apply/step1" method="POST">'
        '<button class="btn-primary" type="submit">YES, APPLY THESE</button>'
        '</form>'
        '<a href="/review" class="back-link">Go back and change something</a>'
    )
    return _page(body)


def render_apply_step2():
    body = (
        '<h1>Last chance to change your mind.</h1>'
        '<p>Your decisions will be saved. Nothing will be deleted or moved. '
        'These are just labels. You can run SIFT again any time.</p>'
        '<form action="/apply/step2" method="POST">'
        '<button class="btn-primary" type="submit">CONFIRM AND FINISH</button>'
        '</form>'
        '<a href="/apply" class="back-link">No, go back</a>'
    )
    return _page(body)


# ── Component 5: readback cascade ────────────────────────────────────────────

def build_readback_prompt(decisions_dict, review_queue):
    """
    Build LLM prompt. Sends project names and decisions only.
    No file paths, no technical detail, no file contents.
    """
    lines = []
    for card in review_queue:
        pid = card['primary_id']
        if pid in decisions_dict:
            lines.append('  ' + card['name'] + ': ' + decisions_dict[pid])

    decisions_text = '\n'.join(lines) if lines else '  (no decisions made)'
    count          = len(lines)

    return (
        'You are reviewing the results of a digital project audit. '
        'The user has just decided what to do with '
        + str(count) + ' item(s).\n\n'
        'Their decisions:\n' + decisions_text + '\n\n'
        'Write 2-3 plain English sentences. '
        'Say what they have, what they chose to do, and what to focus on first. '
        'No recommendations. No encouragement. No jargon. Facts only. '
        'Do not use the words: should, probably, almost certainly, might, seems, appears. '
        'Write like a person summarising what they just saw.'
    )


def call_groq(prompt):
    """
    Tier 1: Groq free tier.
    Raises ValueError if GROQ_API_KEY not set.
    Raises urllib.error.URLError / HTTPError on network or API failure.
    """
    api_key = os.environ.get('GROQ_API_KEY', '').strip()
    if not api_key:
        raise ValueError('GROQ_API_KEY not set')

    payload = json.dumps({
        'model':      'llama3-8b-8192',
        'messages':   [{'role': 'user', 'content': prompt}],
        'max_tokens': 200,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://api.groq.com/openai/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': 'Bearer ' + api_key,
            'Content-Type':  'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result['choices'][0]['message']['content'].strip()


def call_openrouter(prompt):
    """
    Tier 2: OpenRouter free model.
    Raises ValueError if OPENROUTER_API_KEY not set.
    Raises urllib.error.URLError / HTTPError on network or API failure.
    """
    api_key = os.environ.get('OPENROUTER_API_KEY', '').strip()
    if not api_key:
        raise ValueError('OPENROUTER_API_KEY not set')

    payload = json.dumps({
        'model':      'mistralai/mistral-7b-instruct:free',
        'messages':   [{'role': 'user', 'content': prompt}],
        'max_tokens': 200,
    }).encode('utf-8')

    req = urllib.request.Request(
        'https://openrouter.ai/api/v1/chat/completions',
        data=payload,
        headers={
            'Authorization': 'Bearer ' + api_key,
            'Content-Type':  'application/json',
        },
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result['choices'][0]['message']['content'].strip()


def call_ollama(prompt):
    """
    Tier 3: Ollama local model. No key needed.
    Raises urllib.error.URLError if Ollama is not running.
    """
    payload = json.dumps({
        'model':  'mistral',
        'prompt': prompt,
        'stream': False,
    }).encode('utf-8')

    req = urllib.request.Request(
        'http://localhost:11434/api/generate',
        data=payload,
        headers={'Content-Type': 'application/json'},
        method='POST',
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read().decode('utf-8'))
    return result['response'].strip()


def python_fallback_summary(decisions_dict, review_queue):
    """
    Tier 4: Pure Python summary. No API. No key. No network. Always works.
    Returns plain English summary built entirely from SIFT_decisions.json.
    """
    buckets = {
        'FINISH IT': [], 'COME BACK TO IT': [],
        'PUT AWAY':  [], 'START FRESH':     [],
        'ATTACH TO A PROJECT': [], 'MOVE OUT OF THE WAY': [],
    }
    for card in review_queue:
        pid = card['primary_id']
        dec = decisions_dict.get(pid)
        if dec and dec in buckets:
            buckets[dec].append(card['name'])

    total = sum(len(v) for v in buckets.values())
    parts = ['You reviewed ' + str(total) + ' item' + ('s' if total != 1 else '') + '.']

    if buckets['FINISH IT']:
        parts.append('To finish: ' + ', '.join(buckets['FINISH IT']) + '.')
    if buckets['COME BACK TO IT']:
        parts.append('Coming back to: ' + ', '.join(buckets['COME BACK TO IT']) + '.')
    if buckets['PUT AWAY']:
        parts.append('Putting away: ' + ', '.join(buckets['PUT AWAY']) + '.')
    if buckets['START FRESH']:
        parts.append('Starting fresh with: ' + ', '.join(buckets['START FRESH']) + '.')
    if buckets['MOVE OUT OF THE WAY']:
        parts.append('Moving out of the way: ' + ', '.join(buckets['MOVE OUT OF THE WAY']) + '.')

    return ' '.join(parts)


def generate_readback(decisions_dict, review_queue):
    """
    Try LLM tiers in cascade order. Return (summary_text, tier_name).
    Never raises — always reaches Tier 4.
    """
    prompt = build_readback_prompt(decisions_dict, review_queue)

    try:
        text = call_groq(prompt)
        return text, 'Groq (free tier)'
    except Exception:
        pass

    try:
        text = call_openrouter(prompt)
        return text, 'OpenRouter (free model)'
    except Exception:
        pass

    try:
        text = call_ollama(prompt)
        return text, 'Ollama (local, no data sent)'
    except Exception:
        pass

    text = python_fallback_summary(decisions_dict, review_queue)
    return text, 'local summary (no AI used)'


def find_start_with(decisions_dict, review_queue):
    """
    Return the name of the most actionable project to start with, or None.
    Priority: FINISH IT + CAN RUN NOW/NEARLY THERE first, then any FINISH IT.
    """
    for card in review_queue:
        if (decisions_dict.get(card['primary_id']) == 'FINISH IT'
                and card.get('status') in ('CAN RUN NOW', 'NEARLY THERE')):
            return card['name']
    for card in review_queue:
        if decisions_dict.get(card['primary_id']) == 'FINISH IT':
            return card['name']
    return None


def render_readback_consent():
    """HTML for the readback consent page — shown before any API call."""
    body = (
        '<h1>Almost done.</h1>'
        '<div class="consent-warning">'
        'This sends a summary of your decisions to an AI service.<br>'
        'No file contents are sent. Only project names and decisions.'
        '</div>'
        '<form action="/readback" method="POST">'
        '<button class="btn-primary" type="submit" name="action" value="generate">'
        'GENERATE READBACK</button>'
        '</form>'
        '<form action="/readback" method="POST">'
        '<button class="btn-secondary" type="submit" name="action" value="skip">'
        'Skip — show me a plain summary instead</button>'
        '</form>'
    )
    return _page(body)


def render_readback_result(summary_text, tier_name, start_with):
    """HTML for the readback result page."""
    start_html = ''
    if start_with:
        start_html = (
            '<div class="start-with">'
            '<p class="sw-label">WHERE TO START</p>'
            '<p class="sw-name">' + start_with + '</p>'
            '</div>'
        )
    save_html = (
        '<form action="/readback/save" method="POST">'
        '<button class="btn-secondary" type="submit">Save this summary</button>'
        '</form>'
    )
    body = (
        '<div class="readback-text">' + summary_text + '</div>'
        + start_html
        + '<p class="tier-note">Generated using: ' + tier_name + '</p>'
        + save_html
    )
    return _page(body)


# ── Flask app ─────────────────────────────────────────────────────────────────

if FLASK_AVAILABLE:
    app = Flask(__name__)

    @app.route('/')
    def index():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return Response(render_no_scan_page(), mimetype='text/html')
        data = load_report_data(output_dir)
        if data is None:
            return Response(render_no_scan_page(), mimetype='text/html')
        return Response(render_opening_page(data), mimetype='text/html')

    @app.route('/review')
    def review():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return Response(render_no_scan_page(), mimetype='text/html')
        data = load_report_data(output_dir)
        if data is None:
            return Response(render_no_scan_page(), mimetype='text/html')
        queue     = build_review_queue(data)
        decisions = load_decisions(output_dir)
        card, card_num, total = get_current_card(queue, decisions)
        if card is None:
            return redirect(url_for('apply_decisions'))
        if card['type'] == 'loose_file':
            html = render_loose_file_card(card, card_num + 1, total)
        else:
            html = render_card(card, card_num + 1, total)
        return Response(html, mimetype='text/html')

    @app.route('/decide', methods=['POST'])
    def decide():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return redirect(url_for('index'))
        data = load_report_data(output_dir)
        if data is None:
            return redirect(url_for('index'))
        primary_id = request.form.get('primary_id', '').strip()
        decision   = request.form.get('decision',   '').strip()
        if primary_id and decision:
            save_decision(output_dir, primary_id, decision, data['scan_folder'])
        return redirect(url_for('review'))

    @app.route('/apply')
    def apply_decisions():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return redirect(url_for('index'))
        data = load_report_data(output_dir)
        if data is None:
            return redirect(url_for('index'))
        queue     = build_review_queue(data)
        decisions = load_decisions(output_dir)
        return Response(render_apply_step1(queue, decisions), mimetype='text/html')

    @app.route('/apply/step1', methods=['POST'])
    def apply_step1():
        return redirect(url_for('apply_step2'))

    @app.route('/apply/step2', methods=['GET', 'POST'])
    def apply_step2():
        if request.method == 'POST':
            return redirect(url_for('readback'))
        return Response(render_apply_step2(), mimetype='text/html')

    @app.route('/readback', methods=['GET', 'POST'])
    def readback():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return redirect(url_for('index'))
        data = load_report_data(output_dir)
        if data is None:
            return redirect(url_for('index'))

        if request.method == 'GET':
            return Response(render_readback_consent(), mimetype='text/html')

        action     = request.form.get('action', 'skip')
        queue      = build_review_queue(data)
        decisions  = load_decisions(output_dir)
        start_with = find_start_with(decisions, queue)

        if action == 'generate':
            summary_text, tier_name = generate_readback(decisions, queue)
        else:
            summary_text = python_fallback_summary(decisions, queue)
            tier_name    = 'local summary (no AI used)'

        return Response(
            render_readback_result(summary_text, tier_name, start_with),
            mimetype='text/html'
        )

    @app.route('/readback/save', methods=['POST'])
    def readback_save():
        output_dir = find_latest_output_dir()
        if not output_dir:
            return redirect(url_for('index'))
        data = load_report_data(output_dir)
        if data is None:
            return redirect(url_for('index'))
        queue      = build_review_queue(data)
        decisions  = load_decisions(output_dir)
        summary    = python_fallback_summary(decisions, queue)
        start_with = find_start_with(decisions, queue)

        save_path = output_dir / 'SIFT_readback_summary.txt'
        with open(save_path, 'w', encoding='utf-8') as f:
            f.write('SIFT READBACK SUMMARY\n')
            f.write('=' * 40 + '\n\n')
            f.write(summary + '\n\n')
            if start_with:
                f.write('Where to start: ' + start_with + '\n\n')
            f.write('Full decisions:\n')
            for card in queue:
                pid = card['primary_id']
                dec = decisions.get(pid, 'no decision')
                f.write('  ' + card['name'] + ': ' + dec + '\n')

        body = (
            '<h1>Summary saved.</h1>'
            '<p>Saved to the output folder alongside your scan data.</p>'
            '<a href="/" class="back-link">Start over</a>'
        )
        return Response(_page(body), mimetype='text/html')


# ── Server startup ────────────────────────────────────────────────────────────

def find_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 0))
        return s.getsockname()[1]


def main():
    if not FLASK_AVAILABLE:
        print('Flask is required. Install it with:')
        print('  pip install flask')
        sys.exit(1)

    output_dir = find_latest_output_dir()
    if not output_dir:
        print('No scan data found.')
        print('Run: python sift.py  then  python build_clusters.py  '
              'then  python build_entry_points.py  then  python sift_report.py')
    else:
        print(f'Using scan: {output_dir.name}')

    port = find_free_port()
    url  = f'http://127.0.0.1:{port}'
    print(f'Starting SIFT report at {url}')
    print('Opening browser...')
    webbrowser.open(url)
    app.run(host='127.0.0.1', port=port, debug=False)


if __name__ == '__main__':
    main()
