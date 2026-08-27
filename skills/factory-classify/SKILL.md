---
name: factory-classify
description: "AI Factory mandatory first stage: classify a raw idea, task, ticket, or bug by size, risk, and uncertainty using a scorecard and hard triggers, then recommend Small, Medium, or Large flow with blocking questions and routing. Use for 'factory classify', 'классифицируй задачу', 'какой флоу нужен', new raw ideas entering AI Factory, or when an in-flight task hits an escalation or downgrade trigger and needs re-classification."
---

# factory-classify - task classification

Task Classification is the first mandatory stage for any idea entering AI Factory. No task may enter a flow without it.

Role: **Product Brain** leads, **Staff Engineer** checks the technical axes. Roles inherit the model from the invoking context — never pin one.

## Input

- Raw idea text (required).
- Optional context: product area, platform, screen, known constraints, design links, repo/module, current API/model assumptions, analytics requirements, rollout expectations.
- If the affected area is unclear, fan out short parallel read-only research subagents (one per candidate module/system) instead of scanning the repo serially; they return conclusions only.

## What to assess

| Axis | Question |
|---|---|
| Product complexity | are product decisions, rules, non-goals, metrics needed? |
| UX complexity | new states, loading/error/offline, responsive/dark mode? |
| Technical complexity | does it change API, DB, state management, architecture? |
| Integration complexity | client-only, or backend + client, old clients, cache? |
| Risk | data, auth, payments, privacy, crashes, sync, security? |
| QA complexity | smoke checklist enough, or full QA execution plan? |
| Rollout complexity | feature flag, staged rollout, monitoring, rollback? |
| Uncertainty | how many blocking questions; are assumptions safe? |

## Scorecard

Score each axis 0-2. The scorecard standardizes routing but never replaces judgement.

| Axis | 0 | 1 | 2 |
|---|---|---|---|
| Product | all clear | 1-3 clarifications | contested rules/scope |
| UX | local visual change | several UI states | new flow / many states |
| Technical | 1 module, client-only | several modules/state | API/DB/architecture |
| Integration | none | client + existing API | backend + client contract |
| Risk | low | medium | high / data/security/payment |
| QA | smoke enough | emulator QA needed | full QA loop + retest |
| Rollout | not needed | flag desirable | staged rollout required |
| Uncertainty | no blockers | open questions | cannot start without decisions |

Routing by total:

```text
0-5   → Small Task Flow
6-10  → Medium Feature Flow
11+   → Large Feature Flow
```

If blocking questions exist, the flow is assigned conditionally and the task first returns to clarification.

## Hard triggers

**Check hard triggers before scoring** — they short-circuit routing regardless of the sum, so a payments task scored 3 still goes Large.

Regardless of score, the task is **Large** if any apply: payments/billing; auth/permissions; security/privacy; user data migrations; new domain model; breaking API change; data-loss risk; multi-repo changes; mandatory staged rollout; high-risk production behavior.

The task is **at least Medium** if any apply: backend + client integration; new sync logic; complex client state; optimistic update; important edge cases; emulator QA mandatory; feature flag desirable.

## Escalation / downgrade

Classification is never final. Re-run this skill when new facts arrive.

- **Small → Medium**: API change surfaces; required state does not exist; backend sync needed; important edge cases appear; smoke QA is not enough; several modules touched; emulator QA with actual-vs-expected needed.
- **Medium → Large**: new domain model; migration needed; user data touched; staged rollout needed; privacy/security risks; full release dossier required; major product discovery needed; risk of breaking old clients.
- **Medium → Small**: API already supports the behavior; task turns out client-only; no new edge cases; changes are local; smoke QA is enough.

When switching flows, carry completed artifacts forward; do not redo finished stages.

## Output

Produce `classification.md` using the Task Classification template from `factory-artifacts`: title, task kind, recommended flow, classification status (Ready / Needs Clarification / Needs Technical Check), confidence, reason, scorecard with total, blocking questions, assumptions, conditional routing (if X → Small / Medium / Large), and recommended next step.

Rules:

- Separate blocking questions from non-blocking assumptions. A question is blocking if it changes acceptance criteria, QA, or API/state behavior.
- With unresolved blocking questions, status is `Needs Clarification`; do not hand the task to technical stages.
- Always state the conditional routing so the flow can flip as soon as answers arrive.

## Next

- Small → `factory-small`
- Medium → `factory-medium`
- Large → `factory-large`
- Needs Clarification → ask the blocking questions, then re-classify.
