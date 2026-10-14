.PHONY: install test benchmark replay-benchmark smoke replay-smoke paper-check paper-pdf

install:
	python -m pip install -r requirements.txt
	python -m pip install -e .

test:
	pytest -q

benchmark:
	python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl

replay-benchmark:
	python scripts/generate_replay_benchmark.py --output data/replay_benchmark_v1.jsonl

smoke:
	python experiments/run_gaussian_core.py --graph star --n 10 --trials 2000 --gamma 0.6 --beta 0.05

replay-smoke:
	python experiments/run_replay_separation.py --p 0.5 --d 0.05 --beta 0.05 --trials 5000

paper-check:
	python scripts/check_bibliography.py
	python scripts/check_paper_consistency.py
	python scripts/check_review_submission.py

paper-pdf: paper-check
	cd paper/stoc2027_review && latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
