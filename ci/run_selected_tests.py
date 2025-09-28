import json, os, subprocess, sys

def main():
    tests = []
    env = os.environ.copy()
    env['PYTHONPATH'] = env.get('PYTHONPATH', os.getcwd())

    if os.path.exists('selected_tests.json'):
        data = json.load(open('selected_tests.json'))
        tests = data.get('selected_tests', [])
    if not tests:
        tests = ['tests/test_login.py']

    fail_fast = os.getenv('FAIL_FAST') == '1'
    args = ['pytest'] + tests + ['-q', '--junitxml', 'report.xml']
    if fail_fast:
        args.append('-x')

    print('Running:', ' '.join(args))
    proc = subprocess.run(args, text=True, capture_output=True, env=env)  # <— aquí
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)

    with open('pytest_output.log', 'w') as f:
        f.write(proc.stdout)
        f.write('\n--- STDERR ---\n')
        f.write(proc.stderr)

    sys.exit(proc.returncode)

if __name__ == '__main__':
    main()
