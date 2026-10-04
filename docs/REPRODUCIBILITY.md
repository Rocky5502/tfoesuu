# Reproducibility protocol

## Immutable inputs

Every experiment is determined by:

- repository commit SHA;
- benchmark JSONL row;
- explicit random seed;
- implementation version;
- CPU/GPU environment report.

## Generated benchmark

```bash
python scripts/generate_benchmark.py --output data/benchmark_v1.jsonl
```

The generator is deterministic. The manifest contains parameter specifications rather than giant sampled arrays.

## CPU theorem sanity check

```bash
python experiments/run_gaussian_core.py --graph star --n 10 --gamma 0.5 --beta 0.05 --trials 100000
python experiments/run_bernoulli_coupling.py --p0 0.5 --delta 0.01 --samples 1000000
```

## GPU stress sweep

```bash
python experiments/gpu_sweep.py --devices 0,1 --trials 1000000 --benchmark data/benchmark_v1.jsonl --output results/gpu_sweep.jsonl
```

## Artifact freeze

When a figure/table becomes submission-facing:

1. create a frozen config/manifest;
2. rerun from a clean environment;
3. save environment report;
4. save command line and seed;
5. compute SHA-256 checksums;
6. never hand-edit result rows.


## Publication-run provenance

After each frozen long run, create a machine-readable provenance record with
scripts/record_publication_run.py. For the P15 publication sweep, pass the frozen
counterfactual benchmark JSONL, the merged result JSONL, the exact command string,
and a provenance JSON output path.

The record captures the source commit, dirty-tree status, benchmark and result
SHA-256 hashes, platform/Python metadata, NVIDIA environment, and PyTorch/CUDA
device information. Publication artifacts should be generated only from runs
whose provenance records show a clean source tree and the intended frozen commit.
