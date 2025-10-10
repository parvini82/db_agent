from sqlalchemy import Column, Integer, String, Float, ForeignKey, Date
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# --- Products table ---
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    category = Column(String, nullable=False)
    description = Column(String)

    sales = relationship("Sale", back_populates="product")
    purchases = relationship("Purchase", back_populates="product")


# --- Suppliers table ---
class Supplier(Base):
    __tablename__ = "suppliers"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    city = Column(String)
    address = Column(String)

    purchases = relationship("Purchase", back_populates="supplier")


# --- Purchases table ---
class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    supplier_id = Column(Integer, ForeignKey("suppliers.id"))
    purchase_date = Column(Date)
    quantity = Column(Integer)
    unit_cost = Column(Float)

    product = relationship("Product", back_populates="purchases")
    supplier = relationship("Supplier", back_populates="purchases")


# --- Sales table ---
class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"))
    sale_date = Column(Date)
    quantity = Column(Integer)
    unit_price = Column(Float)

    product = relationship("Product", back_populates="sales")
