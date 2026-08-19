from app.database import SessionLocal, engine, Base
from app.models import ProductModel

def init_db():
    Base.metadata.create_all(bind=engine)

db = SessionLocal()
try:
    existing_products = db.query(ProductModel).first()
    if not existing_products:
        # Seed the database with initial products
        seed_products = [
            ProductModel(
                id="1",
                name="Product 1",
                description="Description for Product 1",
                price=10.99,
                category="Category A",
                status="PENDING",
                supplier_id="supplier_1"
            ),
            ProductModel(
                id="2",
                name="Product 2",
                description="Description for Product 2",
                price=15.49,
                category="Category B",
                status="PENDING",
                supplier_id="supplier_2"
            ),
            ProductModel(
                id="3",
                name="Product 3",
                description="Description for Product 3",
                price=7.99,
                category="Category A",
                status="PENDING",
                supplier_id="supplier_3"
            ),
        ]
        db.add_all(seed_products)
        db.commit()
        print("[Product Service] Database tables created and seed data loaded successfully.")
except Exception as e:
    print(f"[Product Service] Error seeding database: {e}")
    db.rollback()
finally:
    db.close()