---
name: factory-small
description: "AI Factory Small Task Flow: fast path for local, low-risk tasks classified as Small — quick requirement check, mini tech plan, scoped implementation with tests, PR description, lightweight review, smoke QA, human approval. Use for 'factory small', small classified tasks like sort changes, visual states, lint/warning fixes, empty states, text fixes, analytics events, small bugs, or local widgets."
---

# factory-small - Small Task Flow

Fast path for tasks classified Small by `factory-classify`: one screen/component/module, no backend API change, no migrations, no auth/payments/privacy, simple rollback, short smoke checklist.

Pipeline:

```text
Classification → Quick Requirement Check → Mini Tech Plan
→ Implementation → Tests → PR Description
→ Lightweight Review → Smoke QA → Human Approval → Merge
```

Stages run on whatever model the invoking context uses — never pin one.

Small stays lean: no subagent fan-out overhead. The only orchestration worth doing is pushing long builds/test runs to the background while the next artifact (PR description, smoke checklist) is drafted.

## 1. Quick Requirement Check — Product Brain

- Input: raw idea + screen/module context.
- Fix expected behavior as a short mini-spec (bullet rules, each testable).
- Separate blocking questions from non-blocking assumptions; record safe assumptions explicitly ("use existing story.isViewed flag; no backend changes").
- Check whether the task must escalate to Medium (see `factory-classify`); if yes, switch flows now.
- Output: short requirement note (expected behavior, blocking questions, assumptions, recommended next) → `requirements.md`.
- Blocking questions open → ask them; do not continue.

## 2. Mini Tech Plan — Staff Engineer

- Input: mini-spec + repo/module context.
- Find where the list/widget/logic lives, which model fields exist, what the minimal safe change is.
- Output: 3-7 concrete implementation steps, risks, minimal expected tests → `tech-plan.md`.
- If the plan reveals API/state/sync work, escalate to Medium instead of stretching the mini plan.

## 3. Implementation — Implementation Engineer

- Input: mini-spec + mini tech plan + affected files. Never a raw idea.
- Give it explicit rules, e.g.:

```text
Implement viewed stories ordering and ring indication.
Rules:
- unviewed stories first;
- viewed stories last;
- unviewed stories show ring/border;
- viewed stories do not show ring/border;
- preserve stable order inside groups;
- do not change backend/API;
- add tests.
```

- Output: code changes + summary → `build-log.md`.

## 4. Tests — Implementation Engineer

- Minimal automated tests for every rule in the mini-spec: ordering, visual state on/off, stable order inside groups, state transition after the triggering action, persistence after refresh/restart if required.
- Output: tests + test run result.

## 5. PR Description — Implementation Engineer

- Output: PR title, summary bullets, tests list, risks list → `pr-description.md` (template in `factory-artifacts`).

## 6. Lightweight Review — Staff Engineer

- Check: behavior matches the mini-spec; no mutation of source data; stable sorting correct; states not swapped; no needless rebuilds/perf issues; tests cover the main rules.
- Output: approve / request changes → `review.md`. Request changes → back to step 3 with concrete findings.
- For riskier diffs, run `factory-critic` on the diff before the verdict.

## 7. Smoke QA — QA Executor or human

- Input: build + smoke checklist derived from the mini-spec (open screen → verify initial state → perform action → verify transition → refresh → verify order → restart if persistence required).
- Output: passed / failed + notes/screenshots → `qa-report.md`. Failed → back to step 3 via a quick triage: requirements, code, or checklist wrong?

## 8. Human Approval → Merge

- Human Owner reviews PR + review + smoke result and approves or returns the task.
- Merge happens under protected branch policy; agents never merge.

## Done when

Implementation completed; minimal tests added or reason documented; lightweight review passed; smoke QA passed or explicitly not required; human approval received; PR merged.

Simplified statuses for tracker: `Task Classification → Ready for Implementation → In Development → Review → Smoke QA → Approved for Merge → Merged → Done`.

## Emergency / hotfix variant

When a Small task is an emergency fix (production-impacting bug, broken build, P0/P1 regression), run the same flow with two stages collapsed and the rest kept fully intact. Speed comes from skipping documents, never from skipping evidence.

What changes vs. the normal Small flow:

- **Skip the brainstorm and the planning documents.** No `requirements.md`, no `tech-plan.md`. Replace them with a one-paragraph triage note inline in the PR/ticket: symptom (what the user sees / what is broken) and suspected area (which layer or component, from the description alone — before reading code).
- **Keep tests mandatory.** Every fix gets a regression test that reproduces the bug — it must fail without the fix and pass with it. No "obvious one-liner" exception. Do not write tests for unrelated code.
- **Keep lightweight review mandatory.** Still run the step 6 review (and `factory-critic` on the diff for riskier hotfixes). Emergencies are when scope creep and untested fixes do the most damage, so review is non-negotiable.
- **Keep smoke QA mandatory** unless persistence/UI is genuinely untouched, in which case record why it was skipped.

### Root-cause gate (before any code)

Hotfixes invite blind patching. Apply the debugging Iron Law:

> **NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**

Run the four-phase method before editing: (1) **investigate** — read the failing code and its immediate neighbors; (2) **hypothesize** a single root cause; (3) **fix** that cause, not the symptom; (4) **verify** with the reproducing test. **3-fix circuit breaker:** if three fix attempts fail, stop patching — the root cause is wrong. Re-investigate from scratch or escalate. If the root cause stays ambiguous after investigation, ask one focused question instead of guessing.

### Blast-radius escalation gate

Before writing the fix, outline which files and layers it touches. Re-classify upward and abandon the hotfix path when ANY of these is true:

- more than 5 files, or
- the change spans multiple layers (UI + state + data), or
- it needs a new abstraction, a new model field, a backend/API change, or a migration.

Hitting any trigger means the work is no longer Small — re-run `factory-classify` and switch to Medium or Large. A migration or schema/contract change always escalates: stopping the bleeding does not justify an unreviewed structural change.

### Scope and tradeoffs

- Change only what addresses the root cause. No drive-by refactors; if you touch unrelated code, stop and flag scope creep. Park out-of-scope issues with `// TODO(hotfix): <description>`.
- A hotfix may intentionally accept a lesser issue to kill a worse one (fix a P0 while accepting a P2 side effect). Document the tradeoff in a `// TODO(hotfix): <known limitation + severity>` comment and in the PR description. The goal is to stop the bleeding, not reach perfection.
- Ship a single, cherry-pick-friendly commit (`fix:` prefix) staging only fix-related files.

### Verification before the merge ask

No "fixed" / "done" claim without fresh evidence in the same message: the reproducing test run and the formatter/linter output from the latest code. A review or QA agent's own "looks good" report is **not** evidence — only the actual run output is. Stage the long test/CI run in the background and draft the PR description while it completes, then attach the real result. Merge still goes through the active project's protected-branch workflow and CI after human approval; agents never merge and never bypass CI for an emergency.
