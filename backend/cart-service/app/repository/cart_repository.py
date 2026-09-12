import logging
import uuid
from typing import Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundException, AppException, ConflictException
from app.models import CartModel, CartItemModel

logger = logging.getLogger(__name__)


class CartRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create_cart_for_customer(self, customer_id: str) -> CartModel:
        """Each customer has exactly one active cart (guide's Cart
        allocation rule) — fetch it if it exists, otherwise create it.
        Handles the race where two concurrent requests both try to
        create the first cart for the same customer."""
        cart = self.db.query(CartModel).filter(CartModel.customer_id == customer_id).first()
        if cart:
            return cart

        new_cart = CartModel(id=f"cart-{uuid.uuid4().hex[:8]}", customer_id=customer_id)
        self.db.add(new_cart)
        try:
            self.db.commit()
            self.db.refresh(new_cart)
            logger.info("Created new cart %s for customer %s", new_cart.id, customer_id)
            return new_cart
        except IntegrityError:
            # Another concurrent request already created it — fetch that one instead.
            self.db.rollback()
            existing = self.db.query(CartModel).filter(CartModel.customer_id == customer_id).first()
            if existing:
                return existing
            logger.exception("Cart creation race condition could not be resolved for %s", customer_id)
            raise AppException("Failed to create cart", status_code=500)
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while creating cart for %s", customer_id)
            raise AppException("Failed to create cart", status_code=500)

    def get_cart_by_id(self, cart_id: str) -> CartModel:
        try:
            cart = self.db.query(CartModel).filter(CartModel.id == cart_id).first()
        except SQLAlchemyError:
            logger.exception("Database error while fetching cart %s", cart_id)
            raise AppException("Failed to retrieve cart", status_code=500)

        if not cart:
            raise NotFoundException(f"Cart {cart_id} not found")
        return cart

    def get_item(self, cart_id: str, product_id: str) -> Optional[CartItemModel]:
        return (
            self.db.query(CartItemModel)
            .filter(CartItemModel.cart_id == cart_id, CartItemModel.product_id == product_id)
            .first()
        )

    def add_or_increment_item(
        self, cart_id: str, product_id: str, product_name: str, unit_price: float, quantity: int
    ) -> CartItemModel:
        existing_item = self.get_item(cart_id, product_id)

        try:
            if existing_item:
                existing_item.quantity += quantity
                # Refresh the price snapshot in case it changed since last add.
                existing_item.unit_price = unit_price
                item = existing_item
            else:
                item = CartItemModel(
                    id=f"item-{uuid.uuid4().hex[:8]}",
                    cart_id=cart_id,
                    product_id=product_id,
                    product_name=product_name,
                    quantity=quantity,
                    unit_price=unit_price,
                )
                self.db.add(item)

            self.db.commit()
            self.db.refresh(item)
        except IntegrityError:
            self.db.rollback()
            logger.exception("Integrity error while adding item to cart %s", cart_id)
            raise ConflictException("Could not add item to cart due to a data conflict")
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while adding item to cart %s", cart_id)
            raise AppException("Failed to add item to cart", status_code=500)

        logger.info("Cart %s: item %s quantity now %s", cart_id, product_id, item.quantity)
        return item

    def update_item_quantity(self, item: CartItemModel, quantity: int) -> CartItemModel:
        item.quantity = quantity
        try:
            self.db.commit()
            self.db.refresh(item)
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while updating item %s", item.id)
            raise AppException("Failed to update cart item", status_code=500)

        logger.info("Cart %s: item %s quantity updated to %s", item.cart_id, item.product_id, quantity)
        return item

    def remove_item(self, item: CartItemModel) -> None:
        try:
            self.db.delete(item)
            self.db.commit()
        except SQLAlchemyError:
            self.db.rollback()
            logger.exception("Database error while removing item %s", item.id)
            raise AppException("Failed to remove cart item", status_code=500)

        logger.info("Removed item %s from cart %s", item.product_id, item.cart_id)