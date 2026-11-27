# kane-general-plugins

This repository is a public Claude Code marketplace named `kane`, a list of plugins that Claude Code can install from. It holds one plugin, `kane`: a package of skills (instructions Claude loads when your request matches), helper agents and tools for running a software project.

## Tiers

| Tier | Plugin | What you get |
|---|---|---|
| `general` | `kane` | Starts, resumes and runs a project on autopilot, keeps notes between sessions, writes plain-prose documents and keeps an Obsidian wiki (a folder of linked notes). Ships helper agents and extra tools. |

## Skills

A skill starts on its own when your request matches. You can also call it by name, such as `/kane:init`.

| Plugin | Skill | What it does |
|---|---|---|
| `kane` | `init` | Starts a project: sorts it into build or deployment, creates the notes folder `.ai/` and begins coordinating. |
| `kane` | `resume` | Reads the status file `.ai/STATE.md` and continues where the last session stopped. |
| `kane` | `auto` | Keeps working step by step and asks you only before big or risky actions. |
| `kane` | `build-loop` | Builds features from `SPEC.md`, fixes bugs, re-tests, and sends work to helper agents. |
| `kane` | `switch`, `maintain` | Moves the project between build and deployment; runs periodic cleanup and a code-health check. |
| `kane` | `wiki` | Saves answers, ingests documents and answers from what it stored, in an Obsidian wiki. |
| `kane` | `write-human-docs` | Writes READMEs, guides, specs, reports and changelogs in plain prose. |
| `kane` | `kane`, `code-style`, `sync` | A signpost that says which skill fits; coding rules loaded for helper agents; a maintainers' check of shared copies. |

## Try it

- `/kane:init a CLI that renames photos by date`
- "What was I working on yesterday?"
- "Write the weekly report for my manager."

## Before you start

- Claude Code is installed. Run the `claude plugin` commands in a terminal, not in the chat.
- This repository is public, so you need no invitation.
- Git is installed. If adding the marketplace asks you to sign in to GitHub, run `gh auth login` and then `gh auth setup-git` (`gh` is the GitHub command-line tool).

## Install

```
claude plugin install kane --marketplace khoadangnguyenn/kane-general-plugins
```

This adds the marketplace and installs the plugin in one step. Install the whole tier, then choose per project. Until you run `/kane:init` in a project, every installed plugin is on there. `/kane:init` asks what kind of work the project is, turns on the packs that fit and turns off the other installed kane plugins for that project only. It saves the choice in `.claude/settings.local.json` inside the project, a personal file you do not commit. Type `/reload-plugins` afterwards to apply it.

## Update

```
claude plugin marketplace update kane
claude plugin update kane@kane
```

Then open a new Claude Code session.
