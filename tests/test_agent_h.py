import json
from datetime import datetime, timezone

from agents import agent_a_intake_context as agent_a
from agents import agent_b_item_pr_extraction as agent_b
from agents import agent_c_budget_validation as agent_c
from agents import agent_d_vendor_matching as agent_d
from agents import agent_e_policy_compliance as agent_e
from agents import agent_f_sole_source_bid_threshold as agent_f
from agents import agent_g_split_order_anomaly as agent_g
from agents import agent_h_exception_triage_orchestration as agent_h
from configs.config import PR_BUNDLES_DIR
from schemas.decision_schema import FinalDecision

FIXED = datetime(2026, 6, 16, 14, 30, 22, tzinfo=timezone.utc)


def _run_all(bundle_name, tmp_path):
    bundle = PR_BUNDLES_DIR / bundle_name
    ares = agent_a.run(bundle, runs_root=tmp_path, when=FIXED)
    agent_b.run(ares)
    agent_c.run(ares)
    agent_d.run(ares)
    agent_e.run(ares)
    agent_f.run(ares)
    agent_g.run(ares)
    return ares, agent_h.run(ares)


def test_clean_pr_auto_po(tmp_path):
    _ares, res = _run_all("pr_bundle_001", tmp_path)
    pkt = res.approval_packet
    assert pkt.final_decision == FinalDecision.AUTO_PO
    assert pkt.po_status == "ready_for_posting"
    assert pkt.exception_count == 0
    assert pkt.routed_to is None
    assert "No critical exceptions." in res.exceptions_path.read_text(encoding="utf-8")


def test_budget_exhausted_blocked(tmp_path):
    _ares, res = _run_all("scenario_04_budget_exhausted", tmp_path)
    pkt = res.approval_packet
    assert pkt.final_decision == FinalDecision.BLOCKED
    assert pkt.po_status == "blocked"
    assert pkt.routed_to == "FP&A"


def test_non_preferred_exception_to_procurement(tmp_path):
    _ares, res = _run_all("scenario_02_non_preferred_vendor", tmp_path)
    pkt = res.approval_packet
    assert pkt.final_decision == FinalDecision.EXCEPTION
    assert pkt.routed_to == "Procurement"
    assert pkt.exception_count >= 1


def test_emergency_sole_source_expedited(tmp_path):
    _ares, res = _run_all("scenario_05_emergency_sole_source", tmp_path)
    assert res.approval_packet.final_decision == FinalDecision.EXPEDITED_APPROVAL
    assert res.approval_packet.routed_to == "Expedited Approval"


def test_vague_buyer_clarification(tmp_path):
    _ares, res = _run_all("scenario_06_vague_item_description", tmp_path)
    assert res.approval_packet.final_decision == FinalDecision.BUYER_CLARIFICATION


def test_split_order_to_compliance(tmp_path):
    _ares, res = _run_all("scenario_07_split_order_pattern", tmp_path)
    pkt = res.approval_packet
    assert pkt.final_decision == FinalDecision.EXCEPTION
    assert pkt.routed_to == "Compliance"


def test_low_confidence_manual_review(tmp_path):
    _ares, res = _run_all("scenario_08_low_confidence_extraction", tmp_path)
    assert res.approval_packet.final_decision == FinalDecision.MANUAL_REVIEW


def test_multi_currency_manual_approval(tmp_path):
    _ares, res = _run_all("scenario_12_multi_currency", tmp_path)
    pkt = res.approval_packet
    assert pkt.final_decision == FinalDecision.MANUAL_APPROVAL
    assert pkt.complex_flags["multi_currency"] is True


def test_findings_deduplicated_and_artifacts_written(tmp_path):
    _ares, res = _run_all("scenario_02_non_preferred_vendor", tmp_path)
    assert res.approval_packet_path.name == "approval_packet.json"
    assert res.exceptions_path.name == "exceptions.md"
    data = json.loads(res.approval_packet_path.read_text(encoding="utf-8"))
    keys = [(f["finding_type"], f["message"]) for f in data["findings"]]
    assert len(keys) == len(set(keys))  # no duplicates after merge
    assert data["final_decision"] == "exception"
