import os
import requests
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"


def analyze_document(text: str):
    try:
        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "llama3-70b-8192",
            "messages": [
                {"role": "system", "content": "Extract anomalies and risk level."},
                {"role": "user", "content": text}
            ],
            "temperature": 0.2
        }

        response = requests.post(GROQ_URL, json=payload, headers=headers)
        data = response.json()

        print("\n[LLM RAW RESPONSE]:\n", data)

        # minimal safe fallback (don’t parse yet)
        return {
            "anomalies": ["llm_detected_issue"],
            "risk_level": "medium",
            "requires_approval": True
        }

    except Exception as e:
        print("[LLM ERROR]", e)

        return {
            "anomalies": ["fallback anomaly"],
            "risk_level": "medium",
            "requires_approval": True
        }