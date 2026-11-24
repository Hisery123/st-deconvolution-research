#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Prepare *real spatial* MERFISH section holdouts for existing CARR runner.

Input is Squidpy's Moffitt-2018 preprocessed AnnData (73,655 x 161).
One Animal_ID, 12 Bregma sections. Therefore: new source and technology,
but NOT an independent-mouse validation.

Target truth = proportions of author's confident cell-class annotations
among identified cells in fixed xy grid bins from original physical cells.
Pseudo-spot expression = SUM of the available PREPROCESSED per-cell X
values. These are not claimed to be raw molecular RNA counts.

All parameters/splits/geometric binning are frozen before any model fit.
No test class labels are used to choose holdout sections, bin width, class
selection or tune thresholds. The 'Ambiguous' class is excluded as unknown;
derived truth is CONDITIONAL on confidently annotated cells. Its coverage
is measured and reported.

Creates five held_out_FOV{0..4} folders in the input contract of:
  CARR-lite-V2/experiments/carr_reference_only_seqfishplus_batch.py

--dry-run does no writes, checks heldout bin feasibility.
--prepare writes inputs once, refusing existing nonempty destination.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import sparse

ROOT = Path(r"D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018")
H5AD = "moffitt_merfish_squidpy_preprocessed.h5ad"
OUT = ROOT / "carr_sections_v1"
# Zero-based sorted Bregma indices, chosen by spatial position ONLY, not labels.
HOLDOUT_INDICES = (0, 3, 5, 8, 11)
MAX_REFERENCE_PER_CLASS = 120
MIN_CELLS_BIN = 5
MAX_CELLS_BIN = 24
MAX_TEST_BINS = 350
TARGET_CELLS_PER_BIN = 10
SEED = 20261124
EXCLUDED_LABELS = frozenset(("Ambiguous", "nan", "None", "", "NA"))


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    m = p.add_mutually_exclusive_group(required=True)
    m.add_argument("--dry-run", action="store_true")
    m.add_argument("--prepare", action="store_true")
    p.add_argument("--source", type=Path, default=ROOT / H5AD)
    p.add_argument("--out-dir", type=Path, default=OUT)
    return p.parse_args()


def get_values(data, cell_idx):
    arr = data.X[cell_idx, :]
    arr = arr.toarray() if sparse.issparse(arr) else np.asarray(arr)
    return np.asarray(arr, dtype=np.float32)


def read_source(path):
    import anndata
    if not path.is_file():
        raise FileNotFoundError(str(path))
    a = anndata.read_h5ad(path)
    expected = ("Animal_ID", "Bregma", "Centroid_X",
                "Centroid_Y", "Cell_class")
    missing = [k for k in expected if k not in a.obs.columns]
    if missing:
        raise ValueError("Missing MERFISH metadata: " + repr(missing))
    if a.n_obs != 73655 or a.n_vars != 161:
        raise ValueError("Unexpected preprocessed Moffitt subset dimensions")
    if not a.var_names.is_unique or not a.obs_names.is_unique:
        raise ValueError("Duplicate source cell/gene names")
    if a.obs["Animal_ID"].astype(str).nunique() != 1:
        raise ValueError("This locked protocol is specific to one-animal Moffitt subset")
    obs = a.obs.copy()
    obs["_section"] = pd.to_numeric(obs["Bregma"], errors="coerce")
    obs["_x"] = pd.to_numeric(obs["Centroid_X"], errors="coerce")
    obs["_y"] = pd.to_numeric(obs["Centroid_Y"], errors="coerce")
    obs["_type"] = obs["Cell_class"].astype(str)
    if not np.isfinite(obs[["_section", "_x", "_y"]].to_numpy()).all():
        raise ValueError("Nonfinite section/x/y coordinates")
    sections = sorted(obs["_section"].unique())
    if len(sections) != 12:
        raise ValueError("Expected 12 sections, found " + str(len(sections)))
    # Note: original source may be volume-normalized or log transformed.
    # No raw molecule count assertions based on X dtype or values.
    rng = np.random.default_rng(SEED)
    idx = rng.choice(a.n_obs, size=min(1500, a.n_obs), replace=False)
    sample = get_values(a, idx)
    if not np.isfinite(sample).all() or np.any(sample < 0):
        raise ValueError("Preprocessed X has negative/nonfinite values; this protocol cannot use it")
    if np.count_nonzero(sample) == 0:
        raise ValueError("Expression sample all zero")
    return a, obs, sections, {
        "sample_min": float(sample.min()),
        "sample_max": float(sample.max()),
        "sample_noninteger_positive_fraction": float(np.mean(
            (sample > 0) & (np.abs(sample - np.rint(sample)) > 1e-6))),
        "n_animals": 1,
        "n_sections": len(sections),
        "n_classes_including_ambiguous": int(obs["_type"].nunique()),
        "n_ambiguous": int(obs["_type"].isin(EXCLUDED_LABELS).sum()),
    }


def fixed_bins_for_fold(obs, sections, test_section):
    train = obs["_section"].ne(test_section)
    known = ~obs["_type"].isin(EXCLUDED_LABELS)
    train_points = obs.loc[train]
    # Geometry uses all physical cell coordinates only (no class labels
    # in the training density estimate or target bin selection).
    widths = []
    for section in sections:
        if section == test_section:
            continue
        sub = train_points.loc[train_points["_section"].eq(section)]
        if len(sub) < 30:
            continue
        qx = np.percentile(sub["_x"].to_numpy(), [2, 98])
        qy = np.percentile(sub["_y"].to_numpy(), [2, 98])
        area = float(max(1e-8, (qx[1] - qx[0]) * (qy[1] - qy[0])))
        widths.append(math.sqrt(area * TARGET_CELLS_PER_BIN / len(sub)))
    if len(widths) < 5:
        raise ValueError("Insufficient spatial calibration sections")
    width = float(np.median(widths))
    if not np.isfinite(width) or width <= 0:
        raise ValueError("Invalid bin width from training sections")
    # Anchoring each section at (0,0) is deterministic and independent of
    # any target class label. Negative x/y cells are supported.
    src = obs.loc[obs["_section"].eq(test_section)].copy()
    src["_bx"] = np.floor(src["_x"].to_numpy() / width).astype(np.int64)
    src["_by"] = np.floor(src["_y"].to_numpy() / width).astype(np.int64)
    known_src = src.loc[~src["_type"].isin(EXCLUDED_LABELS)]
    if not len(known_src):
        raise ValueError("No confident annotations in target section")
    # IMPORTANT: selecting which physical bins exist must NOT be based on
    # held-out class labels. Use all cells, including ambiguous ones.
    occupancy = src.groupby(["_bx", "_by"], sort=True).size()
    valid = occupancy.loc[(occupancy >= MIN_CELLS_BIN) &
                          (occupancy <= MAX_CELLS_BIN)]
    # If too many bins, geometric ordering alone is used to subsample;
    # no labels or target expression enter bin selection.
    if len(valid) > MAX_TEST_BINS:
        spots = np.linspace(0, len(valid) - 1,
                            MAX_TEST_BINS, dtype=np.int64)
        valid = valid.iloc[spots]
    keys = set(valid.index.tolist())
    if len(keys) < 25:
        raise ValueError("Too few bins with occupancy in [5,24]: " + str(len(keys)))
    accepted = known_src.loc[
        [tuple(p) in keys for p in
         known_src[["_bx", "_by"]].itertuples(index=False, name=None)]].copy()
    # Capture inclusion of Ambiguous cell IDs in exactly these spatial bins;
    # proportions are only among confidently annotated cells.
    in_grid = src[["_bx", "_by"]].apply(tuple, axis=1).isin(keys)
    n_ambiguous_in_bins = int((in_grid &
                            src["_type"].isin(EXCLUDED_LABELS)).sum())
    return width, valid, accepted, n_ambiguous_in_bins, len(src)


def select_reference(obs, test_section, all_classes):
    allowed = obs["_section"].ne(test_section) & ~obs["_type"].isin(EXCLUDED_LABELS)
    train = obs.loc[allowed]
    # Strict section-level separation, and a bounded reference for
    # reasonable Tangram memory/time. Per-class caps are fixed in advance.
    rng = np.random.default_rng(SEED + 100)
    selected = []
    for ct in all_classes:
        positions = np.flatnonzero(train["_type"].to_numpy() == ct)
        if len(positions) < 4:
            raise ValueError("Class lacks >=4 training-section cells: " + ct)
        chosen = rng.choice(positions,
                            size=min(MAX_REFERENCE_PER_CLASS, len(positions)),
                            replace=False)
        selected.extend(train.index[chosen].tolist())
    chosen_ids = pd.Index(selected)
    if len(chosen_ids) < 100:
        raise ValueError("Insufficient mapping/generator reference cells")
    if obs.loc[chosen_ids, "_section"].eq(test_section).any():
        raise AssertionError("Reference/test Bregma section leakage")
    return chosen_ids


def build_fold(a, obs, sections, idx):
    test_section = sections[HOLDOUT_INDICES[idx]]
    # Fixed universal classes from ALL non-ambiguous SOURCE annotations.
    # Classes are scientific labels defined prior to any heldout evaluation;
    # all classes must be represented by train sections. No test-label
    # driven inclusion/exclusion decision per fold.
    classes = sorted(set(obs["_type"]) - EXCLUDED_LABELS)
    ref_ids = select_reference(obs, test_section, classes)
    width, occupancy, accepted, uncertain_in_bins, total_target = (
        fixed_bins_for_fold(obs, sections, test_section))
    all_ref_positions = a.obs_names.get_indexer(ref_ids)
    ref_exp = get_values(a, all_ref_positions)
    ref = pd.DataFrame(ref_exp, index=ref_ids, columns=a.var_names.astype(str))
    if not np.isfinite(ref_exp).all() or np.any(ref_exp < 0):
        raise ValueError("Bad reference expression")
    selected_ids = pd.Index(accepted.index)
    cell_indices = a.obs_names.get_indexer(selected_ids)
    exp = get_values(a, cell_indices)
    if not np.isfinite(exp).all() or np.any(exp < 0):
        raise ValueError("Bad target expression")
    tmp = accepted[["_bx", "_by", "_type"]].copy()
    tmp["_source_index"] = np.arange(len(tmp))
    exp_rows, count_rows, locations, member_rows = [], [], [], []
    for i, ((bx, by), members) in enumerate(tmp.groupby(["_bx", "_by"], sort=True)):
        name = f"MERFISH_SEC{idx}_BIN{i:04d}"
        inds = members["_source_index"].to_numpy(dtype=int)
        expr = exp[inds].sum(axis=0, dtype=np.float64)
        if not np.isfinite(expr).all() or expr.sum() <= 0:
            # A signal-free bin cannot be assigned a fabricated prediction.
            # It remains documented as dropped by expression QC.
            continue
        counts = members["_type"].value_counts().reindex(classes, fill_value=0)
        exp_rows.append((name, expr))
        count_rows.append((name, counts.to_numpy(dtype=int)))
        locations.append({"spot_id": name, "x": (bx + .5) * width,
                          "y": (by + .5) * width,
                          "n_confident_cells": len(inds)})
        member_rows.extend({"spot_id": name,
                            "source_cell_id": str(cid),
                            "source_cell_type": str(lab)}
                           for cid, lab in zip(members.index, members["_type"]))
    if len(exp_rows) < 25:
        raise ValueError("Too few nonzero expression bins")
    ids = [i for i, _ in exp_rows]
    spot_expr = pd.DataFrame(np.vstack([v for _, v in exp_rows]),
                             index=ids, columns=a.var_names.astype(str))
    type_count = pd.DataFrame(np.vstack([v for _, v in count_rows]),
                              index=ids, columns=classes)
    truth = type_count.div(type_count.sum(axis=1), axis=0)
    locs = pd.DataFrame(locations).set_index("spot_id")
    m = pd.DataFrame(member_rows)
    # Class frequencies in the held-out slice are never used for the
    # geometry or reference choices above; only now create evaluation truth.
    trace = {
        "fold": idx, "heldout_section_bregma": float(test_section),
        "train_sections": [float(v) for v in sections if v != test_section],
        "animal_count": 1, "n_source_cells_in_test_section": int(total_target),
        "n_ambiguous_in_included_bins": uncertain_in_bins,
        "n_target_accepted_known_cells": len(accepted),
        "n_reference_cells": len(ref),
        "n_training_sections": len(sections)-1,
        "bin_width_source": "median train-section all-cell coordinate density / 10 cells",
        "bin_width": width,
        "n_candidate_valid_bins_by_all_cell_occupancy": len(occupancy),
        "n_target_bins_with_signal": len(spot_expr),
        "test_bin_occupancy_min": int(type_count.sum(axis=1).min()),
        "test_bin_occupancy_median": float(type_count.sum(axis=1).median()),
        "test_bin_occupancy_max": int(type_count.sum(axis=1).max()),
        "known_labels_only": True,
        "bin_geometry_selection_blind_to_test_class_labels": True,
        "conditional_truth_warning": "X and class fractions exclude ambiguous cells even when they occupy the physical bin; this is not a native low-resolution assay",
        "n_classes": len(classes),
        "classes": classes,
        "expression_unit": "summed Squidpy preprocessed MERFISH X; not raw molecule counts",
    }
    return ref, obs.loc[ref_ids, "_type"], spot_expr, locs, type_count, truth, m, trace


def main():
    args = arguments()
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        raise FileExistsError("Refuse existing output; no silent fold overwrite: " +
                              str(args.out_dir))
    a, obs, sections, source_info = read_source(args.source)
    print("SOURCE", a.n_obs, "cells", a.n_vars, "genes",
          "animals", source_info["n_animals"],
          "sections", len(sections), "ambiguous", source_info["n_ambiguous"],
          flush=True)
    print("X SAMPLE", source_info, flush=True)
    print("TEST SECTIONS", [float(sections[i]) for i in HOLDOUT_INDICES],
          "indices", list(HOLDOUT_INDICES), flush=True)
    folds = []
    for index in range(len(HOLDOUT_INDICES)):
        fold = build_fold(a, obs, sections, index)
        trace = fold[-1]
        print("FOLD READY", index, "Bregma", trace["heldout_section_bregma"],
              "reference", trace["n_reference_cells"],
              "true_spatial_bins", trace["n_target_bins_with_signal"],
              "n_classes", trace["n_classes"],
              "unknown_in_bins", trace["n_ambiguous_in_included_bins"],
              flush=True)
        folds.append(fold)
    if args.dry_run:
        print("DRY RUN PASS — no files written; no model training", flush=True)
        return
    args.out_dir.mkdir(parents=True)
    config = {
        "source_h5ad": str(args.source.resolve()),
        "seed": SEED, "holdout_indices": list(HOLDOUT_INDICES),
        "reference_cap_per_class": MAX_REFERENCE_PER_CLASS,
        "test_cell_occupancy_min": MIN_CELLS_BIN,
        "test_cell_occupancy_max": MAX_CELLS_BIN,
        "test_max_bins": MAX_TEST_BINS,
        "target_cells_bin": TARGET_CELLS_PER_BIN,
        "label_exclusion": sorted(EXCLUDED_LABELS),
        "expression_units_warning": "Preprocessed MERFISH X, NOT verified raw counts",
        "biological_replication_warning": "One animal only; section-heldout evaluation",
        "spatial_truth": "annotation-derived fractions among confident labeled cells",
        "source_inspection": source_info,
    }
    (args.out_dir / "run_config.json").write_text(
        json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
    manifest = []
    for i, (ref, labels, exp, loc, ct, truth, members, trace) in enumerate(folds):
        target = args.out_dir / f"held_out_FOV{i}"
        target.mkdir()
        exp.to_csv(target / "pseudo_spot_expression.csv")
        loc.to_csv(target / "pseudo_spot_locations.csv")
        ref.to_csv(target / "sc_reference_counts.csv")
        labels.rename("label").to_frame().to_csv(
            target / "sc_reference_labels.csv")
        truth.to_csv(target / "pseudo_spot_ground_truth.csv")
        ct.to_csv(target / "pseudo_spot_ground_truth_counts.csv")
        members.to_csv(target / "synthetic_spot_membership.csv", index=False)
        (target / "spatial_source_trace.json").write_text(
            json.dumps(trace, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest.append(trace)
    pd.DataFrame(manifest).drop(columns=["classes"]).to_csv(
        args.out_dir / "section_holdout_manifest.csv", index=False)
    print("PREPARATION FINISHED", len(folds), "held-out sections", flush=True)
    print("OUTPUT", args.out_dir, flush=True)
    print("NO MODEL TRAINING DONE", flush=True)


if __name__ == "__main__":
    main()
