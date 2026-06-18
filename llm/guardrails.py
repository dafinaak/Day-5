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
