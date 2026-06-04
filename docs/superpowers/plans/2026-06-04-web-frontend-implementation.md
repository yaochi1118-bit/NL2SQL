# Web Frontend Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Web UI for the DDL-to-SQL tool covering DDL management, chat conversations, history, and LLM config.

**Architecture:** FastAPI REST API backend wrapping existing Service layer (no business logic rewrite), React 18 + TypeScript + Vite SPA frontend communicating via JSON REST. Development uses two processes (Vite dev server + FastAPI); production builds to static files served by FastAPI.

**Tech Stack:** FastAPI + uvicorn (Python), React 18 + TypeScript + Vite + React Router + highlight.js

---

## File Structure

```
my-tool/
├── src/my_tool/
│   ├── api/                          # [NEW] REST API layer
│   │   ├── __init__.py
│   │   ├── server.py                 # FastAPI app factory, startup, static serve
│   │   ├── routes_ddl.py             # DDL CRUD endpoints
│   │   ├── routes_chat.py            # Conversation endpoints
│   │   └── routes_config.py          # Config endpoints
├── frontend/                         # [NEW] React SPA
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── tsconfig.app.json
│   ├── tsconfig.node.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── index.css                 # Global styles (dark theme)
│       ├── api/
│       │   └── client.ts             # Fetch-based HTTP client
│       ├── components/
│       │   ├── Layout.tsx            # Sidebar + Content shell
│       │   ├── Sidebar.tsx           # Nav links + logo
│       │   ├── SyntaxHighlighter.tsx # SQL code highlighting
│       │   ├── ConfirmDialog.tsx     # Delete confirmation
│       │   └── LoadingSpinner.tsx    # Loading indicator
│       └── pages/
│           ├── DDLList.tsx           # DDL schema list
│           ├── DDLDetail.tsx         # DDL schema detail
│           ├── DDLUploadModal.tsx    # Add DDL modal
│           ├── Chat.tsx              # Chat conversation
│           ├── History.tsx           # Conversation history
│           └── Settings.tsx          # LLM config
```

---

### Task 1: FastAPI 后端 + DDL 路由

**Files:**
- Create: `src/my_tool/api/__init__.py`
- Create: `src/my_tool/api/server.py`
- Create: `src/my_tool/api/routes_ddl.py`
- Modify: `pyproject.toml` (add fastapi/uvicorn deps)
- Test: via curl / browser

- [ ] **Step 1: Add fastapi/uvicorn dependencies**

Modify `pyproject.toml` to add these entries under `[project]`:
```toml
dependencies = [
    "typer>=0.12.0",
    "rich>=13.0.0",
    "openai>=1.0.0",
    "pydantic>=2.0.0",
    "tomli-w>=1.0.0",
    "prompt-toolkit>=3.0.0",
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
]
```

Run: `uv sync`
Expected: fastapi and uvicorn installed.

- [ ] **Step 2: Create api/__init__.py**

Create `src/my_tool/api/__init__.py`:
```python
"""REST API layer for DDL-to-SQL tool."""
```

- [ ] **Step 3: Create api/server.py**

Create `src/my_tool/api/server.py`:
```python
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
```

- [ ] **Step 4: Create api/routes_ddl.py**

Create `src/my_tool/api/routes_ddl.py`:
```python
from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
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


def _get_base_path(request) -> Path:
    return request.app.state.base_path


@router.get("/ddls")
def list_ddls(request):
    svc = _get_ddl_service(_get_base_path(request))
    return svc.list_all()


@router.post("/ddls", status_code=201)
def add_ddl(body: DDLAddRequest, request):
    svc = _get_ddl_service(_get_base_path(request))
    try:
        svc.add(body.name, body.text, tags=body.tags, force=body.force)
        return {"status": "ok", "name": body.name}
    except (ValueError, FileExistsError) as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.get("/ddls/{name}")
def get_ddl(name: str, request):
    svc = _get_ddl_service(_get_base_path(request))
    result = svc.get(name)
    if result is None:
        raise HTTPException(status_code=404, detail=f"DDL '{name}' not found.")
    content, meta = result
    return {"name": meta.name, "content": content, "meta": meta}


@router.delete("/ddls/{name}")
def delete_ddl(name: str, request):
    svc = _get_ddl_service(_get_base_path(request))
    try:
        svc.delete(name)
        return {"status": "deleted", "name": name}
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
```

- [ ] **Step 5: Test DDL API endpoints**

Run:
```bash
cd d:/python/学习打包/my-tool
uv run uvicorn my_tool.api.server:app --port 8000 &
```

Wait for startup, then:
```bash
# List (empty)
curl -s http://localhost:8000/api/ddls

# Create
curl -s -X POST http://localhost:8000/api/ddls \
  -H "Content-Type: application/json" \
  -d '{"name":"test","text":"CREATE TABLE users (id INT);","tags":["test"]}'

# Get
curl -s http://localhost:8000/api/ddls/test

# Delete
curl -s -X DELETE http://localhost:8000/api/ddls/test

# Cleanup
kill %1
```

Expected: All endpoints return correct status codes and JSON.

- [ ] **Step 6: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: add FastAPI backend with DDL CRUD routes"
```

---

### Task 2: 对话 & 配置路由

**Files:**
- Create: `src/my_tool/api/routes_chat.py`
- Create: `src/my_tool/api/routes_config.py`
- Test: via curl

- [ ] **Step 1: Create api/routes_chat.py**

Create `src/my_tool/api/routes_chat.py`:
```python
from __future__ import annotations

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from my_tool.service.chat_service import ChatService

router = APIRouter(tags=["chat"])


class ConversationCreateRequest(BaseModel):
    ddl_name: str
    target_db: str


class AskRequest(BaseModel):
    question: str


def _get_chat_service(request) -> ChatService:
    from my_tool.service.chat_service import ChatService
    return ChatService(request.app.state.base_path)


@router.post("/conversations", status_code=201)
def create_conversation(body: ConversationCreateRequest, request):
    svc = _get_chat_service(request)
    try:
        conv = svc.create_conversation(body.ddl_name, body.target_db)
        return conv
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/conversations/{conv_id}/ask")
def ask_question(conv_id: str, body: AskRequest, request):
    svc = _get_chat_service(request)
    try:
        result = svc.ask(conv_id, body.question)
        return result
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/conversations")
def list_conversations(request):
    svc = _get_chat_service(request)
    return svc.list_conversations()


@router.get("/conversations/{conv_id}")
def get_conversation(conv_id: str, request):
    svc = _get_chat_service(request)
    conv = svc.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation '{conv_id}' not found.")
    return conv


@router.delete("/conversations/{conv_id}")
def delete_conversation(conv_id: str, request):
    svc = _get_chat_service(request)
    conv = svc.get_conversation(conv_id)
    if conv is None:
        raise HTTPException(status_code=404, detail=f"Conversation '{conv_id}' not found.")
    # The current ChatService doesn't expose delete; we access the store directly.
    # For now, impl a simple deletion via the underlying store.
    from my_tool.storage.conversation_store import ConversationStore
    store = ConversationStore(request.app.state.base_path / "conversations")
    store.delete(conv_id)
    return {"status": "deleted", "id": conv_id}
```

- [ ] **Step 2: Create api/routes_config.py**

Create `src/my_tool/api/routes_config.py`:
```python
from __future__ import annotations

from fastapi import APIRouter, HTTPException
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


def _get_config_service(request) -> ConfigService:
    return ConfigService(request.app.state.base_path)


@router.get("/config")
def get_config(request):
    svc = _get_config_service(request)
    try:
        return svc.show()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/config")
def update_config(body: ConfigUpdateRequest, request):
    svc = _get_config_service(request)
    try:
        svc.set(body.key, body.value)
        return {"status": "ok"}
    except (FileNotFoundError, ValueError) as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/config/init")
def init_config(body: ConfigInitRequest, request):
    svc = _get_config_service(request)
    svc.init_interactive(body.base_url, body.api_key, body.model)
    return {"status": "ok"}


@router.get("/config/status")
def config_status(request):
    svc = _get_config_service(request)
    return {"exists": svc.config_exists()}
```

- [ ] **Step 3: Test endpoints**

Run:
```bash
cd d:/python/学习打包/my-tool
uv run uvicorn my_tool.api.server:app --port 8000 &
```

```bash
# Config status
curl -s http://localhost:8000/api/config/status

# Config init (adjust values as needed)
curl -s -X POST http://localhost:8000/api/config/init \
  -H "Content-Type: application/json" \
  -d '{"base_url":"https://api.openai.com/v1","api_key":"sk-test","model":"gpt-4o"}'

# Config get
curl -s http://localhost:8000/api/config

# Conversations list (empty)
curl -s http://localhost:8000/api/conversations

# Cleanup
kill %1
```

Expected: All endpoints return correct responses.

- [ ] **Step 4: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: add chat and config API routes"
```

---

### Task 3: React 项目脚手架 + 布局

**Files:**
- Create: `frontend/package.json`
- Create: `frontend/tsconfig.json`
- Create: `frontend/tsconfig.app.json`
- Create: `frontend/tsconfig.node.json`
- Create: `frontend/vite.config.ts`
- Create: `frontend/index.html`
- Create: `frontend/src/main.tsx`
- Create: `frontend/src/App.tsx`
- Create: `frontend/src/index.css`
- Create: `frontend/src/components/Layout.tsx`
- Create: `frontend/src/components/Sidebar.tsx`
- Create: `frontend/src/vite-env.d.ts`

- [ ] **Step 1: Scaffold with Vite and install deps**

```bash
cd d:/python/学习打包/my-tool
mkdir -p frontend/src/api frontend/src/components frontend/src/pages
cd frontend
npm create vite@latest . -- --template react-ts
npm install react-router-dom
npm install -D @types/react @types/react-dom
npm install highlight.js
```

Expected: Vite scaffold + all deps installed.

- [ ] **Step 2: Configure Vite proxy**

Write `frontend/vite.config.ts`:
```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
})
```

- [ ] **Step 3: Write global CSS**

Write `frontend/src/index.css`:
```css
:root {
  --bg-primary: #1a1b26;
  --bg-secondary: #24253a;
  --bg-tertiary: #1e1e2e;
  --text-primary: #cdd6f4;
  --text-secondary: #a6adc8;
  --text-muted: #585b70;
  --accent: #89b4fa;
  --accent-hover: #74c7ec;
  --danger: #f38ba8;
  --success: #a6e3a1;
  --border: #313244;
  --sidebar-width: 240px;
}

* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  background: var(--bg-primary);
  color: var(--text-primary);
  min-height: 100vh;
}

a {
  color: var(--accent);
  text-decoration: none;
}
a:hover {
  color: var(--accent-hover);
}

button {
  cursor: pointer;
  border: none;
  border-radius: 6px;
  padding: 8px 16px;
  font-size: 14px;
  transition: background 0.2s;
}

input, textarea, select {
  background: var(--bg-tertiary);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 8px 12px;
  color: var(--text-primary);
  font-size: 14px;
  width: 100%;
}
input:focus, textarea:focus {
  outline: none;
  border-color: var(--accent);
}

.btn-primary {
  background: var(--accent);
  color: var(--bg-primary);
  font-weight: 600;
}
.btn-primary:hover {
  background: var(--accent-hover);
}

.btn-danger {
  background: transparent;
  color: var(--danger);
  border: 1px solid var(--danger);
}
.btn-danger:hover {
  background: var(--danger);
  color: var(--bg-primary);
}

.btn-secondary {
  background: var(--bg-secondary);
  color: var(--text-primary);
  border: 1px solid var(--border);
}
.btn-secondary:hover {
  background: var(--bg-tertiary);
}
```

- [ ] **Step 4: Write Layout component**

Write `frontend/src/components/Layout.tsx`:
```typescript
import { Outlet } from 'react-router-dom'
import Sidebar from './Sidebar'

export default function Layout() {
  return (
    <div style={{ display: 'flex', minHeight: '100vh' }}>
      <Sidebar />
      <main style={{ flex: 1, padding: '24px 32px', overflow: 'auto' }}>
        <Outlet />
      </main>
    </div>
  )
}
```

- [ ] **Step 5: Write Sidebar component**

Write `frontend/src/components/Sidebar.tsx`:
```typescript
import { NavLink } from 'react-router-dom'

const links = [
  { to: '/ddls', label: 'DDL 管理' },
  { to: '/chat', label: '对话' },
  { to: '/history', label: '历史' },
  { to: '/settings', label: '设置' },
]

export default function Sidebar() {
  return (
    <aside style={{
      width: 'var(--sidebar-width)',
      background: 'var(--bg-secondary)',
      borderRight: '1px solid var(--border)',
      display: 'flex',
      flexDirection: 'column',
      padding: '16px 0',
    }}>
      <div style={{
        padding: '0 20px 16px',
        borderBottom: '1px solid var(--border)',
        marginBottom: 8,
        fontWeight: 700,
        fontSize: 18,
        color: 'var(--accent)',
      }}>
        DDL-to-SQL
      </div>
      <nav style={{ flex: 1, display: 'flex', flexDirection: 'column', gap: 2 }}>
        {links.map(link => (
          <NavLink
            key={link.to}
            to={link.to}
            end={link.to === '/ddls'}
            style={({ isActive }) => ({
              padding: '10px 20px',
              color: isActive ? 'var(--accent)' : 'var(--text-secondary)',
              background: isActive ? 'var(--bg-tertiary)' : 'transparent',
              borderRight: isActive ? '2px solid var(--accent)' : '2px solid transparent',
              fontWeight: isActive ? 600 : 400,
              fontSize: 14,
            })}
          >
            {link.label}
          </NavLink>
        ))}
      </nav>
      <div style={{ padding: '16px 20px', color: 'var(--text-muted)', fontSize: 12 }}>
        v0.1.0
      </div>
    </aside>
  )
}
```

- [ ] **Step 6: Write App.tsx with routing**

Write `frontend/src/App.tsx`:
```typescript
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import DDLList from './pages/DDLList'
import DDLDetail from './pages/DDLDetail'
import Chat from './pages/Chat'
import History from './pages/History'
import Settings from './pages/Settings'

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Navigate to="/ddls" replace />} />
          <Route path="/ddls" element={<DDLList />} />
          <Route path="/ddls/:name" element={<DDLDetail />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/chat/:convId" element={<Chat />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  )
}
```

- [ ] **Step 7: Write main.tsx**

Write `frontend/src/main.tsx`:
```typescript
import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
```

Write `frontend/src/vite-env.d.ts`:
```typescript
/// <reference types="vite/client" />
```

- [ ] **Step 8: Update index.html**

Vite scaffolded this already, verify the title is correct in `frontend/index.html`:
```html
<title>DDL-to-SQL</title>
```

- [ ] **Step 9: Create placeholder pages (minimal)**

Write `frontend/src/pages/DDLList.tsx`:
```typescript
export default function DDLList() {
  return <h1>DDL 管理</h1>
}
```

Create the same placeholder for all other pages:
- `frontend/src/pages/DDLDetail.tsx` → `<h1>DDL 详情</h1>`
- `frontend/src/pages/Chat.tsx` → `<h1>对话</h1>`
- `frontend/src/pages/History.tsx` → `<h1>历史</h1>`
- `frontend/src/pages/Settings.tsx` → `<h1>设置</h1>`

- [ ] **Step 10: Verify frontend builds and runs**

```bash
cd d:/python/学习打包/my-tool/frontend
npx tsc --noEmit
npm run build
```

Expected: Build succeeds with no errors, output lands in `frontend/dist/`.

- [ ] **Step 11: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: scaffold React frontend with layout and routing"
```

---

### Task 4: DDL 管理页面

**Files:**
- Create: `frontend/src/api/client.ts`
- Modify: `frontend/src/pages/DDLList.tsx`
- Modify: `frontend/src/pages/DDLDetail.tsx`
- Create: `frontend/src/pages/DDLUploadModal.tsx`
- Create: `frontend/src/components/SyntaxHighlighter.tsx`
- Create: `frontend/src/components/ConfirmDialog.tsx`
- Create: `frontend/src/components/LoadingSpinner.tsx`

- [ ] **Step 1: Create API client**

Write `frontend/src/api/client.ts`:
```typescript
const BASE = '/api'

async function request<T>(url: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${url}`, {
    headers: { 'Content-Type': 'application/json', ...options?.headers },
    ...options,
  })
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }))
    throw new Error(err.detail || `HTTP ${res.status}`)
  }
  return res.json()
}

export interface DDLMeta {
  name: string
  tags: string[]
  created_at: string
  table_count: number
}

export interface DDLDetail {
  name: string
  content: string
  meta: DDLMeta
}

export interface Conversation {
  id: string
  ddl_name: string
  target_db: string
  created_at: string
  updated_at: string
  message_count: number
  messages?: Message[]
}

export interface Message {
  role: string
  content: string
}

export interface AskResult {
  sql: string
  raw_response: string
  explanation: string
  valid: boolean
  messages: Message[]
}

export interface ConfigDisplay {
  provider: string
  base_url: string
  api_key: string
  model: string
}

// DDL APIs
export const ddlApi = {
  list: () => request<DDLMeta[]>('/ddls'),
  get: (name: string) => request<DDLDetail>(`/ddls/${encodeURIComponent(name)}`),
  create: (data: { name: string; text: string; tags?: string[]; force?: boolean }) =>
    request<{ status: string; name: string }>('/ddls', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  delete: (name: string) =>
    request<{ status: string; name: string }>(`/ddls/${encodeURIComponent(name)}`, {
      method: 'DELETE',
    }),
}

// Conversation APIs
export const chatApi = {
  create: (data: { ddl_name: string; target_db: string }) =>
    request<Conversation>('/conversations', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  ask: (convId: string, question: string) =>
    request<AskResult>(`/conversations/${encodeURIComponent(convId)}/ask`, {
      method: 'POST',
      body: JSON.stringify({ question }),
    }),
  list: () => request<Conversation[]>('/conversations'),
  get: (convId: string) => request<Conversation>(`/conversations/${encodeURIComponent(convId)}`),
  delete: (convId: string) =>
    request<{ status: string; id: string }>(`/conversations/${encodeURIComponent(convId)}`, {
      method: 'DELETE',
    }),
}

// Config APIs
export const configApi = {
  get: () => request<ConfigDisplay>('/config'),
  update: (key: string, value: string) =>
    request<{ status: string }>('/config', {
      method: 'PUT',
      body: JSON.stringify({ key, value }),
    }),
  init: (data: { base_url: string; api_key: string; model: string }) =>
    request<{ status: string }>('/config/init', {
      method: 'POST',
      body: JSON.stringify(data),
    }),
  status: () => request<{ exists: boolean }>('/config/status'),
}
```

- [ ] **Step 2: Create shared components**

Write `frontend/src/components/LoadingSpinner.tsx`:
```typescript
export default function LoadingSpinner({ text = '加载中...' }: { text?: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, padding: 24, color: 'var(--text-muted)' }}>
      <div style={{
        width: 20, height: 20, border: '2px solid var(--border)',
        borderTopColor: 'var(--accent)', borderRadius: '50%',
        animation: 'spin 0.8s linear infinite',
      }} />
      <span>{text}</span>
      <style>{`@keyframes spin { to { transform: rotate(360deg) } }`}</style>
    </div>
  )
}
```

Write `frontend/src/components/ConfirmDialog.tsx`:
```typescript
interface Props {
  open: boolean
  title: string
  message: string
  confirmLabel?: string
  onConfirm: () => void
  onCancel: () => void
}

export default function ConfirmDialog({ open, title, message, confirmLabel = '确认', onConfirm, onCancel }: Props) {
  if (!open) return null
  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    }} onClick={onCancel}>
      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 12, padding: 24, minWidth: 360,
        border: '1px solid var(--border)',
      }} onClick={e => e.stopPropagation()}>
        <h3 style={{ marginBottom: 8 }}>{title}</h3>
        <p style={{ color: 'var(--text-secondary)', marginBottom: 20 }}>{message}</p>
        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="btn-secondary" onClick={onCancel}>取消</button>
          <button className="btn-danger" onClick={onConfirm}>{confirmLabel}</button>
        </div>
      </div>
    </div>
  )
}
```

Write `frontend/src/components/SyntaxHighlighter.tsx`:
```typescript
import { useMemo, useState } from 'react'
import hljs from 'highlight.js/lib/core'
import sql from 'highlight.js/lib/languages/sql'
import 'highlight.js/styles/github-dark.css'

hljs.registerLanguage('sql', sql)

interface Props {
  code: string
  showLineNumbers?: boolean
}

export default function SyntaxHighlighter({ code, showLineNumbers = true }: Props) {
  const [copied, setCopied] = useState(false)
  const highlighted = useMemo(() => {
    const result = hljs.highlight(code, { language: 'sql' })
    return result.value
  }, [code])

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  const lines = highlighted.split('\n')

  return (
    <div style={{
      position: 'relative',
      background: '#1e1e2e',
      borderRadius: 8,
      overflow: 'hidden',
      border: '1px solid var(--border)',
    }}>
      <div style={{
        display: 'flex', justifyContent: 'flex-end', padding: '4px 8px',
        background: 'var(--bg-tertiary)', borderBottom: '1px solid var(--border)',
      }}>
        <button
          onClick={handleCopy}
          style={{
            background: 'transparent', color: copied ? 'var(--success)' : 'var(--text-muted)',
            padding: '2px 8px', fontSize: 12, border: '1px solid var(--border)',
            borderRadius: 4,
          }}
        >
          {copied ? '已复制' : '复制'}
        </button>
      </div>
      <pre style={{ padding: '12px 16px', overflow: 'auto', margin: 0, fontSize: 13, lineHeight: 1.6 }}>
        <code style={{ fontFamily: "'JetBrains Mono', 'Fira Code', monospace" }}
          dangerouslySetInnerHTML={{ __html: highlighted }} />
      </pre>
    </div>
  )
}
```

- [ ] **Step 3: Implement DDLUploadModal**

Write `frontend/src/pages/DDLUploadModal.tsx`:
```typescript
import { useState } from 'react'
import { ddlApi } from '../api/client'

interface Props {
  open: boolean
  onClose: () => void
  onCreated: () => void
}

export default function DDLUploadModal({ open, onClose, onCreated }: Props) {
  const [name, setName] = useState('')
  const [text, setText] = useState('')
  const [tags, setTags] = useState('')
  const [force, setForce] = useState(false)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  if (!open) return null

  const handleSubmit = async () => {
    setError('')
    if (!name.trim()) { setError('请输入名称'); return }
    if (!text.trim()) { setError('请输入 DDL 内容'); return }
    setLoading(true)
    try {
      const tagList = tags.split(',').map(t => t.trim()).filter(Boolean)
      await ddlApi.create({ name: name.trim(), text: text.trim(), tags: tagList, force })
      onCreated()
      onClose()
      setName('')
      setText('')
      setTags('')
      setForce(false)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{
      position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000,
    }} onClick={onClose}>
      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 12, padding: 24, minWidth: 480,
        border: '1px solid var(--border)', maxHeight: '80vh', overflow: 'auto',
      }} onClick={e => e.stopPropagation()}>
        <h2 style={{ marginBottom: 20 }}>添加 DDL</h2>

        {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 14 }}>{error}</div>}

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>名称</label>
          <input value={name} onChange={e => setName(e.target.value)} placeholder="例如：电商系统" />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>DDL 内容</label>
          <textarea
            value={text}
            onChange={e => setText(e.target.value)}
            placeholder="CREATE TABLE users ( ... );"
            rows={10}
            style={{ fontFamily: 'monospace', resize: 'vertical' }}
          />
        </div>

        <div style={{ marginBottom: 12 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>标签（逗号分隔）</label>
          <input value={tags} onChange={e => setTags(e.target.value)} placeholder="MySQL, 生产" />
        </div>

        <div style={{ marginBottom: 20 }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: 8, cursor: 'pointer' }}>
            <input type="checkbox" checked={force} onChange={e => setForce(e.target.checked)} style={{ width: 'auto' }} />
            <span style={{ fontSize: 13, color: 'var(--text-secondary)' }}>覆盖已存在的 DDL</span>
          </label>
        </div>

        <div style={{ display: 'flex', gap: 8, justifyContent: 'flex-end' }}>
          <button className="btn-secondary" onClick={onClose}>取消</button>
          <button className="btn-primary" onClick={handleSubmit} disabled={loading}>
            {loading ? '提交中...' : '添加'}
          </button>
        </div>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Implement DDLList page**

Write `frontend/src/pages/DDLList.tsx`:
```typescript
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ddlApi, DDLMeta } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import ConfirmDialog from '../components/ConfirmDialog'
import DDLUploadModal from './DDLUploadModal'

export default function DDLList() {
  const [ddls, setDdls] = useState<DDLMeta[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [showUpload, setShowUpload] = useState(false)
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    setError('')
    try {
      const data = await ddlApi.list()
      setDdls(data)
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await ddlApi.delete(deleteTarget)
      setDeleteTarget(null)
      load()
    } catch (e: any) {
      setError(e.message)
    }
  }

  const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 24 }}>
        <h1>DDL 管理</h1>
        <button className="btn-primary" onClick={() => setShowUpload(true)}>+ 添加 DDL</button>
      </div>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {loading ? <LoadingSpinner text="加载中..." /> : ddls.length === 0 ? (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          <p style={{ fontSize: 16, marginBottom: 8 }}>暂无 DDL</p>
          <p style={{ fontSize: 14 }}>点击「添加 DDL」按钮上传你的第一个数据库 Schema</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {ddls.map(ddl => (
            <div
              key={ddl.name}
              style={{
                background: 'var(--bg-secondary)',
                border: '1px solid var(--border)',
                borderRadius: 8,
                padding: '16px 20px',
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                cursor: 'pointer',
                transition: 'border-color 0.2s',
              }}
              onClick={() => navigate(`/ddls/${encodeURIComponent(ddl.name)}`)}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 16, marginBottom: 4 }}>{ddl.name}</div>
                <div style={{ display: 'flex', gap: 8, alignItems: 'center', fontSize: 13, color: 'var(--text-secondary)' }}>
                  <span>{ddl.table_count} 张表</span>
                  <span>·</span>
                  <span>{formatDate(ddl.created_at)}</span>
                  {ddl.tags.map(tag => (
                    <span key={tag} style={{
                      background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: 4,
                      fontSize: 12, color: 'var(--accent)',
                    }}>{tag}</span>
                  ))}
                </div>
              </div>
              <button
                className="btn-danger"
                onClick={e => { e.stopPropagation(); setDeleteTarget(ddl.name) }}
                style={{ fontSize: 13, padding: '4px 12px' }}
              >
                删除
              </button>
            </div>
          ))}
        </div>
      )}

      <DDLUploadModal open={showUpload} onClose={() => setShowUpload(false)} onCreated={load} />
      <ConfirmDialog
        open={!!deleteTarget}
        title="确认删除"
        message={`确定要删除 DDL「${deleteTarget}」吗？此操作不可撤销。`}
        confirmLabel="删除"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
```

- [ ] **Step 5: Implement DDLDetail page**

Write `frontend/src/pages/DDLDetail.tsx`:
```typescript
import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { ddlApi, DDLDetail as DDLDetailType } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import SyntaxHighlighter from '../components/SyntaxHighlighter'

export default function DDLDetail() {
  const { name } = useParams<{ name: string }>()
  const navigate = useNavigate()
  const [data, setData] = useState<DDLDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!name) return
    setLoading(true)
    ddlApi.get(decodeURIComponent(name))
      .then(setData)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false))
  }, [name])

  if (loading) return <LoadingSpinner text="加载中..." />
  if (error) return <div style={{ color: 'var(--danger)' }}>{error}</div>
  if (!data) return null

  return (
    <div>
      <button className="btn-secondary" onClick={() => navigate('/ddls')} style={{ marginBottom: 16 }}>
        ← 返回列表
      </button>

      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 8, padding: 20,
        border: '1px solid var(--border)', marginBottom: 20,
      }}>
        <h1 style={{ marginBottom: 8 }}>{data.meta.name}</h1>
        <div style={{ display: 'flex', gap: 12, alignItems: 'center', fontSize: 14, color: 'var(--text-secondary)' }}>
          <span>{data.meta.table_count} 张表</span>
          <span>·</span>
          <span>{new Date(data.meta.created_at).toLocaleString('zh-CN')}</span>
          {data.meta.tags.map(tag => (
            <span key={tag} style={{
              background: 'var(--bg-tertiary)', padding: '2px 8px', borderRadius: 4,
              fontSize: 12, color: 'var(--accent)',
            }}>{tag}</span>
          ))}
        </div>
      </div>

      <h3 style={{ marginBottom: 12 }}>DDL 内容</h3>
      <SyntaxHighlighter code={data.content} />
    </div>
  )
}
```

- [ ] **Step 6: Verify frontend build**

```bash
cd d:/python/学习打包/my-tool/frontend
npx tsc --noEmit
npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 7: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: implement DDL management pages with API client"
```

---

### Task 5: 对话 & 历史 & 设置页面

**Files:**
- Modify: `frontend/src/pages/Chat.tsx`
- Create: `frontend/src/pages/History.tsx`
- Create: `frontend/src/pages/Settings.tsx`

- [ ] **Step 1: Implement Chat page**

Write `frontend/src/pages/Chat.tsx`:
```typescript
import { useEffect, useState, useRef } from 'react'
import { useParams } from 'react-router-dom'
import { chatApi, ddlApi, Conversation, Message, DDLMeta } from '../api/client'
import SyntaxHighlighter from '../components/SyntaxHighlighter'
import LoadingSpinner from '../components/LoadingSpinner'

interface ChatMessage {
  role: 'user' | 'assistant'
  content: string
  sql?: string
}

export default function Chat() {
  const { convId } = useParams<{ convId: string }>()
  const [conv, setConv] = useState<Conversation | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [input, setInput] = useState('')
  const [sending, setSending] = useState(false)
  const [ddlList, setDdlList] = useState<DDLMeta[]>([])
  const [selectedDDL, setSelectedDDL] = useState('')
  const [targetDB, setTargetDB] = useState('PostgreSQL')
  const [creating, setCreating] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  useEffect(() => { scrollToBottom() }, [messages])

  // Load DDL list for new conversations
  useEffect(() => {
    ddlApi.list().then(setDdlList)
  }, [])

  // Load existing conversation
  useEffect(() => {
    if (!convId) return
    chatApi.get(convId).then(c => {
      setConv(c)
      setSelectedDDL(c.ddl_name)
      setTargetDB(c.target_db)
      const msgs: ChatMessage[] = []
      for (const m of c.messages || []) {
        if (m.role === 'user') {
          msgs.push({ role: 'user', content: m.content })
        } else if (m.role === 'assistant') {
          const sql = extractSQL(m.content)
          msgs.push({ role: 'assistant', content: m.content, sql })
        }
      }
      setMessages(msgs)
    })
  }, [convId])

  const extractSQL = (text: string): string | undefined => {
    const match = text.match(/```sql\s*([\s\S]*?)\s*```/)
    return match ? match[1].trim() : undefined
  }

  const handleCreate = async () => {
    if (!selectedDDL) return
    setCreating(true)
    try {
      const c = await chatApi.create({ ddl_name: selectedDDL, target_db: targetDB })
      setConv(c)
      setMessages([])
      // Update URL without navigation
      window.history.pushState(null, '', `/chat/${c.id}`)
    } catch (e: any) {
      alert(e.message)
    } finally {
      setCreating(false)
    }
  }

  const handleSend = async () => {
    const q = input.trim()
    if (!q || !conv) return
    setInput('')
    setMessages(prev => [...prev, { role: 'user', content: q }])
    setSending(true)
    try {
      const result = await chatApi.ask(conv.id, q)
      const sql = result.valid ? result.sql : undefined
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: result.explanation || result.raw_response,
        sql,
      }])
    } catch (e: any) {
      setMessages(prev => [...prev, { role: 'assistant', content: `错误: ${e.message}` }])
    } finally {
      setSending(false)
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // New conversation selector
  if (!conv) {
    return (
      <div>
        <h1 style={{ marginBottom: 24 }}>新对话</h1>
        <div style={{
          background: 'var(--bg-secondary)', borderRadius: 8, padding: 24,
          border: '1px solid var(--border)', maxWidth: 480,
        }}>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>选择 DDL</label>
            <select value={selectedDDL} onChange={e => setSelectedDDL(e.target.value)}>
              <option value="">-- 请选择 --</option>
              {ddlList.map(d => <option key={d.name} value={d.name}>{d.name}</option>)}
            </select>
          </div>
          <div style={{ marginBottom: 16 }}>
            <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>目标数据库</label>
            <input value={targetDB} onChange={e => setTargetDB(e.target.value)} placeholder="PostgreSQL" />
          </div>
          <button className="btn-primary" onClick={handleCreate} disabled={creating || !selectedDDL}>
            {creating ? '创建中...' : '开始对话'}
          </button>
        </div>
      </div>
    )
  }

  // Chat interface
  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: 'calc(100vh - 48px)' }}>
      <div style={{ marginBottom: 16 }}>
        <span style={{ color: 'var(--text-secondary)', fontSize: 14 }}>
          对话: {conv.ddl_name} → {conv.target_db}
        </span>
      </div>

      <div style={{
        flex: 1, overflow: 'auto', marginBottom: 16,
        display: 'flex', flexDirection: 'column', gap: 12,
        padding: '0 4px',
      }}>
        {messages.map((msg, i) => (
          <div key={i} style={{
            maxWidth: '80%',
            alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
          }}>
            <div style={{
              background: msg.role === 'user' ? 'var(--accent)' : 'var(--bg-secondary)',
              color: msg.role === 'user' ? 'var(--bg-primary)' : 'var(--text-primary)',
              borderRadius: 12,
              borderBottomRightRadius: msg.role === 'user' ? 4 : 12,
              borderBottomLeftRadius: msg.role === 'assistant' ? 4 : 12,
              padding: '8px 14px',
              fontSize: 14,
              lineHeight: 1.5,
            }}>
              {msg.content}
            </div>
            {msg.sql && (
              <div style={{ marginTop: 8, width: '100%' }}>
                <SyntaxHighlighter code={msg.sql} />
              </div>
            )}
          </div>
        ))}
        {sending && <LoadingSpinner text="思考中..." />}
        <div ref={messagesEndRef} />
      </div>

      <div style={{ display: 'flex', gap: 8 }}>
        <textarea
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="输入问题... (Enter 发送, Shift+Enter 换行)"
          rows={2}
          style={{
            flex: 1, resize: 'none', fontFamily: 'inherit',
            background: 'var(--bg-secondary)', border: '1px solid var(--border)',
            borderRadius: 8, padding: '10px 14px', color: 'var(--text-primary)',
            fontSize: 14,
          }}
        />
        <button
          className="btn-primary"
          onClick={handleSend}
          disabled={sending || !input.trim()}
          style={{ alignSelf: 'flex-end', height: 40 }}
        >
          发送
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 2: Implement History page**

Write `frontend/src/pages/History.tsx`:
```typescript
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { chatApi, Conversation } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'
import ConfirmDialog from '../components/ConfirmDialog'

export default function History() {
  const [convs, setConvs] = useState<Conversation[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [deleteTarget, setDeleteTarget] = useState<string | null>(null)
  const navigate = useNavigate()

  const load = async () => {
    setLoading(true)
    try {
      setConvs(await chatApi.list())
    } catch (e: any) {
      setError(e.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async () => {
    if (!deleteTarget) return
    try {
      await chatApi.delete(deleteTarget)
      setDeleteTarget(null)
      load()
    } catch (e: any) {
      setError(e.message)
    }
  }

  const formatDate = (s: string) => new Date(s).toLocaleString('zh-CN')

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>历史对话</h1>

      {error && <div style={{ color: 'var(--danger)', marginBottom: 16 }}>{error}</div>}

      {loading ? <LoadingSpinner text="加载中..." /> : convs.length === 0 ? (
        <div style={{ padding: 40, textAlign: 'center', color: 'var(--text-muted)' }}>
          <p style={{ fontSize: 16 }}>暂无历史对话</p>
        </div>
      ) : (
        <div style={{ display: 'grid', gap: 12 }}>
          {convs.map(conv => (
            <div
              key={conv.id}
              style={{
                background: 'var(--bg-secondary)', border: '1px solid var(--border)',
                borderRadius: 8, padding: '16px 20px',
                display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                cursor: 'pointer', transition: 'border-color 0.2s',
              }}
              onClick={() => navigate(`/chat/${conv.id}`)}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'var(--accent)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <div>
                <div style={{ fontWeight: 600, fontSize: 15, marginBottom: 4 }}>
                  {conv.ddl_name}
                  <span style={{ color: 'var(--text-muted)', fontWeight: 400 }}> → {conv.target_db}</span>
                </div>
                <div style={{ fontSize: 13, color: 'var(--text-secondary)' }}>
                  {conv.message_count} 条消息 · {formatDate(conv.created_at)}
                </div>
              </div>
              <button
                className="btn-danger"
                onClick={e => { e.stopPropagation(); setDeleteTarget(conv.id) }}
                style={{ fontSize: 13, padding: '4px 12px' }}
              >
                删除
              </button>
            </div>
          ))}
        </div>
      )}

      <ConfirmDialog
        open={!!deleteTarget}
        title="确认删除"
        message={`确定要删除此对话吗？此操作不可撤销。`}
        confirmLabel="删除"
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  )
}
```

- [ ] **Step 3: Implement Settings page**

Write `frontend/src/pages/Settings.tsx`:
```typescript
import { useEffect, useState } from 'react'
import { configApi, ConfigDisplay } from '../api/client'
import LoadingSpinner from '../components/LoadingSpinner'

export default function Settings() {
  const [config, setConfig] = useState<ConfigDisplay | null>(null)
  const [exists, setExists] = useState(false)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  // Init form state
  const [baseUrl, setBaseUrl] = useState('')
  const [apiKey, setApiKey] = useState('')
  const [model, setModel] = useState('gpt-4o')

  const load = async () => {
    setLoading(true)
    try {
      const status = await configApi.status()
      setExists(status.exists)
      if (status.exists) {
        const c = await configApi.get()
        setConfig(c)
        setBaseUrl(c.base_url)
        setModel(c.model)
      }
    } catch {
      // Config may not exist
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleSave = async () => {
    setError('')
    setSuccess('')
    setSaving(true)
    try {
      if (exists) {
        // Update individual fields that changed
        if (baseUrl !== config?.base_url) await configApi.update('base_url', baseUrl)
        if (apiKey) await configApi.update('api_key', apiKey)
        if (model !== config?.model) await configApi.update('model', model)
      } else {
        await configApi.init({ base_url: baseUrl, api_key: apiKey, model })
      }
      setSuccess('配置已保存')
      load()
    } catch (e: any) {
      setError(e.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <LoadingSpinner text="加载中..." />

  return (
    <div>
      <h1 style={{ marginBottom: 24 }}>设置</h1>

      <div style={{
        background: 'var(--bg-secondary)', borderRadius: 8, padding: 24,
        border: '1px solid var(--border)', maxWidth: 480,
      }}>
        {error && <div style={{ color: 'var(--danger)', marginBottom: 12, fontSize: 14 }}>{error}</div>}
        {success && <div style={{ color: 'var(--success)', marginBottom: 12, fontSize: 14 }}>{success}</div>}

        {exists && config && (
          <div style={{
            background: 'var(--bg-tertiary)', borderRadius: 6, padding: 12, marginBottom: 20,
            fontSize: 13, color: 'var(--text-secondary)',
          }}>
            <div>当前配置: {config.provider} / {config.model}</div>
            <div>API Key: {config.api_key}</div>
          </div>
        )}

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            Base URL
          </label>
          <input value={baseUrl} onChange={e => setBaseUrl(e.target.value)} placeholder="https://api.openai.com/v1" />
        </div>

        <div style={{ marginBottom: 16 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            API Key {exists && '(留空则不修改)'}
          </label>
          <input
            type="password"
            value={apiKey}
            onChange={e => setApiKey(e.target.value)}
            placeholder={exists ? '输入新 Key 以修改' : 'sk-...'}
          />
        </div>

        <div style={{ marginBottom: 24 }}>
          <label style={{ display: 'block', marginBottom: 4, fontSize: 13, color: 'var(--text-secondary)' }}>
            Model
          </label>
          <input value={model} onChange={e => setModel(e.target.value)} placeholder="gpt-4o" />
        </div>

        <button className="btn-primary" onClick={handleSave} disabled={saving}>
          {saving ? '保存中...' : '保存'}
        </button>
      </div>
    </div>
  )
}
```

- [ ] **Step 4: Verify frontend build**

```bash
cd d:/python/学习打包/my-tool/frontend
npx tsc --noEmit
npm run build
```

Expected: Build succeeds with no errors.

- [ ] **Step 5: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: implement Chat, History, and Settings pages"
```

---

### Task 6: 生产构建集成

**Files:**
- Modify: `src/my_tool/api/server.py`
- Create: `frontend/start.sh`
- Modify: `README.md`

- [ ] **Step 1: Update server.py to serve static files in production**

Update `src/my_tool/api/server.py`:
```python
from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from my_tool.api.routes_ddl import router as ddl_router
from my_tool.api.routes_chat import router as chat_router
from my_tool.api.routes_config import router as config_router


def create_app(base_path: Path | None = None) -> FastAPI:
    if base_path is None:
        import os
        env_home = os.environ.get("MY_TOOL_HOME")
        base_path = Path(env_home) if env_home else Path.cwd()

    app = FastAPI(title="DDL-to-SQL API", version="0.1.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.state.base_path = base_path

    app.include_router(ddl_router, prefix="/api")
    app.include_router(chat_router, prefix="/api")
    app.include_router(config_router, prefix="/api")

    # Serve frontend static files in production
    frontend_dist = Path(__file__).resolve().parent.parent.parent.parent / "frontend" / "dist"
    if frontend_dist.exists():
        app.mount("/", StaticFiles(directory=str(frontend_dist), html=True), name="frontend")

    return app


app = create_app()
```

- [ ] **Step 2: Create start script**

Write `frontend/start.sh`:
```bash
#!/usr/bin/env bash
# Start the DDL-to-SQL web application
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

echo "Building frontend..."
cd "$SCRIPT_DIR"
npm run build

echo "Starting backend server..."
cd "$PROJECT_DIR"
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
```

- [ ] **Step 3: Create start.bat for Windows**

Write `frontend/start.bat`:
```bat
@echo off
REM Start the DDL-to-SQL web application

cd /d "%~dp0"
echo Building frontend...
call npm run build
if %ERRORLEVEL% neq 0 exit /b %ERRORLEVEL%

cd /d "%~dp0.."
echo Starting backend server...
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
```

- [ ] **Step 4: Update README.md**

Append to `README.md`:
```markdown
## Web 前端

DDL-to-SQL 提供了一个本地 Web 前端界面。

### 开发模式

需要两个终端：

```bash
# 终端 1：启动后端 API
uv run uvicorn my_tool.api.server:app --reload --port 8000

# 终端 2：启动前端开发服务器
cd frontend
npm run dev
```

打开 http://localhost:5173 即可使用。

### 生产模式

```bash
cd frontend
npm run build
cd ..
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
```

打开 http://localhost:8000 即可使用。

### 一键启动

Windows:
```bat
frontend\start.bat
```

Linux/macOS:
```bash
chmod +x frontend/start.sh
./frontend/start.sh
```
```

- [ ] **Step 5: Verify production build**

```bash
cd d:/python/学习打包/my-tool/frontend
npm run build
```

Expected: Build succeeds.

```bash
cd d:/python/学习打包/my-tool
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
```

Open http://localhost:8000 in browser. Expected: Frontend loads, API calls work.

- [ ] **Step 6: Add .gitignore entries**

Append to `.gitignore`:
```gitignore
# Frontend
frontend/node_modules/
frontend/dist/
```

- [ ] **Step 7: Commit**

```bash
cd d:/python/学习打包/my-tool
git add -A
git commit -m "feat: production build integration, start scripts, README"
```

---

## Spec Coverage Check

| Spec Requirement | Task |
|---|---|
| FastAPI backend app factory | Task 1 Step 3 |
| DDL CRUD (list/add/get/delete) | Task 1 Step 4 |
| CORS middleware for Vite | Task 1 Step 3 |
| Conversation create/ask/list/get/delete | Task 2 Step 1 |
| Config get/update/init/status | Task 2 Step 2 |
| React + Vite + TypeScript scaffold | Task 3 Steps 1-8 |
| Layout + Sidebar | Task 3 Steps 4-5 |
| React Router 6 routes | Task 3 Step 6 |
| API client (fetch) | Task 4 Step 1 |
| SyntaxHighlighter (highlight.js) | Task 4 Step 2 |
| ConfirmDialog / LoadingSpinner | Task 4 Step 2 |
| DDLList page | Task 4 Step 4 |
| DDLDetail page | Task 4 Step 5 |
| DDLUploadModal | Task 4 Step 3 |
| Chat page (messages + send) | Task 5 Step 1 |
| History page | Task 5 Step 2 |
| Settings page | Task 5 Step 3 |
| Production static file serve | Task 6 Step 1 |
| Start scripts | Task 6 Steps 2-3 |
| README documentation | Task 6 Step 4 |
