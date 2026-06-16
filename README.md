# IPRMS — Intelligent Purchase Requisition Management System

IPRMS is an Azure Databricks-based **8-agent purchase requisition management system**. It
processes Purchase Requisition (PR) bundles, validates budget and vendor data, applies a
configurable policy pack, detects procurement risks and anomalies, routes exceptions, and
generates ERP-ready PO drafts with full JSON / Markdown / CSV audit artifacts.

> **Scope:** Purchase Requisition handling only. Invoice handling, invoice-to-PO matching, and
> GRN matching are explicitly **out of scope**.

## Technology decisions

- **Databricks** is the official orchestration / execution and demo platform.
- Core business decisions are **deterministic** (Python / Pydantic / Pandas / PySpark) to preserve idempotency.
- **LangGraph** is optional, only as a lightweight internal wrapper for the Agent A→H sequence (it must not replace Databricks Jobs).
- **LangChain / Azure OpenAI** is optional, only as an Agent B fallback for unclear extraction fields or vague item descriptions. It must **not** decide approval, blocking, routing, or PO posting.
- The system must work even if LangGraph / LangChain are disabled.

## The 8 agents

| Agent | Responsibility | Key output(s) |
|-------|----------------|---------------|
| A | Intake & Context / Gatekeeper | `context_packet.json`, `evidence_index.json` |
| B | Item / PR Extraction | `extracted_pr.json` |
| C | Budget Validation | `budget_check.json` |
| D | Vendor Matching | `vendor_match.json` |
| E | Compliance & Policy | `policy_check.json` |
| F | Sole-source / Bid-threshold | `sole_source_check.json`, `bid_threshold_check.json` |
| G | Split-order / Anomaly Detection | `anomaly_report.json` |
| H | Exception Triage & Lead Orchestration | `exceptions.md`, `approval_packet.json`, `po_draft.json`, `audit_log.md`, `metrics.json`, `run_summary.csv` |

## Repository structure

```
iprms-intelligent-purchase-requisition/
├── agents/        # Agent A–H implementations
├── configs/       # policy_pack.yaml, tolerance_settings.json, routing_rules.json
├── data/          # pr_bundles/ (with manifest.yaml) and sample_prs/
├── notebooks/     # Databricks notebooks (run pipeline, load Delta, demo dashboard)
├── pipelines/     # run_iprms_pipeline.py — deterministic A→H pipeline
├── graph/         # optional LangGraph wrapper (state.py, workflow.py)
├── schemas/       # Pydantic schemas (pr, artifact, finding, decision)
├── runs/          # per-run output: runs/<run_id>/ artifacts
├── tests/         # pytest scenario tests
├── api/           # FastAPI app (main.py)
├── app/           # Streamlit demo app
├── databricks.yml # Databricks Asset Bundle definition
├── Dockerfile
└── requirements.txt
```

## Getting started

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the pipeline on the sample PR bundle
python pipelines/run_iprms_pipeline.py --bundle data/pr_bundles/pr_bundle_001

# 4. Run the tests
pytest tests/
```

Each run produces a `runs/<run_id>/` directory containing all mandatory artifacts, and key
results are also stored in Delta tables (`iprms.*`) when run on Databricks.

## Deployment

The demo API/UI is containerized and deployed to **Azure Container Apps**, while **Databricks**
remains the processing engine:

```
GitHub repo → Docker image → Azure Container Registry → Azure Container Apps
            → FastAPI / Streamlit UI → Databricks Job → Delta tables + artifacts
```

```bash
databricks bundle validate
databricks bundle deploy
databricks bundle run iprms_pipeline
```

## Team

| Engineer | Role |
|----------|------|
| Dafina | Platform & Data Integration Engineer |
| Yllka | PR Extraction & Matching Engineer |
| Rozafa | Compliance, Risk & Orchestration Engineer |
