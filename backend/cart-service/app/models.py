from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class CartModel(Base):
    __tablename__ = "carts"

    id = Column(String, primary_key=True, index=True)   # was Integer
    customer_id = Column(String, unique=True, index=True, nullable=False)

    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")

class CartItemModel(Base):
    __tablename__ = "cart_items"

    id = Column(String, primary_key=True, index=True)   
    cart_id = Column(Integer, ForeignKey("carts.id"), nullable=False)
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Float, nullable=False)

    cart = relationship("CartModel", back_populates="items")