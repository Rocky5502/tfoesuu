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
