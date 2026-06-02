# Discovery Tool

## Purpose

Automated scanner that finds:
- AI tool installations (Claude Code, etc)
- Config files (.env, settings.json)
- Auth tokens and API key locations
- Workspace folders (.openclaw, AppData)

Runs on any Windows machine. Outputs standardized format.

## Why We Need This

Before building integrations or audio layers, we need to know:
1. **What exists** on the machine
2. **Where it lives** (file paths)
3. **What it connects to** (auth, APIs, configs)

This tool answers those questions automatically.

## Usage

1. Download `discovery.bat`
2. Double-click to run
3. A text file opens automatically with results
4. Copy the results and share with your team

## What It Finds

| Item | Purpose |
|------|---------|
| Claude Code location | Where the tool actually installed |
| .env files | API keys, auth tokens |
| .openclaw folder | Your workspace structure |
| AppData folders | Local configs and cache |
| config.json | Settings and preferences |

## Output Format

Results file named: `discovery_results_YYYYMMDD_HHMM.txt`

Contains:
- Machine name
- Username
- Date/time run
- Detailed findings organized by category

## For Your Team

Run this on each machine. Compare results. Understand what each person has installed and where.

This becomes your baseline for understanding system architecture.

## Next Steps

1. Share discovery results with your team
2. Analyze: What patterns exist?
3. Use findings to plan integrations

## Version

Discovery Tool v1.0 - Generic Windows scanner
