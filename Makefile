.PHONY: install test inventory smoke replay-smoke reviewer-check evidence-check

install:
	python -m pip install -e ".[dev]"

test:
	python -m pytest -q

inventory:
	python scripts/validate_benchmark_inventory.py

smoke:
	python experiments/run_gaussian_core.py --graph star --n 8 --trials 500 --gamma 0.7 --beta 0.05

replay-smoke:
	python experiments/run_replay_separation.py --p 0.5 --d 0.05 --beta 0.05 --trials 1000

evidence-check:
	python scripts/validate_preview_results.py reproducibility/p12_p15/evidence/p12_p15_100k_preview_manifest_v1.json --base-dir reproducibility/p12_p15
	python -m pytest -q reproducibility/p19_simple_null/test_p19_audit.py
	cd reproducibility/unknown_shared_nuisance && python -m unittest -q test_exact_witness_audit.py

reviewer-check: test inventory smoke replay-smoke evidence-check
