from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from my_tool.api.routes_ddl import router as ddl_router
from my_tool.api.routes_chat import router as chat_router
from my_tool.api.routes_config import router as config_router


def create_app(base_path: Path | None = None) -> FastAPI:
    """Create the FastAPI application.

    Args:
        base_path: Data storage path (used by services). Defaults to CWD.
    """
    if base_path is None:
        import os

        env_home = os.environ.get("MY_TOOL_HOME")
        base_path = Path(env_home) if env_home else Path.cwd()

    app = FastAPI(title="DDL-to-SQL API", version="0.1.0")

    # CORS: allow Vite dev server
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Inject base_path into app state
    app.state.base_path = base_path

    # Mount routers
    app.include_router(ddl_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(config_router, prefix="/api")

    return app


app = create_app()
