import logging

from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from service import auth_service
from fastapi import Request
from config.env import Env
from utils import helper
import json
from typing import Optional
from core.logging import logger
from domain.dto import auth_dto
from core.exceptions.http import CustomHttpException

reusable_token = OAuth2PasswordBearer("/auth/login")


async def verifyToken(
    auth_service: auth_service.AuthService = Depends(),
    token: str = Depends(reusable_token),
) -> auth_dto.CurrentUser:
    current_user = auth_service.verifyToken(token=token)
    return current_user


async def adminOnly(
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
) -> auth_dto.CurrentUser:
    if current_user.role != "admin":
        exc = CustomHttpException(status_code=401, message="Unauthorized")
        logger.error(exc)
        raise exc

    return current_user
