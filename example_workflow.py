"""
Simple example demonstrating the LangGraph workflow functionality
"""

from core.agent import run_agent_with_workflow, run_agent_simple
from core.workflow import ConversationTurn


def simple_workflow_example():
    """Demonstrate basic workflow usage"""
    print("🚀 LangGraph Workflow Example")
    print("=" * 40)
    
    # Simple query
    question = "How many users do we have?"
    print(f"Question: {question}")
    
    result = run_agent_with_workflow(question)
    
    print(f"Response: {result['response']}")
    print(f"SQL: {result['sql_query']}")
    print()


def multi_turn_conversation_example():
    """Demonstrate multi-turn conversation with memory"""
    print("💬 Multi-turn Conversation Example")
    print("=" * 40)
    
    conversation_history = []
    
    # First question
    q1 = "What tables do we have in the database?"
    print(f"Q1: {q1}")
    
    result1 = run_agent_with_workflow(q1, conversation_history)
    conversation_history = result1['conversation_history']
    
    print(f"A1: {result1['response'][:100]}...")
    print()
    
    # Follow-up question (uses memory)
    q2 = "How many records are in the users table?"
    print(f"Q2: {q2}")
    
    result2 = run_agent_with_workflow(q2, conversation_history)
    conversation_history = result2['conversation_history']
    
    print(f"A2: {result2['response'][:100]}...")
    print()


if __name__ == "__main__":
    try:
        simple_workflow_example()
        multi_turn_conversation_example()
        print("✅ Examples completed successfully!")
    except Exception as e:
        print(f"❌ Example failed: {e}")
        import traceback
        traceback.print_exc()
