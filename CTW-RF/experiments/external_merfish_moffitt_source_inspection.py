#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Acquire and inspect an INDEPENDENT real MERFISH dataset (NO training).

Dataset: Moffitt et al. (2018), mouse hypothalamic preoptic region.
Source: Squidpy's published, preprocessed AnnData (figshare file 28169379).
URL: https://ndownloader.figshare.com/files/28169379
Original source: https://doi.org/10.5061/dryad.8t8s248
Squidpy tutorial: https://squidpy.readthedocs.io/en/stable/notebooks/tutorials/tutorial_merfish.html

This is *only* acquisition and data-schema/numeric inspection, NOT a
deconvolution benchmark. No method results are calculated. In particular,
preprocessed MERFISH expression cannot be asserted to be raw integer
transcript counts merely because values are nonnegative/integer-like.

USAGE (from a Windows Python environment with anndata, pandas, scipy, h5py):
  python external_merfish_moffitt_source_inspection.py --download
  python external_merfish_moffitt_source_inspection.py --inspect-only
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import os
import sys
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd

SOURCE_URL = "https://ndownloader.figshare.com/files/28169379"
DEFAULT_ROOT = Path(r"D:\Research\STdeconv_benchmark\data\external\MERFISH_Moffitt_2018")
FILENAME = "moffitt_merfish_squidpy_preprocessed.h5ad"
OUT_JSON = "source_inspection.json"
EXPECTED_N_CELLS = 73655
EXPECTED_N_GENES = 161


def args_parse():
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--download", action="store_true",
                   help="download the public H5AD if absent, then inspect it")
    g.add_argument("--inspect-only", action="store_true",
                   help="read an existing local H5AD; no download")
    p.add_argument("--data-dir", type=Path, default=DEFAULT_ROOT)
    return p.parse_args()


def sha256(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1048576), b""):
            h.update(chunk)
    return h.hexdigest()


def fetch_if_needed(path):
    if path.is_file():
        print("REUSE DOWNLOADED DATA", str(path), flush=True)
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    part = path.with_name(path.name + f".part_pid{os.getpid()}")
    if part.exists():
        raise FileExistsError("Refusing to overwrite unrelated partial file: " + str(part))
    print("DOWNLOAD START", SOURCE_URL, flush=True)
    print("DESTINATION", path, flush=True)
    try:
        request = Request(SOURCE_URL, headers={"User-Agent": "Mozilla/5.0 academic reproducibility downloader"})
        with urlopen(request, timeout=120) as response, part.open("xb") as output:
            total = 0
            while True:
                buf = response.read(1024 * 1024)
                if not buf:
                    break
                output.write(buf)
                total += len(buf)
                if total // (10 * 1024 * 1024) > (total - len(buf)) // (10 * 1024 * 1024):
                    print("DOWNLOADED_MIB", round(total / (1024 * 1024), 1), flush=True)
        if total < 1_000_000:
            raise ValueError("Downloaded content unexpectedly small; not accepting as H5AD")
        with part.open("rb") as f:
            sig = f.read(8)
        if sig != b"\x89HDF\r\n\x1a\n":
            raise ValueError("Download is not HDF5 (maybe HTTP html); keeping .part file for diagnosis")
        if path.exists():
            raise FileExistsError("Target appeared during download; refusing overwrite " + str(path))
        part.rename(path)
        print("DOWNLOAD COMPLETE", total, "bytes", flush=True)
    except Exception:
        print("DOWNLOAD FAILED; partial file, if any, remains at", part, flush=True)
        raise


def as_strings(series):
    return series.astype("string").fillna("MISSING").astype(str)


def sampled_expression(adata):
    import scipy.sparse as sp
    n = min(1024, adata.n_obs)
    # Deterministic spread, not selected by cell type/truth/performance.
    indices = np.unique(np.linspace(0, adata.n_obs - 1, n, dtype=np.int64))
    sample = adata.X[indices, :]
    sample = sample.toarray() if sp.issparse(sample) else np.asarray(sample)
    sample = np.asarray(sample, dtype=np.float64)
    return {
        "sample_cells": int(len(indices)),
        "sample_min": float(np.min(sample)),
        "sample_max": float(np.max(sample)),
        "sample_fraction_zero": float(np.mean(sample == 0)),
        "sample_fraction_noninteger_positive": float(np.mean(
            (sample > 0) & (np.abs(sample - np.round(sample)) > 1e-6))),
        "sample_nonnegative_finite": bool(np.isfinite(sample).all() and (sample >= 0).all()),
        "X_dtype": str(getattr(adata.X, "dtype", "unknown")),
        "X_sparsity": bool(sp.issparse(adata.X)),
    }


def main():
    a = args_parse()
    target = a.data_dir / FILENAME
    if a.download:
        fetch_if_needed(target)
    if not target.is_file():
        raise FileNotFoundError("Dataset absent: " + str(target))
    import h5py
    if not h5py.is_hdf5(str(target)):
        raise ValueError("File is not HDF5: " + str(target))
    import anndata as ad
    adata = ad.read_h5ad(target)
    obs = adata.obs
    result = {
        "data_source": "Moffitt et al. 2018 MERFISH, Squidpy preprocessed subset",
        "source_url": SOURCE_URL,
        "original_dataset_doi": "10.5061/dryad.8t8s248",
        "h5ad_path": str(target.resolve()),
        "h5ad_bytes": int(target.stat().st_size),
        "h5ad_sha256": sha256(target),
        "n_cells": int(adata.n_obs),
        "n_genes": int(adata.n_vars),
        "obs_columns": list(map(str, obs.columns)),
        "expression": sampled_expression(adata),
        "layers": list(map(str, adata.layers.keys())),
        "has_raw_attribute": bool(adata.raw is not None),
        "obsm_keys": list(map(str, adata.obsm.keys())),
    }
    print("DATASET", result["n_cells"], "cells", result["n_genes"], "genes", flush=True)
    if (adata.n_obs, adata.n_vars) != (EXPECTED_N_CELLS, EXPECTED_N_GENES):
        raise ValueError("Public Squidpy dataset dimensions unexpectedly changed; do not silently proceed")
    print("OBS COLUMNS", result["obs_columns"], flush=True)
    print("EXPRESSION", result["expression"], flush=True)
    print("LAYERS", result["layers"], "ANNDATA_RAW", result["has_raw_attribute"], flush=True)
    needed = ("Animal_ID", "Bregma", "Cell_class", "Centroid_X", "Centroid_Y")
    missing = [col for col in needed if col not in obs]
    result["missing_required_metadata"] = missing
    if missing:
        raise ValueError("Missing expected biological/spatial metadata: " + repr(missing))
    coords = obs[["Centroid_X", "Centroid_Y"]].apply(pd.to_numeric, errors="coerce")
    valid_spatial = np.isfinite(coords.to_numpy()).all(axis=1)
    result["n_cells_with_finite_xy"] = int(valid_spatial.sum())
    for col in ("Animal_ID", "Bregma", "Cell_class", "Behavior", "batch"):
        if col not in obs:
            continue
        counts = as_strings(obs[col]).value_counts(dropna=False)
        result[col + "_counts"] = {str(k): int(v) for k, v in counts.items()}
        print("GROUP", col, "unique", len(counts),
              "largest", [(str(k), int(v)) for k, v in counts.head(15).items()], flush=True)
    if "Animal_ID" in obs and "Cell_class" in obs:
        groups = pd.crosstab(as_strings(obs["Animal_ID"]), as_strings(obs["Cell_class"]))
        result["animal_by_class_counts"] = {
            str(row_id): {str(ct): int(v) for ct, v in row.items() if v > 0}
            for row_id, row in groups.iterrows()
        }
        print("ANIMAL_BY_CLASS", groups.shape, "types", flush=True)
    print("SPATIAL", result["n_cells_with_finite_xy"], "/", adata.n_obs, "finite XY", flush=True)
    if "Cell_ID" in obs:
        result["n_unique_cell_id_field"] = int(obs["Cell_ID"].nunique(dropna=True))
    result["n_unique_obs_names"] = int(adata.obs_names.nunique())
    result["annotation_truth_semantics"] = (
        "Cell_class annotations from the source study; they are not manually "
        "verified cell fractions of Visium spots. Synthetic spatial-bin "
        "proportions may later be generated from original cell labels.")
    result["counts_warning"] = (
        "This is Squidpy PREPROCESSED MERFISH. Inspect source provenance "
        "before using counts-based RCTD/cell2location. Integer-likeness of "
        "a sample does not prove integer raw counts. Do not round, rescale, "
        "or invent raw counts just to satisfy an algorithm.")
    a.data_dir.mkdir(parents=True, exist_ok=True)
    manifest = a.data_dir / OUT_JSON
    if manifest.exists():
        old = json.loads(manifest.read_text(encoding="utf-8"))
        if old.get("h5ad_sha256") != result["h5ad_sha256"]:
            raise ValueError("Source H5AD hash changed versus existing inspection; refusing overwrite")
    manifest.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
    print("SOURCE INSPECTION PASS", str(manifest), flush=True)
    print("NO MODEL TRAINING OR DECONVOLUTION PERFORMED", flush=True)


if __name__ == "__main__":
    main()
