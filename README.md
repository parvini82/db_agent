# 🧠 SQL Agent (LLM-Powered BI Assistant)

An intelligent agent that automatically generates and executes **safe SQL queries** using **LangChain + Ollama (sqlcoder model)**.  
Connects to PostgreSQL, validates SQL via a security guardian, executes safely via SQLAlchemy, and supports visualization in tests.

---

## 🚀 Features
- LLM-based SQL generation via Ollama (`sqlcoder`)
- SQL Guardian blocks unsafe operations (`UPDATE`, `DELETE`, etc.)
- PostgreSQL integration via SQLAlchemy
- Modular and testable architecture
- Seed data for reproducible tests
- Optional visualization for debugging and BI reports

---

## 🧱 Project Structure

sql_agent/
│
├── main.py                     # Entry point
│
├── config/
│   └── settings.py             # Model + DB configs
│
├── core/
│   ├── agent.py                # LLM + Guardian + DB logic
│   ├── db.py                   # SQLAlchemy setup
│   ├── guardian.py             # Safe SQL validator
│   └── llm.py                  # Ollama + LangChain setup
│
├── data/
│   └── seed_data.py            # Populate fake test data
│
└── tests/
    ├── test_agent.py           # Logical tests (no plots)
    └── test_visualization.py   # Visual tests (Matplotlib)

---

## ⚙️ Setup

git clone <repo-url>
cd sql_agent
python -m venv .venv
source .venv/bin/activate   # (on Windows: .venv\Scripts\activate)
pip install -r requirements.txt

Edit your config:

config/settings.py
OLLAMA_MODEL = "sqlcoder:latest"
OLLAMA_BASE_URL = "http://localhost:11434"
DB_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5433/db_agent"

Run Ollama locally:

ollama pull sqlcoder
ollama serve

---

## 🧩 Seed Database

python -m data.seed_data

Expected output:
✅ Seed data inserted successfully.

---

## 🧠 Run the Agent

python main.py

Example output:

✅ Generated & Executed Query:
SELECT category, COUNT(*) AS product_count FROM products GROUP BY category;

📊 Result:
 Electronics | 2
 Grocery     | 1
 Footwear    | 1

---

## 🧪 Testing

Type | Command | Description
------|----------|-------------
Logical tests | pytest -s tests/test_agent.py | Checks LLM & SQL correctness
Visualization tests | pytest -s tests/test_visualization.py | Shows charts for BI debugging

Optional helper:
./scripts/test.sh

---

