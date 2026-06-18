from __future__ import annotations

import os
from typing import Optional

from llm import guardrails
from llm.prompts import ITEM_NORMALIZE_PROMPT


def normalize_item_description(text: str) -> Optional[str]:
    """Return a normalized candidate description, or None if unavailable/disabled."""
    if not guardrails.llm_enabled():
        return None
    try:
        from langchain.chat_models import init_chat_model

        model_name = os.environ.get("IPRMS_LLM_MODEL", "gpt-4o-mini")
        model = init_chat_model(model_name)
        reply = model.invoke(ITEM_NORMALIZE_PROMPT.format(text=text))
        candidate = getattr(reply, "content", str(reply)).strip()
        return candidate or None
    except Exception:
        return None
