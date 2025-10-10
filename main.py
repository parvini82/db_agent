from core.agent import run_agent

if __name__ == "__main__":
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

    question = "Show the number of products per category."

    df = run_agent(question, schema)

    if not df.empty:
        print("\n✅ Query executed successfully.")
        print(df)
