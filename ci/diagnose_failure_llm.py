import json
import os
import re
from pathlib import Path

def simple_rules_based_summary(log_text: str) -> str:
    lines = log_text.lower().splitlines()
    hints = []
    if 'assert' in log_text.lower():
        hints.append('- Parece un fallo de aserción: revisa la expectativa del test vs el cálculo real.')
    if 'importerror' in log_text.lower() or 'module not found' in log_text.lower():
        hints.append('- Error de importación: dependencia o ruta faltante.')
    if 'connection' in log_text.lower() and 'refused' in log_text.lower():
        hints.append('- Error de conexión: revisa variables de entorno y puertos abiertos.')
    if 'timeout' in log_text.lower():
        hints.append('- Timeout: prioriza retry/backoff o sube límites de tiempo.')
    # Look for our demo payment function
    if 'test_payment' in log_text.lower():
        hints.append('- Los fallos provienen de test_payment: revisa cálculo de descuentos en app/payment.py (posible bug intencional para demo).')
    return "\n".join(hints) if hints else "- No se detectaron patrones comunes; revisa el log y el diff del commit."

def make_prompt(log_text: str) -> str:
    return f"""You are a senior DevOps assistant. Read the following pytest log and produce a concise root-cause analysis and next steps.
- Keep it under 120 words.
- Bullet points preferred.
- If you see arithmetic mistakes in discounts, mention checking percentage math.

Pytest log:
{log_text[:8000]}
"""

def diagnose_with_llm(log_text: str) -> str:
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        return None
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        prompt = make_prompt(log_text)
        resp = client.chat.completions.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[
                { 'role': 'system', 'content': 'You are a concise DevOps incident diagnostician.'},
                { 'role': 'user', 'content': prompt}
            ],
            temperature=0.2,
            max_tokens=220
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"[LLM call failed, falling back to rules] {e}"

def junit_failures_errors(report_path: str) -> tuple[int,int,int]:
    if not os.path.exists(report_path):
        return (0, 0, -1)  # sin reporte
    tree = ET.parse(report_path)
    root = tree.getroot()
    # maneja <testsuite> o <testsuites>
    if root.tag == "testsuite":
        tests = int(root.attrib.get("tests", "0"))
        failures = int(root.attrib.get("failures", "0"))
        errors = int(root.attrib.get("errors", "0"))
        return (failures, errors, tests)
    totals = [0,0,0]
    for ts in root.iter("testsuite"):
        totals[0] += int(ts.attrib.get("failures", "0"))
        totals[1] += int(ts.attrib.get("errors", "0"))
        totals[2] += int(ts.attrib.get("tests", "0"))
    return tuple(totals)


def main():
    # 1) Si no se seleccionaron tests, salir
    sel = Path("files/selected_tests.json")
    if sel.exists():
        data = json.loads(sel.read_text())
        if not data.get("selected_tests"):
            print("No tests selected → skipping LLM diagnosis.")
            return

    # 2) Si hubo tests pero 0 fallos/errores, salir
    failures, errors, tests = junit_failures_errors("files/report.xml")
    if tests >= 0 and failures == 0 and errors == 0:
        print("All tests passed → skipping LLM diagnosis.")
        return

    # 3) Si no hay log, tampoco hay mucho que hacer
    log_path = Path('files/pytest_output.log')
    if not log_path.exists():
        print('No pytest_output.log found; nothing to diagnose.')
        return

    log_text = log_path.read_text(encoding='utf-8', errors='ignore')
    llm = diagnose_with_llm(log_text)
    if llm is None or llm.startswith('[LLM call failed'):
        rules = simple_rules_based_summary(log_text)
        summary = f"LLM unavailable → Rules-based diagnosis:\n{rules}" if llm is None else f"{llm}\n\nRules-based addendum:\n{rules}"
    else:
        rules = simple_rules_based_summary(log_text)
        summary = f"{llm}\n\nRules-based addendum:\n{rules}"

    print('=== Failure Diagnosis ===')
    print(summary)

    with open('files/diagnosis.txt', 'w') as f:
        f.write(summary)

if __name__ == '__main__':
    main()
