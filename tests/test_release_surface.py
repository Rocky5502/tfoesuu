"""Reviewer-facing source, packaging, and frozen-evidence regression checks."""

from __future__ import annotations

import hashlib
import tomllib
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[1]


def _sha256(relative: str) -> str:
    return hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()


def test_code_only_tree_has_scoped_review_entrypoint() -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    guide = (ROOT / "docs/REVIEWER_GUIDE.md").read_text(encoding="utf-8")
    assert not (ROOT / "paper").exists()
    assert "reproducibility/p12_p15" in readme
    assert "reproducibility/p19_simple_null" in readme
    assert "198 archived configurations" in readme
    assert "594 exact-law checks" in readme
    assert "not" in guide.lower() and "causal" in guide.lower()
    assert "python -m pytest -q" in readme
    assert (ROOT / "LICENSE").is_file()


def test_accessible_vector_diagram_is_valid_xml() -> None:
    root = ElementTree.parse(ROOT / "docs/assets/tfoesuu-architecture.svg").getroot()
    assert root.tag.endswith("svg")
    assert root.attrib["viewBox"] == "0 0 1200 580"
    tags = {element.tag.rsplit("}", 1)[-1] for element in root.iter()}
    assert "title" in tags and "desc" in tags


def test_dependency_profiles_match_pyproject() -> None:
    data = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = data["project"]
    extras = project["optional-dependencies"]

    def direct_requirements(name: str) -> set[str]:
        return {
            item.strip()
            for item in (ROOT / name).read_text(encoding="utf-8").splitlines()
            if item.strip() and not item.lstrip().startswith(("#", "-r "))
        }

    assert set(project["dependencies"]) == direct_requirements("requirements.txt")
    for extra, file in (
        ("dev", "requirements-dev.txt"),
        ("gpu", "requirements-gpu.txt"),
        ("public", "requirements-public.txt"),
    ):
        assert set(extras[extra]) == direct_requirements(file)
    assert set(extras["public-v2"]) == (
        direct_requirements("requirements-public.txt")
        | direct_requirements("requirements-public-v2.txt")
    )


def test_ci_checks_code_and_frozen_evidence_not_manuscript() -> None:
    ci = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")
    make = (ROOT / "Makefile").read_text(encoding="utf-8")
    assert "python -m pytest -q" in ci
    assert "reproducibility/p12_p15" in ci
    assert "reproducibility/p19_simple_null" in ci
    assert "paper/stoc2027_review" not in ci
    assert "evidence-check:" in make
    assert not (ROOT / ".github/workflows/paper.yml").exists()


def test_original_frozen_audits_preserved_byte_for_byte() -> None:
    expected = {
        "reproducibility/p12_p15/results/preview100k-p12-pc2-149baf36-20261008T170650Z.jsonl":
            "f00458f50d225c8c5bde5cb235c6f67fbc67102157768369df8cd350956f1035",
        "reproducibility/p12_p15/results/preview100k-p15-pc1-149baf36-20261008T170640Z.jsonl":
            "e0750e5d46215909aa710d83bca8ad748877e66f786aa9106e883ce94da274ab",
        "reproducibility/p19_simple_null/p19_sequential_audit.py":
            "0f9ccd5f17f5dd4ea31829dfc82fb2ef855cab55fe99c5653a2c54bea26fc7f1",
        "reproducibility/p19_simple_null/results/p19_sequential_observations.csv":
            "3d59d674928bd93aab69dbb519ef2920aecc5c923afda43ec322a3c212089546",
    }
    for path, digest in expected.items():
        assert _sha256(path) == digest, path


def test_scope_fences_remain_explicit() -> None:
    p19 = (ROOT / "reproducibility/p19_simple_null/README_RESEARCH_AUDIT.md").read_text(
        encoding="utf-8"
    )
    nuisance = (ROOT / "reproducibility/unknown_shared_nuisance/README.md").read_text(
        encoding="utf-8"
    )
    assert "not a historical executable Fairlearn runtime" in p19
    assert "not inferred theorem exponents" in p19
    assert "not a general composite-nuisance theorem" in nuisance
