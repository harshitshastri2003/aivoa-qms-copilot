import json
import os
from typing import Literal

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode

from state import AgentState

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=os.environ["GROQ_API_KEY"],
    temperature=0,
    model_kwargs={"response_format": {"type": "json_object"}},
)

EXTRACTION_PROMPT = """You are a pharma QMS complaint intake assistant.
Extract structured fields from the user's complaint text and independently
assess risk. Return ONLY valid JSON, no markdown fences, in this shape:

{{
  "form": {{
    "customer_name": "...", "complaint_source": "...", "product_name": "...",
    "strength": "...", "batch_number": "...", "manufacturing_date": "...",
    "expiry_date": "...", "affected_quantity": "...", "facility_name": "...",
    "defect_description": "..."
  }},
  "risk_assessment": {{
    "severity": "Critical | Major | Minor",
    "suggested_next_action": "...",
    "risk_summary": "..."
  }}
}}

Only include fields you can actually infer. Omit fields you don't know
rather than guessing. Text:
{text}
"""

EDIT_PROMPT = """You are updating an existing pharma QMS complaint record.
Here is the CURRENT form and risk assessment:

FORM: {current_form}
RISK: {current_risk}

The user sent this correction/follow-up:
{text}

Return ONLY valid JSON containing JUST the fields that need to change
(do not repeat unchanged fields), in this shape:

{{
  "form": {{ ...changed fields only... }},
  "risk_assessment": {{ ...changed fields only, if risk changes... }}
}}
"""


def _parse_json_response(raw: str) -> dict:
    raw = (raw or "").strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    if not raw:
        return {}
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return {}


def classify_intent(state: AgentState) -> Literal["log", "edit"]:
    has_existing_form = bool(state.get("form"))
    return "edit" if has_existing_form else "log"


def log_complaint_node(state: AgentState) -> dict:
    last_msg = state["messages"][-1].content
    resp = llm.invoke([HumanMessage(content=EXTRACTION_PROMPT.format(text=last_msg))])
    parsed = _parse_json_response(resp.content)
    return {
        "form": parsed.get("form", {}),
        "risk_assessment": parsed.get("risk_assessment", {}),
        "status": "Pending Triage",
        "messages": [AIMessage(content="Complaint logged and risk-assessed.")],
    }


def edit_complaint_node(state: AgentState) -> dict:
    last_msg = state["messages"][-1].content
    prompt = EDIT_PROMPT.format(
        current_form=json.dumps(state.get("form", {})),
        current_risk=json.dumps(state.get("risk_assessment", {})),
        text=last_msg,
    )
    resp = llm.invoke([HumanMessage(content=prompt)])
    parsed = _parse_json_response(resp.content)
    return {
        "form": parsed.get("form", {}),
        "risk_assessment": parsed.get("risk_assessment", {}),
        "messages": [AIMessage(content="Updated the relevant fields.")],
    }


def document_extraction_node(state: AgentState) -> dict:
    return log_complaint_node(state) if not state.get("form") else edit_complaint_node(state)


def route(state: AgentState) -> Literal["log_complaint", "edit_complaint"]:
    return "log_complaint" if classify_intent(state) == "log" else "edit_complaint"


def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("log_complaint", log_complaint_node)
    graph.add_node("edit_complaint", edit_complaint_node)
    graph.set_conditional_entry_point(
        route, {"log_complaint": "log_complaint", "edit_complaint": "edit_complaint"}
    )
    graph.add_edge("log_complaint", END)
    graph.add_edge("edit_complaint", END)
    return graph.compile(checkpointer=MemorySaver())


agent_graph = build_graph()
