# Import Column and String types for pending submissions table
from sqlalchemy import Column, String

# Import Base class from database session setup
from app.database import Base

# Define SQL table model for Data Steward approval queue
class SubmissionModel(Base):
    __tablename__ = "approval_submissions"

    # Unique submission queue ID (primary key)
    submission_id = Column(String, primary_key=True, index=True)
    
    # Product details submitted for review
    product_id = Column(String, nullable=False)
    product_name = Column(String, nullable=False)
    supplier_id = Column(String, nullable=False)
    
    # Review status ("PENDING", "APPROVED", "REJECTED")
    status = Column(String, nullable=False, default="PENDING", index=True)
    
    # Mandatory field captured when status changes to REJECTED
    rejection_reason = Column(String, nullable=True)
    
    # ISO timestamp string of submission creation
    created_at = Column(String, nullable=False)