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
