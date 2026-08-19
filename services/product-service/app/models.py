
from sqlalchemy import Column, String, Float

from app.database import Base

class ProductModel(Base):
    __tablename__ = "products"

    
    id = Column(String, primary_key=True, index=True)
    
   
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False, index=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    supplier_id = Column(String, nullable=False)