from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np
import pandas as pd
import scipy
import sklearn
from sklearn.linear_model import LinearRegression

EXPECTED_COMMITS = {
    "old": "e8cc63784de5410805c156715175fc60e2cd5653",
    "new": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
}
EXPECTED_CHECKOUT_SHA256 = {
    "old": {
        "LICENSE": "f95d3cc5bcd913e7f5cb67ad17f8e0c8796e9b1adf96b5395a81c3d5f976d79a",
        "requirements.txt": "3c850a414d8c27a7e51fd9f2eecfe55a743c4dabb3600bccdb2e82b046dac611",
        "fairlearn/_input_validation.py": "0210b9b1e99caef84821554e543d574cc2b17c5b82339730b3d6533a6d93b273",
        "fairlearn/postprocessing/_threshold_optimizer.py": "a59d2ec8a1ec52cec184030576744f57d7f55eac1232a5de2527853445a4bbbe",
        "fairlearn/postprocessing/_interpolated_thresholder.py": "e262c6d2970b3ba1151e02971e2431ed413802edfaea6117df88abdb28d66b5a",
    },
    "new": {
        "LICENSE": "f95d3cc5bcd913e7f5cb67ad17f8e0c8796e9b1adf96b5395a81c3d5f976d79a",
        "requirements.txt": "3c850a414d8c27a7e51fd9f2eecfe55a743c4dabb3600bccdb2e82b046dac611",
        "fairlearn/_input_validation.py": "6ddfac320e0351d60fa1d97096f698af946f35be55a221f84ebe5cc012059284",
        "fairlearn/postprocessing/_threshold_optimizer.py": "a59d2ec8a1ec52cec184030576744f57d7f55eac1232a5de2527853445a4bbbe",
        "fairlearn/postprocessing/_interpolated_thresholder.py": "e262c6d2970b3ba1151e02971e2431ed413802edfaea6117df88abdb28d66b5a",
    },
}
SEEDS = (1, 104729, 130363, 155921)


def _sha256_json(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(payload).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _fixture() -> tuple[pd.DataFrame, pd.Series, pd.DataFrame, pd.DataFrame]:
    x_train = pd.DataFrame(
        [
            [0, 4],
            [6, 2],
            [1, 3],
            [10, 5],
            [1, 7],
            [-2, 1],
            [3, 10],
            [14, 5],
            [1, 3],
            [1, 5],
            [1, 7],
            [-5, 9],
            [3, 13],
            [7, 1],
            [-8, 4],
            [9, 1],
        ]
    )
    y_train = pd.Series([0, 1, 1, 0, 0, 0, 1, 0, 0, 1, 0, 0, 1, 1, 1, 0])
    a1 = "a"
    a2 = "a very very very very very very very long group name"
    a3 = "a group name with commas ,, in , it"
    a4 = "a group name with backslashes \\ in \\\\ it"
    protected_train = pd.DataFrame(
        [
            [a1, a3, a1 + a3],
            [a1, a3, a1 + a3],
            [a2, a3, a2 + a3],
            [a2, a3, a2 + a3],
            [a2, a3, a2 + a3],
            [a2, a3, a2 + a3],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a1, a4, a1 + a4],
            [a1, a4, a1 + a4],
        ],
        columns=["SF1", "SF2", "SF1+2"],
    )
    x_prefix = pd.DataFrame(
        [[5, 4], [7, 2], [0, 3], [1, 2], [-2, 9], [1, 1], [0, 5], [-3, 3]]
    )
    protected_prefix = pd.DataFrame(
        [
            [a1, a3, a1 + a3],
            [a1, a3, a1 + a3],
            [a2, a3, a2 + a3],
            [a2, a3, a2 + a3],
            [a2, a4, a2 + a4],
            [a2, a4, a2 + a4],
            [a1, a4, a1 + a4],
            [a1, a4, a1 + a4],
        ],
        columns=["SF1", "SF2", "SF1+2"],
    )
    return (
        x_train,
        y_train,
        pd.concat([x_prefix, x_train], ignore_index=True),
        pd.concat([protected_prefix, protected_train], ignore_index=True),
    )


def run(version: str, checkout: Path) -> dict[str, object]:
    checkout = checkout.resolve()
    source_hashes = {
        path: _sha256_file(checkout / path)
        for path in EXPECTED_CHECKOUT_SHA256[version]
    }
    if source_hashes != EXPECTED_CHECKOUT_SHA256[version]:
        raise RuntimeError("mounted external source hash gate failed")
    sys.path.insert(0, str(checkout))
    from fairlearn.postprocessing import ThresholdOptimizer

    x_train, y_train, x_test, protected = _fixture()
    estimator = LinearRegression().fit(x_train, y_train)
    train_groups = protected.iloc[-len(x_train) :]
    modes = {
        "multi": (train_groups[["SF1", "SF2"]], protected[["SF1", "SF2"]]),
        "combined": (train_groups["SF1+2"], protected["SF1+2"]),
    }
    records: dict[str, object] = {}
    started = time.perf_counter()
    for mode, (protected_train, protected_test) in modes.items():
        subject = ThresholdOptimizer(
            estimator=estimator,
            constraints="demographic_parity",
            objective="accuracy_score",
            prefit=True,
        ).fit(x_train, y_train, sensitive_features=protected_train)
        pmf = subject._pmf_predict(x_test, sensitive_features=protected_test)
        seed_records: dict[str, object] = {}
        for seed in SEEDS:
            uniforms = np.random.RandomState(seed).rand(len(x_test))
            first = subject.predict(
                x_test, sensitive_features=protected_test, random_state=seed
            )
            second = subject.predict(
                x_test, sensitive_features=protected_test, random_state=seed
            )
            expected = (pmf[:, 1] >= uniforms).astype(int)
            seed_records[str(seed)] = {
                "uniforms": uniforms.tolist(),
                "uniform_sha256": _sha256_json(uniforms.tolist()),
                "predictions": first.astype(int).tolist(),
                "prediction_sha256": _sha256_json(first.astype(int).tolist()),
                "repeat_identical": bool(np.array_equal(first, second)),
                "threshold_correspondence": bool(np.array_equal(first, expected)),
            }
        interpolation = {
            str(key): str(value)
            for key, value in subject.interpolated_thresholder_.interpolation_dict.items()
        }
        records[mode] = {
            "pmf": pmf.tolist(),
            "pmf_sha256": _sha256_json(pmf.tolist()),
            "interpolation": interpolation,
            "interpolation_sha256": _sha256_json(interpolation),
            "group_count": len(interpolation),
            "seeds": seed_records,
        }
    elapsed = time.perf_counter() - started
    multi = records["multi"]
    combined = records["combined"]
    assert isinstance(multi, dict) and isinstance(combined, dict)
    return {
        "schema_version": 1,
        "version": version,
        "commit": EXPECTED_COMMITS[version],
        "source_sha256": source_hashes,
        "python": sys.version,
        "platform": platform.platform(),
        "packages": {
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "scipy": scipy.__version__,
            "scikit_learn": sklearn.__version__,
        },
        "seeds": list(SEEDS),
        "rows": len(x_test),
        "records": records,
        "multi_equals_combined_by_seed": {
            str(seed): multi["seeds"][str(seed)]["predictions"]
            == combined["seeds"][str(seed)]["predictions"]
            for seed in SEEDS
        },
        "elapsed_seconds": elapsed,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", choices=("old", "new"), required=True)
    parser.add_argument("--checkout", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.version, args.checkout), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
