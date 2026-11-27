# Spatial Transcriptomics Deconvolution Research

Reproducible research and **evidence-driven extension planning** for two separate spatial transcriptomics deconvolution studies: **CTW-RF** and **CARR-lite V2**.

> **Current stage (2026-11-27): Master's thesis writing and evidence-based synthesis.** The researcher reports that the planned CTW-RF and CARR-lite V2 supplementary experiments are complete; the repository's latest detailed execution records (2026-11-24) document CTW 24/24 original-baseline runs and CARR five held-out MERFISH sections. Final literature, statistics, and manuscript-format review remain outstanding. Archived 2026-11-21 initialization statements below are historical, not current status.

## Master's thesis writing — start here

The current goal is a rigorous, academically persuasive **master's thesis**, not a chronology of experiments or a top-journal-level new architecture. Internal evidence review stays strict; published-facing prose must emphasize **research questions, substantiated contributions, findings, limitations, and practical significance** without exaggeration or selective reporting.

- **[Academic writing & contribution framing rules](ACADEMIC_WRITING_AND_CONTRIBUTION_STANDARD.md)** — mandatory for ChatGPT/Claude; prohibits experiment-log prose and requires accurate method attribution and negative results
- **[Three-study master's thesis writing blueprint](MASTER_THESIS_WRITING_BLUEPRINT_20261127.md)** — proposed structure integrating CTW-RF, CARR-lite V2, and the independent [CellCharter study](https://github.com/Hisery123/st-clustering-research), without claiming an unperformed end-to-end pipeline
- **[AGENTS.md](AGENTS.md)** — long-term scientific integrity, assistant collaboration, and latest writing-first directive
- **[PROJECT_STATE.md](PROJECT_STATE.md)** — latest checkpoint with source-evidence boundaries
- **[2026-11-27 research journal](RESEARCH_JOURNAL/2026-11-27.md)** — decision to begin thesis writing

**Evidence status:** CTW-RF's held-out method-pool comparisons include unfavorable metrics/comparators; DLPFC real spots lack measured composition ground truth. CARR-lite V2 has an external-source MERFISH study but its five sections all come from **one animal**, not five biological replicates. Never write these as independent-subject validation or universal superiority.


## Archived experiment execution queue (historical 2026-11-21)

The following links document earlier experimental planning and are **not the current next-step queue**. Refer to `PROJECT_STATE.md` top and actual experiment records before running any script.

- [Experiment execution queue / current next steps](EXECUTION_QUEUE.md)
- [CTW-RF: 5-fold global stacking comparator](CTW-RF/experiments/global_stacking_cv.py)
- [CARR-lite V2: cross-method RCTD/CARD adapter](CARR-lite-V2/experiments/cross_method_carr_v2.py)

## Projects

| Project | Scope | Writing focus |
|---|---|---|
| [CTW-RF](CTW-RF/EXPERIMENT_PLAN.md) | Cell-type-wise reliability fusion of existing deconvolution predictions | Present the disjoint-cell-source six-method comparisons, heterogeneous method-pool gains, negative comparators, and real DLPFC application with distinct evidentiary status |
| [CARR-lite V2](CARR-lite-V2/EXPERIMENT_PLAN.md) | Rare-cell-aware post-calibration on a Tangram base model | Explain rare-cell detection versus abundance reconstruction objectives, seqFISH+ and MERFISH results, and domain/animal-independence limits |

## New source archive (2026-11-21)

On GitHub commit [5666894](https://github.com/Hisery123/st-deconvolution-research/commit/5666894905eb7e49d83158fbbcaf88e92ed8a03c), 62 files were imported from historical Windows folders (14 Python scripts, 46 CSV tables, 2 READMEs). They are **source snapshots, not a complete reproducible environment or a new experiment**.

- [CTW-RF historical source snapshot](CTW-RF/source-snapshot/README.md)
- [CARR-lite V2 historical source snapshot](CARR-lite-V2/source-snapshot/README.md)
- [First source audit: code evidence, leakage and selection risks](SOURCE_AUDIT_2026-11-21.md)

## Project memory / handoff

Read in this order when resuming with ChatGPT or Claude:

1. [AGENTS.md](AGENTS.md) — long-term integrity and manual-research rules
2. [PROJECT_STATE.md](PROJECT_STATE.md) — latest verified/unverified project status and immediate priorities
3. [RESEARCH_JOURNAL/2026-11-27.md](RESEARCH_JOURNAL/2026-11-27.md) — latest thesis-writing decision; follow linked 2026-11-24 experiment evidence
4. [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md) — evidence grades, manuscript claims and source fingerprints
5. [ACADEMIC_WRITING_AND_CONTRIBUTION_STANDARD.md](ACADEMIC_WRITING_AND_CONTRIBUTION_STANDARD.md) and [MASTER_THESIS_WRITING_BLUEPRINT_20261127.md](MASTER_THESIS_WRITING_BLUEPRINT_20261127.md) — writing requirements and structure;
6. The relevant project's EXPERIMENT_PLAN.md and current experimental records — never infer a planned task remains unfinished from an old plan

## Scope and limitations

- This public repository includes governance documents, historical script/CSV snapshots, and 2026-11-24 experiment completion records. **Availability of complete raw Windows outputs and full manuscript drafts must be verified before claiming they are archived here.**
- Do not confuse reported manuscript values with independently reproduced results.
- A spot, FOV, slice, donor and random seed are different levels of observation. Statistical inference must respect the independent unit.
- Real DLPFC Visium spots lack ground-truth cell-type composition here; pseudo-spot calibration errors are **not** real-spot errors.
- Never upload passwords, tokens, personal information, protected third-party data, or unpublished materials without authorization.
- Use Git commits, experiment records and raw result files as the source of truth; AI-generated summaries remain secondary.

## Collaboration

The researcher runs experiments manually on Windows; ChatGPT/Claude review protocols, scripts, logs, CSV, evidence strength and manuscript claims. No remote execution on the local computer is presumed.

For historical manuscript source versions and the issues awaiting proof, see [EVIDENCE_REGISTER.md](EVIDENCE_REGISTER.md).
