"""Python 3.8-compatible core for the approval-gated Fairlearn runner."""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import numpy as np

APPROVAL_SCHEMA = "tfoesuu-public-v2-approval-v1"
APPROVAL_SCOPE = "bounded-seven-dataset-fairlearn-v2"
OLD_COMMIT = "e8cc63784de5410805c156715175fc60e2cd5653"
NEW_COMMIT = "0cf59eccfdd364417787fe2c368a1c77c3f378b8"
SEEDS = [1, 104729, 130363, 155921]
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
TRANSCRIPT_SCHEMA = "tfoesuu-fairlearn-public-v2-transcript-v1"


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
