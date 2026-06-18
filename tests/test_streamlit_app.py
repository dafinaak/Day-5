from datetime import datetime, timezone

from app.streamlit_app import available_bundles, collect_run_artifacts
from configs.config import PR_BUNDLES_DIR
from pipelines.run_iprms_pipeline import run_direct

FIXED = datetime(2026, 6, 16, 14, 30, 22, tzinfo=timezone.utc)


def test_available_bundles_lists_scenarios():
    names = {b.name for b in available_bundles()}
    assert "pr_bundle_001" in names
    assert "scenario_02_non_preferred_vendor" in names
    # every listed bundle has a manifest
    for b in available_bundles():
        assert (b / "manifest.yaml").exists()


def test_collect_run_artifacts_clean(tmp_path):
    ares = run_direct(PR_BUNDLES_DIR / "pr_bundle_001", runs_root=tmp_path, when=FIXED)
    art = collect_run_artifacts(ares.run_dir)
    assert art["decision"] == "auto_po"
    assert art["po_status"] == "ready_for_posting"
    assert art["routed_to"] is None
    assert (art["erp_posting_result"] or {})["erp_status"] == "simulated_post_success"
    assert art["tracker_payload"] is None
    assert "No critical exceptions." in art["exceptions_md"]
    assert art["run_summary"]["pr_id"] == "PR-2026-001"
    assert "po_draft.json" in art["artifacts"]


def test_collect_run_artifacts_exception(tmp_path):
    ares = run_direct(PR_BUNDLES_DIR / "scenario_04_budget_exhausted", runs_root=tmp_path, when=FIXED)
    art = collect_run_artifacts(ares.run_dir)
    assert art["decision"] == "blocked"
    assert art["routed_to"] == "FP&A"
    assert art["tracker_payload"]["routed_to"] == "FP&A"
