---
name: factory-medium
description: "AI Factory Medium Feature Flow: standard path for features classified Medium — product clarification, final requirements, UX behavior spec, technical plan, decomposition into child tasks, implementation with tests, PR review, emulator QA loop with triage, human approval. Use for 'factory medium', features touching several modules, client state, small APIs, backend+client integration, edge cases, or anything needing emulator QA but no heavyweight release process."
---

# factory-medium - Medium Feature Flow

Standard path for features classified Medium by `factory-classify`: several modules, possible client state and small API changes, real edge cases, emulator QA required — but no high-risk zone (payments, auth/security, big migrations, complex rollout).

Pipeline:

```text
Classification → Product Clarification → Final Requirements → UX Behavior Spec
→ Technical Plan → Decomposition → Implementation → Developer Tests
→ PR Description → PR Review → QA loop (factory-qa-loop)
→ Release (factory-release) → Merge
```

Stages run on whatever model the invoking context uses — never pin one.

## 1. Product Clarification — Product Brain

- Close product rules and questions: exact behaviors, limits, MVP cuts, flag usage.
- Example shape: "5 fixed reactions; one per user per post; repeated tap removes; selecting another replaces; aggregated counters; no user list in MVP; no notifications in MVP; feature flag on."
- Output: resolved decisions or blocking questions, recorded in `transcript.md`. Blocking questions open → stop; do not enter technical stages.

## 2. Final Requirements — Product Brain

- Turn decisions into verifiable requirements → `requirements.md` (template in `factory-artifacts`): feature, goal, user story, MVP scope, business rules, acceptance criteria, non-goals, analytics, error/offline/unauthorized behavior, open questions (must be `None` to pass the gate).

## 3. UX Behavior Spec — Product Brain

- Describe interface behavior → `ux-spec.md`: normal/selected/loading/error/offline/empty states, dark mode and small screen notes, visual feedback, behavior after refresh/restart.

## 4. Technical Plan — Staff Engineer

- Input: requirements + UX spec + repo context.
- Output → `tech-plan.md` (template in `factory-artifacts`): affected systems, backend changes if any, client changes, API contract, state model, cache behavior, error handling, analytics, feature flag, risks and mitigations, expected tests.
- Check Technical Gate (`factory-gates`) before continuing. If a hard Large trigger surfaces (new domain model, migration, staged rollout, privacy/security), escalate via `factory-classify`.

## 5. Decomposition — Staff Engineer

- Split the feature into small implementation-ready child tasks → `decomposition.md`.
- Every child task carries: title, area, scope, expected output, expected tests, dependencies, risk, definition of done.
- A child task must be small enough for the Implementation Engineer to complete against explicit rules without product interpretation.
- Mark which child tasks are independent (no shared files, no dependency edges) — these are the parallelization units for the next stage.

## 6. Implementation / Tests / PR

| Stage | Role | Output |
|---|---|---|
| Implementation | Implementation Engineer | code changes per child task → `build-log.md` |
| Developer Tests | Implementation Engineer | unit/widget/API tests + results |
| PR Description | Implementation Engineer | summary, tests, risks → `pr-description.md` |
| PR Review | Staff Engineer | approve / request changes → `review.md` |

- The Implementation Engineer works only on child tasks, never on the raw feature.
- Independent child tasks may run as **parallel implementation subagents in isolated worktrees**, merged in dependency order; tasks sharing files run sequentially. Long builds and test suites go to the background while the next artifact is drafted.
- PR Review checks architecture, correctness, edge cases, risks, and test quality; run `factory-critic` on the diff before the verdict. Request changes → fix → re-review.
- PR Review Gate (`factory-gates`) must pass before QA.

## 7. QA loop

Run `factory-qa-loop`: QA execution plan → emulator QA → QA report → product + technical review of findings → triage decisions → fix/requirements/test-plan loops → retest → final QA status.

A failed scenario is never fixed blindly — it goes through triage first.

## 8. Release

Run `factory-release`: release dossier → human approval → merge gate. The Medium dossier may be compact, but the Merge Gate requires it — do not skip to approval without one. The factory run ends at `Approved for Merge`; the merge itself happens under protected branch policy, never by an agent.

## Done when

Requirements fixed; UX behavior described; technical plan ready; decomposition done; implementation via child tasks completed; developer tests passing; PR review passed; QA execution plan completed; findings triaged; blockers fixed and retested; final QA status recorded; release dossier ready; human approval received; PR merged.
