from fastapi import Depends, APIRouter
from core.dependencies import verifyToken
from domain.rest import product_rest, generic_resp
from service import product_service
from domain.dto import auth_dto


ProductRouter = APIRouter(
    prefix="/products",
    tags=["Product"],
    dependencies=[Depends(verifyToken)],
)


@ProductRouter.get(
    "",
    response_model=generic_resp.RespData[
        generic_resp.PaginatedData[product_rest.GetProductListRespDataItem]
    ],
)
def get_product_list(
    query: product_rest.GetProductListReq = Depends(),
    product_service: product_service.ProductService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data, count = product_service.getList(query=query, curr_user_id=current_user.id)

    paginated_data = generic_resp.PaginatedData[
        product_rest.GetProductListRespDataItem
    ](total=count, page=query.page, limit=query.limit, data=data)

    return generic_resp.RespData[
        generic_resp.PaginatedData[product_rest.GetProductListRespDataItem]
    ](data=paginated_data)


@ProductRouter.get(
    "/{product_id}",
    response_model=generic_resp.RespData[product_rest.GetProductDetailRespData],
)
def get_product_detail(
    product_id: str,
    product_service: product_service.ProductService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    product = product_service.getProductDetail(
        product_id=product_id, curr_user_id=current_user.id
    )

    return generic_resp.RespData[product_rest.GetProductDetailRespData](data=product)
