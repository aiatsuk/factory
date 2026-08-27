---
name: factory-artifacts
description: "AI Factory reference: canonical artifact templates — task classification, final requirements, technical plan, PR description, QA execution plan, QA report, triage decision, release dossier. Use when any factory stage needs to emit its artifact, when checking an artifact for completeness, or when the user asks for a factory template."
---

# factory-artifacts - canonical templates

Every factory stage must end in a verifiable artifact. Use these templates verbatim; drop a section only when it is genuinely not applicable and say so.

## Task Classification

```text
Task Classification

Title:

Task kind:
Feature / Bug / Tech debt / UX polish / Analytics / QA / Release

Recommended flow:
Small Task Flow / Medium Feature Flow / Large Feature Flow

Classification status:
Ready / Needs Clarification / Needs Technical Check

Confidence:
High / Medium / Low

Reason:

Scorecard:
- Product complexity:
- UX complexity:
- Technical complexity:
- Integration complexity:
- Risk:
- QA complexity:
- Rollout complexity:
- Uncertainty:
Total:

Blocking questions:
1.

Assumptions:
1.

Routing:
If ... → Small
If ... → Medium
If ... → Large

Recommended next step:
```

## Final Requirements

```text
Final Requirements

Feature:

Goal:

User story:

MVP scope:

Business rules:
1.

Acceptance criteria:
1.

Non-goals:
-

Analytics:
-

Error/offline/unauthorized behavior:

Open questions:
None / list

Recommended next status:
Ready for Technical Discovery
```

## Technical Plan

```text
Technical Plan

Affected systems:

Proposed approach:

Backend impact:

Client impact:

API/state impact:

Data/migration impact:

Caching/offline impact:

Performance considerations:

Security/privacy considerations:

Risks:
1.

Mitigations:
1.

Expected tests:

Recommended next status:
Ready for Decomposition / Ready for Implementation
```

## PR Description

```text
PR Title:

Summary:
-

Tests:
-

Risks:
-
```

## QA Execution Plan

```text
QA Execution Plan

Feature:

Change description:

What changed:

Preconditions:

Environment:

Test accounts:

Setup:
1.

Test data:

Scenarios:

Scenario 1:
Name:
Steps:
1.
Expected:
Evidence required:

Edge cases:

Pass criteria:

Fail criteria:
```

## QA Report

```text
QA Execution Report

Feature:

Build:

Environment:

Summary:
- Total scenarios:
- Passed:
- Failed:
- Blocked:

Failed scenarios:

1. Scenario name
Expected:
Actual:
Evidence:
Severity:
Likely area:

Blocked scenarios:

Known limitations:

Recommendation:
Ready for triage / Ready for approval / Not ready
```

## Triage Decision

```text
Triage Decision

Finding:

Product verdict:

Technical classification:
Code bug / Requirements issue / Test plan issue / Environment issue / Non-blocking / Needs human

Severity:
Low / Medium / High / Critical

Decision:
Needs Code Fix / Needs Requirements Update / Needs Test Plan Update / Environment Issue / Create Follow-up / No Action / Block Merge / Needs Human Decision

Owner:

Required action:

Retest required:
Yes / No

Next status:
```

## Release Dossier

```text
Release Dossier

Feature:

Included:

Not included:

Backend changes:

Client changes:

API changes:

Migrations/config:

Feature flags:

QA status:

Known risks:

Known issues:

Monitoring:

Rollback plan:

Release notes:

Decision:
Ready / Not Ready / Needs Human Decision
```
