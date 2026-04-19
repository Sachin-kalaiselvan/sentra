import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

SYSTEM_PROMPT = """You are an enterprise document analyst. Given document text, return ONLY valid JSON with this exact schema:
{
  "document_type": "invoice|contract|email|report|ticket|spreadsheet|unknown",
  "summary": "2-3 sentence summary",
  "key_fields": {},
  "anomalies": ["list of issues found"],
  "risk_level": "low|medium|high|critical",
  "requires_approval": true,
  "recommended_actions": [
    {
      "action_type": "jira_ticket|send_email|slack_message",
      "title": "short title",
      "description": "what to do and why",
      "priority": "low|medium|high|critical"
    }
  ]
}
Return ONLY the JSON. No explanation, no markdown fences."""


def analyze_document(text: str, filename: str = "") -> dict:
    if not GROQ_API_KEY:
        print("[LLM] GROQ_API_KEY not set, using fallback")
        return _fallback()

    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": GROQ_MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Filename: {filename}\n\nDocument text:\n{text[:12000]}"},
            ],
            "temperature": 0.1,
        }
        response = requests.post(GROQ_URL, json=payload, headers=headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        raw = data["choices"][0]["message"]["content"].strip()
        # Strip markdown fences if model adds them anyway
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        result = json.loads(raw)
        print(f"[LLM] Parsed successfully. Risk: {result.get('risk_level')}, Actions: {len(result.get('recommended_actions', []))}")
        return result
    except json.JSONDecodeError as e:
        print(f"[LLM] JSON parse error: {e}")
        return _fallback()
    except Exception as e:
        print(f"[LLM] Error: {e}")
        return _fallback()


def _fallback() -> dict:
    return {
        "document_type": "unknown",
        "summary": "Could not analyse document.",
        "key_fields": {},
        "anomalies": [],
        "risk_level": "low",
        "requires_approval": False,
        "recommended_actions": [],
    }