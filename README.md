# Spatial Transcriptomics Deconvolution Research

Reproducible research and **evidence-driven extension planning** for two separate spatial transcriptomics deconvolution studies: **CTW-RF** and **CARR-lite V2**.

> Current stage (2026-11-21): repository initialization and source-code/experiment audit. Manuscript-reported numbers have **not** been independently recomputed in this repository. No new scientific experiment was run during initialization.

## Current execution priority

The researcher has prioritized **running the planned incremental experiments first** and deferring comprehensive publication audits until after the expansion runs. Both new scripts are committed but **not yet executed locally**.

- [Experiment execution queue / current next steps](EXECUTION_QUEUE.md)
- [CTW-RF: 5-fold global stacking comparator](CTW-RF/experiments/global_stacking_cv.py)
- [CARR-lite V2: cross-method RCTD/CARD adapter](CARR-lite-V2/experiments/cross_method_carr_v2.py)

## Projects

| Project | Scope | Current priority |
|---|---|---|
| [CTW-RF](CTW-RF/EXPERIMENT_PLAN.md) | Cell-type-wise reliability fusion of existing deconvolution predictions | Audit pseudo-spot/reference cell overlap; out-of-fold evaluation; compare nearest ensemble baselines |
| [CARR-lite V2](CARR-lite-V2/EXPERIMENT_PLAN.md) | Rare-cell-aware post-calibration on a Tangram base model | Audit feature availability and FOV/reference split; then test alternative base deconvolvers |

## New source archive (2026-11-21)

On GitHub commit [5666894](https://github.com/Hisery123/st-deconvolution-research/commit/5666894905eb7e49d83158fbbcaf88e92ed8a03c), 62 files were imported from historical Windows folders (14 Python scripts, 46 CSV tables, 2 READMEs). They are **source snapshots, not a complete reproducible environment or a new experiment**.

- [CTW-RF historical source snapshot](CTW-RF/source-snapshot/README.md)
- [CARR-lite V2 historical source snapshot](CARR-lite-V2/source-snapshot/README.md)
- [First source audit: code evidence, leakage and selection risks](SOURCE_AUDIT_2026-11-21.md)

## Project memory / handoff

Read in this order when resuming with ChatGPT or Claude:

1. [AGENTS.md](AGENTS.md) — long-term integrity and manual-research rules
2. [PROJECT_STATE.md](PROJECT_STATE.md) — latest verified/unverified project status and immediate priorities
3. [RESEARCH_JOURNAL/2026-11-21.md](RESEARCH_JOURNAL/2026-11-21.md) — dated decisions, evidence and unresolved issues
4. [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md) — evidence grades, manuscript claims and source fingerprints
5. The relevant project's EXPERIMENT_PLAN.md — tasks, checks and stop/go gates

## Scope and limitations

- This public repository contains **governance/planning documents plus partial historical script and CSV source snapshots**. No complete reproducible environment, independent recomputation or checked-in manuscript drafts are established.
- Do not confuse reported manuscript values with independently reproduced results.
- A spot, FOV, slice, donor and random seed are different levels of observation. Statistical inference must respect the independent unit.
- Real DLPFC Visium spots lack ground-truth cell-type composition here; pseudo-spot calibration errors are **not** real-spot errors.
- Never upload passwords, tokens, personal information, protected third-party data, or unpublished materials without authorization.
- Use Git commits, experiment records and raw result files as the source of truth; AI-generated summaries remain secondary.

## Collaboration

The researcher runs experiments manually on Windows; ChatGPT/Claude review protocols, scripts, logs, CSV, evidence strength and manuscript claims. No remote execution on the local computer is presumed.

For historical manuscript source versions and the issues awaiting proof, see [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md).
