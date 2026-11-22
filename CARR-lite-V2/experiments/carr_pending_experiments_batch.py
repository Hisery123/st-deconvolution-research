#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run one predeclared CARR-lite V2 extension bundle, with safe checkpoints.

On the existing 52-view simulation suite (13 base scenarios x 4 depths), run:
  (A) marker_k=20/80 and confusion_k=1/5 under strict category hold-out,
      independently for RCTD and CARD (8 jobs),
  (B) strict category-held-out feature ablation no_depth (2 jobs),
  (C) fixed simple logistic-presence and threshold controls (2 jobs).

Only one parameter is changed at a time relative to marker_k=40/confusion_k=3.
Each job gets a new isolated output folder, and a completed job is skipped
only if its config and 52-by-method metric counts can be validated. Partial
outputs are NEVER overwritten or silently skipped. Timing measures full
pipeline wall clock, not model-only inference time.

Example:
  python carr_pending_experiments_batch.py --dry-run  # no files written
  python carr_pending_experiments_batch.py --run      # 12 jobs, resumable
  python carr_pending_experiments_batch.py --run --tasks controls,no_depth
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
import os
from pathlib import Path
import subprocess
import sys
import time

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
DEFAULT_SUITE = Path(r"D:\Research\STdeconv_benchmark\data\groundtruth\rarecell_52scenario_suite")
DEFAULT_OUT = Path(r"D:\Research\STdeconv_benchmark\results\CARRliteV2_pending_batch_20261122_v1")
DEFAULT_REFERENCE = Path(r"D:\Research\STdeconv_benchmark\results\CARRliteV2_category_holdout_20261122_v1")
METRICS = ("target_RMSE", "target_MAE", "balanced_AUPRC",
           "recall_at_10pct_FPR", "matrix_RMSE")


@dataclass(frozen=True)
class Job:
    key: str
    method: str
    kind: str
    marker_k: int = 40
    confusion_k: int = 3
    ablation: str = "none"

    def dest(self, root: Path) -> Path:
        dest = root / self.key / self.method
        if self.ablation != "none":
            dest = dest / self.ablation
        return dest

    def source(self) -> Path:
        if self.kind == "controls":
            return HERE / "logistic_threshold_category_holdout.py"
        return HERE / "category_holdout_carr_v2.py"

    def labels(self) -> tuple[str, ...]:
        if self.kind == "controls":
            return (f"Original_{self.method}", "LogisticPresence12", "Threshold1D")
        return (f"Original_{self.method}", "AbundanceOnly", "HGBC_a15", "HGBC_a30", "HGBC_a50")


def build_jobs(tasks, methods):
    jobs = []
    for method in methods:
        if "sensitivity" in tasks:
            for key, marker_k, confusion_k in (
                ("marker_k20", 20, 3), ("marker_k80", 80, 3),
                ("confusion_k1", 40, 1), ("confusion_k5", 40, 5),
            ):
                jobs.append(Job(key, method, "sensitivity", marker_k, confusion_k))
        if "no_depth" in tasks:
            jobs.append(Job("no_depth", method, "no_depth", ablation="no_depth"))
        if "controls" in tasks:
            jobs.append(Job("logistic_threshold", method, "controls"))
    return jobs


def parse_args():
    ap = argparse.ArgumentParser(description=__doc__)
    action = ap.add_mutually_exclusive_group(required=True)
    action.add_argument("--dry-run", action="store_true", help="check all inputs/jobs; no files written")
    action.add_argument("--run", action="store_true", help="execute all pending jobs")
    ap.add_argument("--suite-root", type=Path, default=DEFAULT_SUITE)
    ap.add_argument("--out-dir", type=Path, default=DEFAULT_OUT)
    ap.add_argument("--reference-root", type=Path, default=DEFAULT_REFERENCE)
    ap.add_argument("--tasks", default="sensitivity,no_depth,controls",
                    help="Comma-separated: sensitivity,no_depth,controls")
    ap.add_argument("--methods", nargs="+", choices=("RCTD", "CARD"),
                    default=["RCTD", "CARD"])
    ap.add_argument("--prediction-template", default="predictions/{method}_self_benchmark.csv")
    ap.add_argument("--seed", type=int, default=20260724)
    return ap.parse_args()


def command_for(job: Job, args, dry=False):
    cmd = [sys.executable, "-u", str(job.source()), "--method", job.method,
           "--suite-root", str(args.suite_root),
           "--prediction-template", args.prediction_template,
           "--seed", str(args.seed),
           "--marker-k", str(job.marker_k),
           "--confusion-k", str(job.confusion_k)]
    if job.ablation != "none":
        cmd += ["--ablation", job.ablation]
    if dry:
        cmd.append("--dry-run")
    else:
        cmd += ["--out-dir", str(args.out_dir / job.key)]
    return cmd


def check_finished(job, dest: Path, seed: int):
    if not dest.is_dir():
        return False
    cfgfile, csvfile = dest / "run_config.json", dest / "metrics_by_scenario.csv"
    if not cfgfile.is_file() or not csvfile.is_file():
        raise RuntimeError("Partial/unknown job directory (refuse overwrite): " + str(dest))
    try:
        cfg = json.loads(cfgfile.read_text(encoding="utf-8"))
        actual_method = cfg.get("base_method", cfg.get("method"))
        expected = {"seed": seed, "marker_k": job.marker_k,
                    "confusion_k": job.confusion_k}
        if any(cfg.get(k) != v for k, v in expected.items()) or actual_method != job.method:
            raise ValueError("run_config does not match requested method/feature parameters")
        if job.kind != "controls" and cfg.get("ablation") != job.ablation:
            raise ValueError("ablation does not match requested job")
        if job.kind == "controls" and [v.get("name") for v in cfg.get("controls", [])] != list(job.labels()[1:]):
            raise ValueError("unexpected simple controls configuration")
        df = pd.read_csv(csvfile)
        required = set(METRICS) | {"scenario_id", "method", "base_method"}
        if not required.issubset(df.columns):
            raise ValueError("missing required metric columns")
        if df["base_method"].nunique() != 1 or df["base_method"].iloc[0] != job.method:
            raise ValueError("wrong base method in metrics")
        counts = df.groupby("method").size().to_dict()
        if counts != {lab: 52 for lab in job.labels()}:
            raise ValueError("unexpected per-label counts: " + str(counts))
        if len(df) != 52 * len(job.labels()) or df["scenario_id"].nunique() != 52:
            raise ValueError("unexpected scenario/row counts")
        if df.duplicated(["scenario_id", "method"]).any():
            raise ValueError("duplicated scenario-method metric row")
        if not np.isfinite(df[list(METRICS)].to_numpy(dtype=float)).all():
            raise ValueError("non-finite metrics")
        folders = [p for p in dest.iterdir() if p.is_dir()]
        if len(folders) != 52:
            raise ValueError("expected 52 scenario prediction folders")
    except Exception as exc:
        raise RuntimeError(f"Existing job fails validation: {dest}: {exc}") from exc
    return True


def validate_reference(args):
    refs = {}
    for method in args.methods:
        p = args.reference_root / method / "metrics_by_scenario.csv"
        if not p.is_file():
            raise FileNotFoundError("Original strict-category reference missing: " + str(p))
        d = pd.read_csv(p)
        if d.groupby("method").size().get("HGBC_a30") != 52:
            raise ValueError("Reference lacks 52 HGBC_a30 rows: " + str(p))
        if d[d.method.eq("HGBC_a30")]["scenario_id"].nunique() != 52:
            raise ValueError("Duplicate baseline scenarios: " + str(p))
        refs[method] = d
    return refs


def preflight(jobs, args):
    if len(args.methods) != len(set(args.methods)):
        raise ValueError("Duplicate base methods")
    validate_reference(args)
    for job in jobs:
        if not job.source().is_file():
            raise FileNotFoundError("Missing experiment script: " + str(job.source()))
        dest = job.dest(args.out_dir)
        if dest.exists() and any(dest.iterdir()):
            complete = check_finished(job, dest, args.seed)
            state = "COMPLETED, SKIP" if complete else "ABSENT"
        elif dest.exists():
            state = "EMPTY DIR"
        else:
            state = "NEW"
        print("PLAN", job.key, job.method, "marker", job.marker_k,
              "confusion", job.confusion_k, "ablation", job.ablation, state,
              flush=True)
    for method in args.methods:
        # Two distinct code paths; one input/split check for each, no output.
        for kind in ("sensitivity", "controls"):
            if not any(j.method == method and j.kind == kind for j in jobs):
                if kind == "sensitivity" and not any(j.method == method and j.kind == "no_depth" for j in jobs):
                    continue
                if kind == "controls":
                    continue
            job = next((j for j in jobs if j.method == method and j.kind == kind),
                       Job("preflight", method, "sensitivity"))
            cmd = command_for(job, args, dry=True)
            # Use canonical k/marker for input validation, then actual jobs use
            # their predeclared varied values during construction/training.
            if kind == "sensitivity":
                i = cmd.index("--marker-k")
                cmd[i + 1] = "40"
                i = cmd.index("--confusion-k")
                cmd[i + 1] = "3"
                if "--ablation" in cmd:
                    j = cmd.index("--ablation")
                    del cmd[j:j + 2]
            result = subprocess.run(cmd, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    text=True, encoding="utf-8", errors="replace")
            if result.returncode or "DRY RUN PASS" not in result.stdout:
                raise RuntimeError("Preflight failed: " + " ".join(cmd) + "\n" + result.stdout)
            print("INPUT PRECHECK PASS", method, kind, flush=True)
    print("BATCH PREFLIGHT PASS:", len(jobs), "jobs", flush=True)


def write_csv_atomic(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    df.to_csv(tmp, index=False)
    os.replace(tmp, path)


def summaries(jobs, args, statuses):
    means = []
    for job in jobs:
        dest = job.dest(args.out_dir)
        if not dest.exists() or not (dest / "run_config.json").exists():
            continue
        if not check_finished(job, dest, args.seed):
            continue
        data = pd.read_csv(dest / "metrics_by_scenario.csv")
        for label, part in data.groupby("method"):
            row = {"job": job.key, "base_method": job.method,
                   "marker_k": job.marker_k, "confusion_k": job.confusion_k,
                   "ablation": job.ablation, "method": label,
                   "n_views": len(part)}
            for met in METRICS:
                row[met] = float(part[met].mean())
            means.append(row)
    if means:
        write_csv_atomic(pd.DataFrame(means), args.out_dir / "batch_metric_means.csv")
    if statuses:
        write_csv_atomic(pd.DataFrame(statuses), args.out_dir / "batch_run_status.csv")
    return len(means)


def do_job(job, args, log_dir):
    dest = job.dest(args.out_dir)
    if dest.exists() and any(dest.iterdir()):
        if check_finished(job, dest, args.seed):
            print("SKIP validated", job.key, job.method, flush=True)
            return 0.0, "skipped_verified"
        raise RuntimeError("Nonempty unknown output directory " + str(dest))
    cmd = command_for(job, args)
    logfile = log_dir / f"{job.key}_{job.method}.log"
    start = time.perf_counter()
    print("START", job.key, job.method, "LOG", logfile, flush=True)
    with logfile.open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                text=True, encoding="utf-8", errors="replace", bufsize=1)
        assert proc.stdout is not None
        for line in proc.stdout:
            log.write(line)
            log.flush()
            if (line.startswith(("TRAINING FOLD", "FINISHED", "OUTPUT", "Traceback"))
                    or line.startswith("Completed B13") or line.startswith("INPUT CHECK PASS")):
                print(job.key, job.method, line.rstrip(), flush=True)
        code = proc.wait()
    elapsed = time.perf_counter() - start
    if code != 0:
        raise RuntimeError(f"Job failed (exit={code}, elapsed={elapsed:.1f}s). Read {logfile}. "
                           "Partial outputs are preserved; do not force overwrite.")
    check_finished(job, dest, args.seed)
    print("DONE", job.key, job.method, "elapsed_seconds", round(elapsed, 2), flush=True)
    return elapsed, "success"


def main():
    args = parse_args()
    requested = [s.strip() for s in args.tasks.split(",") if s.strip()]
    if not requested or len(set(requested)) != len(requested) or not set(requested) <= {"sensitivity", "no_depth", "controls"}:
        raise ValueError("tasks must be distinct names in sensitivity,no_depth,controls")
    jobs = build_jobs(set(requested), args.methods)
    preflight(jobs, args)
    if args.dry_run:
        print("DRY RUN PASS — no files written", flush=True)
        return
    log_dir = args.out_dir / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    statuses = []
    for number, job in enumerate(jobs, 1):
        print(f"BATCH JOB {number}/{len(jobs)}", flush=True)
        try:
            elapsed, state = do_job(job, args, log_dir)
        except Exception:
            statuses.append({"job": job.key, "base_method": job.method,
                             "status": "FAILED_OR_INCOMPLETE", "elapsed_seconds": None})
            summaries(jobs, args, statuses)
            raise
        statuses.append({"job": job.key, "base_method": job.method,
                         "status": state, "elapsed_seconds": round(elapsed, 3)})
        summaries(jobs, args, statuses)
    print("BATCH FINISHED", len(jobs), "jobs", flush=True)
    print("METRICS", args.out_dir / "batch_metric_means.csv", flush=True)
    print("STATUS", args.out_dir / "batch_run_status.csv", flush=True)


if __name__ == "__main__":
    main()
