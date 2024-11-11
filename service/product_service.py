from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.model import product_model
from domain.rest import product_rest
from repository import product_repo
from utils import helper


class ProductService:
    def __init__(self, product_repo: product_repo.ProductRepo = Depends()):
        self.product_repo = product_repo

    def getList(
        self, query: product_rest.GetProductListReq
    ) -> tuple[list[product_rest.GetProductListRespDataItem], int]:
        sort_order = -1 if query.sort_order == "desc" else 1
        products, count = self.product_repo.getList(
            category_id=query.category_id,
            query=query.query,
            query_by=query.query_by,
            sort_by=query.sort_by,
            sort_order=sort_order,
            skip=helper.generateSkip(query.page, query.limit),
            limit=query.limit,
            do_count=True,
        )

        result = []
        for product in products:
            res_item = product_rest.GetProductListRespDataItem(**product.model_dump())
            result.append(res_item)

        return result, count
