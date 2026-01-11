# ✅ R-LAM PROJECT + PAPER CHECKLIST (AUTHORITATIVE)

---

## PHASE 0 — Ground Rules (DO THIS FIRST)

### - [ ] Decide the scope (lock it)

**WHAT:** Define what R-LAM is *not*
**WHY:** Prevents scope creep and reviewer suspicion
**HOW:** Write this in README and Section 6:

> "R-LAM is a lightweight research artifact, not a full workflow engine."

---

### - [ ] Freeze terminology

**WHAT:** Decide exact meanings of:

* action
* replay
* fork
* execution trace
* rerun
  **WHY:** Inconsistency = reviewer confusion
  **HOW:**
* Define once in Section 5
* Use the same words everywhere (paper + code + figures)

---

## PHASE 1 — Project Setup (FOUNDATION)

### - [x] Create repository

**WHAT:** Create GitHub repo `rlam`
**WHY:** Artifact credibility
**HOW:**

```bash
mkdir rlam && cd rlam
git init
```

---

### - [x] Create directory structure

**WHAT:** Minimal but complete layout
**WHY:** Reviewers judge structure silently
**HOW:**

```text
rlam/
├── rlam/
├── examples/
├── tests/
├── pyproject.toml
├── README.md
├── LICENSE
```

---

### - [x] Lock Python version

**WHAT:** Python ≥ 3.10
**WHY:** Deterministic typing & Pydantic
**HOW:** Mention in README + Section 6

---

### - [x] Configure packaging

**WHAT:** `pyproject.toml`
**WHY:** PyPI + reproducibility
**HOW:** Use the exact file I gave earlier

---

### - [x] Add license

**WHAT:** MIT
**WHY:** IEEE + artifact norms
**HOW:** Copy standard MIT license

---

## PHASE 2 — CORE FRAMEWORK IMPLEMENTATION (SECTION V)

---

### - [x] Implement Action schema

**WHAT:** Immutable Action object
**WHY:** Smallest reproducible unit
**HOW:**

* Pydantic model
* Fields: id, type, inputs, parameters, env hash, timestamp
* No mutation after creation

📌 Paper mapping: **Section 5.1**

---

### - [x] Implement environment hashing

**WHAT:** Capture execution context
**WHY:** Determinism + auditability
**HOW:**

* Python version
* OS
* library versions
* Hash into `environment_hash`

---

### - [x] Implement deterministic executor

**WHAT:** Pure execution function
**WHY:** Separate reasoning from execution
**HOW:**

* No retries
* No fallback
* Catch and log all errors

📌 Paper mapping: **Section 5.2**

---

### - [x] Implement execution trace store

**WHAT:** DAG of executed actions
**WHY:** Provenance backbone
**HOW:**

* Nodes = actions
* Edges = data/control dependencies
* Store outputs, status, errors

📌 Paper mapping: **Section 5.3**

---

### - [x] Enforce invariant

**WHAT:** Logged-only execution
**WHY:** Scientific auditability
**HOW:**

* Hard rule in code & paper:

> "An action that is not logged is treated as non-existent."

---

### - [x] Implement replay mechanism

**WHAT:** Output reuse
**WHY:** Prevent nondeterminism
**HOW:**

* No re-execution
* Load output from trace

📌 Paper mapping: **Section 5.4**

---

### - [x] Implement fork mechanism

**WHAT:** Controlled divergence
**WHY:** Scientific experimentation
**HOW:**

* Copy trace prefix
* Modify parameters
* Append new actions

📌 Paper mapping: **Section 5.4**

---

### - [x] Implement failure handling

**WHAT:** Failure as first-class node
**WHY:** Avoid silent corruption
**HOW:**

* Failed actions remain in DAG
* Recovery actions link explicitly

📌 Paper mapping: **Section 5.5**

---

## PHASE 3 — EXAMPLE WORKFLOWS (FOR SECTION VII)

---

### - [x] Example 1: Linear success workflow

**WHAT:** A1 → A2 → A3
**WHY:** Baseline reproducibility
**HOW:**

* Load → preprocess → train
* All SUCCESS

---

### - [ ] Example 2: Failure + recovery

**WHAT:** Failure propagation
**WHY:** Show trace completeness
**HOW:**

* Force A3 failure
* Add recovery action

---

### - [ ] Example 3: Hyperparameter fork

**WHAT:** Replay + fork
**WHY:** Core novelty
**HOW:**

* Reuse A1, A2
* Modify A3 parameters
* Compare outputs

---

## PHASE 4 — EXPERIMENTS (SECTION VII)

---

### - [ ] Define evaluation questions

**WHAT:** What are you proving?
**WHY:** Prevent "toy demo" criticism
**HOW:**

* Does replay preserve outputs?
* Does fork isolate changes?
* Are failures auditable?

---

### - [ ] Define metrics

**WHAT:** Simple, honest metrics
**WHY:** IEEE reviewers expect structure
**HOW:**

* Reproducibility success (binary)
* Trace completeness
* Failure visibility

---

### - [ ] Baseline comparison

**WHAT:** Naive LLM execution
**WHY:** "Compared to what?"
**HOW:**

* Execute without trace
* Show missing provenance

---

### - [ ] Run experiments

**WHAT:** Collect outputs
**WHY:** Evidence
**HOW:**

* Log traces
* Save results as tables

---

### - [ ] Write Section VII

**WHAT:** Experimental Evaluation
**WHY:** Non-negotiable
**HOW:**

* Setup
* Workflows
* Results
* Discussion

---

## PHASE 5 — DIAGRAMS (REVIEWER VISUALS)

---

### - [ ] Figure 1: Architecture Overview

**WHY:** Orientation
**WHERE:** Start of Section 5

---

### - [ ] Figure 2: Execution Trace DAG

**WHY:** Reproducibility proof
**WHERE:** Section 5.3

---

### - [ ] Figure 3: Replay & Forking

**WHY:** Novelty signal
**WHERE:** Section 5.4

---

## PHASE 6 — PAPER SANITY CHECK

---

### - [ ] Claims match evidence

**WHAT:** No overclaims
**WHY:** Reviewer trust
**HOW:** Replace "significant" → "improves"

---

### - [ ] Terminology consistency

**WHAT:** Replay ≠ rerun
**WHY:** Avoid rejection
**HOW:** Search & replace carefully

---

### - [ ] Ethics section present

**WHAT:** Section 8
**WHY:** Mandatory
**HOW:** Already done ✔

---

### - [ ] Artifact mentioned

**WHAT:** PyPI + repo
**WHY:** Credibility
**HOW:** Section 6

---

## PHASE 7 — SUBMISSION READINESS

---

### - [ ] PDF length ≤ IEEE limit

### - [ ] Figures readable in 2-column

### - [ ] Anonymous references

### - [ ] No institution leaks