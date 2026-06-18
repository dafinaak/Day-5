"""Streamlit demo UI for IPRMS (plan §11).

Lets a user select a PR bundle / scenario, validate its manifest, run the local
deterministic pipeline (optionally via the LangGraph skeleton), and view the
final decision, approval packet, exceptions, PO draft, audit log, metrics, and
run_summary.csv.

Run with:  streamlit run app/streamlit_app.py

The data-loading helpers are importable/testable without a Streamlit runtime;
only main() touches st.* and is invoked when run as a script.
"""
from __future__ import annotations

import csv
import json
import sys
from pathlib import Path
from typing import Any, Dict, List

_REPO_ROOT = str(Path(__file__).resolve().parents[1])
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from configs.config import PR_BUNDLES_DIR
from manifest_validation import validate_bundle
from pipelines.run_iprms_pipeline import run_pipeline


def available_bundles() -> List[Path]:
    """All PR bundles (folders containing manifest.yaml), sorted by name."""
    if not PR_BUNDLES_DIR.is_dir():
        return []
    return sorted(p for p in PR_BUNDLES_DIR.iterdir()
                  if p.is_dir() and (p / "manifest.yaml").exists())


def collect_run_artifacts(run_dir: Path | str) -> Dict[str, Any]:
    """Read the key artifacts of a completed run for display."""
    run_dir = Path(run_dir)

    def _json(name: str):
        p = run_dir / name
        return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None

    def _text(name: str):
        p = run_dir / name
        return p.read_text(encoding="utf-8") if p.exists() else ""

    run_summary_row: Dict[str, Any] = {}
    rs = run_dir / "run_summary.csv"
    if rs.exists():
        with rs.open(encoding="utf-8") as f:
            rows = list(csv.DictReader(f))
            if rows:
                run_summary_row = rows[0]

    packet = _json("approval_packet.json") or {}
    return {
        "decision": packet.get("final_decision"),
        "po_status": packet.get("po_status"),
        "routed_to": packet.get("routed_to"),
        "approval_packet": packet,
        "exceptions_md": _text("exceptions.md"),
        "po_draft": _json("po_draft.json"),
        "audit_log_md": _text("audit_log.md"),
        "metrics": _json("metrics.json"),
        "erp_posting_result": _json("erp_posting_result.json"),
        "tracker_payload": _json("tracker_payload.json"),
        "run_summary": run_summary_row,
        "artifacts": sorted(p.name for p in run_dir.iterdir() if p.is_file()),
    }


def main() -> None:  # pragma: no cover - UI, exercised via `streamlit run`
    import streamlit as st

    st.set_page_config(page_title="IPRMS", layout="wide")
    st.title("IPRMS — Intelligent Purchase Requisition Management")

    bundles = available_bundles()
    if not bundles:
        st.error("No PR bundles found under data/pr_bundles/.")
        return

    names = [b.name for b in bundles]
    col1, col2 = st.columns([3, 1])
    with col1:
        selected = st.selectbox("Select PR bundle / scenario", names)
    with col2:
        use_langgraph = st.checkbox("LangGraph engine", value=False)

    bundle_dir = PR_BUNDLES_DIR / selected

    result = validate_bundle(bundle_dir)
    if result.is_valid:
        st.success(f"manifest.yaml valid — bundle '{result.manifest.bundle_id}'")
    else:
        st.error("Invalid bundle:\n- " + "\n- ".join(result.errors))

    if st.button("Run pipeline", disabled=not result.is_valid):
        res = run_pipeline(bundle_dir, use_langgraph=use_langgraph)
        art = collect_run_artifacts(res.run_dir)

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Decision", art["decision"])
        c2.metric("PO status", art["po_status"])
        c3.metric("Routed to", art["routed_to"] or "—")
        c4.metric("ERP", (art["erp_posting_result"] or {}).get("erp_status", "—"))

        st.caption(f"run_id: {res.run_id}  •  engine: "
                   f"{'LangGraph skeleton' if use_langgraph else 'direct Python'}")

        st.subheader("Approval packet")
        st.json(art["approval_packet"])

        st.subheader("Exceptions")
        st.markdown(art["exceptions_md"] or "_none_")

        st.subheader("PO draft")
        st.json(art["po_draft"])

        st.subheader("Audit log")
        st.code(art["audit_log_md"], language="markdown")

        st.subheader("Metrics")
        st.json(art["metrics"])

        if art["tracker_payload"]:
            st.subheader("Tracker payload")
            st.json(art["tracker_payload"])

        st.subheader("run_summary.csv")
        st.table([art["run_summary"]] if art["run_summary"] else [])

        with st.expander("All artifacts"):
            st.write(art["artifacts"])


if __name__ == "__main__":
    main()
