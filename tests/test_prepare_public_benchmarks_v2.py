import json
from pathlib import Path

import pytest

from scripts.prepare_public_benchmarks_v2 import (
    load_source_map,
    partition_feature_columns,
)


def test_v2_preparer_requires_every_protected_column():
    with pytest.raises(ValueError, match="missing declared protected columns"):
        partition_feature_columns(
            "public-adult",
            ["income", "sex"],
            ("sex", "race"),
        )


def test_v2_preparer_removes_protected_columns_without_case_alias_leakage():
    protected, features = partition_feature_columns(
        "public-default-credit",
        ["LIMIT_BAL", "SEX", "AGE", "PAY_0"],
        ("SEX", "AGE"),
    )

    assert protected == ["SEX", "AGE"]
    assert features == ["LIMIT_BAL", "PAY_0"]


def test_v2_preparer_rejects_casefold_ambiguous_columns():
    with pytest.raises(ValueError, match="case-insensitive duplicate"):
        partition_feature_columns(
            "public-german",
            ["sex", "SEX", "age", "credit"],
            ("sex", "age"),
        )


def test_source_map_is_explicit_relative_and_complete(tmp_path: Path):
    path = tmp_path / "sources.json"
    path.write_text(
        json.dumps({"public-adult": ["adult/raw.csv"]}),
        encoding="utf-8",
    )

    assert load_source_map(path, ["public-adult"]) == {
        "public-adult": ["adult/raw.csv"]
    }
    with pytest.raises(ValueError, match="missing selected dataset"):
        load_source_map(path, ["public-adult", "public-bank"])


@pytest.mark.parametrize("bad_path", ["../escape.csv", "/absolute.csv", "C:/absolute.csv"])
def test_source_map_rejects_nonrelative_paths(tmp_path: Path, bad_path: str):
    path = tmp_path / "sources.json"
    path.write_text(json.dumps({"public-adult": [bad_path]}), encoding="utf-8")

    with pytest.raises(ValueError, match="relative source path"):
        load_source_map(path, ["public-adult"])
