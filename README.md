# Sentra — Multi-Agent Enterprise Automation

Upload any business document — PDF, CSV, DOCX, email, spreadsheet, image — and four AI agents collaborate to extract, reason, act, and remember.

## Architecture

```
Upload → Extract Agent → Reason Agent → Act Agent → Memory Agent
           (parse file)    (Groq LLM)   (Jira/Email/Slack)  (Qdrant)
```

| Agent | What it does |
|---|---|
| Extract | Parses PDF, CSV, DOCX, XLSX, TXT, images via OCR |
| Reason | Sends content to Groq LLM, classifies document, detects anomalies, decides actions |
| Act | Creates Jira tickets, sends emails, posts Slack messages |
| Memory | Embeds decisions into Qdrant for semantic retrieval across runs |

## Stack

| Layer | Tech |
|---|---|
| API | FastAPI + uvicorn |
| Agent orchestration | LangGraph (conditional routing) |
| Task queue | Celery + Redis |
| Vector memory | Qdrant + sentence-transformers (all-MiniLM-L6-v2) |
| Document parsing | pdfplumber, python-docx, pandas, pytesseract |
| AI | Groq — llama-3.3-70b-versatile |
| Integrations | Jira REST API, SMTP, Slack Web API |
| Observability | Prometheus metrics, Flower (Celery monitor) |
| CI/CD | GitHub Actions |

## Setup

```bash
git clone https://github.com/Sachin-kalaiselvan/sentra.git
cd sentra/backend
cp .env.example .env
# Edit .env — add GROQ_API_KEY from console.groq.com
docker compose up --build
```

| Service | URL |
|---|---|
| Dashboard | http://localhost:8000 |
| API docs | http://localhost:8000/docs |
| Flower | http://localhost:5555 |
| Prometheus | http://localhost:9090 |

Stop cleanly:
```bash
docker compose down --timeout 5
```

## API

| Method | Path | Description |
|---|---|---|
| GET | `/` | Dashboard UI |
| GET | `/health` | Health check |
| POST | `/upload` | Upload document and start pipeline |
| GET | `/status/{task_id}` | Poll pipeline status |
| POST | `/approve/{task_id}` | Approve and execute high-risk actions |
| GET | `/pending/{task_id}` | Get pending approval details |
| GET | `/memory/search?q=...` | Semantic search over past decisions |
| GET | `/audit/{task_id}` | Full Celery audit trail for a run |
| GET | `/runs` | Active and reserved tasks |
| GET | `/metrics` | Prometheus metrics |

## Demo run

**Input — `test_invoice.txt`:**
```
INVOICE #INV-2024-0891
Date: 2024-01-15 / Due: 2024-01-01  <-- OVERDUE

Vendor: Acme Supplies Ltd
Client: TechCorp India Pvt Ltd
Client PO#: [MISSING]

- Cloud Infrastructure Q4    ₹1,85,000
- Support Contract renewal   ₹42,000
- Setup fee (duplicate?)     ₹42,000

TOTAL DUE: ₹3,17,420 (18% GST)
Notes: Second reminder. No response received.
```

**Pipeline output (with Groq API key):**
```json
{
  "document_type": "invoice",
  "risk_level": "high",
  "summary": "Overdue invoice for ₹3,17,420 from Acme Supplies. PO number missing, possible duplicate line item, second reminder with no client response.",
  "anomalies": [
    "invoice overdue — due 2024-01-01",
    "client PO number missing",
    "duplicate line item: ₹42,000 appears twice"
  ],
  "recommended_actions": [
    {"action_type": "jira_ticket", "title": "Overdue invoice INV-2024-0891", "priority": "high"},
    {"action_type": "slack_message", "title": "Payment alert: 14 days overdue", "priority": "high"}
  ]
}
```

**Agent trace:**
- Extract: parsed 464 chars from txt file
- Reason: classified invoice, risk high, 3 anomalies found
- Act: queued Jira + Slack for approval (high risk requires sign-off)
- Memory: embedded decision into Qdrant

**Memory search** — after this run, searching `"overdue invoice missing PO"` returns this document with ~87% similarity score.

## Notes

- `.env` is excluded from git (contains secrets) — create from `.env.example` on each machine
- The sentence-transformer model downloads on first run (~90 MB, cached in container)
- Qdrant data persists across restarts via Docker volume
- Integrations are optional — unconfigured ones return `{"success": false, "error": "not configured"}` without crashing the pipeline