import os
from typing import Dict, List

import yaml
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from llm_client.llm_calls import init_model
from llm_client.multichat.manager import ChatManager
from pydantic import BaseModel


cfg = yaml.safe_load(open(os.environ["BASE_CFG_PATH"], "r"))
chat_cfg = cfg["llm_chat_cfg"]["azure_openai"]
llm = init_model(chat_cfg)
manager = ChatManager(session_args={"llm": llm, "limit_len": cfg["limit_len"]})


app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/")
def index() -> FileResponse:
    return FileResponse("static/index.html")


class ChatRequest(BaseModel):
    account_id: str
    text: str


class EditRegenerateRequest(BaseModel):
    account_id: str
    history: List[Dict[str, str]]


class TitleRequest(BaseModel):
    account_id: str
    new_title: str


@app.get("/api/sessions")
def list_sessions(account_id: str) -> List[Dict[str, str]]:
    return [
        {"session_id": session_id, "title": title}
        for session_id, title in manager.list_session_id_title(account_id)
    ]


@app.post("/api/sessions")
def create_session(account_id: str) -> Dict[str, str]:
    return {"session_id": manager.create_session(account_id)}


@app.delete("/api/sessions/{session_id}")
def delete_session(session_id: str, account_id: str) -> None:
    manager.delete_session(account_id, session_id)


@app.get("/api/sessions/{session_id}/history")
def get_history(session_id: str, account_id: str) -> List[Dict[str, str]]:
    return manager.get_full_history(account_id, session_id)


@app.post("/api/sessions/{session_id}/chat")
def chat(session_id: str, r: ChatRequest) -> Dict[str, str]:
    reply = manager.chat(r.account_id, session_id, r.text)
    return {"reply": reply}


@app.post("/api/sessions/{session_id}/edit_regenerate")
def edit_and_regenerate(session_id: str, r: EditRegenerateRequest) -> Dict[str, str]:
    reply = manager.edit_and_regenerate(r.account_id, session_id, r.history)
    return {"reply": reply}


@app.patch("/api/sessions/{session_id}/title")
def edit_title(session_id: str, r: TitleRequest) -> None:
    manager.edit_title(r.account_id, session_id, r.new_title)
