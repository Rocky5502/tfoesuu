.PHONY: install test benchmark smoke paper-check

install:
	python -m pip install -r requirements.txt
	python -m pip install -e .

test:
	pytest -q

benchmark:
	python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl

smoke:
	python experiments/run_gaussian_core.py --graph star --n 10 --trials 2000 --gamma 0.6 --beta 0.05

paper-check:
	python scripts/check_bibliography.py
