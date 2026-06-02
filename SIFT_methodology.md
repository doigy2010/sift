# SIFT — Methodology
*How to run a SIFT investigation. Step by step.*

---

## The core rule

**Go in cold.**

Never ask the owner what the project is before you scan.
If you ask first, you inherit their blind spots.
SIFT finds what is actually there — not what the owner thinks is there.

---

## What you need

- Python 3.7 or above installed on your laptop (not the scanned laptop)
- The SIFT script (`sift.py`) on a USB stick or downloaded
- The scanned laptop in front of you, unlocked
- A folder or drive to save output to

---

## Step 1 — Copy SIFT onto the scanned laptop

Copy `sift.py` and `requirements.txt` onto the scanned laptop.
USB stick is fine. Email is fine.

SIFT runs from the scanned laptop directly.
This keeps everything local. Nothing goes to the internet automatically.

---

## Step 2 — Open a terminal on the scanned laptop

**Windows:** Press Win + R → type `cmd` → Enter
**Mac:** Open Terminal from Applications
**Linux:** Open your terminal application

Navigate to the folder where you copied SIFT:
```
cd path/to/where/sift/is
```

---

## Step 3 — Install dependencies

```
pip install -r requirements.txt
```

This installs two things:
- `tqdm` — shows a progress bar so you know it has not frozen
- `pyzipper` — encrypts the output zip

If pip is not available: install Python first (python.org), then try again.

---

## Step 4 — Run SIFT

**Windows (double-click):** Run `run_sift.bat`

**All platforms (terminal):**
```
python sift.py
```

SIFT will:
1. Show a warning and ask for consent
2. Ask which path to scan (press Enter to scan current folder)
3. Start scanning — progress bar shows files processed
4. Tell you where the output is when done
5. Offer to create an encrypted zip

---

## Step 5 — Choose what to scan

When SIFT asks for a path:
- Press Enter to scan the folder SIFT is running from
- Type `C:\` (Windows) or `/` (Mac/Linux) to scan the whole laptop
- Type a specific project folder path to scan just that project

**For a full laptop scan:** type the root drive and press Enter.
This takes longer on large laptops. Expect 5–20 minutes.

---

## Step 6 — Wait for the scan to complete

SIFT shows:
- A progress bar counting files
- The name of the current file
- Estimated time remaining

**If interrupted:** SIFT saves a checkpoint as it goes.
Run it again from the same folder — it will resume from where it stopped.

---

## Step 7 — Collect the output

When SIFT finishes, it creates a folder named `SIFT_output_YYYY_MM_DD_HHMMSS`.

Contents:
- `SIFT_contents.txt` — full list of everything found, with stats
- `SIFT_chunk_01.txt`, `SIFT_chunk_02.txt` — the actual file contents, chunked for LLMs
- `SIFT_git_history.txt` — git commit history if a git repo was found
- `SIFT_fingerprint.txt` — scan ID, machine name, date, file count

**Set a password** when SIFT asks. The encrypted zip protects the output in transit.

---

## Step 8 — Copy the output off the laptop

Copy the encrypted zip to:
- Your own laptop
- A USB stick
- Email to yourself

SIFT does not send anything anywhere. You control where the output goes.

---

## Step 9 — Run the LLM analysis

Open a **fresh incognito window** in your browser.
Go to the LLM of your choice (Claude, ChatGPT, Gemini, Groq, Kimi).

Upload or paste the files in this order:
1. Start with `SIFT_contents.txt` — this gives the LLM an overview first
2. Then each chunk in order: `SIFT_chunk_01.txt`, `02`, `03` etc.
3. If git history exists, upload that last

The discovery prompt at the top of every file tells the LLM exactly what to do.
You do not need to write a prompt yourself.

---

## Step 10 — Run multiple LLMs independently

This is the most important step and the one most people skip.

Run the **same files** through at least two different LLMs.
Use a fresh window for each. Do not let them see each other's answers.

Then compare:
- **Where all models agree** — trust it
- **Where models disagree** — investigate it
- **What one model found that others missed** — flag it

Disagreement between models is information. Do not flatten it.

---

## Step 11 — Write up the findings

After the LLM analysis, write a short summary:
- What the project actually is
- What state it is in
- What is broken or missing
- What it would take to continue

Keep it plain English. If the owner cannot understand it — rewrite it.

---

## What SIFT does NOT do

- Does not modify anything on the scanned laptop
- Does not connect to the internet
- Does not send files anywhere automatically
- Does not execute any code it finds
- Does not guarantee to find everything — very large or cloud-only files may be missed

---

## If something goes wrong

**SIFT crashes mid-scan:**
Run it again from the same folder. It will resume from the checkpoint.

**Files are missing from the output:**
Check `SIFT_contents.txt` — the skipped files section lists anything SIFT could not read and why.

**The LLM says it does not understand the output:**
Start with `SIFT_contents.txt` only. Ask the LLM to summarise what it sees before sending chunks.

**Python is not installed:**
Download from python.org. During install, check "Add Python to PATH". Run again.

---

*SIFT. Born June 2026.*
*"Sifting through shit to get to paradise."*
