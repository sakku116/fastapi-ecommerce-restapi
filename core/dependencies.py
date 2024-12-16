import logging
from typing import Literal, Type, TypeVar

from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto
from domain.model import user_model
from service import auth_service

reusable_token = OAuth2PasswordBearer("/auth/login")
_TModel = TypeVar("_TModel", bound=BaseModel)


async def verifyToken(
    auth_service: auth_service.AuthService = Depends(),
    token: str = Depends(reusable_token),
) -> auth_dto.CurrentUser:
    current_user = auth_service.verifyToken(token=token)
    return current_user


class RoleRequired:
    def __init__(self, role: list[Literal[user_model.USER_ROLE_ENUMS]]):
        self.role = role

    def __call__(self, current_user: auth_dto.CurrentUser = Depends(verifyToken)):
        if current_user.role not in self.role:
            exc = CustomHttpException(status_code=401, message="Unauthorized")
            logger.error(exc)
            raise exc

        return current_user


def formOrJsonDependGenerator(model: Type[_TModel]) -> _TModel:
    async def formOrJsonInner(request: Request) -> _TModel:
        type_ = request.headers["Content-Type"].split(";", 1)[0]
        if type_ == "application/json":
            data = await request.json()
        elif (
            type_ == "multipart/form-data"
            or type_ == "application/x-www-form-urlencoded"
        ):
            data = await request.form()
        else:
            raise CustomHttpException(status_code=415, message="Unsupported Media Type")
        return model.model_validate(data)

    return Depends(formOrJsonInner)
