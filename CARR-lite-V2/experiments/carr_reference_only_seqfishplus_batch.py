#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CARR-lite V2 reference-cell-only synthetic training -> held-out seqFISH+ FOV.

Uses ONLY reference cells (from each existing outer FOV fold) to create
supervised training pseudo-spots. Keeps disjoint reference-cell subsets:
  generator cells -> synthetic spot expression + synthetic known proportions
  mapping cells   -> Tangram reference AND CARR feature reference profiles
Re-runs Tangram on BOTH synthetic training and held-out test expression using
the SAME mapping reference cells, to avoid comparing incompatible baselines.

Reuses existing, unmodified local scripts:
  D:/Research/STdeconv_benchmark/methods/Tangram/run_tangram_self_benchmark.py
  D:/Research/STdeconv_benchmark/run_carr_lite_v2_seqfishplus_5fold.py

No true held-out FOV labels/counts/proportions are loaded before predictions
are finished; they are loaded exclusively in the final evaluation block.
All experiment inputs, Tangram predictions, and output metrics are written to
a new RESULTS directory. The old fold directories and results are read only.

--dry-run checks five input folds and local runners without any writes.
--run executes all five FOVs; --resume resumes an interrupted same-config run.

This is same-source seqFISH+-reference-cell training, NOT independent scRNA-seq
or cross-platform validation. Pseudo-spots reused generator cells; they are
synthetic augmentations, not independent biological replicates.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
from time import perf_counter

import numpy as np
import pandas as pd

DEFAULT_DATA = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\seqfishplus_cortex_real_spatial_noleak")
DEFAULT_OUT = Path(r"D:\Research\STdeconv_benchmark\results\CARR_reference_only_seqfishplus_20261123_v1")
DEFAULT_CARR = Path(r"D:\Research\STdeconv_benchmark\run_carr_lite_v2_seqfishplus_5fold.py")
DEFAULT_TANGRAM = Path(r"D:\Research\STdeconv_benchmark\methods\Tangram\run_tangram_self_benchmark.py")
METRICS = ("matrix_RMSE", "mean_spot_JSD", "singleton_RMSE", "singleton_vs_zero_AUPRC",
           "singleton_vs_zero_AUROC", "zero_prediction_mean")
REQUIRED = ("pseudo_spot_expression.csv", "pseudo_spot_locations.csv",
            "sc_reference_counts.csv", "sc_reference_labels.csv",
            "pseudo_spot_ground_truth.csv", "pseudo_spot_ground_truth_counts.csv")


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--carr-runner", type=Path, default=DEFAULT_CARR)
    p.add_argument("--tangram-runner", type=Path, default=DEFAULT_TANGRAM)
    p.add_argument("--tangram-python", type=Path, default=Path(sys.executable),
                   help="Python executable for Tangram subprocesses; separate from the CARR environment")
    p.add_argument("--n-train-spots", type=int, default=400)
    p.add_argument("--min-cells", type=int, default=6)
    p.add_argument("--max-cells", type=int, default=12)
    p.add_argument("--seed", type=int, default=20261123)
    p.add_argument("--num-epochs", type=int, default=500)
    p.add_argument("--max-genes", type=int, default=3000)
    p.add_argument("--device", default="auto")
    return p.parse_args()


def read_matrix(path):
    x = pd.read_csv(path, index_col=0)
    x.index = x.index.astype(str)
    x.columns = x.columns.astype(str)
    return x


def get_labels(path):
    tab = read_matrix(path)
    options = ["label", "cell_type", "celltype", "annotation", "Subset", "cluster"]
    names = [k for k in options if k in tab.columns]
    if names:
        key = names[0]
    elif tab.shape[1] == 1:
        key = str(tab.columns[0])
    else:
        raise ValueError("Cannot identify reference label column in " + str(path))
    return tab[key].astype(str)


def load_source(fold):
    reference = read_matrix(fold / "sc_reference_counts.csv")
    labels = get_labels(fold / "sc_reference_labels.csv")
    common_cells = reference.index.intersection(labels.index)
    reference = reference.loc[common_cells]
    labels = labels.loc[common_cells]
    expression = read_matrix(fold / "pseudo_spot_expression.csv")
    locations = read_matrix(fold / "pseudo_spot_locations.csv")
    if not expression.index.is_unique or not reference.index.is_unique:
        raise ValueError(f"Duplicated cell or spot IDs in {fold}")
    if not expression.index.isin(locations.index).all():
        raise ValueError(f"Unmatched test spot coordinates in {fold}")
    if not expression.index.is_unique:
        raise ValueError("Nonunique target spots")
    if not reference.columns.is_unique or not expression.columns.is_unique:
        raise ValueError("Duplicate gene names")
    genes = reference.columns.intersection(expression.columns)
    if len(genes) < 10:
        raise ValueError("Insufficient shared reference/target genes")
    if len(common_cells) < 50:
        raise ValueError("Insufficient outer reference cells")
    if not np.isfinite(reference[genes].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite reference counts")
    if not np.isfinite(expression[genes].to_numpy(dtype=float)).all():
        raise ValueError("Nonfinite test spot expression")
    if reference[genes].to_numpy(dtype=float).min() < 0 or expression[genes].to_numpy(dtype=float).min() < 0:
        raise ValueError("Negative counts")
    return reference.loc[:, genes], labels, expression.loc[:, genes], locations.loc[expression.index]


def split_reference(reference, labels, seed):
    rng = np.random.default_rng(seed)
    generator, mapping = [], []
    for ct in sorted(labels.unique()):
        cells = labels[labels == ct].index.to_numpy()
        cells = rng.permutation(cells)
        if len(cells) == 1:
            n_gen = 0  # keep one mapping exemplar, no synthetic donor
        else:
            n_gen = min(len(cells) - 1, max(1, int(round(0.40 * len(cells)))))
        generator.extend(cells[:n_gen].tolist())
        mapping.extend(cells[n_gen:].tolist())
    if len(generator) < 30 or len(mapping) < len(labels.unique()):
        raise ValueError("Reference split cannot support generation and all types")
    if set(generator).intersection(mapping):
        raise ValueError("Reference generator/mapping cell overlap")
    return (reference.loc[generator], labels.loc[generator],
            reference.loc[mapping], labels.loc[mapping])


def make_synthetic(gen_counts, gen_labels, cell_types, n_spots, min_cells, max_cells, seed):
    rng = np.random.default_rng(seed)
    gen = gen_counts.to_numpy(dtype=np.float32)
    uid = gen_counts.index.to_numpy()
    types = pd.Index(cell_types)
    type_index = types.get_indexer(gen_labels.values)
    if np.any(type_index < 0):
        raise ValueError("Unrecognized reference class")
    n = len(uid)
    if n < max_cells:
        raise ValueError("Not enough generator cells per synthetic spot")
    class_sizes = gen_labels.value_counts()
    rare_pool = class_sizes.sort_values().index[:max(1, len(class_sizes) // 3)]
    rare_candidates = np.flatnonzero(gen_labels.isin(rare_pool).to_numpy())
    expression = np.zeros((n_spots, gen.shape[1]), dtype=np.float32)
    counts = np.zeros((n_spots, len(types)), dtype=np.int32)
    membership = []
    policies = []
    spot_ids = [f"synthetic_{k:04d}" for k in range(n_spots)]
    for i, spot in enumerate(spot_ids):
        n_cells = int(rng.integers(min_cells, max_cells + 1))
        policy = "natural" if i % 2 == 0 else "rare_enriched"
        if policy == "rare_enriched":
            preferred = int(rng.choice(rare_candidates))
            rest = np.arange(n)
            rest = rest[rest != preferred]
            chosen = np.r_[preferred, rng.choice(rest, size=n_cells - 1, replace=False)]
        else:
            chosen = rng.choice(n, size=n_cells, replace=False)
        expression[i] = gen[chosen].sum(axis=0)
        counts[i] = np.bincount(type_index[chosen], minlength=len(types))
        policies.append(policy)
        membership.extend({"spot_id": spot, "source_cell_id": str(uid[j]),
                           "cell_type": str(gen_labels.iloc[j]), "policy": policy}
                          for j in chosen)
    expr = pd.DataFrame(expression, index=spot_ids, columns=gen_counts.columns)
    ct = pd.DataFrame(counts, index=spot_ids, columns=types)
    truth = ct.div(ct.sum(axis=1), axis=0)
    loc = pd.DataFrame({
        "grid_center_x": [i % 20 for i in range(n_spots)],
        "grid_center_y": [i // 20 for i in range(n_spots)]},
        index=spot_ids)
    return expr, ct, truth, loc, pd.DataFrame(membership), policies


def write_prediction_inputs(folder, expression, locations, ref_counts, ref_labels,
                            truth=None, count_truth=None, membership=None):
    folder.mkdir(parents=True, exist_ok=False)
    expression.to_csv(folder / "pseudo_spot_expression.csv")
    locations.to_csv(folder / "pseudo_spot_locations.csv")
    ref_counts.to_csv(folder / "sc_reference_counts.csv")
    ref_labels.rename("label").to_frame().to_csv(folder / "sc_reference_labels.csv")
    if truth is not None:
        truth.to_csv(folder / "pseudo_spot_ground_truth.csv")
        count_truth.to_csv(folder / "pseudo_spot_ground_truth_counts.csv")
        membership.to_csv(folder / "synthetic_spot_membership.csv", index=False)


def import_carr(path):
    spec = importlib.util.spec_from_file_location("original_carr_seqfishplus", str(path))
    if spec is None or spec.loader is None:
        raise ImportError("Cannot load user's existing CARR source")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    assert len(module.FEATURE_COLUMNS) == 12
    return module


def tangram(folder, runner, args, log_dir, role):
    prediction = folder / "predictions" / "Tangram_self_benchmark.csv"
    if prediction.is_file():
        pred = read_matrix(prediction)
        expected_spots = read_matrix(folder / "pseudo_spot_expression.csv").index
        labels = get_labels(folder / "sc_reference_labels.csv")
        if set(pred.index) != set(expected_spots) or set(pred.columns) != set(labels.unique()):
            raise ValueError("Existing Tangram prediction invalid: " + str(prediction))
        print("  REUSE", role, prediction, flush=True)
        return pred
    log_dir.mkdir(parents=True, exist_ok=True)
    cmd = [str(args.tangram_python), str(runner), "--base_dir", str(folder),
           "--seed", str(args.seed), "--num_epochs", str(args.num_epochs),
           "--mode", "cells", "--density_prior", "rna_count_based",
           "--device", str(args.device), "--max_genes", str(args.max_genes)]
    log = log_dir / (role + "_tangram.log")
    t0 = perf_counter()
    with log.open("w", encoding="utf-8") as f:
        f.write("COMMAND " + subprocess.list2cmdline(cmd) + "\n")
        f.flush()
        proc = subprocess.run(cmd, stdout=f, stderr=subprocess.STDOUT)
    if proc.returncode != 0 or not prediction.is_file():
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-20:]
        raise RuntimeError(role + " Tangram failed; log " + str(log) +
                           "\n" + "\n".join(tail))
    print("  TANGRAM", role, "seconds", round(perf_counter() - t0, 2), flush=True)
    return read_matrix(prediction)


def target_inference_bundle(source_expression, source_locations, ref_counts, ref_labels,
                            target_pred, cell_types, fov):
    # Deliberately DO NOT read target pseudo_spot_ground_truth or target count truth.
    spot_ids = source_expression.index
    pred = target_pred.loc[spot_ids, cell_types].astype(float)
    if not np.isfinite(pred.to_numpy()).all():
        raise ValueError("Target prediction has nonfinite outputs")
    dummy = pd.DataFrame(0.0, index=spot_ids, columns=cell_types)
    return {
        "fold": None, "fov": fov, "truth": dummy, "counts": dummy,
        "expression": source_expression, "locations": source_locations,
        "prediction": pred,
        "ref_counts": ref_counts, "ref_labels": ref_labels,
    }


def run_fold(fold, outer_dir, args, carr):
    fov = int(fold.name.replace("held_out_FOV", ""))
    done = outer_dir / "fov_metrics.csv"
    if done.is_file():
        print("SKIP COMPLETED FOV", fov, flush=True)
        return pd.read_csv(done)
    outer_dir.mkdir(parents=True, exist_ok=True)
    ref, labels, target_expr, target_loc = load_source(fold)
    generator, gen_labels, mapper, map_labels = split_reference(ref, labels, args.seed + 100 * fov)
    types = pd.Index(sorted(map_labels.unique()))
    syn_expr, syn_counts, syn_truth, syn_loc, members, policies = make_synthetic(
        generator, gen_labels, types, args.n_train_spots,
        args.min_cells, args.max_cells, args.seed + fov)
    train_dir = outer_dir / "synthetic_train"
    test_dir = outer_dir / "heldout_test"
    if not train_dir.exists():
        write_prediction_inputs(train_dir, syn_expr, syn_loc, mapper, map_labels,
                                truth=syn_truth, count_truth=syn_counts, membership=members)
    if not test_dir.exists():
        # No true target ground-truth file is copied into inference directory.
        write_prediction_inputs(test_dir, target_expr, target_loc, mapper, map_labels)
    diagnostics = {
        "held_out_fov": fov, "n_generator_cells": len(generator),
        "n_mapping_reference_cells": len(mapper),
        "n_reference_cell_types": len(types), "n_synthetic_training_spots": len(syn_expr),
        "n_synthetic_membership_records": len(members),
        "n_test_spots": len(target_expr),
        "n_natural_spots": policies.count("natural"),
        "n_rare_enriched_spots": policies.count("rare_enriched"),
        "n_generator_mapping_overlap": len(generator.index.intersection(mapper.index)),
        "singletons_unsupported_in_generator": "|".join(
            sorted(set(types) - set(gen_labels.unique()))),
    }
    (outer_dir / "source_split_diagnostics.json").write_text(
        json.dumps(diagnostics, indent=2, ensure_ascii=False), encoding="utf-8")
    train_pred = tangram(train_dir, args.tangram_runner, args, outer_dir / "logs", "train")
    test_pred = tangram(test_dir, args.tangram_runner, args, outer_dir / "logs", "test")
    train_dataset = {
        "fold": train_dir, "fov": "synthetic", "truth": syn_truth, "counts": syn_counts,
        "expression": syn_expr, "locations": syn_loc,
        "prediction": train_pred.loc[syn_truth.index, types],
        "ref_counts": mapper, "ref_labels": map_labels,
    }
    profiles = carr.reference_profiles(mapper, map_labels, syn_expr.columns, types)
    train_bundle = carr.build_candidates(train_dataset, profiles, confusion_k=3, marker_k=40)
    model = carr.fit_models(train_bundle["candidates"], seed=args.seed + 10 * fov)
    test_dataset = target_inference_bundle(
        target_expr, target_loc, mapper, map_labels, test_pred, types, fov)
    test_bundle = carr.build_candidates(test_dataset, profiles, confusion_k=3, marker_k=40)
    q_pred, gates, _ = carr.make_predictions(test_bundle, model, [0.50])
    outputs = {
        "Tangram_reference_matched": test_dataset["prediction"],
        "CARR_reference_only_AbundanceOnly": q_pred,
        "CARR_reference_only_Gate_a50": gates[0.50],
    }
    for pred in outputs.values():
        carr.validate_output(pred, test_dataset["truth"])
    pdir = outer_dir / "predictions"
    pdir.mkdir(exist_ok=True)
    for name, pred in outputs.items():
        pred.to_csv(pdir / (name + ".csv"))
    # Ground truth is read only AFTER all held-out FOV predictions are saved.
    truth = read_matrix(fold / "pseudo_spot_ground_truth.csv").astype(float)
    true_counts = read_matrix(fold / "pseudo_spot_ground_truth_counts.csv").astype(float)
    if not truth.index.equals(target_expr.index) or set(truth.columns) != set(types):
        raise ValueError("Evaluation-only truth index/class mismatch for FOV" + str(fov))
    truth = truth.loc[target_expr.index, types]
    true_counts = true_counts.loc[target_expr.index, types]
    eval_dataset = {"fov": fov, "truth": truth, "counts": true_counts}
    rows = [carr.evaluate(eval_dataset, pred, name) for name, pred in outputs.items()]
    pd.DataFrame(rows).to_csv(done, index=False)
    print("COMPLETED FOV", fov,
          "Tangram JSD", round(rows[0]["mean_spot_JSD"], 6),
          "CARR JSD", round(rows[2]["mean_spot_JSD"], 6),
          "Tangram singleton AUPRC", round(rows[0]["singleton_vs_zero_AUPRC"], 6),
          "CARR singleton AUPRC", round(rows[2]["singleton_vs_zero_AUPRC"], 6),
          flush=True)
    return pd.DataFrame(rows)


def main():
    args = arguments()
    if args.n_train_spots < 20 or args.min_cells < 2 or args.max_cells < args.min_cells:
        raise ValueError("Invalid synthetic spot count/cells-per-spot settings")
    for path in (args.data_root, args.carr_runner, args.tangram_runner, args.tangram_python):
        if not path.exists():
            raise FileNotFoundError(str(path))
    folds = sorted(args.data_root.glob("held_out_FOV*"),
                   key=lambda p: int(p.name.replace("held_out_FOV", "")))
    if [p.name for p in folds] != [f"held_out_FOV{i}" for i in range(5)]:
        raise ValueError("Expected exactly held_out_FOV0..held_out_FOV4")
    config = {
        "n_train_spots": args.n_train_spots, "min_cells": args.min_cells,
        "max_cells": args.max_cells, "seed": args.seed,
        "num_epochs": args.num_epochs, "max_genes": args.max_genes,
        "device": args.device, "data_root": str(args.data_root.resolve()),
        "carr_runner": str(args.carr_runner.resolve()),
        "tangram_runner": str(args.tangram_runner.resolve()),
        "folds": [f.name for f in folds],
        "protocol": "40 percent stratified generator, rest mapping; 50pct natural/rare enriched;",
        "base_method": "Tangram mode=cells density_prior=rna_count_based (both train and test)",
        "CARR": "historical runner 12 features, marker_k40, confusion_k3, Gate_a50",
        "evaluation": "5 leave-one-FOV-out spatially-informed pseudo-spots; truth only after inference",
        "scientific_boundary": [
            "Reference cells originate from same seqFISH+ sample/domain, not external scRNA",
            "Generator and mapping cells ID-disjoint for each outer fold",
            "Training spot expression is cell-count-summed synthetic mixture, not direct spatial spot",
            "Synthetic spots reuse generator cells across spots, not independent samples",
            "True held-out FOV labels not used to train CARR or Tangram",
            "Tangram is transductive on unlabeled spot expression",
            "Not a cross-platform or independent donor generalization evaluation",
        ],
    }
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        if not args.resume:
            raise FileExistsError("Output is nonempty; refuse overwrite: " + str(args.out_dir) +
                                  ". To resume the identical config use --run --resume.")
        saved = json.loads((args.out_dir / "run_config.json").read_text(encoding="utf-8"))
        if saved != config:
            raise ValueError("Resume configuration differs from original run")
    if args.dry_run:
        if args.resume:
            raise ValueError("--resume is only valid with --run")
        print("TANGRAM PYTHON", args.tangram_python, flush=True)
        probe = subprocess.run(
            [str(args.tangram_python), "-c",
             "import sys, tangram, torch, anndata; "
             "print('TANGRAM_IMPORT_PASS', sys.executable, 'CUDA', torch.cuda.is_available())"],
            capture_output=True, text=True)
        if probe.returncode != 0:
            raise RuntimeError("Tangram interpreter preflight failed:\n" +
                               probe.stdout + "\n" + probe.stderr)
        print(probe.stdout.strip(), flush=True)
        print("PLAN 5 held-out FOV x 2 Tangram fits = 10 new Tangram maps")
        print("TRAIN", args.n_train_spots, "reference-cell-generated pseudo-spots per FOV")
        print("PREDICT", "Tangram / CARR abundance-only / CARR Gate a50")
        for f in folds:
            ref, labels, expr, loc = load_source(f)
            generator, g_labels, mapper, m_labels = split_reference(
                ref, labels, args.seed + 100 * int(f.name.replace("held_out_FOV", "")))
            print("CHECK", f.name, "target_spots", len(expr), "genes", len(expr.columns),
                  "generator_cells", len(generator), "mapping_cells", len(mapper),
                  "mapping_types", m_labels.nunique(), flush=True)
        import_carr(args.carr_runner)
        print("DRY RUN PASS — no files written")
        return

    carr = import_carr(args.carr_runner)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    # A previous run may have been interrupted before Tangram import. Preserve
    # its original run_config.json; record the new subprocess interpreter
    # separately, so --resume retains exact-config matching.
    runtime_path = args.out_dir / "tangram_python_runtime.json"
    runtime = {"tangram_python": str(args.tangram_python.resolve())}
    if runtime_path.exists():
        saved_runtime = json.loads(runtime_path.read_text(encoding="utf-8"))
        if saved_runtime != runtime:
            raise ValueError("Tangram interpreter differs from existing resume runtime")
    else:
        old_predictions = list(args.out_dir.glob(
            "held_out_FOV*/**/predictions/Tangram_self_benchmark.csv"))
        if old_predictions:
            raise ValueError("Existing Tangram predictions lack interpreter provenance; "
                             "refuse to mix Python environments mid-resume")
        runtime_path.write_text(
            json.dumps(runtime, indent=2, ensure_ascii=False), encoding="utf-8")
    print("TANGRAM SUBPROCESS PYTHON", args.tangram_python, flush=True)
    if not (args.out_dir / "run_config.json").exists():
        (args.out_dir / "run_config.json").write_text(
            json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")
    frames = []
    for f in folds:
        fov = int(f.name.replace("held_out_FOV", ""))
        print("START FOV", fov, flush=True)
        result = run_fold(f, args.out_dir / f.name, args, carr)
        frames.append(result)
    all_metrics = pd.concat(frames, ignore_index=True)
    all_metrics.to_csv(args.out_dir / "all_fov_metrics.csv", index=False)
    summary = all_metrics.groupby("method")[list(METRICS)].mean().reset_index()
    summary.to_csv(args.out_dir / "five_fov_descriptive_means.csv", index=False)
    paired = []
    for fov, group in all_metrics.groupby("held_out_fov"):
        by = group.set_index("method")
        orig = by.loc["Tangram_reference_matched"]
        for method in ("CARR_reference_only_AbundanceOnly", "CARR_reference_only_Gate_a50"):
            met = by.loc[method]
            paired.append({"held_out_fov": fov, "method": method,
                           **{"delta_" + key: float(met[key] - orig[key]) for key in METRICS}})
    pd.DataFrame(paired).to_csv(args.out_dir / "paired_fov_differences.csv", index=False)
    print("BATCH FINISHED 5 FOV; 15 held-out method/FOV metric rows")
    print("OUTPUT", args.out_dir)
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
