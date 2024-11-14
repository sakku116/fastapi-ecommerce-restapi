import logging

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from service import auth_service
from fastapi import Request
from config.env import Env
from utils import helper
import json
from typing import Optional, Literal
from core.logging import logger
from domain.dto import auth_dto
from core.exceptions.http import CustomHttpException
from domain.model import user_model

reusable_token = OAuth2PasswordBearer("/auth/login")


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