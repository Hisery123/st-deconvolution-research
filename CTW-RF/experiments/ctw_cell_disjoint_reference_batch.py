#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CTW-RF supplemental cell-disjoint reference benchmark.

A NEW benchmark is built from source SINGLE-CELL counts, not copied from
the historical (reference-overlapping) 2000-pseudospot benchmark.

Within EACH cell type, unique source cell IDs are split into three disjoint
sets: mapping reference / train-mixture donors / test-mixture donors.
Pseudo-spots reuse donors WITHIN a set; train/test donors do not overlap.

For balanced and cell-uniform sampling, make 1200 train and 800 held-out
test pseudo-spots, 8 donor cells per spot, 19-or-data-derived cell types.
Fit three freshly generated baselines using the SAME reference:
  Tangram (existing original implementation via separate Python 3.7)
  NNLS_500 (500 most expressed reference genes)
  NNLS_marker20 (up to 20 reference-derived markers per type)
Compare EqualWeight, GlobalStacking, CTW_HardSelect, CTW_InvRMSE_p2,
CTW_SoftOpt, and every base method on independent DONOR-CELL test pools.

IMPORTANT: This is a supplemental 3-method protocol, NOT a re-run of the
original historical six baselines. No claims of independent donor or
cross-platform validation. No old input or historical prediction is reused.

--dry-run: read/validate input + test Tangram import, absolutely NO writes.
--run: one batch, refuse any existing results directory.
--run --resume: restart after failure with identical run config, reusing
             any COMPLETE inputs and validated prediction files.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd
from scipy.optimize import nnls

import global_stacking_cv as metric
import ctw_matched_fusion_comparisons_batch as ctw

DEFAULT_SOURCE = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\self_benchmark_cortex_svz")
DEFAULT_OUT = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1")
DEFAULT_TANGRAM = Path(r"D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py")
DEFAULT_TANGRAM_PYTHON = Path(r"D:\ProgramData\miniconda3\envs\Tangram\python.exe")
SCENARIOS = ("balanced_celltype", "cell_uniform")
METHODS = ("Tangram", "NNLS_500", "NNLS_marker20")
FUSIONS = ("EqualWeight", "GlobalStacking", "CTW_HardSelect",
           "CTW_InvRMSE_p2", "CTW_SoftOpt")
RESULT_METRICS = ("JSD", "matrix_RMSE", "aggregated_celltype_RMSE",
                  "mean_celltype_RMSE")


def get_args():
    p = argparse.ArgumentParser(description=__doc__)
    action = p.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true")
    action.add_argument("--run", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--tangram-runner", type=Path, default=DEFAULT_TANGRAM)
    p.add_argument("--tangram-python", type=Path, default=DEFAULT_TANGRAM_PYTHON)
    p.add_argument("--device", default="auto")
    p.add_argument("--tangram-epochs", type=int, default=500)
    p.add_argument("--tangram-genes", type=int, default=3000)
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--train-spots", type=int, default=1200)
    p.add_argument("--test-spots", type=int, default=800)
    p.add_argument("--cells-per-spot", type=int, default=8)
    return p.parse_args()


def read_source(root):
    counts = pd.read_csv(root / "sc_reference_counts.csv", index_col=0)
    labels = pd.read_csv(root / "sc_reference_labels.csv", index_col=0)
    counts.index = counts.index.astype(str)
    labels.index = labels.index.astype(str)
    counts.columns = counts.columns.astype(str)
    if counts.index.has_duplicates or labels.index.has_duplicates:
        raise ValueError("Duplicate source cell IDs: cannot safely split")
    if counts.columns.has_duplicates:
        raise ValueError("Duplicate gene names")
    lab_candidates = ("label", "cell_type", "CellType", "celltype", "annotation",
                      "type", "cluster")
    col = next((x for x in lab_candidates if x in labels.columns), None)
    if col is None:
        raise ValueError("Missing known cell-type column in source reference labels")
    common = counts.index.intersection(labels.index)
    if len(common) < 50:
        raise ValueError("Too few source reference cells")
    counts = counts.loc[common].apply(pd.to_numeric, errors="raise").astype(np.float32)
    types = labels.loc[common, col].astype(str)
    if types.isna().any() or not counts.columns.is_unique:
        raise ValueError("Invalid reference")
    arr = counts.to_numpy()
    if not np.isfinite(arr).all() or np.min(arr) < 0:
        raise ValueError("Invalid source reference counts")
    if len(counts.columns) < 50:
        raise ValueError("Fewer than 50 genes")
    if types.nunique() < 3:
        raise ValueError("Fewer than 3 cell types")
    return counts, types


def split_cells(labels, seed):
    rng = np.random.default_rng(seed)
    slots = {"reference": [], "train_donor": [], "test_donor": []}
    per_type = []
    for ct in sorted(labels.unique()):
        ids = rng.permutation(labels[labels.eq(ct)].index.to_numpy())
        n = len(ids)
        if n == 1:
            nref, ntrain = 1, 0
        elif n == 2:
            nref, ntrain = 1, 1
        else:
            nref = max(1, min(n - 2, int(round(n * 0.50))))
            ntrain = max(1, min(n - nref - 1, (n - nref) // 2))
        refs = list(ids[:nref])
        trains = list(ids[nref:nref + ntrain])
        tests = list(ids[nref + ntrain:])
        slots["reference"].extend(refs)
        slots["train_donor"].extend(trains)
        slots["test_donor"].extend(tests)
        per_type.append({"cell_type": ct, "source_n": n,
                         "reference_n": len(refs),
                         "train_donor_n": len(trains),
                         "test_donor_n": len(tests)})
    r, tr, te = (set(slots[key]) for key in
                 ("reference", "train_donor", "test_donor"))
    if r & tr or r & te or tr & te:
        raise AssertionError("Source cell ID overlap across partitions")
    if len(tr) < 20 or len(te) < 20:
        raise ValueError("Too few independent train/test donor cells")
    return slots, pd.DataFrame(per_type)


def make_spots(counts, labels, donors, all_types, n_spots, cells_per_spot,
               seed, sampling, prefix):
    rng = np.random.default_rng(seed)
    donor = counts.loc[donors]
    dlabels = labels.loc[donors]
    arr = donor.to_numpy(dtype=np.float32)
    ids = donor.index.to_numpy()
    type_idx = pd.Index(all_types).get_indexer(dlabels.to_numpy())
    if len(donor) < 4 or np.any(type_idx < 0):
        raise ValueError("Invalid donor pool")
    by_type = {k: np.flatnonzero(dlabels.to_numpy() == k)
               for k in sorted(dlabels.unique())}
    available = list(by_type)
    expr = np.empty((n_spots, counts.shape[1]), dtype=np.float32)
    ctcounts = np.zeros((n_spots, len(all_types)), dtype=np.int16)
    members = []
    names = [f"{prefix}_{i:05d}" for i in range(n_spots)]
    for i, sid in enumerate(names):
        if sampling == "balanced_celltype":
            chosen = [int(rng.choice(by_type[str(ct)]))
                      for ct in rng.choice(available, size=cells_per_spot,
                                           replace=True)]
        elif sampling == "cell_uniform":
            chosen = rng.choice(len(ids), size=cells_per_spot,
                                replace=True).tolist()
        else:
            raise ValueError("Unknown sampling: " + sampling)
        chosen = np.asarray(chosen, dtype=int)
        expr[i, :] = arr[chosen].sum(axis=0)
        ctcounts[i, :] = np.bincount(type_idx[chosen], minlength=len(all_types))
        members.extend({"spot_id": sid, "source_cell_id": str(ids[j]),
                        "cell_type": str(dlabels.iloc[j]),
                        "draw_position": slot}
                       for slot, j in enumerate(chosen.tolist()))
    x = np.arange(n_spots) % 50
    y = np.arange(n_spots) // 50
    locs = pd.DataFrame({"x": x.astype(float), "y": y.astype(float),
                         "n_cells": cells_per_spot}, index=names)
    expr_df = pd.DataFrame(expr, index=names, columns=counts.columns)
    count_df = pd.DataFrame(ctcounts, index=names, columns=all_types)
    truth_df = count_df / float(cells_per_spot)
    return expr_df, locs, truth_df, count_df, pd.DataFrame(members)


def verify_existing(folder, expression, reference, labels):
    required = ("pseudo_spot_expression.csv", "pseudo_spot_locations.csv",
                "sc_reference_counts.csv", "sc_reference_labels.csv")
    missing = [n for n in required if not (folder / n).is_file()]
    if missing:
        raise FileNotFoundError("Incomplete existing input " + str(folder) +
                                " missing " + str(missing))
    obs = pd.read_csv(folder / "pseudo_spot_expression.csv", index_col=0)
    old_ref = pd.read_csv(folder / "sc_reference_counts.csv", index_col=0)
    old_labels = pd.read_csv(folder / "sc_reference_labels.csv", index_col=0)
    if not obs.index.astype(str).equals(expression.index):
        raise ValueError("Resume expression spot ID mismatch: " + str(folder))
    if not obs.columns.astype(str).equals(expression.columns):
        raise ValueError("Resume expression gene mismatch: " + str(folder))
    if not np.array_equal(obs.to_numpy(dtype=np.float32), expression.to_numpy()):
        raise ValueError("Resume expression differs from regenerated inputs")
    if not old_ref.index.astype(str).equals(reference.index):
        raise ValueError("Resume mapping reference IDs changed")
    if not old_labels.index.astype(str).equals(labels.index):
        raise ValueError("Resume mapping labels changed")


def create_inputs(folder, expression, locations, ref, labels):
    if folder.exists():
        verify_existing(folder, expression, ref, labels)
        print("REUSE INPUTS", folder, flush=True)
        return
    folder.mkdir(parents=True)
    expression.to_csv(folder / "pseudo_spot_expression.csv")
    locations.to_csv(folder / "pseudo_spot_locations.csv")
    ref.to_csv(folder / "sc_reference_counts.csv")
    labels.rename("label").to_frame().to_csv(folder / "sc_reference_labels.csv")


def get_tangram_prediction(folder, args, logpath, expected):
    pred_path = folder / "predictions" / "Tangram_self_benchmark.csv"
    if pred_path.is_file():
        pred = pd.read_csv(pred_path, index_col=0)
        pred.index = pred.index.astype(str)
        if set(pred.index) != set(expected.index) or set(pred.columns) != set(expected.columns):
            raise ValueError("Unexpected existing Tangram prediction IDs/classes")
        if not np.isfinite(pred.to_numpy(dtype=float)).all():
            raise ValueError("Nonfinite existing Tangram predictions")
        print("REUSE TANGRAM", folder, flush=True)
        return pred.loc[expected.index, expected.columns].astype(float)
    cmd = [str(args.tangram_python), str(args.tangram_runner),
           "--base_dir", str(folder), "--seed", str(args.seed),
           "--num_epochs", str(args.tangram_epochs),
           "--mode", "cells", "--density_prior", "rna_count_based",
           "--device", args.device, "--max_genes", str(args.tangram_genes)]
    logpath.parent.mkdir(exist_ok=True, parents=True)
    start = time.perf_counter()
    with logpath.open("w", encoding="utf-8") as f:
        f.write("COMMAND " + subprocess.list2cmdline(cmd) + "\n")
        f.flush()
        result = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    if result.returncode != 0 or not pred_path.is_file():
        tail = logpath.read_text(encoding="utf-8", errors="replace").splitlines()[-25:]
        raise RuntimeError("Tangram failed; see " + str(logpath) +
                           "\n" + "\n".join(tail))
    pred = pd.read_csv(pred_path, index_col=0)
    pred.index = pred.index.astype(str)
    if set(pred.index) != set(expected.index) or set(pred.columns) != set(expected.columns):
        raise ValueError("Tangram output spot/type mismatch")
    pred = pred.loc[expected.index, expected.columns].astype(float)
    if not np.isfinite(pred.to_numpy()).all():
        raise ValueError("Nonfinite Tangram predictions")
    print("TANGRAM DONE", folder.name,
          "seconds", round(time.perf_counter() - start, 2), flush=True)
    return pred


def reference_profiles(reference, labels, classes):
    a = reference.to_numpy(dtype=float)
    sums = a.sum(axis=1, keepdims=True)
    sums[sums <= 0] = 1.0
    a = a / sums
    return np.stack([a[labels.to_numpy() == ct].mean(axis=0)
                     for ct in classes], axis=0)


def gene_sets(reference, labels, types):
    profile = reference_profiles(reference, labels, types)
    ranked = reference.to_numpy(dtype=float).sum(axis=0)
    top500 = np.argsort(-ranked, kind="stable")[:min(500, len(ranked))]
    marker = set()
    for ci in range(len(types)):
        others = np.delete(profile, ci, axis=0)
        mean_other = others.mean(axis=0)
        # Reference-only enrichment (never use train/test spot truth).
        score = np.log(profile[ci] + 1e-8) - np.log(mean_other + 1e-8)
        score[profile[ci] <= 0] = -np.inf
        top = np.argsort(-score, kind="stable")[:min(20, len(score))]
        marker.update(int(j) for j in top if np.isfinite(score[j]))
    marker = np.asarray(sorted(marker), dtype=int)
    if len(marker) < 10 or len(top500) < 10:
        raise ValueError("Reference gene selection found too few genes")
    return profile, {"NNLS_500": top500, "NNLS_marker20": marker}


def nnls_predict(expression, profiles, selected):
    A = np.ascontiguousarray(profiles[:, selected].T, dtype=np.float64)
    b = np.asarray(expression.to_numpy(dtype=np.float64)[:, selected])
    total = np.asarray(expression.to_numpy(dtype=np.float64).sum(axis=1))
    if np.any(total <= 0):
        raise ValueError("Zero-expression pseudo-spot")
    b = b / total[:, None]
    out = np.zeros((len(b), profiles.shape[0]), dtype=float)
    for i in range(len(b)):
        w, _ = nnls(A, b[i])
        sm = float(w.sum())
        if sm <= 1e-12:
            raise ValueError("NNLS returned a zero-total proportion")
        out[i, :] = w / sm
    return pd.DataFrame(out, index=expression.index)


def run_scenario(name, counts, labels, split, classes, args):
    folder = args.out_dir / name
    done = folder / "test_metrics.csv"
    if done.is_file():
        print("SKIP COMPLETED", name, flush=True)
        return pd.read_csv(done)
    folder.mkdir(exist_ok=True, parents=True)
    reference = counts.loc[split["reference"]]
    ref_labels = labels.loc[reference.index]
    offset = 0 if name == "balanced_celltype" else 100000
    train_expr, train_locs, train_y, train_n, train_members = make_spots(
        counts, labels, split["train_donor"], classes, args.train_spots,
        args.cells_per_spot, args.seed + offset + 41, name, "TRAIN")
    test_expr, test_locs, test_y, test_n, test_members = make_spots(
        counts, labels, split["test_donor"], classes, args.test_spots,
        args.cells_per_spot, args.seed + offset + 73, name, "TEST")
    training_folder = folder / "train"
    testing_folder = folder / "test"
    create_inputs(training_folder, train_expr, train_locs, reference, ref_labels)
    create_inputs(testing_folder, test_expr, test_locs, reference, ref_labels)
    # Hold-out ground truth is stored outside Tangram input folders.
    truth_folder = folder / "ground_truth_and_membership"
    if not truth_folder.exists():
        truth_folder.mkdir()
        train_y.to_csv(truth_folder / "train_truth.csv")
        test_y.to_csv(truth_folder / "test_truth.csv")
        train_n.to_csv(truth_folder / "train_counts.csv")
        test_n.to_csv(truth_folder / "test_counts.csv")
        train_members.to_csv(truth_folder / "train_membership.csv", index=False)
        test_members.to_csv(truth_folder / "test_membership.csv", index=False)
    pred_train = {"Tangram": get_tangram_prediction(
        training_folder, args, folder / "logs" / "train_tangram.log", train_y)}
    pred_test = {"Tangram": get_tangram_prediction(
        testing_folder, args, folder / "logs" / "test_tangram.log", test_y)}
    profile, genes = gene_sets(reference, ref_labels, classes)
    pred_folder = folder / "derived_baseline_predictions"
    pred_folder.mkdir(exist_ok=True)
    for method, indices in genes.items():
        for splitname, expression, target in (
                ("train", train_expr, pred_train), ("test", test_expr, pred_test)):
            path = pred_folder / (splitname + "_" + method + ".csv")
            if path.is_file():
                p = pd.read_csv(path, index_col=0)
                p.index = p.index.astype(str)
                if set(p.index) != set(expression.index) or set(p.columns) != set(classes):
                    raise ValueError("Existing NNLS prediction mismatch: " + str(path))
                target[method] = p.loc[expression.index, classes]
            else:
                p = nnls_predict(expression, profile, indices)
                p.columns = classes
                p.to_csv(path)
                target[method] = p
    ytr = train_y.to_numpy(dtype=float)
    yte = test_y.to_numpy(dtype=float)
    ptrain = np.stack([metric.normalize(pred_train[m].to_numpy(dtype=float), m)
                       for m in METHODS])
    ptest = np.stack([metric.normalize(pred_test[m].to_numpy(dtype=float), m)
                      for m in METHODS])
    train_indices = np.arange(len(ytr))
    fitted = {
        "GlobalStacking": metric.fit_global_weights(ptrain, ytr),
        "CTW_HardSelect": ctw.hardselect_weights(ptrain, ytr, train_indices),
        "CTW_InvRMSE_p2": ctw.invrmse_weights(ptrain, ytr, train_indices),
    }
    fitted["CTW_SoftOpt"], fallback = ctw.softopt_weights(
        ptrain, ytr, train_indices)
    predictions = {
        "EqualWeight": np.mean(ptest, axis=0),
        "GlobalStacking": metric.fuse(ptest, fitted["GlobalStacking"]),
        "CTW_HardSelect": ctw.fuse_cellwise(
            ptest, fitted["CTW_HardSelect"], "CTW_HardSelect"),
        "CTW_InvRMSE_p2": ctw.fuse_cellwise(
            ptest, fitted["CTW_InvRMSE_p2"], "CTW_InvRMSE_p2"),
        "CTW_SoftOpt": ctw.fuse_cellwise(
            ptest, fitted["CTW_SoftOpt"], "CTW_SoftOpt"),
    }
    for i, method in enumerate(METHODS):
        predictions[method] = ptest[i]
    results = []
    for method, vals in predictions.items():
        x = metric.normalize(vals, method)
        results.append({"scenario": name, "method": method,
                        "n_train_spots": len(train_y),
                        "n_test_spots": len(test_y),
                        "n_reference_cells": len(reference),
                        "n_train_donor_cells": len(split["train_donor"]),
                        "n_test_donor_cells": len(split["test_donor"]),
                        "softopt_fallback_cts": fallback if method == "CTW_SoftOpt" else 0,
                        **metric.metric_dict(yte, x)})
        pd.DataFrame(x, index=test_y.index, columns=classes).to_csv(
            folder / ("test_prediction_" + method + ".csv"))
    for method, weights in fitted.items():
        w = np.asarray(weights)
        if w.ndim == 1:
            w = w[:, None]
            celltypes = ["ALL"]
        else:
            celltypes = list(classes)
        pd.DataFrame(
            [{"fusion": method, "base_method": METHODS[mi],
              "cell_type": ct, "weight": float(w[mi, ci])}
             for mi in range(len(METHODS))
             for ci, ct in enumerate(celltypes)]
        ).to_csv(folder / ("weights_" + method + ".csv"), index=False)
    pd.DataFrame(results).to_csv(done, index=False)
    print("COMPLETED", name, "CTW JSD",
          round(next(x["JSD"] for x in results if x["method"] == "CTW_SoftOpt"), 6),
          "Global JSD",
          round(next(x["JSD"] for x in results if x["method"] == "GlobalStacking"), 6),
          "NNLS_500 JSD",
          round(next(x["JSD"] for x in results if x["method"] == "NNLS_500"), 6),
          "Tangram JSD",
          round(next(x["JSD"] for x in results if x["method"] == "Tangram"), 6),
          "SoftOpt fallback", fallback, flush=True)
    return pd.DataFrame(results)


def main():
    args = get_args()
    if args.train_spots < 100 or args.test_spots < 100 or args.cells_per_spot < 2:
        raise ValueError("Invalid pseudo-spot budget")
    for p in (args.source / "sc_reference_counts.csv",
              args.source / "sc_reference_labels.csv",
              args.tangram_runner, args.tangram_python):
        if not p.is_file():
            raise FileNotFoundError(str(p))
    config = {
        "source": str(args.source.resolve()), "seed": args.seed,
        "train_spots": args.train_spots, "test_spots": args.test_spots,
        "cells_per_spot": args.cells_per_spot,
        "tangram_runner": str(args.tangram_runner.resolve()),
        "tangram_python": str(args.tangram_python.resolve()),
        "tangram_epochs": args.tangram_epochs,
        "tangram_genes": args.tangram_genes,
        "device": args.device, "scenarios": list(SCENARIOS),
        "base_methods": list(METHODS),
        "protocol": "type-stratified disjoint 50pct reference; remaining train/test donors",
        "semantics": "within-source single-cell-disjoint simulated pseudo-spots",
    }
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        if not args.resume:
            raise FileExistsError("Refusing nonempty result folder: " + str(args.out_dir))
        cfgpath = args.out_dir / "run_config.json"
        if not cfgpath.is_file() or json.loads(cfgpath.read_text(encoding="utf-8")) != config:
            raise ValueError("Resume config changed; refusing to mix results")
    counts, labels = read_source(args.source)
    split, split_summary = split_cells(labels, args.seed)
    classes = sorted(labels.unique())
    print("SOURCE", len(counts), "cells", len(counts.columns),
          "genes", len(classes), "types", flush=True)
    for k in ("reference", "train_donor", "test_donor"):
        print("CELL SPLIT", k, len(split[k]), flush=True)
    print("TYPES WITHOUT TEST DONORS",
          split_summary.loc[split_summary.test_donor_n.eq(0), "cell_type"].tolist())
    print("TYPES WITHOUT TRAIN DONORS",
          split_summary.loc[split_summary.train_donor_n.eq(0), "cell_type"].tolist())
    if args.dry_run:
        probe = subprocess.run(
            [str(args.tangram_python), "-c",
             "import sys, tangram, torch, anndata; "
             "print('TANGRAM_IMPORT_PASS', sys.executable, 'CUDA', torch.cuda.is_available())"],
            capture_output=True, text=True)
        if probe.returncode != 0:
            raise RuntimeError("Tangram interpreter cannot import dependencies:\n" +
                               probe.stdout + "\n" + probe.stderr)
        print(probe.stdout.strip())
        # Nonwriting in-memory smoke of the reference-only design and NNLS.
        ref = counts.loc[split["reference"]]
        ref_types = labels.loc[ref.index]
        prof, selections = gene_sets(ref, ref_types, classes)
        for mix_name in SCENARIOS:
            smoke_expr, smoke_loc, smoke_y, smoke_count, smoke_members = make_spots(
                counts, labels, split["train_donor"], classes, 6,
                args.cells_per_spot, args.seed + 999, mix_name, "DRY")
            if not np.allclose(smoke_y.sum(axis=1).to_numpy(), 1.0):
                raise ValueError("Dry-run pseudo-spot truth not compositional")
            for method, gene_idx in selections.items():
                out = nnls_predict(smoke_expr, prof, gene_idx)
                if not np.allclose(out.sum(axis=1).to_numpy(), 1.0):
                    raise ValueError("Dry-run NNLS is not compositional: " + method)
            print("SMOKE PASS", mix_name, "spots", len(smoke_expr),
                  "nnls_methods", len(selections), flush=True)
        print("PLAN scenarios", list(SCENARIOS), "x 2 Tangram runs = 4 mappings;",
              "train/test", args.train_spots, args.test_spots,
              "methods", list(METHODS))
        print("DRY RUN PASS — no files written")
        return
    args.out_dir.mkdir(exist_ok=True, parents=True)
    cfgpath = args.out_dir / "run_config.json"
    if not cfgpath.exists():
        cfgpath.write_text(json.dumps(config, indent=2, ensure_ascii=False),
                           encoding="utf-8")
    if not (args.out_dir / "source_split_by_type.csv").exists():
        split_summary.to_csv(args.out_dir / "source_split_by_type.csv", index=False)
        pd.DataFrame([{"source_cell_id": x, "partition": name,
                       "cell_type": labels.loc[x]}
                      for name, ids in split.items()
                      for x in ids]).to_csv(args.out_dir / "source_cell_partition.csv",
                                          index=False)
    data = []
    for name in SCENARIOS:
        print("START", name, flush=True)
        data.append(run_scenario(name, counts, labels, split, classes, args))
    result = pd.concat(data, ignore_index=True)
    result.to_csv(args.out_dir / "metrics_by_sampling_scenario.csv", index=False)
    print("BATCH FINISHED: 2 scenarios x 8 methods = 16 held-out method/scenario rows")
    print(result[["scenario", "method", "JSD", "matrix_RMSE",
                  "aggregated_celltype_RMSE"]].to_string(index=False))
    print("OUTPUT", args.out_dir)


if __name__ == "__main__":
    main()
