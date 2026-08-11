from typing import TypedDict, Optional, Annotated
from langgraph.graph.message import add_messages


def merge_dict(old: dict | None, new: dict | None) -> dict:
    old = old or {}
    new = new or {}
    return {**old, **new}


class ComplaintForm(TypedDict, total=False):
    customer_name: Optional[str]
    complaint_source: Optional[str]
    product_name: Optional[str]
    strength: Optional[str]
    batch_number: Optional[str]
    manufacturing_date: Optional[str]
    expiry_date: Optional[str]
    affected_quantity: Optional[str]
    facility_name: Optional[str]
    defect_description: Optional[str]


class RiskAssessment(TypedDict, total=False):
    severity: Optional[str]
    suggested_next_action: Optional[str]
    risk_summary: Optional[str]


class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    form: Annotated[ComplaintForm, merge_dict]
    risk_assessment: Annotated[RiskAssessment, merge_dict]
    status: str