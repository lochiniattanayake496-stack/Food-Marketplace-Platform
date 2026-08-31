from app.database import engine, SessionLocal, Base
from app.models import CartModel, CartItemModel

def init_db():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        existing_cart = db.query(CartModel).first()
        if not existing_cart:
            sample_cart = CartModel(id="cart-456", customer_id="cog-usr-003")
            db.add(sample_cart)
            db.commit()

            sample_item = CartItemModel(
                id="item-001",
                cart_id="cart-456",
                product_id="prod-101",
                product_name="Organic Apples",
                quantity=2,
                unit_price=4.99
            )
            db.add(sample_item)
            db.commit()
            print("[Cart Service] Database tables created and seed data loaded.")
    except Exception as e:
        print(f"[Cart Service] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()