---
name: factory-release
description: "AI Factory release stage: assemble the release dossier from requirements, PR, review, and QA artifacts, run the merge gate checklist, obtain human approval, and set up rollout monitoring with follow-up or incident loops. Use for 'factory release', 'prepare the release dossier', merge readiness checks, 'можно ли мержить', post-QA approval requests, or rollout monitoring after a factory merge."
---

# factory-release - dossier, approval, merge, rollout

Closing stage for Medium and Large factory flows, after `factory-qa-loop` records the final QA status.

```text
Release Dossier → Human Approval → Merge → Rollout Monitoring
```

Stages run on whatever model the invoking context uses — never pin one.

## 1. Release Dossier — Product Brain

- Input: requirements + PR + review + final QA + known risks.
- Output → `release-dossier.md` (template in `factory-artifacts`): included / not included, backend changes, client changes, API changes, migrations/config, feature flags, QA status, known risks, known issues, monitoring, rollback plan, release notes, decision (Ready / Not Ready / Needs Human Decision).
- The dossier must be readable by the Human Owner in minutes: what ships, what does not, what can break, how to roll back.

## 2. Human Approval — Human Owner

- Input: release dossier + PR + CI status + final QA report.
- Output: approved / not approved. Not approved → return the task to the exact stage named in the decision (fix, requirements, QA, or dossier).
- Agents prepare everything; only the Human Owner approves.

## 3. Merge — Human / protected branch policy / CI

Merge Gate (`factory-gates`) — merge is allowed only if:

```text
- PR approved;
- CI green;
- final QA passed, or accepted with explicit non-blocking issues;
- release dossier ready (Medium/Large);
- human approval received;
- rollback understood where needed.
```

Agents never merge. Do not commit, push, or transition tickets unless the user separately asks.

## 4. Rollout Monitoring

- Input: metrics, logs, crashes, user feedback after merge/release.
- Product Brain writes the rollout summary; Staff Engineer handles incident analysis.
- Output → `rollout.md`: rollout report and follow-up tasks, or an incident/fix loop back into the appropriate flow (`factory-classify` the incident if its scope is unclear).
- Done only when rollout is stable and follow-ups are filed.
