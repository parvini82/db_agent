from sqlalchemy import create_engine, Column, Integer, String, Float, Text, Date, ForeignKey, func
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from datetime import date

Base = declarative_base()


# -----------------------------
# MODELS
# -----------------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    category = Column(String)
    description = Column(Text)

    purchases = relationship("Purchase", back_populates="product", cascade="all, delete-orphan")
    sales = relationship("Sale", back_populates="product", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, category={self.category})>"


class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)
    city = Column(String)
    address = Column(String)

    purchases = relationship("Purchase", back_populates="supplier", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Supplier(id={self.id}, name={self.name}, city={self.city})>"


class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    supplier_id = Column(Integer, ForeignKey("suppliers.id"), nullable=False)
    purchase_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_cost = Column(Float, nullable=False)

    product = relationship("Product", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")

    def __repr__(self):
        return f"<Purchase(id={self.id}, product_id={self.product_id}, supplier_id={self.supplier_id}, quantity={self.quantity})>"


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    sale_date = Column(Date, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    product = relationship("Product", back_populates="sales")

    def __repr__(self):
        return f"<Sale(id={self.id}, product_id={self.product_id}, quantity={self.quantity}, unit_price={self.unit_price})>"


# -----------------------------
# DATABASE SETUP
# -----------------------------
def get_engine():
    """Change host here depending on Docker or local."""
    return create_engine("postgresql+psycopg2://postgres:postgres123@localhost:5433/db_agent")



engine = get_engine()
Session = sessionmaker(bind=engine)


# -----------------------------
# SEED DATA
# -----------------------------
def seed_data(session):
    """Insert sample data into all tables if empty."""
    if session.query(Product).count() > 0:
        print("Database already seeded.")
        return

    # Products
    p1 = Product(name="Laptop", category="Electronics", description="High performance laptop")
    p2 = Product(name="Smartphone", category="Electronics", description="Latest model smartphone")
    p3 = Product(name="Tablet", category="Electronics", description="Portable tablet device")

    # Suppliers
    s1 = Supplier(name="Tech Supplies Inc.", city="New York", address="123 Tech Street")
    s2 = Supplier(name="Mobile Distributors", city="San Francisco", address="456 Mobile Ave")

    session.add_all([p1, p2, p3, s1, s2])
    session.commit()

    # Purchases
    purchases = [
        Purchase(product_id=p1.id, supplier_id=s1.id, purchase_date=date(2023, 1, 15), quantity=50, unit_cost=800.0),
        Purchase(product_id=p1.id, supplier_id=s2.id, purchase_date=date(2023, 2, 20), quantity=30, unit_cost=850.0),
        Purchase(product_id=p2.id, supplier_id=s1.id, purchase_date=date(2023, 1, 10), quantity=100, unit_cost=500.0),
        Purchase(product_id=p3.id, supplier_id=s2.id, purchase_date=date(2023, 3, 25), quantity=75, unit_cost=350.0),
    ]

    # Sales
    sales = [
        Sale(product_id=p1.id, sale_date=date(2023, 1, 25), quantity=10, unit_price=1000.0),
        Sale(product_id=p2.id, sale_date=date(2023, 2, 15), quantity=50, unit_price=600.0),
        Sale(product_id=p3.id, sale_date=date(2023, 4, 5), quantity=20, unit_price=400.0),
    ]

    session.add_all(purchases + sales)
    session.commit()
    print("✅ Data seeding complete!")


# -----------------------------
# QUERIES
# -----------------------------
def highest_profit_product(session):
    """Compute product with highest profit = total sales revenue - total purchase cost."""
    result = (
        session.query(
            Product.name.label("product_name"),
            func.sum(Sale.quantity * Sale.unit_price - Purchase.quantity * Purchase.unit_cost).label("profit"),
        )
        .join(Sale, Sale.product_id == Product.id)
        .join(Purchase, Purchase.product_id == Product.id)
        .group_by(Product.id)
        .order_by(func.sum(Sale.quantity * Sale.unit_price - Purchase.quantity * Purchase.unit_cost).desc())
        .first()
    )
    if result:
        print(f"💰 Highest profit product: {result.product_name} → Profit: {round(result.profit, 2)}")
    else:
        print("No data found.")


# -----------------------------
# MAIN
# -----------------------------
if __name__ == "__main__":
    Base.metadata.create_all(engine)
    session = Session()

    seed_data(session)
    highest_profit_product(session)

    session.close()
