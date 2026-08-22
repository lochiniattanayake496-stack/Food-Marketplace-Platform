import uuid
from typing import List
from fastapi import FastAPI, HTTPException, Depends, Query, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CartModel, CartItemModel
from app.schemas import CartResponse, AddCartItemRequest, UpdateCartItemRequest
from app.seed import init_db

app = FastAPI(
    title="Cart Microservice API",
    description="Handles active shopping cart management, item quantities, and cart updates.",
    version="1.0.0"
)

@app.on_event("startup")
def on_startup():
    init_db()


#---GET ACTIVE CART BY CUSTOMER ID---

@app.get("/api/v1/carts", response_model=CartResponse)
def get_cart_by_customer_id(customer_id: str = Query(..., description="Unique Customer ID"), db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.customer_id == customer_id).first()
    if not cart:
        cart = CartModel(customer_id=customer_id)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    total_price = sum(item.quantity * item.price for item in cart.items)
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": cart.items,
        "totalPrice": total_price
    }

# --- ADD ITEM TO CART ---#

@app.post("/api/v1/carts/{cart_id}/items", response_model=CartResponse)
def add_or_update_cart_item(cart_id: str, item_req: AddCartItemRequest, db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    existing_item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.product_id == item_req.productId
    ).first()

    if existing_item:
        existing_item.quantity += item_req.quantity
    else:
        new_item = CartItemModel(
            id=f"item-{uuid.uuid4().hex[:6]}",
            cart_id=cart_id,
            product_id=item_req.productId,
            product_name=item_req.productName,
            quantity=item_req.quantity,
            unit_price=item_req.unitPrice
        )
        db.add(new_item)

    db.commit()
    db.refresh(cart)

    total_price = sum(i.quantity * i.unit_price for i in cart.items)
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": cart.items,
        "totalPrice": total_price
    }

# --- UPDATE ITEM IN CART ---#

@app.patch("/api/v1/carts/{cart_id}/items/{product_id}", response_model=CartResponse)
def patch_cart_item(
    cart_id: str, 
    product_id: str, 
    item_update: UpdateCartItemRequest, 
    db: Session = Depends(get_db)
):
    cart = db.query(CartModel).filter(CartModel.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart.")

    
    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(item, field, value)

    db.commit()
    db.refresh(cart)

    total_price = sum(i.quantity * i.unit_price for i in cart.items)
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": cart.items,
        "totalPrice": total_price
    }

# --- REMOVE ITEM FROM CART ---
@app.delete("/api/v1/carts/{cart_id}/items/{product_id}", response_model=CartResponse)
def remove_cart_item(cart_id: str, product_id: str, db: Session = Depends(get_db)):
    cart = db.query(CartModel).filter(CartModel.id == cart_id).first()
    if not cart:
        raise HTTPException(status_code=404, detail="Cart not found.")

    item = db.query(CartItemModel).filter(
        CartItemModel.cart_id == cart_id,
        CartItemModel.product_id == product_id
    ).first()

    if not item:
        raise HTTPException(status_code=404, detail="Item not found in cart.")

    db.delete(item)
    db.commit()
    db.refresh(cart)

    total_price = sum(i.quantity * i.unit_price for i in cart.items)
    return {
        "id": cart.id,
        "customer_id": cart.customer_id,
        "items": cart.items,
        "totalPrice": total_price
    }