from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.rest import category_rest
from repository import category_repo
from utils import helper


class CategoryService:
    def __init__(self, category_repo: category_repo.CategoryRepo = Depends()):
        self.category_repo = category_repo

    def getList(
        self, query: category_rest.GetCategoryListReq
    ) -> tuple[list[category_rest.GetCategoryListRespDataItem], int]:
        sort_order = -1 if query.sort_order == "desc" else 1
        categories, count = self.category_repo.getList(
            query=query.query,
            query_by=query.query_by,
            sort_by=query.sort_by,
            sort_order=sort_order,
            skip=helper.generateSkip(query.page, query.limit),
            limit=query.limit,
            do_count=True,
        )

        result = []
        for category in categories:
            res_item = category_rest.GetCategoryListRespDataItem(
                **category.model_dump()
            )
            result.append(res_item)

        return result, count
