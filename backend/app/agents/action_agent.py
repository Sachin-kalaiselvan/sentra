import os
import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()


def action_agent(state: dict) -> dict:
    llm_result = state.get("llm_result", {})
    recommended_actions = llm_result.get("recommended_actions", [])

    if state.get("requires_approval"):
        print(f"[Action] Requires approval — queuing {len(recommended_actions)} actions")
        state["actions"] = [{"status": "pending_approval", "actions": recommended_actions}]
        return state

    executed = []
    for action in recommended_actions:
        action_type = action.get("action_type", "")
        result = {"type": action_type, "title": action.get("title", "")}

        if action_type == "jira_ticket":
            result["result"] = _create_jira_ticket(action)
        elif action_type == "send_email":
            result["result"] = _send_email(action)
        elif action_type == "slack_message":
            result["result"] = _send_slack(action)
        else:
            result["result"] = {"success": False, "error": f"unknown action type: {action_type}"}

        executed.append(result)
        print(f"[Action] {action_type}: {result['result']}")

    state["actions"] = executed
    return state


def _create_jira_ticket(action: dict) -> dict:
    base_url = os.getenv("JIRA_BASE_URL", "")
    email = os.getenv("JIRA_EMAIL", "")
    token = os.getenv("JIRA_API_TOKEN", "")
    project = os.getenv("JIRA_PROJECT_KEY", "OPS")

    if not base_url or not token:
        return {"success": False, "error": "Jira not configured"}

    priority_map = {"low": "Low", "medium": "Medium", "high": "High", "critical": "Highest"}
    payload = {
        "fields": {
            "project": {"key": project},
            "summary": action.get("title", "Agent-generated ticket"),
            "description": action.get("description", ""),
            "issuetype": {"name": "Task"},
            "priority": {"name": priority_map.get(action.get("priority", "medium"), "Medium")},
        }
    }
    try:
        response = requests.post(
            f"{base_url}/rest/api/2/issue",
            json=payload,
            auth=(email, token),
            headers={"Content-Type": "application/json"},
            timeout=10,
        )
        response.raise_for_status()
        data = response.json()
        return {"success": True, "issue_key": data["key"], "url": f"{base_url}/browse/{data['key']}"}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _send_email(action: dict) -> dict:
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", 587))
    user = os.getenv("SMTP_USER", "")
    password = os.getenv("SMTP_PASSWORD", "")
    from_addr = os.getenv("EMAIL_FROM", user)
    recipients = action.get("recipients", [])

    if not user or not password:
        return {"success": False, "error": "SMTP not configured"}
    if not recipients:
        return {"success": False, "error": "no recipients"}

    try:
        msg = MIMEMultipart()
        msg["Subject"] = action.get("title", "Sentra Notification")
        msg["From"] = from_addr
        msg["To"] = ", ".join(recipients)
        msg.attach(MIMEText(action.get("description", ""), "plain"))

        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_addr, recipients, msg.as_string())

        return {"success": True, "recipients": recipients}
    except Exception as e:
        return {"success": False, "error": str(e)}


def _send_slack(action: dict) -> dict:
    token = os.getenv("SLACK_BOT_TOKEN", "")
    channel = action.get("slack_channel", os.getenv("SLACK_CHANNEL", "#ops-alerts"))

    if not token:
        return {"success": False, "error": "Slack not configured"}

    try:
        blocks = [
            {"type": "header", "text": {"type": "plain_text", "text": action.get("title", "Sentra Alert")}},
            {"type": "section", "text": {"type": "mrkdwn", "text": action.get("description", "")[:3000]}},
            {"type": "context", "elements": [{"type": "mrkdwn", "text": f"Priority: *{action.get('priority','medium').upper()}*"}]},
        ]
        response = requests.post(
            "https://slack.com/api/chat.postMessage",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
            json={"channel": channel, "blocks": blocks},
            timeout=10,
        )
        data = response.json()
        if not data.get("ok"):
            return {"success": False, "error": data.get("error", "unknown")}
        return {"success": True, "channel": channel, "ts": data.get("ts")}
    except Exception as e:
        return {"success": False, "error": str(e)}