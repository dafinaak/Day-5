"""Day 5 - Spec-Driven Development artifact checks.

These tests are documentation/spec guards only. They verify that the Day 5
artifacts exist and contain the expected content. They do NOT touch or change
any IPRMS business logic, agents, schemas, or configs.
"""

from pathlib import Path

# Repository root = parent of the tests/ directory.
ROOT = Path(__file__).resolve().parent.parent

SDD_DOC = ROOT / "docs" / "IPRMS_Spec_Driven_Development.md"
NOTEBOOK_DOC = ROOT / "docs" / "Day5_Kaggle_Notebook_Content.md"
FEATURE_FILE = ROOT / "features" / "pr_processing.feature"
README = ROOT / "README.md"

REQUIRED_SCENARIOS = [
    "Clean PR is converted into PO draft",
    "PR exceeds budget",
    "PR uses non-preferred vendor",
    "Split-order anomaly is detected",
    "Sole-source PR requires compliance review",
]


def test_sdd_doc_exists():
    assert SDD_DOC.is_file(), f"Missing: {SDD_DOC}"


def test_notebook_doc_exists():
    assert NOTEBOOK_DOC.is_file(), f"Missing: {NOTEBOOK_DOC}"


def test_feature_file_exists():
    assert FEATURE_FILE.is_file(), f"Missing: {FEATURE_FILE}"


def test_readme_has_day5_section():
    text = README.read_text(encoding="utf-8")
    assert "Day 5 - Spec-Driven Production Readiness" in text


def test_feature_file_contains_required_scenarios():
    text = FEATURE_FILE.read_text(encoding="utf-8")
    for scenario in REQUIRED_SCENARIOS:
        assert scenario in text, f"Missing scenario: {scenario}"
