from __future__ import annotations


class PromptBuilder:
    """Build prompts for LLM SQL generation."""

    SYSTEM_PROMPT_TEMPLATE = """你是一个 SQL 生成助手。根据用户提供的数据库 DDL 和自然语言问题，生成对应的 SQL 查询语句。

目标数据库方言：{target_db}

以下是 DDL 定义：
{ddl_content}

要求：
1. 只输出可执行的 SQL 语句
2. 用自然语言简要解释 SQL 的逻辑
3. 如果问题有歧义，说明你的假设
4. SQL 必须与目标数据库方言兼容"""

    @classmethod
    def build_system_prompt(cls, ddl_content: str, target_db: str) -> str:
        """Build the system prompt with DDL context."""
        return cls.SYSTEM_PROMPT_TEMPLATE.format(
            target_db=target_db,
            ddl_content=ddl_content,
        )

    SYSTEM_PROMPT_MULTI_DDL_TEMPLATE = """你是一个 SQL 生成助手。根据用户提供的数据库 DDL 和自然语言问题，生成对应的 SQL 查询语句。

目标数据库方言：{target_db}

以下是所有可用的 DDL 定义，请根据问题自动选择最相关的 DDL 作为依据：
{ddl_index}

要求：
1. 只输出可执行的 SQL 语句
2. 用自然语言简要解释 SQL 的逻辑
3. 如果问题有歧义，说明你的假设
4. SQL 必须与目标数据库方言兼容"""

    @classmethod
    def build_multi_ddl_prompt(cls, ddl_list: list[tuple[str, str, list[str]]], target_db: str) -> str:
        """Build a system prompt with multiple DDLs for auto-detection.

        Args:
            ddl_list: List of (ddl_name, ddl_content, tags) tuples.
            target_db: Target database dialect.
        """
        index_parts = []
        for i, (name, content, tags) in enumerate(ddl_list, 1):
            tag_str = ", ".join(tags) if tags else "无标签"
            index_parts.append(f"--- DDL {i}: {name} (标签: {tag_str}) ---\n{content}")
        ddl_index = "\n\n".join(index_parts)
        return cls.SYSTEM_PROMPT_MULTI_DDL_TEMPLATE.format(
            target_db=target_db,
            ddl_index=ddl_index,
        )

    @classmethod
    def build_messages(
        cls,
        system_prompt: str,
        history: list[dict],
        new_question: str,
    ) -> list[dict]:
        """Build the full messages array for the LLM API call.

        Args:
            system_prompt: The system prompt with DDL context.
            history: Previous conversation messages (without system prompt).
            new_question: The user's new question.
        """
        messages: list[dict] = [{"role": "system", "content": system_prompt}]
        messages.extend(history)
        messages.append({"role": "user", "content": new_question})
        return messages
