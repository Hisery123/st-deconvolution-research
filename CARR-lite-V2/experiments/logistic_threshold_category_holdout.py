#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Predeclared logistic and fixed-threshold controls for CARR-lite V2.

Uses the same four leave-category-out folds, local mass-conserving target
projection, and evaluation seeds as category_holdout_carr_v2.py.
LogisticPresence12 fits class-balanced LogisticRegression to training-view
presence and uses the TRAINING-ONLY mean positive proportion as its amount.
Threshold1D applies a fixed 0.005 cut to the raw target prediction, with no
threshold tuning. Both controls are intentionally simple comparators.

Examples:
  python logistic_threshold_category_holdout.py --method RCTD --dry-run
  python logistic_threshold_category_holdout.py --method RCTD --out-dir NEW_ROOT
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import category_holdout_carr_v2 as heldout
import cross_method_carr_v2 as cross

CONTROL_NAMES = ("LogisticPresence12", "Threshold1D")
THRESHOLD = 0.005


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", required=True, choices=("RCTD", "CARD"))
    ap.add_argument("--suite-root", type=Path, default=cross.DEFAULT_SUITE)
    ap.add_argument("--prediction-template", default="predictions/{method}_self_benchmark.csv")
    ap.add_argument("--out-dir", type=Path, default=None)
    ap.add_argument("--seed", type=int, default=20260724)
    ap.add_argument("--confusion-k", type=int, default=3)
    ap.add_argument("--marker-k", type=int, default=40)
    ap.add_argument("--dry-run", action="store_true")
    return ap.parse_args()


def train_logistic(train, seed):
    features = pd.concat([d["features"] for d in train], axis=0)
    truth = np.concatenate([cross.v2.target_truth(d) for d in train])
    if len(features) != len(truth) or not np.isfinite(features.to_numpy(dtype=float)).all():
        raise ValueError("Invalid training features/labels")
    presence = (truth > 0).astype(int)
    if set(np.unique(presence)) != {0, 1}:
        raise ValueError("Both presence classes required in training folds")
    positive_mean = float(np.mean(truth[presence == 1]))
    if not (0 < positive_mean <= 1.0):
        raise ValueError("Invalid positive class mean")
    model = make_pipeline(
        StandardScaler(),
        LogisticRegression(C=1.0, class_weight="balanced", max_iter=2000,
                           random_state=seed),
    )
    model.fit(features.to_numpy(dtype=float), presence)
    return model, positive_mean


def apply_controls(dataset, trained):
    model, positive_mean = trained
    x = dataset["features"].to_numpy(dtype=float)
    p = model.predict_proba(x)[:, 1]
    desired = np.clip(p * positive_mean, 0.0, 1.0)
    logistic = cross.v2.set_local_target(dataset, desired)

    base = dataset["features"]["base_target"].to_numpy(dtype=float)
    threshold_target = np.where(base >= THRESHOLD, base, 0.0)
    threshold = cross.v2.set_local_target(dataset, threshold_target)
    return {"LogisticPresence12": logistic, "Threshold1D": threshold}


def main():
    args = parse_args()
    views = cross.read_views(args.suite_root)
    plan = heldout.build_plan(views, args)
    print("INPUT CHECK PASS:", args.method, len(plan), "scenario views / 13 bases", flush=True)
    print("SPLIT CHECK PASS: four disjoint held-out categories", flush=True)
    print("CONTROLS:", ", ".join(CONTROL_NAMES), "threshold", THRESHOLD, flush=True)
    if args.dry_run:
        print("DRY RUN PASS — no files written", flush=True)
        return

    out_root = args.out_dir or (args.suite_root / "batch_runs" / "CARRliteV2_logistic_threshold")
    out = out_root / args.method
    if out.exists() and any(out.iterdir()):
        raise FileExistsError("Output directory nonempty: " + str(out))

    datasets = []
    for i, (scenario, folder) in enumerate(views, 1):
        pred_path = cross.prediction_path(folder, scenario, args.method,
                                         args.prediction_template)
        d = cross.make_dataset(folder, scenario, pred_path,
                               args.confusion_k, args.marker_k)
        d["category"] = heldout.category_from_base(d["base"])
        datasets.append(d)
        print("Loaded", i, "/", len(views), scenario, flush=True)

    feature_schema = tuple(datasets[0]["features"].columns)
    if len(datasets) != 52 or len(feature_schema) != 12:
        raise ValueError("Unexpected scenario count or 12-feature layout")
    if any(tuple(d["features"].columns) != feature_schema for d in datasets):
        raise ValueError("Feature schema inconsistent across views")
    out.mkdir(parents=True, exist_ok=True)
    rows, manifest = [], []
    for fold, cat in enumerate(heldout.CATEGORIES, 1):
        train = [d for d in datasets if d["category"] != cat]
        test = [d for d in datasets if d["category"] == cat]
        if len(test) != heldout.EXPECTED_VIEWS[cat] or ({d["base"] for d in train} & {d["base"] for d in test}):
            raise ValueError("Fold group leakage / view count mismatch: " + cat)
        print("TRAINING FOLD", fold, cat, "train", len(train), "test", len(test), flush=True)
        trained = train_logistic(train, args.seed + fold)
        for d in test:
            outputs = {"Original_" + args.method: d["prediction"]}
            outputs.update(apply_controls(d, trained))
            dest = out / d["scenario_id"]
            dest.mkdir(parents=True, exist_ok=False)
            manifest.append({"scenario_id": d["scenario_id"],
                             "held_out_base": d["base"], "held_out_category": cat,
                             "fold": fold})
            for label, prediction in outputs.items():
                prediction.to_csv(dest / (label + ".csv"))
                metric = cross.v1.evaluate(d, prediction, label,
                                            args.seed + fold * 100 + int(d["depth"]))
                metric.update({"scenario_id": d["scenario_id"],
                               "base_method": args.method, "held_out_base": d["base"],
                               "held_out_category": cat, "fold": fold,
                               "split_mode": "category_holdout"})
                rows.append(metric)
            print("Completed", d["scenario_id"], flush=True)
        pd.DataFrame(rows).to_csv(out / "metrics_by_scenario.csv", index=False)

    if len(rows) != 156 or len(manifest) != 52:
        raise ValueError("Unexpected number of evaluation rows")
    pd.DataFrame(manifest).to_csv(out / "split_manifest.csv", index=False)
    config = {
        "status": "exploratory", "method": args.method,
        "base_method": args.method, "seed": args.seed, "confusion_k": args.confusion_k,
        "marker_k": args.marker_k, "folds": list(heldout.CATEGORIES),
        "split_mode": "leave_one_category_out", "prediction_template": args.prediction_template,
        "features": list(feature_schema),
        "controls": [
            {"name": "LogisticPresence12", "model": "StandardScaler + class_balanced_LogisticRegression",
             "C": 1.0, "class_weight": "balanced", "positive_amount": "training positive mean"},
            {"name": "Threshold1D", "threshold": THRESHOLD,
             "threshold_source": "fixed in advance; no fitting"},
        ],
        "notes": ["Same split and metric seeds as category_holdout_carr_v2.py",
                  "Calibration separately fitted per base method and held-in categories",
                  "Logistic uses simulated known-depth feature; real data needs no-depth study",
                  "Threshold1D is a fixed comparator; no threshold search on held-out labels"],
    }
    (out / "run_config.json").write_text(json.dumps(config, ensure_ascii=False, indent=2),
                                          encoding="utf-8")
    print("FINISHED", len(rows), "result rows", flush=True)
    print("OUTPUT", out, flush=True)


if __name__ == "__main__":
    main()
