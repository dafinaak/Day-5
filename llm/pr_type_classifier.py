"""Agent A PR-type classification fallback (controlled LLM, plan §4.1).

Used ONLY when deterministic metadata rules cannot classify the PR type. The LLM
may only *suggest* one of standard / emergency / capex; it never decides routing,
approval, budget, vendor, compliance, anomaly, or PO rules.

Deterministic-safe: returns None when the fallback is disabled (default) or when
no model/credentials are configured — so the pipeline stays deterministic. A real
suggestion requires IPRMS_LLM_FALLBACK_ENABLED + a configured model (e.g.
OPENAI_API_KEY, IPRMS_LLM_MODEL).
"""
from __future__ import annotations

import os
from typing import Any, Dict, Optional

from llm import guardrails
from llm.prompts import PR_TYPE_PROMPT

_VALID = {"standard", "emergency", "capex"}


def classify_pr_type(metadata: Dict[str, Any]) -> Optional[str]:
    """Return 'standard' | 'emergency' | 'capex', or None if unavailable/disabled."""
    if not guardrails.llm_enabled():
        return None
    try:
        from langchain.chat_models import init_chat_model

        model_name = os.environ.get("IPRMS_LLM_MODEL", "gpt-4o-mini")
        model = init_chat_model(model_name)
        reply = model.invoke(PR_TYPE_PROMPT.format(metadata=metadata))
        text = getattr(reply, "content", str(reply)).strip().lower()
        return text if text in _VALID else None
    except Exception:
        # No model / no key / any error -> no suggestion (stay deterministic).
        return None
