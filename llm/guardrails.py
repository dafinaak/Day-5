"""Guardrails for the controlled LLM boundary (IPRMS, plan §4.1).

LLM output is advisory only and NEVER drives a final decision. It is allowed at
exactly two fallback points:
  * Agent A — PR-type classification when metadata is insufficient.
  * Agent B — vague item descriptions / unclear OCR-PDF extraction normalization.

NOT allowed (always rule-based): budget validation, vendor approval/preferred,
compliance decision, split-order/anomaly final decision, approval routing, and
PO draft posting/blocking. Original parser/OCR/metadata evidence is always kept.
"""
from __future__ import annotations

import os

ALLOWED_FALLBACK_POINTS = (
    "agent_a_pr_type_classification",
    "agent_b_item_extraction",
)

FORBIDDEN_DECISIONS = (
    "budget_validation", "vendor_approval", "compliance", "split_order",
    "approval_routing", "po_draft_posting",
)


def llm_enabled() -> bool:
    """True only when the controlled LLM fallback is explicitly enabled via env."""
    return os.environ.get("IPRMS_LLM_FALLBACK_ENABLED", "").strip().lower() in (
        "1", "true", "yes", "on",
    )


def assert_allowed(fallback_point: str) -> None:
    """Raise if a caller tries to use the LLM outside the two allowed points."""
    if fallback_point not in ALLOWED_FALLBACK_POINTS:
        raise ValueError(
            f"LLM fallback not allowed at '{fallback_point}'. "
            f"Allowed only: {ALLOWED_FALLBACK_POINTS}"
        )
