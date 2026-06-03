from __future__ import annotations

import re


class SQLParser:
    """Extract and validate SQL from LLM responses."""

    SQL_KEYWORDS = {
        "SELECT", "INSERT", "UPDATE", "DELETE", "CREATE", "DROP", "ALTER", "WITH", "EXPLAIN",
    }

    @classmethod
    def extract_sql(cls, text: str | None) -> str:
        """Extract SQL from LLM response, stripping Markdown and explanation text.

        Priority:
        1. First ```sql ... ``` code block
        2. First ``` ... ``` code block
        3. Plain text starting with an SQL keyword
        4. Empty string
        """
        if not text:
            return ""

        # Try ```sql ... ``` block first
        match = re.search(r"```sql\s*\n(.*?)(?:\n|)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Try ``` ... ``` block
        match = re.search(r"```\s*\n(.*?)(?:\n|)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()

        # Check if the text itself is SQL-like
        stripped = text.strip()
        if stripped and cls._looks_like_sql(stripped):
            return stripped

        return ""

    @classmethod
    def _looks_like_sql(cls, text: str) -> bool:
        """Check if text starts with a known SQL keyword."""
        first_word = text.split()[0].upper() if text.split() else ""
        return first_word in cls.SQL_KEYWORDS

    @classmethod
    def validate_sql_basic(cls, sql: str | None, db_type: str) -> bool:
        """Basic SQL validation — checks if it's non-empty and starts with a known keyword.

        Args:
            sql: The SQL string to validate.
            db_type: Target database dialect (currently unused — reserved for future
                     syntax-level validation against specific dialects).
        """
        if not sql:
            return False
        stripped = sql.strip()
        if not stripped:
            return False
        return cls._looks_like_sql(stripped)
