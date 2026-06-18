"""LLM fallback traceability for IPRMS (plan §4.1 / §7).

Builds the LLMFallbackTrace record written to llm_fallback_trace.json whenever an
Agent A or Agent B LLM fallback is used. Records whether fallback ran, the
triggering reason, confidence, model/prompt version, the normalized candidate,
and a pointer to the original parser/OCR/metadata evidence (the source of truth).
"""
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
