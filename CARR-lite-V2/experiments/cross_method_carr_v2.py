#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Apply the existing CARR-lite V2 three-branch calibrator to RCTD/CARD outputs.

This is a new adapter; historical Tangram scripts remain unchanged.
Per base method, it retrains the calibrator on 12 base scenarios and holds out
all four depths of the 13th base. A distinct calibrator is trained for each
base method (not a zero-shot Tangram-to-RCTD transfer claim).
Writes only to --out-dir, never edits input predictions or source snapshots.

Examples:
  python cross_method_carr_v2.py --method RCTD --dry-run
  python cross_method_carr_v2.py --method CARD --dry-run
  python cross_method_carr_v2.py --method RCTD
"""
from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve()
LEGACY_DIR = HERE.parents[1] / "source-snapshot" / "CARR_lite_v2_52scenario"
sys.path.insert(0, str(LEGACY_DIR))

# Use the same definitions, model configurations and metric code as the
# source snapshot, rather than silently replacing the research method.
import carr_lite_tangram as v1
import carr_lite_tangram_v2 as v2
import carr_lite_v2_52scenario as legacy

DEFAULT_SUITE = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\rarecell_52scenario_suite")
METHODS = ("RCTD", "CARD", "SPOTlight", "Tangram")


def args_parser():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--suite-root", type=Path, default=DEFAULT_SUITE)
    ap.add_argument("--method", choices=METHODS, required=True)
    ap.add_argument("--prediction-template",
                    default="predictions/{method}_self_benchmark.csv",
                    help="Relative to each view_dir or absolute; fields: method, scenario_id")
    ap.add_argument("--out-dir", type=Path, default=None,
                    help="Default: SUITE_ROOT/batch_runs/CARRliteV2_cross_method")
    ap.add_argument("--seed", type=int, default=20260724)
    ap.add_argument("--confusion-k", type=int, default=3)
    ap.add_argument("--marker-k", type=int, default=40)
    ap.add_argument("--dry-run", action="store_true",
                    help="Check manifest and all prediction CSV alignments; write nothing")
    ap.add_argument("--force", action="store_true",
                    help="Explicitly allow replacing files in the output directory")
    return ap.parse_args()


def prediction_path(view_dir, scenario_id, method, template):
    rel = template.format(method=method, scenario_id=scenario_id)
    path = Path(rel)
    return path if path.is_absolute() else view_dir / path


def read_views(suite_root):
    manifest = suite_root / "scenario_views" / "scenario_view_manifest.csv"
    if not manifest.is_file():
        raise FileNotFoundError(manifest)
    with manifest.open(encoding="utf-8-sig", newline="") as f:
        entries = list(csv.DictReader(f))
    if len(entries) != 52:
        raise ValueError("Expected 52 scenario views; got " + str(len(entries)))
    views = []
    for row in entries:
        scenario = row["scenario_id"]
        folder = legacy.resolve_view_dir(suite_root, row)
        views.append((scenario, folder))
    return views


def validate_prediction(path, truth):
    if not path.is_file():
        raise FileNotFoundError(path)
    pred = legacy.read_indexed(path)
    if pred.index.has_duplicates or pred.columns.has_duplicates:
        raise ValueError("Duplicate row/column keys in " + str(path))
    if set(pred.index) != set(truth.index) or set(pred.columns) != set(truth.columns):
        raise ValueError("Prediction / truth spot or cell-type IDs disagree: " + str(path))
    vals = pred.loc[truth.index, truth.columns].to_numpy(dtype=float)
    if not np.isfinite(vals).all() or np.min(vals) < -1e-6:
        raise ValueError("Non-finite or negative prediction: " + str(path))
    if np.any(np.sum(np.maximum(vals, 0), axis=1) <= v1.EPS):
        raise ValueError("Empty prediction row: " + str(path))
    pred = pred.loc[truth.index, truth.columns].copy()
    pred.iloc[:, :] = v1.normalize_rows(pred.to_numpy(dtype=float))
    return pred


def make_dataset(view_dir, scenario_id, pred_path, confusion_k, marker_k):
    # Mirrors the original build_view_dataset; only the base prediction changes.
    truth = legacy.read_indexed(view_dir / "pseudo_spot_ground_truth.csv")
    metadata = legacy.read_indexed(view_dir / "spot_metadata.csv")
    expression = legacy.read_indexed(legacy.find_expression(view_dir))
    prediction = validate_prediction(pred_path, truth)
    expression = expression.loc[truth.index]
    metadata = metadata.loc[truth.index]

    profiles = v1.reference_profiles(view_dir, expression.columns, truth.columns)
    targets = metadata["target_cell_type"].astype(str).drop_duplicates().tolist()
    definitions, log_profiles = v1.build_type_definitions(
        profiles, targets, confusion_k, marker_k)
    observed_log = np.log1p(v1.normalize_rows(expression.to_numpy(dtype=float)) * 1e6)
    pred_arr = prediction.to_numpy(dtype=float)
    reconstructed_log = np.log1p(np.maximum(pred_arr @ profiles.to_numpy(), 0) * 1e6)
    rows, labels = [], []
    for i, spot_id in enumerate(truth.index):
        target = str(metadata.at[spot_id, "target_cell_type"])
        d = definitions[target]
        ti, ci, mi = d["target_index"], d["confusion_indices"], d["marker_indices"]
        base_target = pred_arr[i, ti]
        conf_values = pred_arr[i, ci]
        obs_marker = observed_log[i, mi].mean()
        target_marker_ref = log_profiles[ti, mi].mean()
        conf_marker_ref = log_profiles[ci][:, mi].mean()
        residual = observed_log[i] - reconstructed_log[i]
        rows.append({
            "base_target": base_target,
            "base_confusion_sum": conf_values.sum(),
            "base_target_minus_confmax": base_target - conf_values.max(),
            "base_target_share_local": base_target / max(base_target + conf_values.sum(), v1.EPS),
            "observed_marker_score": obs_marker,
            "observed_marker_margin": obs_marker - conf_marker_ref,
            "marker_fit_target": -abs(obs_marker - target_marker_ref),
            "residual_projection": float(
                residual @ d["contrast"] / max(np.linalg.norm(d["contrast"]), v1.EPS)),
            "residual_marker_mean": float(residual[mi].mean()),
            "library_size_log": float(np.log1p(expression.iloc[i].sum())),
            "reference_similarity_max": d["reference_similarity_max"],
            "depth_fraction": int(legacy.depth_from_scenario(scenario_id)) / 100.0,
        })
        labels.append(float(truth.iloc[i, ti] - base_target))
    return {
        "base": legacy.base_from_scenario(scenario_id),
        "depth": legacy.depth_from_scenario(scenario_id),
        "scenario_id": scenario_id,
        "view_dir": view_dir,
        "truth": truth,
        "metadata": metadata,
        "prediction": prediction,
        "features": pd.DataFrame(rows, index=truth.index),
        "labels": pd.Series(labels, index=truth.index, name="delta"),
        "definitions": definitions,
    }


def apply_models(dataset, trained):
    abundance, positive_model, classifier = trained
    x = dataset["features"].to_numpy()
    quantitative = v1.apply_local_correction(dataset, abundance.predict(x))
    q_target = np.array([
        quantitative.at[s, str(dataset["metadata"].at[s, "target_cell_type"])]
        for s in quantitative.index])
    positive = positive_model.predict(x)
    presence = classifier.predict_proba(x)[:, 1]
    outputs = {"AbundanceOnly": quantitative}
    for strength in (0.15, 0.30, 0.50):
        desired = v2.soft_presence_fusion(
            dataset, q_target, presence, positive, strength)
        outputs["HGBC_a%02d" % round(strength * 100)] = v2.set_local_target(
            dataset, desired)
    return outputs


def main():
    args = args_parser()
    views = read_views(args.suite_root)
    method = args.method
    out_root = args.out_dir or (
        args.suite_root / "batch_runs" / "CARRliteV2_cross_method")
    out_method = out_root / method
    base_files = []
    for scene, folder in views:
        truth = legacy.read_indexed(folder / "pseudo_spot_ground_truth.csv")
        path = prediction_path(folder, scene, method, args.prediction_template)
        validate_prediction(path, truth)
        base_files.append({"scenario_id": scene, "prediction_file": str(path)})
    print("INPUT CHECK PASS:", method, len(base_files), "scenario views")
    if args.dry_run:
        print("DRY RUN PASS — no files written")
        return

    if out_method.exists() and any(out_method.iterdir()) and not args.force:
        raise FileExistsError(
            "Output directory not empty: " + str(out_method) +
            " (use --force only if deliberate)")
    datasets = []
    for i, (scene, folder) in enumerate(views, 1):
        pred_path = prediction_path(folder, scene, method, args.prediction_template)
        datasets.append(make_dataset(
            folder, scene, pred_path, args.confusion_k, args.marker_k))
        print("Loaded", i, "/", len(views), scene, flush=True)

    bases = sorted({d["base"] for d in datasets})
    if len(bases) != 13:
        raise ValueError("Expected 13 biological base groups, got " + str(len(bases)))
    # Do not create any output until every input and grouping is validated.
    out_method.mkdir(parents=True, exist_ok=True)
    rows = []
    for fold, held_out in enumerate(bases, 1):
        train = [d for d in datasets if d["base"] != held_out]
        test = [d for d in datasets if d["base"] == held_out]
        models = legacy.train_fold(train, args.seed + fold)
        for d in test:
            outputs = {"Original_" + method: d["prediction"]}
            outputs.update(apply_models(d, models))
            dest = out_method / d["scenario_id"]
            dest.mkdir(parents=True, exist_ok=True)
            for label, frame in outputs.items():
                frame.to_csv(dest / (label + ".csv"))
                seed = args.seed + fold * 100 + int(d["depth"])
                metric = v1.evaluate(d, frame, label, seed)
                metric.update({"scenario_id": d["scenario_id"],
                               "base_method": method, "fold": fold})
                rows.append(metric)
            print("Completed", d["scenario_id"], flush=True)
        pd.DataFrame(rows).to_csv(out_method / "metrics_by_scenario.csv", index=False)

    config = {
        "status": "exploratory", "base_method": method, "seed": args.seed,
        "scenario_count": len(views), "base_group_count": len(bases),
        "confusion_k": args.confusion_k, "marker_k": args.marker_k,
        "prediction_template": args.prediction_template,
        "source_inputs": base_files,
        "notes": [
            "CARR retrained per method, not zero-shot cross-method transfer",
            "The 12th known-depth feature matches the original simulated protocol",
            "Source-cell independence and external validity not yet established",
        ],
    }
    (out_method / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    print("FINISHED", len(rows), "result rows")
    print("OUTPUT", out_method)


if __name__ == "__main__":
    main()
