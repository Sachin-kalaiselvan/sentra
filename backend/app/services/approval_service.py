import json
import redis

# USE SAME DB AS CELERY (db=0)
r = redis.Redis(host="localhost", port=6380, db=0, decode_responses=True)


def store_pending(task_id: str, state: dict):
    print(f"[APPROVAL] Storing task: {task_id}")
    r.set(task_id, json.dumps(state))


def get_pending(task_id: str):
    data = r.get(task_id)
    print(f"[APPROVAL] Fetching task: {task_id} -> {data}")

    if data:
        return json.loads(data)
    return None


def approve_task(task_id: str):
    state = get_pending(task_id)

    if not state:
        return {"error": "task not found"}

    executed_actions = []
    for anomaly in state.get("anomalies", []):
        executed_actions.append(f"approved_action_executed: {anomaly}")

    state["actions"] = executed_actions
    state["requires_approval"] = False

    r.delete(task_id)

    print(f"[APPROVAL] Approved task: {task_id}")

    return state