from __future__ import annotations

import re
from collections import defaultdict
from collections.abc import Sequence

import numpy as np

from .public_fairlearn_v2_protocol import EXPECTED_NEW, EXPECTED_OLD

TRANSCRIPT_SCHEMA = "tfoesuu-fairlearn-public-v2-transcript-v1"
CAMPAIGN_OUTPUT_SCHEMA = "tfoesuu-fairlearn-public-v2-campaign-output-v2"
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_GIT_RE = re.compile(r"^[0-9a-f]{40}$")


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


def _protected_tuple(value: object) -> tuple[str, ...]:
    if isinstance(value, (list, tuple)):
        return tuple(str(component) for component in value)
    return (str(value),)


def _legacy_merge_map(groups: object) -> dict[tuple[str, ...], set[str]]:
    """Reproduce the pinned parent's multi-column NumPy merge behavior."""

    if not isinstance(groups, list) or not groups:
        raise ValueError("protected groups must be a nonempty list")
    values = np.asarray(groups)
    if values.ndim == 1:
        merged = values
    elif values.ndim == 2 and values.shape[1] == 1:
        merged = values[:, 0]
    elif values.ndim == 2:
        merged = np.apply_along_axis(
            lambda row: ",".join(
                str(component).replace("\\", "\\\\").replace(",", "\\,")
                for component in row
            ),
            axis=1,
            arr=values,
        )
    else:
        raise ValueError("protected groups must be a one- or two-dimensional census")
    result: dict[tuple[str, ...], set[str]] = defaultdict(set)
    for group, encoded in zip(groups, merged, strict=True):
        result[_protected_tuple(group)].add(str(encoded))
    return result


def summarize_public_fairlearn_v2_rows(
    records: Sequence[dict],
    evaluation_contexts: dict[str, dict],
) -> list[dict]:
    """Compute exact row and protected-tuple discrepancy counts.

    The campaign transcript intentionally contains no protected values.  This
    audit therefore requires the separately frozen input contexts and rejects
    any row-order drift before joining them to the exact PMFs.
    """

    by_key = {
        (row.get("dataset_id"), row.get("version")): row
        for row in records
        if isinstance(row, dict)
    }
    if len(by_key) != len(records):
        raise ValueError("row audit requires unique transcript records")
    dataset_ids = {dataset_id for dataset_id, _ in by_key}
    expected_keys = {
        (dataset_id, version)
        for dataset_id in dataset_ids
        for version in ("old", "new")
    }
    if set(by_key) != expected_keys or set(evaluation_contexts) != dataset_ids:
        raise ValueError("row audit requires a complete transcript and context census")

    reports = []
    for dataset_id in sorted(dataset_ids):
        old_record = by_key[(dataset_id, "old")]
        new_record = by_key[(dataset_id, "new")]
        context = evaluation_contexts[dataset_id]
        positions = context.get("evaluation_positions")
        groups = context.get("native_evaluation_groups")
        training_groups = context.get("native_training_groups")
        if (
            not isinstance(positions, list)
            or positions != old_record.get("source_row_positions")
            or positions != new_record.get("source_row_positions")
        ):
            raise ValueError(f"{dataset_id}: evaluation positions are not aligned")
        if not isinstance(groups, list) or len(groups) != len(positions):
            raise ValueError(f"{dataset_id}: protected groups are not aligned")
        training_map = _legacy_merge_map(training_groups)
        evaluation_map = _legacy_merge_map(groups)
        if set(training_map) != set(evaluation_map):
            raise ValueError(f"{dataset_id}: training/evaluation protected support differs")
        encoding_mismatches = [
            list(protected)
            for protected in sorted(training_map)
            if training_map[protected] != evaluation_map[protected]
        ]

        old_multi = _pmf(old_record, "multi")[:, 1]
        old_canonical = _pmf(old_record, "canonical")[:, 1]
        new_multi = _pmf(new_record, "multi")[:, 1]
        new_canonical = _pmf(new_record, "canonical")[:, 1]
        parent_difference = np.abs(old_multi - old_canonical)
        repair_difference = np.abs(new_multi - new_canonical)
        grouped: dict[tuple[str, ...], list[float]] = defaultdict(list)
        for group, difference in zip(groups, parent_difference, strict=True):
            grouped[_protected_tuple(group)].append(float(difference))

        group_reports = []
        for protected, differences in sorted(grouped.items()):
            values = np.asarray(differences, dtype=float)
            affected = int(np.count_nonzero(values))
            group_reports.append(
                {
                    "protected_tuple": list(protected),
                    "evaluation_rows": int(values.size),
                    "parent_affected_rows": affected,
                    "parent_affected_fraction": affected / int(values.size),
                    "parent_max_abs_pmf_difference": float(values.max()),
                    "parent_mean_abs_pmf_difference": float(values.mean()),
                }
            )

        parent_affected = int(np.count_nonzero(parent_difference))
        reports.append(
            {
                "dataset_id": dataset_id,
                "evaluation_rows": len(positions),
                "parent_affected_rows": parent_affected,
                "parent_affected_fraction": parent_affected / len(positions),
                "parent_max_abs_pmf_difference": float(parent_difference.max()),
                "parent_mean_abs_pmf_difference": float(parent_difference.mean()),
                "repair_affected_rows": int(np.count_nonzero(repair_difference)),
                "repair_affected_fraction": (
                    int(np.count_nonzero(repair_difference)) / len(positions)
                ),
                "parent_encoding_mismatched_group_count": len(encoding_mismatches),
                "parent_encoding_mismatched_protected_tuples": encoding_mismatches,
                "groups": group_reports,
            }
        )
    return reports


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


def validate_public_fairlearn_v2_campaign_outputs(
    old: dict,
    new: dict,
    protocol: dict,
    *,
    expected_protocol_sha256: str,
    expected_runner_commit: str,
    expected_input_bundle_manifest_sha256: str,
) -> dict:
    """Validate root provenance before admitting the paired transcript census."""

    if not _SHA256_RE.fullmatch(expected_protocol_sha256):
        raise ValueError("expected protocol SHA-256 is invalid")
    if not _GIT_RE.fullmatch(expected_runner_commit):
        raise ValueError("expected runner commit is invalid")
    if not _SHA256_RE.fullmatch(expected_input_bundle_manifest_sha256):
        raise ValueError("expected input bundle SHA-256 is invalid")
    commits = {"old": EXPECTED_OLD, "new": EXPECTED_NEW}
    documents = {"old": old, "new": new}
    approval_hashes = set()
    records = []
    for version, document in documents.items():
        if not isinstance(document, dict) or document.get("schema") != CAMPAIGN_OUTPUT_SCHEMA:
            raise ValueError(f"{version}: campaign output schema mismatch")
        if document.get("version") != version or document.get("commit") != commits[version]:
            raise ValueError(f"{version}: campaign source identity mismatch")
        if document.get("protocol_sha256") != expected_protocol_sha256:
            raise ValueError(f"{version}: campaign protocol identity mismatch")
        if (
            document.get("input_bundle_manifest_sha256")
            != expected_input_bundle_manifest_sha256
        ):
            raise ValueError(f"{version}: campaign input bundle identity mismatch")
        runner = document.get("runner")
        if (
            not isinstance(runner, dict)
            or runner.get("commit") != expected_runner_commit
            or runner.get("clean") is not True
        ):
            raise ValueError(f"{version}: campaign runner identity mismatch")
        approval = document.get("approval")
        if (
            not isinstance(approval, dict)
            or approval.get("authorized") is not True
            or approval.get("protocol_sha256") != expected_protocol_sha256
            or not _SHA256_RE.fullmatch(str(approval.get("approval_sha256", "")))
        ):
            raise ValueError(f"{version}: campaign approval identity mismatch")
        approval_hashes.add(approval["approval_sha256"])
        source = document.get("source")
        source_hashes = source.get("source_sha256") if isinstance(source, dict) else None
        if (
            not isinstance(source, dict)
            or source.get("version") != version
            or source.get("commit") != commits[version]
            or not isinstance(source_hashes, dict)
            or not source_hashes
            or any(not _SHA256_RE.fullmatch(str(value)) for value in source_hashes.values())
        ):
            raise ValueError(f"{version}: campaign source hash identity mismatch")
        runtime = document.get("runtime")
        packages = runtime.get("packages") if isinstance(runtime, dict) else None
        if (
            not isinstance(runtime, dict)
            or not str(runtime.get("python", "")).strip()
            or not str(runtime.get("platform", "")).strip()
            or not isinstance(packages, dict)
            or set(packages)
            != {"fairlearn", "numpy", "pandas", "scipy", "scikit_learn"}
            or any(not str(value).strip() for value in packages.values())
        ):
            raise ValueError(f"{version}: campaign runtime identity is incomplete")
        if (
            not str(document.get("started_at", "")).strip()
            or not str(document.get("finished_at", "")).strip()
            or isinstance(document.get("elapsed_seconds"), bool)
            or not isinstance(document.get("elapsed_seconds"), (int, float))
            or document["elapsed_seconds"] < 0.0
        ):
            raise ValueError(f"{version}: campaign timing metadata is invalid")
        version_records = document.get("records")
        if (
            not isinstance(version_records, list)
            or len(version_records) != len(protocol["datasets"])
            or any(row.get("version") != version for row in version_records)
        ):
            raise ValueError(f"{version}: campaign record partition mismatch")
        records.extend(version_records)
    if len(approval_hashes) != 1:
        raise ValueError("old/new campaign approval identity mismatch")
    report = validate_public_fairlearn_v2_transcripts(records, protocol)
    return {
        **report,
        "campaign_provenance_valid": True,
        "runner_commit": expected_runner_commit,
        "input_bundle_manifest_sha256": expected_input_bundle_manifest_sha256,
        "approval_sha256": next(iter(approval_hashes)),
    }
