from typing import Generic, TypeVar, Union

from pydantic import BaseModel

"""
support schema detail in fastapi swaggers docs
example
@router.get("/users", response_model=RespDataWithMeta[list[dto.User]])
"""

M = TypeVar("M", bound=BaseModel)


def generatePaginationNumberList(
    current_page: int = 1, amount: int = 10, data_count: int = 0
):
    page_total = int(((data_count - 1) / amount) + 1)
    if page_total <= 5:
        return [i for i in range(1, page_total + 1)]

    max_page_num_left = 2
    if current_page < 3:
        max_page_num_left = current_page - 1
    max_page_num_right = 5 - 1 - max_page_num_left
    if page_total - current_page < 3:
        max_page_num_right = page_total - current_page
        max_page_num_left = 5 - 1 - max_page_num_right

    return (
        [i for i in range(current_page - max_page_num_left, current_page)]
        + [current_page]
        + [i for i in range(current_page + 1, max_page_num_right + current_page + 1)]
    )

class BaseResp_Meta(BaseModel):
    code: int = 200
    error: bool = False
    message: str = "OK"
    error_detail: Union[str, list, dict, None] = None

class BaseResp(BaseModel):
    meta: BaseResp_Meta = BaseResp_Meta()

class RespData(BaseResp, Generic[M]):
    data: M = None  # support any object

class PaginationMeta(BaseModel):
    total: int = 0
    current_page: int = 0
    page_total: int = 0
    page_num_list: list[int] = [0]

    def __init__(self, total: int, page: int, limit: int, show_all: bool = False):
        """
        attributes will be calculated automatically by inputed __init__() args
        """
        if page == 0:
            page = 1

        super().__init__(
            total=total,
            current_page=1 if show_all else page,
            page_total=1 if show_all or not limit else int(((total - 1) / limit) + 1),
            page_num_list=(
                [1]
                if show_all or not limit
                else generatePaginationNumberList(
                    current_page=page, amount=limit, data_count=total
                )
            ),
        )