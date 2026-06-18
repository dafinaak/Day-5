from __future__ import annotations

from typing import Optional

from schemas.pr_schema import LLMFallbackTrace


def make_trace(
    *,
    source_agent: str,
    fallback_type: str,
    used: bool,
    reason: str,
    confidence: float,
    normalized_candidate: Optional[str] = None,
    model: Optional[str] = None,
    prompt_version: Optional[str] = None,
    original_evidence: Optional[str] = None,
) -> LLMFallbackTrace:
    return LLMFallbackTrace(
        source_agent=source_agent,
        fallback_type=fallback_type,
        used=used,
        reason=reason,
        confidence=confidence,
        normalized_candidate=normalized_candidate,
        model=model,
        prompt_version=prompt_version,
        original_evidence=original_evidence,
    )
