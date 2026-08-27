---
name: factory-gates
description: "AI Factory reference: gate rules (requirement, technical, PR review, QA, merge), Definition of Ready and Done per flow size, tracker status sets with transition rules, and the post-QA decision catalogue. Use when checking whether a factory task may pass to the next stage, when wiring factory statuses into Linear/GitHub Issues/Jira/Tracker, or when deciding what counts as Ready or Done for Small, Medium, or Large tasks."
---

# factory-gates - gates, DoR/DoD, statuses

Reference skill. Gates are hard checks between stages: a task that fails a gate goes back, not forward.

## Gate rules

**Requirement Gate** — pass only if: goal clear; user story clear; business rules fixed; acceptance criteria exist; non-goals exist; blocking questions closed; behavior verifiable.

**Technical Gate** — implementation may start only if: affected systems understood; approach chosen; risks described; child tasks small enough; expected tests defined; protected/high-risk areas untouched without approval.

**PR Review Gate** — PR may go to QA only if: PR linked to the task; scope did not grow; CI/tests green or reasons documented; review has no blocking issues; known risks recorded.

**QA Gate** — task may go to approval only if: QA plan executed; failed scenarios resolved through triage; blockers fixed; retest done; final QA report ready.

**Merge Gate** — merge allowed only if: PR approved; CI green; final QA passed or accepted with explicit non-blocking issues; release dossier ready for Medium/Large; human approval received; rollback understood where needed.

## Definition of Ready / Done

| Flow | Ready | Done |
|---|---|---|
| Small | quick requirement check done; no blocking product questions; affected area known; behavior testable with a short checklist | implementation done; minimal tests added or reason documented; lightweight review passed; smoke QA passed; human approval received |
| Medium | product rules fixed; final requirements exist; UX behavior spec exists; technical plan exists; QA plan derivable | implementation done; developer tests passed or documented; PR review passed; emulator QA completed; findings triaged; retest passed if needed; human approval received |
| Large | product discovery completed; requirements gate passed; UX spec exists; technical discovery and architecture completed; decomposition exists; rollout/rollback expectations known | all child tasks completed; tests and PR reviews completed; QA execution plan completed; emulator QA and retest completed; final QA report exists; release dossier exists; human approval received; merge completed under protected branch policy |

## Tracker statuses

Full set (Medium/Large):

```text
New Idea → Task Classification → Needs Product Clarification → Ready for Requirements
→ Requirements Approved → Ready for Technical Discovery → Technical Plan Ready
→ Ready for Decomposition → Ready for Engineering → In Development → Developer Tests
→ PR Preparation → PR Review → (Needs Code Fix) → Ready for QA → QA In Progress
→ (QA Failed → QA Triage → Needs Requirements Update / Needs Test Plan Update → Ready for Retest)
→ Final QA Passed → Ready for Release Approval → Approved for Merge → Merged
→ Rollout Monitoring → Done
```

Simplified set (Small):

```text
Task Classification → Ready for Implementation → In Development → Review
→ Smoke QA → Approved for Merge → Merged → Done
```

Transition rules:

```text
Needs Product Clarification → must not pass to Technical Discovery.
Ready for Engineering → only after clear requirements and technical plan.
Ready for QA → only after PR review.
Ready for Release Approval → only after QA result and triage of all findings.
Approved for Merge → only after human approval and green CI.
```

## Post-QA decision catalogue

| Decision | When | Then |
|---|---|---|
| Needs Code Fix | code violates requirements | fix → review → retest |
| Needs Requirements Update | requirements incomplete/contested | update requirements → impact check → update plan/implementation → retest |
| Needs Test Plan Update | expected behavior in QA plan wrong | update QA plan → retest scenario |
| Environment Issue | fixtures/staging/test data broken | fix setup → rerun |
| Create Follow-up | real but non-blocking | linked ticket |
| No Action | behavior matches requirements | record rationale |
| Block Merge | high severity / data/security/crash/core flow | fix before merge |
| Needs Human Decision | product vs technical conflict | Human Owner decides |

## Technical Gate: three-axis plan review and PR-size split

Before the Technical Gate passes for Medium/Large, the technical plan goes through a three-axis review. Each axis is an independent pass/fail check; the plan does not advance to engineering until all three clear (or the gaps are explicitly accepted and recorded).

1. **Simplicity** — is the plan the most straightforward design that still meets every requirement? Flag accidental complexity: speculative abstractions, layers added "for later", new infrastructure where existing patterns suffice. Pass when the plan introduces no complexity that a reviewer cannot justify against a stated requirement.
2. **Convention adherence** — does the plan follow the active project's architecture, layering, naming, state-management, localization, repository, and CI conventions? Pass when no part of the plan fights established patterns without an approved deviation. Project-specific realization belongs in that project's own documented engineering guidance; do not duplicate it in this portable plugin.
3. **PR-size** — is the plan small enough to land as one reviewable PR? Pass when scope, file count, and change surface stay within a single coherent review. If it does not, the plan must be split (below).

These three checks are part of Definition of Ready for the engineering stage: a plan that fails any axis is **not Ready** and returns to technical discovery, not forward to `In Development`.

### Plan-too-large → split into part-N plans (human-approved)

When the PR-size axis fails, propose a split instead of forcing an oversized PR through. The split is a recommendation, never automatic:

1. **Propose, then wait.** Present the proposed split (the parts, their boundaries, and the merge order) and obtain explicit human approval before generating anything. Keeping the plan as a single PR is always a valid human choice.
2. **One standalone plan per part.** Each part is a complete plan at the same template and detail level as the original — title, type, acceptance criteria, tasks, and file references — so it can be built and reviewed on its own.
3. **Explicit Dependencies section.** Every part names which prior part(s) must merge first in a `## Dependencies` section. This is what makes the split safe to land incrementally under the Merge Gate's branch policy.
4. **Mark the original.** Annotate the original plan that it has been split and point to the parts, so no one builds from the superseded whole.

Each resulting part re-enters the gates independently: every `part-N` plan must clear the Technical Gate (all three axes) and DoR before its own engineering, and merges in dependency order — a later part is not Ready for merge until the parts it depends on have merged and passed their Merge Gate.
