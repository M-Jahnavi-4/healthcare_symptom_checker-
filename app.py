
import os
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import openai

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY

app = Flask(__name__, static_folder='static', template_folder='templates')

PROMPT_TEMPLATE = """You are a careful medical-safety aware assistant.
Given a user's symptom text, suggest:
1) 3-5 possible *probable* conditions (brief, layman-friendly)
2) Recommended next steps (self-care, urgency and when to see a doctor)
3) A clear educational disclaimer that you are not a doctor.

Output as JSON with keys: conditions (list of short strings), next_steps (list of strings), disclaimer (string).

Symptom text:
{symptoms}
"""

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/diagnose', methods=['POST'])
def diagnose():
    data = request.json or {}
    symptoms = data.get('symptoms', '').strip()
    if not symptoms:
        return jsonify({'error': 'Please provide symptoms.'}), 400

    # Build prompt
    prompt = PROMPT_TEMPLATE.format(symptoms=symptoms)

    if not OPENAI_API_KEY:
        # Mocked rule-based response (useful if API key not set)
        conditions = [
            "Common Cold",
            "Allergic Rhinitis",
            "Viral Infection"
        ]
        next_steps = [
            "Rest and drink fluids.",
            "Use OTC paracetamol or ibuprofen for fever/body ache if appropriate.",
            "Seek urgent care if severe breathing difficulty, chest pain, or confusion."
        ]
        disclaimer = ("Educational purposes only — not a substitute for professional medical advice, diagnosis, or treatment. "
                      "If symptoms are severe or worsening, seek medical care immediately.")
        return jsonify({'conditions': conditions, 'next_steps': next_steps, 'disclaimer': disclaimer, 'source': 'mock'})

    # Call OpenAI (or compatible) API
    try:
        resp = openai.ChatCompletion.create(
            model=os.getenv('OPENAI_MODEL', 'gpt-4o-mini'),
            messages=[{'role': 'system', 'content': 'You are an expert medical-safety aware assistant.'},
                      {'role': 'user', 'content': prompt}],
            max_tokens=400,
            temperature=0.2,
        )
        text = resp['choices'][0]['message']['content'].strip()
    except Exception as e:
        return jsonify({'error': 'LLM request failed', 'details': str(e)}), 500

    # Try to parse the assistant text as simple lines; if parsing fails, return the raw text.
    # Expected format (assistant should produce JSON-like or bullet lists). We'll do best-effort parsing.
    import re, json
    # First try to find a JSON blob in the output
    json_blob = None
    m = re.search(r'\{.*\}', text, re.DOTALL)
    if m:
        try:
            json_blob = json.loads(m.group(0))
        except Exception:
            json_blob = None
    if json_blob:
        return jsonify(json_blob)

    # Fallback: heuristically extract lines
    lines = [ln.strip('-•* ').strip() for ln in text.splitlines() if ln.strip()]
    conditions = []
    next_steps = []
    disclaimer = ""
    mode = None
    for ln in lines:
        low = ln.lower()
        if 'condition' in low or 'possible' in low or 'probable' in low:
            mode = 'cond'
            continue
        if 'next' in low or 'step' in low or 'recommend' in low:
            mode = 'next'
            continue
        if 'disclaim' in low or 'not a doctor' in low:
            mode = 'disc'
            disclaimer += ln + " "
            continue
        if mode == 'cond' and len(conditions) < 10:
            conditions.append(ln)
        elif mode == 'next' and len(next_steps) < 20:
            next_steps.append(ln)
        elif mode == 'disc':
            disclaimer += ln + " "

    # If we couldn't detect sections, return the assistant text as a single 'next_steps' entry
    if not conditions and not next_steps:
        next_steps = [text]
        disclaimer = ("Educational purposes only — not a substitute for professional medical advice, diagnosis, or treatment. "
                      "If symptoms are severe or worsening, seek medical care immediately.")

    return jsonify({'conditions': conditions, 'next_steps': next_steps, 'disclaimer': disclaimer, 'source': 'llm'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
