# Import models and database session setup
from app.database import engine, SessionLocal, Base
from app.models import CartModel, CartItemModel

def init_db():
    # Automatically create tables (carts and cart_items)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if cart table is empty before seeding
        existing_cart = db.query(CartModel).first()
        if not existing_cart:
            # Seed an active shopping cart for customer 'cust-123'
            initial_cart = CartModel(
                cart_id="cart-456",
                customer_id="cust-123",
                total_price=9.98
            )
            db.add(initial_cart)
            db.flush()  # Flush to register cart_id for line-item foreign key

            # Add an initial item to this cart
            initial_item = CartItemModel(
                cart_id="cart-456",
                product_id="prod-101",
                product_name="Organic Apples",
                quantity=2,
                unit_price=4.99
            )
            db.add(initial_item)
            db.commit()
            print("[Cart Service] Initial database tables and seed data created successfully.")
    except Exception as e:
        print(f"[Cart Service] Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()