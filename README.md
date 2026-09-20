# CyberShield Free MVP

A local, defensive cybersecurity message analyzer using free/open-source tools.

## Stack
- Python + FastAPI
- Plain HTML/CSS/JavaScript
- Optional Ollama local LLM (no paid API required)
- Local rule-based fallback works even without an LLM

## Run
1. Install Python 3.10+.
2. Create a virtual environment:
   `python -m venv .venv`
3. Activate it.
4. Install:
   `pip install -r requirements.txt`
5. Start:
   `uvicorn app:app --reload`
6. Open http://127.0.0.1:8000

## Optional local AI
Install Ollama from https://ollama.com, then pull a model such as:
`ollama pull llama3.2:3b`

Set `OLLAMA_MODEL=llama3.2:3b` before starting the server.

If Ollama is unavailable, CyberShield automatically uses its local rule-based analyzer.

## Important
This prototype is for defensive triage. It does not prove that a message is malicious.
Do not paste passwords, OTPs, private keys, or other secrets.
For production, add authentication, rate limiting, secure logging, privacy controls,
isolated URL/file analysis, and human security-team escalation.
