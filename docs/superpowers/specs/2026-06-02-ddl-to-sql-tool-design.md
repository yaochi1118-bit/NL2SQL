# DDL-to-SQL 智能查询工具 — 设计文档

## 概述

一个 CLI 工具，支持用户上传数据库 DDL（表结构定义），然后基于 LLM（OpenAI 兼容 API）将自然语言问题转化为对应数据库方言的 SQL 查询语句。

**核心理念：** 先做 CLI 工具，架构上做好分层，后续可低成本升级为 API 服务或 Web 应用。

---

## 1. 技术栈

| 组件 | 选型 | 说明 |
|------|------|------|
| 语言 | Python >= 3.11 | 项目已有 |
| 构建 | uv | 项目已有 |
| CLI 框架 | [Typer](https://typer.tiangolo.com/) | 基于 Click，支持自动补全 |
| 终端美化 | [Rich](https://rich.readthedocs.io/) | 彩色输出、表格、Markdown 渲染 |
| LLM SDK | [openai](https://pypi.org/project/openai/) | OpenAI 兼容 API 官方 SDK |
| 数据校验 | [Pydantic](https://docs.pydantic.dev/) | 配置/数据结构校验 |
| TOML 写入 | [tomli-w](https://pypi.org/project/tomli-w/) | 读取用标准库 `tomllib` |
| 交互输入 | [prompt-toolkit](https://python-prompt-toolkit.readthedocs.io/) | 对话模式增强输入体验 |

---

## 2. 项目目录结构

```
my-tool/
├── pyproject.toml
├── config.toml                     # LLM 等全局配置（用户可编辑）
├── ddl/                            # DDL 存储目录
│   ├── <project-name>/
│   │   ├── schema.ddl              # 原始 DDL 内容
│   │   └── meta.json               # 元信息（名称、标签、创建时间等）
│   └── ...
├── conversations/                  # 对话历史存储
│   └── conv-<timestamp>-<name>-<id>.json
└── src/
    └── my_tool/
        ├── __init__.py
        ├── main.py                 # CLI 入口
        ├── cli/
        │   ├── __init__.py
        │   ├── ddl_cmd.py          # ddl 子命令
        │   ├── chat_cmd.py         # chat 子命令
        │   └── config_cmd.py       # config 子命令
        ├── service/
        │   ├── __init__.py
        │   ├── ddl_service.py      # DDL 管理业务逻辑
        │   ├── chat_service.py     # 对话/生成 SQL 业务逻辑
        │   └── config_service.py   # 配置管理业务逻辑
        ├── core/
        │   ├── __init__.py
        │   ├── llm_client.py       # OpenAI 兼容 API 客户端封装
        │   ├── prompt_builder.py   # Prompt 模板构建
        │   └── sql_parser.py       # SQL 提取与基本校验
        └── storage/
            ├── __init__.py
            ├── ddl_store.py        # DDL 文件读写管理
            └── conversation_store.py  # 对话历史持久化
```

### 层级职责

```
┌─────────────────────────────────────┐
│  CLI 层 (cli/)                       │
│  命令解析、参数校验、终端输出展示     │
│  依赖 → service 层                    │
├─────────────────────────────────────┤
│  服务层 (service/)                    │
│  业务编排、调用 core + storage        │
│  依赖 → core 层 + storage 层          │
├─────────────────────────────────────┤
│  核心层 (core/)                       │
│  LLM 调用、Prompt 构建、SQL 处理      │
│  纯逻辑，无状态，无 I/O               │
├─────────────────────────────────────┤
│  存储层 (storage/)                    │
│  文件读写操作、数据持久化             │
│  只操作文件系统                       │
└─────────────────────────────────────┘
```

---

## 3. 配置设计 (`config.toml`)

```toml
[llm]
provider = "openai-compatible"
base_url = "https://api.deepseek.com/v1"
api_key = "sk-xxxxxxxxxxxxxxxx"
model = "deepseek-chat"
```

配置管理方式：
- `my-tool config init` — 交互式引导创建 `config.toml`
- `my-tool config set <key> <value>` — 修改配置项（如 `my-tool config set model gpt-4o`）
- `my-tool config show` — 查看当前配置（API Key 脱敏显示）

---

## 4. CLI 命令设计

### 配置命令

| 命令 | 说明 |
|------|------|
| `my-tool config init` | 交互式初始化配置文件 |
| `my-tool config set <key> <value>` | 设置配置项 |
| `my-tool config show` | 查看当前配置 |

### DDL 管理命令

| 命令 | 说明 |
|------|------|
| `my-tool ddl add <name> --file <path>` | 从文件添加 DDL |
| `my-tool ddl add <name> --text "<ddl>"` | 从文本添加 DDL |
| `my-tool ddl add <name> --file <path> --tag <tag>` | 添加 DDL 并打标签 |
| `my-tool ddl list` | 列出所有 DDL（表格展示） |
| `my-tool ddl show <name>` | 查看 DDL 详情 |
| `my-tool ddl delete <name>` | 删除指定 DDL |

### 对话命令

| 命令 | 说明 |
|------|------|
| `my-tool chat start <ddl-name>` | 开始新对话（会提示选择目标数据库） |
| `my-tool chat continue` | 继续上一次对话 |
| `my-tool chat history` | 查看对话历史列表 |

### 完整使用流程

```bash
# 1. 初始化
my-tool config init

# 2. 上传 DDL
my-tool ddl add 电商系统 --file ./schema.sql --tag 生产

# 3. 开始对话
my-tool chat start 电商系统
# → 提示选择目标数据库：MySQL / PostgreSQL / SQLite / MaxCompute
# → 进入交互式对话模式，用户提问，AI 生成 SQL

# 4. 继续上次对话
my-tool chat continue

# 5. 管理 DDL
my-tool ddl list
my-tool ddl delete 电商系统
```

---

## 5. 核心模块设计

### 5.1 LLM 客户端 (`core/llm_client.py`)

封装 OpenAI 兼容 API 的调用：

```python
class LLMClient:
    def __init__(self, config: LLMConfig): ...
    def chat(self, messages: list[dict], stream: bool = True) -> str: ...
```

- 使用 `openai` SDK，配置 `base_url` + `api_key`
- 支持流式输出，用户能看到字符逐字生成
- 统一的错误处理（网络错误、认证错误、限流等）

### 5.2 Prompt 构建器 (`core/prompt_builder.py`)

构建发送给 LLM 的 System Prompt：

```
你是一个 SQL 生成助手。根据用户提供的数据库 DDL 和自然语言问题，
生成对应的 SQL 查询语句。

目标数据库方言：{target_db}

DDL 定义：
{ddl_content}

要求：
1. 只输出可执行的 SQL 语句
2. 用自然语言简要解释 SQL 的逻辑
3. 如果问题有歧义，说明你的假设
4. SQL 必须与目标数据库方言兼容
```

多轮对话时，将历史消息加入 `messages` 数组。

### 5.3 SQL 解析器 (`core/sql_parser.py`)

- `extract_sql(text: str) -> str` — 从 LLM 回复中提取纯 SQL（去除 Markdown 标记和解释文字）
- `validate_sql_basic(sql: str, db_type: str) -> bool` — 基本语法校验

### 5.4 DDL 存储 (`storage/ddl_store.py`)

文件组织结构：
```
ddl/<project-name>/
├── schema.ddl      # DDL 内容
└── meta.json       # 元信息
```

`meta.json` 格式：
```json
{
  "name": "电商系统",
  "tags": ["生产"],
  "created_at": "2026-06-02T14:00:00",
  "table_count": 12
}
```

接口：
- `save(name, content, tags)` — 保存 DDL
- `list_all()` — 列出所有 DDL（返回元信息列表）
- `get(name)` — 获取 DDL 内容
- `delete(name)` — 删除 DDL
- `get_meta(name)` — 获取 DDL 元信息

### 5.5 对话历史存储 (`storage/conversation_store.py`)

文件格式（每个对话一个 JSON 文件）：
```json
{
  "id": "conv-20260602-电商系统-a1b2c3",
  "ddl_name": "电商系统",
  "target_db": "PostgreSQL",
  "created_at": "2026-06-02T14:00:00",
  "updated_at": "2026-06-02T14:30:00",
  "message_count": 8,
  "messages": [
    {"role": "system", "content": "..."},
    {"role": "user", "content": "查询最近7天下单最多的前10个商品"},
    {"role": "assistant", "content": "SELECT ...\n\n解释..."}
  ]
}
```

接口：
- `save(conversation)` — 保存/更新对话
- `list_all()` — 列出所有历史对话
- `get(conv_id)` — 获取指定对话
- `get_latest()` — 获取最近的对话（用于 `chat continue`）
- `delete(conv_id)` — 删除对话

---

## 6. 目标数据库支持

初始支持的数据库类型：

| 数据库 | 方言标识 |
|--------|---------|
| MySQL | `mysql` |
| PostgreSQL | `postgresql` |
| SQLite | `sqlite` |
| MaxCompute | `maxcompute` |

用户在 `chat start` 时从上述列表中选择目标数据库，Prompt 中注入对应的方言要求。

---

## 7. 错误处理

| 场景 | 处理方式 |
|------|---------|
| 配置未初始化 | 提示运行 `my-tool config init` |
| API Key 无效 / 网络错误 | 显示错误详情，引导检查配置 |
| Token 超限（DDL 过大） | 提示精简 DDL 或分段上传 |
| LLM 回复无有效 SQL | 重试提示或建议换种问法 |
| 上传同名 DDL | 提示已存在，询问是否覆盖 |
| 上传空文件 | 拒绝并提示 |
| DDL 内容非标准 SQL | 警告但不阻止 |
| 对话历史超长 | 自动截断早期消息，保留最近 N 轮 |
| 未选择 DDL 就提问 | 提示先运行 `chat start` |
| 删除有活跃对话的 DDL | 提示会影响进行中的对话 |

---

## 8. 后续扩展方向

1. **API 服务** — 新增 `api/` 层（FastAPI），复用 `service/` 层
2. **Web 前端** — 新增 `web/` 层，调用 API
3. **SQL 执行** — 可选功能：配置数据库连接信息，直接执行并返回结果
4. **多 LLM 供应商** — 扩展支持 Anthropic Claude 等非 OpenAI 兼容 API
5. **DDL 差异对比** — 对比不同版本的 DDL 变更

---

## 9. 非功能需求

- 所有敏感信息（API Key）存储在本地配置文件中，不发送到第三方
- DDL 和对话历史均存储在本地，不上传到任何外部服务
- LLM 调用通过用户配置的 API 直连，不经过中间代理
