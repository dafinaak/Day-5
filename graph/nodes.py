"""LangGraph nodes for the IPRMS A->H pipeline skeleton.

Each node wraps a deterministic Agent function (A-H). Nodes and edges only
provide shared state, conditional routing, fallback control, and an audit trail —
they never replace deterministic business rules, and their output must match the
direct Python pipeline for the same input and config.

Skeleton only — implemented in Task 7 (deterministic pipeline runner + LangGraph
internal flow). See the IPRMS plan (Workflow / §10).
"""
from __future__ import annotations
