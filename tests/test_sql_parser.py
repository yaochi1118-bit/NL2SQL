from my_tool.core.sql_parser import SQLParser


class TestSQLParser:
    def test_extract_sql_from_code_block(self):
        text = "```sql\nSELECT * FROM users;\n```"
        assert SQLParser.extract_sql(text) == "SELECT * FROM users;"

    def test_extract_sql_with_explanation(self):
        text = """Here's the query you need:
```sql
SELECT u.name, COUNT(o.id) as order_count
FROM users u
JOIN orders o ON u.id = o.user_id
GROUP BY u.name
ORDER BY order_count DESC
LIMIT 10;
```
This will show the top 10 users by order count."""
        result = SQLParser.extract_sql(text)
        assert "SELECT u.name" in result
        assert "LIMIT 10" in result
        assert "Here's the query" not in result

    def test_extract_sql_plain_text(self):
        text = "SELECT * FROM users;"
        assert SQLParser.extract_sql(text) == "SELECT * FROM users;"

    def test_extract_sql_multiple_code_blocks(self):
        text = "First:\n```sql\nSELECT 1;\n```\nSecond:\n```sql\nSELECT 2;\n```"
        # Should return the first block
        assert SQLParser.extract_sql(text) == "SELECT 1;"

    def test_extract_sql_no_sql_found(self):
        text = "I don't know how to answer that question."
        assert SQLParser.extract_sql(text) == ""

    def test_validate_basic_valid_select(self):
        assert SQLParser.validate_sql_basic("SELECT * FROM users WHERE id = 1;", "MySQL") is True

    def test_validate_basic_valid_with_cte(self):
        assert SQLParser.validate_sql_basic(
            "WITH cte AS (SELECT * FROM users) SELECT * FROM cte;", "PostgreSQL"
        ) is True

    def test_extract_sql_none_input(self):
        assert SQLParser.extract_sql(None) == ""

    def test_extract_sql_from_generic_code_block(self):
        text = "```\nSELECT * FROM users;\n```"
        assert SQLParser.extract_sql(text) == "SELECT * FROM users;"

    def test_extract_sql_code_block_no_trailing_newline(self):
        text = "```sql\nSELECT 1;```"
        assert SQLParser.extract_sql(text) == "SELECT 1;"

    def test_validate_basic_empty(self):
        assert SQLParser.validate_sql_basic("", "MySQL") is False
        assert SQLParser.validate_sql_basic("   ", "SQLite") is False
        assert SQLParser.validate_sql_basic(None, "PG") is False

    def test_validate_basic_drop_and_alter(self):
        assert SQLParser.validate_sql_basic("DROP TABLE users;", "MySQL") is True
        assert SQLParser.validate_sql_basic("ALTER TABLE users ADD COLUMN age INT;", "PG") is True

    def test_validate_basic_non_sql(self):
        assert SQLParser.validate_sql_basic("Hello world", "MySQL") is False
        assert SQLParser.validate_sql_basic("What is the capital of France?", "PG") is False
