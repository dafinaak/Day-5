from __future__ import annotations

from enum import Enum
from typing import List, Tuple

from pydantic import BaseModel, Field, field_validator


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def rank(self) -> int:
        """Numeric order so Agent H can compute the highest severity in a run."""
        return {"low": 1, "medium": 2, "high": 3, "critical": 4}[self.value]


class FindingStatus(str, Enum):
    OPEN = "open"          # default, as in the plan example
    MERGED = "merged"      # set by Agent H after deduplication
    RESOLVED = "resolved"
    DISMISSED = "dismissed"


class FindingType:
    """Common finding-type constants (convention: UPPER_SNAKE_CASE).

    Not exhaustive — `finding_type` is a plain string by design so each agent
    can emit its own types without changing this schema.
    """
    BUDGET_EXCEEDED = "BUDGET_EXCEEDED"
    COST_CENTER_NOT_FOUND = "COST_CENTER_NOT_FOUND"
    NON_PREFERRED_VENDOR = "NON_PREFERRED_VENDOR"
    PRICE_VARIANCE = "PRICE_VARIANCE"
    VAGUE_ITEM_DESCRIPTION = "VAGUE_ITEM_DESCRIPTION"
    LOW_CONFIDENCE_EXTRACTION = "LOW_CONFIDENCE_EXTRACTION"
    SOLE_SOURCE = "SOLE_SOURCE"
    EMERGENCY_SOLE_SOURCE = "EMERGENCY_SOLE_SOURCE"
    BID_THRESHOLD_EXCEEDED = "BID_THRESHOLD_EXCEEDED"
    SPLIT_ORDER = "SPLIT_ORDER"
    THRESHOLD_AVOIDANCE = "THRESHOLD_AVOIDANCE"
    FRAMEWORK_AGREEMENT = "FRAMEWORK_AGREEMENT"
    BLANKET_ORDER = "BLANKET_ORDER"
    MULTI_CURRENCY = "MULTI_CURRENCY"


class Finding(BaseModel):
    """One issue reported by any agent, in the unified format."""

    finding_id: str = Field(..., description="Unique id within a run, e.g. 'F-001'")
    finding_type: str = Field(..., description="UPPER_SNAKE_CASE category, e.g. 'BUDGET_EXCEEDED'")
    severity: Severity
    confidence: float = Field(..., ge=0.0, le=1.0, description="0.0–1.0")
    message: str
    evidence: List[str] = Field(default_factory=list, description="Artifact filenames supporting this finding")
    source_agent: str = Field(..., description="e.g. 'Agent C'")
    recommended_action: str
    status: FindingStatus = FindingStatus.OPEN

    @field_validator("finding_type")
    @classmethod
    def _normalize_type(cls, v: str) -> str:
        return v.strip().upper()

    @property
    def dedup_key(self) -> Tuple[str, str]:
        """Key Agent H uses to detect the same problem reported by two agents."""
        return (self.finding_type, self.message.strip().lower())