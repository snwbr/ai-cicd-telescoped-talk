import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

DEFAULT_MODEL = os.getenv('MODEL_PATH', 'model_rf.pkl')
MAPPING_PATH = 'files/test_index.json'

def featurize_row(files, commit_msg_len=50, weekday=2):
    # align with training features
    training_meta = json.load(open(MAPPING_PATH))
    FILES = training_meta['files']

    row = {}
    for f in FILES:
        row[f'file_{f}'] = int(f in files)
    row['commit_msg_len'] = int(commit_msg_len)
    row['weekday'] = int(weekday)
    return pd.DataFrame([row])

# ml/predict_tests.py  (reemplaza decide_tests)
def decide_tests(changed_files, min_tests=1, top_k=None, prob_threshold=None):
    model = joblib.load(DEFAULT_MODEL)
    df = featurize_row(changed_files)
    proba = model.predict_proba(df)[0]
    classes = model.classes_

    scored = sorted(
        [(c, float(p)) for c, p in zip(classes, proba) if c != 'none'],
        key=lambda x: x[1], reverse=True
    )

    # Umbral opcional
    if prob_threshold is not None:
        picked = [c for c, p in scored if p >= prob_threshold]
    else:
        k = top_k if top_k is not None else 2
        picked = [c for c, _ in scored[:k]]

    if not picked:
        picked = [scored[0][0]] if scored else ['tests/test_login.py']
    return picked, scored


# ml/predict_tests.py (solo el main modificado)
def main():
    changed = []
    if os.path.exists('files/changed_files.json'):
        changed = json.load(open('files/changed_files.json'))
    else:
        env = os.getenv('CHANGED_FILES')
        if env:
            changed = [s.strip() for s in env.split(',') if s.strip()]
        # Si no hay archivo ni env ⇒ lista vacía

    # Si no hay cambios en app/, NO seleccionar tests
    if not changed:
        decision = {
            'changed_files': [],
            'selected_tests': [],
            'class_probs': [],
            'note': 'No app/ changes detected; skipping tests.'
        }
        print("=== AI Test Selection ===")
        print(json.dumps(decision, indent=2))
        with open('files/selected_tests.json', 'w') as f:
            json.dump(decision, f, indent=2)
        return

    tests, scored = decide_tests(
        changed,
        min_tests=int(os.getenv('MIN_TESTS', '1')),
        top_k=int(os.getenv('TOP_K', '2')) if os.getenv('TOP_K') else None,
        prob_threshold=float(os.getenv('PROB_THRESHOLD')) if os.getenv('PROB_THRESHOLD') else None
    )

    decision = {
        'changed_files': changed,
        'selected_tests': tests,
        'class_probs': [{'label': c, 'prob': float(p)} for c,p in scored]
    }
    print("=== AI Test Selection ===")
    print(json.dumps(decision, indent=2))
    with open('files/selected_tests.json', 'w') as f:
        json.dump(decision, f, indent=2)

if __name__ == '__main__':
    main()
