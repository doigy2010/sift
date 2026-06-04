# SIFT — The Questions
*The most important file in this repository.*
*Every question that shaped SIFT. Always open. Always growing.*
*Add questions as they arise. Never delete old ones.*
*The questions matter as much as the answers.*

---

## How to use this file

When a new question arises — add it here first.
Before writing any code. Before making any decision.
The question comes before the answer.
Always.

Format:
```
Q: The question
A: The answer (if known)
STATUS: Open / Answered / Deferred
RAISED: Date
```

---

## The founding questions
*The questions that built SIFT from nothing*

---

Q: If you were handed a laptop with an unknown project and could not speak to the owner — what would you do?
A: Scan first. Ask nothing. Let the evidence speak.
STATUS: Answered
RAISED: June 2026

---

Q: If you ask the owner what the project is before looking — what happens?
A: You inherit their blind spots. Their confusion becomes your confusion. Their optimism becomes your bias.
STATUS: Answered
RAISED: June 2026

---

Q: How do you stop the LLM being biased by its own memory from previous sessions?
A: Fresh incognito window. No memory. No context. Clean slate every time. Claude Code has memory — do not use it for discovery.
STATUS: Answered
RAISED: June 2026

---

Q: How do you protect the laptop from the script doing damage?
A: Read only. No write permission given. No execution of anything found. LLM never touches the machine. Only receives plain text.
STATUS: Answered
RAISED: June 2026

---

Q: How do you send data to the LLM without an API?
A: Human in the loop. Python produces the file with prompt already at top. Human pastes it. Human pastes reply back. Total control. Zero black box.
STATUS: Answered
RAISED: June 2026

---

Q: How do you protect sensitive data before it leaves the machine?
A: Redact before anything is written to output. Show context without showing value. Bank accounts last 3 digits. Emails domain and last 2 characters. API keys name only value fully gone. Passwords fully gone.
STATUS: Answered
RAISED: June 2026

---

Q: What if one LLM gets it wrong?
A: Use multiple LLMs independently. Compare results. The ensemble analysis finds the truth across all models. Agreement builds confidence. Disagreement reveals ambiguity.
STATUS: Answered
RAISED: June 2026

---

Q: What about files it cannot read?
A: Log everything. Skip nothing silently. Binary files get a full index entry — name, size, date, type. Everything accounted for. Nothing hidden.
STATUS: Answered
RAISED: June 2026

---

Q: What about system files — Windows, Python installations, Adobe?
A: Skip known system folders professionally. Called deNISTing in forensic practice. Standard installation files add zero discovery value. Log that they were skipped. Nothing hidden. Just set aside.
STATUS: Answered
RAISED: June 2026

---

Q: What about the size of the output — too big for an LLM to read?
A: Split into summary and full index. LLM reads summary first. Asks for specific files if needed. Only targeted content retrieved. No overload.
STATUS: Answered
RAISED: June 2026

---

Q: What about memory crashing on large machines with millions of files?
A: Write to disk as you scan. Never hold file content in RAM. Crash safe — partial output better than nothing.
STATUS: Answered
RAISED: June 2026

---

Q: What about machine speed while scanning — everything freezes?
A: Throttle. Small pause between files. Machine stays responsive. Configurable at top of script.
STATUS: Answered
RAISED: June 2026

---

Q: What about different types of users — coders vs non-coders?
A: Two modes. Builder mode produces plain English output no jargon. Developer mode produces full technical detail.
STATUS: Answered
RAISED: June 2026

---

Q: What if you do not know which folder to scan — you are handed an unknown laptop?
A: Scan the whole machine. SIFT detects all drives automatically. No knowledge of the machine needed.
STATUS: Answered
RAISED: June 2026

---

Q: What about Google Drive and cloud storage synced locally?
A: Treat as any other folder. Scan separately from local files for cleaner results. First run local. Second run Drive. Compare the two.
STATUS: Answered
RAISED: June 2026

---

Q: What if all five projects are genuinely unrecoverable?
A: Say so clearly. Then list what the user learned from building them. The knowledge does not disappear because the files are not worth keeping. Graduate. Start fresh with what you know.
STATUS: Answered
RAISED: June 2026

---

Q: How do you get the LLM to return honest output not positive spin?
A: Four rules baked into every prompt. Forbid encouragement. Require uncertainty to be named. Require evidence for every claim. Forbid the word should. Add adversarial instruction — make the strongest case it is not worth continuing before making the case it is.
STATUS: Answered
RAISED: June 2026

---

Q: How do you calculate real completion percentage without assumption?
A: Measure what exists against what should exist for that project type. Every project type has a known anatomy. Inventory check against known standard. Logic not opinion.
STATUS: Answered
RAISED: June 2026

---

Q: How do you pick which project to focus on first?
A: Four factors scored 1 to 5. Completion, connection, momentum, value. Highest score first. If tied — ask which one would make the user happiest to finish. Evidence decides. Human breaks the tie.
STATUS: Answered
RAISED: June 2026

---

Q: How do you flag anomalies without making assumptions?
A: Logic flags. Human decides. SIFT never acts alone. Flag the observation. State it as fact. Offer a bat file to move to review folder — never delete. Human confirms before anything happens.
STATUS: Answered
RAISED: June 2026

---

Q: What is the real product SIFT is building toward?
A: A pipeline from invisible to complete. Scan — Map — Story — Triage — Brief — Build — Complete. From scattered mess to working product without writing a single line of code.
STATUS: Answered
RAISED: June 2026

---

Q: How do you present information to someone overwhelmed who does not speak tech?
A: One card. One project. Three things only. What it is in one sentence. How far as one real percentage. Honest verdict as one of four words. Finish. Decide. Learn From. Start Fresh. Nothing else on the card.
STATUS: Answered
RAISED: June 2026

---

Q: What is SIFT really?
A: A mirror for your digital work life. A thinking tool disguised as a file scanner. A witness — never a judge.
STATUS: Answered
RAISED: June 2026

---

## The design questions
*Questions about how SIFT is built*

---

Q: Should the prompts be treated as engineering not decoration?
A: Yes. Prompts are versioned, documented, and tested like code. Every prompt has a record of what it does, why it is worded that way, what bias it prevents, when it was last tested.
STATUS: Answered
RAISED: June 2026

---

Q: What is the minimum viable version to prove the concept?
A: Phase 1 only — scan and index. Prove it works reliably on different machines before building the visual map or triage board.
STATUS: Answered
RAISED: June 2026

---

Q: What does nothing goes to GitHub without passing tests first mean in practice?
A: Automated test script runs before every push. Known input. Known output. Pass or fail. No exceptions.
STATUS: Answered
RAISED: June 2026

---

Q: What is the zip password bug?
A: Standard Python zipfile silently ignores passwords on write. Not actually encrypted. Fixed in v2.2 using pyzipper.
STATUS: Answered
RAISED: June 2026

---

Q: What is the Mode 2 store search bug?
A: Script was searching from current working directory not script directory. Fails silently when run from different location. Fixed in v2.2.
STATUS: Answered
RAISED: June 2026

---

## The open questions
*Not yet answered. The frontier of SIFT.*

---

Q: How do we version control the prompts as they evolve?
A: Unknown. Needs design.
STATUS: Open
RAISED: June 2026

---

Q: How do we test prompt quality without bias in the testing itself?
A: Unknown. Circular problem. Needs design.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT tune its prompts per LLM — Claude vs GPT vs Gemini behave differently?
A: Unknown. Needs research.
STATUS: Open
RAISED: June 2026

---

Q: Can SIFT become predictive — not just what you have but what you need to complete it?
A: Possible in Phase 4. Requires pattern recognition across many machines not just one. Deferred.
STATUS: Deferred
RAISED: June 2026

---

Q: What is the minimum evidence threshold before SIFT flags an anomaly?
A: Unknown. Needs testing on real machines to calibrate.
STATUS: Open
RAISED: June 2026

---

Q: What does SIFT DRIVE look like — scanning Google Drive via API not synced files?
A: Separate project. Same methodology. Different data source. Needs Google Drive API integration.
STATUS: Deferred
RAISED: June 2026

---

Q: What does the visual map look like and what tools build it?
A: Designed — NetworkX for connections, D3.js for rendering, Timeline.js for time dimension. Not yet built.
STATUS: Deferred — Phase 2
RAISED: June 2026

---

Q: How do we make honest output feel human not clinical?
A: Unknown. Balance between removing spin and removing warmth is not yet solved.
STATUS: Open
RAISED: June 2026

---

Q: What happens when SIFT runs on a machine with malware?
A: Reading malware files as text should be safe. Not fully verified. Needs security review before SIFT is used on unknown machines in the wild.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT run from a USB stick so nothing needs installing on the scanned machine?
A: Possible. Would remove the Python installation requirement. Significant improvement for cold unknown laptop use case.
STATUS: Open
RAISED: June 2026

---

Q: What does SIFT GIT look like — scanning GitHub repositories?
A: Same methodology. Different data source. Repository contents plus commit history plus issues plus PRs. Rich data for discovery.
STATUS: Deferred
RAISED: June 2026

---

Q: How does SIFT compare two scans of the same machine over time — what changed?
A: Scan ID and fingerprint system exists. Diff logic not yet built. High value feature.
STATUS: Open
RAISED: June 2026

---

Q: What is the right community testing process — how do we collect real machine results at scale?
A: Unknown. Needs design. GitHub issues? A simple form? Discord?
STATUS: Open
RAISED: June 2026

---

Q: How do we know if SIFT is getting better or worse with each version?
A: No measurement system exists yet. Needs baseline metrics. What does good output look like quantitatively?
STATUS: Open
RAISED: June 2026

---

## Add new questions below this line

---

Q: Should SIFT show a progress bar during scanning?
A: Yes. Users need feedback. Currently no progress bar shows during scan. Machine appears frozen.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT show total file count before scanning starts?
A: Yes. User needs to know scale of what is being scanned.
STATUS: Open
RAISED: June 2026

---

Q: Should SIFT show current file number and name during scan?
A: Yes. Shows the scan is alive and progressing.
STATUS: Open
RAISED: June 2026

---

Q: Where did assumptions creep into SIFT output in the first real scan?
A: Multiple places. "Almost certainly not needed", "probably yes", "this looks like Poly", "could be a standalone tool", "safe to delete". All inference dressed as analysis. All forbidden.
STATUS: Answered
RAISED: June 2026

---

Q: How do we eliminate probably and almost certainly from SIFT output?
A: Ban them structurally in the prompt. Forbidden words list: probably, almost certainly, likely, appears to be, seems like, could be, might be, looks like. If it cannot be stated as fact from evidence — say "unknown" or "cannot determine from index alone". Unknown is honest. Probably is spin wearing a disguise.
STATUS: Answered
RAISED: June 2026

---

Q: Does banning forbidden words actually prevent inference or just hide it?
A: No. Banning words does not prevent inference. The LLM still infers — it just finds different words to express the same uncertain conclusion. Forbidden word lists treat the symptom not the cause. The real fix is structural — only ask questions the evidence can actually answer. If the question requires inference the question should not be asked of the LLM at all. Python asks only evidence questions. LLM only receives evidence not gaps.
STATUS: Answered
RAISED: June 2026

---

Q: What is the difference between scanning and metadata indexing and tagging?
A: Three completely different operations with different costs and outputs.

SCANNING — Python opens every file and reads the raw text. Full content. Slow. High memory. High disk write. Gives everything but costs the most.

METADATA INDEXING — Python reads only the file system properties without opening the file. Name, size, created date, modified date, extension, location. Extremely fast. Near zero memory. No disk read at all. Gives the shape of what exists without seeing inside it.

TAGGING — After reading, applying labels to files based on what was found. "This is a config file." "This references three other files." "This has no entry point." Tags are derived facts added on top of what was read. Cheap to store. Powerful for grouping and filtering.

These three can be run at different stages. Metadata first — instant picture of scale. Scanning only the files that matter based on metadata. Tagging after scanning to build the cluster map.
STATUS: Answered
RAISED: June 2026

---

Q: What is the time difference between scanning and metadata indexing?
A: Significant. On a 40,000 file folder:

METADATA ONLY — seconds. Python never opens a file. Just reads directory listings.
SCANNING TEXT FILES — minutes. Python opens and reads 3,745 files.
SCANNING ALL FILES — much longer. Attempting to read 40,000 files including binaries.

The smart approach: metadata pass first to build the inventory instantly. Then targeted scan of only the files worth reading. Two passes. Much faster than one full scan.
STATUS: Answered
RAISED: June 2026

---

Q: What is the speed impact on the laptop while SIFT is running?
A: Current version — significant. Without throttling it uses 100% of one CPU core. Everything else slows. With 3ms throttle between files — manageable but still noticeable on slow machines. The real fix is the two-pass approach. Metadata pass is so fast it causes almost no slowdown. Targeted scan pass reads far fewer files. Total CPU impact drops dramatically.
STATUS: Answered
RAISED: June 2026

---

Q: Does the developer vs tinkerer distinction affect how file types should be interpreted?
A: Yes. Critically. A README.md in a developer's folder signals an intentional project root. A README.md in a tinkerer's folder may have been created by an LLM with no understanding of what it is for. A requirements.txt in a developer's folder means a properly structured Python project. In a tinkerer's folder it may mean they copied a file because an LLM told them to. File presence is a fact. File intent is not. SIFT must separate these completely.
STATUS: Answered
RAISED: June 2026

---

Q: How do you detect project boundaries for tinkerers who do not follow conventions?
A: Not from conventions. From connection clusters. Which files reference which other files. A project boundary is where a cluster of mutually-referencing files lives. Not where a README exists. Not where a config file exists. Where the files themselves point at each other.
STATUS: Answered
RAISED: June 2026

---

Q: Can Python map which files reference each other without understanding the code?
A: Yes. Text pattern matching only. Does file A contain the filename of file B anywhere in its text? If yes — connection found. No code understanding needed. No language parsing needed. Just text search. Works across all languages and all file types equally.
STATUS: Answered
RAISED: June 2026

---

Q: How much of each file should SIFT read for the index?
A: Not all. Not one line. The right balance:
First 5 meaningful lines — shows intent and starting point
Last 5 meaningful lines — shows where it ended up
Any line containing a file reference — shows connections
Any line containing a URL — shows external dependencies
Any line containing TODO or ERROR — shows known problems
Any line that looks like a title or heading — shows self-description
The gap between first and last tells the story of the build without reading the whole thing.
STATUS: Answered
RAISED: June 2026

---

Q: What is a completion signal for a non-coder tinkerer's files?
A: Not conventions. Entry points. Does a runnable thing exist that starts this file?
Python — is there a bat file that calls this script? That is the entry point.
HTML — does it have complete html/head/body structure? Or is it a fragment?
JavaScript — is the function called somewhere or just defined?
The bat file as entry point is the tinkerer's version of if __name__ == main. SIFT should look for bat files and trace what they call. That chain is the real project structure.
STATUS: Answered
RAISED: June 2026

---

Q: Is it dangerous to start a new project without the LLM knowing your existing setup?
A: Yes. Concretely dangerous in these ways:
The LLM may build something you already have. Duplication of effort.
The LLM may build something that conflicts with what exists. Breaking existing tools.
The LLM may use a library you already have installed in a conflicting version.
The LLM may create files in locations that overwrite existing files.
The LLM may assume a clean machine when your machine has a complex existing ecosystem.
Without knowing the setup the LLM is building blind. It will be confident and wrong.
STATUS: Answered
RAISED: June 2026

---

Q: How can an LLM know your setup before starting a new project?
A: SIFT. Run SIFT on your machine first. Hand the index summary to the LLM before starting any new project. The LLM now knows:
What tools already exist
What libraries are already installed
What folder structure is already in place
What is connected to what
What is already working
What is half built
It can now build without breaking. Without duplicating. Without conflicting.
This is the most immediately practical use case for SIFT. Not recovering stranger projects. Informing your own LLM before every new build session.
STATUS: Answered
RAISED: June 2026

---

Q: Should Obsidian plugin folders be added to SKIP_DIRS immediately?
A: Yes. .obsidian/plugins contains zero user-created content. Installed software only. Same category as node_modules and Python site-packages. Adding this to SKIP_DIRS immediately reduces the unreadable file count from 36,623 to probably under 500 on this machine. Massive improvement to scan quality.
STATUS: Answered
RAISED: June 2026

---

Q: Should SIFT detect Claude Code worktrees and flag them?
A: Yes. .claude/worktrees/ is a known pattern. Always temporary. Always potentially duplicating real files. SIFT should detect this pattern and warn — not assume it is safe to delete, not assume it is needed — just flag its existence, its size, and what it appears to duplicate.
STATUS: Answered
RAISED: June 2026

---

Q: If forbidden word lists do not prevent inference — what actually does?
A: Structural prompt design. Only ask the LLM questions the evidence can answer. Never ask it to interpret gaps. The question list fed to the LLM must be derived from what SIFT actually found — not from general curiosity about the project. This is a design problem not a word problem.
STATUS: Open — needs design
RAISED: June 2026

---

Q: What is the right two-pass architecture for SIFT? Metadata first then targeted scan?
A: Designed but not built. Pass 1 — metadata only, instant, full inventory. Pass 2 — targeted scan of files flagged as interesting by Pass 1. Pass 2 list built from: recently modified files, files with interesting extensions, files in non-system folders, files over a minimum size threshold. This cuts scan time and machine impact dramatically.
STATUS: Open — needs building
RAISED: June 2026

---

Q: How does SIFT build a connection map from text pattern matching?
A: For every readable file — extract all filenames mentioned in its text. Cross-reference against the full file inventory. Where a match exists — draw a connection. Build a graph of these connections. Cluster files that are mutually connected. Flag files with no connections as orphans. This is the connection mapping phase — not yet built.
STATUS: Open — needs building
RAISED: June 2026

---

Q: What Python libraries are needed for connection mapping and cluster detection?
A: networkx — builds and analyses the connection graph. Detects clusters automatically. Finds orphan nodes. Calculates which files are most central to the project. Industry standard for graph analysis.
pathlib — already in use. File path operations.
re — already in use. Pattern matching to find filename references in text.
collections — Counter and defaultdict for frequency analysis.
No external API needed. All standard or single-install libraries.
STATUS: Answered
RAISED: June 2026

---

Q: What Python libraries are needed for the metadata-only fast pass?
A: os.stat() — already available in standard library. Returns size, created, modified, permissions without opening the file. os.walk() — already in use. scandir() — faster than walk for metadata-only passes. Returns DirEntry objects with cached stat data. No additional libraries needed.
STATUS: Answered
RAISED: June 2026

---

Q: What is the build time estimate for connection mapping?
A: Realistic estimate for a non-coder using AI assistance:
Connection map builder — 2 to 4 hours of Claude Code sessions
Cluster detection using networkx — 1 to 2 hours
Orphan detection — 30 minutes
Integration into existing SIFT — 2 to 3 hours
Testing on real folders — 1 to 2 hours
Total — roughly 2 to 3 focused sessions
This is not a weekend project. It is a week of focused evenings or 3 dedicated days.
STATUS: Answered
RAISED: June 2026

---

Q: What did we not consider that we should have?
A: Several things:
1. File encoding — non-English files, files with special characters. SIFT may misread or skip these silently.
2. Symlinks — symbolic links that point elsewhere on the machine. Following them could cause infinite loops.
3. Files that change while being scanned — cloud-synced files that update mid-scan. Produces inconsistent results.
4. Hidden files — dot files and folders that contain important config but look like system files.
5. Files with no extension — common in tinkerer setups. SIFT currently has no strategy for these.
6. Very large single files — a single 500mb log file would block the scan for minutes.
7. The LLM context window across multiple sessions — if SIFT output is used across multiple LLM conversations the LLM loses context between sessions. Needs a session handover strategy.
STATUS: Open — needs design
RAISED: June 2026

---

Q: What did we not ask that we should have?
A: The most important question we have not asked: What does SIFT do when it finds the same project in two different states — a working version and a broken version? Which one does it report on? How does it know which is current? This is the tinkerer's most common situation. Multiple versions of the same thing. No clear signal of which one is the real one.
STATUS: Open — critical
RAISED: June 2026

---

Q: What does this all mean for SIFT's build roadmap?
A: SIFT is currently a file reader and lister. What it needs to become is a connection mapper and cluster detector. The current version is valuable as a starting point. But the real intelligence is in the connection map. That is what separates SIFT from a file browser. That is what makes the tinkerer use case work. Without connection mapping SIFT tells you what exists. With connection mapping it tells you what it means.
STATUS: Answered
RAISED: June 2026

---

Q: What triggers a Heartbeat rescan — manual, scheduled, or file change threshold?
STATUS: Open
RAISED: June 2026

---

Q: What is the token cap on the readback screen to keep cost predictable?
STATUS: Open
RAISED: June 2026

---

Q: What batching rules apply to Heartbeat mode — hourly, nightly, or on X file changes?
STATUS: Open
RAISED: June 2026

---

Q: Does Archive physically move files or mark them?
STATUS: Open
RAISED: June 2026

---

Q: Does SIFT work on mobile — single column layout, 48px minimum buttons?
STATUS: Open
RAISED: June 2026

---

*Last updated: June 2026*
*This file is never finished. Every new question is progress.*
*The questions are the product.*

