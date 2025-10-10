from langchain_ollama import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from sqlalchemy import create_engine, text
import pandas as pd
import re
from matplotlib import pyplot as plt


# ---------- 1️⃣ Guardian Class ----------
class SqlGuardian:
    """Prevents execution of unsafe SQL queries (anything other than SELECT)."""
    def guard_select(self, query: str) -> str:
        # 🔹 پاک‌سازی تگ‌ها، SQL:، backtick و فاصله‌ها
        query = (
            query.strip()
            .replace("SQL:", "", 1)
            .replace("sql:", "", 1)
            .strip("`").strip()
        )
        # حذف تگ‌های شبیه <s>, </s>, <think> و غیره
        query = re.sub(r"<[^>]+>", "", query).strip()

        # 🔹 دستورهای خطرناک (case-insensitive)
        forbidden = [
            "UPDATE", "DELETE", "INSERT", "DROP", "ALTER",
            "CREATE", "TRUNCATE", "REPLACE", "EXEC",
            "MERGE", "GRANT", "REVOKE"
        ]

        q_upper = query.upper()

        if any(word in q_upper for word in forbidden):
            raise ValueError(f"🚫 Dangerous SQL detected — forbidden keyword in query.\n\n{query}")


        return query


# ---------- 2️⃣ LLM Config ----------
llm = OllamaLLM(
    model="sqlcoder:latest",
    base_url="http://localhost:11434"
)

template = """
You are an AI assistant specialized in generating SQL queries.

Database schema:
{schema}

Generate a correct, optimized SQL query for the following user request.
Return ONLY the SQL query.

User request:
{question}
"""

prompt = PromptTemplate(input_variables=["schema", "question"], template=template)
chain = LLMChain(llm=llm, prompt=prompt)
guardian = SqlGuardian()


# ---------- 3️⃣ DB Connection ----------
engine = create_engine(
    "postgresql+psycopg2://postgres:postgres123@localhost:5433/db_agent",
    echo=False  # True برای دیباگ
)


# ---------- 4️⃣ Agent Function ----------
def run_agent(user_question: str, db_schema: str):
    """Generate, validate, and execute SQL query safely."""
    response = chain.run({"schema": db_schema, "question": user_question})

    # 🧱 Guardian check
    safe_query = guardian.guard_select(response)

    # 🧩 اجرای کوئری با SQLAlchemy
    with engine.connect() as conn:
        result = conn.execute(text(safe_query))
        rows = result.fetchall()
        cols = result.keys()
        df = pd.DataFrame(rows, columns=cols)

    print("\n✅ Generated & Executed Query:\n", safe_query)
    print("\n📊 Result (top 10 rows):")
    print(df.head(10).to_string(index=False))


    return df
if __name__ == "__main__":
    database_schema = """
    Tables:
    products(id, name, category, description)
    suppliers(id, name, city, address)
    purchases(id, product_id, supplier_id, purchase_date, quantity, unit_cost)
    sales(id, product_id, sale_date, quantity, unit_price)

    Relations:
    - purchases.product_id is related to products.id
    - purchases.supplier_id is related to suppliers.id
    - sales.product_id is related to products.id
    """

    question = """
        Show the number of products per category.
    """
    question2 = """
        Show total sales revenue per month in the last 6 months.
    """

    df=run_agent(question, database_schema)

    if not df.empty:
        plt.figure()
        plt.bar(df['category'].astype(str), df['product_count'])
        plt.xlabel('category')
        plt.ylabel('count')
        plt.title('Products per category')
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()
        plt.show()

    # df=run_agent(question2, database_schema)
    # df = df.sort_values('month')  # مرتب‌سازی بر اساس تاریخ
    #
    # plt.figure(figsize=(8, 4))
    # plt.plot(df['month'], df['total_sales'], marker='o', color='royalblue', linewidth=2)
    #
    # plt.title('Total Sales by Month (Last 6 Months)')
    # plt.xlabel('Month')
    # plt.ylabel('Total Sales ($)')
    # plt.grid(True, linestyle='--', alpha=0.5)
    # plt.xticks(rotation=45, ha='right')
    #
    # # اضافه کردن مقدار عددی روی هر نقطه
    # for i, val in enumerate(df['total_sales']):
    #     plt.text(df['month'].iloc[i], val, f'{val:,.0f}', ha='center', va='bottom', fontsize=8)
    #
    # plt.tight_layout()
    # plt.show()
