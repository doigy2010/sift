#!/usr/bin/env python3
"""
SIFT — Find the truth in any codebase
https://github.com/Waqas56jb/sift

Read only. Never writes to or changes the scanned laptop.
"""

import os
import sys
import re
import json
import hashlib
import platform
import subprocess
from datetime import datetime
from pathlib import Path

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    import pyzipper
    PYZIPPER_AVAILABLE = True
except ImportError:
    PYZIPPER_AVAILABLE = False


# ─── CONSTANTS ────────────────────────────────────────────────────────────────

CHUNK_SIZE = 80_000  # characters per chunk — safe for most LLMs

SCRIPT_NAME = Path(__file__).name

SKIP_EXTENSIONS = {
    '.exe', '.dll', '.so', '.dylib', '.bin', '.dat', '.db', '.sqlite',
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.webp',
    '.mp3', '.mp4', '.wav', '.avi', '.mov', '.mkv', '.flac',
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2',
    '.pdf', '.docx', '.xlsx', '.pptx', '.odt',
    '.pyc', '.pyo', '.class', '.o', '.obj',
    '.DS_Store', '.lock',
}

SKIP_DIRS = {
    '__pycache__', 'node_modules', '.venv', 'venv', 'env',
    '.tox', 'dist', 'build', '.idea', '.vscode',
}

DISCOVERY_PROMPT = """\
=============================================================
SIFT DISCOVERY PROMPT — READ THIS FIRST
=============================================================

You are about to read the contents of an unknown codebase or project.
Your job is to find the truth — not confirm what someone told you.

Please answer:
1. What is this project? What was it trying to do?
2. What tech stack is it built on?
3. How far along is it? What works? What is broken or missing?
4. What are the biggest problems or risks you can see?
5. What would it take to get this project working?
6. Is there anything unusual, suspicious, or notable here?

Rules:
- Go in cold. No assumptions.
- Report what you see, not what you expect.
- If something is unclear — say so. Do not guess.
- If you find something unexpected — flag it.

=============================================================
"""


# ─── REDACTION ────────────────────────────────────────────────────────────────

REDACTION_RULES = [
    # API keys / secrets (name=value or name: value)
    (re.compile(r'(?i)(api[_\-]?key|secret[_\-]?key|access[_\-]?token|auth[_\-]?token)\s*[=:]\s*\S+'),
     r'\1: [REDACTED]'),
    # Passwords
    (re.compile(r'(?i)(password|passwd|pwd)\s*[=:]\s*\S+'),
     r'\1: [REDACTED]'),
    # PEM private keys
    (re.compile(r'-----BEGIN [A-Z ]*PRIVATE KEY-----.*?-----END [A-Z ]*PRIVATE KEY-----', re.DOTALL),
     '[PRIVATE KEY REDACTED]'),
    # JWT tokens
    (re.compile(r'\beyJ[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]+\.[A-Za-z0-9_\-]*\b'),
     '[JWT REDACTED]'),
    # AWS-style access key IDs
    (re.compile(r'\b(AKIA|AIPA|ASIA)[A-Z0-9]{16}\b'),
     '[AWS KEY REDACTED]'),
    # UK sort codes — XX-XX-NN (last segment kept)
    (re.compile(r'\b\d{2}-\d{2}-(\d{2})\b'),
     r'XX-XX-\1'),
    # Credit/debit cards — last 4 digits kept
    (re.compile(r'\b(?:\d[ \-]?){12}(\d{4})\b'),
     r'XXXXXXXXXXXX\1'),
    # Email addresses — first 2 chars + domain kept
    (re.compile(r'\b([A-Za-z0-9._%+\-]{1,2})[A-Za-z0-9._%+\-]+@([A-Za-z0-9.\-]+\.[A-Za-z]{2,})\b'),
     r'\1**@\2'),
    # Phone numbers — last 3 digits kept
    (re.compile(r'\b(\+?[\d\s\-\(\)]{5,})(\d{3})\b'),
     r'XXXXXXX\2'),
]


def redact(text: str) -> str:
    for pattern, replacement in REDACTION_RULES:
        text = pattern.sub(replacement, text)
    return text


# ─── FILE COLLECTION ──────────────────────────────────────────────────────────

def should_skip_dir(name: str) -> bool:
    if name in SKIP_DIRS:
        return True
    if name.startswith('SIFT_output'):
        return True
    return False


def collect_files(scan_path: Path) -> list:
    files = []
    for root, dirs, filenames in os.walk(scan_path):
        dirs[:] = [d for d in dirs if not should_skip_dir(d)]
        for fname in filenames:
            if fname == SCRIPT_NAME:
                continue
            if Path(fname).suffix.lower() in SKIP_EXTENSIONS:
                continue
            files.append(Path(root) / fname)
    return sorted(files)


# ─── FILE READING ─────────────────────────────────────────────────────────────

def read_file_safe(path: Path):
    for enc in ('utf-8', 'latin-1', 'cp1252'):
        try:
            with open(path, 'r', encoding=enc, errors='strict') as f:
                return f.read(), None
        except UnicodeDecodeError:
            continue
        except PermissionError:
            return None, 'permission denied'
        except Exception as e:
            return None, str(e)
    return None, 'binary or unreadable encoding'


# ─── GIT HISTORY ──────────────────────────────────────────────────────────────

def read_git_history(scan_path: Path):
    if not (scan_path / '.git').exists():
        return None
    try:
        graph = subprocess.run(
            ['git', '-C', str(scan_path), 'log', '--oneline', '--all',
             '--graph', '--decorate', '--max-count=500'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()

        detail = subprocess.run(
            ['git', '-C', str(scan_path), 'log', '--format=fuller', '--max-count=50'],
            capture_output=True, text=True, timeout=30
        ).stdout.strip()

        if not graph:
            return None
        return (
            "=== GIT LOG — graph view (up to 500 commits) ===\n\n" + graph +
            "\n\n=== GIT LOG — full detail (last 50 commits) ===\n\n" + detail
        )
    except Exception as e:
        return f"Git history could not be read: {e}"


# ─── CHECKPOINT ───────────────────────────────────────────────────────────────

def load_checkpoint(output_dir: Path) -> dict:
    cp = output_dir / 'sift_checkpoint.json'
    if cp.exists():
        try:
            with open(cp) as f:
                return json.load(f)
        except Exception:
            pass
    return {'processed': [], 'chunks': [], 'partial': '', 'chunk_num': 1}


def save_checkpoint(output_dir: Path, state: dict):
    with open(output_dir / 'sift_checkpoint.json', 'w') as f:
        json.dump(state, f, indent=2)


# ─── FINGERPRINT ──────────────────────────────────────────────────────────────

def make_fingerprint(scan_path, scan_id, file_count, total_bytes):
    lines = [
        "SIFT SCAN FINGERPRINT",
        "=" * 40,
        f"Scan ID:       {scan_id}",
        f"Machine:       {platform.node()}",
        f"OS:            {platform.system()} {platform.release()}",
        f"Scan path:     {scan_path}",
        f"Date/time:     {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Files scanned: {file_count:,}",
        f"Total size:    {total_bytes:,} bytes",
        "=" * 40,
    ]
    return '\n'.join(lines)


# ─── MAIN ─────────────────────────────────────────────────────────────────────

def main():
    print()
    print("=" * 60)
    print("  SIFT — Find the truth in any codebase")
    print("  Read only. Nothing on this laptop will be changed.")
    print("=" * 60)
    print()
    print("WARNING")
    print("This script reads all text files on the path you choose.")
    print("That may include passwords and personal data.")
    print("Sensitive patterns are redacted before output is written.")
    print("You are responsible for handling the output files safely.")
    print("You must have permission to scan this laptop.")
    print()
    if input("Continue? (Y/N): ").strip().upper() != 'Y':
        print("Exiting.")
        sys.exit(0)

    print()
    default = str(Path.cwd())
    raw = input(f"Path to scan [{default}]: ").strip()
    scan_path = Path(raw) if raw else Path(default)

    if not scan_path.exists():
        print(f"\nPath not found: {scan_path}")
        sys.exit(1)

    date_str = datetime.now().strftime('%Y_%m_%d_%H%M%S')
    output_dir = Path.cwd() / f'SIFT_output_{date_str}'
    output_dir.mkdir(exist_ok=True)

    scan_id = hashlib.md5(
        f"{platform.node()}{date_str}{scan_path}".encode()
    ).hexdigest()[:12].upper()

    print(f"\nScan ID:  {scan_id}")
    print(f"Output:   {output_dir}\n")

    state = load_checkpoint(output_dir)
    done_set = set(state['processed'])
    chunks = state['chunks']
    partial = state['partial']

    print("Discovering files...")
    all_files = collect_files(scan_path)
    remaining = [f for f in all_files if str(f) not in done_set]
    print(f"Found {len(all_files):,} files — {len(remaining):,} to process.\n")

    skipped = []
    total_bytes = 0
    file_list = []

    iterator = tqdm(remaining, desc="Scanning", unit="file") if TQDM_AVAILABLE else remaining

    for fpath in iterator:
        if not TQDM_AVAILABLE:
            print(f"  {fpath.name}")

        content, err = read_file_safe(fpath)
        try:
            rel = fpath.relative_to(scan_path)
        except ValueError:
            rel = fpath

        if err:
            skipped.append((str(rel), err))
        else:
            total_bytes += len(content.encode('utf-8', errors='replace'))
            safe = redact(content)
            entry = f"\n\n{'=' * 60}\nFILE: {rel}\n{'=' * 60}\n\n{safe}\n"
            file_list.append(str(rel))

            if partial and len(partial) + len(entry) > CHUNK_SIZE:
                chunks.append(partial)
                partial = ''
            partial += entry

        state['processed'].append(str(fpath))
        state['partial'] = partial
        state['chunks'] = chunks
        done_set.add(str(fpath))
        save_checkpoint(output_dir, state)

    if partial:
        chunks.append(partial)

    # Git history
    git_text = read_git_history(scan_path)
    total_chunks = len(chunks) + (1 if git_text else 0)

    # Contents file
    contents = [
        DISCOVERY_PROMPT,
        "SIFT CONTENTS",
        "=" * 60,
        f"Scan ID:     {scan_id}",
        f"Path:        {scan_path}",
        f"Date:        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Files read:  {len(file_list):,}",
        f"Files skipped: {len(skipped):,}",
        f"Chunks:      {total_chunks}",
        f"Git history: {'yes — see SIFT_git_history.txt' if git_text else 'no'}",
        "",
        "FILES INCLUDED:",
        *[f"  {f}" for f in file_list],
        "",
    ]
    if skipped:
        contents += [
            "FILES SKIPPED:",
            *[f"  {p} — {r}" for p, r in skipped],
            "",
        ]

    (output_dir / 'SIFT_contents.txt').write_text('\n'.join(contents), encoding='utf-8')

    # Chunk files
    for i, body in enumerate(chunks, 1):
        header = f"{DISCOVERY_PROMPT}\nChunk {i} of {total_chunks}\n\n"
        (output_dir / f'SIFT_chunk_{i:02d}.txt').write_text(header + body, encoding='utf-8')

    # Git history file
    if git_text:
        header = f"{DISCOVERY_PROMPT}\nGit History — Chunk {total_chunks} of {total_chunks}\n\n"
        (output_dir / 'SIFT_git_history.txt').write_text(header + git_text, encoding='utf-8')

    # Fingerprint
    fp = make_fingerprint(scan_path, scan_id, len(file_list), total_bytes)
    (output_dir / 'SIFT_fingerprint.txt').write_text(fp, encoding='utf-8')

    # Summary
    print(f"\n{'=' * 60}")
    print("SIFT complete.")
    print(f"  Scan ID:    {scan_id}")
    print(f"  Files read: {len(file_list):,}  |  Skipped: {len(skipped):,}")
    print(f"  Chunks:     {total_chunks}")
    print(f"  Output:     {output_dir}")
    print(f"{'=' * 60}\n")

    # Encrypted zip
    if PYZIPPER_AVAILABLE:
        if input("Create encrypted zip of output? (Y/N): ").strip().upper() == 'Y':
            pw = input("Set a password for the zip: ").strip()
            if pw:
                zip_path = output_dir.parent / f'SIFT_output_{date_str}.zip'
                with pyzipper.AESZipFile(
                    zip_path, 'w',
                    compression=pyzipper.ZIP_DEFLATED,
                    encryption=pyzipper.WZ_AES
                ) as zf:
                    zf.setpassword(pw.encode())
                    for f in output_dir.iterdir():
                        if f.name != 'sift_checkpoint.json':
                            zf.write(f, f.name)
                print(f"\nEncrypted zip: {zip_path}")
                print("IMPORTANT: SIFT does not store your password. Do not lose it.")
    else:
        print("Tip: install pyzipper to enable encrypted zip output.")
        print("     pip install pyzipper\n")

    # Remove checkpoint
    cp = output_dir / 'sift_checkpoint.json'
    if cp.exists():
        cp.unlink()

    print(f"\nDone. Email the zip to yourself before leaving this laptop.")
    print(f"Output folder: {output_dir}\n")


if __name__ == '__main__':
    main()
