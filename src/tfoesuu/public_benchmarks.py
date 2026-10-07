from __future__ import annotations

from dataclasses import asdict, dataclass
import json
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class PublicBenchmarkSpec:
    """Metadata contract for one planned public fairness-regression subject.

    These entries identify public input populations.  They do not encode
    empirical TFOESUU results.  The old/new executable software versions,
    stochastic patch, seeds, and train/evaluation split are generated locally.
    """

    benchmark_id: str
    name: str
    task: str
    protected_attributes: tuple[str, ...]
    source: str
    source_url: str
    doi: str | None
    loader_family: str
    status: str


def public_benchmark_registry_v1() -> list[PublicBenchmarkSpec]:
    """Frozen v1 registry for the submission-facing public benchmark layer."""
    return [
        PublicBenchmarkSpec(
            benchmark_id="public-adult",
            name="Adult Census Income",
            task="binary-classification",
            protected_attributes=("sex", "race"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/2/adult",
            doi="10.24432/C5XW20",
            loader_family="uci",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-bank",
            name="Bank Marketing",
            task="binary-classification",
            protected_attributes=("age",),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/222/bank+marketing",
            doi="10.24432/C5K306",
            loader_family="uci",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-german",
            name="Statlog German Credit",
            task="binary-classification",
            protected_attributes=("sex", "age"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/144/statlog+german+credit+data",
            doi="10.24432/C5NC77",
            loader_family="uci",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-compas",
            name="ProPublica COMPAS",
            task="binary-classification",
            protected_attributes=("race", "sex"),
            source="ProPublica compas-analysis",
            source_url="https://github.com/propublica/compas-analysis",
            doi=None,
            loader_family="propublica",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-lawschool",
            name="Law School GPA",
            task="regression-to-thresholded-decision",
            protected_attributes=("race", "gender"),
            source="AIF360 LawSchoolGPADataset",
            source_url="https://aif360.readthedocs.io/en/latest/modules/generated/aif360.datasets.LawSchoolGPADataset.html",
            doi=None,
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-meps21",
            name="MEPS Panel 21",
            task="binary-classification",
            protected_attributes=("race",),
            source="AIF360 / AHRQ MEPS",
            source_url="https://aif360.readthedocs.io/en/latest/modules/generated/aif360.sklearn.datasets.fetch_meps.html",
            doi=None,
            loader_family="aif360",
            status="planned",
        ),
        PublicBenchmarkSpec(
            benchmark_id="public-default-credit",
            name="Default of Credit Card Clients",
            task="binary-classification",
            protected_attributes=("sex", "age"),
            source="UCI Machine Learning Repository",
            source_url="https://archive.ics.uci.edu/dataset/350/default+of+credit+card+clients",
            doi="10.24432/C55S3H",
            loader_family="uci",
            status="planned",
        ),
    ]


def write_public_benchmark_registry(
    rows: Iterable[PublicBenchmarkSpec],
    path: str | Path,
) -> None:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as fh:
        for row in rows:
            payload = asdict(row)
            payload["protected_attributes"] = list(row.protected_attributes)
            fh.write(json.dumps(payload, sort_keys=True) + "\n")


def read_public_benchmark_registry(
    path: str | Path,
) -> list[PublicBenchmarkSpec]:
    rows: list[PublicBenchmarkSpec] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            payload = json.loads(line)
            payload["protected_attributes"] = tuple(payload["protected_attributes"])
            rows.append(PublicBenchmarkSpec(**payload))
    return rows
