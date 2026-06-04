from __future__ import annotations

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

from my_tool.service.config_service import ConfigService

router = APIRouter(tags=["config"])


class ConfigUpdateRequest(BaseModel):
    key: str
    value: str


class ConfigInitRequest(BaseModel):
    base_url: str
    api_key: str
    model: str = "gpt-4o"


def _get_config_service(request: Request) -> ConfigService:
    return ConfigService(request.app.state.base_path)


@router.get("/config")
def get_config(request: Request):
    svc = _get_config_service(request)
    try:
        return svc.show()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/config")
def update_config(body: ConfigUpdateRequest, request: Request):
    svc = _get_config_service(request)
    try:
        svc.set(body.key, body.value)
        return {"status": "ok"}
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config/init")
def init_config(body: ConfigInitRequest, request: Request):
    svc = _get_config_service(request)
    svc.init_interactive(body.base_url, body.api_key, body.model)
    return {"status": "ok"}


@router.get("/config/status")
def config_status(request: Request):
    svc = _get_config_service(request)
    return {"exists": svc.config_exists()}
