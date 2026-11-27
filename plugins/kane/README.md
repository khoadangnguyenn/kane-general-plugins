# kane

kane helps you run a software project with Claude Code. It sends routine work to cheaper helper agents, keeps project notes between sessions, writes documents people can read, and keeps a wiki of what you learn.

Tier: general · Includes: nothing, it stands alone.

## Skills

A skill is a set of instructions Claude Code loads when your request matches it. You can also call one by name, like `/kane:init`.

| Skill | What it does | Say something like |
|---|---|---|
| `init` | Starts a project: sorts the job into build or deployment, creates the notes in `.ai/`, begins coordinating | `/kane:init a CLI that renames photos by date` |
| `resume` | Reads `.ai/STATE.md` (the project's status file) and continues where the last session stopped | "What was I working on yesterday?" |
| `auto` | Keeps going step by step and asks only before risky actions: real machines, deleting data, rewriting git history, spending money | "Keep going, ask me only if it matters" |
| `build-loop` | Builds features from `SPEC.md`, fixes bugs, re-tests, and hands the work to the agents below | "Add the export feature from the spec" |
| `switch` | Moves the project between build and deployment and writes a handover note | "The build is done, switch to deployment" |
| `maintain` | Periodic cleanup: scores code health, refreshes the codebase map, finds duplicate code | "It has been a while, check code health" |
| `wiki` | An Obsidian knowledge base: saves answers, ingests documents, answers from what it stored | "Save this answer for later" |
| `write-human-docs` | Writes READMEs, guides, ADRs (records of an architecture decision), specs and changelogs in plain prose | "Write the weekly report for my manager" |
| `kane`, `code-style`, `sync` | `kane` says which skill fits when you are unsure. `code-style` is loaded for agents automatically. `sync` is for maintainers only | "Where do I start?" |

## Agents

An agent is a helper Claude Code starts for one job, with its own model and instructions. Haiku is a small, cheap model. Sonnet is a stronger one.

| Agent | Job |
|---|---|
| `builder` | Writes code test-first (Sonnet), usually in its own git worktree, a separate checkout of the repo |
| `critic` | Reviews work independently and always starts fresh (Sonnet) |
| `grunt` | Does mechanical jobs you fully specified, such as running tests or renaming (Haiku) |
| `scout` | Gathers facts from the web, docs and code. It draws no conclusions and edits nothing (Haiku) |
| `writer` | Writes documents for human readers (Sonnet) |

Hooks are small scripts that run on Claude Code events. kane's hooks copy reference files into `.ai/ref/` and remind Claude which skill fits. They also stop the main session from running tests or web searches itself, so `grunt` and `scout` do that work. kane also starts six MCP servers (extra tools for Claude): `context7`, `exa`, `playwright`, `codegraph`, `pdf` and `obsidian`.

## Install

Run these in a terminal, not in the Claude Code chat. You need read access to the kane repository you were given, so accept the GitHub invitation first. Git must also sign in to GitHub without a prompt, for example after `gh auth login` and `gh auth setup-git`.

```
claude plugin marketplace add <owner>/<your-kane-repository>
claude plugin install kane@kane
```

Replace `<owner>` with the owner's GitHub name. Open a new session afterwards.
