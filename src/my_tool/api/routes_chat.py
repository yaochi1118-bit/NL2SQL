from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from my_tool.service.chat_service import ChatService
from my_tool.storage.conversation_store import ConversationStore

router = APIRouter(tags=["chat"])


class ConversationCreateRequest(BaseModel):
    ddl_name: str
    target_db: str


class AskRequest(BaseModel):
    question: str


def _get_chat_service(request: Request) -> ChatService:
    return ChatService(request.app.state.base_path)


@router.post("/conversations", status_code=201)
def create_conversation(body: ConversationCreateRequest, request: Request):
    svc = _get_chat_service(request)
    try:
        conv = svc.create_conversation(body.ddl_name, body.target_db)
        return conv
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/conversations/{conv_id}/ask")
def ask_question(conv_id: str, body: AskRequest, request: Request):
    svc = _get_chat_service(request)
    try:
        result = svc.ask(conv_id, body.question)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversations")
def list_conversations(request: Request):
    svc = _get_chat_service(request)
    return svc.list_conversations()


@router.get("/conversations/{conv_id}")
def get_conversation(conv_id: str, request: Request):
    svc = _get_chat_service(request)
    conv = svc.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation '{conv_id}' not found.")
    return conv


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: str, request: Request):
    svc = _get_chat_service(request)
    conv = svc.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation '{conv_id}' not found.")
    store = ConversationStore(request.app.state.base_path / "conversations")
    store.delete(conv_id)
    return {"status": "deleted", "id": conv_id}
