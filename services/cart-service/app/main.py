
from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, Field
from typing import List

app = FastAPI(
    title="Cart Microservice API",
    description="Handles active shopping cart management, item quantities, and cart updates.",
    version="1.0.0"
)

# --- PYDANTIC MODELS (Data Contracts) ---


class CartItem(BaseModel):
    productId: str      
    productName: str    
    quantity: int      
    unitPrice: float    


class Cart(BaseModel):
    cartId: str             
    customerId: str         
    items: List[CartItem]  
    totalPrice: float      


class AddCartItemRequest(BaseModel):
    productId: str
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")  

# --- MOCK DATABASE ---

cart_db = {
    "cartId": "cart-456",
    "customerId": "cust-123",
    "items": [
        {
            "productId": "prod-101",
            "productName": "Organic Apples",
            "quantity": 2,
            "unitPrice": 4.99
        }
    ],
    "totalPrice": 9.98
}


def recalculate_total():
    cart_db["totalPrice"] = round(
        sum(item["quantity"] * item["unitPrice"] for item in cart_db["items"]), 2
    )

# --- API ENDPOINTS ---


@app.get("/api/v1/cart", response_model=Cart)
def get_cart(customerId: str = Query(..., description="The ID of the customer whose cart is being retrieved.")):
    """
    Fetch active shopping cart state for a given customerId.
    """
    
    if customerId != cart_db["customerId"]:
        raise HTTPException(status_code=404, detail="Cart not found for the given customer ID.")
    return cart_db


@app.post("/api/v1/cart/items", response_model=Cart)
def add_item_to_cart(request: AddCartItemRequest):
    """
    Add a product to the active cart.
    Increments quantity if item already exists in the cart.
    """
    # Mock lookup database of valid products for pricing
    mock_catalog = {
        "prod-101": {"name": "Organic Apples", "price": 4.99},
        "prod-102": {"name": "Whole Milk 1L", "price": 2.49}
    }
    
    
    if request.productId not in mock_catalog:
        raise HTTPException(status_code=400, detail="Invalid request body or product not found.")
    
    product_info = mock_catalog[request.productId]
    
   
    for item in cart_db["items"]:
        if item["productId"] == request.productId:
            item["quantity"] += request.quantity
            recalculate_total()  # Update total price
            return cart_db

    
    cart_db["items"].append({
        "productId": request.productId,
        "productName": product_info["name"],
        "quantity": request.quantity,
        "unitPrice": product_info["price"]
    })
    
    recalculate_total()  
    return cart_db


@app.delete("/api/v1/cart/items/{productId}", response_model=Cart)
def remove_item(productId: str):
    """
    Remove an item completely from the active shopping cart by product ID.
    """
    initial_item_count = len(cart_db["items"])
    
   
    cart_db["items"] = [item for item in cart_db["items"] if item["productId"] != productId]
    
   r
    if len(cart_db["items"]) == initial_item_count:
        raise HTTPException(status_code=404, detail="Product not found in the cart.")
    
    recalculate_total()  
    return cart_db