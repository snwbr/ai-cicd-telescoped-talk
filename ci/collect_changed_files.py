# ci/collect_changed_files.py
import json, os, subprocess, sys, pathlib

APP_PREFIX = "app/"

def sh(cmd):
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def safe_sh(cmd):
    return subprocess.run(cmd, check=False, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

def get_changed_files():
    event_name = os.getenv("GITHUB_EVENT_NAME", "")
    event_path = os.getenv("GITHUB_EVENT_PATH", "")
    head = os.getenv("GITHUB_SHA", "").strip()
    changed = []

    # Trae refs remotas por si el checkout fue shallow
    safe_sh(["git", "fetch", "--no-tags", "--prune", "--depth=1000", "origin", "+refs/heads/*:refs/remotes/origin/*"])

    def diff_names(a, b):
        r = safe_sh(["git", "diff", "--name-only", f"{a}..{b}"])
        return [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]

    # 1) pull_request: compara base.sha vs HEAD
    if event_name == "pull_request" and event_path and os.path.exists(event_path):
        import json as _json
        ev = _json.load(open(event_path))
        base_sha = ev.get("pull_request", {}).get("base", {}).get("sha", "")
        if not base_sha:
            # fallback a la rama base
            base_ref = os.getenv("GITHUB_BASE_REF", "")
            if base_ref:
                base_sha = safe_sh(["git", "rev-parse", f"origin/{base_ref}"]).stdout.strip()
        if base_sha:
            changed = diff_names(base_sha, head)
            if changed:
                return changed

    # 2) push: usa el SHA anterior del evento
    before = os.getenv("GITHUB_EVENT_BEFORE", os.getenv("BEFORE_SHA", "")).strip()
    if not before and event_path and os.path.exists(event_path):
        import json as _json
        ev = _json.load(open(event_path))
        before = ev.get("before", "") or ev.get("commits", [{}])[0].get("id", "")

    # Caso “initial push” (before == 0000…)
    if before and set(before) == {"0"}:
        # compara contra árbol vacío
        r = safe_sh(["git", "ls-tree", "--name-only", "-r", head])
        changed = [ln.strip() for ln in r.stdout.splitlines() if ln.strip()]
        return changed

    if before:
        changed = diff_names(before, head)
        if changed:
            return changed

    # 3) Fallback general: último commit vs su padre
    r = safe_sh(["git", "rev-parse", "HEAD~1"])
    if r.returncode == 0:
        parent = r.stdout.strip()
        changed = diff_names(parent, head)
        if changed:
            return changed

    # 4) Último recurso: nada
    return []

def main():
    # Permitir override manual
    env = os.getenv('CHANGED_FILES')
    if env:
        changed = [s.strip() for s in env.split(',') if s.strip()]
    else:
        changed = get_changed_files()

    print("Changed files (all):", changed)
    changed_app = [f for f in changed if f.startswith(APP_PREFIX)]
    print("Changed files (app/ only):", changed_app)

    with open('files/changed_files.json', 'w') as f:
        json.dump(changed_app, f, indent=2)

if __name__ == '__main__':
    main()
