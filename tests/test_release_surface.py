import hashlib
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


def test_hostile_novelty_audit_covers_every_replay_claim():
    audit_path = ROOT / "docs" / "HOSTILE_NOVELTY_AUDIT_P12_P19.md"
    assert audit_path.is_file()
    audit = audit_path.read_text(encoding="utf-8")
    lowered_audit = audit.lower()

    for claim in ("P12", "P13", "P14", "P15", "P16", "P17", "P18", "P19"):
        assert f"| {claim} |" in audit

    for required_boundary in (
        "specialized instantiation",
        "scoped extension",
        "not a novelty claim",
        "human literature sign-off",
    ):
        assert required_boundary in lowered_audit

    for primary_source in (
        "10.2307/2531961",
        "10.1214/13-AOS1144",
        "10.1109/TAC.2013.2261188",
        "10.1109/TIT.2014.2387857",
        "10.1109/TIT.2014.2363846",
        "10.1111/sjos.12757",
        "proceedings.mlr.press/v54/malek17a.html",
        "proceedings.mlr.press/v162/yan22c.html",
    ):
        assert primary_source in audit


def test_review_submission_uses_narrow_novelty_language():
    body = (ROOT / "paper" / "stoc2027_review" / "review_main_body.tex").read_text(
        encoding="utf-8"
    )
    forbidden = ("first-ever", "unprecedented", "we invent", "we introduce pairing")
    lowered = body.lower()
    assert all(phrase not in lowered for phrase in forbidden)
    assert "specialized instantiation" in body
    assert "MalekEtAl2017" in body


def test_p19_sequential_supplement_is_frozen_and_narrow():
    root = (
        ROOT
        / "paper"
        / "stoc2027_review"
        / "supplemental"
        / "p19_simple_null_20261014"
    )
    expected = {
        "p19_sequential_audit.py": (
            "0f9ccd5f17f5dd4ea31829dfc82fb2ef855cab55fe99c5653a2c54bea26fc7f1"
        ),
        "results/p19_sequential_observations.csv": (
            "3d59d674928bd93aab69dbb519ef2920aecc5c923afda43ec322a3c212089546"
        ),
    }
    for relative, digest in expected.items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest

    readme = (root / "README_RESEARCH_AUDIT.md").read_text(encoding="utf-8")
    assert "NOT the frozen PC1/PC2 P12/P15 campaign" in readme
    assert "not a historical executable Fairlearn runtime" in readme
    assert "not inferred theorem exponents" in readme


def test_unknown_shared_nuisance_manuscript_fences_support_and_domain():
    appendix = (
        ROOT
        / "paper"
        / "stoc2027_review"
        / "appendix"
        / "09_robust_matched_nuisance.tex"
    ).read_text(encoding="utf-8")
    body = (ROOT / "paper" / "stoc2027_review" / "review_main_body.tex").read_text(
        encoding="utf-8"
    )

    assert "0<p<p+\\eta<p+s<p+s+\\eta<1" in appendix
    assert "D(P_{1,p,h}\\Vert P_{0,p,h})=\\infty" in appendix
    assert "not a general" in appendix
    assert "does not extend the P19" in body
