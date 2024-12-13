from typing import TypeVar, Type, Literal
from fastapi import Request, Depends
from pydantic import BaseModel
from core.exceptions.http import CustomHttpException

_TModel = TypeVar("_TModel", bound=BaseModel)

def formOrJson(model: Type[_TModel]) -> _TModel:
    async def formOrJsonInner(request: Request) -> _TModel:
        type_ = request.headers["Content-Type"].split(";", 1)[0]
        if type_ == "application/json":
            data = await request.json()
        elif type_ == "multipart/form-data":
            data = await request.form()
        else:
            raise CustomHttpException(status_code=415, message="Unsupported Media Type")
        return model.model_validate(data)
    return Depends(formOrJsonInner)

def generateFormOrJsonOpenapiBody(
    model: Type[_TModel],
    required: bool = True,
    first: Literal["form", "json"] = "form"
) -> dict:
    if first == "json":
        contents = {
            "application/json": {
                "schema": model.model_json_schema()
            },
            "multipart/form-data": {
                "schema": model.model_json_schema()
            },
        }

    elif first == "form":
        contents = {
            "multipart/form-data": {
                "schema": model.model_json_schema()
            },
            "application/json": {
                "schema": model.model_json_schema()
            },
        }

    return {
        "content": contents,
        "required": required
    }