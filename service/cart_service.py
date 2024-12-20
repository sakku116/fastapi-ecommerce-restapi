from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto, cart_dto
from domain.model import cart_model
from domain.rest import cart_rest
from repository import cart_repo, product_repo
from utils import helper


class CartService:
    def __init__(
        self,
        cart_repo: cart_repo.CartRepo = Depends(),
        product_repo: product_repo.ProductRepo = Depends(),
    ) -> None:
        self.cart_repo = cart_repo
        self.product_repo = product_repo

    def addToCart(
        self,
        payload: cart_rest.AddToChartReq,
        current_user: auth_dto.CurrentUser,
    ) -> cart_rest.AddToCartRespData:
        time_now = helper.timeNow()

        # check if cart exists
        cart = self.cart_repo.getByUserId(user_id=current_user.id)
        if not cart:
            # create new cart
            logger.debug(f"cart not found, creating new one for user {current_user.id}")
            cart = cart_model.CartModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                user_id=current_user.id,
            )
            self.cart_repo.create(cart=cart)

        # check product
        product = self.product_repo.getById(id=payload.product_id)
        if not product:
            logger.debug(f"product not found: {payload.product_id}")
            exc = CustomHttpException(
                status_code=400,
                message=f"product not found: {payload.product_id}",
            )
            raise exc

        # check product_variant
        product_variant = self.product_repo.getProductVariant(
            id=payload.product_variant_id
        )
        if not product_variant:
            logger.debug(f"product variant not found: {payload.product_variant_id}")
            exc = CustomHttpException(
                status_code=400,
                message=f"product variant not found: {payload.product_variant_id}",
            )
            raise exc

        # check cart item by product_id and pruduct_variant_id
        cart_item = self.cart_repo.getCartItem(
            cart_id=cart.id,
            product_id=payload.product_id,
            product_variant_id=payload.product_variant_id,
        )
        if not cart_item:
            # create cart item
            logger.debug(
                f"cart item for cart {cart.id} not found, creating new one for user {current_user.id}"
            )
            cart_item = cart_model.CartItemModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                created_by=current_user.id,
                cart_id=cart.id,
                product_id=payload.product_id,
                product_variant_id=payload.product_variant_id,
                quantity=payload.quantity,
            )
            self.cart_repo.create(cart_item=cart_item)

        else:
            # update cart item
            logger.debug(f"cart item of cart {cart.id} found, updating it")
            cart_item.quantity += payload.quantity
            cart_item.updated_at = helper.timeNow()
            cart_item = self.cart_repo.updateCartItem(
                id=cart_item.id, cart_item=cart_item
            )
            if not cart_item:
                logger.error(f"failed to update cart item: {cart_item}")
                exc = CustomHttpException(
                    status_code=500,
                    message=f"failed to update cart item: {cart_item}",
                )
                raise exc

        # response
        resp = cart_rest.AddToCartRespData(
            id=cart_item.id,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
            product_name=product.name,
            quantity=cart_item.quantity,
            description=product.description,
            price_per_unit=product_variant.price,
            price_per_unit_currency=product_variant.price_currency,
            localized_price_per_unit=helper.localizePrice(
                price=product_variant.price,
                currency_code=current_user.currency,
                language_code=current_user.language,
            ),  # TODO: change to precise currency exchange rate
        )

        return resp

    def updateCartItem(
        self,
        current_user: auth_dto.CurrentUser,
        cart_item_id: str,
        payload: cart_rest.UpdateCartItemReq,
    ) -> cart_rest.UpdateCartItemRespData:
        # check cart item
        cart_item = self.cart_repo.getCartItemById(
            id=cart_item_id,
        )
        if not cart_item:
            logger.debug(f"cart item not found: {cart_item_id}")
            exc = CustomHttpException(
                status_code=400,
                message=f"cart item not found: {cart_item_id}",
            )
            raise exc

        # get cart
        cart = self.cart_repo.getById(id=cart_item.cart_id)
        if not cart:
            logger.debug(f"cart not found: {cart_item.cart_id}")
            exc = CustomHttpException(
                status_code=500,
                message=f"internal server error",
                detail="cart not found",
            )
            raise exc

        # validate cart ownership
        if cart.user_id != current_user.id:
            logger.debug(f"cart of cart item not owned by user: {current_user.id}")
            exc = CustomHttpException(
                status_code=403,
                message=f"forbidden",
                detail="cart of cart item not owned by user",
            )
            raise exc

        # lookup product
        product = self.product_repo.getById(id=cart_item.product_id)
        if not product:
            logger.debug(f"product not found: {cart_item.product_id}")
            exc = CustomHttpException(
                status_code=500,
                message=f"internal server error",
                detail=f"product not found: {cart_item.product_id}",
            )
            raise exc

        # lookup product variant
        product_variant = self.product_repo.getProductVariant(
            id=cart_item.product_variant_id
        )
        if not product_variant:
            logger.debug(f"product variant not found: {cart_item.product_variant_id}")
            exc = CustomHttpException(
                status_code=500,
                message=f"internal server error",
                detail=f"product variant not found: {cart_item.product_variant_id}",
            )
            raise exc

        # update fields
        if payload.description != None:
            if payload.description == "null":
                cart_item.description = None
            else:
                cart_item.description = payload.description

        if payload.quantity != None:
            if payload.quantity <= 0:
                logger.debug(f"invalid quantity: {payload.quantity}")
                exc = CustomHttpException(
                    status_code=400,
                    message=f"invalid quantity: {payload.quantity}",
                )
                raise exc

            cart_item.quantity = payload.quantity

        cart_item.updated_at = helper.timeNow()

        # update cart
        cart_item = self.cart_repo.updateCartItem(id=cart_item.id, cart_item=cart_item)
        if not cart_item:
            logger.error(f"failed to update cart item: {cart_item}")
            exc = CustomHttpException(
                status_code=500,
                message=f"failed to update cart item: {cart_item}",
            )
            raise exc

        # response
        resp = cart_rest.UpdateCartItemRespData(
            id=cart_item.id,
            created_at=cart_item.created_at,
            updated_at=cart_item.updated_at,
            product_name=product.name,
            quantity=cart_item.quantity,
            description=cart_item.description,
            price_per_unit=product_variant.price,
            price_per_unit_currency=product_variant.price_currency,
            localized_price_per_unit=helper.localizePrice(
                price=product_variant.price,
                currency_code=current_user.currency,
                language_code=current_user.language,
            ),
        )

        return resp

    def getUserCartDetail(
        self, current_user: auth_dto.CurrentUser
    ) -> cart_rest.GetUserCartDetailRespData:
        time_now = helper.timeNow()

        # check if cart exists
        cart = self.cart_repo.getByUserId(user_id=current_user.id)
        if not cart:
            # create new cart
            logger.debug(f"cart not found, creating new one for user {current_user.id}")
            cart = cart_model.CartModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                user_id=current_user.id,
            )
            self.cart_repo.create(cart=cart)

        # get cart items
        cart_items = self.cart_repo.getCartItemsByCartId(cart_id=cart.id)

        # items
        final_cart_items = []
        final_total_price = 0  # TODO: update this to precise currency exchange rate calculation
        for item in cart_items:
            # lookup product
            product = self.product_repo.getById(id=item.product_id)
            if not product:
                logger.warning(
                    f"product {item.product_id} not found for cart item {item.id}"
                )
                continue

            # lookup product variant
            variant = self.product_repo.getProductVariant(id=item.product_variant_id)
            if not variant:
                logger.warning(
                    f"product variant {item.product_variant_id} not found for cart item {item.id}"
                )
                continue

            final_cart_items.append(item)
            final_total_price += item.quantity * variant.price

        # prepare response
        resp = cart_rest.GetUserCartDetailRespData(
            total_items=len(cart_items),
            localized_total_price=helper.localizePrice(
                price=final_total_price,
                currency_code=current_user.currency,
                language_code=current_user.language,
            ),
        )

        return resp

    def deleteCartItem(
        self, current_user: auth_dto.CurrentUser, cart_item_id: str
    ) -> cart_rest.DeleteCartItemRespData:
        # check cart item
        cart_item = self.cart_repo.getCartItemById(
            id=cart_item_id,
        )
        if not cart_item:
            logger.debug(f"cart item not found: {cart_item_id}")
            exc = CustomHttpException(
                status_code=404,
                message=f"cart item not found",
            )
            raise exc

        # get cart
        cart = self.cart_repo.getById(id=cart_item.cart_id)
        if not cart:
            logger.debug(f"cart not found: {cart_item.cart_id}")
            exc = CustomHttpException(
                status_code=500,
                message=f"internal server error",
                detail="cart not found",
            )
            raise exc

        # check if cart is owned by user
        if cart.user_id != current_user.id:
            logger.debug(f"cart of cart item not owned by user: {current_user.id}")
            exc = CustomHttpException(
                status_code=403,
                message=f"forbidden",
                detail="cart of cart item not owned by user",
            )
            raise exc

        # delete cart item
        self.cart_repo.deleteCartItem(id=cart_item.id)

        # response
        resp = cart_rest.DeleteCartItemRespData(**cart.model_dump())
        return resp

    def getCartItems(
        self, current_user: auth_dto.CurrentUser
    ) -> list[cart_rest.GetChartItemsRespDataItem]:
        # get cart
        cart = self.cart_repo.getByUserId(user_id=current_user.id)
        if not cart:
            logger.debug(f"cart not found: {current_user.id}")
            exc = CustomHttpException(
                status_code=404,
                message=f"cart not found",
            )
            raise exc

        # get cart items
        cart_items = self.cart_repo.getCartItemsByCartId(cart_id=cart.id)

        # prepare response
        resp = []
        for item in cart_items:
            res_item = cart_rest.GetChartItemsRespDataItem(
                id=item.id,
                created_at=item.created_at,
                updated_at=item.updated_at,
                quantity=item.quantity,
                description=item.description,
            )

            # lookup product
            product = self.product_repo.getById(id=item.product_id)
            if not product:
                logger.warning(
                    f"product {item.product_id} not found for cart item {item.id}"
                )
                continue

            # lookup product_variant
            variant = self.product_repo.getProductVariant(id=item.product_variant_id)
            if not variant:
                logger.warning(
                    f"product variant {item.product_variant_id} not found for cart item {item.id}"
                )
                continue

            res_item.product_name = product.name
            res_item.price_per_unit = variant.price
            res_item.price_per_unit_currency = current_user.currency
            res_item.localized_price_per_unit = helper.localizePrice(
                price=variant.price,
                currency_code=current_user.currency,
                language_code=current_user.language,
            ) # TODO: update to precise currency exchange rate

            resp.append(res_item)

        return resp