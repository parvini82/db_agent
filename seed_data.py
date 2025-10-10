from faker import Faker
import random
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text

# ---------- Database Configuration ----------
DB_URL = "postgresql+psycopg2://postgres:postgres123@localhost:5433/db_agent"
engine = create_engine(DB_URL)
fake = Faker()

# ---------- Number of Records for Each Table ----------
NUM_PRODUCTS = 50
NUM_SUPPLIERS = 10
NUM_PURCHASES = 200
NUM_SALES = 300


# ---------- Seed Functions ----------
def seed_products():
    """Generate and insert fake products into the database."""
    print("Seeding products...")
    categories = ["Food", "Drink", "Pet", "Electronics", "Clothes", "Toys"]
    with engine.begin() as conn:
        for _ in range(NUM_PRODUCTS):
            conn.execute(
                text("""
                    INSERT INTO products (name, category, description)
                    VALUES (:name, :category, :description)
                """),
                {
                    "name": fake.word().capitalize(),
                    "category": random.choice(categories),
                    "description": fake.sentence()
                }
            )


def seed_suppliers():
    """Generate and insert fake suppliers into the database."""
    print("Seeding suppliers...")
    with engine.begin() as conn:
        for _ in range(NUM_SUPPLIERS):
            conn.execute(
                text("""
                    INSERT INTO suppliers (name, city, address)
                    VALUES (:name, :city, :address)
                """),
                {
                    "name": fake.company(),
                    "city": fake.city(),
                    "address": fake.address()
                }
            )


def seed_purchases():
    """Generate and insert fake purchase records into the database."""
    print("Seeding purchases...")
    with engine.begin() as conn:
        for _ in range(NUM_PURCHASES):
            conn.execute(
                text("""
                    INSERT INTO purchases (product_id, supplier_id, purchase_date, quantity, unit_cost)
                    VALUES (:product_id, :supplier_id, :purchase_date, :quantity, :unit_cost)
                """),
                {
                    "product_id": random.randint(1, NUM_PRODUCTS),
                    "supplier_id": random.randint(1, NUM_SUPPLIERS),
                    "purchase_date": fake.date_between(start_date="-6M", end_date="today"),
                    "quantity": random.randint(10, 200),
                    "unit_cost": round(random.uniform(5, 150), 2)
                }
            )


def seed_sales():
    """Generate and insert fake sales records into the database."""
    print("Seeding sales...")
    with engine.begin() as conn:
        for _ in range(NUM_SALES):
            conn.execute(
                text("""
                    INSERT INTO sales (product_id, sale_date, quantity, unit_price)
                    VALUES (:product_id, :sale_date, :quantity, :unit_price)
                """),
                {
                    "product_id": random.randint(1, NUM_PRODUCTS),
                    "sale_date": fake.date_between(start_date="-3M", end_date="today"),
                    "quantity": random.randint(1, 50),
                    "unit_price": round(random.uniform(10, 200), 2)
                }
            )



