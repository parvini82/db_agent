"""
Database Agent with LangGraph Workflow Integration

This module provides both the original simple agent and the new LangGraph workflow-based agent.
"""

from core.llm import chain
from core.db import execute_query
from core.guardian import SqlGuardian
from core.workflow import run_workflow, ConversationTurn
import pandas as pd
from typing import Dict, Any, List, Optional

from rag.retriever import retrieve_context

guardian = SqlGuardian()


def run_agent(user_question: str) -> pd.DataFrame:
    """
    Original simple agent implementation (for backward compatibility)
    
    Args:
        user_question: The user's question
        
    Returns:
        DataFrame with query results
    """
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


def run_agent_with_workflow(user_question: str, conversation_history: List[ConversationTurn] = None) -> Dict[str, Any]:
    """
    Run the LangGraph workflow-based agent with conversation memory
    
    Args:
        user_question: The user's question
        conversation_history: Previous conversation turns for context
        
    Returns:
        Dictionary containing response, SQL query, results, and metadata
    """
    return run_workflow(user_question, conversation_history)


def run_agent_simple(user_question: str) -> pd.DataFrame:
    """
    Alias for the original run_agent function
    """
    return run_agent(user_question)
