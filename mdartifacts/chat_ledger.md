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
- *Conference Pivot:* Transitioned focus to IEEE Conference submission (deadline: October 26, 2026) with enlarged scope covering Specific Learning Disorder (SLD) differential screening: Impairment in Reading (Dyslexia) vs Impairment in Written Expression (Motor Dysgraphia).
- *RAD 4th Iteration (V4 Dual-Stream SLD):*
  - Stream 1: Pretrained Bi-LSTM evaluating the 8 standard kinematic features for fine-motor instability (Motor Dysgraphia).
  - Stream 2: Hybrid stroke-visual trajectory heuristics identifying mirror reversals (b vs d, p vs q) and phonological edit distance (Dyslexia).
  - Stream 3: Cognitive initiation latency tracking working memory hesitation (> 1500 ms threshold).
  - Clinical Integrator: Mathematically formulated dual risk percentages aligned with DSM-5 diagnostic categories.
  - Modular Grammar Toggle: Architectural switch (`ENABLE_GRAMMAR_ANALYSIS`) for future sentence-level tasks.
- *Workspace Architecture:* Single central notebook `playground.ipynb` acts as staging/sandbox before converting code to `.py` scripts. Section 9 added for SLD differential screening.
- *Model Centralization:* `scripts/model_builder.py` is the single source of truth for neural network architecture definitions; prevents divergent training/evaluation/inference models.
- *Hyperparameter Centralization:* All paths, sequence limits (`MAX_TIMESTEPS=500`), dimensions (`FEATURES=8`), and training parameters (`BATCH_SIZE=32`, `EPOCHS=50`, `LEARNING_RATE=1e-3`) are centralized in `scripts/config.py`.
- *Literature Centralization:* Single unified folder `academic_resources/` for 38 research PDFs.
- *Style Invariant:* Strict zero-emoji policy across all artifacts, code comments, and chat responses; no informal jargons like "Golden features".
- *Kin-Coder Dumb Coder Architecture (Academic & Engineering Record):*
  - Paradigm: Transparent, non-neural spatial segmenter and topological glyph decoder designed for low-resource hardware (< 1 MB RAM, < 1 ms latency).
  - Rotation & Uphill Baseline Resilience: 2D Principal Component Alignment (PCA) deskewing calculates dominant trajectory axis and rotates coordinates into a canonical horizontal frame without coordinate reflection, preserving true mirror reversals ('b' vs 'd') regardless of tablet angle.
  - Spatial Topology over Chronology: Evaluates geometric bounding boxes, stem positions, loop centroids, and diagonal slopes rather than stroke timestamps, ensuring robustness against erratic, inverted, or switched stroke orders (e.g., 'N' vs inverted 'И', 'F' with leftward bars).
  - Spatial Gap Space Emission: Measures inter-cluster horizontal distance along the deskewed baseline to emit ASCII space `' '` tokens for sentence assembly.


#### Sub-Agent Task Delegations
| Task ID | Assignee | Task Description | Status | Output / Artifact |
| :--- | :--- | :--- | :--- | :--- |
| T01 | `ml-coder` | Implement `orthographic_decoder.py` for stroke reversals and spelling distance | **Completed** | [`scripts/orthographic_decoder.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/orthographic_decoder.py) |
| T02 | `ml-coder` | Implement `sld_integrator.py` combining kinematics, orthography, and latency | **Completed** | [`scripts/sld_integrator.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/sld_integrator.py) |
| T03 | `ml-coder` | Update `scripts/config.py` with SLD clinical thresholds and weights | **Completed** | [`scripts/config.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/config.py) |
| T04 | `ml-coder` | Update `server.py` and `screening.html` with dual-stream differential UI | **Completed** | [`scripts/server.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/server.py), [`data_collector/screening.html`](file:///Users/asthiseta/Project/somethinginmyeye/data_collector/screening.html) |
| T05 | `ml-coder` | Add Section 9 to `playground.ipynb` demonstrating SLD differential evaluation | **Completed** | [`playground.ipynb`](file:///Users/asthiseta/Project/somethinginmyeye/playground.ipynb) |
| T06 | `academic-writer` | Draft IEEE conference paper outline and full manuscript | **Completed** | [`le-conference-dyslexia/conference_outline.md`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/conference_outline.md), [`le-conference-dyslexia/conference_paper.md`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/conference_paper.md) |
| T07 | `academic-writer` | Compile IEEE conference paper into Word format (`.docx`) | **Completed** | [`scripts/build_conference_docx.py`](file:///Users/asthiseta/Project/somethinginmyeye/scripts/build_conference_docx.py), [`le-conference-dyslexia/elkinematics-conference.docx`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/elkinematics-conference.docx) |
| T08 | `ml-coder` | Integrate transparent Digital Ink stroke transcriber and decouple from inference | **Completed** | [`data_collector/screening.html`](file:///Users/asthiseta/Project/somethinginmyeye/data_collector/screening.html) |
| T09 | `ml-coder` | Calibrate NIV velocity inversion thresholds and eliminate UI jargon | **Completed** | [`data_collector/screening.html`](file:///Users/asthiseta/Project/somethinginmyeye/data_collector/screening.html), [`mdartifacts/things_we_learned_along_the_way.md`](file:///Users/asthiseta/Project/somethinginmyeye/mdartifacts/things_we_learned_along_the_way.md) |
| T10 | `ml-coder` | Implement fixed viewport and tactile on-screen tablet touch scrollbar | **Completed** | [`data_collector/screening.html`](file:///Users/asthiseta/Project/somethinginmyeye/data_collector/screening.html) |
| T11 | `ml-coder` | Implement horizontal reflection test, fix reciprocal pair false-positives, create roadmap | **Completed** | [`data_collector/screening.html`](file:///Users/asthiseta/Project/somethinginmyeye/data_collector/screening.html), [`mdartifacts/roadmap.md`](file:///Users/asthiseta/Project/somethinginmyeye/mdartifacts/roadmap.md) |

---


## Ongoing Workstreams Overview

### 1. Coding and Machine Learning (`ml-coder`)
- Current System: Dual-Stream SLD Differential Screening Framework (4th RAD Prototype).
- Completed Upgrades:
  - Kinematic stream: Bi-LSTM on the 8 standard kinematic features (`delta_x`, `delta_y`, `pressure`, `tiltX`, `tiltY`, `velocity`, `acceleration`, `jerk`).
  - Orthographic stream: Geometric stroke trajectory analysis for mirror reversals (b vs d, p vs q) and normalized Levenshtein distance.
  - Cognitive stream: Initiation latency tracking with clinical threshold at 1500 ms.
  - Server and Dashboard: Real-time dual risk indices (Dysgraphia Risk % and Dyslexia Risk %) with explainable heatmaps and reversal alerts.
  - Centralized Playground: `playground.ipynb` updated with Section 9.

### 2. Academic Writing and Publication (`academic-writer`)
- Target Venue: **IEEE Conference** (Submission deadline: October 26, 2026).
- Working Title: *Prototyping a Multi-Stream SLD Screening Framework: A Dual-Stream Kinematic-Orthographic System for Differential Screening of Dyslexia and Dysgraphia*.
- Manuscript Status:
  - Outline drafted: [`le-conference-dyslexia/conference_outline.md`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/conference_outline.md).
  - Full text completed: [`le-conference-dyslexia/conference_paper.md`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/conference_paper.md).
  - Word submission document compiled: [`le-conference-dyslexia/elkinematics-conference.docx`](file:///Users/asthiseta/Project/somethinginmyeye/le-conference-dyslexia/elkinematics-conference.docx).
- Word Count: ~4,200 words, strict IEEE 2-column formatting, 22 IEEE academic citations.

---

## Ledger Maintenance Rules
1. **At the start of every session/discussion:** Append a session block with the date, current focus, and new insights.
2. **When sub-agents complete a task:** Record the task ID, sub-agent name, summary of changes, and output files.
3. **When key decisions are reached:** Summarize the rationale and impact on either the code or the manuscript.

