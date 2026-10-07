from pathlib import Path
import subprocess
import sys

from tfoesuu.public_results import PublicResultRow, write_public_results


def test_public_result_renderer_smoke(tmp_path: Path):
    rows = []
    methods = ["independent", "vertex-paired", "four-way", "suite", "tfoesuu"]
    for di, (dataset_id, dataset_name, edges) in enumerate([
        ("public-adult", "Adult Census Income", 100),
        ("public-german", "German Credit", 60),
    ]):
        for pj, d in enumerate([0.05, 0.02]):
            for mi, method in enumerate(methods):
                base = 10000.0 / d
                multiplier = {
                    "independent": 8.0,
                    "vertex-paired": 6.0,
                    "four-way": 2.0,
                    "suite": 2.0,
                    "tfoesuu": 1.0,
                }[method]
                rows.append(
                    PublicResultRow(
                        dataset_id=dataset_id,
                        dataset_name=dataset_name,
                        method=method,
                        patch_size=d,
                        common_shift=0.05,
                        confidence_target=0.05,
                        trials=1000,
                        graph_vertices=2 * edges,
                        graph_edges=edges,
                        impacted_edges=max(1, edges // 10),
                        replay_rounds=base * multiplier / 4.0,
                        concrete_program_executions=base * multiplier,
                        type_i_error=0.005 * mi,
                        type_ii_error=0.01 + 0.002 * pj,
                        seed=1000 + 100 * di + 10 * pj + mi,
                        dataset_sha256=("a" if di == 0 else "b") * 64,
                        source_commit="0123456789abcdef",
                    )
                )

    results = tmp_path / "public_results.jsonl"
    pdf = tmp_path / "public_results.pdf"
    png = tmp_path / "public_results.png"
    write_public_results(rows, results)

    subprocess.run(
        [
            sys.executable,
            "scripts/render_public_results.py",
            "--results",
            str(results),
            "--output",
            str(pdf),
            "--png-output",
            str(png),
        ],
        check=True,
    )
    assert pdf.is_file() and pdf.stat().st_size > 0
    assert png.is_file() and png.stat().st_size > 0