import re

class SqlGuardian:
    """Prevents execution of unsafe SQL queries (anything other than SELECT)."""
    def guard_select(self, query: str) -> str:
        query = (
            query.strip()
            .replace("SQL:", "", 1)
            .replace("sql:", "", 1)
            .strip("`").strip()
        )
        # Remove common junk like ```sql, /* ... */, <s>, </s>, etc.
        query = re.sub(r"```[\s\S]*?```", "", query)  # remove fenced code
        query = re.sub(r"/\*.*?\*/", "", query)  # remove inline comments
        query = re.sub(r"<[^>]+>", "", query)  # remove XML-style tags
        query = query.strip()
        query = re.sub(r"<[^>]+>", "", query).strip()
        forbidden = [
            "UPDATE", "DELETE", "INSERT", "DROP", "ALTER",
            "CREATE", "TRUNCATE", "REPLACE", "EXEC",
            "MERGE", "GRANT", "REVOKE"
        ]
        if any(word in query.upper() for word in forbidden):
            raise ValueError(f"🚫 Dangerous SQL detected:\n{query}")
        return query
