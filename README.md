# AI in DevOps Demo — Test Selection (ML) + Failure Diagnosis (LLM)

This repo contains two concrete demos you can run locally or in GitHub Actions:

1) **Option 1 — ML Test Selector (scikit-learn)**
   - Trains a model on synthetic historical data to predict *which tests are likely to fail* given changed files.
   - Uses those predictions to select a **minimal set of tests** to run in CI.

2) **Option 3 — LLM Failure Diagnosis**
   - If tests fail, captures logs and (optionally) calls a **LLM** (OpenAI API or compatible) to explain the likely root cause and next steps.
   - If no API key is present, falls back to a smart rules-based summary so the pipeline still works.

---

## Project layout

```
ai-devops-demo/
├─ app/
│  ├─ login.py
│  ├─ payment.py
│  └─ ui.py
├─ ml/
│  ├─ train_test_selector.py
│  └─ predict_tests.py
├─ ci/
│  ├─ collect_changed_files.py
│  ├─ run_selected_tests.py
│  └─ diagnose_failure_llm.py
├─ tests/
│  ├─ test_login.py
│  ├─ test_payment.py
│  └─ test_ui.py
├─ .github/workflows/ci.yml
├─ requirements.txt
└─ README.md
```

---

## Quickstart (local)

```bash
python -m venv .venv && source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt

# 1) Train the ML model (synthetic data)
python ml/train_test_selector.py

# 2) Simulate changed files (or use Git) and predict which tests to run
#    You can pass CHANGED_FILES environment variable as a comma-separated list
CHANGED_FILES="app/login.py,app/payment.py" python ml/predict_tests.py

# 3) Run the selected tests and capture logs (exit code preserved)
python ci/run_selected_tests.py

# 4) If tests failed, run diagnosis (uses OpenAI if OPENAI_API_KEY is set)
python ci/diagnose_failure_llm.py
```

To force a failing test for demo purposes, set an env var before step 3:
```bash
export BREAK_PAYMENT=1
```

---

## GitHub Actions

The workflow **.github/workflows/ci.yml** does this:

1. Checkout
2. Install deps
3. Train ML model (cached)
4. Collect changed files
5. Predict tests (Option 1)
6. Run tests (continues on error so the job can still post diagnosis)
7. Diagnose failure with LLM (Option 3)
8. Upload artifacts (logs, reports, diagnosis)

> The job will succeed even if tests fail, so you can demo the diagnosis output in PR checks. Adjust to your taste.

---

## Configuration

- **CHANGED_FILES**: override detected changes, e.g. `CHANGED_FILES="app/login.py,app/ui.py"`
- **MIN_TESTS**: minimum number of tests to run even if predicted risk is low (default `1`).
- **FAIL_FAST**: `1` to stop pytest on first failure.
- **OPENAI_API_KEY**: enable LLM diagnosis (OpenAI-compatible). If not set, uses rule-based diagnosis.
- **MODEL_PATH**: path for the trained model (default `model_rf.pkl`).

---

## Notes

- The ML dataset is synthetic but structured to be realistic (files-to-tests signal + some noise).
- The LLM prompt is carefully designed to produce concise, actionable guidance.
- Replace the OpenAI client with your preferred provider if needed.
