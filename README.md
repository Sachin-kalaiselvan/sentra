# sentra

drop in any business doc (pdf, csv, docx, email, spreadsheet, image) and four agents tag-team it: pull the content out, figure out what's going on, do something about it, remember it for next time.

```
upload → extract → reason → act → memory
         (parse)   (groq)   (jira/email/slack)  (qdrant)
```

- **extract** - pdf, csv, docx, xlsx, txt, images via OCR
- **reason** - groq LLM classifies the doc, spots anomalies, decides actions
- **act** - jira tickets, emails, slack posts
- **memory** - embeds each decision in qdrant so later runs can search it

## stack

fastapi + uvicorn, langgraph for routing between agents, celery + redis for the queue, qdrant + sentence-transformers (all-MiniLM-L6-v2) for memory, pdfplumber / python-docx / pandas / pytesseract for parsing, groq `llama-3.3-70b-versatile`, jira REST + SMTP + slack web API, prometheus + flower for watching it, github actions for CI.

## run it

```bash
git clone https://github.com/Sachin-kalaiselvan/sentra.git
cd sentra/backend
cp .env.example .env      # put your GROQ_API_KEY in (console.groq.com)
docker compose up --build
```

- dashboard http://localhost:8000
- api docs http://localhost:8000/docs
- flower http://localhost:5555
- prometheus http://localhost:9090

stop: `docker compose down --timeout 5`

## api

| method | path | what |
|---|---|---|
| GET | `/` | dashboard |
| GET | `/health` | health |
| POST | `/upload` | upload a doc, kicks off the pipeline |
| GET | `/status/{task_id}` | poll status |
| POST | `/approve/{task_id}` | approve + run high-risk actions |
| GET | `/pending/{task_id}` | what's waiting on approval |
| GET | `/memory/search?q=...` | semantic search over past decisions |
| GET | `/audit/{task_id}` | full celery audit trail |
| GET | `/runs` | active + reserved tasks |
| GET | `/metrics` | prometheus |

## example run

in, `test_invoice.txt`:
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

out (with a groq key):
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

trace: extract parsed 464 chars → reason said invoice, high risk, 3 anomalies → act queued jira + slack for sign-off (high risk needs approval) → memory stored it. search `"overdue invoice missing PO"` afterwards and this doc comes back at ~87% similarity.

## heads up

- `.env` isn't in git (secrets), make it from `.env.example` on each machine
- the sentence-transformer model downloads on first run, ~90 MB, cached in the container
- qdrant data survives restarts via a docker volume
- integrations are optional, anything not set up returns `{"success": false, "error": "not configured"}` and the pipeline keeps going
