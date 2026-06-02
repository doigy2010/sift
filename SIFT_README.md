# SIFT

**Find the truth in any codebase.**

SIFT is a free open source tool that recovers unknown or broken projects.

You point it at a laptop. It tells you exactly what is there and what it was trying to do. No explanation needed from the owner. No assumptions. No bias.

---

## The problem

Thousands of people have half-built projects sitting on laptops.
A developer disappeared. A project was abandoned. Nobody knows what is there anymore.

Standard approach: ask the owner what it is — and inherit all their blind spots.

SIFT approach: look at everything first — and find the truth.

---

## How it works

1. Run SIFT on the laptop
2. SIFT reads every file — nothing is changed, nothing is deleted, read only
3. SIFT redacts any sensitive data it finds before producing output
4. SIFT produces a set of output files with a discovery prompt already attached
5. You upload each file to an LLM of your choice
6. You get a plain English picture of what the project is and what it does

No coding knowledge needed to use the output.

---

## Key features

- Read only — never writes to or changes the laptop being scanned
- Works on Windows, Mac and Linux
- Automatic sensitive data redaction before anything leaves the laptop
- Output chunked to LLM-friendly sizes with prompt already attached
- Git history read if present — often more revealing than the code itself
- Progress bar so you know it has not frozen
- Resumable if interrupted
- Encrypted zip output — you set the password
- Full contents summary before any chunks

---

## What goes to the LLM

Plain text only. The LLM never connects to the laptop.
Python reads the files. Extracts the text. Redacts sensitive patterns.
You paste or upload to the LLM of your choice.
The laptop is never touched by the LLM.

---

## Recommended LLMs to use

Run the same output through multiple models independently for best results:
- Claude
- ChatGPT
- Gemini
- Groq
- Kimi

Then compare what each one says. Where they agree — trust it. Where they disagree — that is the signal.

---

## Installation

Requires Python 3.7 or above.

```
git clone https://github.com/yourusername/sift
cd sift
pip install -r requirements.txt
python sift.py
```

---

## Usage

```
python sift.py
```

Run from any folder. SIFT will ask where to scan.
Output saves to a dated folder wherever the script is run from.

---

## License

MIT — free to use, free to modify, free to share.

---

*SIFT. Born June 2026.*
*"Sifting through shit to get to paradise."*

