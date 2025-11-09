import json
import os
import random
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

# Synthetic historical dataset generator
random.seed(42)
np.random.seed(42)

FILES = ['app/login.py', 'app/payment.py', 'app/ui.py']
TESTS = ['tests/test_login.py', 'tests/test_payment.py', 'tests/test_ui.py']

def make_example(n=20000):
    rows = []
    for i in range(n):
        # random subset of changed files
        k = np.random.choice([1, 2, 3], p=[0.6, 0.3, 0.1])
        changed = sorted(np.random.choice(FILES, size=k, replace=False).tolist())
        # label: which test failed (primary failure)
        # induce correlations with indirect dependencies:
        # Model learns that file changes can affect multiple related tests
        
        failed = None
        
        # Simulate indirect dependencies FIRST (before direct correlations)
        # This teaches the model that single file changes can affect related tests
        # UI and Login are often related (UI forms, authentication interfaces, etc.)
        if 'app/ui.py' in changed and len(changed) == 1:
            if random.random() < 0.25:  # 25% chance of indirect effect
                # ui.py alone → sometimes login fails (UI changes affect login forms)
                failed = 'tests/test_login.py'
        
        if not failed and 'app/login.py' in changed and len(changed) == 1:
            if random.random() < 0.20:  # 20% chance
                # login.py alone → sometimes ui fails (login logic affects UI components)
                failed = 'tests/test_ui.py'
        
        # Direct correlations (primary failure) - only if no indirect dependency
        if not failed:
            if 'app/payment.py' in changed and random.random() < 0.55:
                failed = 'tests/test_payment.py'
            elif 'app/login.py' in changed and random.random() < 0.45:
                failed = 'tests/test_login.py'
            elif 'app/ui.py' in changed and random.random() < 0.35:
                failed = 'tests/test_ui.py'
            else:
                # sometimes nothing fails (ok build); mark "none"
                failed = 'none' if random.random() < 0.35 else random.choice(TESTS)

        commit_msg_len = np.random.randint(10, 120)
        weekday = np.random.randint(0, 7)

        rows.append({
            'changed_files': ','.join(changed),
            'commit_msg_len': commit_msg_len,
            'weekday': weekday,
            'failed_test': failed
        })
    return pd.DataFrame(rows)

def featurize(df):
    # one-hot for files + numeric features
    X_files = pd.DataFrame({f'file_{f}': df['changed_files'].apply(lambda s: int(f in s.split(','))) for f in FILES})
    X = pd.concat([
        X_files,
        df[['commit_msg_len', 'weekday']].astype(int)
    ], axis=1)
    return X

def main(model_path='files/model_rf.pkl', mapping_path='files/test_index.json'):
    df = make_example()
    # keep 'none' as a class to learn "likely no failures"
    y = df['failed_test']

    X = featurize(df)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=7, stratify=y)

    clf = RandomForestClassifier(
        n_estimators=500,
        max_depth=10,
        class_weight="balanced",
        min_samples_leaf=1,
        random_state=7,
        n_jobs=-1
    )
    clf.fit(X_train, y_train)

    y_pred = clf.predict(X_test)
    report = classification_report(y_test, y_pred, digits=3)
    print("=== Model Report ===")
    print(report)

    joblib.dump(clf, model_path)

    # Save mapping/meta if needed
    meta = {
        'files': FILES,
        'tests': TESTS
    }
    with open(mapping_path, 'w') as f:
        json.dump(meta, f, indent=2)

    print(f"Saved model to {model_path}")
    print(f"Saved mapping to {mapping_path}")

if __name__ == '__main__':
    model_path = os.getenv('MODEL_PATH', 'files/model_rf.pkl')
    main(model_path=model_path)
