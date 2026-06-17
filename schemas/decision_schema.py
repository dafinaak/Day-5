"""Final-decision schemas (IPRMS) — Agent H outputs.

Holds the deterministic final-decision artifacts produced by Agent H
(approval_packet.json now; po_draft / metrics extended in Task 28). Kept separate
from extraction/matching (pr_schema) and compliance/risk (artifact_schema) per
plan §3.
"""
from __future__ import annotations

from enum import Enum
from typing import Dict, List, Optional

from pydantic import BaseModel, Field

from schemas.finding_schema import Finding


class FinalDecision(str, Enum):
    AUTO_PO = "auto_po"
    AUTO_APPROVE = "auto_approve"
    MANUAL_REVIEW = "manual_review"
    BUYER_CLARIFICATION = "buyer_clarification"
    EXPEDITED_APPROVAL = "expedited_approval"
    MANUAL_APPROVAL = "manual_approval"
    EXCEPTION = "exception"
    BLOCKED = "blocked"


class ApprovalPacket(BaseModel):
    run_id: str
    pr_id: str
    final_decision: FinalDecision
    routed_to: Optional[str] = None
    approval_level_required: str = ""
    po_status: str = "blocked"                    # ready_for_posting | blocked
    exception_count: int = 0
    highest_severity: str = "none"               # none | low | medium | high | critical
    complex_flags: Dict[str, bool] = Field(default_factory=dict)
    summary: str = ""
    findings: List[Finding] = Field(default_factory=list)
