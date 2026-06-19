# IPRMS - Intelligent Purchase Requisition Management System

IPRMS is a **standalone, deterministic, Python-based 8-agent system** for processing Purchase
Requisitions (PRs). For every PR bundle it validates budget and vendor data, applies a
configurable **policy pack**, detects procurement risks and anomalies, routes exceptions, and
generates ERP-ready PO drafts together with a full set of **JSON / Markdown / CSV audit
artifacts**.

The system runs entirely on a local machine (or a single Docker container). 

> **Scope:** Purchase Requisition handling only. Invoice handling, invoice-to-PO matching, and
> GRN (Goods Receipt Note) matching are explicitly

---

## Table of contents

1. [Quick start](#1-quick-start-for-the-mentor)
2. [What the system does](#2-what-the-system-does)
3. [Prerequisites](#3-prerequisites)
4. [Installation](#4-installation)
5. [Running the pipeline (CLI)](#5-running-the-pipeline-cli)
6. [Running the demo UI (Streamlit)](#6-running-the-demo-ui-streamlit)
7. [Running the API (FastAPI)](#7-running-the-api-fastapi)
8. [Running with Docker (optional)](#8-running-with-docker-optional)
9. [Running the tests](#9-running-the-tests)
10. [Built-in demo scenarios](#10-built-in-demo-scenarios)
11. [Run artifacts](#11-run-artifacts)
12. [Configuration - the single source of truth](#12-configuration--the-single-source-of-truth)
13. [Architecture & design guarantees](#13-architecture--design-guarantees)
14. [Repository structure](#14-repository-structure)

---

## 1. Quick start

A reviewer can verify the project with the following commands from the repository root:

```bash

python -m venv .venv
.venv\Scripts\Activate.ps1                  

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the full test suite (expect: 170 passed)
pytest -q

# 4. Launch the interactive demo UI
streamlit run app/streamlit_app.py
```

The Streamlit UI opens in the browser. Pick any bundle/scenario from the dropdown, click
**Run pipeline**, and inspect the decision, approval packet, exceptions, PO draft, audit log,
metrics and all generated artifacts. Tick **LangGraph engine** to re-run the same PR through
the LangGraph skeleton and confirm the output is identical.

---

## 2. What the system does

Each PR bundle flows through a fixed, deterministic sequence of eight agents (A -> H) plus an
ERP/tracker stub:

| Agent | Responsibility | Key output(s) |
|-------|----------------|---------------|
| **A** | Intake & Context / Gatekeeper (manifest validation, PR-type, idempotency hash) | `context_packet.json`, `evidence_index.json` |
| **B** | Item / PR field extraction (digital PDF + JSON, per-field confidence & bounding boxes) | `extracted_pr.json` |
| **C** | Budget validation against the cost-center snapshot | `budget_check.json` |
| **D** | Vendor matching & catalogue pricing | `vendor_match.json` |
| **E** | Compliance, approval thresholds & complex-procurement flags | `policy_check.json` |
| **F** | Sole-source & bid-threshold checks | `sole_source_check.json`, `bid_threshold_check.json` |
| **G** | Split-order & anomaly detection (historical PRs) | `anomaly_report.json` |
| **H** | Exception triage, final decision & orchestration | `exceptions.md`, `approval_packet.json`, `po_draft.json`, `audit_log.md`, `metrics.json`, `run_summary.csv` |

The **final decision** is one of: `auto_po`, `auto_approve`, `manual_approval`,
`manual_review`, `buyer_clarification`, `expedited_approval`, `exception`, `blocked`.

---

## 3. Prerequisites

- **Python 3.11 or newer.** Recommended: Python 3.12, which was used for development and verification.
- **pip** and the ability to create a virtual environment (`venv`).
- *(Optional)* **Docker**, only if you prefer the containerized demo.
- *(Optional)* **Tesseract OCR**, only if you want to process *scanned* PDFs. Digital-PDF
  parsing (PyMuPDF / pdfplumber) needs no system dependency.

No external services, databases, API keys, or cloud accounts are required for the core system.

---

## 4. Installation

```bash

python -m venv .venv
.venv\Scripts\Activate.ps1                  

# 2. Install all dependencies
pip install -r requirements.txt

# 3. configure local environment 
copy .env.example .env                            

# 4. Verify the install
python -c "import pandas, pydantic, yaml, fitz, fastapi, streamlit, pytest; print('IPRMS deps OK')"
```

> The optional `.env` file is **not** needed to run or demo the project. The deterministic core
> runs fully without it, and decisions are identical whether the LLM fallback is enabled or not.

---

## 5. Running the pipeline (CLI)

The official execution flow is the deterministic Python runner:

```bash
python pipelines/run_iprms_pipeline.py --bundle data/pr_bundles/pr_bundle_001
```

Available options:

| Flag | Description |
|------|-------------|
| `--bundle <path>` | **(required)** Path to a PR bundle folder (must contain `manifest.yaml`). |
| `--run-id <id>` | *(optional)* Use an explicit run id instead of an auto-generated one. |
| `--langgraph` | *(optional)* Execute through the LangGraph skeleton instead of the direct path. Output must be identical. |

Example - run a scenario through the LangGraph engine:

```bash
python pipelines/run_iprms_pipeline.py --bundle data/pr_bundles/scenario_05_emergency_sole_source --langgraph
```

Typical console output:

```
[IPRMS] run_id=RUN-20260618T150433Z-c3d29a46
[IPRMS] run_dir=.../runs/RUN-20260618T150433Z-c3d29a46
[IPRMS] decision=auto_po  po_status=ready_for_posting
[IPRMS] erp_status=simulated_post_success  exceptions=0
[IPRMS] engine=direct Python
```

All artifacts for the run are written under `runs/<run_id>/` (see
[Run artifacts](#11-run-artifacts)).

---

## 6. Running the demo UI (Streamlit)

The Streamlit app is the recommended way to demonstrate the project:

```bash
streamlit run app/streamlit_app.py
```

It opens at **http://localhost:8501**. From the UI you can:

- Select any PR bundle / scenario from the dropdown.
- See live `manifest.yaml` validation.
- Click **Run pipeline** and view: the decision header (Decision / PO status / Routed to /
  ERP), the approval packet, exceptions, PO draft, audit log, metrics, tracker payload,
  `run_summary.csv`, and the complete list of generated artifacts.
- Toggle **LangGraph engine** to re-run the same PR through the LangGraph skeleton and confirm
  the result matches the direct pipeline.

---

## 7. Running the API (FastAPI)

```bash
uvicorn api.main:app --reload
```

The API serves at **http://localhost:8000**. Interactive Swagger docs are at
**http://localhost:8000/docs**.

| Method | Endpoint | Purpose |
|--------|----------|---------|
| `POST` | `/run-pr` | Run a PR bundle. Body: `{"bundle_dir": "...", "use_langgraph": false}` |
| `GET`  | `/runs/{run_id}` | Run summary (decision, routing, input hash, exceptions) |
| `GET`  | `/runs/{run_id}/decision` | Full approval packet |
| `GET`  | `/runs/{run_id}/artifacts` | List of artifacts for the run |
| `GET`  | `/runs/{run_id}/audit-log` | Audit log (Markdown, plain text) |
| `GET`  | `/runs/{run_id}/summary` | Validated run summary |
| `GET`  | `/metrics` | Aggregate metrics across all runs |

Example - run a bundle and read back its decision:

```bash
curl -X POST http://localhost:8000/run-pr \
  -H "Content-Type: application/json" \
  -d "{\"bundle_dir\": \"data/pr_bundles/pr_bundle_001\"}"

curl http://localhost:8000/runs/RUN-.../decision
```

---

## 8. Running with Docker (optional)

Docker is **optional** - only for a self-contained local demo. The image is built on
`python:3.12-slim`.

```bash
# Build the image
docker build -t iprms .

# Run the FastAPI service (default) on http://localhost:8000
docker run --rm -p 8000:8000 iprms

# Or run the Streamlit demo UI on http://localhost:8501
docker run --rm -p 8501:8501 iprms \
    streamlit run app/streamlit_app.py --server.port 8501 --server.address 0.0.0.0
```

---

## 9. Running the tests

```bash
# Run the full suite (expect: 170 passed)
pytest -q

# Verbose, with test names
pytest -v

# Run a single test file
pytest tests/test_pipeline.py
```

The suite (170 tests across 16 files) covers every agent (A-H), the Pydantic schemas, the
end-to-end pipeline, **LangGraph parity** (same final decisions and equivalent artifacts as the
direct path), **idempotency** (stable input hash), the API endpoints, and the controlled-LLM
guardrails.

---

## 10. Built-in demo scenarios

The repository ships with 12 designed scenarios plus a baseline bundle, each with a
`manifest.yaml`, input data, and an `expected_outcome.json` oracle. They exercise every decision
path:

| Bundle | Purpose | Expected decision | Routed to |
|--------|---------|-------------------|-----------|
| `pr_bundle_001` | Baseline clean IT PR | `auto_po` | - |
| `scenario_01_clean_pr` | Standard IT consumables, approved vendor, in budget | `auto_po` | - |
| `scenario_02_non_preferred_vendor` | Non-preferred vendor without justification | `exception` | Procurement |
| `scenario_03_same_week_threshold_anomaly` | 3 PRs same dept/week above threshold | `exception` | Compliance/Procurement |
| `scenario_04_budget_exhausted` | Cost center budget exhausted | `blocked` | FP&A |
| `scenario_05_emergency_sole_source` | Emergency sole-source purchase | `expedited_approval` | Expedited Approval |
| `scenario_06_vague_item_description` | Item too vague to price | `buyer_clarification` | Buyer Clarification |
| `scenario_07_split_order_pattern` | Same item split across 5 PRs | `exception` | Compliance Review |
| `scenario_08_low_confidence_extraction` | Low extraction confidence | `manual_review` | Manual Review |
| `scenario_09_small_clean_pr` | Small clean PR under threshold | `auto_approve` | - |
| `scenario_10_framework_agreement` | Framework agreement PR | policy-driven | Configured Policy Routing |
| `scenario_11_blanket_order` | Blanket order PR | policy-driven | Configured Policy Routing |
| `scenario_12_multi_currency` | Multi-currency PR / PO | policy validation | Finance/Procurement |

Run any of them via the CLI, the UI, or the API, e.g.:

```bash
python pipelines/run_iprms_pipeline.py --bundle data/pr_bundles/scenario_04_budget_exhausted
```

---

## 11. Run artifacts

Every run stores all outputs locally under `runs/<run_id>/`. The run directory is resolved from
the repo root (see `configs/config.py` -> `RUNS_DIR`), so it is always created in the same place
regardless of the current working directory.

```
runs/<run_id>/
+-- context_packet.json       
+-- evidence_index.json        
+-- extracted_pr.json         
+-- budget_check.json         
+-- vendor_match.json          
+-- policy_check.json        
+-- sole_source_check.json     
+-- bid_threshold_check.json   
+-- anomaly_report.json        
+-- exceptions.md            
+-- approval_packet.json       
+-- po_draft.json              
+-- audit_log.md               
+-- metrics.json             
+-- run_summary.csv           
+-- tracker_payload.json      
+-- llm_fallback_trace.json    
`-- erp_posting_result.json    
```

All artifacts are written through `artifact_store.ArtifactStore`, which centralizes path
resolution and writing so every agent uses one consistent layout.

---

## 12. Configuration - the single source of truth

All procurement rules live in **`configs/policy_pack.yaml`**.

It defines, among others:

- `approval_thresholds` - `manager_limit`, `finance_limit`, `director_limit`
- `tolerances` - catalogue price variance %, minimum extraction confidence
- `routing` - where each exception type is sent
- `bid_rules` - bid threshold amount and minimum required bids
- complex-procurement flags, multi-currency rules, and PR-type classification

**Demonstration of config-driven behaviour:** change `manager_limit` from `1000` to `100`,
re-run `pr_bundle_001` (amount = 450 EUR), and the decision flips from `auto_po` to
`manual_approval` routed to Finance. Revert the value and it returns to
`auto_po`. This proves the policy pack drives every decision.

---

## 13. Architecture & design guarantees

- **Deterministic core.** All business decisions (budget, vendor, compliance, sole-source,
  anomaly, routing, PO) are deterministic Python / Pydantic / Pandas, so runs are reproducible
  and idempotent.
- **Idempotency.** Agent A computes a SHA-256 `input_hash` over the bundle, manifest and policy
  pack. Re-running identical input yields the same hash and `idempotency_check: passed`.
- **LangGraph parity.** LangGraph is an *optional internal skeleton* that wraps the same A->H
  functions for flow/state/audit. It produces the **same final decisions and equivalent
  artifacts** as the direct Python pipeline; parity tests verify that the skeleton calls the
  same deterministic agent functions (artifacts are byte-identical when run with the same fixed
  run_id and normalized runtime fields). The project runs fully without LangGraph.
- **Controlled LLM boundary.** LangChain/LLM is allowed at **exactly two advisory points**
  (Agent A PR-type classification, Agent B vague/unclear extraction), is **off by default**, and
  **never** decides budget, vendor, compliance, split-order, routing, or PO. With it disabled,
  decisions are identical.

---

## 14. Repository structure

```
iprms-intelligent-purchase-requisition/
+-- agents/       
+-- api/          
+-- app/          
+-- configs/       
  config.py
+-- data/         
  manifest.yaml 
  expected_outcome.json
+-- graph/        
  state.py
  nodes.py
  workflow.py
+-- llm/           
+-- pipelines/    
+-- schemas/       
+-- runs/          
+-- tests/         
+-- Dockerfile     
+-- requirements.txt
`-- README.md
```

---

## 15. Day 5 - Spec-Driven Production Readiness

As part of the Kaggle AI Agents Intensive (Day 5 - *Spec-Driven Production Grade
Development in the Age of Vibe Coding*), IPRMS has been documented as a spec-driven,
production-ready system:

- **Spec-Driven Development mapping** - IPRMS treats specs, configs, schemas, tests,
  and audit artifacts as the source of truth (not code). See
  [docs/IPRMS_Spec_Driven_Development.md](docs/IPRMS_Spec_Driven_Development.md).
- **Gherkin behavior specs** - human-readable, deterministic pipeline scenarios were
  added in [features/pr_processing.feature](features/pr_processing.feature).
- **Production-readiness documentation** - ready-to-paste Kaggle notebook content and
  the IPRMS production architecture are in
  [docs/Day5_Kaggle_Notebook_Content.md](docs/Day5_Kaggle_Notebook_Content.md).
- **Optional Google Cloud codelabs** - the Day 5 cloud deployment codelabs were
  **reviewed but not executed**, because they require a billing-enabled Google Cloud
  project. No cloud deployment was attempted and no billing services were created.
- **Determinism preserved** - the core IPRMS pipeline remains fully deterministic:
  *same input bundle + same configs = same outputs.* No business logic was changed.

</content>
</invoke>
