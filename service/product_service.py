from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.model import product_model
from domain.rest import product_rest
from repository import product_repo, user_repo
from utils import helper
from babel.numbers import format_currency
from babel import Locale

class ProductService:
    def __init__(self, product_repo: product_repo.ProductRepo = Depends(), user_repo: user_repo.UserRepo = Depends()):
        self.product_repo = product_repo
        self.user_repo = user_repo

    def getList(
        self, query: product_rest.GetProductListReq, curr_user_id: str
    ) -> tuple[list[product_rest.GetProductListRespDataItem], int]:
        current_user = self.user_repo.getById(id=curr_user_id)
        if not current_user:
            exc = CustomHttpException(
                status_code=500,
                message="User not found",
            )
            logger.error(exc)
            raise exc

        user_local = Locale(current_user.language)
        user_local.default

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
            res_item = product_rest.GetProductListRespDataItem(
                name=product.name,
                price=product.price,
                img=product.img
            )

            # localize price
            if product.price:
                res_item.localized_price = helper.localizePrice(
                    price=product.price,
                    currency_code=current_user.currency,
                    language_code=current_user.language
                )

            result.append(res_item)

        return result, count
