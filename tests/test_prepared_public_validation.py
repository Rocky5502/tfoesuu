import json
from pathlib import Path

import numpy as np
import pytest

from tfoesuu.public_benchmarks import (
    public_benchmark_registry_v1,
    validate_prepared_public_directory,
)

SHA = "149baf36fe7fa4c5d9bf96a0fcee445566fc9f8b"


def _write_prepared_directory(root: Path) -> None:
    manifest = []
    for index, spec in enumerate(public_benchmark_registry_v1()):
        probabilities = np.array([0.2, 0.4, 0.7], dtype=np.float64)
        labels = np.array([0, 1, index % 2], dtype=np.int8)
        np.savez_compressed(
            root / f"{spec.benchmark_id}.npz",
            baseline_probabilities=probabilities,
            evaluation_labels=labels,
        )
        metadata = {
            "dataset_id": spec.benchmark_id,
            "dataset_name": spec.name,
            "source_url": spec.source_url,
            "source_doi": spec.doi,
            "protected_attributes": list(spec.protected_attributes),
            "canonical_loaded_data_sha256": f"{index + 1:064x}",
            "split_seed": 20271008,
            "rows_loaded": 12,
            "train_rows": 9,
            "evaluation_contexts": 3,
            "max_contexts": 3,
            "base_predictor": "test predictor",
            "base_accuracy": 0.75,
            "probability_clip": [0.1, 0.8],
            "preparation_source_commit": SHA,
            "target_transform": "test binary target",
        }
        (root / f"{spec.benchmark_id}.json").write_text(
            json.dumps(metadata), encoding="utf-8"
        )
        manifest.append(metadata)
    (root / "prepared_manifest.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def test_strict_prepared_directory_validation_accepts_coherent_artifacts(tmp_path: Path):
    _write_prepared_directory(tmp_path)
    report = validate_prepared_public_directory(tmp_path, expected_source_commit=SHA)

    assert report["dataset_ids"] == sorted(
        spec.benchmark_id for spec in public_benchmark_registry_v1()
    )
    assert report["source_commit"] == SHA
    assert len(report["files"]) == 15
    assert all(len(entry["sha256"]) == 64 for entry in report["files"])


@pytest.mark.parametrize("bad_probability", [np.nan, np.inf, 0.0, 1.0])
def test_strict_validation_rejects_nonfinite_or_boundary_probabilities(
    tmp_path: Path, bad_probability: float
):
    _write_prepared_directory(tmp_path)
    dataset_id = "public-adult"
    np.savez_compressed(
        tmp_path / f"{dataset_id}.npz",
        baseline_probabilities=np.array([0.2, bad_probability, 0.7]),
        evaluation_labels=np.array([0, 1, 0], dtype=np.int8),
    )

    with pytest.raises(ValueError, match="finite interior probabilities"):
        validate_prepared_public_directory(tmp_path, expected_source_commit=SHA)


def test_strict_validation_rejects_label_length_mismatch(tmp_path: Path):
    _write_prepared_directory(tmp_path)
    dataset_id = "public-bank"
    np.savez_compressed(
        tmp_path / f"{dataset_id}.npz",
        baseline_probabilities=np.array([0.2, 0.4, 0.7]),
        evaluation_labels=np.array([0, 1], dtype=np.int8),
    )

    with pytest.raises(ValueError, match="label length"):
        validate_prepared_public_directory(tmp_path, expected_source_commit=SHA)


def test_strict_validation_rejects_manifest_metadata_drift(tmp_path: Path):
    _write_prepared_directory(tmp_path)
    meta_path = tmp_path / "public-compas.json"
    metadata = json.loads(meta_path.read_text(encoding="utf-8"))
    metadata["rows_loaded"] += 1
    meta_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="does not match manifest"):
        validate_prepared_public_directory(tmp_path, expected_source_commit=SHA)


def test_strict_validation_rejects_missing_registered_dataset(tmp_path: Path):
    _write_prepared_directory(tmp_path)
    (tmp_path / "public-german.npz").unlink()

    with pytest.raises(ValueError, match="prepared NPZ IDs"):
        validate_prepared_public_directory(tmp_path, expected_source_commit=SHA)


def test_strict_validation_rejects_source_commit_mismatch(tmp_path: Path):
    _write_prepared_directory(tmp_path)

    with pytest.raises(ValueError, match="source commit"):
        validate_prepared_public_directory(
            tmp_path,
            expected_source_commit="0" * 40,
        )
