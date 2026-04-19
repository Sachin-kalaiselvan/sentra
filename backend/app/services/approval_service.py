import json
import os
import redis

r = redis.Redis.from_url(os.getenv("REDIS_URL", "redis://redis:6379/0"), decode_responses=True)


def store_pending(task_id: str, state: dict):
    r.set(task_id, json.dumps(state), ex=86400)


def get_pending(task_id: str):
    data = r.get(task_id)
    return json.loads(data) if data else None


def approve_task(task_id: str):
    state = get_pending(task_id)
    if not state:
        return {"error": "task not found"}
    executed = [f"approved: {a}" for a in state.get("anomalies", [])]
    state["actions"] = executed
    state["requires_approval"] = False
    r.delete(task_id)
    return state