import json
import os
import subprocess

def git_diff_files():
    try:
        # Compare with origin/main if available; otherwise with previous commit
        base = os.getenv('DIFF_BASE', 'origin/main')
        res = subprocess.run(['git', 'fetch', 'origin', 'main'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        res = subprocess.run(['git', 'diff', '--name-only', f'{base}...HEAD'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        files = [line.strip() for line in res.stdout.splitlines() if line.strip()]
        return files
    except Exception:
        return []

def main():
    changed = git_diff_files()
    print("Changed files:", changed)
    if not changed:
        # Fallback to env or a sensible default for demo
        env = os.getenv('CHANGED_FILES')
        if env:
            changed = [s.strip() for s in env.split(',') if s.strip()]
        else:
            changed = ['app/login.py', 'app/payment.py']

    print("Changed files:", changed)
    with open('changed_files.json', 'w') as f:
        json.dump(changed, f, indent=2)

if __name__ == '__main__':
    main()
