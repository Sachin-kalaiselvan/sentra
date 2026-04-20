## Demo run

**Test document uploaded:** `test_invoice.txt`

```
INVOICE #INV-2024-0891
Date: 2024-01-15
Due Date: 2024-01-01  <-- OVERDUE

Vendor: Acme Supplies Ltd
Client: TechCorp India Pvt Ltd
Client PO#: [MISSING]

Line items:
- Cloud Infrastructure Q4    ₹1,85,000
- Support Contract renewal   ₹42,000
- Setup fee (duplicate?)     ₹42,000

Total: ₹3,17,420 (18% GST included)
Notes: Second reminder. First sent 2024-01-05. No response received.
```

**Pipeline output (with Groq API key configured):**

```json
{
  "document_type": "invoice",
  "risk_level": "high",
  "summary": "Overdue invoice for ₹3,17,420 from Acme Supplies to TechCorp India. Client PO number is missing and a duplicate line item is present. Second payment reminder with no response.",
  "anomalies": [
    "invoice is overdue — due date 2024-01-01 has passed",
    "client PO number is missing",
    "possible duplicate line item: ₹42,000 appears twice"
  ],
  "recommended_actions": [
    {
      "action_type": "jira_ticket",
      "title": "Overdue invoice INV-2024-0891 — follow up required",
      "priority": "high"
    },
    {
      "action_type": "slack_message",
      "title": "Payment alert: INV-2024-0891 overdue by 14 days",
      "priority": "high"
    }
  ]
}
```

**What each agent did:**
- **Extract** — read 464 chars of text from the .txt file
- **Reason** — sent content to Groq LLM, detected 3 anomalies, classified as high risk
- **Act** — queued Jira ticket and Slack message for approval (high risk requires human sign-off)
- **Memory** — embedded the decision into Qdrant for future retrieval

**Memory search** — after this run, searching `"overdue invoice missing PO"` returns this document with a similarity score of ~87%.