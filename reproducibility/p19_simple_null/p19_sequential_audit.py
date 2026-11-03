#!/usr/bin/env python3
"""Independent, preregistered P19 CPU falsification audit (Oct 14, 2026).

All observations are explicit four-call executions of synthetic common-uniform
threshold programs. The two legal groups differ ONLY in control access:
 boundary={candidate, low}, matched={candidate, high control}.
Same simple null, same singleton alternative, same delta and physical cost (4)
per tape. This is NOT a real-software performance benchmark, nor independent
novelty evidence. The code avoids imported tfoesuu project implementation.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
import numpy as np

SEED = 20261014
PATCH_SIZES = (0.025, 0.035, 0.050, 0.070, 0.100, 0.140)
P, S, TAU, DELTA = 0.30, 0.11, 0.16, 0.05
TRIALS = 2400
MAX_ROUNDS = 80000


def quartet(u, d, alternative, mode):
    """Return four raw binary outputs from 4 program executions per tape.

    Coordinates are [old(candidate), new(candidate), old(reference), new(reference)].
    A low reference has threshold p+s; a high reference threshold p+s+tau.
    """
    cu_old = u <= P
    cu_new = u <= P + S + TAU + (d if alternative else 0.0)
    ref_old = u <= P
    ref_new = u <= P + S + (TAU if mode == 'matched' else 0.0)
    return (cu_old, cu_new, ref_old, ref_new)


def one_round_increments(u, d, alternative):
    """Boundary raw quartet's log-likelihood increment log(P_alt/P_null)."""
    a,b,c,e = quartet(u,d,alternative,'boundary')
    diff = (b.astype(int)-a.astype(int))-(e.astype(int)-c.astype(int))
    A = diff == 1
    B = ~(a | b | c | e)
    assert not np.any(A & B)
    r = 1 - P - S - TAU
    return np.where(A, math.log((TAU+d)/TAU), np.where(B, math.log((r-d)/r), 0.0))


def matched_group(rng, d, alternative, trials):
    """Zero-type-I truncated first-witness test, recording EVERY four-call round."""
    L = math.ceil(math.log(DELTA) / math.log1p(-d))
    active = np.ones(trials, bool)
    rounds = np.zeros(trials, np.int32)
    rejected = np.zeros(trials, bool)
    for _ in range(L):
        ids = np.flatnonzero(active)
        if ids.size == 0:
            break
        u = rng.random(ids.size)
        a,b,c,e = quartet(u,d,alternative,'matched')
        witness = (b.astype(int)-a.astype(int))-(e.astype(int)-c.astype(int)) != 0
        rounds[ids] += 1
        rejected[ids[witness]] = True
        active[ids[witness]] = False
    assert np.all(rounds >= 1)
    return rounds, rejected, L


def boundary_group(rng, d, alternative, trials):
    """Exact finite-law, simple-vs-simple sequential likelihood ratio test.

    Ville boundaries enforce each pointwise error <= DELTA with no fixed horizon.
    A high safety cap is a reproducibility fail, never silently classified.
    """
    active = np.ones(trials, bool)
    rounds = np.zeros(trials, np.int32)
    llr = np.zeros(trials, np.float64)
    rejected = np.zeros(trials, bool)
    upper = -math.log(DELTA)
    lower = math.log(DELTA)
    for step in range(MAX_ROUNDS):
        ids = np.flatnonzero(active)
        if ids.size == 0:
            return rounds, rejected, 0
        u = rng.random(ids.size)
        llr[ids] += one_round_increments(u,d,alternative)
        rounds[ids] += 1
        high = llr[ids] >= upper
        low = llr[ids] <= lower
        assert not np.any(high & low)
        rejected[ids[high]] = True
        active[ids[high | low]] = False
    return rounds, rejected, int(active.sum())


def summarize(rounds, rejected, alternative, mode, d, n, L):
    empirical_error = float((~rejected).mean() if alternative else rejected.mean())
    err_count = int((~rejected).sum() if alternative else rejected.sum())
    cost = 4.0 * rounds
    mean = float(cost.mean())
    se = float(cost.std(ddof=1) / math.sqrt(n))
    out = dict(mode=mode, truth=('alternative' if alternative else 'null'), d=d,
               n_trials=n, error_count=err_count, observed_error_rate=empirical_error,
               mean_concrete_executions=mean, sem_concrete_executions=se,
               ci95_mean_low=max(0.,mean-1.96*se), ci95_mean_high=mean+1.96*se,
               mean_replay_rounds=float(rounds.mean()), max_rounds=int(rounds.max()),
               fixed_round_cap=L if mode == 'matched' else None)
    if mode == 'matched':
        out['exact_null_cost'] = 4*L if not alternative else None
        out['exact_alt_cost'] = 4*(1-math.pow(1-d,L))/d if alternative else None
        out['exact_alt_miss_probability'] = math.pow(1-d,L) if alternative else None
    return out


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', type=Path, default=Path('audit_output'))
    args = parser.parse_args()
    args.out.mkdir(parents=True,exist_ok=True)
    code_hash = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    rows=[]
    for j,d in enumerate(PATCH_SIZES):
        for mode in ('matched','boundary'):
            for alternative in (False,True):
                # Distinct deterministic streams; never paired by chance or re-used.
                rng = np.random.default_rng(np.random.SeedSequence([SEED,j,int(alternative),0 if mode=='matched' else 1]))
                if mode=='matched':
                    rounds, rejected, L = matched_group(rng,d,alternative,TRIALS)
                    cap_hit = 0
                else:
                    rounds, rejected, cap_hit = boundary_group(rng,d,alternative,TRIALS)
                    L = None
                if cap_hit: raise RuntimeError(f'{cap_hit} unresolved trials at cap, d={d}, mode={mode}')
                rows.append(summarize(rounds,rejected,alternative,mode,d,TRIALS,L))
    path=args.out/'p19_sequential_observations.csv'
    with path.open('w',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
        writer.writeheader();writer.writerows(rows)
    from scipy.stats import binomtest
    # Validation gate: error bound is probabilistic; a 95% binomial CI may straddle delta.
    for row in rows:
        row['error_exact_p_at_delta'] = float(binomtest(row['error_count'],TRIALS,DELTA,alternative='greater').pvalue)
    manifest = dict(title='P19 matched-vs-boundary common-uniform sequential audit',
        seed=SEED, trials_per_condition=TRIALS, p=P, s=S, tau=TAU, delta=DELTA,
        patch_sizes=PATCH_SIZES, modes=['matched','boundary'],truths=['null','alternative'],
        cost_unit='each group round=4 synthetic program evaluations, not elapsed runtime',
        null='old all=p; new high=p+s+tau; new low=p+s',
        alternative='as null, candidate high new probability increases by d',
        boundary='SPRT raw four-way log LR, upper=log(1/delta), lower=log(delta)',
        matched='reject first differing raw patch delta, truncated L=ceil(log(delta)/log(1-d))',
        source_sha256=code_hash, csv_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
        rows=rows, limitation='Original independent CPU synthetic experiment; NOT the frozen P12/P15 data or real software. Empirical slopes are finite-range diagnostics, not theoretical proof.')
    (args.out/'p19_audit_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
    from scipy.stats import linregress
    print('SOURCE SHA256',code_hash)
    print('d    boundary null mean calls   matched null mean calls   ratio')
    for d in PATCH_SIZES:
        b=next(x for x in rows if x['d']==d and x['mode']=='boundary' and x['truth']=='null')
        m=next(x for x in rows if x['d']==d and x['mode']=='matched' and x['truth']=='null')
        print(f'{d:5.3f} {b["mean_concrete_executions"]:23.1f} {m["mean_concrete_executions"]:24.1f} {b["mean_concrete_executions"]/m["mean_concrete_executions"]:6.2f}')
    for mode in ('matched','boundary'):
        x=np.log(np.array(PATCH_SIZES))
        y=np.log([next(row for row in rows if row['mode']==mode and row['truth']=='null' and row['d']==d)['mean_concrete_executions'] for d in PATCH_SIZES])
        reg=linregress(x,y)
        print('FINITE-GRID LOG-LOG SLOPE',mode,f'{reg.slope:.4f}',f'R2={reg.rvalue**2:.4f}')
    print('MAX OBSERVED ERROR RATE', max(row['observed_error_rate'] for row in rows))
    print('CSV SHA256',manifest['csv_sha256'])
    return rows

if __name__=='__main__': main()
