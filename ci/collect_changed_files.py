# ci/collect_changed_files.py
import json, os, subprocess, sys, pathlib

APP_PREFIX = "app/"

def git_diff_files():
    try:
        base = os.getenv('DIFF_BASE', 'origin/main')
        subprocess.run(['git', 'fetch', 'origin', 'main'], check=False,
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        res = subprocess.run(['git', 'diff', '--name-only', f'{base}...HEAD'],
                             check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        files = [l.strip() for l in res.stdout.splitlines() if l.strip()]
        return files
    except Exception:
        return []

def main():
    changed = git_diff_files()
    # Permitir override manual
    env = os.getenv('CHANGED_FILES')
    if env:
        changed = [s.strip() for s in env.split(',') if s.strip()]

    # Filtrar SOLO archivos del app/
    changed_app = [f for f in changed if f.startswith(APP_PREFIX)]

    print("Changed files (all):", changed)
    print("Changed files (app/ only):", changed_app)

    with open('files/changed_files.json', 'w') as f:
        json.dump(changed_app, f, indent=2)

if __name__ == '__main__':
    main()
