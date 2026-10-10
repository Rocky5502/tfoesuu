"""Python 3.8-compatible core for the approval-gated Fairlearn runner."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import numpy as np

APPROVAL_SCHEMA = "tfoesuu-public-v2-approval-v1"
APPROVAL_SCOPE = "bounded-seven-dataset-fairlearn-v2"
OLD_COMMIT = "e8cc63784de5410805c156715175fc60e2cd5653"
NEW_COMMIT = "0cf59eccfdd364417787fe2c368a1c77c3f378b8"
SEEDS = [1, 104729, 130363, 155921]
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TRANSCRIPT_SCHEMA = "tfoesuu-fairlearn-public-v2-transcript-v1"
INPUT_BUNDLE_SCHEMA = "tfoesuu-fairlearn-public-v2-input-bundle-v1"
DATASET_INPUT_SCHEMA = "tfoesuu-fairlearn-public-v2-dataset-input-v1"
EXPECTED_CHECKOUT_SHA256 = {
    "old": {
        "LICENSE": "f95d3cc5bcd913e7f5cb67ad17f8e0c8796e9b1adf96b5395a81c3d5f976d79a",
        "requirements.txt": "3c850a414d8c27a7e51fd9f2eecfe55a743c4dabb3600bccdb2e82b046dac611",
        "fairlearn/_input_validation.py": (
            "0210b9b1e99caef84821554e543d574cc2b17c5b82339730b3d6533a6d93b273"
        ),
        "fairlearn/postprocessing/_threshold_optimizer.py": (
            "a59d2ec8a1ec52cec184030576744f57d7f55eac1232a5de2527853445a4bbbe"
        ),
        "fairlearn/postprocessing/_interpolated_thresholder.py": (
            "e262c6d2970b3ba1151e02971e2431ed413802edfaea6117df88abdb28d66b5a"
        ),
    },
    "new": {
        "LICENSE": "f95d3cc5bcd913e7f5cb67ad17f8e0c8796e9b1adf96b5395a81c3d5f976d79a",
        "requirements.txt": "3c850a414d8c27a7e51fd9f2eecfe55a743c4dabb3600bccdb2e82b046dac611",
        "fairlearn/_input_validation.py": (
            "6ddfac320e0351d60fa1d97096f698af946f35be55a221f84ebe5cc012059284"
        ),
        "fairlearn/postprocessing/_threshold_optimizer.py": (
            "a59d2ec8a1ec52cec184030576744f57d7f55eac1232a5de2527853445a4bbbe"
        ),
        "fairlearn/postprocessing/_interpolated_thresholder.py": (
            "e262c6d2970b3ba1151e02971e2431ed413802edfaea6117df88abdb28d66b5a"
        ),
    },
}


def _sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


class ScoreLookupEstimator:
    """Prefit estimator mapping immutable source-row positions to scores."""

    def __init__(self, positions, scores):
        positions_array = np.asarray(positions)
        scores_array = np.asarray(scores, dtype=float)
        if positions_array.ndim != 1 or scores_array.shape != positions_array.shape:
            raise ValueError("positions and scores must be aligned vectors")
        if len({int(value) for value in positions_array}) != len(positions_array):
            raise ValueError("score lookup positions must be unique")
        if not np.all(np.isfinite(scores_array)):
            raise ValueError("score lookup values must be finite")
        self._scores = {
            int(position): float(score)
            for position, score in zip(positions_array, scores_array)
        }
        # scikit-learn's check_is_fitted accepts a trailing-underscore attribute.
        self.is_fitted_ = True

    def fit(self, X, y=None):
        return self

    def predict(self, X):
        rows = np.asarray(X)
        if rows.ndim == 2 and rows.shape[1] == 1:
            rows = rows[:, 0]
        if rows.ndim != 1:
            raise ValueError("score lookup X must contain one source-row column")
        missing = [int(value) for value in rows if int(value) not in self._scores]
        if missing:
            raise ValueError(f"score lookup received unknown source rows: {missing[:5]}")
        return np.asarray([self._scores[int(value)] for value in rows], dtype=float)


def _read_json_object(path, name):
    try:
        value = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError(f"{name} is unreadable or invalid") from exc
    if not isinstance(value, dict):
        raise TypeError(f"{name} must be a JSON object")
    return value


def _float_hex_vector(values, name):
    if not isinstance(values, list) or not values:
        raise ValueError(f"{name} must be a nonempty list")
    try:
        decoded = [float.fromhex(value) for value in values]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} contains an invalid hexadecimal float") from exc
    if not np.all(np.isfinite(decoded)):
        raise ValueError(f"{name} must contain finite scores")
    return decoded


def load_runner_input_bundle(bundle_dir, protocol_path):
    """Validate and load an immutable, outcome-free runner input bundle."""

    root = Path(bundle_dir)
    protocol_file = Path(protocol_path)
    if not root.is_dir() or not protocol_file.is_file():
        raise ValueError("runner input bundle and protocol must exist")
    protocol = _read_json_object(protocol_file, "analysis protocol")
    manifest = _read_json_object(
        root / "input_bundle_manifest.json", "runner input bundle manifest"
    )
    if manifest.get("schema") != INPUT_BUNDLE_SCHEMA:
        raise ValueError("runner input bundle schema mismatch")
    expected_identities = {
        "protocol_sha256": _sha256(protocol_file),
        "prepared_manifest_sha256": protocol.get("prepared_input", {}).get(
            "manifest_sha256"
        ),
        "companion_manifest_sha256": protocol.get("score_model", {}).get(
            "companion_manifest_sha256"
        ),
        "plan_sha256": protocol.get("runner_preflight", {}).get("plan_sha256"),
    }
    if any(manifest.get(name) != value for name, value in expected_identities.items()):
        raise ValueError("runner input bundle protocol identity mismatch")
    expected_ids = set(protocol.get("datasets", {}))
    rows = manifest.get("datasets")
    if not expected_ids or not isinstance(rows, list):
        raise ValueError("runner input bundle dataset census is invalid")
    by_id = {
        row.get("dataset_id"): row
        for row in rows
        if isinstance(row, dict) and isinstance(row.get("dataset_id"), str)
    }
    if len(by_id) != len(rows) or set(by_id) != expected_ids:
        raise ValueError("runner input bundle dataset census mismatch")
    expected_files = {"input_bundle_manifest.json"}
    loaded = []
    for dataset_id in sorted(expected_ids):
        row = by_id[dataset_id]
        expected_path = f"{dataset_id}.json"
        if row.get("path") != expected_path:
            raise ValueError(f"{dataset_id}: runner input path mismatch")
        path = root / expected_path
        expected_files.add(expected_path)
        if (
            not path.is_file()
            or isinstance(row.get("bytes"), bool)
            or row.get("bytes") != path.stat().st_size
            or not isinstance(row.get("sha256"), str)
            or not _SHA256_RE.fullmatch(row["sha256"])
            or row["sha256"] != _sha256(path)
        ):
            raise ValueError(f"{dataset_id}: runner input file identity mismatch")
        payload = _read_json_object(path, f"{dataset_id} runner input")
        if payload.get("schema") != DATASET_INPUT_SCHEMA:
            raise ValueError(f"{dataset_id}: runner input schema mismatch")
        if payload.get("dataset_id") != dataset_id:
            raise ValueError(f"{dataset_id}: runner input dataset identity mismatch")
        loaded.append(
            {
                "dataset_id": dataset_id,
                "training_positions": payload.get("training_positions"),
                "training_scores": _float_hex_vector(
                    payload.get("training_score_hex"), "training_score_hex"
                ),
                "training_labels": payload.get("training_labels"),
                "evaluation_positions": payload.get("evaluation_positions"),
                "evaluation_scores": _float_hex_vector(
                    payload.get("evaluation_score_hex"), "evaluation_score_hex"
                ),
                "native_training_groups": payload.get("native_training_groups"),
                "native_evaluation_groups": payload.get("native_evaluation_groups"),
                "canonical_training_groups": payload.get("canonical_training_groups"),
                "canonical_evaluation_groups": payload.get("canonical_evaluation_groups"),
                "prepared_manifest_sha256": expected_identities[
                    "prepared_manifest_sha256"
                ],
                "companion_manifest_sha256": expected_identities[
                    "companion_manifest_sha256"
                ],
                "plan_sha256": expected_identities["plan_sha256"],
                "seeds": protocol.get("randomness", {}).get("seeds", SEEDS),
            }
        )
    actual_files = {path.name for path in root.iterdir() if path.is_file()}
    if actual_files != expected_files:
        raise ValueError("runner input bundle contains an unexpected file census")
    return loaded


def validate_subject_checkout(checkout, version):
    """Require the exact clean pinned source tree before subject import."""

    root = Path(checkout).resolve()
    expected_commits = {"old": OLD_COMMIT, "new": NEW_COMMIT}
    if version not in expected_commits or not root.is_dir():
        raise ValueError("subject checkout/version is invalid")
    try:
        commit = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError("subject checkout Git identity is unreadable") from exc
    if commit != expected_commits[version] or status:
        raise ValueError("subject checkout is not the clean pinned commit")
    hashes = {}
    for relative, expected in EXPECTED_CHECKOUT_SHA256[version].items():
        path = root / relative
        if not path.is_file():
            raise ValueError(f"subject checkout file is missing: {relative}")
        observed = _sha256(path)
        if observed != expected:
            raise ValueError(f"subject checkout file hash mismatch: {relative}")
        hashes[relative] = observed
    return {"version": version, "commit": commit, "source_sha256": hashes}


def _group_count(values):
    rows = np.asarray(values, dtype=object)
    if rows.ndim == 1:
        keys = [str(value) for value in rows]
    elif rows.ndim == 2 and rows.shape[1] > 0:
        keys = [tuple(str(value) for value in row) for row in rows]
    else:
        raise ValueError("protected groups must be a nonempty vector or matrix")
    return len(set(keys))


def _validate_aligned(name, expected_length, *values):
    for value in values:
        try:
            observed = len(value)
        except TypeError as exc:
            raise ValueError(f"{name} inputs must be sized") from exc
        if observed != expected_length:
            raise ValueError(f"{name} inputs must have matching lengths")


def run_dataset_transcript(
    *,
    threshold_optimizer_cls,
    dataset_id,
    version,
    commit,
    training_positions,
    training_scores,
    training_labels,
    evaluation_positions,
    evaluation_scores,
    native_training_groups,
    native_evaluation_groups,
    canonical_training_groups,
    canonical_evaluation_groups,
    prepared_manifest_sha256,
    companion_manifest_sha256,
    plan_sha256,
    seeds=SEEDS,
):
    """Execute one immutable public-context transcript after external approval.

    This function deliberately accepts the subject class by injection so the
    caller must first mount and verify the pinned Fairlearn checkout. It does
    not read data or approval records and therefore cannot widen campaign
    scope on its own.
    """

    expected_commits = {"old": OLD_COMMIT, "new": NEW_COMMIT}
    if version not in expected_commits or commit != expected_commits[version]:
        raise ValueError("version and source commit do not match the pinned pair")
    for name, digest in (
        ("prepared manifest", prepared_manifest_sha256),
        ("companion manifest", companion_manifest_sha256),
        ("preflight plan", plan_sha256),
    ):
        if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
            raise ValueError(f"{name} SHA-256 is invalid")

    train_positions = np.asarray(training_positions)
    eval_positions = np.asarray(evaluation_positions)
    if train_positions.ndim != 1 or eval_positions.ndim != 1:
        raise ValueError("source row positions must be vectors")
    if len(train_positions) == 0 or len(eval_positions) == 0:
        raise ValueError("training and evaluation inputs must be nonempty")
    _validate_aligned(
        "training",
        len(train_positions),
        training_scores,
        training_labels,
        native_training_groups,
        canonical_training_groups,
    )
    _validate_aligned(
        "evaluation",
        len(eval_positions),
        evaluation_scores,
        native_evaluation_groups,
        canonical_evaluation_groups,
    )
    train_ids = {int(value) for value in train_positions}
    eval_ids = {int(value) for value in eval_positions}
    if len(train_ids) != len(train_positions) or len(eval_ids) != len(eval_positions):
        raise ValueError("source row positions must be unique within each split")
    if train_ids & eval_ids:
        raise ValueError("training and evaluation source rows must be disjoint")

    native_count = _group_count(native_training_groups)
    canonical_count = _group_count(canonical_training_groups)
    if native_count != canonical_count:
        raise ValueError("native and canonical training group cardinalities differ")
    if (
        not seeds
        or any(isinstance(seed, bool) or not isinstance(seed, int) for seed in seeds)
        or len(set(seeds)) != len(seeds)
    ):
        raise ValueError("seeds must be distinct integers")

    all_positions = np.concatenate((train_positions, eval_positions))
    all_scores = np.concatenate(
        (np.asarray(training_scores, dtype=float), np.asarray(evaluation_scores, dtype=float))
    )
    estimator = ScoreLookupEstimator(all_positions, all_scores)
    x_train = train_positions.reshape(-1, 1)
    x_eval = eval_positions.reshape(-1, 1)
    y_train = np.asarray(training_labels)
    modes = {
        "multi": (native_training_groups, native_evaluation_groups),
        "canonical": (canonical_training_groups, canonical_evaluation_groups),
    }
    mode_records = {}
    common_tapes = {
        str(seed): np.random.RandomState(seed).rand(len(eval_positions)) for seed in seeds
    }
    for mode, (train_groups, eval_groups) in modes.items():
        subject = threshold_optimizer_cls(
            estimator=estimator,
            constraints="demographic_parity",
            objective="accuracy_score",
            prefit=True,
        ).fit(x_train, y_train, sensitive_features=train_groups)
        pmf = np.asarray(
            subject._pmf_predict(x_eval, sensitive_features=eval_groups), dtype=float
        )
        if pmf.shape != (len(eval_positions), 2) or not np.all(np.isfinite(pmf)):
            raise ValueError(f"{mode} subject returned an invalid PMF")
        if np.any(pmf < 0.0) or np.any(pmf > 1.0) or not np.array_equal(
            pmf.sum(axis=1), np.ones(len(eval_positions))
        ):
            raise ValueError(f"{mode} subject returned invalid PMF probabilities")
        seed_records = {}
        for seed in seeds:
            first = np.asarray(
                subject.predict(x_eval, sensitive_features=eval_groups, random_state=seed)
            ).astype(int)
            second = np.asarray(
                subject.predict(x_eval, sensitive_features=eval_groups, random_state=seed)
            ).astype(int)
            uniforms = common_tapes[str(seed)]
            expected = (pmf[:, 1] >= uniforms).astype(int)
            seed_records[str(seed)] = {
                "uniforms": uniforms.tolist(),
                "predictions": first.tolist(),
                "repeat_identical": bool(np.array_equal(first, second)),
                "threshold_correspondence": bool(np.array_equal(first, expected)),
            }
        mode_records[mode] = {"pmf": pmf.tolist(), "seeds": seed_records}

    return {
        "schema": TRANSCRIPT_SCHEMA,
        "dataset_id": str(dataset_id),
        "version": version,
        "commit": commit,
        "prepared_manifest_sha256": prepared_manifest_sha256,
        "companion_manifest_sha256": companion_manifest_sha256,
        "plan_sha256": plan_sha256,
        "source_row_positions": [int(value) for value in eval_positions],
        "native_group_count": native_count,
        "canonical_group_count": canonical_count,
        "modes": mode_records,
    }


def validate_campaign_approval(protocol_path, approval_path):
    """Validate fresh external authority without modifying the preregistration."""

    protocol = Path(protocol_path)
    approval_file = Path(approval_path)
    if not protocol.is_file():
        raise ValueError("protocol file is missing")
    if not approval_file.is_file():
        raise ValueError("fresh campaign approval file is missing")
    try:
        approval = json.loads(approval_file.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, ValueError) as exc:
        raise ValueError("campaign approval is unreadable or invalid") from exc
    if not isinstance(approval, dict) or approval.get("schema") != APPROVAL_SCHEMA:
        raise ValueError("campaign approval schema mismatch")
    if approval.get("authorized") is not True:
        raise ValueError("campaign approval must explicitly authorize execution")
    if approval.get("scope") != APPROVAL_SCOPE:
        raise ValueError("campaign approval scope mismatch")
    digest = approval.get("protocol_sha256")
    if not isinstance(digest, str) or not _SHA256_RE.fullmatch(digest):
        raise ValueError("campaign approval protocol SHA-256 is invalid")
    if digest != _sha256(protocol):
        raise ValueError("campaign approval protocol SHA-256 mismatch")
    if approval.get("old_commit") != OLD_COMMIT or approval.get("new_commit") != NEW_COMMIT:
        raise ValueError("campaign approval source pair mismatch")
    if approval.get("seeds") != SEEDS:
        raise ValueError("campaign approval seed list mismatch")
    if approval.get("authorized_by") != "user":
        raise ValueError("campaign approval must be explicitly user-authorized")
    timestamp = approval.get("authorized_at")
    if not isinstance(timestamp, str) or not timestamp.strip():
        raise ValueError("campaign approval timestamp is missing")
    return {
        "schema": APPROVAL_SCHEMA,
        "authorized": True,
        "scope": APPROVAL_SCOPE,
        "protocol_sha256": digest,
        "approval_sha256": _sha256(approval_file),
    }
