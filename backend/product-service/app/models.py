from sqlalchemy import Column, String, Float, DateTime
from datetime import datetime
from app.database import Base

class ProductModel(Base):
    __tablename__ = "products"

    id = Column(String, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=True)
    status = Column(String, nullable=False, default="PENDING", index=True)
    supplier_id = Column(String, nullable=False, index=True)
    rejection_reason = Column(String, nullable=True)
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
