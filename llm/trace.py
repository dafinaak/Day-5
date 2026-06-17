"""LLM fallback traceability for IPRMS.

Writes llm_fallback_trace.json (and feeds context_packet.json) whenever an
Agent A or Agent B LLM fallback is used. Records, per the audit requirements:
  * whether fallback was used,
  * the triggering reason,
  * confidence,
  * model / prompt version,
  * the normalized candidate value,
  * and a pointer to the original parser/OCR/metadata evidence (kept as source of truth).

The artifact is produced ONLY when a fallback actually runs.

Skeleton only — implemented in Task 4 / Task 13. See IPRMS plan §4.1 and §7 (Run Artifacts).
"""
from __future__ import annotations
