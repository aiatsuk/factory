# AI Factory

AI Factory is a self-contained, risk-proportional delivery plugin. It classifies raw ideas, tasks, tickets, bugs, and features, then routes work through a Small, Medium, or Large flow with explicit artifacts, gates, QA, adversarial review, and human approval.

## Included skills

- `ai-factory` — entry point and flow router.
- `factory-classify` — mandatory scorecard and flow selection.
- `factory-small`, `factory-medium`, `factory-large` — delivery flows.
- `factory-artifacts`, `factory-gates` — artifact templates and gate rules.
- `factory-critic` — adversarial review contract.
- `factory-qa-loop`, `factory-release` — QA and release stages.

The bundle has no scripts, lifecycle hooks, MCP servers, or runtime services. It runs on the host's active model and does not pin models.

## Use

Install the repository with your host's normal plugin workflow. The root contains a Codex manifest in `.codex-plugin/plugin.json` and a Claude-compatible manifest and marketplace entry in `.claude-plugin/`.

Invoke `$ai-factory`, or ask naturally to classify a task, select a delivery flow, run factory QA, prepare a release dossier, or review an artifact adversarially.

## Canonical version and updates

Use this repository as the canonical public source. [ai-factory.json](./ai-factory.json) is the machine-readable update contract: it names the current version, release tag, supported entry points, and exact version locations that must change together. `main` is the latest public source; `v<version>` tags are immutable releases.

## Public-package policy

This public bundle includes all current AI Factory skills. Two project-local references were generalized so the plugin remains self-contained: project-specific architecture conventions are supplied by the active project, and merge rules refer to its protected-branch workflow and CI.

No license is included because the original source did not specify one.
