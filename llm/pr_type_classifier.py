"""Agent A PR-type classification fallback (controlled LLM).

Used ONLY when deterministic metadata/rules cannot classify the PR type as
standard / emergency / capex. The LLM may only *suggest* a PR type; it must not
decide routing, approval, budget, vendor, compliance, anomaly, or PO rules.

When used, the suggestion, triggering reason, confidence, and model/prompt
version are recorded via llm.trace (llm_fallback_trace.json). The project must
remain fully testable with this fallback disabled or mocked.

Skeleton only — implemented in Task 4. See IPRMS plan §4.1 (Controlled LLM Boundary).
"""
from __future__ import annotations
