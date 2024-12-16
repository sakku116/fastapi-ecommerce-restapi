from pydantic import BaseModel, model_validator
from domain.model import category_model
from typing import Optional, Literal
from fastapi import UploadFile, Form
from dataclasses import dataclass


class GetCategoryListReq(BaseModel):
    query: Optional[str] = None
    query_by: Optional[Literal["name"]] = None
    sort_by: Literal["created_at", "updated_at", "name"] = "updated_at"
    sort_order: Literal["asc", "desc"] = "desc"
    page: int = 1
    limit: int = 10


class GetCategoryListRespDataItem(category_model.CategoryModel):
    pass

@dataclass
class CreateCategoryReq():
    name: str = Form()
    description: Optional[str] = Form(None)
    img: Optional[UploadFile] = None


class CreateCategoryRespData(category_model.CategoryModel):
    pass

@dataclass
class PatchCategoryReq:
    name: Optional[str] = Form(None)
    description: Optional[str] = Form(None, description="use string 'null' to set it to null")
    img: Optional[UploadFile] = None


class PatchCategoryRespData(category_model.CategoryModel):
    pass

class DeleteCategoryRespData(category_model.CategoryModel):
    pass