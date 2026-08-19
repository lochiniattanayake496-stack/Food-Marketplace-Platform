# Import column types and ForeignKey to link cart items to a parent cart
from sqlalchemy import Column, String, Float, Integer, ForeignKey

# Import relationship to enable object navigation (e.g., cart.items)
from sqlalchemy.orm import relationship

# Import Base from database configuration
from app.database import Base

# Parent SQL table storing active user carts
class CartModel(Base):
    __tablename__ = "carts"

   
    cart_id = Column(String, primary_key=True, index=True)
    
    
    customer_id = Column(String, nullable=False, unique=True, index=True)
    
   
    total_price = Column(Float, default=0.0)

    
    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")


# Child SQL table storing individual product items inside a cart
class CartItemModel(Base):
    __tablename__ = "cart_items"

   
    id = Column(Integer, primary_key=True, autoincrement=True)
    
   
    cart_id = Column(String, ForeignKey("carts.cart_id"), nullable=False)
    
   
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    unit_price = Column(Float, nullable=False)

   
    cart = relationship("CartModel", back_populates="items")