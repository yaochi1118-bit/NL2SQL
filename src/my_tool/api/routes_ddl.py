from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel

from my_tool.service.ddl_service import DDLService

router = APIRouter(tags=["ddl"])


class DDLAddRequest(BaseModel):
    name: str
    text: str
    tags: list[str] = []
    force: bool = False


def _get_ddl_service(base_path: Path) -> DDLService:
    return DDLService(base_path)


@router.get("/ddls")
def list_ddls(request: Request):
    svc = _get_ddl_service(request.app.state.base_path)
    return svc.list_all()


@router.post("/ddls", status_code=201)
def add_ddl(body: DDLAddRequest, request: Request):
    svc = _get_ddl_service(request.app.state.base_path)
    try:
        svc.add(body.name, body.text, tags=body.tags, force=body.force)
        return {"status": "ok", "name": body.name}
    except (ValueError, FileExistsError) as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/ddls/{name}")
def get_ddl(name: str, request: Request):
    svc = _get_ddl_service(request.app.state.base_path)
    result = svc.get(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"DDL '{name}' not found.")
    content, meta = result
    return {"name": meta.name, "content": content, "meta": meta}


class DDLUpdateRequest(BaseModel):
    text: str
    tags: list[str] = []


@router.put("/ddls/{name}")
def update_ddl(name: str, body: DDLUpdateRequest, request: Request):
    svc = _get_ddl_service(request.app.state.base_path)
    try:
        svc.add(name, body.text, tags=body.tags, force=True)
        return {"status": "ok", "name": name}
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/ddls/{name}")
def delete_ddl(name: str, request: Request):
    svc = _get_ddl_service(request.app.state.base_path)
    try:
        svc.delete(name)
        return {"status": "deleted", "name": name}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
