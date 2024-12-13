from pydantic import BaseModel, model_validator
from domain.model import category_model
from typing import Optional, Literal
from fastapi import UploadFile, Form
from dataclasses import dataclass


class GetCategoryListReq(BaseModel):
    query: Optional[str] = None
    query_by: Optional[Literal[category_model.QUERIABLE_FIELDS_ENUMS]] = None
    sort_by: Literal[category_model.SORTABLE_FIELDS_ENUMS] = (
        category_model.SORTABLE_FIELDS_ENUMS_DEF
    )
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10


class GetCategoryListRespDataItem(category_model.CategoryModel):
    pass

@dataclass
class CreateCategoryReq():
    name: str = Form()
    description: Optional[str] = Form(None)
    img: Optional[UploadFile] = UploadFile(...)


class CreateCategoryRespData(category_model.CategoryModel):
    pass

@dataclass
class PatchCategoryReq:
    name: Optional[str] = Form(None)
    description: Optional[str] = Form(None, description="use string 'null' to set it to null")
    img: Optional[UploadFile] = None


class PatchCategoryRespData(category_model.CategoryModel):
    pass
