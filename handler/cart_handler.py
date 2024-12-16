from fastapi import APIRouter, Depends
from core.dependencies import verifyToken
from domain.dto import auth_dto
from service import cart_service
from domain.rest import generic_resp, cart_rest
from utils import request as req_utils
from core.dependencies import formOrJsonDependGenerator

CartRouter = APIRouter(
    prefix="/cart",
    tags=["Cart"],
    dependencies=[Depends(verifyToken)],
)


@CartRouter.get(
    "",
    description="get current user cart",
    response_model=generic_resp.RespData[cart_rest.GetUserCartDetailRespData],
)
def get_user_cart(
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    cart_service: cart_service.CartService = Depends(),
):
    data = cart_service.getUserCartDetail(current_user=current_user)
    return generic_resp.RespData[cart_rest.GetUserCartDetailRespData](data=data)


@CartRouter.post(
    "/items",
    description="add item to cart",
    response_model=generic_resp.RespData[cart_rest.AddToCartRespData],
    openapi_extra={
        "requestBody": req_utils.generateFormOrJsonOpenapiBody(cart_rest.AddToChartReq)
    },
)
def add_to_cart(
    payload=formOrJsonDependGenerator(cart_rest.AddToChartReq),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    cart_service: cart_service.CartService = Depends(),
):
    data = cart_service.addToCart(payload=payload, current_user=current_user)
    return generic_resp.RespData[cart_rest.AddToCartRespData](data=data)


@CartRouter.delete(
    "/items/{cart_item_id}",
    description="delete item from cart",
    response_model=generic_resp.RespData[cart_rest.DeleteCartItemRespData],
)
def delete_cart_item(
    cart_item_id: str,
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    cart_service: cart_service.CartService = Depends(),
):
    data = cart_service.deleteCartItem(
        current_user=current_user, cart_item_id=cart_item_id
    )
    return generic_resp.RespData[cart_rest.DeleteCartItemRespData](data=data)


@CartRouter.patch(
    "/items/{cart_item_id}",
    description="update item in cart",
    response_model=generic_resp.RespData[cart_rest.UpdateCartItemRespData],
    openapi_extra={
        "requestBody": req_utils.generateFormOrJsonOpenapiBody(
            cart_rest.UpdateCartItemReq
        )
    },
)
def update_cart_item(
    cart_item_id: str,
    payload=formOrJsonDependGenerator(cart_rest.UpdateCartItemReq),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
    cart_service: cart_service.CartService = Depends(),
):
    data = cart_service.updateCartItem(
        current_user=current_user, cart_item_id=cart_item_id, payload=payload
    )
    return generic_resp.RespData[cart_rest.UpdateCartItemRespData](data=data)