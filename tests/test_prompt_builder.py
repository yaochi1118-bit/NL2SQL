from my_tool.core.prompt_builder import PromptBuilder


class TestPromptBuilder:
    def test_build_system_prompt(self):
        ddl_content = "CREATE TABLE users (id INT);\nCREATE TABLE orders (id INT);"
        prompt = PromptBuilder.build_system_prompt(
            ddl_content=ddl_content,
            target_db="PostgreSQL",
        )
        assert "PostgreSQL" in prompt
        assert "CREATE TABLE users" in prompt
        assert "CREATE TABLE orders" in prompt
        assert "SQL 生成助手" in prompt

    def test_build_system_prompt_mysql(self):
        ddl_content = "CREATE TABLE products (id INT);"
        prompt = PromptBuilder.build_system_prompt(ddl_content, "MySQL")
        assert "MySQL" in prompt
        assert "products" in prompt

    def test_build_messages(self):
        ddl = "CREATE TABLE t (id INT);"
        system_prompt = PromptBuilder.build_system_prompt(ddl, "SQLite")
        messages = PromptBuilder.build_messages(
            system_prompt=system_prompt,
            history=[
                {"role": "user", "content": "第一个问题"},
                {"role": "assistant", "content": "第一个回答"},
            ],
            new_question="追问",
        )
        assert len(messages) == 4
        assert messages[0]["role"] == "system"
        assert messages[1] == {"role": "user", "content": "第一个问题"}
        assert messages[2] == {"role": "assistant", "content": "第一个回答"}
        assert messages[3]["role"] == "user"
        assert messages[3]["content"] == "追问"

    def test_build_messages_no_history(self):
        ddl = "CREATE TABLE t (id INT);"
        system_prompt = PromptBuilder.build_system_prompt(ddl, "MySQL")
        messages = PromptBuilder.build_messages(
            system_prompt=system_prompt,
            history=[],
            new_question="第一个问题",
        )
        assert len(messages) == 2
        assert messages[0]["role"] == "system"
        assert messages[1]["role"] == "user"
