import hashlib
import json
from pathlib import Path

import numpy as np
import pytest

from tfoesuu.public_benchmarks import public_benchmark_registry_v1
from tfoesuu.public_benchmarks_v2 import (
    V2_NPZ_KEYS,
    canonical_scalar_token,
    evaluation_alignment_sha256,
    training_alignment_sha256,
    validate_prepared_public_v2_directory,
)
from tfoesuu.public_score_companion_v2 import (
    SCORE_NPZ_KEYS,
    score_alignment_sha256,
    validate_public_score_companion_v2,
)

SHA = "583190edf7fe238331dd5123525b168f8a87c6bd"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _write_v2_directory(root: Path, source_root: Path) -> None:
    manifest = []
    for index, spec in enumerate(public_benchmark_registry_v1()):
        source_path = source_root / f"{spec.benchmark_id}.source"
        source_path.write_bytes(f"source-{spec.benchmark_id}\n".encode())
        n_rows = 4
        probabilities = np.array([0.2, 0.4, 0.6, 0.7], dtype=np.float64)
        labels = np.array([0, 1, 0, 1], dtype=np.int8)
        positions = np.array([1, 3, 7, 9], dtype=np.int64)
        training_labels = np.array([1, 0, 1, 0, 1, 0, 1, 0], dtype=np.int8)
        training_positions = np.array([0, 2, 4, 5, 6, 8, 10, 11], dtype=np.int64)
        protected = np.array(
            [
                [canonical_scalar_token(f"g{row % 2}-{col}") for col in range(len(spec.protected_attributes))]
                for row in range(n_rows)
            ],
            dtype=np.str_,
        )
        features = np.array(
            [[canonical_scalar_token(row), canonical_scalar_token(float(row) / 10)] for row in range(n_rows)],
            dtype=np.str_,
        )
        training_protected = protected[[1, 0, 3, 2, 1, 0, 3, 2]].copy()
        training_features = features[[1, 0, 3, 2, 1, 0, 3, 2]].copy()
        arrays = {
            "baseline_probabilities": probabilities,
            "evaluation_labels": labels,
            "source_row_positions": positions,
            "protected_attribute_values": protected,
            "non_protected_feature_values": features,
            "training_labels": training_labels,
            "training_source_row_positions": training_positions,
            "training_protected_attribute_values": training_protected,
            "training_non_protected_feature_values": training_features,
        }
        assert set(arrays) == V2_NPZ_KEYS
        np.savez_compressed(root / f"{spec.benchmark_id}.npz", **arrays)
        all_protected = np.concatenate((training_protected, protected), axis=0)
        catalog = {
            name: sorted(set(all_protected[:, col].tolist()))
            for col, name in enumerate(spec.protected_attributes)
        }
        evaluation_joint_counts: dict[str, int] = {}
        for row in protected.tolist():
            key = json.dumps(row, separators=(",", ":"))
            evaluation_joint_counts[key] = evaluation_joint_counts.get(key, 0) + 1
        training_joint_counts: dict[str, int] = {}
        for row in training_protected.tolist():
            key = json.dumps(row, separators=(",", ":"))
            training_joint_counts[key] = training_joint_counts.get(key, 0) + 1
        metadata = {
            "schema": "tfoesuu-public-context-v2.1",
            "dataset_id": spec.benchmark_id,
            "dataset_name": spec.name,
            "source_url": spec.source_url,
            "source_doi": spec.doi,
            "protected_attributes": list(spec.protected_attributes),
            "protected_columns": list(spec.protected_attributes),
            "protected_semantics": {
                name: f"source-defined {name} category"
                for name in spec.protected_attributes
            },
            "non_protected_feature_columns": ["feature-a", "feature-b"],
            "canonical_loaded_data_sha256": f"{index + 1:064x}",
            "source_artifacts": [
                {
                    "relative_path": source_path.name,
                    "bytes": source_path.stat().st_size,
                    "sha256": _sha256(source_path),
                }
            ],
            "split_seed": 20271008,
            "rows_loaded": 12,
            "train_rows": 8,
            "heldout_rows": 4,
            "evaluation_contexts": n_rows,
            "max_contexts": n_rows,
            "base_predictor": "test predictor",
            "base_accuracy": 0.75,
            "probability_clip": [0.1, 0.8],
            "preparation_source_commit": SHA,
            "preparation_environment": {
                "python": "3.12.0",
                "platform": "test-platform",
                "packages": {
                    "aif360": "0.6.1",
                    "numpy": "2.0.0",
                    "pandas": "2.2.0",
                    "scikit-learn": "1.5.0",
                    "ucimlrepo": "0.0.7",
                    "xlrd": "2.0.2",
                },
            },
            "row_id_semantics": "zero-based canonical-loaded row position",
            "value_encoding": "canonical-json-scalars-v1",
            "protected_missing_policy": "explicit-category",
            "counterfactual_semantics": "observational-context-only",
            "counterfactual_transform": {
                "status": "not-defined",
                "reason": "no causal intervention is identified by this artifact",
            },
            "identifiability_scope": "observed-joint-group-comparisons-only",
            "minimum_joint_group_support": 2,
            "protected_value_catalog": catalog,
            "training_joint_group_counts": training_joint_counts,
            "evaluation_joint_group_counts": evaluation_joint_counts,
            "training_alignment_sha256": training_alignment_sha256(
                training_labels=training_labels,
                training_source_row_positions=training_positions,
                training_protected_attribute_values=training_protected,
                training_non_protected_feature_values=training_features,
            ),
            "evaluation_alignment_sha256": evaluation_alignment_sha256(
                baseline_probabilities=probabilities,
                evaluation_labels=labels,
                source_row_positions=positions,
                protected_attribute_values=protected,
                non_protected_feature_values=features,
            ),
        }
        (root / f"{spec.benchmark_id}.json").write_text(
            json.dumps(metadata, sort_keys=True), encoding="utf-8"
        )
        manifest.append(metadata)
    (root / "prepared_v2_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8"
    )


@pytest.fixture
def v2_directory(tmp_path: Path) -> tuple[Path, Path]:
    prepared = tmp_path / "prepared_v2"
    sources = tmp_path / "sources"
    prepared.mkdir()
    sources.mkdir()
    _write_v2_directory(prepared, sources)
    return prepared, sources


def _write_score_companion(root: Path, prepared: Path) -> None:
    datasets = []
    for spec in public_benchmark_registry_v1():
        with np.load(prepared / f"{spec.benchmark_id}.npz", allow_pickle=False) as source:
            training_positions = source["training_source_row_positions"]
            evaluation_positions = source["source_row_positions"]
            evaluation_scores = source["baseline_probabilities"]
        training_scores = np.linspace(0.1, 0.8, len(training_positions), dtype=np.float64)
        arrays = {
            "training_source_row_positions": training_positions,
            "evaluation_source_row_positions": evaluation_positions,
            "training_scores": training_scores,
            "evaluation_scores": evaluation_scores,
        }
        assert set(arrays) == SCORE_NPZ_KEYS
        np.savez_compressed(root / f"{spec.benchmark_id}.npz", **arrays)
        prepared_metadata = json.loads(
            (prepared / f"{spec.benchmark_id}.json").read_text(encoding="utf-8")
        )
        metadata = {
            "schema": "tfoesuu-public-score-companion-v2.2",
            "dataset_id": spec.benchmark_id,
            "prepared_training_alignment_sha256": prepared_metadata[
                "training_alignment_sha256"
            ],
            "prepared_evaluation_alignment_sha256": prepared_metadata[
                "evaluation_alignment_sha256"
            ],
            "model_contract": "V2.1 logistic regression, clipped to [0.1,0.8]",
            "score_alignment_sha256": score_alignment_sha256(**arrays),
        }
        (root / f"{spec.benchmark_id}.json").write_text(
            json.dumps(metadata, sort_keys=True), encoding="utf-8"
        )
        datasets.append(metadata)
    manifest = {
        "schema": "tfoesuu-public-score-companion-v2.2",
        "prepared_manifest_sha256": _sha256(prepared / "prepared_v2_manifest.json"),
        "preparation_source_commit": SHA,
        "datasets": datasets,
    }
    (root / "score_companion_manifest.json").write_text(
        json.dumps(manifest, sort_keys=True), encoding="utf-8"
    )


def test_v2_validator_accepts_aligned_complete_artifacts(v2_directory):
    prepared, sources = v2_directory

    report = validate_prepared_public_v2_directory(
        prepared,
        expected_source_commit=SHA,
        source_root=sources,
    )

    assert len(report["dataset_ids"]) == 7
    assert report["multicolumn_materialized_ids"] == [
        "public-adult",
        "public-compas",
        "public-default-credit",
        "public-german",
        "public-lawschool",
    ]
    assert report["source_bytes_verified"] is True
    assert report["readiness_scope"] == "representation-only"
    assert report["outcome_ready"] is False


def test_score_companion_accepts_complete_aligned_scores(v2_directory, tmp_path):
    prepared, _ = v2_directory
    companion = tmp_path / "score_companion"
    companion.mkdir()
    _write_score_companion(companion, prepared)

    report = validate_public_score_companion_v2(companion, prepared)

    assert report["dataset_ids"] == sorted(
        spec.benchmark_id for spec in public_benchmark_registry_v1()
    )
    assert report["evaluation_scores_reproduce_v2"] is True
    assert report["outcome_ready"] is False


def test_score_companion_rejects_training_score_reorder(v2_directory, tmp_path):
    prepared, _ = v2_directory
    companion = tmp_path / "score_companion"
    companion.mkdir()
    _write_score_companion(companion, prepared)
    path = companion / "public-adult.npz"
    with np.load(path, allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    arrays["training_scores"] = arrays["training_scores"][::-1]
    np.savez_compressed(path, **arrays)

    with pytest.raises(ValueError, match="score alignment"):
        validate_public_score_companion_v2(companion, prepared)


def test_score_companion_rejects_evaluation_score_drift(v2_directory, tmp_path):
    prepared, _ = v2_directory
    companion = tmp_path / "score_companion"
    companion.mkdir()
    _write_score_companion(companion, prepared)
    path = companion / "public-meps21.npz"
    with np.load(path, allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    arrays["evaluation_scores"] = arrays["evaluation_scores"].copy()
    arrays["evaluation_scores"][0] += 0.01
    np.savez_compressed(path, **arrays)

    with pytest.raises(ValueError, match="evaluation scores do not reproduce"):
        validate_public_score_companion_v2(companion, prepared)


def test_score_companion_rejects_prepared_manifest_drift(v2_directory, tmp_path):
    prepared, _ = v2_directory
    companion = tmp_path / "score_companion"
    companion.mkdir()
    _write_score_companion(companion, prepared)
    manifest = prepared / "prepared_v2_manifest.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(ValueError, match="prepared manifest SHA-256"):
        validate_public_score_companion_v2(companion, prepared)


def test_v2_validator_rejects_missing_protected_column(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-adult.npz"
    with np.load(path, allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    arrays["protected_attribute_values"] = arrays["protected_attribute_values"][:, :1]
    np.savez_compressed(path, **arrays)

    with pytest.raises(ValueError, match="protected matrix shape"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_protected_row_reordering(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-adult.npz"
    with np.load(path, allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    arrays["protected_attribute_values"] = arrays["protected_attribute_values"][[1, 0, 2, 3]]
    np.savez_compressed(path, **arrays)

    with pytest.raises(ValueError, match="alignment SHA-256"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_training_row_reordering(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-adult.npz"
    with np.load(path, allow_pickle=False) as stored:
        arrays = {name: stored[name] for name in stored.files}
    arrays["training_protected_attribute_values"] = arrays[
        "training_protected_attribute_values"
    ][[1, 0, 2, 3, 4, 5, 6, 7]]
    np.savez_compressed(path, **arrays)

    with pytest.raises(ValueError, match="training alignment SHA-256"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_protected_feature_leakage(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-german.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["non_protected_feature_columns"][0] = "sex"
    path.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
    _replace_manifest_row(prepared, metadata)

    with pytest.raises(ValueError, match="protected-feature leakage"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_category_catalog_drift(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-compas.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["protected_value_catalog"]["race"].append(canonical_scalar_token("invented"))
    path.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
    _replace_manifest_row(prepared, metadata)

    with pytest.raises(ValueError, match="protected value catalog"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_insufficient_joint_group_support(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-adult.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["minimum_joint_group_support"] = 5
    path.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
    _replace_manifest_row(prepared, metadata)

    with pytest.raises(ValueError, match="fewer than two supported joint groups"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_incomplete_environment_lock(v2_directory):
    prepared, sources = v2_directory
    path = prepared / "public-bank.json"
    metadata = json.loads(path.read_text(encoding="utf-8"))
    metadata["preparation_environment"]["packages"].pop("ucimlrepo")
    path.write_text(json.dumps(metadata, sort_keys=True), encoding="utf-8")
    _replace_manifest_row(prepared, metadata)

    with pytest.raises(ValueError, match="incomplete preparation environment"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def test_v2_validator_rejects_source_byte_mismatch(v2_directory):
    prepared, sources = v2_directory
    source = sources / "public-lawschool.source"
    source.write_bytes(b"x" * source.stat().st_size)

    with pytest.raises(ValueError, match="source artifact .* SHA-256 mismatch"):
        validate_prepared_public_v2_directory(prepared, source_root=sources)


def _replace_manifest_row(prepared: Path, metadata: dict) -> None:
    path = prepared / "prepared_v2_manifest.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))
    manifest = [metadata if row["dataset_id"] == metadata["dataset_id"] else row for row in manifest]
    path.write_text(json.dumps(manifest, sort_keys=True), encoding="utf-8")
