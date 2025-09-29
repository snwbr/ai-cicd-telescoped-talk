# ci/run_selected_tests.py
import json, os, subprocess, sys

def main():
    env = os.environ.copy()
    env['PYTHONPATH'] = env.get('PYTHONPATH', os.getcwd())

    tests = []
    if os.path.exists('files/selected_tests.json'):
        data = json.load(open('files/selected_tests.json'))
        tests = data.get('selected_tests', [])

    if not tests:
        msg = "No tests selected (no app/ changes). Skipping pytest."
        print(msg)
        # Dejar un reporte mínimo opcional para herramientas que esperan XML
        with open('files/report.xml', 'w') as f:
            f.write('<testsuite name="skip" tests="0" failures="0" errors="0"></testsuite>')
        with open('files/pytest_output.log', 'w') as f:
            f.write(msg + '\n')
        sys.exit(0)

    fail_fast = os.getenv('FAIL_FAST') == '1'
    args = ['pytest'] + tests + ['-q', '--junitxml', 'files/report.xml']
    if fail_fast: args.append('-x')

    print('Running:', ' '.join(args))
    proc = subprocess.run(args, text=True, capture_output=True, env=env)
    print(proc.stdout)
    print(proc.stderr, file=sys.stderr)

    with open('files/pytest_output.log', 'w') as f:
        f.write(proc.stdout)
        f.write('\n--- STDERR ---\n')
        f.write(proc.stderr)

    sys.exit(proc.returncode)

if __name__ == '__main__':
    main()
