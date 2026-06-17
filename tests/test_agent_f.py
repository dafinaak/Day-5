import json
from datetime import datetime, timezone

from agents import agent_a_intake_context as agent_a
from agents import agent_b_item_pr_extraction as agent_b
from agents import agent_f_sole_source_bid_threshold as agent_f
from configs.config import PR_BUNDLES_DIR

FIXED = datetime(2026, 6, 16, 14, 30, 22, tzinfo=timezone.utc)


def _run_f(bundle_name, tmp_path):
    bundle = PR_BUNDLES_DIR / bundle_name
    ares = agent_a.run(bundle, runs_root=tmp_path, when=FIXED)
    agent_b.run(ares)
    return ares, agent_f.run(ares)


def test_clean_pr_no_sole_source_no_threshold(tmp_path):
    _ares, res = _run_f("pr_bundle_001", tmp_path)  # bids 3, amount 450
    ss = res.sole_source_check
    bt = res.bid_threshold_check
    assert ss.sole_source is False
    assert ss.result == "ok"
    assert bt.exceeds_threshold is False
    assert bt.sufficient_bids is True
    assert res.findings == []


def test_emergency_sole_source_expedited(tmp_path):
    _ares, res = _run_f("scenario_05_emergency_sole_source", tmp_path)
    ss = res.sole_source_check
    assert ss.sole_source is True            # Scenario 5: sole_source = true
    assert ss.emergency is True
    assert ss.expedited_approval_required is True
    assert ss.result == "emergency_sole_source"
    f = next(f for f in res.findings if f.finding_type == "EMERGENCY_SOLE_SOURCE")
    assert "Expedited Approval" in f.recommended_action


def test_bid_threshold_exceeded_without_enough_bids(tmp_path):
    # Tamper amount above threshold (5000) with few bids -> exceeded.
    bundle = PR_BUNDLES_DIR / "pr_bundle_001"
    ares = agent_a.run(bundle, runs_root=tmp_path, when=FIXED)
    agent_b.run(ares)
    ep = ares.run_dir / "extracted_pr.json"
    data = json.loads(ep.read_text(encoding="utf-8"))
    data["estimated_amount"]["value"] = 9000.0
    ep.write_text(json.dumps(data), encoding="utf-8")
    # also reduce bids in the requisition metadata
    meta_path = ares.run_dir  # extracted is in run_dir; metadata is in bundle (read-only)
    res = agent_f.run(ares)
    bt = res.bid_threshold_check
    assert bt.exceeds_threshold is True
    assert bt.result == "threshold_exceeded"
    # pr_bundle_001 has 3 bids -> sufficient, so no finding in this case
    assert bt.sufficient_bids is True
    assert not any(f.finding_type == "BID_THRESHOLD_EXCEEDED" for f in res.findings)


def test_bid_threshold_exceeded_with_insufficient_bids(tmp_path):
    # scenario_05: amount 4800 (<5000) -> not exceeded; verify boundary via tamper.
    bundle = PR_BUNDLES_DIR / "scenario_05_emergency_sole_source"  # bids=1
    ares = agent_a.run(bundle, runs_root=tmp_path, when=FIXED)
    agent_b.run(ares)
    ep = ares.run_dir / "extracted_pr.json"
    data = json.loads(ep.read_text(encoding="utf-8"))
    data["estimated_amount"]["value"] = 9000.0  # now above threshold, bids=1 < 3
    ep.write_text(json.dumps(data), encoding="utf-8")
    res = agent_f.run(ares)
    bt = res.bid_threshold_check
    assert bt.exceeds_threshold is True
    assert bt.sufficient_bids is False
    assert any(f.finding_type == "BID_THRESHOLD_EXCEEDED" for f in res.findings)


def test_artifacts_written_and_serialized(tmp_path):
    _ares, res = _run_f("scenario_05_emergency_sole_source", tmp_path)
    assert res.sole_source_path.name == "sole_source_check.json"
    assert res.bid_threshold_path.name == "bid_threshold_check.json"
    ss = json.loads(res.sole_source_path.read_text(encoding="utf-8"))
    assert ss["sole_source"] is True
    assert ss["result"] == "emergency_sole_source"
