"""
LangGraph Workflow Implementation for Database Agent

This module implements a structured workflow using LangGraph that coordinates
the agent's reasoning and actions through well-defined nodes and edges.
"""

from typing import TypedDict, List, Dict, Any, Optional, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import pandas as pd
import json
from dataclasses import dataclass

from rag.retriever import retrieve_context
from core.llm import llm
from core.db import execute_query
from core.guardian import SqlGuardian
from langchain.prompts import PromptTemplate


@dataclass
class ConversationTurn:
    """Represents a single conversation turn"""
    question: str
    sql_query: str
    result_summary: str
    answer: str
    timestamp: str


class WorkflowState(TypedDict):
    """State schema for the LangGraph workflow"""
    # Core workflow data
    user_query: str
    context: str
    generated_sql: str
    query_result: Optional[pd.DataFrame]
    final_response: str
    
    # Memory and conversation management
    conversation_history: List[ConversationTurn]
    current_turn: Optional[ConversationTurn]
    
    # Error handling
    error_message: Optional[str]
    execution_success: bool
    
    # LangChain messages for compatibility
    messages: Annotated[List[BaseMessage], add_messages]


class DatabaseWorkflow:
    """LangGraph-based workflow for database query processing"""
    
    def __init__(self):
        self.guardian = SqlGuardian()
        self.workflow = self._build_workflow()
        
        # Enhanced prompts for better context awareness
        self.sql_prompt = PromptTemplate(
            input_variables=["schema", "question", "conversation_context"],
            template="""
You are an expert SQL query generator for database analysis.

Database Schema Context:
{schema}

Previous Conversation Context:
{conversation_context}

Current User Question:
{question}

Instructions:
1. Generate a precise SQL query based on the user's question
2. Use the schema context to ensure table and column names are correct
3. Consider previous conversation context if relevant
4. Return ONLY the SQL query, no explanations or markdown formatting
5. Ensure the query is optimized and follows best practices

SQL Query:
"""
        )
        
        self.response_prompt = PromptTemplate(
            input_variables=["question", "sql_query", "result_summary", "error"],
            template="""
You are a helpful database assistant. Provide a clear, informative response.

User Question: {question}
Generated SQL: {sql_query}
Query Result: {result_summary}
Error (if any): {error}

Provide a natural language response that:
1. Directly answers the user's question
2. Explains the key findings from the data
3. If there was an error, explain what went wrong and suggest alternatives
4. Keep the response concise but informative

Response:
"""
        )
    
    def _build_workflow(self) -> StateGraph:
        """Build the LangGraph workflow with nodes and edges"""
        workflow = StateGraph(WorkflowState)
        
        # Add nodes
        workflow.add_node("retrieve_context", self._retrieve_context_node)
        workflow.add_node("generate_sql", self._generate_sql_node)
        workflow.add_node("execute_query", self._execute_query_node)
        workflow.add_node("respond", self._respond_node)
        workflow.add_node("handle_error", self._handle_error_node)
        
        # Define the workflow edges
        workflow.set_entry_point("retrieve_context")
        
        # Linear flow: retrieve_context → generate_sql → execute_query
        workflow.add_edge("retrieve_context", "generate_sql")
        workflow.add_edge("generate_sql", "execute_query")
        
        # Conditional routing after execution
        workflow.add_conditional_edges(
            "execute_query",
            self._route_after_execution,
            {
                "success": "respond",
                "error": "handle_error"
            }
        )
        
        # End points
        workflow.add_edge("respond", END)
        workflow.add_edge("handle_error", END)
        
        return workflow.compile()
    
    def _retrieve_context_node(self, state: WorkflowState) -> WorkflowState:
        """Node 1: Retrieve relevant database context using RAG"""
        try:
            print("🔍 Retrieving relevant database context...")
            
            # Retrieve context with increased top_k for better coverage
            context = retrieve_context(state["user_query"], top_k=5)
            state["context"] = context
            
            print(f"📚 Retrieved context ({len(context)} chars): {context[:100]}...")
            
        except Exception as e:
            error_msg = f"Failed to retrieve context: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_message"] = error_msg
            
        return state
    
    def _generate_sql_node(self, state: WorkflowState) -> WorkflowState:
        """Node 2: Generate SQL query based on context and conversation history"""
        try:
            print("🧠 Generating SQL query...")
            
            # Build conversation context from history
            conversation_context = self._build_conversation_context(state["conversation_history"])
            
            # Generate SQL using enhanced prompt
            sql_prompt = self.sql_prompt.format(
                schema=state["context"],
                question=state["user_query"],
                conversation_context=conversation_context
            )
            
            response = llm.invoke(sql_prompt)
            sql_query = response.strip()
            
            # Clean up the response
            sql_query = self._clean_sql_response(sql_query)
            state["generated_sql"] = sql_query
            
            print(f"🔧 Generated SQL: {sql_query}")
            
        except Exception as e:
            error_msg = f"Failed to generate SQL: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_message"] = error_msg
            
        return state
    
    def _execute_query_node(self, state: WorkflowState) -> WorkflowState:
        """Node 3: Execute and validate the SQL query"""
        try:
            print("⚡ Executing SQL query...")
            
            # Validate with guardian
            safe_query = self.guardian.guard_select(state["generated_sql"])
            state["generated_sql"] = safe_query  # Update with validated query
            
            # Execute the query
            result_df = execute_query(safe_query)
            state["query_result"] = result_df
            state["execution_success"] = True
            
            print(f"✅ Query executed successfully. Rows: {len(result_df)}")
            
        except Exception as e:
            error_msg = f"Query execution failed: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_message"] = error_msg
            state["execution_success"] = False
            
        return state
    
    def _respond_node(self, state: WorkflowState) -> WorkflowState:
        """Node 4: Generate final human-readable response"""
        try:
            print("💬 Generating response...")
            
            # Create result summary
            result_summary = self._create_result_summary(state["query_result"])
            
            # Generate response
            response_prompt = self.response_prompt.format(
                question=state["user_query"],
                sql_query=state["generated_sql"],
                result_summary=result_summary,
                error=""
            )
            
            final_response = llm.invoke(response_prompt)
            state["final_response"] = final_response
            
            # Create conversation turn
            from datetime import datetime
            turn = ConversationTurn(
                question=state["user_query"],
                sql_query=state["generated_sql"],
                result_summary=result_summary,
                answer=final_response,
                timestamp=datetime.now().isoformat()
            )
            
            state["current_turn"] = turn
            state["conversation_history"].append(turn)
            
            # Limit conversation history to prevent memory bloat
            if len(state["conversation_history"]) > 10:
                state["conversation_history"] = state["conversation_history"][-10:]
            
            print("✅ Response generated successfully")
            
        except Exception as e:
            error_msg = f"Failed to generate response: {str(e)}"
            print(f"❌ {error_msg}")
            state["error_message"] = error_msg
            
        return state
    
    def _handle_error_node(self, state: WorkflowState) -> WorkflowState:
        """Node: Handle errors and provide error response"""
        error_msg = state.get("error_message", "Unknown error occurred")
        
        # Generate error response
        error_response = f"""
I encountered an error while processing your request: {error_msg}

Please try rephrasing your question or check if the information you're looking for exists in the database.
"""
        
        state["final_response"] = error_response
        
        # Create error turn for history
        from datetime import datetime
        error_turn = ConversationTurn(
            question=state["user_query"],
            sql_query=state.get("generated_sql", ""),
            result_summary="Error occurred",
            answer=error_response,
            timestamp=datetime.now().isoformat()
        )
        
        state["current_turn"] = error_turn
        state["conversation_history"].append(error_turn)
        
        print(f"❌ Error handled: {error_msg}")
        return state
    
    def _route_after_execution(self, state: WorkflowState) -> str:
        """Determine routing after query execution"""
        if state.get("execution_success", False):
            return "success"
        return "error"
    
    def _build_conversation_context(self, history: List[ConversationTurn]) -> str:
        """Build context string from conversation history"""
        if not history:
            return "No previous conversation context."
        
        context_parts = []
        for turn in history[-3:]:  # Last 3 turns
            context_parts.append(f"Q: {turn.question}")
            context_parts.append(f"SQL: {turn.sql_query}")
            context_parts.append(f"A: {turn.answer[:100]}...")
        
        return "\n".join(context_parts)
    
    def _clean_sql_response(self, response: str) -> str:
        """Clean SQL response from LLM"""
        # Remove markdown formatting
        if response.startswith("```sql"):
            response = response.replace("```sql", "").replace("```", "").strip()
        elif response.startswith("```"):
            response = response.replace("```", "").strip()
        
        # Remove any extra text before/after SQL
        lines = response.split('\n')
        sql_lines = []
        in_sql = False
        
        for line in lines:
            line = line.strip()
            if line.upper().startswith(('SELECT', 'WITH', 'INSERT', 'UPDATE', 'DELETE')):
                in_sql = True
            if in_sql:
                sql_lines.append(line)
        
        return '\n'.join(sql_lines).strip()
    
    def _create_result_summary(self, result_df: Optional[pd.DataFrame]) -> str:
        """Create a summary of query results"""
        if result_df is None:
            return "No results returned."
        
        if len(result_df) == 0:
            return "Query returned no rows."
        
        if len(result_df) > 10:
            summary = f"Query returned {len(result_df)} rows. Sample data:\n"
            summary += result_df.head(5).to_string(index=False)
        else:
            summary = f"Query returned {len(result_df)} rows:\n"
            summary += result_df.to_string(index=False)
        
        return summary
    
    def run(self, user_query: str, conversation_history: List[ConversationTurn] = None) -> Dict[str, Any]:
        """
        Execute the workflow for a user query
        
        Args:
            user_query: The user's question
            conversation_history: Previous conversation turns
            
        Returns:
            Dictionary with workflow results
        """
        # Initialize state
        initial_state = {
            "user_query": user_query,
            "context": "",
            "generated_sql": "",
            "query_result": None,
            "final_response": "",
            "conversation_history": conversation_history or [],
            "current_turn": None,
            "error_message": None,
            "execution_success": False,
            "messages": [HumanMessage(content=user_query)]
        }
        
        print(f"🚀 Starting workflow for query: {user_query}")
        
        # Execute workflow
        final_state = self.workflow.invoke(initial_state)
        
        # Return structured results
        return {
            "response": final_state["final_response"],
            "sql_query": final_state["generated_sql"],
            "query_result": final_state["query_result"],
            "context_used": final_state["context"],
            "error": final_state.get("error_message"),
            "conversation_history": final_state["conversation_history"],
            "current_turn": final_state.get("current_turn")
        }


# Convenience function for easy integration
def run_workflow(user_query: str, conversation_history: List[ConversationTurn] = None) -> Dict[str, Any]:
    """
    Run the database workflow for a user query
    
    Args:
        user_query: The user's question
        conversation_history: Previous conversation turns
        
    Returns:
        Dictionary with workflow results
    """
    workflow = DatabaseWorkflow()
    return workflow.run(user_query, conversation_history)
