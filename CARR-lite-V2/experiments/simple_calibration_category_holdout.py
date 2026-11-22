#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Simple post-calibration controls for CARR-lite V2 category hold-out.

Predeclared simple calibrators:
  Ridge12       : standardized 12-feature Ridge regression for delta (truth-base)
  Isotonic1D    : monotone 1D map from raw base target proportion to true target

Both use precisely the category-held-in training views and the same local
target/confusion-mass projection and evaluation as the full CARR methods.
They are refitted independently for RCTD and CARD, not cross-method transfer.
No test truth is used for fitting or hyperparameter tuning.

Example:
  python simple_calibration_category_holdout.py --method RCTD --dry-run
  python simple_calibration_category_holdout.py --method RCTD \
    --out-dir "D:\Research\STdeconv_benchmark\results\CARRliteV2_simple_controls_20261122_v1"

The script never overwrites a nonempty output directory.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import category_holdout_carr_v2 as heldout
import cross_method_carr_v2 as cross


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", choices=("RCTD", "CARD"), required=True)
    ap.add_argument("--suite-root", type=Path, default=cross.DEFAULT_SUITE)
    ap.add_argument("--prediction-template",
                    default="predictions/{method}_self_benchmark.csv")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="New batch root; method directory must be empty or absent")
    ap.add_argument("--seed", type=int, default=20260724)
    ap.add_argument("--confusion-k", type=int, default=3)
    ap.add_argument("--marker-k", type=int, default=40)
    ap.add_argument("--no-depth", action="store_true",
                    help="Exclude known depth_fraction feature for Ridge12; "
                         "Isotonic1D never uses that feature")
    ap.add_argument("--dry-run", action="store_true",
                    help="Validate source predictions and disjoint folds, write nothing")
    return ap.parse_args()


def target_truth(d):
    # Same target truth accessor as the existing CARR source snapshot.
    return cross.v2.target_truth(d)


def fit_simple_controls(train):
    """Fit using TRAINING views only. No held-out data or truth here."""
    features = pd.concat([d["features"] for d in train], axis=0)
    delta = np.concatenate([d["labels"].to_numpy(dtype=float) for d in train])
    base = features["base_target"].to_numpy(dtype=float)
    truth_target = np.concatenate([target_truth(d) for d in train])

    if not np.isfinite(features.to_numpy(dtype=float)).all():
        raise ValueError("Non-finite training features")
    if not np.isfinite(truth_target).all() or not np.isfinite(delta).all():
        raise ValueError("Non-finite training labels")
    if np.any(truth_target < -1e-8) or np.any(truth_target > 1 + 1e-8):
        raise ValueError("Ground-truth target proportion outside [0,1]")
    if len(base) < 2 or len(np.unique(base)) < 2:
        raise ValueError("Insufficient distinct training predictions for calibration")

    # Ridge12 is the simple *full-feature* baseline. Alpha is fixed in advance.
    ridge = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    ridge.fit(features.to_numpy(dtype=float), delta)

    # Isotonic1D only knows the raw target abundance. Its monotonic constraint
    # preserves ranking except for ties/clipping/projection; no extra features.
    iso = IsotonicRegression(
        increasing=True, out_of_bounds="clip", y_min=0.0, y_max=1.0
    )
    iso.fit(base, truth_target)
    return ridge, iso


def apply_simple_controls(d, trained):
    ridge, iso = trained
    features = d["features"].to_numpy(dtype=float)
    delta = ridge.predict(features)
    ridge_prediction = cross.v1.apply_local_correction(d, delta)

    base_target = d["features"]["base_target"].to_numpy(dtype=float)
    target_prediction = iso.predict(base_target)
    iso_prediction = cross.v2.set_local_target(d, target_prediction)
    return {"Ridge12": ridge_prediction, "Isotonic1D": iso_prediction}


def main():
    args = parse_args()
    views = cross.read_views(args.suite_root)
    plan = heldout.build_plan(views, args)  # Validates each input against truth.
    print("INPUT CHECK PASS:", args.method, len(plan), "scenario views / 13 bases")
    print("SPLIT CHECK PASS: four disjoint held-out categories")
    print("CONTROLS: Ridge12, Isotonic1D")
    print("DEPTH FEATURE:", "excluded from Ridge12" if args.no_depth
          else "included in Ridge12 (simulated protocol only)")
    if args.dry_run:
        print("DRY RUN PASS — no files written")
        return

    root = (args.out_dir or
            args.suite_root / "batch_runs" / "CARRliteV2_simple_controls")
    method_output = root / args.method
    if args.no_depth:
        method_output = method_output / "no_depth"
    if method_output.exists() and any(method_output.iterdir()):
        raise FileExistsError("Output directory nonempty; refusing overwrite: "
                              + str(method_output))

    datasets = []
    for i, (scenario, folder) in enumerate(views, 1):
        input_file = cross.prediction_path(
            folder, scenario, args.method, args.prediction_template
        )
        d = cross.make_dataset(
            folder, scenario, input_file, args.confusion_k, args.marker_k
        )
        d["category"] = heldout.category_from_base(d["base"])
        if args.no_depth:
            d["features"] = d["features"].drop(columns=["depth_fraction"])
        if set(d["features"].columns) - set(cross.ABLATION_COLUMNS.get(
                "none", ())) == set():
            raise ValueError("Unexpected empty features")
        datasets.append(d)
        print("Loaded", i, "/", len(views), scenario, flush=True)

    if len(datasets) != 52 or {
            d["scenario_id"] for d in datasets
    } != {r["scenario_id"] for r in plan}:
        raise ValueError("Dataset/manifest mismatch")
    if len({d["base"] for d in datasets}) != 13:
        raise ValueError("Expected exactly 13 distinct base groups")
    # Validate same ordered feature schema before any output is made.
    feature_schema = tuple(datasets[0]["features"].columns)
    if any(tuple(d["features"].columns) != feature_schema for d in datasets):
        raise ValueError("Inconsistent feature columns across views")

    metrics = []
    manifest = []
    method_output.mkdir(parents=True, exist_ok=True)
    for fold, category in enumerate(heldout.CATEGORIES, 1):
        train = [d for d in datasets if d["category"] != category]
        test = [d for d in datasets if d["category"] == category]
        if len(test) != heldout.EXPECTED_VIEWS[category]:
            raise ValueError("Test view count mismatch in " + category)
        train_base = {d["base"] for d in train}
        test_base = {d["base"] for d in test}
        if train_base & test_base:
            raise ValueError("Training/test base overlap in " + category)
        print("TRAINING FOLD", fold, category,
              "train", len(train), "test", len(test), flush=True)
        models = fit_simple_controls(train)
        for d in test:
            predictions = {"Original_" + args.method: d["prediction"]}
            predictions.update(apply_simple_controls(d, models))
            dest = method_output / d["scenario_id"]
            dest.mkdir(parents=True, exist_ok=False)
            manifest.append({
                "scenario_id": d["scenario_id"],
                "held_out_base": d["base"],
                "held_out_category": category,
                "fold": fold,
                "train_views": len(train),
                "test_views": len(test),
            })
            for label, pred in predictions.items():
                # Reuse evaluator and EXACT random seed logic from strict
                # category-held-out CARR experiment for balanced AUPRC.
                seed = args.seed + 100 * fold + int(d["depth"])
                metric = cross.v1.evaluate(d, pred, label, seed)
                metric.update({
                    "scenario_id": d["scenario_id"],
                    "base_method": args.method,
                    "held_out_category": category,
                    "fold": fold,
                    "split_mode": "category_holdout",
                    "no_depth": args.no_depth,
                })
                metrics.append(metric)
                pred.to_csv(dest / (label + ".csv"))
            print("Completed", d["scenario_id"], flush=True)
        pd.DataFrame(metrics).to_csv(
            method_output / "metrics_by_scenario.csv", index=False
        )

    if len(metrics) != 156 or len(manifest) != 52:
        raise ValueError("Unexpected output count (expected 52 views * 3)")
    pd.DataFrame(manifest).to_csv(method_output / "split_manifest.csv", index=False)
    (method_output / "run_config.json").write_text(
        json.dumps({
            "status": "exploratory",
            "protocol": "leave_one_category_out",
            "method": args.method,
            "seed": args.seed,
            "confusion_k": args.confusion_k,
            "marker_k": args.marker_k,
            "no_depth": args.no_depth,
            "controls": [
                {"name": "Ridge12", "model": "StandardScaler+Ridge",
                 "alpha": 1.0, "fit_target": "true_target - base_target",
                 "features": list(feature_schema)},
                {"name": "Isotonic1D", "model": "IsotonicRegression",
                 "input_feature": "base_target",
                 "fit_target": "true_target", "out_of_bounds": "clip",
                 "increasing": True},
            ],
            "projection": "same local confusion-mass-constrained projection as CARR",
            "evaluation": "v1.evaluate; same fold & depth seeds as strict CARR",
            "source_inputs": plan,
            "notes": [
                "Both simple calibrators are fit only on held-in categories.",
                "Ridge12 controls for the 12-feature access of full CARR.",
                "Isotonic1D uses one raw abundance feature only.",
                "Original prediction is re-evaluated as a seed/metric alignment control.",
                "Independent external biological validity has not been established."
            ],
        }, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("FINISHED", len(metrics), "result rows")
    print("OUTPUT", method_output)


if __name__ == "__main__":
    main()
