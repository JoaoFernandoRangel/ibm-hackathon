from src.Diary import DiaryAnalyzer
import json


def assess_risk(form_data: dict, backend: str = "watsonx", watsonx_api_key: str | None = None, watsonx_project_id: str | None = None) -> dict:
    """Avalia risco com base em `form_data` usando Granite (watsonx/local).

    Retorna dict: {"risk_level": "low|medium|high", "score": int(0-10), "justification": str}
    """

    # Cria prompt pedindo JSON estruturado com score e justificativa
    prompt = """
You are a clinical triage system. You will receive a filled form with patient data.
Avalie o nível de risco para agravamento/aguda necessidade de atenção médica.
Retorne SOMENTE um JSON válido com os campos:
{
  "risk_level": "low" | "medium" | "high",
  "score": 0-10,
  "justification": "texto explicando por que esse nível"
}

FORM DATA:
"""

    for k, v in form_data.items():
        prompt += f"{k}: {v}\n"

    # Instancia DiaryAnalyzer para usar o backend
    an = DiaryAnalyzer(backend=backend, watsonx_api_key=watsonx_api_key, watsonx_project_id=watsonx_project_id)

    # Gera resposta curta (JSON)
    generated = an.generate_summary_from_text(prompt, max_new_tokens=256)

    # Extraí JSON do texto gerado
    try:
        ini = generated.find("{")
        end = generated.rfind("}")
        if ini != -1 and end != -1:
            jtext = generated[ini:end+1]
            return json.loads(jtext)
    except Exception:
        pass

    # Fallback heurístico simples: score baseado em pain_scale e chronic_conditions
    score = 0
    try:
        pain = float(form_data.get("pain_scale_0_to_10", 0))
        score += min(10, int(pain))
    except Exception:
        pass

    if form_data.get("chronic_conditions"):
        score = min(10, score + 2)

    if score >= 7:
        level = "high"
    elif score >= 4:
        level = "medium"
    else:
        level = "low"

    return {"risk_level": level, "score": score, "justification": "heuristic fallback"}
