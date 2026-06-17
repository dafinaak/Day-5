from datetime import datetime, timezone

from agents import agent_a_intake_context as agent_a
from agents import agent_b_item_pr_extraction as agent_b
from agents import agent_g_split_order_anomaly as agent_g
from configs.config import PR_BUNDLES_DIR

FIXED = datetime(2026, 6, 16, 14, 30, 22, tzinfo=timezone.utc)


def _run_g(bundle_name, tmp_path):
    bundle = PR_BUNDLES_DIR / bundle_name
    ares = agent_a.run(bundle, runs_root=tmp_path, when=FIXED)
    agent_b.run(ares)
    return ares, agent_g.run(ares)


def test_clean_base_bundle_no_anomaly(tmp_path):
    # pr_bundle_001: history is Finance/HR only, current is IT -> no anomaly.
    _ares, res = _run_g("pr_bundle_001", tmp_path)
    rep = res.anomaly_report
    assert rep.anomaly_detected is False
    assert rep.split_order_detected is False
    assert rep.result == "clean"
    assert res.findings == []


def test_split_order_detected(tmp_path):
    # scenario_07: same item (Dell Latitude laptop) across 5 PRs.
    _ares, res = _run_g("scenario_07_split_order_pattern", tmp_path)
    rep = res.anomaly_report
    assert rep.split_order_detected is True
    assert rep.same_item_count >= 3
    assert rep.result == "split_order_detected"
    assert any(f.finding_type == "SPLIT_ORDER" for f in res.findings)


def test_same_week_threshold_anomaly(tmp_path):
    # scenario_03: multiple Operations PRs same week, combined over threshold.
    _ares, res = _run_g("scenario_03_same_week_threshold_anomaly", tmp_path)
    rep = res.anomaly_report
    assert rep.anomaly_detected is True
    assert rep.same_department_same_week_count >= 3
    assert rep.combined_amount >= rep.threshold      # combined reaches 5000 threshold
    assert rep.threshold_avoidance is True
    assert rep.result == "anomaly_detected"
    types = {f.finding_type for f in res.findings}
    assert "SAME_WEEK_MULTIPLE_PRS" in types
    assert "THRESHOLD_AVOIDANCE" in types


def test_threshold_from_policy_not_hardcoded(tmp_path):
    _ares, res = _run_g("scenario_03_same_week_threshold_anomaly", tmp_path)
    assert res.anomaly_report.threshold == 5000     # bid_rules.threshold_amount


def test_anomaly_report_written(tmp_path):
    _ares, res = _run_g("scenario_07_split_order_pattern", tmp_path)
    import json
    assert res.anomaly_report_path.name == "anomaly_report.json"
    data = json.loads(res.anomaly_report_path.read_text(encoding="utf-8"))
    assert data["result"] == "split_order_detected"
    assert data["split_order_detected"] is True
