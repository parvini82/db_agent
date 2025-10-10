from sqlalchemy import text
from core.db import engine

def seed_data():
    with engine.begin() as conn:
        # 🧹 Clean existing tables
        conn.execute(text("TRUNCATE TABLE sales, purchases, products, suppliers RESTART IDENTITY CASCADE;"))

        # --- Seed products ---
        conn.execute(text("""
            INSERT INTO products (name, category, description) VALUES
            ('Laptop', 'Electronics', 'High-performance laptop'),
            ('Keyboard', 'Electronics', 'Mechanical keyboard'),
            ('Coffee', 'Grocery', 'Arabica beans'),
            ('Sneakers', 'Footwear', 'Running shoes');
        """))

        # --- Seed suppliers ---
        conn.execute(text("""
            INSERT INTO suppliers (name, city, address) VALUES
            ('TechZone', 'Paris', '123 Tech St'),
            ('FoodMart', 'Lyon', '77 Fresh Rd'),
            ('RunFast', 'Nice', '11 Sport Ave');
        """))

        # --- Seed purchases ---
        conn.execute(text("""
            INSERT INTO purchases (product_id, supplier_id, purchase_date, quantity, unit_cost) VALUES
            (1, 1, CURRENT_DATE - interval '90 days', 50, 600),
            (2, 1, CURRENT_DATE - interval '60 days', 100, 50),
            (3, 2, CURRENT_DATE - interval '30 days', 200, 8),
            (4, 3, CURRENT_DATE - interval '15 days', 60, 45);
        """))

        # --- Seed sales ---
        conn.execute(text("""
            INSERT INTO sales (product_id, sale_date, quantity, unit_price) VALUES
            (1, CURRENT_DATE - interval '3 months', 20, 900),
            (2, CURRENT_DATE - interval '2 months', 40, 80),
            (3, CURRENT_DATE - interval '1 month', 150, 12),
            (4, CURRENT_DATE - interval '10 days', 25, 75);
        """))
    print("✅ Seed data inserted successfully.")
