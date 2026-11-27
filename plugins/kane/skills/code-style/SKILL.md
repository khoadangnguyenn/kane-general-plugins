---
name: code-style
description: Smallest complete change rules for code. Injected by crew hooks.
disable-model-invocation: true
license: MIT
---

<!-- Adapted from DietrichGebert/ponytail (MIT, Copyright (c) 2026 DietrichGebert).
     Rewritten for crew. Keep this notice if you copy large parts. -->

# code-style

Write the smallest change that fully solves the task. The best code is the code
never written. Be lazy about the solution, never about finishing the change.
End your reply with one or two lines: what you skipped, what you did not check,
and any risk the user must know.

## Before you write

Read the task and the code it touches. List every place the change must reach:
callers, tests, fixtures, config, exports, and any decision record that names
the file (crew memory lists them). Check what the change could break: data it
would destroy or expose, callers that stop working. That is scope. Extra
features are not scope.

## The ladder

Take the first option that fully works:

1. Does it need to exist? Skip features and options nobody asked for. Name them
   in one line. A vague request gets the smallest version that does the core job.
2. Already in this codebase (helper, module, pattern)? Use it the way the
   surrounding code does.
3. Standard library or platform feature? Use it, unless the project has its own.
4. An installed dependency? Use it. Never add a dependency for a few lines.
5. Can it be one line a reader gets at a glance? One line.
6. Otherwise: the minimum code that works.

## Rules

- No abstraction, wrapper, option, config or "for later" code nobody asked for.
  Deletion beats addition. Keep the structure the codebase already has.
- The shortest working diff wins, once you know everything it must touch. A
  one-liner that needs decoding is not short.
- Comment only the why the code cannot show, in one line.
- Bug fix: before you edit, grep every caller of the function you touch. Fix the
  root cause once, in the shared code.
- Code you move or merge keeps its error handling and validation.
- Between options of equal size, take the one that is right on edge cases.
- New non-trivial logic (a branch, a loop, a parser, a numeric kernel, a whole
  new script) leaves one small test or an assert-based self-check. Trivial
  changes need none.
- A shortcut with a known limit gets a comment in this form:
  `shortcut: <the limit>, <when to upgrade>`. A shortcut with no trigger rots.

## Never cut

- Validation at trust boundaries. Error handling that prevents data loss.
  Security basics.
- A reference implementation for any optimized or device-specific kernel. When
  geometry or calibration changes, regenerate the reference in the same commit.
- Measurement code keeps its control, its noise estimate and its printed counts.
- Every remote or device command keeps its timeout. Clean up your own processes
  after a failure.
- Units in names and calibration the real hardware needs.
- Anything the user asked for.

## Device and performance code

When a measured target exists (latency, accuracy), the minimum code is the
smallest code that meets the target on the target device. Do not replace a hot
loop with a generic call before you measure. Pack skills list device traps.

## Experiment code

A throwaway analysis script may skip structure. It may not skip checks: fixed
seeds, one command to rerun, the counts printed, the control included.

## Review mode (used by the `critic` agent in `code` mode)

Order of importance: correct, safe, holds under load, tested, fast, lean.

- Read the diff, then the code it touches: callers, callees, tests.
- Every finding needs a concrete case: "this input leads to this wrong result".
  No case, no finding. No style taste, no vague worry.
- Re-read the lines before you report. Confirm the caller exists and the code
  is really unused (grep the whole tree, including tests and config).
- A `shortcut:` comment that names its limit is a decision, not a finding,
  unless the real load already crosses the limit.
- Propose the smallest fix. Prefer fixes that delete code.
- Groups: Must fix (bug, security, data loss), Should fix (risky code without a
  test, real slowness, duplication), Nice to have. Number findings across groups.
- Each finding has four short parts: what this is, the problem, the fix, and
  what happens if we skip it. End with `Verdict:` and `Not checked:`.

## How crew makes this stick

Self-activation is not reliable. An outside test of ponytail as a bare skill
saw zero self-activations in ten sessions. So crew injects this text:

- at session start, for every role that writes code;
- at sub-agent start, through the agent's `skills:` list or a SubagentStart hook;
- as a three-line reminder before an Edit or Write on a code file.

`crew debt` greps `shortcut:` comments into a ledger and flags the ones with
no trigger.
