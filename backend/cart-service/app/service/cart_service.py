import logging

from sqlalchemy.orm import Session

from app.core.exceptions import ForbiddenException, ValidationException, NotFoundException
from app.models import CartModel, AddCartItemRequest, UpdateCartItemRequest
from app.repository.cart_repository import CartRepository
from app.service import product_client

logger = logging.getLogger(__name__)


class CartService:
    def __init__(self, db: Session):
        self.repository = CartRepository(db)

    def _to_response_dict(self, cart: CartModel) -> dict:
        total_price = sum(item.quantity * item.unit_price for item in cart.items)
        return {
            "id": cart.id,
            "customer_id": cart.customer_id,
            "items": cart.items,
            "total_price": total_price,
        }

    def _assert_owns_cart(self, cart: CartModel, current_customer_id: str) -> None:
        if cart.customer_id != current_customer_id:
            logger.warning(
                "Customer %s attempted to access cart %s owned by %s",
                current_customer_id, cart.id, cart.customer_id,
            )
            raise ForbiddenException("You do not have permission to access this cart")

    def get_my_cart(self, current_customer_id: str) -> dict:
        cart = self.repository.get_or_create_cart_for_customer(current_customer_id)
        return self._to_response_dict(cart)

    def add_item(self, cart_id: str, item_req: AddCartItemRequest, current_customer_id: str) -> dict:
        cart = self.repository.get_cart_by_id(cart_id)
        self._assert_owns_cart(cart, current_customer_id)

        # Always fetch real product data — price/name/availability are
        # never trusted from the client request body.
        product = product_client.fetch_product(item_req.product_id)

        existing_item = self.repository.get_item(cart_id, item_req.product_id)
        already_in_cart = existing_item.quantity if existing_item else 0
        requested_total = already_in_cart + item_req.quantity

        if requested_total > product.stock:
            raise ValidationException(
                f"Only {product.stock} of '{product.name}' available "
                f"({already_in_cart} already in cart)"
            )

        self.repository.add_or_increment_item(
            cart_id=cart_id,
            product_id=product.id,
            product_name=product.name,
            unit_price=product.price,
            quantity=item_req.quantity,
        )

        cart = self.repository.get_cart_by_id(cart_id)
        return self._to_response_dict(cart)

    def update_item_quantity(
        self, cart_id: str, product_id: str, update: UpdateCartItemRequest, current_customer_id: str
    ) -> dict:
        cart = self.repository.get_cart_by_id(cart_id)
        self._assert_owns_cart(cart, current_customer_id)

        item = self.repository.get_item(cart_id, product_id)
        if not item:
            raise NotFoundException("Item not found in cart")

        # Re-check stock against the live product, in case it changed
        # since the item was first added.
        product = product_client.fetch_product(product_id)
        if update.quantity > product.stock:
            raise ValidationException(f"Only {product.stock} of '{product.name}' available")

        self.repository.update_item_quantity(item, update.quantity)

        cart = self.repository.get_cart_by_id(cart_id)
        return self._to_response_dict(cart)

    def remove_item(self, cart_id: str, product_id: str, current_customer_id: str) -> dict:
        cart = self.repository.get_cart_by_id(cart_id)
        self._assert_owns_cart(cart, current_customer_id)

        item = self.repository.get_item(cart_id, product_id)
        if not item:
            raise NotFoundException("Item not found in cart")

        self.repository.remove_item(item)

        cart = self.repository.get_cart_by_id(cart_id)
        return self._to_response_dict(cart)