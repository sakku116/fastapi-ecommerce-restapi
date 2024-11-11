from fastapi import Depends, APIRouter
from core.dependencies import verifyToken
from domain.rest import category_rest, generic_resp
from service import category_service


CategoryRouter = APIRouter(
    prefix="/categories",
    tags=["Category"],
    dependencies=[Depends(verifyToken)],
)


@CategoryRouter.get(
    "",
    response_model=generic_resp.RespData[
        generic_resp.PaginatedData[category_rest.GetCategoryListRespDataItem]
    ],
)
def get_product_list(
    query: category_rest.GetCategoryListReq = Depends(),
    category_service: category_service.CategoryService = Depends(),
):
    data, count = category_service.getList(query=query)

    paginated_data = generic_resp.PaginatedData[
        category_rest.GetCategoryListRespDataItem
    ](total=count, page=query.page, limit=query.limit, data=data)

    return generic_resp.RespData[
        generic_resp.PaginatedData[category_rest.GetCategoryListRespDataItem]
    ](data=paginated_data)
