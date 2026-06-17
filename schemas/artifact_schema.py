"""Compliance & risk artifact schemas (IPRMS).

Pydantic models for the compliance/risk run artifacts produced by Agents E/F/G:
  * Agent E -> policy_check.json (PolicyCheck)
  * Agent F -> sole_source_check.json / bid_threshold_check.json (added in Task 25)
  * Agent G -> anomaly_report.json (added in Task 26)

Kept separate from pr_schema.py (extraction/matching, Agents B/C/D) per plan §3.
"""
from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field

from schemas.finding_schema import Finding


# ---------- Agent E: policy_check.json ----------
class PolicyCheck(BaseModel):
    pr_id: str
    compliance_status: str                       # "compliant" | "violation"
    approval_level_required: str                 # Manager | Finance | Director | Board
    manual_approval_required: bool
    non_preferred_vendor: bool = False
    vendor_approved: bool = True
    budget_ok: bool = True
    urgency: str = ""
    violations: List[str] = Field(default_factory=list)
    # Complex-procurement flags (defaults here; populated by Agent E / Task 24).
    framework_agreement_flag: bool = False
    blanket_order_flag: bool = False
    emergency_procurement_flag: bool = False
    multi_currency_flag: bool = False
    findings: List[Finding] = Field(default_factory=list)
