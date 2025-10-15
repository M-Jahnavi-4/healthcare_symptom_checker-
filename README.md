
# Healthcare Symptom Checker (LLM-based)

Educational demo project that accepts symptom text and returns probable conditions and recommended next steps using a Large Language Model (LLM).

**IMPORTANT**: This tool is for _educational purposes only_. It is **NOT** medical advice.

## What is included
- `app.py` - Flask backend with `/api/diagnose` endpoint and simple frontend at `/`
- `templates/index.html` - Minimal UI to enter symptoms and view results
- `static/style.css` - Styling
- `requirements.txt` - Python dependencies
- `.env.example` - How to set your API key

## Setup (local)
1. Clone or extract the project folder.
2. Create a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS / Linux
   venv\Scripts\activate    # Windows (PowerShell)
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Create a `.env` file in the project root (or set environment variable `OPENAI_API_KEY`). Use `.env.example` as a template.
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-4o-mini
   ```
5. Run the app:
   ```bash
   python app.py
   ```
6. Open http://127.0.0.1:5000 in your browser.

## Notes
- If `OPENAI_API_KEY` is **not** set, the app will run in a **mocked mode** (rule-based) so you can demo without API usage.
- Keep your API key secret. For production use, secure server environment variables and follow rate-limiting and safety best practices.
