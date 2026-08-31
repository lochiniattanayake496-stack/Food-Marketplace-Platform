from app.database import Base, engine, SessionLocal
from app.models import UserModel

def init_db():
    Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing_users = db.query(UserModel).first()
    if not existing_users:
        seed_user = [
            UserModel(
                id="1",
                name="Ravindu Steward",
                email="ravindu.steward@example.com",
                role="DataSteward",
                status="ACTIVE"
            ),
            UserModel(
                id="2",
                email="supplier@farms.com",
                role="Supplier",
                name="Sahan Supplier",
                status="ACTIVE"
            ),
            UserModel(
                id="3",
                email="customer@gmail.com",
                role="Customer",
                name="Nirasha Customer",
                status="ACTIVE"
            )
        ]
        db.add_all(seed_user)
        db.commit()
        print("[User Service] Database tables created and seed data loaded.")
except Exception as e:
    print(f"[User Service] Error seeding database: {e}")
    db.rollback()
finally:
    db.close()