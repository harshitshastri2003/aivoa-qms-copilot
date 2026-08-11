import io
import os

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pypdf import PdfReader

from langchain_core.messages import HumanMessage
from graph import agent_graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    thread_id: str
    message: str


class ChatResponse(BaseModel):
    reply: str
    form: dict
    risk_assessment: dict
    status: str


def _run_turn(thread_id: str, text: str) -> ChatResponse:
    config = {"configurable": {"thread_id": thread_id}}
    result = agent_graph.invoke({"messages": [HumanMessage(content=text)]}, config)
    return ChatResponse(
        reply=result["messages"][-1].content,
        form=result.get("form", {}),
        risk_assessment=result.get("risk_assessment", {}),
        status=result.get("status", "Pending Triage"),
    )


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    return _run_turn(req.thread_id, req.message)


@app.post("/upload", response_model=ChatResponse)
async def upload_document(thread_id: str, file: UploadFile = File(...)):
    raw = await file.read()
    if file.filename.lower().endswith(".pdf"):
        reader = PdfReader(io.BytesIO(raw))
        text = "\n".join(page.extract_text() or "" for page in reader.pages)
    else:
        text = raw.decode("utf-8", errors="ignore")
    return _run_turn(thread_id, text)


@app.get("/state/{thread_id}")
def get_state(thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}
    snapshot = agent_graph.get_state(config)
    return {
        "form": snapshot.values.get("form", {}),
        "risk_assessment": snapshot.values.get("risk_assessment", {}),
        "status": snapshot.values.get("status", "Pending Triage"),
    }


class CommitRequest(BaseModel):
    thread_id: str


@app.post("/commit")
def commit(req: CommitRequest):
    config = {"configurable": {"thread_id": req.thread_id}}
    agent_graph.update_state(config, {"status": "Ready to Commit"})
    return {"status": "Ready to Commit"}