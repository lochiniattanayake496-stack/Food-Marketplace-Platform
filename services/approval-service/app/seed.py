# Import models and database session configuration
from app.database import engine, SessionLocal, Base
from app.models import SubmissionModel

def init_db():
    # Automatically create approval_submissions table
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if submissions queue is empty
        existing_submission = db.query(SubmissionModel).first()
        if not existing_submission:
            # Seed initial pending product submissions awaiting Data Steward review
            seed_submissions = [
                SubmissionModel(
                    submission_id="sub-202",
                    product_id="prod-101",
                    product_name="Organic Apples",
                    supplier_id="sup-88",
                    status="PENDING",
                    created_at="2026-06-01T12:00:00Z"
                ),
                SubmissionModel(
                    submission_id="sub-203",
                    product_id="prod-103",
                    product_name="Artisanal Cheese",
                    supplier_id="sup-45",
                    status="PENDING",
                    created_at="2026-06-02T14:30:00Z"
                )
            ]
            db.add_all(seed_submissions)
            db.commit()
            print("[Approval Service] Initial database tables and seed data created successfully.")
    except Exception as e:
        print(f"[Approval Service] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()