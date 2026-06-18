"""Prompt templates for the controlled LLM fallback (IPRMS, plan §4.1).

These prompts are used ONLY at the two allowed fallback points. They ask the
model to return a single, constrained value (a PR-type label or a normalized
item description) — never a decision.
"""
from __future__ import annotations

PROMPT_VERSION = "v1"

PR_TYPE_PROMPT = (
    "You classify a purchase requisition's type from its metadata.\n"
    "Return EXACTLY one lowercase word: standard, emergency, or capex.\n"
    "Do not explain. Do not decide approval, budget, vendor, or routing.\n"
    "Metadata: {metadata}\n"
    "PR type:"
)

ITEM_NORMALIZE_PROMPT = (
    "Rewrite this vague purchase item description into a clear, specific,\n"
    "catalogue-style description (brand/spec/category if inferable).\n"
    "Return ONLY the normalized description text, nothing else.\n"
    "Original: {text}\n"
    "Normalized:"
)
