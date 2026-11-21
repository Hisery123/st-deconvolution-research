#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Stricter four-category held-out validation of CARR-lite V2 on RCTD/CARD.

Uses the same feature construction, three-branch model, evaluation, and inputs
as cross_method_carr_v2.py. The ONLY planned experimental change is the split:
hold out all bases and all four sequencing depths belonging to one category
(stable / medium / confusable / lowref) at once. Each base method is retrained
independently; this is not zero-shot cross-method transfer.

Example (checks inputs, writes nothing):
  python category_holdout_carr_v2.py --method RCTD --dry-run
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path

import pandas as pd

import cross_method_carr_v2 as cross

CATEGORIES = ("stable", "medium", "confusable", "lowref")
EXPECTED_BASES = {"stable": 4, "medium": 3, "confusable": 3, "lowref": 3}
EXPECTED_VIEWS = {k: 4 * v for k, v in EXPECTED_BASES.items()}


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--method", choices=("RCTD", "CARD"), required=True)
    parser.add_argument("--suite-root", type=Path, default=cross.DEFAULT_SUITE)
    parser.add_argument("--prediction-template",
                        default="predictions/{method}_self_benchmark.csv")
    parser.add_argument("--out-dir", type=Path, default=None,
                        help="Root of a NEW output batch; never reuse leave-base outputs")
    parser.add_argument("--seed", type=int, default=20260724)
    parser.add_argument("--confusion-k", type=int, default=3)
    parser.add_argument("--marker-k", type=int, default=40)
    parser.add_argument("--ablation", choices=("none", "no_depth"), default="none",
                        help="Optional removal of known simulated depth, retrained per fold")
    parser.add_argument("--dry-run", action="store_true",
                        help="Validate 52 predictions and category splits; no files written")
    return parser.parse_args()


def category_from_base(base):
    parts = str(base).split("_", 2)
    if len(parts) != 3 or not parts[0].startswith("B") or parts[1] not in CATEGORIES:
        raise ValueError("Unknown base/category format: " + str(base))
    return parts[1]


def build_plan(views, args):
    rows = []
    for scenario, folder in views:
        base = cross.legacy.base_from_scenario(scenario)
        category = category_from_base(base)
        truth = cross.legacy.read_indexed(folder / "pseudo_spot_ground_truth.csv")
        prediction_path = cross.prediction_path(
            folder, scenario, args.method, args.prediction_template
        )
        cross.validate_prediction(prediction_path, truth)
        rows.append({
            "scenario_id": scenario,
            "held_out_base": base,
            "category": category,
            "view_dir": str(folder),
            "prediction_file": str(prediction_path),
        })
    if len(rows) != 52 or len({r["scenario_id"] for r in rows}) != 52:
        raise ValueError("Expected 52 distinct scenario IDs")
    base_counter = Counter(r["held_out_base"] for r in rows)
    category_base_counter = Counter(
        category_from_base(base) for base in base_counter
    )
    category_view_counter = Counter(r["category"] for r in rows)
    if len(base_counter) != 13 or set(base_counter.values()) != {4}:
        raise ValueError("Expected exactly 13 bases, each with four depths")
    if dict(category_base_counter) != EXPECTED_BASES:
        raise ValueError(
            "Base group distribution mismatch: " + str(dict(category_base_counter)))
    if dict(category_view_counter) != EXPECTED_VIEWS:
        raise ValueError(
            "View category distribution mismatch: " + str(dict(category_view_counter)))
    for category in CATEGORIES:
        train_bases = {
            r["held_out_base"] for r in rows if r["category"] != category
        }
        test_bases = {
            r["held_out_base"] for r in rows if r["category"] == category
        }
        if not train_bases or not test_bases or train_bases & test_bases:
            raise ValueError("Training/test base overlap: " + category)
        print(
            "FOLD", category,
            "train_views", 52 - EXPECTED_VIEWS[category],
            "test_views", EXPECTED_VIEWS[category],
            "test_bases", len(test_bases),
            flush=True,
        )
    return rows


def main():
    args = parse_args()
    views = cross.read_views(args.suite_root)
    plan = build_plan(views, args)
    print("INPUT CHECK PASS:", args.method, "52 scenario views / 13 bases")
    print("SPLIT CHECK PASS: four disjoint held-out categories")
    print("ABLATION:", args.ablation)
    if args.dry_run:
        print("DRY RUN PASS — no files written")
        return

    root = (args.out_dir or
            args.suite_root / "batch_runs" / "CARRliteV2_category_holdout")
    output = root / args.method
    if args.ablation != "none":
        output = output / args.ablation
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(
            "Output directory not empty (refusing overwrite): " + str(output))
    excluded = cross.ABLATION_COLUMNS[args.ablation]
    datasets = []
    for idx, (scenario, folder) in enumerate(views, 1):
        pred_path = cross.prediction_path(
            folder, scenario, args.method, args.prediction_template)
        d = cross.make_dataset(
            folder, scenario, pred_path, args.confusion_k, args.marker_k)
        if excluded:
            missing = set(excluded) - set(d["features"].columns)
            if missing:
                raise ValueError("Missing ablation columns: " + str(sorted(missing)))
            d["features"] = d["features"].drop(columns=list(excluded))
        d["category"] = category_from_base(d["base"])
        datasets.append(d)
        print("Loaded", idx, "/", len(views), scenario, flush=True)

    if len(datasets) != 52 or {
            d["scenario_id"] for d in datasets} != {
            p["scenario_id"] for p in plan}:
        raise ValueError("Dataset/manifest mismatch before training")
    output.mkdir(parents=True, exist_ok=True)
    metrics = []
    split_manifest = []
    for fold, held_out in enumerate(CATEGORIES, 1):
        train = [d for d in datasets if d["category"] != held_out]
        test = [d for d in datasets if d["category"] == held_out]
        if len(test) != EXPECTED_VIEWS[held_out]:
            raise ValueError("Unexpected held-out view count: " + held_out)
        train_bases = {d["base"] for d in train}
        test_bases = {d["base"] for d in test}
        if train_bases & test_bases:
            raise ValueError("Category hold-out leaked base groups")
        print("TRAINING FOLD", fold, held_out, "train", len(train),
              "test", len(test), flush=True)
        models = cross.legacy.train_fold(train, args.seed + fold)
        for d in test:
            outputs = {"Original_" + args.method: d["prediction"]}
            outputs.update(cross.apply_models(d, models))
            dest = output / d["scenario_id"]
            dest.mkdir(parents=True, exist_ok=False)
            split_manifest.append({
                "scenario_id": d["scenario_id"],
                "held_out_base": d["base"],
                "held_out_category": held_out,
                "fold": fold,
                "train_view_count": len(train),
                "test_view_count": len(test),
            })
            for label, frame in outputs.items():
                frame.to_csv(dest / (label + ".csv"))
                metric_seed = args.seed + 100 * fold + int(d["depth"])
                metric = cross.v1.evaluate(d, frame, label, metric_seed)
                metric.update({
                    "scenario_id": d["scenario_id"],
                    "base_method": args.method,
                    "held_out_base": d["base"],
                    "held_out_category": held_out,
                    "fold": fold,
                    "split_mode": "category_holdout",
                    "ablation": args.ablation,
                })
                metrics.append(metric)
            print("Completed", d["scenario_id"], flush=True)
        pd.DataFrame(metrics).to_csv(output / "metrics_by_scenario.csv", index=False)
    if len(metrics) != 260 or len(split_manifest) != 52:
        raise ValueError("Unexpected final output count")
    pd.DataFrame(split_manifest).to_csv(output / "split_manifest.csv", index=False)
    config = {
        "status": "exploratory",
        "split_mode": "leave_one_category_out",
        "categories": list(CATEGORIES),
        "expected_base_counts": EXPECTED_BASES,
        "expected_view_counts": EXPECTED_VIEWS,
        "base_method": args.method,
        "seed": args.seed,
        "scenario_count": 52,
        "fold_count": 4,
        "ablation": args.ablation,
        "excluded_feature_columns": list(excluded),
        "confusion_k": args.confusion_k,
        "marker_k": args.marker_k,
        "prediction_template": args.prediction_template,
        "source_inputs": plan,
        "notes": [
            "Same data, model and evaluation functions as cross_method_carr_v2.py",
            "Entire scenario categories and all depth variants are held out",
            "Calibration model retrained separately per base method and fold",
            "Known-depth feature valid only for the simulated-depth protocol",
            "Category holdout reduces related-scenario exposure but does not"
            " establish independent external dataset validity",
            "No test scenario targets are used by train_fold to fit the models",
        ],
    }
    (output / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FINISHED", len(metrics), "result rows")
    print("OUTPUT", output)


if __name__ == "__main__":
    main()
