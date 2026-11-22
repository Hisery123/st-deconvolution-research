#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EnDecon aggregation-only Python port (Tu et al., Bioinformatics 2023).

Original R algorithm: Zhangxf-ccnu/EnDecon/R/EnDeconv.R, solve_ensemble.
This port aggregates existing deconvolution outputs; it does not rerun the
full R EnDecon package or its original 14 component algorithms.
No truth data is used for ensemble fitting. The method uses all observed
spot prediction matrices jointly (transductive unsupervised fusion).
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
from time import perf_counter
import numpy as np
import pandas as pd
import global_stacking_cv as ctw

BASE = Path(r'D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz_2000spots')
CTW = Path(r'D:\Research\STdeconv_benchmark\results\CTWRF_matched_fusion_20261122_v1')
OUT = Path(r'D:\Research\STdeconv_benchmark\results\CTWRF_EnDecon_aggregation_20261122_v1')
POOLS = {
    'strong2': ('CARD', 'cell2location'),
    'expanded4': ('CARD', 'cell2location', 'RCTD', 'SPOTlight'),
    'full6': tuple(ctw.METHOD_FILES),
}
METRICS = ('JSD', 'matrix_RMSE', 'aggregated_celltype_RMSE', 'mean_celltype_RMSE')


def weighted_median(x, w):
    """Weighted median per spot and cell type (method axis=0).

    Exact 50/50 ties choose lower median; source R tie semantics may differ.
    """
    order = np.argsort(x, axis=0, kind='stable')
    sorted_x = np.take_along_axis(x, order, axis=0)
    cum = np.cumsum(w[order], axis=0)
    loc = np.argmax(cum >= 0.5, axis=0)
    return np.take_along_axis(sorted_x, loc[None], axis=0)[0]


def endecon_port(p, max_iter=100, epsilon=1e-5):
    """R solve_ensemble defaults: mean init, median L1 lambda, softmax weights,
    weighted median update, absolute objective convergence at 1e-5.
    """
    m = p.shape[0]
    h = np.mean(p, axis=0)
    d0 = np.abs(p - h).sum(axis=(1, 2))
    lam = float(np.median(d0))
    w = np.full(m, 1.0 / m)
    if lam <= 0:
        if not np.allclose(p, p[0]):
            raise ValueError('Invalid zero lambda for nonidentical predictions')
        return ctw.normalize(h, 'EnDecon zero-lambda'), w, lam, 0, True
    prev, converged = 0.0, False
    for step in range(1, max_iter + 1):
        d = np.abs(p - h).sum(axis=(1, 2))
        z = -d / lam
        z -= max(z)
        e = np.exp(z)
        w = e / e.sum()
        h = weighted_median(p, w)
        updated_d = np.abs(p - h).sum(axis=(1, 2))
        positive = w > 0
        objective = float(updated_d @ w + lam * (w[positive] * np.log(w[positive])).sum())
        if abs(objective - prev) < epsilon:
            converged = True
            break
        prev = objective
    return ctw.normalize(h, 'EnDecon weighted median'), w, lam, step, converged


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument('--dry-run', action='store_true')
    mode.add_argument('--run', action='store_true')
    ap.add_argument('--base-dir', type=Path, default=BASE)
    ap.add_argument('--ctw-results', type=Path, default=CTW)
    ap.add_argument('--out-dir', type=Path, default=OUT)
    args = ap.parse_args()

    test = np.array([[[.8, .2]], [[.3, .7]], [[.6, .4]]])
    arr, w, lam, steps, converged = endecon_port(test)
    assert arr.shape == (1, 2) and np.isclose(arr.sum(), 1) and np.isclose(sum(w), 1)
    print('ALGORITHM SELFTEST PASS', flush=True)
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        raise FileExistsError('Refusing to overwrite nonempty output: ' + str(args.out_dir))
    names = list(ctw.METHOD_FILES)
    gt, preds, sources = ctw.load_inputs(args.base_dir / 'pseudo_spot_ground_truth.csv',
                                         args.base_dir / 'predictions', names)
    refpath = args.ctw_results / 'summary_metrics_by_seed_pool.csv'
    ref = pd.read_csv(refpath)
    required = {'seed', 'pool', 'method', *METRICS}
    if not required.issubset(ref.columns):
        raise ValueError('Missing CTW matched comparison columns')
    for pool in POOLS:
        for method in ('CTW_SoftOpt', 'GlobalStacking'):
            r = ref[(ref.pool == pool) & (ref.method == method)]
            if sorted(r.seed.tolist()) != [2026, 2027, 2028]:
                raise ValueError('Missing reference comparison: ' + pool + '/' + method)
    if gt.shape != (2000, 19):
        raise ValueError('Unexpected existing CTW dataset dimensions')
    print('INPUT CHECK PASS', len(gt), 'spots', gt.shape[1], 'cell types', len(names), 'methods')
    print('CTW REFERENCE PASS 3 seeds x 3 method pools')
    print('DESIGN 3 pools x 3 unsupervised ensemble controls = 9 rows')
    if args.dry_run:
        print('DRY RUN PASS — no files written')
        return

    lookup = {name: i for i, name in enumerate(names)}
    metric_rows, weight_rows, run_rows, compare_rows = [], [], [], []
    result_matrices = {}
    for pool, members in POOLS.items():
        p = preds[[lookup[x] for x in members]]
        start = perf_counter()
        ens, weights, lam, steps, converged = endecon_port(p)
        elapsed = perf_counter() - start
        variants = {'EnDecon_weighted_median': ens,
                    'coordinate_median': ctw.normalize(np.median(p, axis=0), 'median'),
                    'equal_mean': ctw.normalize(np.mean(p, axis=0), 'equal')}
        for name, output in variants.items():
            metric_rows.append({'pool': pool, 'method': name, **ctw.metric_dict(gt.to_numpy(), output)})
            result_matrices[(pool, name)] = output
        weight_rows.extend({'pool': pool, 'base_method': name, 'weight': float(v)}
                           for name, v in zip(members, weights))
        run_rows.append({'pool': pool, 'lambda': lam, 'iterations': steps,
                         'converged': converged, 'aggregate_runtime_seconds': elapsed})
        ens_met = metric_rows[-3]
        for _, row in ref[ref.pool == pool].iterrows():
            if row['method'] not in ('CTW_SoftOpt', 'GlobalStacking'):
                continue
            compare_rows.append({'pool': pool, 'seed': int(row.seed),
                                 'ctw_method': row.method, 'comparator': 'EnDecon_weighted_median',
                                 **{'delta_endecon_minus_' + key: float(ens_met[key] - row[key])
                                    for key in METRICS}})
        print('COMPLETED', pool, 'EnDecon JSD', round(ens_met['JSD'], 6),
              'RMSE', round(ens_met['matrix_RMSE'], 6),
              'iterations', steps, 'converged', converged, flush=True)
    if len(metric_rows) != 9 or len(compare_rows) != 18:
        raise ValueError('Unexpected output size')
    args.out_dir.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(metric_rows).to_csv(args.out_dir / 'ensemble_metrics_by_pool.csv', index=False)
    pd.DataFrame(weight_rows).to_csv(args.out_dir / 'endecon_weights_by_pool.csv', index=False)
    pd.DataFrame(run_rows).to_csv(args.out_dir / 'endecon_diagnostics_by_pool.csv', index=False)
    pd.DataFrame(compare_rows).to_csv(args.out_dir / 'ctw_matched_seed_comparisons.csv', index=False)
    (args.out_dir / 'predictions').mkdir(exist_ok=True)
    for (pool, name), matrix in result_matrices.items():
        pd.DataFrame(matrix, index=gt.index, columns=gt.columns).to_csv(
            args.out_dir / 'predictions' / (pool + '__' + name + '.csv'))
    config = {
        'status': 'exploratory',
        'paper': 'Tu et al., Bioinformatics 39(1) btac825; doi:10.1093/bioinformatics/btac825',
        'source_code': 'https://github.com/Zhangxf-ccnu/EnDecon/blob/master/R/EnDeconv.R',
        'implementation': 'Python aggregation-only port of R solve_ensemble, not official R package',
        'source_predictions': sources, 'method_pools': POOLS, 'lambda_rule': 'median initial L1 distances',
        'max_iter': 100, 'epsilon': 1e-5,
        'weighted_median_exact_half_ties': 'lower; may differ from R spatstat.geom',
        'notes': ['No target ground truth used to train EnDecon ensemble weights',
                  'Unsupervised transductive global weights use all spot predictions',
                  'CTW results use matched held-out five-fold out-of-fold predictions',
                  'No original R package execution or all 14 original component methods',
                  'Repetition of same unsupervised result across CTW random seeds is not independent replication']}
    (args.out_dir / 'run_config.json').write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding='utf-8')
    print('BATCH FINISHED 3 method pools x 3 ensemble variants; 18 CTW reference comparisons')
    print('OUTPUT', args.out_dir)


if __name__ == '__main__':
    main()
