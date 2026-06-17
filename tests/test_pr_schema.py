import json

import pytest
from pydantic import ValidationError

from configs.config import PR_BUNDLES_DIR
from schemas.pr_schema import (
    BudgetCheck,
    BudgetResult,
    ClassificationSource,
    ExtractedField,
    ExtractedPR,
    LLMFallbackTrace,
    PRType,
    PRTypeClassification,
    VendorMatch,
    VendorMatchResult,
)


def _field(value, confidence=0.97, page=1, bbox=None):
    return ExtractedField(value=value, confidence=confidence, source_page=page, bounding_box=bbox)


def _sample_extracted_pr() -> ExtractedPR:
    return ExtractedPR(
        pr_id=_field("PR-2026-001"),
        requester=_field("Arben Krasniqi"),
        department=_field("IT"),
        cost_center=_field("CC-IT-001"),
        vendor_name=_field("Gjirafa Mall", bbox=[120, 250, 420, 280]),
        item_description=_field("Wireless keyboard"),
        item_category=_field("IT Equipment"),
        quantity=_field(15),
        unit_price=_field(30.0),
        estimated_amount=_field(450.0),
        currency=_field("EUR"),
        business_justification=_field("Replacement keyboards for IT support team."),
        urgency=_field("normal"),
        confidence_score=0.96,
    )


def test_extracted_pr_parses_and_keeps_provenance():
    pr = _sample_extracted_pr()
    assert pr.vendor_name.value == "Gjirafa Mall"
    assert pr.vendor_name.bounding_box == [120, 250, 420, 280]
    assert pr.quantity.value == 15
    assert pr.confidence_score == 0.96


def test_bounding_box_must_have_four_numbers():
    with pytest.raises(ValidationError):
        ExtractedField(value="x", confidence=0.9, bounding_box=[1, 2, 3])  # only 3


def test_extracted_pr_from_real_bundle():
    """Build an ExtractedPR from pr_bundle_001's requisition_form.json."""
    form = json.loads(
        (PR_BUNDLES_DIR / "pr_bundle_001" / "requisition_form.json").read_text(encoding="utf-8")
    )
    conf = form["simulated_confidence_score"]
    pr = ExtractedPR(
        pr_id=_field(form["pr_id"], conf),
        requester=_field(form["requester"], conf),
        department=_field(form["department"], conf),
        cost_center=_field(form["cost_center"], conf),
        vendor_name=_field(form["vendor_name"], conf),
        item_description=_field(form["item_description"], conf),
        item_category=_field(form["item_category"], conf),
        quantity=_field(form["quantity"], conf),
        unit_price=_field(float(form["unit_price"]), conf),
        estimated_amount=_field(float(form["estimated_amount"]), conf),
        currency=_field(form["currency"], conf),
        business_justification=_field(form["business_justification"], conf),
        urgency=_field(form["urgency"], conf),
        confidence_score=conf,
    )
    assert pr.cost_center.value == "CC-IT-001"
    assert pr.estimated_amount.value == 450.0


def test_budget_check_serializes_enum_as_string():
    bc = BudgetCheck(
        pr_id="PR-2026-001", cost_center="CC-IT-001", cost_center_exists=True,
        requested_amount=450.0, available_budget=7000.0, currency="EUR",
        result=BudgetResult.PASSED,
    )
    data = json.loads(bc.model_dump_json())
    assert data["result"] == "passed"
    assert isinstance(data["result"], str)
    assert data["findings"] == []


def test_vendor_match_serializes_enum_as_string():
    vm = VendorMatch(
        pr_id="PR-2026-001", vendor_name="Gjirafa Mall", approved=True, preferred=True,
        vendor_status="approved", requested_unit_price=30.0, catalogue_unit_price=30.0,
        price_variance_percent=0.0, within_price_tolerance=True,
        result=VendorMatchResult.MATCHED,
    )
    data = json.loads(vm.model_dump_json())
    assert data["result"] == "matched"
    assert isinstance(data["result"], str)


def test_extracted_pr_llm_fields_default_off():
    pr = _sample_extracted_pr()
    assert pr.llm_fallback_used is False
    assert pr.llm_normalized_candidate is None
    data = json.loads(pr.model_dump_json())
    assert data["llm_fallback_used"] is False
    assert data["llm_normalized_candidate"] is None


def test_pr_type_classification_serializes_enums_as_strings():
    c = PRTypeClassification(
        pr_type=PRType.EMERGENCY,
        source=ClassificationSource.METADATA,
        confidence=0.95,
    )
    data = json.loads(c.model_dump_json())
    assert data["pr_type"] == "emergency"
    assert data["source"] == "metadata"
    assert isinstance(data["pr_type"], str) and isinstance(data["source"], str)
    assert data["llm_fallback_used"] is False  # default


def test_pr_type_confidence_bounds():
    with pytest.raises(ValidationError):
        PRTypeClassification(pr_type=PRType.STANDARD,
                             source=ClassificationSource.METADATA, confidence=1.5)


def test_llm_fallback_trace_shape():
    t = LLMFallbackTrace(
        source_agent="Agent A",
        fallback_type="pr_type_classification",
        used=True,
        reason="metadata insufficient to classify PR type",
        confidence=0.7,
        model="claude-x",
        prompt_version="v1",
        normalized_candidate="emergency",
        original_evidence="context_packet.json",
    )
    data = json.loads(t.model_dump_json())
    assert data["used"] is True
    assert data["fallback_type"] == "pr_type_classification"
    assert data["normalized_candidate"] == "emergency"
    assert data["original_evidence"] == "context_packet.json"