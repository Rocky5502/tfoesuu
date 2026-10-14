from pathlib import Path

import tomllib

ROOT = Path(__file__).resolve().parents[1]


def test_readme_names_authoritative_review_and_admitted_evidence():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "paper/stoc2027_review/main.tex" in readme
    assert "requirements-public-v2.txt" in readme
    assert "198 configurations" in readme
    assert "594 exact-law comparisons" in readme
    assert "preregistered TBD result templates" not in readme


def test_package_metadata_exposes_public_dependency_profiles():
    metadata = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    project = metadata["project"]
    extras = project["optional-dependencies"]

    def direct_requirements(filename: str) -> set[str]:
        return {
            line.strip()
            for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith(("#", "-r "))
        }

    assert set(project["dependencies"]) == direct_requirements("requirements.txt")
    assert set(extras["dev"]) == direct_requirements("requirements-dev.txt")
    assert set(extras["gpu"]) == direct_requirements("requirements-gpu.txt")
    assert set(extras["public"]) == direct_requirements("requirements-public.txt")
    assert set(extras["public-v2"]) == (
        direct_requirements("requirements-public.txt")
        | direct_requirements("requirements-public-v2.txt")
    )


def test_ci_and_makefile_enforce_review_submission_gate():
    ci = (ROOT / ".github" / "workflows" / "ci.yml").read_text(encoding="utf-8")
    paper = (ROOT / ".github" / "workflows" / "paper.yml").read_text(encoding="utf-8")
    makefile = (ROOT / "Makefile").read_text(encoding="utf-8")

    assert "python scripts/check_review_submission.py" in ci
    assert "python scripts/check_review_submission.py" in paper
    assert "paper/stoc2027_review" in paper
    assert "python scripts/check_review_submission.py" in makefile
    assert "cd paper/stoc2027_review" in makefile


def test_generated_manuscript_artifacts_are_not_versioned():
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
    assert "paper/**/build*/" in ignore
    assert "paper/**/*.pdf" in ignore
    assert "output/" in ignore
