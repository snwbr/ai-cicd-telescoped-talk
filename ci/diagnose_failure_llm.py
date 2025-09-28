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

def main():
    log_path = Path('pytest_output.log')
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

    with open('diagnosis.txt', 'w') as f:
        f.write(summary)

if __name__ == '__main__':
    main()
