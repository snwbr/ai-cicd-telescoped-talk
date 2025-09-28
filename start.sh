#!/bin/bash
# Descomentar para debug
# set -x

python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 1) Entrenar el modelo (RF)
python3 ml/train_test_selector.py

# 2) Simular archivos cambiados y predecir tests
#CHANGED_FILES="app/login.py,app/payment.py" python3 ml/predict_tests.py
# o si no se quiere simular cambios, se puede usar el script de collect_changed_files.py
python ci/collect_changed_files.py

# 3) Forzar fallo de demo (opcional para ver diagnóstico)
export BREAK_PAYMENT=$1

# 4) Ejecutar tests seleccionados y guardar logs
python3 ci/run_selected_tests.py

# 5) Diagnóstico con LLM (si tienes OPENAI_API_KEY) o fallback por reglas
#export OPENAI_API_KEY=<openai_api_key>
python3 ci/diagnose_failure_llm.py
