from pydantic import BaseModel
from typing import Optional, Literal
from domain.model import product_model, base_model
from minio import Minio
from utils import helper


class BaseProductResp(base_model.MinioUtil):
    _bucket_name = product_model.ProductModel.getBucketName()
    _minio_fields = product_model.ProductModel.getMinioFields()
    id: str = ""
    name: str = ""
    price: float = 0
    localized_price: str = ""
    img: Optional[str] = None

    def asResponse(
        self,
        minio_client: Optional[Minio] = None,
        currency_code: Optional[str] = None,
        language_code: Optional[str] = None,
    ):
        """
        - localize price in localized_price field
        - convert img to minio url instead filename
        """

        if self.price and currency_code and language_code:
            self.localized_price = helper.localizePrice(self.price, currency_code, language_code)
        if self.img:
            self.urlizeMinioFields(minio_client=minio_client)


class GetProductListReq(BaseModel):
    category_id: Optional[str] = None
    query: Optional[str] = None
    query_by: Optional[Literal[product_model.QUERIABLE_FIELDS_ENUMS]] = None
    sort_by: Literal[product_model.SORTABLE_FIELDS_ENUMS] = (
        product_model.SORTABLE_FIELDS_ENUMS_DEF
    )
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10


class GetProductListRespDataItem(BaseProductResp):
    pass


class GetProductDetailRespData(product_model.ProductModel, BaseProductResp):
    pass
