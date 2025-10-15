"""
Test script for the LangGraph Database Workflow

This script demonstrates the workflow functionality with multi-turn conversations
and memory management.
"""

from core.agent import run_agent_with_workflow, run_agent_simple
from core.workflow import ConversationTurn
import json


def test_workflow_single_query():
    """Test the workflow with a single query"""
    print("🔍 Testing Single Query Workflow")
    print("=" * 50)
    
    question = "How many users do we have in total?"
    print(f"Question: {question}")
    
    result = run_agent_with_workflow(question)
    
    print(f"Response: {result['response']}")
    print(f"SQL Query: {result['sql_query']}")
    print(f"Records Found: {len(result['query_result']) if result['query_result'] is not None else 0}")
    
    if result['error']:
        print(f"Error: {result['error']}")
    
    print()


def test_workflow_multi_turn_conversation():
    """Test multi-turn conversation with memory"""
    print("💬 Testing Multi-turn Conversation")
    print("=" * 50)
    
    conversation_history = []
    
    # First question
    question1 = "What are the different product categories in our database?"
    print(f"Q1: {question1}")
    
    result1 = run_agent_with_workflow(question1, conversation_history)
    conversation_history = result1['conversation_history']
    
    print(f"A1: {result1['response']}")
    print(f"SQL1: {result1['sql_query']}")
    print()
    
    # Follow-up question that references previous context
    question2 = "How many products are in each category?"
    print(f"Q2: {question2}")
    
    result2 = run_agent_with_workflow(question2, conversation_history)
    conversation_history = result2['conversation_history']
    
    print(f"A2: {result2['response']}")
    print(f"SQL2: {result2['sql_query']}")
    print()
    
    # Another follow-up
    question3 = "Which category has the most products?"
    print(f"Q3: {question3}")
    
    result3 = run_agent_with_workflow(question3, conversation_history)
    
    print(f"A3: {result3['response']}")
    print(f"SQL3: {result3['sql_query']}")
    print()


def test_workflow_error_handling():
    """Test error handling in the workflow"""
    print("🛡️ Testing Error Handling")
    print("=" * 50)
    
    # Test with invalid query
    invalid_question = "SELECT * FROM non_existent_table"
    print(f"Invalid Question: {invalid_question}")
    
    result = run_agent_with_workflow(invalid_question)
    
    print(f"Response: {result['response']}")
    if result['error']:
        print(f"Error: {result['error']}")
    print()


def test_workflow_vs_simple_agent():
    """Compare workflow vs simple agent"""
    print("🔄 Comparing Workflow vs Simple Agent")
    print("=" * 50)
    
    question = "Show me the top 5 most active users"
    print(f"Question: {question}")
    
    # Test simple agent
    print("\n1️⃣ Simple Agent:")
    try:
        df_simple = run_agent_simple(question)
        print("✅ Simple agent completed successfully")
        print(f"Records: {len(df_simple)}")
    except Exception as e:
        print(f"❌ Simple agent error: {e}")
    
    # Test workflow agent
    print("\n2️⃣ Workflow Agent:")
    try:
        result_workflow = run_agent_with_workflow(question)
        print("✅ Workflow agent completed successfully")
        print(f"Response: {result_workflow['response'][:100]}...")
        print(f"Records: {len(result_workflow['query_result']) if result_workflow['query_result'] is not None else 0}")
    except Exception as e:
        print(f"❌ Workflow agent error: {e}")
    
    print()


def test_conversation_memory():
    """Test conversation memory functionality"""
    print("🧠 Testing Conversation Memory")
    print("=" * 50)
    
    conversation_history = []
    
    # Build up conversation
    questions = [
        "What tables do we have in the database?",
        "How many records are in the users table?",
        "What's the average age of users?",
        "Show me users older than the average age"
    ]
    
    for i, question in enumerate(questions, 1):
        print(f"Q{i}: {question}")
        
        result = run_agent_with_workflow(question, conversation_history)
        conversation_history = result['conversation_history']
        
        print(f"A{i}: {result['response'][:150]}...")
        print(f"SQL{i}: {result['sql_query']}")
        print()


def test_workflow_state_management():
    """Test workflow state management"""
    print("📊 Testing Workflow State Management")
    print("=" * 50)
    
    question = "What's the total revenue from sales?"
    print(f"Question: {question}")
    
    result = run_agent_with_workflow(question)
    
    # Show state information
    print("Workflow State Information:")
    print(f"- User Query: {question}")
    print(f"- Context Used: {len(result['context_used'])} characters")
    print(f"- SQL Generated: {result['sql_query']}")
    print(f"- Execution Success: {result['error'] is None}")
    print(f"- Conversation Turns: {len(result['conversation_history'])}")
    
    if result['current_turn']:
        turn = result['current_turn']
        print(f"- Current Turn Timestamp: {turn.timestamp}")
        print(f"- Result Summary: {turn.result_summary[:100]}...")
    
    print()


def main():
    """Run all workflow tests"""
    print("🚀 LangGraph Database Workflow Tests")
    print("=" * 60)
    
    try:
        # Run all tests
        test_workflow_single_query()
        test_workflow_multi_turn_conversation()
        test_workflow_error_handling()
        test_workflow_vs_simple_agent()
        test_conversation_memory()
        test_workflow_state_management()
        
        print("✅ All workflow tests completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
