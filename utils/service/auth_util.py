from datetime import timedelta
from typing import Union

from fastapi import Depends

from config.env import Env
from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto
from domain.model import refresh_token_model, user_model
from repository import refresh_token_repo
from utils import helper
from utils import jwt as jwt_utils


class AuthUtil:
    def __init__(
        self,
        refresh_token_repo: refresh_token_repo.RefreshTokenRepo = Depends()
    ):
        self.refresh_token_repo = refresh_token_repo

    def generateAccessTokenAndRefreshToken(
        self,
        user: Union[user_model.UserModel, str]
    ) -> tuple[str, str]:
        # prepare user
        if isinstance(user, str):
            user = self.refresh_token_repo.getById(id=user)
            if not user:
                exc = CustomHttpException(status_code=401, message="User not found")
                logger.error(exc)
                raise exc

        # generate jwt token
        jwt_payload = auth_dto.JwtPayload(
            **user.model_dump(),
            sub=user.id,
            exp=int(
                (
                    helper.timeNow() + timedelta(hours=Env.TOKEN_EXPIRES_HOURS)
                ).timestamp()
            ),
        )
        jwt_token = jwt_utils.encodeToken(
            payload=jwt_payload.model_dump(mode="json"), secret=Env.JWT_SECRET_KEY
        )

        # remove previous refresh token
        prev_refresh_token = self.refresh_token_repo.getLastByCreatedBy(
            created_by=user.id
        )
        if prev_refresh_token:
            self.refresh_token_repo.delete(id=prev_refresh_token.id)

        # generate refresh token
        time_now = helper.timeNow()
        new_refresh_token = refresh_token_model.RefreshTokenModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            created_by=user.id,
            expired_at=int(
                (
                    helper.timeNow() + timedelta(hours=Env.REFRESH_TOKEN_EXPIRES_HOURS)
                ).timestamp()
            ),
        )
        self.refresh_token_repo.create(data=new_refresh_token)

        return jwt_token, new_refresh_token.id