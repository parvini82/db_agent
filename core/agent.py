from core.llm import chain
from core.db import execute_query
from core.guardian import SqlGuardian
import pandas as pd

from rag.retriever import retrieve_context

guardian = SqlGuardian()

def run_agent(user_question: str) -> pd.DataFrame:
    context = retrieve_context(user_question)
    response = chain.invoke({"schema": context, "question": user_question})

    print("📚 Selected metadata from RAG:\n", context)

    if isinstance(response, dict):
        if "text" in response:
            response = response["text"]
        elif "output_text" in response:
            response = response["output_text"]
        else:
            response = str(response)
    elif not isinstance(response, str):
        response = str(response)

    print("🧠 Raw LLM response:", response)  # Debug print

    safe_query = guardian.guard_select(response)
    df = execute_query(safe_query)
    print("\n✅ Generated & Executed Query:\n", safe_query)
    print("\n📊 Result (top 10 rows):")
    print(df.head(10).to_string(index=False))
    return df
