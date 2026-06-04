# DDL-to-SQL Web 前端设计文档

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this spec task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**目标**：为 DDL-to-SQL 工具构建一个本地 Web 前端，覆盖 DDL 管理、智能对话、对话历史、LLM 配置管理全部功能。

**技术栈**：
- 后端：Python FastAPI，直接复用现有 Service/Core/Storage 层
- 前端：React 18 + TypeScript + Vite + React Router
- 通信：REST API（JSON），开发期双进程，生产期 FastAPI serve 静态文件

---

## 整体架构

```
my-tool/
├── src/my_tool/
│   ├── ...                   # 现有 Python 层（不变）
│   └── api/                  # [新增] REST API 层
│       ├── __init__.py
│       ├── server.py         # FastAPI 应用、启动入口
│       ├── routes_ddl.py     # DDL CRUD 路由
│       ├── routes_chat.py    # 对话路由
│       └── routes_config.py  # 配置路由
├── frontend/                 # [新增] React 前端
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/              # HTTP 请求封装
│       │   └── client.ts
│       ├── components/       # 共享组件
│       │   ├── Layout.tsx
│       │   ├── Sidebar.tsx
│       │   ├── SyntaxHighlighter.tsx
│       │   ├── ConfirmDialog.tsx
│       │   └── LoadingSpinner.tsx
│       └── pages/            # 页面组件
│           ├── DDLList.tsx
│           ├── DDLDetail.tsx
│           ├── DDLUploadModal.tsx
│           ├── Chat.tsx
│           ├── History.tsx
│           └── Settings.tsx
└── tests/                    # 现有测试
```

## 后端 API 设计

### 通用约定
- 基础路径：`/api`
- 请求/响应格式：JSON
- 错误响应：`{"detail": "错误信息"}`
- 状态码：200 成功，404 未找到，409 冲突，422 参数错误

### 1. DDL 管理

```
GET    /api/ddls                    # DDL 列表
POST   /api/ddls                    # 添加 DDL
GET    /api/ddls/{name}             # DDL 详情
DELETE /api/ddls/{name}             # 删除 DDL
```

**POST /api/ddls** 请求体：
```json
{
  "name": "电商系统",
  "text": "CREATE TABLE users (...)",
  "file_path": null,
  "tags": ["MySQL", "生产"],
  "force": false
}
```

### 2. 对话

```
POST   /api/conversations                    # 创建对话
POST   /api/conversations/{id}/ask            # 提问
GET    /api/conversations                     # 对话列表
GET    /api/conversations/{id}                # 对话详情
DELETE /api/conversations/{id}                # 删除对话
```

**POST /api/conversations** 请求体：
```json
{
  "ddl_name": "电商系统",
  "target_db": "PostgreSQL"
}
```

**POST /api/conversations/{id}/ask** 请求体：
```json
{
  "question": "查询销量前10的商品"
}
```
响应：
```json
{
  "sql": "SELECT ...",
  "raw_response": "...",
  "explanation": "查询逻辑说明",
  "valid": true,
  "messages": [...]
}
```

### 3. 配置

```
GET    /api/config                  # 查看配置（API Key 脱敏）
PUT    /api/config                  # 更新单个配置项
POST   /api/config/init             # 初始化配置
GET    /api/config/status           # 配置是否已存在
```

## 前端组件设计

### 布局

```
┌─────────────────────────────────────┐
│  Sidebar    │  Content Area          │
│             │                        │
│  [Logo]     │  Breadcrumb            │
│             │                        │
│  ● DDL 管理 │  Page Content          │
│  ○ 对话     │  (React Router)        │
│  ○ 历史     │                        │
│  ○ 设置     │                        │
│             │                        │
│  v0.1.0     │                        │
└─────────────────────────────────────┘
```

- 左侧固定宽度侧边栏（240px），右侧内容区自适应
- 侧边栏高亮当前路由，点击切换页面
- 内容区顶部面包屑，下方页面内容

### 页面

**DDLList** — DDL 列表页
- 顶部：标题 + "添加 DDL" 按钮
- 列表：卡片或表格，展示名称、标签、表数量、创建时间
- 操作：查看详情、删除
- 空状态：友好的提示引导

**DDLDetail** — DDL 详情页
- 元数据：名称、标签、表数量
- 内容：SQL 语法高亮（带行号）
- 操作：返回列表

**DDLUploadModal** — 添加 DDL 弹窗
- 名称输入框
- 两种输入方式：文本输入（textarea）或文件上传
- 标签输入
- force 覆盖选项

**Chat** — 对话页
- 消息列表（滚动到底部自动跟随）
- 用户消息靠右，助手消息靠左
- SQL 代码块用 SyntaxHighlighter 渲染（带复制按钮）
- 底部输入框 + 发送按钮
- 输入 Enter 发送，Shift+Enter 换行

**History** — 历史对话列表
- 卡片列表：对话ID、DDL名、目标数据库、消息数、时间
- 点击进入继续对话
- 空状态提示

**Settings** — 配置页
- 表单：Base URL、API Key（密码框）、Model
- 保存按钮
- 若已配置：显示当前值（API Key 脱敏），可修改

### 共享组件

- **SyntaxHighlighter**：基于 highlight.js 或 prism，SQL 语法高亮，带复制按钮
- **ConfirmDialog**：删除确认弹窗
- **LoadingSpinner**：加载中状态
- **Layout**：侧边栏 + 内容区框架
- **Sidebar**：导航菜单

## 运行方式

### 开发模式（两个终端）

```bash
# 终端 1：启动 FastAPI 后端
cd my-tool
uv run uvicorn my_tool.api.server:app --reload --port 8000

# 终端 2：启动 React 前端
cd my-tool/frontend
npm run dev    # Vite dev server on port 5173
```

Vite 配置代理 `/api` → `localhost:8000`。

### 生产模式

```bash
cd my-tool/frontend
npm run build
# 静态文件产出到 frontend/dist/
# FastAPI 启动时自动 serve dist/ 目录
```

## 依赖

**Python 新增依赖**：
- `fastapi>=0.109.0`
- `uvicorn[standard]>=0.27.0`

**前端依赖**：
- `react`, `react-dom`
- `react-router-dom`
- `@types/react`, `@types/react-dom`
- `typescript`
- `vite`
- `@vitejs/plugin-react`
- `highlight.js`（SQL 语法高亮）

## 实施计划

实施分为 6 个任务，按依赖顺序：

### Task 1: FastAPI 后端 + DDL 路由
- 添加 fastapi/uvicorn 依赖
- 创建 `api/` 包
- 实现 `server.py`（FastAPI 应用工厂）
- 实现 `routes_ddl.py`（DDL CRUD，直接调用 DDLService）
- 测试 API 端点

### Task 2: 对话 & 配置路由
- 实现 `routes_chat.py`（创建/提问/列表/详情/删除）
- 实现 `routes_config.py`（查看/更新/初始化/状态）
- 测试所有端点

### Task 3: React 项目脚手架 + 布局
- 用 Vite 初始化 frontend/
- 配置 TypeScript、React Router
- 实现 Layout + Sidebar 组件
- 实现页面路由和导航切换

### Task 4: DDL 管理页面
- 实现 API client（fetch 封装）
- DDLList 页面（列表 + 添加按钮）
- DDLUploadModal（文本/文件上传）
- DDLDetail 页面（语法高亮）

### Task 5: 对话 & 历史页面
- Chat 页面（消息列表 + 输入框）
- SQL 代码高亮 + 复制按钮
- History 页面
- Settings 页面

### Task 6: 生产构建集成
- Vite build 配置
- FastAPI 静态文件 serve
- 一键启动脚本
- README 更新
