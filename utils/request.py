from typing import Literal, Type, TypeVar

from pydantic import BaseModel

_TModel = TypeVar("_TModel", bound=BaseModel)


def generateFormOrJsonOpenapiBody(
    model: Type[_TModel], required: bool = True, first: Literal["form", "json"] = "form"
) -> dict:
    if first == "json":
        contents = {
            "application/json": {"schema": model.model_json_schema()},
            "multipart/form-data": {"schema": model.model_json_schema()},
        }

    elif first == "form":
        contents = {
            "multipart/form-data": {"schema": model.model_json_schema()},
            "application/json": {"schema": model.model_json_schema()},
        }

    return {"content": contents, "required": required}
