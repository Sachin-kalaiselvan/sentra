from typing import TypedDict, List, Dict, Any


class SentraState(TypedDict):
    task_id: str
    filename: str
    extracted_data: Dict
    anomalies: List[str]
    actions: List[Any]
    memory_notes: List[str]
    risk_level: str
    requires_approval: bool
    llm_result: Dict