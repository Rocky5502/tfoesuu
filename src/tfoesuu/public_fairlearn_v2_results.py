from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from .public_fairlearn_v2_protocol import EXPECTED_NEW, EXPECTED_OLD

TRANSCRIPT_SCHEMA = "tfoesuu-fairlearn-public-v2-transcript-v1"


def _pmf(record: dict, mode: str) -> np.ndarray:
    try:
        values = np.asarray(record["modes"][mode]["pmf"], dtype=float)
    except (KeyError, TypeError, ValueError) as exc:
        raise ValueError(f"{record.get('dataset_id')}/{record.get('version')}: invalid PMF") from exc
    rows = len(record.get("source_row_positions", ()))
    if values.shape != (rows, 2) or not np.all(np.isfinite(values)):
        raise ValueError(f"{record['dataset_id']}/{record['version']}: invalid PMF shape")
    if np.any(values < 0.0) or np.any(values > 1.0) or not np.array_equal(
        values.sum(axis=1), np.ones(rows)
    ):
        raise ValueError(f"{record['dataset_id']}/{record['version']}: invalid PMF probabilities")
    return values


def _validate_seed_records(record: dict, pmfs: dict[str, np.ndarray], seeds: list[int]) -> None:
    rows = len(record["source_row_positions"])
    for mode, pmf in pmfs.items():
        seed_records = record["modes"][mode].get("seeds")
        if not isinstance(seed_records, dict) or set(seed_records) != {str(seed) for seed in seeds}:
            raise ValueError(f"{record['dataset_id']}/{record['version']}: seed census mismatch")
        for seed in seeds:
            row = seed_records[str(seed)]
            uniforms = np.asarray(row.get("uniforms"), dtype=float)
            predictions = np.asarray(row.get("predictions"))
            if uniforms.shape != (rows,) or not np.all(
                np.isfinite(uniforms) & (uniforms >= 0.0) & (uniforms < 1.0)
            ):
                raise ValueError("invalid common uniform tape")
            expected = (pmf[:, 1] >= uniforms).astype(int)
            if (
                predictions.shape != (rows,)
                or not np.array_equal(predictions, expected)
                or row.get("threshold_correspondence") is not True
            ):
                raise ValueError("prediction threshold correspondence failed")
            if row.get("repeat_identical") is not True:
                raise ValueError("repeated seeded prediction is not identical")


def validate_public_fairlearn_v2_transcripts(
    records: Sequence[dict],
    protocol: dict,
) -> dict:
    """Validate the complete paired transcript census and compute exact estimands."""

    dataset_ids = set(protocol["datasets"])
    expected_keys = {(dataset_id, version) for dataset_id in dataset_ids for version in ("old", "new")}
    by_key = {
        (row.get("dataset_id"), row.get("version")): row
        for row in records
        if isinstance(row, dict)
    }
    if len(by_key) != len(records) or set(by_key) != expected_keys:
        raise ValueError("transcripts must contain the complete old/new census")
    commits = {"old": EXPECTED_OLD, "new": EXPECTED_NEW}
    expected_prepared = protocol["prepared_input"]["manifest_sha256"]
    expected_companion = protocol["score_model"]["companion_manifest_sha256"]
    expected_plan = protocol["runner_preflight"]["plan_sha256"]
    seeds = protocol["randomness"]["seeds"]
    parsed_pmfs: dict[tuple[str, str], dict[str, np.ndarray]] = {}

    for key, record in by_key.items():
        dataset_id, version = key
        if record.get("schema") != TRANSCRIPT_SCHEMA:
            raise ValueError(f"{dataset_id}/{version}: transcript schema mismatch")
        if record.get("commit") != commits[version]:
            raise ValueError(f"{dataset_id}/{version}: source commit mismatch")
        if record.get("prepared_manifest_sha256") != expected_prepared:
            raise ValueError(f"{dataset_id}/{version}: prepared manifest mismatch")
        if record.get("companion_manifest_sha256") != expected_companion:
            raise ValueError(f"{dataset_id}/{version}: score companion mismatch")
        if record.get("plan_sha256") != expected_plan:
            raise ValueError(f"{dataset_id}/{version}: preflight plan mismatch")
        positions = record.get("source_row_positions")
        if (
            not isinstance(positions, list)
            or not positions
            or any(isinstance(value, bool) or not isinstance(value, int) for value in positions)
            or len(set(positions)) != len(positions)
        ):
            raise ValueError(f"{dataset_id}/{version}: invalid source row positions")
        if record.get("native_group_count") != record.get("canonical_group_count"):
            raise ValueError(f"{dataset_id}/{version}: protected group cardinality mismatch")
        parsed_pmfs[key] = {mode: _pmf(record, mode) for mode in ("multi", "canonical")}

    reports = []
    for dataset_id in sorted(dataset_ids):
        old = parsed_pmfs[(dataset_id, "old")]
        new = parsed_pmfs[(dataset_id, "new")]
        if not np.array_equal(new["multi"], new["canonical"]):
            raise ValueError(f"{dataset_id}: repaired multi-column PMF differs from canonical")
        single = protocol["datasets"][dataset_id]["role"] == "single-attribute negative control"
        if single and not (
            np.array_equal(old["multi"], new["multi"])
            and np.array_equal(old["canonical"], new["canonical"])
        ):
            raise ValueError(f"{dataset_id}: single-attribute negative control changed")
        old_difference = np.abs(old["multi"][:, 1] - old["canonical"][:, 1])
        new_difference = np.abs(new["multi"][:, 1] - new["canonical"][:, 1])
        reports.append(
            {
                "dataset_id": dataset_id,
                "old_max_abs_pmf_difference": float(old_difference.max()),
                "old_mean_abs_pmf_difference": float(old_difference.mean()),
                "new_max_abs_pmf_difference": float(new_difference.max()),
                "new_mean_abs_pmf_difference": float(new_difference.mean()),
            }
        )

    for record in by_key.values():
        _validate_seed_records(
            record,
            parsed_pmfs[(record["dataset_id"], record["version"])],
            seeds,
        )
    for dataset_id in dataset_ids:
        reference = by_key[(dataset_id, "old")]["modes"]["multi"]["seeds"]
        for seed in seeds:
            expected_uniforms = reference[str(seed)]["uniforms"]
            for version in ("old", "new"):
                for mode in ("multi", "canonical"):
                    observed = by_key[(dataset_id, version)]["modes"][mode]["seeds"][str(seed)][
                        "uniforms"
                    ]
                    if observed != expected_uniforms:
                        raise ValueError(f"{dataset_id}: common uniform tape drift")

    return {
        "schema": "tfoesuu-fairlearn-public-v2-validation-v1",
        "record_count": len(records),
        "datasets": reports,
        "new_repair_conformance": True,
        "single_attribute_negative_controls": True,
        "scope": "paired-software-behavior-only",
    }
