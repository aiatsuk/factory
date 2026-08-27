---
name: factory-large
description: "AI Factory Large Feature Flow: full process for big or high-risk initiatives classified Large — product discovery, requirements gate, UX spec, technical discovery, architecture, decomposition, implementation, PR review, QA test design, emulator QA loop with product+technical triage, release dossier, human approval, merge, rollout monitoring. Use for 'factory large', new domain models, migrations, payments/auth/privacy work, staged rollouts, multi-repo changes, or anything hitting a Large hard trigger."
---

# factory-large - Large Feature Flow

Full process for initiatives classified Large by `factory-classify`: new product capability, several screens plus backend, new domain model, migrations, user data impact, feature flag / staged rollout, security/payment/auth/privacy risks.

Pipeline:

```text
Classification → Idea Intake → Product Discovery → Requirement Questions
→ Requirements Gate → Final Requirements → UX Behavior Spec
→ Technical Discovery → Architecture → Decomposition
→ Implementation → Developer Tests → PR Preparation → PR Review
→ QA Test Design → QA loop (factory-qa-loop)
→ Release Dossier → Human Approval → Merge → Rollout Monitoring
```

Stages run on whatever model the invoking context uses — never pin one.

## Product stages — Product Brain

Stages 1-4 record their output in `transcript.md`; dedicated files start at stage 5.

1. **Idea Intake** — accept the raw idea, ticket, screenshot, competitor example, or user request; produce draft title, draft goal, initial scope, initial risks.
2. **Product Discovery / Clarification** — why, for whom, what value; MVP scope, non-goals, open questions. With blocking questions open, the task never enters technical stages.
3. **Requirement Questions** — close uncertainties. Rule: a question that affects acceptance criteria, QA, or API/state behavior is blocking.
4. **Requirements Gate** — verdict `Requirements Approved` or `Needs Clarification`. Pass only if: clear goal; user story; business rules; acceptance criteria; non-goals; error/offline/unauthorized behavior defined; feature verifiable in QA; no unresolved blocking questions.
5. **Final Requirements** — final product spec → `requirements.md` (template in `factory-artifacts`), including analytics requirements and rollout assumptions; open questions must be `None`.
6. **UX / Behavior Spec** — UI states, transitions, error/offline behavior → `ux-spec.md`.

## Technical stages — Staff Engineer

7. **Technical Discovery** — affected systems, data model, API contract, client state model, cache strategy, migration strategy, compatibility, performance, security/privacy, observability, risks and mitigations → discovery report in `tech-plan.md`. Discovery across several systems/repos fans out to parallel read-only research subagents; the Staff Engineer merges their findings.
8. **Architecture / Technical Design** — fix the architectural decision as a design document appended to `tech-plan.md`; record alternatives rejected and why.
9. **Technical Decomposition** — parent task + child tasks + dependencies → `decomposition.md`. Each child task: title, area, scope, expected output, expected tests, dependencies, risk, definition of done. Check the Technical Gate (`factory-gates`).

## Engineering stages — Implementation Engineer

10. **Implementation** — execute child tasks against their DoD; never the raw feature → `build-log.md`. Independent child tasks (no shared files, no dependency edges) run as parallel implementation subagents in isolated worktrees, merged in dependency order; dependent or file-sharing tasks run sequentially.
11. **Developer Tests** — automated tests per requirements and risks; record results. Long suites run in the background while PR preparation is drafted.
12. **PR Preparation** — PR title, summary, tests, risks, checklist → `pr-description.md`.

## Review — Staff Engineer

13. **PR Review** — correctness, architecture consistency, tests, risks; verdict approve / request changes / needs human → `review.md`. `factory-critic` attacks the diff before the verdict. PR Review Gate must pass before QA.

## QA stages

14. **QA Test Design** — Staff Engineer derives the full test-case set with edge cases from requirements + UX spec + tech design + PR review → `qa-test-design.md`.
15. **QA loop** — run `factory-qa-loop`: QA execution plan → emulator QA → QA report → product review + technical review per finding → triage decisions → fix / requirements / test-plan / environment loops → retest → final QA report. Repeat until final QA is passed or explicitly blocked.

## Release stages

16. **Release Dossier → Human Approval → Merge → Rollout Monitoring** — run `factory-release`. Human Owner makes the final call; merge only under protected branch policy; monitor rollout and open follow-ups or incident loops.

## Done when

Product discovery completed; requirements approved; UX spec ready; technical design approved; feature decomposed into implementation-ready tasks; all child tasks completed; tests and PR reviews done; QA test design and execution plan completed; emulator QA and retest completed with evidence; product + technical triage completed; final QA passed; release dossier ready; rollout/rollback/monitoring plan known; human approval received; PR merged; rollout monitored.
