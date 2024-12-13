from fastapi import Depends, APIRouter
from core.dependencies import verifyToken, RoleRequired
from domain.rest import category_rest, generic_resp
from service import category_service
from domain.dto import auth_dto


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


@CategoryRouter.post(
    "",
    tags=["Admin Only"],
    description="admin only",
    response_model=generic_resp.RespData[category_rest.CreateCategoryRespData],
)
def create_category(
    payload: category_rest.CreateCategoryReq = Depends(),
    category_service: category_service.CategoryService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(RoleRequired(role=["admin"])),
):
    data = category_service.createCategory(
        payload=payload, curr_user_id=current_user.id
    )

    resp = generic_resp.RespData[category_rest.CreateCategoryRespData](data=data)
    resp.meta.message = "Category created successfully"
    return resp

@CategoryRouter.patch(
    "/{category_id}",
    tags=["Admin Only"],
    description="admin only",
    response_model=generic_resp.RespData[category_rest.PatchCategoryRespData],
)
def patch_category(
    category_id: str,
    payload: category_rest.PatchCategoryReq = Depends(),
    category_service: category_service.CategoryService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(RoleRequired(role=["admin"])),
):
    data = category_service.patchCategory(
        category_id=category_id, payload=payload
    )

    resp = generic_resp.RespData[category_rest.PatchCategoryRespData](data=data)
    resp.meta.message = "Category updated successfully"
    return resp