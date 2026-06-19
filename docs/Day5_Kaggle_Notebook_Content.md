# Day 5 – Spec-Driven Production Grade Development

> Ready-to-paste Kaggle notebook markdown for the **Kaggle AI Agents Intensive**
> final assignment, connected to the **IPRMS – Intelligent Purchase Requisition
> Management System** capstone project.

---

## Overview

Day 5 of the AI Agents Intensive focuses on **Spec-Driven Production Grade
Development in the Age of Vibe Coding** — moving from quick, code-as-truth
prototyping toward systems where specifications, configs, schemas, tests, and audit
artifacts are the real source of truth.

The Day 5 codelab builds an **Expense Agent** on Google Cloud: an event-driven agent
that receives an expense, checks it against a threshold, auto-approves small amounts,
escalates larger ones to a manager, and records logs/traces for observability.

This notebook summarizes the whitepaper and codelab concepts and shows how my
capstone, **IPRMS**, already applies the same production pattern — locally and
deterministically.

---

## Whitepaper Summary

The Day 5 material argues that "vibe coding" (letting the running code define
behavior) does not scale to production. Production-grade agentic systems need:

- **Specifications as the source of truth** — behavior is defined in specs, configs,
  and schemas, not improvised in code.
- **Determinism and reproducibility** — the same input produces the same output.
- **Policy-based decisions** — thresholds and routing rules are explicit and
  versioned.
- **Human-in-the-loop escalation** — agents auto-handle the safe cases and escalate
  the rest.
- **Auditability and observability** — every decision is logged and traceable.

The Expense Agent codelab demonstrates these principles end-to-end on a cloud
runtime with Pub/Sub events, an agent runtime, a manager dashboard, and Cloud
logging/tracing.

---

## Key Concepts Learned

- **Spec-driven development (SDD):** specs, configs, schemas, tests, and audit
  artifacts — not code — are authoritative.
- **Event-driven input:** work is triggered by an event (e.g. a submission) rather
  than a manual run.
- **Deterministic agent pipeline:** decision logic is rule-based and reproducible.
- **Policy-based routing:** thresholds decide auto-approval vs. escalation.
- **Human-in-the-loop:** reviewers handle exceptions through a dashboard.
- **Auditability & observability:** logs, traces, and metrics make every decision
  explainable.

---

## Optional Codelabs Review

The Day 5 optional **Google Cloud deployment codelabs** (Expense Agent on the cloud
runtime, Pub/Sub wiring, and manager dashboard deployment) were **reviewed and
studied** to understand the production architecture and the mapping to IPRMS.

I walked through the codelab steps and architecture diagrams to extract the pattern:
event → agent runtime → threshold decision → auto-approve or human review →
logging/observability.

---

## Billing Note

> ⚠️ **The optional Google Cloud deployment codelabs were reviewed but NOT
> executed**, because they require a **billing-enabled Google Cloud project**
> (Cloud Run / agent runtime, Pub/Sub, and logging services can incur charges).
>
> No Google Cloud deployment was attempted and no billing-enabled services were
> created. Instead, IPRMS demonstrates the **same Day 5 production pattern locally**:
>
> - event-driven input concept (PR submitted event),
> - deterministic agent pipeline (agents A–H),
> - policy-based routing (`routing_rules.json`),
> - human-in-the-loop escalation (FP&A / Procurement / Legal review),
> - auditability (`audit_log`, `evidence_index`),
> - and observability (`metrics`).

---

## IPRMS Mapping

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

## IPRMS Spec-Driven Development Artifacts

In IPRMS, code is not the source of truth. These versioned artifacts are:

- `configs/policy_pack.yaml` — business policies, thresholds, required reviews.
- `configs/routing_rules.json` — deterministic exception routing.
- `configs/tolerance_settings.json` — numeric tolerances for budget/price/matching.
- **Pydantic schemas** (`schemas/`) — strict data contracts; invalid data is rejected.
- **pytest tests** (`tests/`) — executable specification of expected behavior.
- **PR bundle `manifest.yaml`** — declared contents and provenance of each bundle.
- **Audit artifacts** — `audit_log`, `evidence_index`, `metrics`.
- **Gherkin scenarios** — `features/pr_processing.feature`.

**Determinism guarantee:** *same input bundle + same configs = same outputs.*

LLMs, LangChain, or LangGraph may assist with extraction and orchestration, but every
**final business decision** (budget, vendor, bid-threshold, sole-source, split-order,
routing) is made by deterministic, rule-based logic.

---

## IPRMS Production Architecture

```
PR submission (bundle + manifest.yaml, "PR submitted" event)
        │
        ▼
IPRMS pipeline (LangGraph orchestration)
        │
        ▼
Agents A → H
  A Intake & Context     E Policy Compliance
  B PR Extraction        F Sole-Source / Bid
  C Budget Validation    G Split-Order / Anomaly
  D Vendor Matching      H Exception Triage
        │
        ▼
Deterministic checks (policy_pack / routing_rules / tolerance_settings)
        │
        ├──────────────► PO draft (auto-approved)
        │
        └──────────────► Exception route (FP&A / Procurement / Legal)
        │
        ▼
Audit artifacts (audit_log / evidence_index / metrics)
        │
        ▼
Dashboard / monitoring (exception review dashboard)
```

---

## Final Reflection

Day 5 reframed how I think about building agentic systems: the goal is not just code
that runs, but a system whose behavior is **defined by specifications and reproducible
by design**. The Expense Agent codelab showed the cloud-native version of this
pattern, while IPRMS demonstrates that the *same discipline* — event-driven input,
deterministic agents, policy-based routing, human-in-the-loop escalation, audit, and
observability — can be implemented locally and deterministically, without any cloud
billing.

By mapping the Day 5 Expense Agent onto IPRMS, I confirmed that my capstone already
embodies spec-driven, production-grade development: specs and configs are the source
of truth, every decision is auditable, and the core pipeline stays deterministic.
