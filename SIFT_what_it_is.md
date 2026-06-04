# SIFT — What It Is
*The definitive description. Updated June 2026.*
*Replace all previous versions of this document.*

---

## The one line

SIFT is an external brain for anyone who builds things and needs to understand what they have.

---

## The problem it solves

Every person who builds with AI tools has the same problem.

They have a machine full of things they created. Scripts, tools, projects, half-built ideas, abandoned experiments. Some of it works. Some of it is broken. Some of it is duplicated. Most of it is invisible.

The LLM they build with does not know any of it exists. So every new build session starts blind. The LLM makes decisions without knowing what is already there. It installs libraries that conflict. It creates files that overwrite. It builds things that already exist. It breaks things it never knew about.

The human does not know all of it exists either. They forgot what they built six months ago. They cannot remember which version is current. They do not know what connects to what. They are scared to delete anything in case it matters.

SIFT solves both problems at once.

It reads everything on the machine. Maps what connects to what. Finds what is complete and what is broken. Identifies duplicates and versions. Produces a plain English picture for the human and a structured context document for the LLM.

After SIFT runs — the human knows what they have. The LLM knows the machine. Building can begin without breaking anything.

---

## Who it is for

**Anyone who builds with AI tools**
You use Claude, ChatGPT, Cursor, or any AI assistant to create things. You have accumulated projects, scripts, and tools across your machine. You are not sure what still works, what connects to what, or whether starting something new will break something old. SIFT gives you and your LLM the full picture before you build.

**Non-linear thinkers and tinkerers**
You do not work in straight lines. You drift between projects. You name files in ways that made sense at the time. You have multiple versions of the same thing with no clear record of which is current. You have no working memory of what you built six months ago. SIFT is your external memory. It finds what you forgot and shows you what is real.

**Developers handed unknown codebases**
Someone left. A project was abandoned. You have a folder and no handover. SIFT reads everything, maps the structure, and gives you the picture before you touch a single file. Cold discovery. No briefing needed.

**Agencies and freelancers doing rescue work**
First tool on every inherited project. Run it cold. Let the evidence speak before the client explains anything. What the client thinks exists and what actually exists are rarely the same thing.

**Solo founders and micro businesses**
You built something with AI assistance. It works but you do not fully understand it. You are scared to change it in case you break it. You cannot explain it to anyone else. SIFT maps it and tells you in plain English what it is and how it fits together.

**Anyone starting a new project**
Before every new build session — run SIFT. Give the LLM the machine context document. The LLM now knows what exists, what is installed, what ports are in use, what folders are off limits. It builds in the right direction without breaking what is already working.

**Teams onboarding new developers**
New person joins. Runs SIFT on the codebase. Gets the full picture in hours not weeks. No two week handover process. No inherited assumptions. Just the evidence of what is actually there.

---

## What SIFT produces

**For the human:**
A plain English picture of everything found. One project at a time. Memory prosthetics — what you were working on, where you stopped, what was broken, which version is your best one. One decision at a time. No jargon. No technical terms. Designed to work for people who think non-linearly and have no working memory.

**For the LLM:**
A structured machine context document. Complete. Unambiguous. Contains everything the LLM needs to build correctly — installed libraries and versions, active services and ports, existing project inventory, folder rules, current build focus. Handed to the LLM at the start of every new session. The LLM is never blind again.

**For deep investigation:**
A full technical index. Every file. Every connection. Every cluster. Every orphan. Every broken dependency. Every duplicate. Used for project recovery, codebase archaeology, and technical rescue work.

---

## What SIFT never does

Never changes, moves or deletes any file on the machine being scanned.
Never sends anything anywhere without the human seeing it first.
Never connects to the internet automatically.
Never makes assumptions about intent from file names or conventions.
Never uses uncertain language as if it were fact.
Never requires coding knowledge to operate.
Never requires the human to explain what the project is before scanning.

---

## How it works

**Pass 1 — Metadata sweep**
Python reads every file's properties without opening any file. Name, size, date, location. Instant. No impact on machine speed. Produces a complete inventory.

**Pass 2 — Targeted scan**
Python opens and reads only the files worth reading — based on what Pass 1 found. Skips system files, installed software, plugins, and binary files. Reads text, code, config, and documentation files. Redacts sensitive data before anything is written to output.

**Pass 3 — Connection mapping**
Python traces which files reference which other files. Builds a connection graph. Groups connected files into clusters. Flags files with no connections as orphans. Identifies entry points — the files that start things running.

**Pass 4 — Output generation**
Three outputs produced:
  1. Full technical index — everything found, every connection
  2. Machine context document — structured facts for the LLM
  3. Human report — plain English, one project at a time, decision prompts

**Multi-model ensemble — optional**
Upload the index to multiple LLMs independently. Compare what each one says. Where they agree — confidence. Where they disagree — signal. The ensemble prompt is included in every output.

---

## The two end users

SIFT has two completely different end users with completely different needs.

The human needs plain English, memory support, one decision at a time, no jargon, emotional safety around their files.

The LLM needs structured data, complete machine state, no ambiguity, facts not stories.

Same scan. Two outputs. Each designed for its specific reader.

---

## The build roadmap

**Version 1 — shipped**
File scanner and indexer. Reads everything. Redacts sensitive data. Produces index. Multi-model ensemble support. Builder and developer modes.

**Version 2 — in build**
Two-pass architecture. Connection mapping. Cluster detection. Orphan flagging. Machine context document. Duplicate and version detection. Human plain English report.

**Version 3 — designed**
Triage interface. One decision per cluster. Four options — finish, park, archive, start fresh. Broken dependency flagging. Completion scoring per cluster.

**Version 4 — concept**
Visual connection map rendered in browser. Build brief generator for unfinished clusters. Direct integration with Claude Code. Predictive — what is missing to complete each project.

---

## The tagline

*Sifting through shit to get to paradise.*

Public: *Know what you've got. Keep what matters. Build without fear.*

---

## Born

June 2026. In a single conversation. By a non-coder using AI.

The methodology, the questions, the design, the evolution — all human.

The code — AI assisted.

Proof that you do not need to know how to code to build something that works.

---

*This document replaces all previous versions of SIFT_what_it_is.md*
*Updated as SIFT evolves. Always reflects current reality not original intent.*

