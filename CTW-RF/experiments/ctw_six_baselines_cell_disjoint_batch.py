#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Re-run six ORIGINAL CTW-RF baseline implementations on cell-disjoint inputs.

Reuses the already COMPLETED CTWRF_cell_disjoint_20261123_v1 pseudo-spot
sources. It does not rebuild splits, relabel test cells or reuse historic
baseline predictions. For each of two sampling modes and train/test parts,
run Tangram, RCTD, CellDART, CARD, cell2location, SPOTlight on identical
reference cells and source-disjoint spots. Train fusion weights ONLY on
train pseudospot truth, assess on test pseudospot truth. Test truth is kept
outside all method input directories.

IMPORTANT:
  * All original baseline scripts were supplied by the user as a ZIP and
    checked by SHA256. A hash mismatch is an ERROR, not silently accepted.
  * These are method-specific original settings, not equal compute budgets.
  * Some methods remove tiny reference classes; record their failures or
    performance, never use test truth for after-the-fact selection.
  * Two sampling modes are not independent biological replicates.
  * No source/historical experiment outputs will be overwritten.

Single Windows commands:
  python ctw_six_baselines_cell_disjoint_batch.py --dry-run
  python ctw_six_baselines_cell_disjoint_batch.py --run
  python ctw_six_baselines_cell_disjoint_batch.py --run --resume

A --run requires all dependency probes to PASS; if a method fails during
a run, remaining tasks are attempted and logged. --resume continues tasks
with valid prediction files. Fusion metrics are computed ONLY when all
six baselines for both train/test within a scenario have succeeded.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

import numpy as np
import pandas as pd

import ctw_matched_fusion_comparisons_batch as ctw
import global_stacking_cv as cv

SCENARIOS = ("balanced_celltype", "cell_uniform")
METHODS = ("Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight")
POOLS = {
    "strong2": ("CARD", "cell2location"),
    "expanded4": ("CARD", "cell2location", "RCTD", "SPOTlight"),
    "full6": ("Tangram", "RCTD", "CellDART", "CARD", "cell2location", "SPOTlight"),
}
STRATEGIES = ("EqualWeight", "GlobalStacking", "CTW_HardSelect",
              "CTW_InvRMSE_p2", "CTW_SoftOpt")
SOURCE_DEFAULT = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_cell_disjoint_20261123_v1")
OUT_DEFAULT = Path(r"D:\Research\STdeconv_benchmark\results\CTWRF_six_method_disjoint_20261123_v1")
METHOD_ROOT_DEFAULT = Path(r"D:\Research\STdeconv_benchmark\methods")
RUNNERS = {
    "Tangram": ("Tangram/run_tangram_self_benchmark.py",
                "d96ee0b34609e03f8a99ca1ef1986c0baf844e7e75693d5939dae821b209c638"),
    "RCTD": ("RCTD/run_RCTD_generic_benchmark.R",
             "3fab396112b1e4e00f9e25a9f74d9b83d90cece01ac7e75bf8625ab9ac7aa405"),
    "CellDART": ("CellDART_original/run_CellDART_generic_benchmark.py",
                 "c276531e6bfcfc1fad1514a26049be3f553bd834e10cbce9080cb2e2b12497f9"),
    "CARD": ("CARD/run_CARD_generic_benchmark.R",
             "f26167cd1fb073bc7edc91c7952f3f73fa8deedfc1d9696709247fa290f2ad43"),
    "cell2location": ("Cell2location/run_cell2location_self_benchmark.py",
                      "555e249b7f3fd197c61e2d566e39ce6dcfffddc5b399ed5fa32a5a3baa78bd7d"),
    "SPOTlight": ("SPOTlight/SPOTlight.R",
                  "8071ed9cc28c9d55add638445db4ba7f3172bcd13662dba1edbf31cf5b769141"),
}
OUTPUTS = {
    "Tangram": "Tangram_self_benchmark.csv",
    "RCTD": "RCTD_self_benchmark.csv",
    "CellDART": "CellDART_self_benchmark.csv",
    "CARD": "CARD_self_benchmark.csv",
    "cell2location": "Cell2location_self_benchmark.csv",
    "SPOTlight": "SPOTlight_self_benchmark.csv",
}
ENV_NAMES = {
    "Tangram": "Tangram",
    "RCTD": "RCTD",
    "CellDART": "CellDART-GPU",
    "CARD": "CARD",
    "cell2location": "cell2loc_env",
    "SPOTlight": "SPOTlight",
}

# Direct interpreters avoid conda-run inheriting the user's activated
# Windows virtualenv/Python path. These paths are taken from the user's
# real Conda environment list; importability still requires dry-run.
PYTHON_DEFAULTS = {
    "Tangram": r"D:\ProgramData\miniconda3\envs\Tangram\python.exe",
    "CellDART": r"D:\ProgramData\miniconda3\envs\CellDART-GPU\python.exe",
    "cell2location": r"D:\ProgramData\miniconda3\envs\cell2loc_env\python.exe",
}
ENV_IMPORT = {
    "Tangram": "import tangram, torch, anndata",
    "RCTD": "stopifnot(requireNamespace('spacexr', quietly=TRUE), requireNamespace('Matrix', quietly=TRUE))",
    "CellDART": "import scanpy; from CellDART import da_cellfraction",
    "CARD": "stopifnot(requireNamespace('CARD', quietly=TRUE), requireNamespace('MuSiC', quietly=TRUE), requireNamespace('Matrix', quietly=TRUE))",
    "cell2location": "import cell2location, scvi, anndata",
    "SPOTlight": "stopifnot(requireNamespace('SPOTlight', quietly=TRUE), requireNamespace('Seurat', quietly=TRUE), requireNamespace('SeuratObject', quietly=TRUE))",
}
R_METHODS = frozenset(("RCTD", "CARD", "SPOTlight"))
INPUT_FILES = ("pseudo_spot_expression.csv", "pseudo_spot_locations.csv",
               "sc_reference_counts.csv", "sc_reference_labels.csv")


def arguments():
    p = argparse.ArgumentParser(description=__doc__)
    mode = p.add_mutually_exclusive_group(required=True)
    mode.add_argument("--dry-run", action="store_true")
    mode.add_argument("--run", action="store_true")
    p.add_argument("--resume", action="store_true")
    p.add_argument("--source-root", type=Path, default=SOURCE_DEFAULT)
    p.add_argument("--out-dir", type=Path, default=OUT_DEFAULT)
    p.add_argument("--method-root", type=Path, default=METHOD_ROOT_DEFAULT)
    p.add_argument("--conda", default=r"D:\ProgramData\miniconda3\Scripts\conda.exe")
    p.add_argument("--python-tangram", type=Path, default=Path(PYTHON_DEFAULTS["Tangram"]))
    p.add_argument("--python-celldart", type=Path, default=Path(PYTHON_DEFAULTS["CellDART"]))
    p.add_argument("--python-cell2location", type=Path, default=Path(PYTHON_DEFAULTS["cell2location"]))
    p.add_argument("--seed", type=int, default=2026)
    p.add_argument("--rctd-cores", type=int, default=4)
    p.add_argument("--celldart-iterations", type=int, default=3000)
    p.add_argument("--celldart-pseudo", type=int, default=20000)
    p.add_argument("--cell2location-map-epochs", type=int, default=20000)
    p.add_argument("--cell2location-ref-epochs", type=int, default=250)
    p.add_argument("--tangram-epochs", type=int, default=500)
    p.add_argument("--env-tangram", default=ENV_NAMES["Tangram"])
    p.add_argument("--env-rctd", default=ENV_NAMES["RCTD"])
    p.add_argument("--env-celldart", default=ENV_NAMES["CellDART"])
    p.add_argument("--env-card", default=ENV_NAMES["CARD"])
    p.add_argument("--env-cell2location", default=ENV_NAMES["cell2location"])
    p.add_argument("--env-spotlight", default=ENV_NAMES["SPOTlight"])
    return p.parse_args()


def filehash(path):
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1048576), b""):
            h.update(block)
    return h.hexdigest()


def source_paths(args, scenario, part):
    return args.source_root / scenario / part


def truth_path(args, scenario, part):
    return args.source_root / scenario / "ground_truth_and_membership" / (part + "_truth.csv")


def member_path(args, scenario, part):
    return args.source_root / scenario / "ground_truth_and_membership" / (part + "_membership.csv")


def read_ids(path):
    t = pd.read_csv(path, usecols=[0], dtype=str)
    ids = pd.Index(t.iloc[:, 0].astype(str))
    if not ids.is_unique:
        raise ValueError("Duplicate IDs: " + str(path))
    return ids


def validate_sources(args):
    """Only structural input and source-cell overlap checks, no writes."""
    partition_path = args.source_root / "source_cell_partition.csv"
    if not partition_path.is_file():
        raise FileNotFoundError("Missing source-cell partition: " + str(partition_path))
    partitions = pd.read_csv(partition_path, dtype=str)
    if not {"source_cell_id", "partition", "cell_type"}.issubset(partitions.columns):
        raise ValueError("Missing source partition columns")
    if not partitions.source_cell_id.is_unique:
        raise ValueError("Overlapping source cells in partition manifest")
    sets = {
        k: set(partitions.loc[partitions.partition.eq(k), "source_cell_id"])
        for k in ("reference", "train_donor", "test_donor")
    }
    if any(not ids for ids in sets.values()):
        raise ValueError("Missing a source cell partition")
    if sets["reference"] & sets["train_donor"] or sets["reference"] & sets["test_donor"] or sets["train_donor"] & sets["test_donor"]:
        raise ValueError("Source donor partitions overlap")
    all_info = {}
    for scenario in SCENARIOS:
        truths = {}
        cellsets = {}
        for part in ("train", "test"):
            base = source_paths(args, scenario, part)
            for f in INPUT_FILES:
                if not (base / f).is_file():
                    raise FileNotFoundError(str(base / f))
            tpath = truth_path(args, scenario, part)
            mpath = member_path(args, scenario, part)
            if not tpath.is_file() or not mpath.is_file():
                raise FileNotFoundError("Missing truth/membership for " + scenario + "/" + part)
            truth = pd.read_csv(tpath, index_col=0)
            truth.index = truth.index.astype(str)
            if not truth.index.is_unique:
                raise ValueError("Duplicated truth spot IDs")
            vals = truth.to_numpy(dtype=float)
            if not np.isfinite(vals).all() or np.any(vals < 0) or not np.allclose(vals.sum(axis=1), 1):
                raise ValueError("Noncompositional truth " + str(tpath))
            expression_ids = read_ids(base / "pseudo_spot_expression.csv")
            location_ids = read_ids(base / "pseudo_spot_locations.csv")
            if not expression_ids.equals(truth.index) or set(location_ids) != set(truth.index):
                raise ValueError("Spot IDs are inconsistent: " + scenario + "/" + part)
            reference_ids = read_ids(base / "sc_reference_counts.csv")
            reference_labels_ids = read_ids(base / "sc_reference_labels.csv")
            if set(reference_ids) != sets["reference"] or set(reference_labels_ids) != sets["reference"]:
                raise ValueError("Reference IDs differ from frozen partition: " + str(base))
            membership = pd.read_csv(mpath, dtype=str)
            if not {"spot_id", "source_cell_id"}.issubset(membership.columns):
                raise ValueError("Malformed membership file " + str(mpath))
            if not set(membership.spot_id).issubset(set(truth.index)):
                raise ValueError("Membership contains unknown spots: " + scenario + "/" + part)
            donor_key = "train_donor" if part == "train" else "test_donor"
            contributors = set(membership.source_cell_id)
            if not contributors.issubset(sets[donor_key]):
                raise ValueError("Donor leakage: " + scenario + "/" + part)
            truths[part] = truth
            cellsets[part] = contributors
        if cellsets["train"] & cellsets["test"]:
            raise ValueError("Train/test donor reuse in " + scenario)
        if not truths["train"].columns.equals(truths["test"].columns):
            raise ValueError("Train/test truth type columns differ")
        r1 = source_paths(args, scenario, "train") / "sc_reference_counts.csv"
        r2 = source_paths(args, scenario, "test") / "sc_reference_counts.csv"
        if filehash(r1) != filehash(r2):
            raise ValueError("Train/test reference counts differ: " + scenario)
        all_info[scenario] = {
            "n_train_spots": len(truths["train"]),
            "n_test_spots": len(truths["test"]),
            "n_reference": len(sets["reference"]),
            "train_donor_used": len(cellsets["train"]),
            "test_donor_used": len(cellsets["test"]),
            "cell_types": list(truths["train"].columns),
        }
    return all_info


def chosen_env(args):
    return {
        "Tangram": args.env_tangram,
        "RCTD": args.env_rctd,
        "CellDART": args.env_celldart,
        "CARD": args.env_card,
        "cell2location": args.env_cell2location,
        "SPOTlight": args.env_spotlight,
    }


def runner_paths(args):
    paths = {}
    for method, (relpath, expected_sha) in RUNNERS.items():
        path = args.method_root.joinpath(*relpath.split("/"))
        if not path.is_file():
            raise FileNotFoundError("Missing " + method + " script: " + str(path))
        sha = filehash(path)
        if sha != expected_sha:
            raise ValueError(method + " script has changed since inspected ZIP: " +
                             str(path) + " SHA256=" + sha +
                             "; freeze and review the changed runner before rerun")
        paths[method] = path
    return paths


def chosen_python(args):
    return {"Tangram": args.python_tangram,
            "CellDART": args.python_celldart,
            "cell2location": args.python_cell2location}


def env_probe(args, environments):
    """Read-only dependency probes, distinct from heavy model training."""
    try:
        version = subprocess.run([args.conda, "--version"], capture_output=True,
                                 text=True, timeout=45)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError("Conda executable not usable: " + str(exc)) from exc
    if version.returncode:
        raise RuntimeError("Conda failed: " + (version.stderr or version.stdout))
    print("CONDA", version.stdout.strip() or version.stderr.strip(), flush=True)
    failed = []
    python_paths = chosen_python(args)
    for method in METHODS:
        if method in R_METHODS:
            command = [args.conda, "run", "--no-capture-output", "-n",
                       environments[method], "Rscript", "-e", ENV_IMPORT[method]]
            target = environments[method]
        else:
            python = python_paths[method]
            command = [str(python), "-c", ENV_IMPORT[method]]
            target = str(python)
        try:
            result = subprocess.run(command, capture_output=True,
                                    text=True, timeout=150)
            good = result.returncode == 0
            explanation = (result.stderr or result.stdout)[-1000:].strip()
        except (subprocess.TimeoutExpired, OSError) as exc:
            good, explanation = False, str(exc)
        print("ENV", method, target, "PASS" if good else "FAIL",
              explanation[:250] if not good else "", flush=True)
        if not good:
            failed.append(method)
    if failed:
        raise RuntimeError("Environment preflight failed for " +
                           ", ".join(failed) +
                           ". No experiment has been launched. "
                           "Use --env-* overrides if an existing env has another name.")


def setup_stages(args):
    """Copy only four frozen input files. Never modify original experiment."""
    for scenario in SCENARIOS:
        for part in ("train", "test"):
            source = source_paths(args, scenario, part)
            stage = args.out_dir / "views" / scenario / part
            stage.mkdir(parents=True, exist_ok=True)
            for name in INPUT_FILES:
                destination = stage / name
                original = source / name
                if destination.is_file():
                    if filehash(original) != filehash(destination):
                        raise ValueError("Staged source file changed: " + str(destination))
                else:
                    shutil.copy2(original, destination)
            (stage / "predictions").mkdir(exist_ok=True)


def build_command(args, method, script, stage, envs):
    if method in R_METHODS:
        command = [args.conda, "run", "--no-capture-output",
                   "-n", envs[method], "Rscript", str(script)]
    else:
        command = [str(chosen_python(args)[method]), str(script)]
    command += ["--base_dir", str(stage)]
    if method == "Tangram":
        command += ["--seed", str(args.seed), "--num_epochs", str(args.tangram_epochs),
                    "--mode", "cells", "--density_prior", "rna_count_based",
                    "--device", "auto", "--max_genes", "3000"]
    elif method == "RCTD":
        command += ["--out_dir", str(stage / "predictions"),
                    "--max_cores", str(args.rctd_cores),
                    "--doublet_mode", "full", "--CELL_MIN_INSTANCE", "2"]
    elif method == "CellDART":
        command += ["--seed", str(args.seed), "--nmix", "8",
                    "--n_pseudo", str(args.celldart_pseudo),
                    "--n_iterations", str(args.celldart_iterations),
                    "--n_hvg", "3000"]
    elif method == "CARD":
        command += ["--out_dir", str(stage / "predictions"),
                    "--minCountGene", "5", "--minCountSpot", "5"]
    elif method == "cell2location":
        command += ["--seed", str(args.seed),
                    "--ref_max_epochs", str(args.cell2location_ref_epochs),
                    "--map_max_epochs", str(args.cell2location_map_epochs),
                    "--n_cells_per_location", "8",
                    "--posterior_samples", "1000"]
    elif method == "SPOTlight":
        command += ["--out_dir", str(stage / "predictions"),
                    "--seed", str(args.seed), "--cl_n", "3", "--hvg", "2000"]
    return command


def validated_prediction(path, expected):
    if not path.is_file():
        return False, "prediction missing"
    try:
        p = cv.read_matrix(path)
        p.index = p.index.astype(str)
        if set(p.index) != set(expected.index) or len(p.index) != len(expected.index):
            return False, "spot IDs differ from truth"
        if set(p.columns) != set(expected.columns):
            return False, "cell types differ: " + str(sorted(set(expected.columns)-set(p.columns)))
        array = p.loc[expected.index, expected.columns].to_numpy(dtype=float)
        if not np.isfinite(array).all() or np.min(array) < -1e-6:
            return False, "negative/NaN prediction"
        if np.any(array.sum(axis=1) <= 0):
            return False, "zero-total prediction spot"
        if np.any(np.abs(array.sum(axis=1) - 1) > 0.01):
            return False, "rows not compositional (>0.01 deviation)"
        return True, "valid"
    except Exception as exc:
        return False, repr(exc)


def run_task(args, scenario, part, method, script, envs):
    stage = args.out_dir / "views" / scenario / part
    outpred = stage / "predictions" / OUTPUTS[method]
    truth = pd.read_csv(truth_path(args, scenario, part), index_col=0)
    truth.index = truth.index.astype(str)
    valid, why = validated_prediction(outpred, truth)
    log = args.out_dir / "logs" / (scenario + "_" + part + "_" + method + ".log")
    if valid:
        print("REUSE", scenario, part, method, flush=True)
        return {"scenario": scenario, "part": part, "method": method,
                "status": "reused_valid", "elapsed_seconds": 0.0,
                "prediction": str(outpred), "log": str(log), "note": why}
    if outpred.is_file():
        # Preserve an invalid partial output for the final audit and allow
        # automatic retry on --resume. No historical source files touched.
        rejected = outpred.with_name(
            outpred.name + ".rejected_" + str(time.time_ns()) + ".csv")
        outpred.rename(rejected)
        print("QUARANTINED INVALID OUTPUT", rejected, why, flush=True)
    command = build_command(args, method, script, stage, envs)
    log.parent.mkdir(exist_ok=True, parents=True)
    print("START", scenario, part, method, flush=True)
    start = time.perf_counter()
    with log.open("w", encoding="utf-8") as f:
        f.write("COMMAND " + subprocess.list2cmdline(command) + "\n")
        f.flush()
        result = subprocess.run(command, stdout=f, stderr=subprocess.STDOUT)
    elapsed = time.perf_counter() - start
    valid, why = validated_prediction(outpred, truth)
    success = result.returncode == 0 and valid
    if not success and log.is_file():
        tail = log.read_text(encoding="utf-8", errors="replace").splitlines()[-12:]
        print("FAILED", scenario, part, method, "exit", result.returncode,
              "reason", why, "\n".join(tail), flush=True)
    else:
        print("DONE", scenario, part, method,
              "seconds", round(elapsed, 1), flush=True)
    return {"scenario": scenario, "part": part, "method": method,
            "status": "success" if success else "failed",
            "returncode": result.returncode, "elapsed_seconds": round(elapsed, 3),
            "prediction": str(outpred), "log": str(log), "note": why}


def load_predictions(args, scenario, part, methods, truth):
    stack = []
    for method in methods:
        predpath = args.out_dir / "views" / scenario / part / "predictions" / OUTPUTS[method]
        good, note = validated_prediction(predpath, truth)
        if not good:
            raise ValueError("Incomplete " + scenario + "/" + part + "/" +
                             method + ": " + note)
        p = cv.read_matrix(predpath)
        stack.append(cv.normalize(p.loc[truth.index, truth.columns].to_numpy(), method))
    return np.stack(stack, axis=0)


def compare_pool(args, scenario, poolname, selected_methods):
    train_truth = pd.read_csv(truth_path(args, scenario, "train"), index_col=0)
    test_truth = pd.read_csv(truth_path(args, scenario, "test"), index_col=0)
    train_truth.index = train_truth.index.astype(str)
    test_truth.index = test_truth.index.astype(str)
    classes = list(train_truth.columns)
    if classes != list(test_truth.columns):
        raise ValueError("Train/test truth labels differ")
    ytrain, ytest = train_truth.to_numpy(dtype=float), test_truth.to_numpy(dtype=float)
    ptr = load_predictions(args, scenario, "train", selected_methods, train_truth)
    pte = load_predictions(args, scenario, "test", selected_methods, test_truth)
    tr = np.arange(len(train_truth))
    fitted = {
        "GlobalStacking": cv.fit_global_weights(ptr, ytrain),
        "CTW_HardSelect": ctw.hardselect_weights(ptr, ytrain, tr),
        "CTW_InvRMSE_p2": ctw.invrmse_weights(ptr, ytrain, tr),
    }
    fitted["CTW_SoftOpt"], n_fallback = ctw.softopt_weights(ptr, ytrain, tr)
    derived = {
        "EqualWeight": pte.mean(axis=0),
        "GlobalStacking": cv.fuse(pte, fitted["GlobalStacking"]),
        "CTW_HardSelect": ctw.fuse_cellwise(pte, fitted["CTW_HardSelect"], "CTW_HardSelect"),
        "CTW_InvRMSE_p2": ctw.fuse_cellwise(pte, fitted["CTW_InvRMSE_p2"], "CTW_InvRMSE_p2"),
        "CTW_SoftOpt": ctw.fuse_cellwise(pte, fitted["CTW_SoftOpt"], "CTW_SoftOpt"),
    }
    derived.update({name: pte[i] for i, name in enumerate(selected_methods)})
    rows, weight_rows = [], []
    for label, values in derived.items():
        x = cv.normalize(values, label)
        rows.append({"scenario": scenario, "pool": poolname, "method": label,
                     "n_methods_in_pool": len(selected_methods),
                     "n_train_spots": len(ytrain), "n_test_spots": len(ytest),
                     "softopt_fallback_celltypes": n_fallback if label == "CTW_SoftOpt" else 0,
                     **cv.metric_dict(ytest, x)})
        dest = args.out_dir / "fusion_predictions" / scenario / poolname
        dest.mkdir(parents=True, exist_ok=True)
        pd.DataFrame(x, index=test_truth.index, columns=classes).to_csv(
            dest / ("test_" + label + ".csv"))
    for strategy, weight in fitted.items():
        w = np.asarray(weight)
        ct_names = ["ALL"] if w.ndim == 1 else classes
        for i, method in enumerate(selected_methods):
            for ci, cell_type in enumerate(ct_names):
                weight_rows.append({
                    "scenario": scenario, "pool": poolname,
                    "fusion_method": strategy, "base_method": method,
                    "cell_type": cell_type,
                    "weight": float(w[i] if w.ndim == 1 else w[i, ci]),
                })
    print("EVALUATED", scenario, poolname,
          "CTW_SoftOpt JSD", round(next(row["JSD"] for row in rows
                                         if row["method"] == "CTW_SoftOpt"), 6),
          "softopt_fallback", n_fallback, flush=True)
    return rows, weight_rows


def main():
    args = arguments()
    if args.rctd_cores < 1 or min(args.celldart_iterations, args.celldart_pseudo,
                                  args.cell2location_map_epochs,
                                  args.cell2location_ref_epochs,
                                  args.tangram_epochs) < 1:
        raise ValueError("Invalid positive training budgets")
    source = args.source_root.resolve()
    output = args.out_dir.resolve()
    if source == output or source in output.parents or output in source.parents:
        raise ValueError("New workspace must be independent from source results")
    info = validate_sources(args)
    scripts = runner_paths(args)
    environments = chosen_env(args)
    config = {
        "source_root": str(source), "out_dir": str(output),
        "method_root": str(args.method_root.resolve()),
        "source_cell_disjoint_protocol": "reference/train_donor/test_donor strict IDs",
        "scenarios": list(SCENARIOS), "pools": {k: list(v) for k,v in POOLS.items()},
        "methods": list(METHODS), "runner_sha256": {m: RUNNERS[m][1] for m in METHODS},
        "conda": args.conda, "environments": environments,
        "python_interpreters": {k: str(v.resolve())
                                for k, v in chosen_python(args).items()},
        "seed": args.seed,
        "rctd_cores": args.rctd_cores, "celldart_iterations": args.celldart_iterations,
        "celldart_pseudo": args.celldart_pseudo,
        "cell2location_map_epochs": args.cell2location_map_epochs,
        "cell2location_ref_epochs": args.cell2location_ref_epochs,
        "tangram_epochs": args.tangram_epochs,
    }
    config_file = args.out_dir / "run_config.json"
    if args.out_dir.exists() and any(args.out_dir.iterdir()):
        if not args.resume or not config_file.is_file():
            raise FileExistsError("New output exists: use --run --resume for frozen config")
        prior = json.loads(config_file.read_text(encoding="utf-8"))
        if prior != config:
            raise ValueError("Resume config mismatch; original result directory preserved")
    for scenario, s in info.items():
        print("SOURCE READY", scenario, s["n_train_spots"], "train spots,",
              s["n_test_spots"], "test spots,", s["n_reference"],
              "reference cells,", len(s["cell_types"]), "cell types",
              flush=True)
    for method, p in scripts.items():
        print("RUNNER SHA256 PASS", method, str(p), flush=True)
    print("BUDGET cell2location", args.cell2location_ref_epochs,
          "reference epochs and", args.cell2location_map_epochs,
          "map epochs * 4 runs (CPU by original runner);",
          "CellDART iterations", args.celldart_iterations, "* 4 runs", flush=True)
    print("PYTHON DIRECT INTERPRETERS",
          {k: str(v) for k, v in chosen_python(args).items()}, flush=True)
    env_probe(args, environments)
    if args.dry_run:
        print("PLAN", len(SCENARIOS), "sampling scenarios x 2 train/test",
              "x 6 original baseline runners = 24 tasks",
              "then 2 scenarios x 3 matched method pools", flush=True)
        print("DRY RUN PASS — no experiment outputs written", flush=True)
        return
    args.out_dir.mkdir(parents=True, exist_ok=True)
    if not config_file.exists():
        config_file.write_text(json.dumps(config, indent=2, ensure_ascii=False),
                               encoding="utf-8")
    setup_stages(args)
    rows = []
    all_success = True
    summary_path = args.out_dir / "baseline_task_status.csv"
    for scenario in SCENARIOS:
        for part in ("train", "test"):
            for method in METHODS:
                result = run_task(args, scenario, part, method,
                                  scripts[method], environments)
                rows.append(result)
                all_success = all_success and result["status"] in ("success", "reused_valid")
                pd.DataFrame(rows).to_csv(summary_path, index=False)
    metric_rows, weight_rows = [], []
    for scenario in SCENARIOS:
        missing = [
            method + "/" + part
            for method in METHODS for part in ("train", "test")
            if not validated_prediction(
                args.out_dir / "views" / scenario / part / "predictions" / OUTPUTS[method],
                pd.read_csv(truth_path(args, scenario, part), index_col=0))[0]
        ]
        if missing:
            print("SKIP FULL SIX FUSION", scenario,
                  "missing/invalid", ", ".join(missing), flush=True)
            all_success = False
            continue
        for poolname, members in POOLS.items():
            m, w = compare_pool(args, scenario, poolname, members)
            metric_rows.extend(m)
            weight_rows.extend(w)
            pd.DataFrame(metric_rows).to_csv(
                args.out_dir / "heldout_metrics_by_scenario_pool.csv",
                index=False)
            pd.DataFrame(weight_rows).to_csv(
                args.out_dir / "frozen_weights_by_scenario_pool.csv",
                index=False)
    if not all_success:
        raise RuntimeError("BATCH PARTIAL: see baseline_task_status.csv and logs. "
                           "Keep files and use --run --resume to retry "
                           "missing methods after fixing their dependencies.")
    print("BATCH FINISHED", len(SCENARIOS),
          "scenarios, 24/24 base method runs, 6 matched pool evaluations;",
          len(metric_rows), "held-out metric rows", flush=True)
    print("OUTPUT", args.out_dir, flush=True)


if __name__ == "__main__":
    main()
