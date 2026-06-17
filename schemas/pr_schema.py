"""Extraction & matching schemas (IPRMS).

Pydantic models for the outputs of Agent B (extracted_pr.json),
Agent C (budget_check.json) and Agent D (vendor_match.json), plus the
PR-type classification fields (Agent A) and the controlled-LLM fallback trace
(llm_fallback_trace.json). Consistent with the run artifacts in plani.pdf §6/§7
and the controlled-LLM boundary in §4.1.
"""
from __future__ import annotations

from enum import Enum
from typing import Generic, List, Optional, TypeVar

from pydantic import BaseModel, Field, field_validator

from schemas.finding_schema import Finding

BoundingBox = List[float]  # [x0, y0, x1, y1]
T = TypeVar("T")


# ---------- Agent B: extracted_pr.json ----------
class ExtractedField(BaseModel, Generic[T]):
    """A single extracted value with its provenance (per plani.pdf §6 example)."""
    value: T
    confidence: float = Field(..., ge=0.0, le=1.0)
    source_page: Optional[int] = None
    bounding_box: Optional[BoundingBox] = None  # [x0, y0, x1, y1]

    @field_validator("bounding_box")
    @classmethod
    def _check_bbox(cls, v: Optional[BoundingBox]) -> Optional[BoundingBox]:
        if v is not None and len(v) != 4:
            raise ValueError("bounding_box must have exactly 4 numbers [x0, y0, x1, y1]")
        return v


class ExtractedPR(BaseModel):
    pr_id: ExtractedField[str]
    requester: ExtractedField[str]
    department: ExtractedField[str]
    cost_center: ExtractedField[str]
    vendor_name: ExtractedField[str]
    item_description: ExtractedField[str]
    item_category: ExtractedField[str]
    quantity: ExtractedField[int]
    unit_price: ExtractedField[float]
    estimated_amount: ExtractedField[float]
    currency: ExtractedField[str]
    business_justification: ExtractedField[str]
    urgency: ExtractedField[str]
    confidence_score: float = Field(..., ge=0.0, le=1.0)  # overall extraction confidence
    # Top-level provenance, optional — provenance is primarily per-field above.
    # Listed here to formally satisfy the plani.pdf §6 "must include" field list.
    source_page: Optional[int] = None
    bounding_box: Optional[BoundingBox] = None  # [x0, y0, x1, y1]
    # Controlled LLM fallback (§4.1): advisory only. The per-field values above
    # remain the parser/OCR source of truth; the normalized candidate is stored
    # separately and is only set when an Agent B fallback actually runs.
    llm_fallback_used: bool = False
    llm_normalized_candidate: Optional[str] = None

    @field_validator("bounding_box")
    @classmethod
    def _check_bbox(cls, v: Optional[BoundingBox]) -> Optional[BoundingBox]:
        if v is not None and len(v) != 4:
            raise ValueError("bounding_box must have exactly 4 numbers [x0, y0, x1, y1]")
        return v


# ---------- Agent C: budget_check.json ----------
class BudgetResult(str, Enum):
    PASSED = "passed"
    FAILED_BUDGET_EXHAUSTED = "failed_budget_exhausted"
    ROUTE_TO_FPA = "route_to_FP&A"


class BudgetCheck(BaseModel):
    pr_id: str
    cost_center: str
    cost_center_exists: bool
    requested_amount: float
    available_budget: float
    currency: str
    result: BudgetResult
    routed_to: Optional[str] = None
    findings: List[Finding] = Field(default_factory=list)


# ---------- Agent D: vendor_match.json ----------
class VendorMatchResult(str, Enum):
    MATCHED = "matched"                      # approved + preferred, clean
    NON_PREFERRED = "non_preferred"          # Scenario 2
    PRICING_UNCERTAIN = "pricing_uncertain"  # Scenario 6 (vague item)
    NOT_APPROVED = "not_approved"


class VendorMatch(BaseModel):
    pr_id: str
    vendor_name: str
    approved: bool
    preferred: bool
    vendor_status: str
    justification_present: bool = False
    requested_unit_price: Optional[float] = None
    catalogue_unit_price: Optional[float] = None
    price_variance_percent: Optional[float] = None
    within_price_tolerance: Optional[bool] = None
    result: VendorMatchResult
    findings: List[Finding] = Field(default_factory=list)


# ---------- Agent A: PR-type classification (context_packet.json) ----------
class PRType(str, Enum):
    STANDARD = "standard"
    EMERGENCY = "emergency"
    CAPEX = "capex"


class ClassificationSource(str, Enum):
    METADATA = "metadata"   # deterministic rules from PR metadata
    LLM = "llm"             # controlled fallback (metadata insufficient)
    DEFAULT = "default"     # metadata insufficient and no fallback available


class PRTypeClassification(BaseModel):
    pr_type: PRType
    source: ClassificationSource
    confidence: float = Field(..., ge=0.0, le=1.0)
    llm_fallback_used: bool = False


# ---------- Controlled LLM fallback trace (llm_fallback_trace.json, §4.1) ----------
class LLMFallbackTrace(BaseModel):
    source_agent: str                            # "Agent A" | "Agent B"
    fallback_type: str                           # "pr_type_classification" | "item_extraction"
    used: bool
    reason: str                                  # why the fallback was triggered
    confidence: float = Field(..., ge=0.0, le=1.0)
    model: Optional[str] = None
    prompt_version: Optional[str] = None
    normalized_candidate: Optional[str] = None   # LLM suggestion (advisory only)
    original_evidence: Optional[str] = None      # pointer to parser/OCR/metadata source of truth
