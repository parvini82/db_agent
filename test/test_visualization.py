import matplotlib.pyplot as plt
from core.agent import run_agent

schema = """
Tables:
products(id, name, category, description)
suppliers(id, name, city, address)
purchases(id, product_id, supplier_id, purchase_date, quantity, unit_cost)
sales(id, product_id, sale_date, quantity, unit_price)
Relations:
- purchases.product_id → products.id
- purchases.supplier_id → suppliers.id
- sales.product_id → products.id
"""

def test_visualize_category_distribution():
    df = run_agent("Show the number of products per category.", schema)
    if not df.empty:
        plt.bar(df["category"], df["product_count"])
        plt.title("Products per Category (Test)")
        plt.xlabel("Category")
        plt.ylabel("Count")
        plt.tight_layout()
        plt.show()

def test_visualize_monthly_sales():
    df = run_agent("Show total sales revenue per month in the last 6 months.", schema)
    if not df.empty:
        plt.plot(df["month"], df["total_sales"], marker="o")
        plt.title("Monthly Sales Revenue (Test)")
        plt.xlabel("Month")
        plt.ylabel("Total Sales ($)")
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.show()
