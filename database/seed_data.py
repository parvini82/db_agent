from sqlalchemy import text
from faker import Faker
import random
from database.connection import engine

def seed_data():
    fake = Faker()
    categories = ["Electronics", "Grocery", "Footwear", "Clothing", "Office", "Home", "Sports"]

    with engine.begin() as conn:
        # 🧹 Clean existing tables
        conn.execute(text("TRUNCATE TABLE sales, purchases, products, suppliers RESTART IDENTITY CASCADE;"))

        # --- Seed products ---
        products = [
            (fake.word().capitalize(), random.choice(categories), fake.sentence(nb_words=4))
            for _ in range(20)
        ]
        conn.execute(
            text(
                "INSERT INTO products (name, category, description) VALUES " +
                ",".join([f"('{p[0]}','{p[1]}','{p[2]}')" for p in products]) + ";"
            )
        )

        # --- Seed suppliers ---
        suppliers = [
            (fake.company(), fake.city(), fake.address())
            for _ in range(10)
        ]
        conn.execute(
            text(
                "INSERT INTO suppliers (name, city, address) VALUES " +
                ",".join([f"('{s[0]}','{s[1]}','{s[2]}')" for s in suppliers]) + ";"
            )
        )

        # --- Seed purchases ---
        purchase_values = []
        for _ in range(50):
            purchase_values.append(
                f"({random.randint(1, 20)}, {random.randint(1, 10)}, "
                f"CURRENT_DATE - interval '{random.randint(10, 120)} days', "
                f"{random.randint(10, 200)}, {round(random.uniform(5, 1000), 2)})"
            )
        conn.execute(
            text(
                "INSERT INTO purchases (product_id, supplier_id, purchase_date, quantity, unit_cost) VALUES "
                + ",".join(purchase_values) + ";"
            )
        )

        # --- Seed sales ---
        sale_values = []
        for _ in range(100):
            sale_values.append(
                f"({random.randint(1, 20)}, "
                f"CURRENT_DATE - interval '{random.randint(1, 90)} days', "
                f"{random.randint(1, 100)}, {round(random.uniform(10, 2000), 2)})"
            )
        conn.execute(
            text(
                "INSERT INTO sales (product_id, sale_date, quantity, unit_price) VALUES "
                + ",".join(sale_values) + ";"
            )
        )

    print("✅ Randomized seed data inserted successfully.")
