# IPRMS – Spec-Driven Development

This document explains how the **Intelligent Purchase Requisition Management System
(IPRMS)** follows **Spec-Driven Development (SDD)**, and how it maps to the Day 5
Kaggle AI Agents Intensive theme:
*"Spec-Driven Production Grade Development in the Age of Vibe Coding."*

---

## 1. Why IPRMS is Spec-Driven

In "vibe coding," the running code is treated as the source of truth: behavior is
whatever the latest edit happens to produce. IPRMS deliberately rejects that model.

**In IPRMS, code is *not* the source of truth.** Code is an *executor* of decisions
that are defined elsewhere. The authoritative definition of correct behavior lives in
versioned specifications, configurations, schemas, policies, tests, and audit
artifacts. If the code and a spec disagree, the spec wins and the code is treated as
a defect.

This makes the system **auditable** (every decision traces back to a written rule)
and **reproducible** (the same inputs and specs always yield the same outputs).

---

## 2. Source-of-Truth Artifacts

The following artifacts — not the code — define what IPRMS is allowed to do:

| Artifact | Role as source of truth |
| --- | --- |
| `configs/policy_pack.yaml` | Business policies: approval rules, thresholds, required reviews, compliance gates. |
| `configs/routing_rules.json` | Deterministic routing: which exceptions go to FP&A, Procurement, or Legal. |
| `configs/tolerance_settings.json` | Numeric tolerances for budget, price variance, and matching confidence. |
| **Pydantic schemas** (`schemas/`) | Strict data contracts for PR bundles, line items, and agent outputs. Invalid data is rejected, not guessed. |
| **pytest tests** (`tests/`) | Executable specification of expected behavior for each agent and the full pipeline. |
| **PR bundle `manifest.yaml`** | Declares the contents and provenance of each input bundle. |
| **Audit artifacts** (`audit_log`, `evidence_index`, `metrics`) | Immutable record of what happened and why, for every run. |
| **Gherkin scenarios** (`features/pr_processing.feature`) | Human-readable behavior specs describing intended pipeline outcomes. |

Because these artifacts are versioned, a change in behavior **requires a change in a
spec**, reviewed through normal source control — not an undocumented code tweak.

---

## 3. Deterministic Design

IPRMS is built on a single guarantee:

> **Same input bundle + same configs = same outputs.**

Given an identical PR bundle and an identical set of policy/routing/tolerance configs,
the pipeline produces byte-stable decisions, the same PO draft (or the same exception
route), and the same audit trail. There is no hidden randomness in the decision path.

This determinism is what makes the system testable and auditable: a reviewer can
re-run any historical bundle against its configs and reproduce the original outcome
exactly.

---

## 4. Role of LLMs / LangChain / LangGraph

IPRMS may use **LLMs, LangChain, or LangGraph** to *support* the pipeline — for
example, to help extract structured fields from messy documents (Agent B) or to
orchestrate the flow of agents (Agent H).

However, these components are **assistive, not authoritative**:

- LLMs may *propose* extracted values; Pydantic schemas validate them and reject
  anything malformed or low-confidence.
- Orchestration may be expressed in LangGraph; the *decisions* inside each node are
  deterministic, rule-based checks driven by the config artifacts.
- **Final business decisions** — approve/route, budget pass/fail, vendor preference,
  bid-threshold, sole-source, split-order — are always made by deterministic rules,
  never by a probabilistic model.

This keeps the "intelligent" parts of IPRMS confined to perception and routing
assistance, while every outcome that affects money or compliance remains
reproducible and explainable.

---

## 5. Day 5 → IPRMS Mapping

The Day 5 Expense Agent codelab concepts map directly onto IPRMS concepts:

| Day 5 Expense Agent concept | IPRMS concept |
| --- | --- |
| Expense submission | Purchase Requisition (PR) bundle |
| Amount threshold | Budget / bid threshold |
| Auto-approval | Auto PO draft |
| Manager review | FP&A / Procurement / Legal review |
| Pub/Sub event | PR submitted event |
| Agent Runtime | IPRMS pipeline / LangGraph orchestration |
| Manager dashboard | Exception review dashboard |
| Cloud logs / traces | `audit_log`, `evidence_index`, `metrics` |

---

## 6. Production-Grade Architecture

IPRMS implements the same production pattern taught in Day 5, locally and
deterministically:

```
            ┌─────────────────────┐
            │   PR submission     │  (PR bundle + manifest.yaml)
            │  "PR submitted"     │  event-driven input concept
            └──────────┬──────────┘
                       │
                       ▼
            ┌─────────────────────┐
            │   IPRMS pipeline    │  (LangGraph orchestration)
            └──────────┬──────────┘
                       │
                       ▼
   ┌───────────────────────────────────────────────┐
   │  Agents A → H                                   │
   │   A Intake & Context     E Policy Compliance    │
   │   B PR Extraction        F Sole-Source / Bid    │
   │   C Budget Validation    G Split-Order/Anomaly  │
   │   D Vendor Matching      H Exception Triage     │
   └──────────────────────┬────────────────────────┘
                          │
                          ▼
            ┌─────────────────────┐
            │ Deterministic checks │  (policy_pack / routing_rules /
            │  rule-based decision │   tolerance_settings)
            └──────────┬──────────┘
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
 ┌─────────────────┐      ┌──────────────────────┐
 │   PO draft      │      │  Exception route      │
 │ (auto-approved) │      │ (FP&A/Procurement/Legal)
 └────────┬────────┘      └──────────┬───────────┘
          │                          │
          └────────────┬─────────────┘
                       ▼
            ┌─────────────────────┐
            │   Audit artifacts    │  audit_log / evidence_index / metrics
            └──────────┬──────────┘
                       ▼
            ┌─────────────────────┐
            │ Dashboard / monitor  │  Exception review dashboard
            └─────────────────────┘
```

**Flow summary:** PR submission → pipeline → agents A–H → deterministic checks →
PO draft *or* exception route → audit artifacts → dashboard / monitoring.

This mirrors the Day 5 cloud reference architecture (event → agent runtime →
threshold decision → auto-approve or human review → logging/observability) while
keeping IPRMS fully deterministic and runnable without any cloud billing.
