"""Guardrails for the controlled LLM boundary (IPRMS).

Enforces that LLM output is advisory only and never drives a final decision.
LLM is allowed ONLY at two fallback points:
  * Agent A: PR-type classification when metadata is insufficient.
  * Agent B: vague item descriptions / unclear OCR-PDF extraction normalization.

NOT allowed (must stay rule-based): budget validation, vendor approval/preferred,
compliance decision, split-order/anomaly final decision, approval routing, and
PO draft posting/blocking. Original parser/OCR/metadata evidence is always kept.

Skeleton only — implemented in Task 4 / Task 13. See IPRMS plan §4.1.
"""
from __future__ import annotations
