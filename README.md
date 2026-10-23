# AI-2: AI Backend Engineering

Build AI-powered pipelines in Python. Extract structure from unstructured inputs, work with embeddings and vector databases, and implement retrieval-augmented generation (RAG) to improve model output.

## First-Time Setup

1. **Clone this repo** using GitHub Desktop (URL provided in class)
2. **Open the folder** in VS Code (`File` → `Open Folder` → select `odsa-ai-backend`)
3. **Open the setup notebook:** `notebooks/session_0_1_setup.ipynb`
4. **Follow it step by step** — it will install everything and verify your environment

The setup notebook walks you through installing `uv`, Python, dependencies, selecting your kernel, and creating your workspace. Every step has a verification check — all should show **PASS** before you move on.

## Before Each Class

```
1. Open GitHub Desktop → Fetch origin → Pull
2. Copy the new session notebook from notebooks/ into my_work/
3. Open the copy from my_work/ and work there
```

**Why `my_work/`?** This folder is git-ignored. When the instructor pushes updates, `git pull` updates the master copies in `notebooks/` without touching your work. No merge conflicts, no lost progress.

## Project Structure

```
odsa-ai-backend/
├── notebooks/           ← Master copies (don't edit these directly)
│   ├── session_0_1_setup.ipynb
│   ├── session_1_1.ipynb
│   └── ...
│
├── my_work/             ← YOUR workspace (git-ignored, safe from updates)
│   ├── session_1_1.ipynb
│   └── ...
│
├── src/                 ← Pre-built pipeline modules (provided to you)
│   ├── s0_generation/   ← Session 1.1: API integration
│   ├── s1_extraction/   ← Session 1.2: Batch processing
│   ├── s2_embeddings/   ← Session 2.1: Embeddings
│   ├── s3_ingestion/    ← Session 2.2: Vector ingestion
│   ├── s4_retrieval/    ← Sessions 3.1–3.2: RAG
│   └── s5_observability/← Session 4.1: Logging
│
├── data/                ← Course dataset
├── pyproject.toml       ← Dependencies (uv reads this)
├── .env.example         ← API key template
└── .gitignore           ← Keeps .env, .venv/, my_work/ out of git
```

## Sessions

| Week | Session | Topic |
|------|---------|-------|
| 1 | 1.1 | LLM API Integration |
| 1 | 1.2 | Batch Processing & Extraction |
| 2 | 2.1 | Embeddings & Model Selection |
| 2 | 2.2 | Chunking & Vector Ingestion |
| 3 | 3.1 | Naive RAG |
| 3 | 3.2 | Metadata-Aware RAG |
| 4 | 4.1 | Observability & Debugging |
| 4 | 4.2 | Module Test |

## Grading

| Component | Weight |
|-----------|--------|
| Lab 1 — Batch Extraction | 20% |
| Lab 2 — RAG Evaluation | 20% |
| Written Exam | 50% |
| Participation | 10% |
| **Passing** | **70% or above** |

## Troubleshooting

| Problem | Fix |
|---------|-----|
| `uv` not found | Close and reopen your terminal after installing uv |
| Kernel not listed in VS Code | `Cmd/Ctrl+Shift+P` → "Reload Window", then reselect kernel |
| "Module not found" error | Make sure your kernel is set to `.venv`, not system Python |
| `AuthenticationError` | Check `.env` is in the project root and key starts with `sk-ant-` |
| Packages missing after `uv sync` | Reload VS Code window, then re-run the package check cell |
| Cells error after reloading VS Code | Normal — reload clears variables. Run cells from the top again |
| `git pull` has conflicts | You may have edited a file in `notebooks/`. Work in `my_work/` instead |

## Need Help?

- Re-run `notebooks/session_0_1_setup.ipynb` to diagnose environment issues
- Check the troubleshooting table above
- Ask in class or during office hours

## Secrets

1Password (account `tkhllc`) is the source of truth. This repo reads the `homelab-ai` and `homelab-apps` vaults via `op://` references in `.env.tpl`.
Convention: homelab-main `docs/security/secrets-management-1password.md`.

- Local dev: `op inject -i .env.tpl -o .env` (`.env` is gitignored; never commit it).
- One-offs: `op run --env-file .env.tpl -- <cmd>`.
- Never hand-write a secret value into `.env`, code, docs or chat. Create the 1Password item first, then reference it in `.env.tpl`.
- On homelab hosts the `op-render` manifest owns the rendered file.
- Before committing: `just check-secrets` (gitleaks).
