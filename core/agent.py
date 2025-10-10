from core.llm import chain
from core.db import execute_query
from core.guardian import SqlGuardian
import pandas as pd

guardian = SqlGuardian()

def run_agent(user_question: str, db_schema: str) -> pd.DataFrame:
    response = chain.run({"schema": db_schema, "question": user_question})
    safe_query = guardian.guard_select(response)
    df = execute_query(safe_query)
    print("\n✅ Generated & Executed Query:\n", safe_query)
    print("\n📊 Result (top 10 rows):")
    print(df.head(10).to_string(index=False))
    return df
