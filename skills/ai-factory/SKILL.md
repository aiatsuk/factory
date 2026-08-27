---
name: ai-factory
description: "AI Factory plugin entrypoint: route any raw idea, task, ticket, bug, or feature request through mandatory Task Classification and then the matching Small / Medium / Large delivery flow with gates, QA loop, triage, and human-approved merge. Use when the user asks for AI Factory, factory delivery, risk-proportional task processing, task classification, or says phrases like 'прогони через фабрику', 'классифицируй задачу', 'factory classify', 'factory flow', or gives a raw idea and asks which process it needs."
---

# ai-factory - risk-proportional delivery factory

Use this skill when the user wants the whole AI Factory lifecycle, gives a raw idea without saying which process it needs, or is unsure which factory stage to run.

## Core idea

```text
First classify the task.
Then pick the right flow.
Then use each role in its strong zone.
```

Process is proportional to risk:

- Small tasks move fast.
- Medium features get real requirements, a tech plan, and emulator QA.
- Large features get the full product + technical + QA + release process.

Never strangle a small task with a heavyweight process. Never push a large feature through the short path without requirements, review, and QA.

## Roles (model-agnostic)

Stages are executed by roles, not by named models. **Never request or pin a specific model for any stage** — every stage inherits whatever model the invoking context already runs. A role is a perspective and an output contract.

| Role | Responsibility |
|---|---|
| **Product Brain** | product framing, requirements, UX behavior, business rules, product triage, release summaries |
| **Staff Engineer** | technical plans, architecture, decomposition, PR review, edge cases, QA planning, technical triage |
| **Implementation Engineer** | scoped implementation, tests, fixes, mass edits, PR descriptions |
| **QA Executor** | smoke QA, emulator runs, screenshots, logs, actual vs expected |
| **Critic** | adversarial pass over a stage artifact before its gate — contract in `factory-critic` |
| **Human Owner** | final product, technical, and release decisions; merge approval |

The Implementation Engineer never receives raw ideas ("make reactions"). It only receives small verifiable tasks with explicit rules, scope, and expected tests.

All roles are defined entirely inside this plugin: each stage states its role contract, and the Critic has its own skill. Run a role as a subagent with that contract when the runtime allows, otherwise inline. AI Factory has no dependencies on other plugins.

## Orchestration, parallelism, background work

The session running this skill is the **orchestrator**: it routes stages, enforces gates, merges results into artifacts, and delegates heavy work.

- **Delegate roles to subagents when the runtime provides them** (e.g. the Agent tool in Claude Code). Give each subagent one stage contract and the minimal inputs; it returns conclusions and artifact content, not raw file dumps. No subagent tool → run roles inline, sequentially.
- **Parallelize independent work inside a stage; never across a gate.** A gate is a hard barrier: nothing behind it starts before it passes — including "optimistic" work while waiting for human approval.
- **Launch independent subagents as one concurrent batch**, then collect all results before moving on. Good fan-out points:
  - research/discovery across modules, repos, or systems (classification, technical discovery);
  - independent child tasks at implementation — one subagent per task;
  - per-finding Product Review and Technical Review in the QA loop;
  - independent artifact drafting (PR description while tests run).
- **Isolate concurrent writers.** Child tasks that mutate files run in parallel only in isolated worktrees (or equivalent), merged in dependency order; tasks touching the same files run sequentially. Read-only fan-out needs no isolation.
- **Independence is semantic, not just file paths**: tasks sharing symbols, registries, DI containers, generated files, or lockfiles are NOT independent even when their file sets differ. On a merge conflict: serialize — re-run the later task against the merged base; if it still conflicts, escalate to the Staff Engineer instead of force-resolving.
- **Push long operations to the background early** and keep working: emulator/AVD boot, app builds and installs, dependency fetches, long test suites. Start them before they are needed (boot the emulator while the QA plan is being finalized). A stage that consumes a background job **blocks on it**: wait for completion, apply the one-retry rule on failure, then proceed or report the job as a blocker — never assume it succeeded.
- **Serial resources stay serial.** One emulator runs scenarios sequentially; parallelize QA only across multiple devices/AVDs, one executor per device.
- **Keep the orchestrator's context lean.** The orchestrator never bulk-reads code or logs itself when a subagent can summarize; it owns sequencing, gates, and artifact assembly.
- **Bounded retries, honest failures.** A failed subagent or background job is retried once with a sharper prompt/fix; after that it is reported as a blocker, never silently dropped or faked. The same applies to implementation itself: an unresolved build or test failure after the retry reopens the tech plan or stops as a blocker to the Human Owner — never advance to PR with undocumented red tests.
- **No model pinning anywhere** — subagents and background workers inherit the model from the invoking context, same as every stage.

## Stages

- `factory-classify` - mandatory first stage for any idea: scorecard, hard triggers, blocking questions, flow recommendation, escalation/downgrade rules.
- `factory-small` - Small Task Flow: quick requirement check, mini tech plan, implementation, tests, PR description, lightweight review, smoke QA, human approval.
- `factory-medium` - Medium Feature Flow: product clarification, final requirements, UX behavior spec, technical plan, decomposition, implementation, PR review, QA loop, human approval.
- `factory-large` - Large Feature Flow: full product discovery, requirements gate, UX spec, technical discovery, architecture, decomposition, implementation, PR review, QA test design, QA loop, release dossier, human approval, rollout monitoring.
- `factory-qa-loop` - QA execution plan, emulator QA, QA report, product + technical review of findings, triage decision, fix loops, retest, final QA report.
- `factory-release` - release dossier, human approval, merge gate, rollout monitoring.
- `factory-critic` - adversarial pass over any stage artifact before its gate (objections with severities, simpler alternative, gate question).
- `factory-gates` - gate rules, Definition of Ready/Done per flow, tracker statuses, post-QA decision types (reference).
- `factory-artifacts` - canonical artifact templates: classification, requirements, tech plan, QA plan, QA report, triage decision, release dossier (reference).

## Routing

- Raw idea, ticket, bug, or feature request with no classification yet: run `factory-classify` first. Always.
- Classification says Small: run `factory-small`.
- Classification says Medium: run `factory-medium`.
- Classification says Large: run `factory-large`.
- User asks only to classify: run `factory-classify` and stop.
- Build exists and user asks to verify it in the app: run `factory-qa-loop`.
- QA report exists and findings need decisions: run `factory-qa-loop` from its triage step.
- QA passed and user wants merge readiness: run `factory-release`.
- User asks about gates, statuses, or DoR/DoD: consult `factory-gates`.
- User asks for an artifact template: consult `factory-artifacts`.
- If during any flow new facts hit an escalation or downgrade trigger, re-run `factory-classify` and switch flows; carry finished artifacts forward.
- Resume an in-flight run: open its run folder, read `transcript.md` for the last completed stage and the recorded next action, continue from there; never redo completed artifacts.
- If requirements change mid-flight (even without a flow change), mark every artifact derived from the old requirement stale — tech plan, decomposition, QA plan — and re-validate each against the new requirement before proceeding.

## Artifact rules

- Every stage must produce a verifiable artifact, not just chat output.
- When file writes are allowed and `PRODUCT_WORK_ITEM_ROOT` is set by an explicit Product Workspace binding, resolve it as an absolute existing directory containing exactly one matching `project.json` or `ticket.json`, then create the run at `$PRODUCT_WORK_ITEM_ROOT/processes/factory/<YYYY-MM-DD-HHMM>-factory-<slug>/`. Never infer a work item from the current repository, ticket-like text, or the latest session. If the variable is set but invalid, stop and repair the binding instead of silently writing elsewhere.
- When `PRODUCT_WORK_ITEM_ROOT` is unset, preserve the standalone legacy behavior: create `meetings/<YYYY-MM-DD-HHMM>-factory-<slug>/` once per run.
- Keep all run artifacts in the resolved run folder: `transcript.md`, `classification.md`, `requirements.md`, `ux-spec.md`, `tech-plan.md`, `decomposition.md`, `build-log.md`, `pr-description.md`, `review.md`, `qa-test-design.md` (Large only), `qa-plan.md`, `qa-report.md`, `triage.md`, `retest.md`, `final-qa.md`, `release-dossier.md`, `rollout.md`.
- `transcript.md` is the run's state cursor: every stage appends its status, key decisions, and the exact next action. Clarification, intake, and discovery stages that have no dedicated file write their output here.
- In a Product Workspace, `transcript.md` remains the factory stage journal; it does not replace the separately captured full host-session transcript.
- In plan mode or when writes are not allowed, emit the same artifact content in chat and stop at the same gates.

## Boundaries

- Agents never merge. Final merge to main requires Human Owner approval and protected branch policy.
- Do not commit, push, open PRs, deploy, or transition tickets unless the user separately asks.
- Therefore a factory run terminates at **`Approved for Merge` / ready-for-merge**: opening the PR, running CI, and the merge itself happen outside the run, or inside it only on a separate explicit user request. The Merge Gate's CI/merge conditions are checked at merge time by whoever merges.
- Do not enter technical stages while blocking product questions are open: ask questions, record assumptions, separate blocking from non-blocking, and stop at the gate.
- A QA report is input for triage, never an automatic verdict.
- Do not pin models to stages; inherit the model from the invoking context.
- AI Factory is self-contained: do not route factory stages through other plugins' skills. Roles, the Critic, and the emulator QA runbook are all defined in `factory-*` skills and maintained here.
