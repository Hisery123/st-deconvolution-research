#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""CTW-RF: frozen-reference, multi-section DLPFC Visium APPLICATION.

Reads the existing reference_70 logcounts and 10x HDF5 DLPFC slides.
Derives three NNLS baselines using reference cells ONLY, constructs
reference-derived training pseudo-spots, fits CTW/stacking on those,
then applies the FROZEN methods and weights across every discovered
DLPFC slice (nominal 12). This is an external application rather than
a re-run of historical six baselines and is not a ground-truth accuracy
benchmark on actual Visium.

No test composition labels are used, inferred, or generated for Visium.
Layer-stratified predictions are descriptive, NOT cell-fraction truth.
All published results of older experiments are untouched.

Examples:
  python ctw_dlpfc_multislice_application_batch.py --dry-run
  python ctw_dlpfc_multislice_application_batch.py --run
  python ctw_dlpfc_multislice_application_batch.py --run --resume
"""
from __future__ import annotations

import argparse
import json
import re
import time
from pathlib import Path

import h5py
import numpy as np
import pandas as pd
from scipy.optimize import nnls
from scipy.sparse import csc_matrix

import global_stacking_cv as cv
import ctw_matched_fusion_comparisons_batch as ctw

DEFAULT_DATA = Path(r"D:\paper\ST_Benchmark_Planning\mvp\data")
DEFAULT_REF = Path(r"D:\Research\real_DLPFC\candidate_inputs")
DEFAULT_OUT = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_DLPFC_multislice_20261123_v1")
REF_EXPRESSION = "reference_70_expression_logcounts.csv"
REF_LABELS = "reference_70_labels.csv"
METHODS = ("NNLS_all", "NNLS_top300", "NNLS_marker20")
FUSIONS = ("EqualWeight", "GlobalStacking", "CTW_HardSelect", "CTW_InvRMSE_p2", "CTW_SoftOpt")
ALL_METHODS = METHODS + FUSIONS
TARGET_IDS = ("151507", "151508", "151509", "151510", "151669", "151670",
              "151671", "151672", "151673", "151674", "151675", "151676")


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--data-root", type=Path, default=DEFAULT_DATA)
    p.add_argument("--reference-root", type=Path, default=DEFAULT_REF)
    p.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    p.add_argument("--seed", type=int, default=20261123)
    p.add_argument("--train-spots", type=int, default=600)
    p.add_argument("--synthetic-test-spots", type=int, default=200)
    p.add_argument("--cells-per-spot", type=int, default=8)
    return p.parse_args()


def label_column(labels):
    keys = ("label", "cell_type", "celltype", "annotation_1",
            "annotation", "type", "cluster", "celltype_major")
    col = next((s for s in keys if s in labels.columns), None)
    if col is None and labels.shape[1] == 1:
        col = labels.columns[0]
    if col is None:
        raise ValueError("No cell type label column; found " + str(labels.columns.tolist()))
    return col


def load_reference(root):
    labels = pd.read_csv(root / REF_LABELS, index_col=0)
    expression = pd.read_csv(root / REF_EXPRESSION, index_col=0)
    labels.index = labels.index.astype(str)
    expression.index = expression.index.astype(str)
    expression.columns = expression.columns.astype(str)
    if labels.index.has_duplicates or expression.index.has_duplicates:
        raise ValueError("Reference IDs are duplicated")
    # Handle either cell x gene or gene x cell references without trusting filenames.
    forward = len(expression.index.intersection(labels.index))
    backward = len(expression.columns.intersection(labels.index))
    if backward > forward:
        expression = expression.T
    common = labels.index.intersection(expression.index)
    if len(common) < 40:
        raise ValueError("Reference cell/label IDs do not match, common=" + str(len(common)))
    types = labels.loc[common, label_column(labels)].astype(str)
    if types.isna().any() or types.eq("nan").any():
        raise ValueError("Missing reference cell types")
    expression = expression.loc[common]
    if expression.columns.has_duplicates:
        raise ValueError("Duplicate reference gene names")
    expression = expression.apply(pd.to_numeric, errors="raise").astype(np.float32)
    arr = expression.to_numpy()
    if not np.isfinite(arr).all() or (arr < 0).any():
        raise ValueError("Invalid/negative reference expression")
    if types.nunique() < 3:
        raise ValueError("Insufficient reference cell types")
    return expression, types


def discover_slides(root):
    slides = []
    for sid in TARGET_IDS:
        path = root / sid / "filtered_feature_bc_matrix.h5"
        if path.is_file():
            slides.append((sid, path))
    if not slides:
        raise FileNotFoundError("No DLPFC 10x .h5 files under " + str(root))
    return slides


def decode_strings(a):
    return [v.decode("utf-8") if isinstance(v, bytes) else str(v) for v in a]


def h5_header(path):
    with h5py.File(path, "r") as h:
        if "matrix" not in h:
            raise ValueError("Missing 10x HDF5 matrix group: " + str(path))
        m = h["matrix"]
        gene_key = "name" if "name" in m["features"] else "id"
        genes = decode_strings(m["features"][gene_key][:])
        barcodes = decode_strings(m["barcodes"][:])
        dims = tuple(int(v) for v in m["shape"][:])
        if dims != (len(genes), len(barcodes)):
            raise ValueError("10x shape not (genes, spots): " + str(path))
        if len(set(barcodes)) != len(barcodes):
            raise ValueError("Duplicate spot barcodes in " + str(path))
    return genes, barcodes


def read_selected_h5(path, shared_genes):
    with h5py.File(path, "r") as h:
        m = h["matrix"]
        gene_key = "name" if "name" in m["features"] else "id"
        genes = decode_strings(m["features"][gene_key][:])
        barcodes = decode_strings(m["barcodes"][:])
        idx = {g: i for i, g in enumerate(genes)}
        missing = [g for g in shared_genes if g not in idx]
        if missing:
            raise ValueError(path.parent.name + ": missing panel genes: " + str(missing[:8]))
        mat = csc_matrix(
            (m["data"][:], m["indices"][:], m["indptr"][:]),
            shape=tuple(int(x) for x in m["shape"][:]))
        selected = np.asarray([idx[g] for g in shared_genes], dtype=int)
        arr = mat[selected, :].T.toarray().astype(np.float64)
    if not np.isfinite(arr).all() or (arr < 0).any():
        raise ValueError("Nonfinite or negative spot expression: " + str(path))
    totals = arr.sum(axis=1)
    if np.any(totals <= 0):
        raise ValueError("Zero shared-gene total for " + str(np.count_nonzero(totals <= 0)) +
                         " spots in " + str(path))
    return pd.DataFrame(arr, index=barcodes, columns=shared_genes)


def split_reference(labels, seed):
    rng = np.random.default_rng(seed)
    split = {"reference": [], "train_donor": [], "check_donor": []}
    counts = []
    for ct in sorted(labels.unique()):
        ids = rng.permutation(labels[labels.eq(ct)].index.to_numpy())
        n = len(ids)
        if n == 1:
            nr, nt = 1, 0
        elif n == 2:
            nr, nt = 1, 1
        else:
            nr = min(n - 2, max(1, round(n * .50)))
            nt = min(n - nr - 1, max(1, round(n * .30)))
        parts = (list(ids[:nr]), list(ids[nr:nr + nt]),
                 list(ids[nr + nt:]))
        for k, part in zip(split, parts):
            split[k].extend(part)
        counts.append({"cell_type": ct, "n_total": n, "n_reference": len(parts[0]),
                       "n_train_donor": len(parts[1]), "n_check_donor": len(parts[2])})
    a, b, c = (set(split[k]) for k in split)
    if a & b or a & c or b & c:
        raise AssertionError("Reference/train/check cell ID overlap")
    if len(b) < 20 or len(c) < 20:
        raise ValueError("Too few separated calibration/check donors")
    return split, pd.DataFrame(counts)


def compositional(x, label):
    x = np.asarray(x, dtype=np.float64)
    if not np.isfinite(x).all() or np.any(x < 0):
        raise ValueError("Invalid expression: " + label)
    sums = x.sum(axis=1)
    if np.any(sums <= 0):
        raise ValueError("Zero expression row: " + label)
    return x / sums[:, None]


def make_spots(expression, labels, donors, classes, n_spots, cells_per, seed):
    rng = np.random.default_rng(seed)
    donor = expression.loc[donors]
    genes = expression.columns
    values = compositional(donor.to_numpy(), "donors")
    typ = labels.loc[donors].to_numpy()
    idx = pd.Index(classes).get_indexer(typ)
    out = np.zeros((n_spots, len(genes)), dtype=np.float64)
    truth = np.zeros((n_spots, len(classes)), dtype=np.float64)
    for i in range(n_spots):
        chosen = rng.integers(len(donor), size=cells_per)
        out[i] = values[chosen].sum(axis=0)
        truth[i] = np.bincount(idx[chosen], minlength=len(classes)) / cells_per
    names = [f"SYN{i:05d}" for i in range(n_spots)]
    return pd.DataFrame(compositional(out, "pseudo-spots"),
                        index=names, columns=genes), pd.DataFrame(
                            truth, index=names, columns=classes)


def build_profiles(reference, labels, classes):
    norm = compositional(reference.to_numpy(), "reference")
    label_values = labels.loc[reference.index].to_numpy()
    return np.vstack([norm[label_values == ct].mean(axis=0) for ct in classes])


def select_features(profiles, reference, classes):
    abundance = reference.to_numpy(dtype=float).sum(axis=0)
    top = np.argsort(-abundance, kind="stable")[:min(300, len(abundance))]
    markers = set()
    for i in range(len(classes)):
        other = np.delete(profiles, i, axis=0).mean(axis=0)
        score = np.log(profiles[i] + 1e-9) - np.log(other + 1e-9)
        score[profiles[i] <= 0] = -np.inf
        for j in np.argsort(-score, kind="stable")[:20]:
            if np.isfinite(score[j]):
                markers.add(int(j))
    if len(markers) < 8:
        raise ValueError("Too few reference-only markers for NNLS")
    return {"NNLS_all": np.arange(reference.shape[1]),
            "NNLS_top300": np.asarray(top, dtype=int),
            "NNLS_marker20": np.asarray(sorted(markers), dtype=int)}


def nnls_predict(observed, profiles, features, classes, return_diagnostics=False):
    """All-gene NNLS is the fixed fallback when a restricted panel has zero support.

    A spot with no signal in the marker panel must not halt a whole slice.
    The fallback is deterministic, reference-only, and its usage is reported.
    It is NOT interpreted as a successful marker-panel estimate.
    """
    X = compositional(observed.to_numpy(dtype=float), "observed")
    if "NNLS_all" not in features or list(features)[0] != "NNLS_all":
        raise ValueError("NNLS_all must be the first baseline for transparent fallback")
    outputs = {}
    issues = []
    for method, selected in features.items():
        if len(selected) == 0:
            raise ValueError("Empty gene selection: " + method)
        design = np.asarray(profiles[:, selected].T, dtype=np.float64)
        response = X[:, selected]
        pred = np.zeros((len(observed), len(classes)), dtype=np.float64)
        for i in range(len(observed)):
            w, _ = nnls(design, response[i])
            total = float(w.sum())
            if not np.isfinite(total):
                raise ValueError("Nonfinite NNLS output: " + method +
                                 ", spot " + str(observed.index[i]))
            if total <= 0:
                if method == "NNLS_all":
                    raise ValueError("Full-gene NNLS zero solution for " +
                                     str(observed.index[i]) +
                                     "; no defensible fallback available")
                # Keep the input spot, but report that its restricted panel
                # had insufficient support and the all-gene solution was used.
                fallback = outputs["NNLS_all"].iloc[i].to_numpy(dtype=float)
                if not np.isfinite(fallback).all() or fallback.sum() <= 0:
                    raise ValueError("Invalid all-gene fallback for " +
                                     str(observed.index[i]))
                pred[i] = fallback
                issues.append({
                    "spot_id": str(observed.index[i]),
                    "method": method,
                    "fallback_method": "NNLS_all",
                    "reason": ("zero_selected_gene_signal"
                               if float(response[i].sum()) <= 1e-15
                               else "nnls_zero_despite_selected_signal"),
                    "selected_gene_signal_fraction": float(response[i].sum()),
                })
            else:
                pred[i] = w / total
        outputs[method] = pd.DataFrame(pred, index=observed.index, columns=classes)
    diag = pd.DataFrame(issues, columns=[
        "spot_id", "method", "fallback_method", "reason",
        "selected_gene_signal_fraction"])
    if len(diag):
        print("NNLS PANEL FALLBACK", {k: int(v) for k, v in
              diag.groupby("method").size().items()},
              "of", len(observed), "spots (full-gene estimate substituted)",
              flush=True)
    if return_diagnostics:
        return outputs, diag
    return outputs


def train_fusion(source, targets):
    y = targets.to_numpy(dtype=float)
    preds = np.stack([source[m].to_numpy(dtype=float) for m in METHODS])
    fold = np.arange(len(targets))
    weights = {
        "GlobalStacking": cv.fit_global_weights(preds, y),
        "CTW_HardSelect": ctw.hardselect_weights(preds, y, fold),
        "CTW_InvRMSE_p2": ctw.invrmse_weights(preds, y, fold),
    }
    weights["CTW_SoftOpt"], fallback = ctw.softopt_weights(preds, y, fold)
    return weights, fallback


def apply_fusion(baselines, weights, classes):
    preds = np.stack([baselines[m].to_numpy(dtype=float) for m in METHODS])
    results = {key: baselines[key] for key in METHODS}
    results["EqualWeight"] = pd.DataFrame(
        cv.normalize(preds.mean(axis=0), "EqualWeight"),
        index=baselines[METHODS[0]].index, columns=classes)
    results["GlobalStacking"] = pd.DataFrame(
        cv.normalize(cv.fuse(preds, weights["GlobalStacking"]), "GlobalStacking"),
        index=baselines[METHODS[0]].index, columns=classes)
    for method in ("CTW_HardSelect", "CTW_InvRMSE_p2", "CTW_SoftOpt"):
        vals = ctw.fuse_cellwise(preds, weights[method], method)
        results[method] = pd.DataFrame(vals, index=baselines[METHODS[0]].index,
                                       columns=classes)
    return results


def canonical_layer(value):
    s = str(value).strip().lower().replace("_", " ").replace("-", " ")
    if not s or s in ("nan", "none", "unknown", "na", "undetermined"):
        return None
    if s in ("wm", "white matter", "white matter (wm)"):
        return "WM"
    if re.search(r"\bwhite\s+matter\b", s):
        return "WM"
    m = re.fullmatch(r"(?:layer\s*)?l?\s*([1-6])(?:\.0)?", s)
    if m:
        return "L" + m.group(1)
    return None


def layer_assignments(slide_dir, spot_ids):
    spot_index = pd.Index(spot_ids).astype(str)
    best = None
    for filename in ("manual_layer_annotations.csv", "spots_aligned.csv"):
        path = slide_dir / filename
        if not path.is_file():
            continue
        tab = pd.read_csv(path)
        if tab.empty:
            continue
        # Select a barcode column by actual overlap, not an assumed CSV schema.
        score = [(len(spot_index.intersection(tab[col].astype(str))), col)
                 for col in tab.columns]
        overlap, barcode_col = max(score, key=lambda x: x[0])
        if overlap == 0:
            continue
        # Prefer actual layer/annotation columns; never interpret in_tissue flags.
        candidates = [c for c in tab.columns if c != barcode_col and
                      re.search(r"layer|annotation", c, flags=re.IGNORECASE)]
        if not candidates:
            continue
        for col in candidates:
            normalized = tab[col].map(canonical_layer)
            valid = int(normalized.notna().sum())
            if not valid:
                continue
            tmp = pd.Series(normalized.to_numpy(),
                            index=tab[barcode_col].astype(str)).groupby(level=0).first()
            matched = tmp.reindex(spot_index)
            n_matched = int(matched.notna().sum())
            if best is None or n_matched > best[0]:
                best = (n_matched, matched, filename, col)
    if best is None:
        return pd.Series(index=spot_index, dtype="object"), "NO_LAYER_LABELS"
    return best[1], best[2] + ":" + str(best[3])


def summarize_slice(sid, results, layers, layer_source, classes):
    records = []
    for method, pred in results.items():
        for ct in classes:
            records.append({"slide": sid, "method": method, "cell_type": ct,
                            "mean_predicted_fraction": float(pred[ct].mean()),
                            "n_spots": len(pred)})
    labeled = layers.dropna()
    layer_mean = []
    for method, pred in results.items():
        for layer, ids in labeled.groupby(labeled):
            sub = pred.loc[ids.index]
            for ct in classes:
                layer_mean.append({"slide": sid, "method": method, "layer": layer,
                                   "cell_type": ct, "n_spots": len(sub),
                                   "mean_predicted_fraction": float(sub[ct].mean())})
    summary = {"slide": sid, "n_spots": len(layers),
               "n_labeled_spots": len(labeled),
               "layer_source": layer_source, "n_cell_types": len(classes)}
    oligo_types = [c for c in classes
                   if re.search(r"oligo", c, re.IGNORECASE) and
                   not re.search(r"opc|precursor", c, re.IGNORECASE)]
    if len(oligo_types) == 1:
        ct = oligo_types[0]
        pred = results["CTW_SoftOpt"][ct]
        wm_ids = labeled[labeled.eq("WM")].index
        gray_ids = labeled[labeled.ne("WM")].index
        if len(wm_ids) and len(gray_ids):
            summary["oligo_WM_minus_cortex"] = float(
                pred.loc[wm_ids].mean() - pred.loc[gray_ids].mean())
            summary["oligo_class"] = ct
    return pd.DataFrame(records), pd.DataFrame(layer_mean), summary


def preflight(args):
    slides = discover_slides(args.data_root)
    expr, types = load_reference(args.reference_root)
    all_genes = set(expr.columns)
    headers = {}
    for sid, path in slides:
        genes, spots = h5_header(path)
        common = all_genes.intersection(genes)
        all_genes.intersection_update(genes)
        headers[sid] = {"n_spots": len(spots), "n_h5_genes": len(genes),
                        "n_ref_common_genes": len(common)}
    panel = [g for g in expr.columns if g in all_genes]
    if len(panel) < 100:
        raise ValueError("Insufficient shared reference/H5 genes: " + str(len(panel)))
    expr = expr.loc[:, panel]
    split, split_table = split_reference(types, args.seed)
    for sid in headers:
        p = args.data_root / sid
        _, spots = h5_header(p / "filtered_feature_bc_matrix.h5")
        layer, source = layer_assignments(p, spots)
        headers[sid]["layer_labeled"] = int(layer.notna().sum())
        headers[sid]["layer_source"] = source
    print("PREFLIGHT reference_cells", len(expr), "cell_types", types.nunique(),
          "shared_genes_all_slides", len(panel), "slides_found", len(slides),
          "expected", len(TARGET_IDS), flush=True)
    print("CELL SPLIT", {k: len(v) for k, v in split.items()}, flush=True)
    for sid, item in headers.items():
        print("SLIDE", sid, item, flush=True)
    return slides, expr, types, split, split_table, panel, headers


def main():
    args = arguments()
    if args.train_spots < 100 or args.synthetic_test_spots < 50 or args.cells_per_spot < 2:
        raise ValueError("Invalid calibration budget")
    if args.resume and args.dry_run and not args.out_dir.exists():
        raise FileNotFoundError("No output to resume")
    slides, expr, types, split, split_table, panel, headers = preflight(args)
    conf = {"reference_root": str(args.reference_root.resolve()),
            "data_root": str(args.data_root.resolve()),
            "seed": args.seed, "train_spots": args.train_spots,
            "synthetic_test_spots": args.synthetic_test_spots,
            "cells_per_spot": args.cells_per_spot,
            "slides": [sid for sid, _ in slides],
            "panel": panel, "methods": list(METHODS),
            "role": "DLPFC real Visium application, no true cell-type proportions"}
    config_file = args.out_dir / "run_config.json"
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        if not args.resume or not config_file.is_file():
            raise FileExistsError("Existing output; use --run --resume for same config")
        if json.loads(config_file.read_text(encoding="utf-8")) != conf:
            raise ValueError("Resume config mismatch")
    if args.dry_run:
        ref = expr.loc[split["reference"]]
        cls = sorted(types.unique())
        prof = build_profiles(ref, types.loc[ref.index], cls)
        features = select_features(prof, ref, cls)
        sx, sy = make_spots(expr, types, split["train_donor"],
                            cls, 4, args.cells_per_spot, args.seed)
        out = nnls_predict(sx, prof, features, cls)
        # Force one spot to contain no marker-panel signal to test the
        # all-gene fallback without reading or writing any Visium output.
        restricted = set(int(x) for x in features["NNLS_marker20"])
        candidate = next((j for j in range(prof.shape[1])
                          if j not in restricted and float(prof[:, j].sum()) > 0),
                         None)
        if candidate is None:
            raise ValueError("Cannot construct a silent-marker fallback smoke test")
        blind = pd.DataFrame(np.zeros((1, len(prof[0]))),
                             index=["SMOKE_MARKER_ZERO"], columns=sx.columns)
        blind.iloc[0, candidate] = 1.0
        _, diagnostic = nnls_predict(blind, prof, features, cls,
                                     return_diagnostics=True)
        if "NNLS_marker20" not in diagnostic.method.tolist():
            raise AssertionError("Marker-silent spot must trigger fallback")
        print("FALLBACK SMOKE PASS", len(diagnostic), "fallback rows", flush=True)
        print("SMOKE PASS 4 synthetic spots", len(out), "NNLS methods;",
              "feature_counts", {k:len(v) for k,v in features.items()}, flush=True)
        print("DRY RUN PASS — no files written", flush=True)
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not config_file.exists():
        config_file.write_text(json.dumps(conf, ensure_ascii=False, indent=2),
                               encoding="utf-8")
    (args.out_dir / "source_split_by_type.csv").write_text(
        split_table.to_csv(index=False), encoding="utf-8")
    classes = sorted(types.unique())
    reference = expr.loc[split["reference"]]
    profiles = build_profiles(reference, types.loc[reference.index], classes)
    features = select_features(profiles, reference, classes)
    train_x, train_y = make_spots(expr, types, split["train_donor"], classes,
                                  args.train_spots, args.cells_per_spot, args.seed + 11)
    test_x, test_y = make_spots(expr, types, split["check_donor"], classes,
                                args.synthetic_test_spots, args.cells_per_spot, args.seed + 23)
    train_pred = nnls_predict(train_x, profiles, features, classes)
    weights, fallbacks = train_fusion(train_pred, train_y)
    check_pred = apply_fusion(nnls_predict(test_x, profiles, features, classes),
                              weights, classes)
    calib_rows = [{"method": method, **cv.metric_dict(
                   test_y.to_numpy(), p.to_numpy())}
                  for method, p in check_pred.items()]
    pd.DataFrame(calib_rows).to_csv(
        args.out_dir / "synthetic_donor_holdout_metrics.csv", index=False)
    print("CALIBRATION synthetics checked; SoftOpt fallback", fallbacks,
          "metrics not a real Visium ground-truth test", flush=True)
    pd.DataFrame(
        [{"fusion": k, "base_method": METHODS[i],
          "cell_type": "ALL" if np.ndim(w) == 1 else ct,
          "weight": float(w[i] if np.ndim(w) == 1 else w[i, ci])}
         for k, w in weights.items()
         for i in range(len(METHODS))
         for ci, ct in enumerate(["ALL"] if np.ndim(w) == 1 else classes)]
    ).to_csv(args.out_dir / "frozen_fusion_weights.csv", index=False)
    summary = []
    means = []
    layers_all = []
    for sid, h5 in slides:
        target_dir = args.out_dir / sid
        record = target_dir / "slide_summary.json"
        if record.is_file():
            info = json.loads(record.read_text(encoding="utf-8"))
            means_file = target_dir / "celltype_means.csv"
            layers_file = target_dir / "layer_celltype_means.csv"
            if not means_file.is_file() or not layers_file.is_file():
                raise ValueError("Partial completed slide: " + sid)
            summary.append(info)
            means.append(pd.read_csv(means_file))
            layers_all.append(pd.read_csv(layers_file))
            print("REUSE COMPLETED SLIDE", sid, flush=True)
            continue
        print("START SLIDE", sid, flush=True)
        start = time.perf_counter()
        target_dir.mkdir(exist_ok=True, parents=True)
        observed = read_selected_h5(h5, panel)
        layer, source = layer_assignments(h5.parent, observed.index)
        base, nnls_issues = nnls_predict(
            observed, profiles, features, classes, return_diagnostics=True)
        results = apply_fusion(base, weights, classes)
        for method, pred in results.items():
            pred.to_csv(target_dir / (method + "_prediction.csv"))
        layer.rename("manual_layer").to_csv(target_dir / "matched_layers.csv")
        one_means, one_layers, info = summarize_slice(
            sid, results, layer, source, classes)
        info["run_seconds"] = round(time.perf_counter() - start, 3)
        info["nnls_panel_fallback_count"] = int(len(nnls_issues))
        info["nnls_marker20_fallback_count"] = int(
            (nnls_issues["method"] == "NNLS_marker20").sum())
        info["nnls_top300_fallback_count"] = int(
            (nnls_issues["method"] == "NNLS_top300").sum())
        nnls_issues.to_csv(target_dir / "nnls_panel_fallback_spots.csv",
                           index=False)
        one_means.to_csv(target_dir / "celltype_means.csv", index=False)
        one_layers.to_csv(target_dir / "layer_celltype_means.csv", index=False)
        record.write_text(json.dumps(info, ensure_ascii=False, indent=2),
                          encoding="utf-8")
        summary.append(info)
        means.append(one_means)
        layers_all.append(one_layers)
        print("COMPLETED SLIDE", sid, "spots", len(observed),
              "labeled", info["n_labeled_spots"],
              "marker_fallback", info["nnls_marker20_fallback_count"],
              "top300_fallback", info["nnls_top300_fallback_count"],
              "seconds", info["run_seconds"], flush=True)
    pd.DataFrame(summary).to_csv(args.out_dir / "slide_coverage_summary.csv", index=False)
    pd.concat(means, ignore_index=True).to_csv(
        args.out_dir / "all_slide_celltype_means.csv", index=False)
    pd.concat(layers_all, ignore_index=True).to_csv(
        args.out_dir / "all_slide_layer_celltype_means.csv", index=False)
    print("BATCH FINISHED", len(slides), "DLPFC slices;",
          len(slides) * len(ALL_METHODS), "slice-method prediction matrices")
    print("OUTPUT", args.out_dir)


if __name__ == "__main__":
    main()
