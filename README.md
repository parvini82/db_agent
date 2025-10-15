# 🧠 Database Agent (LLM-Powered BI Assistant)

An intelligent database agent that automatically generates and executes **safe SQL queries** using **LangChain + Ollama (sqlcoder model)**. Now featuring **LangGraph workflow** for advanced conversation memory and multi-turn interactions.

## 🚀 Key Features

### Core Capabilities
- **LLM-based SQL generation** via Ollama (`sqlcoder`)
- **SQL Guardian** blocks unsafe operations (`UPDATE`, `DELETE`, etc.)
- **PostgreSQL integration** via SQLAlchemy
- **RAG-powered context retrieval** for relevant schema information
- **Modular and testable architecture**

### Advanced Features (LangGraph Workflow)
- **Conversation memory** for multi-turn interactions
- **Workflow-based processing** with structured nodes
- **Context-aware SQL generation** using previous conversations
- **Comprehensive error handling** with graceful degradation
- **Session management** with conversation history
- **RESTful API** with multiple endpoints

---

## 🏗️ Architecture

### Simple Agent (Original)
```
User Query → RAG Context → LLM → SQL Guardian → Database → Response
```

### LangGraph Workflow (Advanced)
```
User Query → retrieve_context → generate_sql → execute_query → respond
                ↓                    ↓              ↓           ↓
            RAG Context        LLM + Memory    Guardian    Natural Response
```

**Workflow Nodes:**
1. **`retrieve_context`**: Retrieves relevant table descriptions using RAG
2. **`generate_sql`**: Generates SQL queries with conversation context
3. **`execute_query`**: Executes and validates SQL queries with guardian
4. **`respond`**: Formats human-readable responses

---

## 📁 Project Structure

```
db_agent/
│
├── 📄 README.md                    # This file
├── 📄 requirments.txt              # Dependencies
├── 🐳 Dockerfile                   # Container setup
├── 🐳 docker-compose.yml           # Multi-service setup
│
├── 🔧 config/
│   └── settings.py                 # Model + DB configurations
│
├── 🧠 core/
│   ├── agent.py                    # Simple agent + LangGraph integration
│   ├── workflow.py                 # LangGraph workflow implementation
│   ├── db.py                       # SQLAlchemy database operations
│   ├── guardian.py                 # SQL security validator
│   └── llm.py                      # Ollama + LangChain setup
│
├── 🗄️ database/
│   ├── connection.py               # Database connection setup
│   ├── models.py                   # SQLAlchemy models
│   ├── init_db.py                  # Database initialization
│   └── seed_data.py                # Sample data generation
│
├── 🔍 rag/
│   ├── metadata_preparer.py        # Schema metadata preparation
│   └── retriever.py                # Context retrieval engine
│
├── 🌐 api/
│   └── main.py                     # FastAPI REST endpoints
│
├── 🧪 test/
│   └── test_visualization.py       # Visualization tests
│
├── 📝 test_workflow.py             # LangGraph workflow tests
├── 📝 example_workflow.py          # Usage examples
│
└── 🤖 model/
    ├── Modelfile                   # Ollama model configuration
    └── sqlcoder-7b-2.Q4_K_M.gguf  # SQLCoder model file
```

---

## ⚙️ Setup

### 1. Clone and Install
```bash
git clone <repo-url>
cd db_agent
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirments.txt
```

### 2. Environment Configuration
Create `.env` file:
```bash
# Ollama Configuration
OLLAMA_MODEL=sqlcoder
OLLAMA_BASE_URL=http://localhost:11434

# Database Configuration
DB_URL=postgresql+psycopg2://postgres:postgres123@localhost:5432/db_agent

# Qdrant Configuration (for RAG)
QDRANT_URL=http://localhost:6333
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

### 3. Start Required Services

#### Start Ollama with SQLCoder
```bash
# Pull the SQLCoder model
ollama pull sqlcoder

# Start Ollama server
ollama serve
```

#### Start PostgreSQL Database
```bash
# Using Docker Compose
docker-compose up -d postgres

# Or start your local PostgreSQL instance
```

#### Start Qdrant (for RAG)
```bash
# Using Docker
docker run -p 6333:6333 qdrant/qdrant

# Or use the provided docker-compose
docker-compose up -d qdrant
```

### 4. Initialize Database
```bash
# Initialize database schema
python -m database.init_db

# Seed with sample data
python -m database.seed_data
```

### 5. Prepare RAG Metadata
```bash
# Generate and index database metadata for RAG
python -m rag.metadata_preparer
```

---

## 🚀 Usage

### Simple Agent (Basic)
```python
from core.agent import run_agent

# Single query
result = run_agent("How many users do we have?")
print(result)
```

### LangGraph Workflow (Advanced)
```python
from core.agent import run_agent_with_workflow

# Single query with advanced features
result = run_agent_with_workflow("How many users do we have?")
print(result['response'])  # Natural language response
print(result['sql_query'])  # Generated SQL
print(result['query_result'])  # DataFrame results

# Multi-turn conversation
conversation_history = []
result1 = run_agent_with_workflow("What user roles exist?", conversation_history)
conversation_history = result1['conversation_history']

result2 = run_agent_with_workflow("How many users have each role?", conversation_history)
```

### API Usage

#### Start the API Server
```bash
uvicorn api.main:app --reload
```

#### Standard Chat Endpoint
```bash
curl -X POST "http://localhost:8000/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "Show me the top 5 most active users",
    "use_workflow": true
  }'
```

#### Workflow-specific Endpoint
```bash
curl -X POST "http://localhost:8000/chat/workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "user123",
    "message": "How many active users do we have?"
  }'
```

#### Get Conversation History
```bash
curl "http://localhost:8000/chat/history/user123"
```

#### Clear Conversation History
```bash
curl -X DELETE "http://localhost:8000/chat/history/user123"
```

---

## 🧪 Testing

### Run Workflow Tests
```bash
# Comprehensive workflow tests
python test_workflow.py

# Simple usage examples
python example_workflow.py
```

### Run Visualization Tests
```bash
# BI visualization tests
python -m pytest test/test_visualization.py -s
```

### Run API Tests
```bash
# Start API server
uvicorn api.main:app --reload

# Test endpoints
curl http://localhost:8000/
```

---

## 🔧 Configuration Options

### Model Configuration
```python
# config/settings.py
OLLAMA_MODEL = "sqlcoder"  # or "sqlcoder:latest"
OLLAMA_BASE_URL = "http://localhost:11434"
```

### Database Configuration
```python
DB_URL = "postgresql+psycopg2://user:password@host:port/database"
```

### RAG Configuration
```python
QDRANT_URL = "http://localhost:6333"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
```

---

## 🛡️ Security Features

### SQL Guardian
- **Blocks dangerous operations**: `UPDATE`, `DELETE`, `DROP`, etc.
- **Allows only SELECT queries**: Read-only operations
- **Query validation**: Syntax and security checks
- **Error handling**: Graceful failure on invalid queries

### Input Validation
- **Parameterized queries**: Prevents SQL injection
- **Query sanitization**: Removes potentially dangerous content
- **Context validation**: Ensures relevant schema usage

---

## 📊 Example Queries

### Simple Queries
```python
# Count records
"How many products are in each category?"

# Aggregations
"What's the average price of electronics?"

# Filtering
"Show me users created in the last month"
```

### Complex Multi-turn Conversations
```python
# First question
"What are the different product categories?"

# Follow-up (uses previous context)
"How many products are in each category?"

# Further analysis
"Which category has the highest average price?"
```

### Workflow Benefits
- **Context Awareness**: Follow-up questions understand previous context
- **Memory Management**: Automatically maintains conversation history
- **Error Recovery**: Graceful handling of invalid queries
- **Session Management**: Persistent conversation state across API calls

---

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individual container
docker build -t db-agent .
docker run -p 8000:8000 db-agent
```

### Production Considerations
- **Environment variables**: Secure configuration management
- **Database connection pooling**: Optimize database connections
- **Model caching**: Cache LLM responses for better performance
- **Rate limiting**: Implement API rate limiting
- **Monitoring**: Add logging and monitoring

---

## 🔄 Migration Guide

### From Simple Agent to Workflow

**Before (Simple Agent):**
```python
from core.agent import run_agent
df = run_agent("How many users?")
```

**After (Workflow Agent):**
```python
from core.agent import run_agent_with_workflow
result = run_agent_with_workflow("How many users?")
print(result['response'])
```

### API Migration

**Before:**
```bash
curl -X POST "http://localhost:8000/chat" \
  -d '{"session_id": "user123", "message": "query"}'
```

**After (with workflow):**
```bash
curl -X POST "http://localhost:8000/chat/workflow" \
  -d '{"session_id": "user123", "message": "query"}'
```

---

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit changes**: `git commit -m 'Add amazing feature'`
4. **Push to branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

---

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 🙏 Acknowledgments

- **LangChain**: For the LLM framework
- **Ollama**: For local LLM deployment
- **SQLCoder**: For specialized SQL generation
- **LangGraph**: For advanced workflow management
- **Qdrant**: For vector similarity search
- **FastAPI**: For the REST API framework

---

## 📞 Support

For questions, issues, or contributions:
- **Issues**: Create a GitHub issue
- **Discussions**: Use GitHub Discussions
- **Documentation**: Check the workflow implementation in `core/workflow.py`

---

## 🔮 Future Enhancements

- **Custom Node Types**: Add specialized nodes for different query types
- **Dynamic Routing**: Implement conditional routing based on query complexity
- **Caching**: Add result caching for frequently asked questions
- **Analytics**: Track query performance and user patterns
- **Multi-database Support**: Extend to support multiple database connections

---

*Built with ❤️ for intelligent database interactions*