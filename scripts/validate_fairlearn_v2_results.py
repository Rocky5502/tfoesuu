from __future__ import annotations

import argparse
import json
from pathlib import Path

EXPECTED = {
    "old": "e8cc63784de5410805c156715175fc60e2cd5653",
    "new": "0cf59eccfdd364417787fe2c368a1c77c3f378b8",
}
EXPECTED_PACKAGES = {
    "numpy": "1.20.3",
    "pandas": "1.2.4",
    "scipy": "1.6.3",
    "scikit_learn": "0.24.2",
}
EXPECTED_SEEDS = [1, 104729, 130363, 155921]


def _load(path: Path) -> dict[str, object]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise TypeError(f"{path}: expected one JSON object")
    return value


def validate(old_path: Path, new_path: Path) -> dict[str, object]:
    reports = {"old": _load(old_path), "new": _load(new_path)}
    canonical_uniforms: dict[str, list[float]] = {}
    for version, report in reports.items():
        if report.get("version") != version or report.get("commit") != EXPECTED[version]:
            raise ValueError(f"{version}: identity mismatch")
        if report.get("packages") != EXPECTED_PACKAGES:
            raise ValueError(f"{version}: package lock mismatch")
        if report.get("seeds") != EXPECTED_SEEDS or report.get("rows") != 24:
            raise ValueError(f"{version}: frozen protocol mismatch")
        records = report.get("records")
        if not isinstance(records, dict) or set(records) != {"multi", "combined"}:
            raise ValueError(f"{version}: execution modes mismatch")
        for mode, mode_record in records.items():
            if not isinstance(mode_record, dict):
                raise TypeError(f"{version}/{mode}: malformed record")
            seeds = mode_record.get("seeds")
            if not isinstance(seeds, dict) or set(seeds) != {str(x) for x in EXPECTED_SEEDS}:
                raise ValueError(f"{version}/{mode}: seed set mismatch")
            for seed in EXPECTED_SEEDS:
                seed_record = seeds[str(seed)]
                if not isinstance(seed_record, dict):
                    raise TypeError(f"{version}/{mode}/{seed}: malformed record")
                if not seed_record.get("repeat_identical"):
                    raise ValueError(f"{version}/{mode}/{seed}: nonreproducible prediction")
                if not seed_record.get("threshold_correspondence"):
                    raise ValueError(f"{version}/{mode}/{seed}: tape correspondence failed")
                uniforms = seed_record.get("uniforms")
                if not isinstance(uniforms, list) or len(uniforms) != 24:
                    raise ValueError(f"{version}/{mode}/{seed}: malformed tape")
                previous = canonical_uniforms.setdefault(str(seed), uniforms)
                if uniforms != previous:
                    raise ValueError(f"{version}/{mode}/{seed}: common tape mismatch")

    new_control = reports["new"].get("multi_equals_combined_by_seed")
    if not isinstance(new_control, dict) or not all(new_control.values()):
        raise ValueError("new revision fails the frozen canonical-combination control")

    def mode(version: str, name: str) -> dict[str, object]:
        records = reports[version]["records"]
        assert isinstance(records, dict)
        value = records[name]
        assert isinstance(value, dict)
        return value

    disagreement_counts: dict[str, dict[str, int]] = {}
    for name in ("multi", "combined"):
        disagreement_counts[name] = {}
        old_seeds = mode("old", name)["seeds"]
        new_seeds = mode("new", name)["seeds"]
        assert isinstance(old_seeds, dict) and isinstance(new_seeds, dict)
        for seed in EXPECTED_SEEDS:
            old_predictions = old_seeds[str(seed)]["predictions"]
            new_predictions = new_seeds[str(seed)]["predictions"]
            disagreement_counts[name][str(seed)] = sum(
                left != right
                for left, right in zip(old_predictions, new_predictions, strict=True)
            )

    old_control = reports["old"]["multi_equals_combined_by_seed"]
    assert isinstance(old_control, dict)
    group_counts = {
        version: {
            name: mode(version, name)["group_count"]
            for name in ("multi", "combined")
        }
        for version in ("old", "new")
    }
    return {
        "schema_version": 1,
        "runtime_gate_passed": True,
        "shared_tape_gate_passed": True,
        "new_canonical_control_passed": True,
        "old_canonical_control_by_seed": old_control,
        "documented_defect_reproduced": not all(old_control.values()),
        "group_counts": group_counts,
        "old_new_prediction_disagreements": disagreement_counts,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("old", type=Path)
    parser.add_argument("new", type=Path)
    args = parser.parse_args()
    print(json.dumps(validate(args.old, args.new), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
