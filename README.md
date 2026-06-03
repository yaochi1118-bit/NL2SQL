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
