# DDL-to-SQL 智能查询工具

> 上传数据库 DDL 定义，用自然语言提问，自动生成 SQL 查询语句。

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)]()
[![License](https://img.shields.io/badge/license-MIT-green.svg)]()

---

## 📖 简介

本工具允许用户上传数据库表结构定义（DDL），然后通过自然语言提问，借助 LLM（大语言模型）自动生成对应的 SQL 查询语句。支持多轮对话、多数据库方言、历史记录管理。

### 适用场景

- **数据分析师**：快速查询数据库，无需手写复杂 SQL
- **开发者**：原型开发阶段快速验证查询逻辑
- **DBA**：日常查询辅助，减少重复劳动

---

## ✨ 功能特性

| 功能 | 说明 |
|------|------|
| **DDL 管理** | 通过文本或文件上传 DDL，支持标签分类、列表/查看/删除 |
| **智能问答** | 基于已上传的 DDL，用自然语言提问生成 SQL |
| **多轮对话** | 支持对话历史，可基于上下文继续追问 |
| **多数据库方言** | 支持 MySQL、PostgreSQL、SQLite、MaxCompute |
| **对话历史** | 自动保存对话记录，支持继续上一次对话 |
| **LLM 配置** | 支持任意 OpenAI 兼容 API（DeepSeek、GPT、Claude 等） |
| **流式输出** | LLM 响应流式处理，大响应无阻塞 |
| **SQL 验证** | 自动提取和基础校验生成的 SQL 语句 |

---

## 🏗 架构设计

四层架构，各层职责清晰，方便后续扩展（如 API/Web 接入）：

```
┌─────────────────────────────────────────────────┐
│                   CLI 层 (cli/)                  │
│    Typer 命令：config / ddl / chat              │
│    Rich 输出：表格、语法高亮、面板              │
├─────────────────────────────────────────────────┤
│              业务逻辑层 (service/)               │
│    ConfigService / DDLService / ChatService     │
│    校验、编排、错误处理                         │
├──────────────────┬──────────────────────────────┤
│  核心层 (core/)  │   存储层 (storage/)          │
│  LLMClient       │   ConfigStore (TOML)         │
│  PromptBuilder   │   DDLStore (文件系统)        │
│  SQLParser       │   ConversationStore (JSON)   │
└──────────────────┴──────────────────────────────┘
```

### 目录结构

```
my-tool/
├── src/my_tool/
│   ├── __init__.py           # 版本号
│   ├── main.py               # 入口点，组装子命令
│   ├── models.py             # Pydantic 数据模型
│   ├── cli/                  # 命令行界面
│   │   ├── config_cmd.py     # config init/set/show
│   │   ├── ddl_cmd.py        # ddl add/list/show/delete
│   │   └── chat_cmd.py       # chat start/continue/history
│   ├── service/              # 业务逻辑
│   │   ├── config_service.py
│   │   ├── ddl_service.py
│   │   └── chat_service.py
│   ├── core/                 # 核心能力
│   │   ├── llm_client.py     # OpenAI 兼容 API 客户端
│   │   ├── prompt_builder.py # 提示词构建
│   │   └── sql_parser.py     # SQL 提取与验证
│   └── storage/              # 持久化
│       ├── config_store.py
│       ├── ddl_store.py
│       └── conversation_store.py
└── tests/                    # 94 个测试用例
```

---

## 🚀 快速开始

### 环境要求

- Python >= 3.11
- [uv](https://docs.astral.sh/uv/) 包管理器（推荐）或 pip

### 安装

```bash
# 克隆项目
git clone <repo-url>
cd my-tool

# 使用 uv 安装（推荐）
uv sync
uv run my-tool --help

# 或使用 pip
pip install -e .
my-tool --help
```

### 配置 LLM

首次使用需要配置 LLM API（支持任意 OpenAI 兼容接口）：

```bash
# 交互式配置（推荐）
my-tool config init

# 或命令行参数
my-tool config init \
  --base-url https://api.deepseek.com/v1 \
  --api-key sk-your-api-key \
  --model deepseek-chat
```

支持任意 OpenAI 兼容 API：
- **DeepSeek**：`https://api.deepseek.com/v1`
- **OpenAI**：`https://api.openai.com/v1`
- **Azure OpenAI**：你的 Azure 部署端点
- **本地模型**：`http://localhost:11434/v1`（Ollama）

查看和修改配置：

```bash
# 查看当前配置（API Key 自动脱敏显示）
my-tool config show

# 修改单个配置项
my-tool config set model gpt-4o
my-tool config set base_url https://api.openai.com/v1
```

---

## 📘 使用指南

### 1️⃣ DDL 管理

```bash
# 通过文本添加 DDL
my-tool ddl add 电商系统 \
  --text "CREATE TABLE users (id INT PRIMARY KEY, name VARCHAR(100), email VARCHAR(200)); CREATE TABLE orders (id INT PRIMARY KEY, user_id INT, amount DECIMAL(10,2));" \
  --tag 生产 --tag MySQL

# 从 SQL 文件导入
my-tool ddl add 财务系统 --file ./schema.sql

# 覆盖已存在的 DDL
my-tool ddl add 电商系统 --text "..." --force

# 查看 DDL 列表
my-tool ddl list

# 查看 DDL 详情（含语法高亮）
my-tool ddl show 电商系统

# 删除 DDL
my-tool ddl delete 电商系统
```

### 2️⃣ 智能对话

```bash
# 基于某个 DDL 开始新对话
my-tool chat start 电商系统 --target-db PostgreSQL

# 或交互式选择目标数据库
my-tool chat start 电商系统

# 继续上一次对话
my-tool chat continue

# 继续指定对话
my-tool chat continue conv-20260603-电商系统-a1b2c3

# 查看对话历史
my-tool chat history
```

### 3️⃣ 完整工作流示例

```bash
# 1. 配置 LLM
my-tool config init --base-url https://api.deepseek.com/v1 --api-key sk-xxx

# 2. 上传 DDL
my-tool ddl add 电商系统 --text "
CREATE TABLE users (
  id INT PRIMARY KEY,
  name VARCHAR(100),
  email VARCHAR(200),
  created_at TIMESTAMP
);
CREATE TABLE orders (
  id INT PRIMARY KEY,
  user_id INT,
  product VARCHAR(100),
  amount DECIMAL(10,2),
  status VARCHAR(20),
  ordered_at TIMESTAMP
);
"

# 3. 智能问答
my-tool chat start 电商系统 --target-db PostgreSQL
# > 查询所有用户的订单总数
# > 找出消费金额最高的前10名用户
# > 统计本月各商品的销售数量
```

---

## 🧪 开发与测试

### 运行测试

```bash
# 运行全部 94 个测试
uv run env PYTHONPATH=src pytest

# 运行特定测试文件
uv run env PYTHONPATH=src pytest tests/test_sql_parser.py

# 运行特定测试类
uv run env PYTHONPATH=src pytest tests/test_chat_service.py::TestChatService

# 带覆盖率报告
uv run env PYTHONPATH=src pytest --cov=my_tool
```

> **Windows 用户注意**：如果遇到 `VIRTUAL_ENV` 环境变量冲突，使用 `uv run env PYTHONPATH=src pytest` 替代直接调用。

### 项目技术栈

| 组件 | 技术 |
|------|------|
| CLI 框架 | [Typer](https://typer.tiangolo.com/) |
| 终端输出 | [Rich](https://rich.readthedocs.io/) |
| 数据模型 | [Pydantic v2](https://docs.pydantic.dev/) |
| LLM API | [OpenAI Python SDK](https://pypi.org/project/openai/) |
| 交互输入 | [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) |
| 构建系统 | [uv](https://docs.astral.sh/uv/) |
| 测试框架 | [pytest](https://docs.pytest.org/) |

---

## 📁 数据存储

所有数据存储在工具的**运行目录**下（可通过 `MY_TOOL_HOME` 环境变量自定义）：

```
./my-tool-home/
├── config.toml           # LLM 配置
├── ddl/
│   ├── 电商系统/
│   │   ├── schema.ddl    # DDL 原始内容
│   │   └── meta.json     # 元数据（标签、表数量等）
│   └── 财务系统/
│       ├── schema.ddl
│       └── meta.json
└── conversations/
    ├── conv-20260603-电商系统-a1b2c3.json
    └── conv-20260603-财务系统-d4e5f6.json
```

---

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `MY_TOOL_HOME` | 数据存储根目录 | 当前工作目录 |

---

## 🔧 常见问题

**Q: 支持哪些 LLM 提供商？**
A: 任何 OpenAI 兼容 API 均可，包括 DeepSeek、OpenAI、Azure OpenAI、Ollama 本地模型等。

**Q: SQL 生成结果不准确怎么办？**
A: 确保 DDL 定义完整（包含字段类型、约束、外键等），并在问题中提供足够的上下文。多轮对话中可对结果进行追问修正。

**Q: 如何更换 LLM 模型？**
A: 使用 `my-tool config set model <新模型名>` 即可，无需重新初始化。

**Q: 对话记录存在哪里？**
A: 存储在运行目录的 `conversations/` 文件夹中，JSON 格式，可手动查看和备份。

---

## 📄 License

MIT

---

## 🌐 Web 前端

DDL-to-SQL 提供了一个本地 Web 前端界面，以图形化方式替代命令行操作，支持 DDL 管理、智能对话、历史记录、配置管理等全部核心功能。

> **技术栈**：React 18 + TypeScript + Vite（前端），FastAPI（后端 API）

---

### 环境要求

| 依赖 | 版本 | 说明 |
|------|------|------|
| Python | >= 3.11 | 后端 API 服务 |
| Node.js | >= 18 | 前端构建和开发服务器（[下载](https://nodejs.org/)） |
| npm | >= 9 | 随 Node.js 一同安装 |

> **首次使用前**，确保已执行 `uv sync` 安装 Python 依赖，并完成 LLM 配置（`my-tool config init` 或通过 Web 界面配置）。

---

### 安装前端依赖

```bash
cd frontend
npm install
```

> 只需执行一次，或在 `package.json` 更新后重新执行。

---

### 开发模式

前后端分离运行，支持热更新，适合开发调试：

```bash
# 终端 1：启动后端 API 服务（端口 8000）
uv run uvicorn my_tool.api.server:app --reload --port 8000

# 终端 2：启动前端开发服务器（端口 5173）
cd frontend
npm run dev
```

- 前端开发服务器运行在 **http://localhost:5173**
- `/api/*` 请求自动代理到后端 `http://localhost:8000`
- 修改前端代码后页面自动热更新，无需手动刷新

---

### 生产模式

先构建前端静态文件，再由后端统一提供服务（单进程，端口 8000）：

```bash
# 1. 构建前端
cd frontend
npm run build

# 2. 启动后端（自动托管前端静态文件）
cd ..
uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000
```

- 所有资源由后端统一在 **http://localhost:8000** 提供
- 前端构建产物位于 `frontend/dist/`（已加入 `.gitignore`）

---

### 一键启动

项目提供了一键启动脚本，自动完成前端构建和后端启动：

**Windows（双击运行）：**
```bat
frontend\start.bat
```

**Linux/macOS：**
```bash
chmod +x frontend/start.sh
./frontend/start.sh
```

脚本执行流程：
1. `cd frontend && npm run build` — 构建前端
2. `uv run uvicorn my_tool.api.server:app --host 127.0.0.1 --port 8000` — 启动后端

打开 **http://localhost:8000** 即可使用。

---

### Web 界面使用指南

#### 🏠 页面概览

```
┌─────────────────────────────────────────────────┐
│  DDL-to-SQL  v0.1.0       │ DDL管理 │ 对话 │ 历史 │ 设置 │
│  ─────────────────────────────────────────────── │
│  │                                             │
│  │  ┌───────┐  ┌───────┐  ┌───────┐          │
│  │  │ DDL-1 │  │ DDL-2 │  │ DDL-3 │  ...     │
│  │  └───────┘  └───────┘  └───────┘          │
│  │                                             │
│  └─────────────────────────────────────────────┘
```

左侧边栏包含 4 个导航入口：
- **DDL 管理** — 上传、查看、删除 DDL
- **对话** — 基于 DDL 进行智能问答
- **历史** — 查看和继续历史对话
- **设置** — 配置 LLM API

---

#### ① DDL 管理页面（`/ddls`）

**DDL 列表：**
- 以卡片形式展示所有已上传的 DDL
- 每张卡片显示：名称、表数量、标签、创建时间
- 点击卡片进入详情页
- 点击 ❌ 按钮删除 DDL（弹出确认对话框）

**上传 DDL：**
- 点击"上传 DDL"按钮打开上传弹窗
- **名称**：必填，DDL 的唯一标识
- **DDL 内容**：必填，粘贴 SQL DDL 语句（`CREATE TABLE` 等）
- **标签**：可选，逗号分隔（如 `MySQL, 生产环境`）
- **覆盖**：勾选后可覆盖已存在的同名 DDL（否则重名会报错）

**DDL 详情页（`/ddls/:name`）：**
- 展示 DDL 元数据（名称、表数量、标签、创建时间、更新时间）
- SQL 内容高亮显示，支持一键复制

---

#### ② 对话页面（`/chat`）

**新建对话：**
- 选择一个已上传的 DDL
- 输入目标数据库类型（如 `PostgreSQL`、`MySQL`、`SQLite`、`MaxCompute`）
- 点击"开始对话"

**进行对话：**
- 在输入框输入自然语言问题（如"查询所有用户的订单总数"）
- 按 `Enter` 发送，`Shift+Enter` 换行
- AI 回复将展示文字解释 + SQL 代码块（语法高亮）
- 可连续追问，上下文自动保持

**继续历史对话：**
- 通过 URL `/chat/:convId` 直接进入指定对话
- 或在"历史"页面点击对话卡片进入

---

#### ③ 历史页面（`/history`）

- 以卡片列表展示所有历史对话记录
- 每张卡片显示：对话 ID、关联 DDL 名称、目标数据库
- 点击卡片跳转到该对话，可继续提问
- 点击 ❌ 按钮删除对话（弹出确认对话框）

---

#### ④ 设置页面（`/settings`）

- **查看配置**：自动加载并展示当前 LLM 配置
- **初始化配置**：如果尚未配置，点击"初始化配置"按钮
- **修改配置项**：
  - **API 地址（base_url）**：如 `https://api.deepseek.com/v1`
  - **API Key**：密码输入框，已保存的 Key 会脱敏显示（`sk-****`）
  - **模型名（model）**：如 `deepseek-chat`、`gpt-4o`、`claude-sonnet-4-20250514`
  - 每个字段独立保存，仅保存有改动的字段

---

#### 完整使用流程示例

```text
1. 打开 http://localhost:8000 → 自动跳转到 DDL 管理页面
2. 先进入"设置"，配置 LLM API（base_url / api_key / model）
3. 回到"DDL 管理"，点击"上传 DDL"，输入表结构和名称
4. 进入"对话"，选择刚上传的 DDL，输入目标数据库，点击"开始对话"
5. 输入自然语言查询 → 获得 AI 生成的 SQL
6. 可继续追问或返回历史记录查看
```

---

### 常见问题

**Q: 前端页面白屏 / 无法加载？**
A: 
- 开发模式：确认两个终端都已启动，访问 `http://localhost:5173`
- 生产模式：确认已执行 `npm run build`，访问 `http://localhost:8000`
- 检查浏览器控制台是否有网络错误

**Q: API 请求返回 422 或 CORS 错误？**
A:
- 开发模式：确保前端开发服务器在 `localhost:5173` 运行，后端在 `localhost:8000`
- Vite 代理配置在 `frontend/vite.config.ts` 中，确保 `/api` 代理指向正确的后端地址

**Q: `npm install` 报错？**
A: 确保 Node.js >= 18，npm >= 9。可尝试删除 `node_modules/` 后重新安装：
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

**Q: `npm run build` 构建失败？**
A: 检查 TypeScript 类型错误：
```bash
cd frontend
npx tsc --noEmit
```
根据错误提示修类型后再重新构建。

**Q: 如何更换前端端口？**
A: 修改 `frontend/vite.config.ts` 中的 `server.port` 字段，同时更新后端 CORS 配置中的 `allow_origins`。
