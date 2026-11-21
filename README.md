# Spatial Transcriptomics Deconvolution Research

Reproducible research and **evidence-driven extension planning** for two separate spatial transcriptomics deconvolution studies: **CTW-RF** and **CARR-lite V2**.

> Current stage (2026-11-21): repository initialization and source-code/experiment audit. Manuscript-reported numbers have **not** been independently recomputed in this repository. No new scientific experiment was run during initialization.

## Projects

| Project | Scope | Current priority |
|---|---|---|
| [CTW-RF](CTW-RF/EXPERIMENT_PLAN.md) | Cell-type-wise reliability fusion of existing deconvolution predictions | Audit pseudo-spot/reference cell overlap; out-of-fold evaluation; compare nearest ensemble baselines |
| [CARR-lite V2](CARR-lite-V2/EXPERIMENT_PLAN.md) | Rare-cell-aware post-calibration on a Tangram base model | Audit feature availability and FOV/reference split; then test alternative base deconvolvers |

## Project memory / handoff

Read in this order when resuming with ChatGPT or Claude:

1. [AGENTS.md](AGENTS.md) — long-term integrity and manual-research rules
2. [PROJECT_STATE.md](PROJECT_STATE.md) — latest verified/unverified project status and immediate priorities
3. [RESEARCH_JOURNAL/2026-11-21.md](RESEARCH_JOURNAL/2026-11-21.md) — dated decisions, evidence and unresolved issues
4. [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md) — evidence grades, manuscript claims and source fingerprints
5. The relevant project's EXPERIMENT_PLAN.md — tasks, checks and stop/go gates

## Scope and limitations

- This public repository currently contains **governance and experimental planning documents**, not published raw data, verified reproduction scripts or checked-in manuscript drafts.
- Do not confuse reported manuscript values with independently reproduced results.
- A spot, FOV, slice, donor and random seed are different levels of observation. Statistical inference must respect the independent unit.
- Real DLPFC Visium spots lack ground-truth cell-type composition here; pseudo-spot calibration errors are **not** real-spot errors.
- Never upload passwords, tokens, personal information, protected third-party data, or unpublished materials without authorization.
- Use Git commits, experiment records and raw result files as the source of truth; AI-generated summaries remain secondary.

## Collaboration

The researcher runs experiments manually on Windows; ChatGPT/Claude review protocols, scripts, logs, CSV, evidence strength and manuscript claims. No remote execution on the local computer is presumed.

For historical manuscript source versions and the issues awaiting proof, see [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md).
