---
name: factory-qa-loop
description: "AI Factory QA loop: build a QA execution plan, run emulator QA with evidence, write the QA report, review every finding from product and technical sides, make triage decisions, run fix/requirements/test-plan/environment loops, retest, and record the final QA status. Use for 'factory qa', 'run the QA loop', emulator QA of a factory build, triaging QA findings, retest requests, or when a QA report needs product/technical verdicts instead of blind fixes."
---

# factory-qa-loop - QA execution, report, triage, retest

QA loop for Medium and Large factory flows (Small uses its own smoke QA). Core rule: **a QA report records actual behavior; it is input for triage, never an automatic verdict.** Failed scenarios are never fixed blindly.

```text
QA Execution Plan → Emulator QA → QA Report
→ Product Review + Technical Review of findings
→ Triage Decision per finding
→ Fix / Requirements / Test Plan / Environment loop
→ Retest → Final QA Report
```

Stages run on whatever model the invoking context uses — never pin one.

## 1. QA Execution Plan — Staff Engineer

- Input: requirements + UX spec + PR review + known risks. For Large, also the QA test design (`qa-test-design.md`); Medium has no separate test-design stage — the execution plan subsumes test-case design, do not wait for or duplicate that artifact.
- Output → `qa-plan.md` (template in `factory-artifacts`): feature, change description, what changed, preconditions, environment, test accounts, setup steps, test data, scenarios with steps/expected/evidence required, edge cases, pass criteria, fail criteria.
- Every scenario must state the evidence required (screenshots, logs) and unambiguous expected behavior.

## 2. Emulator QA — QA Executor

- Input: build + QA plan + emulator + test account.
- Start the slow parts **in the background early**: boot the AVD and build/install the app while step 1 finalizes the plan, then collect them here.
- Walk the scenarios in the running app; for each capture starting state, execute steps, capture evidence, mark pass / fail / blocked / not run, record expected vs actual.
- One device is a serial resource: scenarios on it run sequentially. With several AVDs available, split scenario groups across devices — one QA Executor subagent per device, results merged into one report.
- Execute through the adb runbook below. It is self-contained and maintained inside AI Factory; the loop has no dependencies on other plugins.
- The runbook is **Android-specific**. For backend-only, web, or other non-Android scope there is no emulator pass: verify through automated tests plus an API/manual smoke checklist, mark emulator scenarios `not applicable` in the report, and say so honestly — never fake a device run.
- Evidence layout inside the run folder: `screenshots/`, `ui-trees/`, `logcat.txt`.

### adb runbook

```bash
adb devices                                                 # pick <serial>; if empty:
$ANDROID_HOME/emulator/emulator -list-avds                  # then start one in the background:
$ANDROID_HOME/emulator/emulator -avd <name> &
adb -s <serial> wait-for-device shell \
  'while [ "$(getprop sys.boot_completed)" != "1" ]; do sleep 2; done'   # wait for full boot
adb -s <serial> install -r <path-to-apk>                    # install the build under test
adb -s <serial> shell cmd package resolve-activity --brief <package>
adb -s <serial> shell am start -n <package>/<activity>      # launch app
adb -s <serial> exec-out uiautomator dump /dev/tty > ui-trees/<step>.xml
                                                            # strip the trailing "UI hierchary dumped..." line before XML parsing
adb -s <serial> shell input tap <x> <y>                     # center of bounds="[x1,y1][x2,y2]"
adb -s <serial> shell input swipe <x1> <y1> <x2> <y2>       # scroll; keep ~150-200px off edges
adb -s <serial> shell input text "hello%sworld"             # type; spaces must be escaped as %s
adb -s <serial> shell input keyevent 4                      # back
adb -s <serial> exec-out screencap -p > screenshots/<step>.png
adb -s <serial> logcat -c                                   # clear before a scenario
adb -s <serial> logcat -d > logcat.txt                      # save after; crashes: logcat -b crash
```

Rules:

- Derive tap coordinates from the UI tree dump, never from screenshots.
- If a target node is missing and scrollable elements exist: swipe, re-dump, re-search at least once before concluding it is missing.
- Never fake execution. No emulator, build, or test account → mark the scenarios `blocked` and report the blocker.

## 3. QA Report — QA Executor, formatted by Product Brain

- Output → `qa-report.md` (template in `factory-artifacts`): build, environment, totals (passed/failed/blocked), failed scenarios with expected vs actual + evidence + severity + likely area, blocked scenarios, known limitations, recommendation (ready for triage / ready for approval / not ready).

## 4. Per-finding review

| Review | Role | Question |
|---|---|---|
| Product Review | Product Brain | does actual behavior violate requirements, or are requirements incomplete/contested? |
| Technical Review | Staff Engineer | code bug, test plan issue, environment issue, or acceptable limitation? what area, what severity? |

The two reviews are independent perspectives — run them **in parallel**, and batch per-finding reviews concurrently (one subagent per review when the runtime allows). Triage waits for both verdicts on a finding.

## 5. Triage Decision — Product Brain + Staff Engineer, Human if needed

For each finding pick exactly one decision → `triage.md` (template in `factory-artifacts`):

| Decision | When | Then |
|---|---|---|
| Needs Code Fix | code violates requirements | Implementation Engineer fixes → Staff Engineer reviews → retest |
| Needs Requirements Update | requirements incomplete or contested | Product Brain updates → Staff Engineer checks impact → QA plan updated → implementation updated if needed → retest |
| Needs Test Plan Update | expected behavior in QA plan is wrong | update QA plan → retest corrected scenario |
| Environment Issue | fixtures, staging, test data broken | fix setup → rerun scenario |
| Create Follow-up | real but non-blocking | linked follow-up ticket |
| No Action | behavior matches requirements | record rationale |
| Block Merge | high severity / data/security/crash/core flow | fix required before merge |
| Needs Human Decision | product and technical verdicts conflict | Human Owner decides |

Each triage record: finding, product verdict, technical classification, severity (Low/Medium/High/Critical), decision, owner, required action, retest required, next status.

Fixes for independent findings may run as parallel subagents under the same worktree-isolation rules as implementation; retest then batches all fixed scenarios in one run.

## 6. Retest — QA Executor

- Input: updated build + failed scenarios + updated QA plan.
- Re-run fixed scenarios plus adjacent regression checks; capture evidence → `retest.md`.
- New or surviving findings → back to triage.
- **Loop bound:** if the same finding survives two retest cycles, or a fix introduces a new finding of equal or higher severity, stop looping — escalate it as `Needs Human Decision` and record the history in `triage.md`. Never grind the loop hoping it converges, and never mark `passed` to escape it.

## 7. Final QA Report

- Consolidate original report + retests → `final-qa.md`: final status `passed` or `blocked`, with outstanding non-blocking issues listed explicitly.
- QA Gate (`factory-gates`): the task may go to approval only when the QA plan is executed, failed scenarios triaged, blockers fixed, retest done, and the final report exists.

## Next

- Final QA **passed** (or accepted with explicit non-blocking issues) → `factory-release` for the Medium/Large dossier and approval.
- Final QA **blocked** → report the blockers to the Human Owner with the triage history; the task returns to the stage each blocker's triage decision names, or stops if the Human Owner halts it.
