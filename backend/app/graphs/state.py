from typing import TypedDict, List, Dict


class SentraState(TypedDict):
    filename: str
    extracted_data: Dict
    anomalies: List[str]
    actions: List[str]
    memory_notes: List[str]

    # NEW FIELDS
    risk_level: str
    requires_approval: bool