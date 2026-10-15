# Elkinematics Chat and Session Ledger

This ledger tracks sessions, architectural decisions, new insights, sub-agent task delegations, and progressive milestones for the Elkinematics project (Dysgraphia / Dyslexia Kinematic Screening System and JISEBI Academic Publication).

All conversations, turns, tool calls, and token metrics are also automatically captured into SQLite database (`agents/logs/ledger.db`) and stream JSONL (`agents/logs/<session_id>.jsonl`) via Antigravity lifecycle hooks (`.agents/hooks.json` -> `agents/sync_transcript.py`).

---

## Centralized Database Ledger (Automated Observability)

- **Database Path:** [`agents/logs/ledger.db`](file:///Users/asthiseta/Project/somethinginmyeye/agents/logs/ledger.db)
- **Engine Module:** [`agents/chat_ledger.py`](file:///Users/asthiseta/Project/somethinginmyeye/agents/chat_ledger.py)
- **Syncer Script:** [`agents/sync_transcript.py`](file:///Users/asthiseta/Project/somethinginmyeye/agents/sync_transcript.py)
- **Lifecycle Hook:** [`.agents/hooks.json`](file:///Users/asthiseta/Project/somethinginmyeye/.agents/hooks.json) (Auto-triggers on `PostInvocation` and `Stop`)
- **Tables:** `sessions`, `turns`, `tool_executions`
- **Current Active Conversation ID:** `052b92b0-3957-419c-9e58-c305ffde297b`

---

## Active Sub-Agents Fleet

| Sub-Agent Name | Role | Core Competencies | Status |
| :--- | :--- | :--- | :--- |
| **`ml-coder`** | ML and Software Engineer | Model architectures (BiLSTM, TimeDistributed, CNN), feature engineering (8 standard kinematic features), statistical validation, data preprocessing, web canvas / Flask API. | **Active and Available** |
| **`academic-writer`** | Academic and Scientific Writer | Manuscript drafting (JISEBI 2024 / IEEE), IMRaD structuring, literature synthesis, research gap framing, discussion of empirical findings. | **Active and Available** |
| **`research`** | Literature and Web Researcher | Exploring papers, checking citations, retrieving academic benchmarks and clinical background. | **Built-in** |

---

## Session History and Logs

### Session: 2026-10-15 (Reactivation and Sub-Agent Orchestration)
- **Status:** In Progress
- **Primary Goal:** Reactivate project workflow, establish chat ledger, integrate user's new insights, and configure specialized sub-agents for coding and writing.
- **Key Milestones:**
  - [x] Defined and registered `ml-coder` sub-agent for implementation and ML engineering.
  - [x] Defined and registered `academic-writer` sub-agent for scientific publication and JISEBI drafting.
  - [x] Initialized automated Centralized Chat Ledger (`agents/logs/ledger.db` + lifecycle hooks).
  - [x] Consolidated all 38 academic literature PDFs into root `academic_resources/` directory.
  - [x] Created `archive/` folder; archived `evaluation_results/`, `evaluation_results_kfold/`, and stripped notebook `archive/notebooks/somethinginmyeye.ipynb`.
  - [x] Centralized all configurations and hyperparameters into `scripts/config.py`.
  - [x] Centralized all model architectures (V0, V1, V2 Bi-LSTM) into `scripts/model_builder.py`.
  - [x] Created the single main research and experimentation notebook `playground.ipynb`.
  - [x] Persisted project-wide engineering and academic guidelines into `AGENTS.md`.
  - [x] Enforced zero-emoji and clean technical terminology invariants (no informal jargons).

#### Architectural Upgrades and Insights Log
- *Workspace Architecture:* Single central notebook `playground.ipynb` acts as staging/sandbox before converting code to `.py` scripts.
- *Model Centralization:* `scripts/model_builder.py` is the single source of truth for neural network architecture definitions; prevents divergent training/evaluation/inference models.
- *Hyperparameter Centralization:* All paths, sequence limits (`MAX_TIMESTEPS=500`), dimensions (`FEATURES=8`), and training parameters (`BATCH_SIZE=32`, `EPOCHS=50`, `LEARNING_RATE=1e-3`) are centralized in `scripts/config.py`.
- *Literature Centralization:* Single unified folder `academic_resources/` for 38 research PDFs.
- *Style Invariant:* Strict zero-emoji policy across all artifacts, code comments, and chat responses; no informal jargons like "Golden features".

#### Sub-Agent Task Delegations
| Task ID | Assignee | Task Description | Status | Output / Artifact |
| :--- | :--- | :--- | :--- | :--- |
| — | — | — | — | — |

---

## Ongoing Workstreams Overview

### 1. Coding and Machine Learning (`ml-coder`)
- Current Model: Bidirectional LSTM on 8 standard kinematic features.
- Pending Upgrades:
  - Time-Distributed Heatmap / token-level risk assessment.
  - Statistical hypothesis testing (T-Test / Mann-Whitney U) on kinematic features between Normal vs Dyslexia cohorts.
  - Dual-Stream / Two-Headed exploratory design (kinematics + spatial stroke form).

### 2. Academic Writing and Publication (`academic-writer`)
- Target Venue: **JISEBI 2024** (Journal of Information Systems Engineering and Business Intelligence).
- Manuscript Working Title: *Prototyping an Early Dysgraphia Screening System Using Explainable AI Approach Through Handwriting Kinematics*.
- Target Length: 3,000–6,000 words; minimum 20 IEEE citations; structured IMRaD.
- Current Working Drafts: `mdartifacts/journal_outline.md`, `elkinematic-journal/`.

---

## Ledger Maintenance Rules
1. **At the start of every session/discussion:** Append a session block with the date, current focus, and new insights.
2. **When sub-agents complete a task:** Record the task ID, sub-agent name, summary of changes, and output files.
3. **When key decisions are reached:** Summarize the rationale and impact on either the code or the manuscript.
