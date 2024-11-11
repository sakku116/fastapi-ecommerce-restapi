from fastapi import Depends, APIRouter
from core.dependencies import verifyToken
from domain.rest import product_rest, generic_resp
from service import product_service


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
):
    data, count = product_service.getList(query=query)

    paginated_data = generic_resp.PaginatedData[
        product_rest.GetProductListRespDataItem
    ](total=count, page=query.page, limit=query.limit, data=data)

    return generic_resp.RespData[
        generic_resp.PaginatedData[product_rest.GetProductListRespDataItem]
    ](data=paginated_data)
