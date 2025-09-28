import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

DEFAULT_MODEL = os.getenv('MODEL_PATH', 'model_rf.pkl')
MAPPING_PATH = 'test_index.json'

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

def decide_tests(changed_files, min_tests=1, top_k=2):
    model = joblib.load(DEFAULT_MODEL)
    df = featurize_row(changed_files)
    # predict proba for classes
    proba = model.predict_proba(df)[0]
    classes = model.classes_
    scored = sorted(zip(classes, proba), key=lambda x: x[1], reverse=True)

    # classes may include 'none' meaning "likely no failures"
    tests = [c for c,_ in scored if c != 'none'][:max(top_k, min_tests)]
    # if none of the known tests are triggered, fall back to a minimal smoke test set
    if not tests:
        tests = ['tests/test_login.py']

    return tests, scored

def main():
    changed_env = os.getenv('CHANGED_FILES')
    if changed_env:
        changed = [s.strip() for s in changed_env.split(',') if s.strip()]
    else:
        # try to read from artifact of collect_changed_files.py
        if os.path.exists('changed_files.json'):
            changed = json.load(open('changed_files.json'))
        else:
            changed = ['app/login.py']

    tests, scored = decide_tests(changed, min_tests=int(os.getenv('MIN_TESTS', '1')))

    decision = {
        'changed_files': changed,
        'selected_tests': tests,
        'class_probs': [{ 'label': c, 'prob': float(p)} for c,p in scored]
    }
    print("=== AI Test Selection ===")
    print(json.dumps(decision, indent=2))

    with open('selected_tests.json', 'w') as f:
        json.dump(decision, f, indent=2)

if __name__ == '__main__':
    main()
