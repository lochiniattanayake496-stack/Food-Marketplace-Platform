from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.core.auth import get_current_user, CurrentUser
from app.models import CartResponse, AddCartItemRequest, UpdateCartItemRequest
from app.service.cart_service import CartService

router = APIRouter(prefix="/api/v1/carts", tags=["Cart"])


@router.get("", response_model=CartResponse)
def get_my_cart(
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """Returns (or creates) the calling customer's own active cart.
    No customer_id query param — identity comes from the auth token,
    so a customer can never fetch anyone else's cart."""
    service = CartService(db)
    return service.get_my_cart(current_user.id)


@router.post("/{cart_id}/items", response_model=CartResponse)
def add_item_to_cart(
    cart_id: str,
    item_req: AddCartItemRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = CartService(db)
    return service.add_item(cart_id, item_req, current_user.id)


@router.patch("/{cart_id}/items/{product_id}", response_model=CartResponse)
def update_cart_item(
    cart_id: str,
    product_id: str,
    item_update: UpdateCartItemRequest,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = CartService(db)
    return service.update_item_quantity(cart_id, product_id, item_update, current_user.id)


@router.delete("/{cart_id}/items/{product_id}", response_model=CartResponse)
def remove_cart_item(
    cart_id: str,
    product_id: str,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    service = CartService(db)
    return service.remove_item(cart_id, product_id, current_user.id)