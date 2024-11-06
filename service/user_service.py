from fastapi import Depends
from domain.model import user_model
from repository import user_repo
from domain.dto import auth_dto
from core.logging import logger
from domain.rest import user_rest
from core.exceptions.http import CustomHttpException
from utils import bcrypt as bcrypt_utils
from pydantic import ValidationError
from datetime import datetime


class UserService:
    def __init__(self, user_repo: user_repo.UserRepo = Depends()) -> None:
        self.user_repo = user_repo

    def getMe(self, current_user: auth_dto.CurrentUser) -> user_rest.GetMeRespData:
        return user_rest.GetMeRespData(**current_user.model_dump())

    def updateMyProfile(self, current_user: auth_dto.CurrentUser, payload: user_rest.UpdateMyProfileReq) -> user_rest.UpdateMyProfileRespData:
        user = self.user_repo.getById(id=current_user.id)
        if not user:
            exc = CustomHttpException(
                status_code=404, message="User not found"
            )
            logger.error(exc)
            raise exc

        # validate username
        if payload.username != None:
            _user = self.user_repo.getByUsername(username=payload.username)
            if _user and _user.id != user.id:
                exc = CustomHttpException(
                    status_code=400, message="Username is already taken"
                )
                logger.error(exc)
                raise exc

            if " " in payload.username:
                exc = CustomHttpException(
                    status_code=400, message="Username must not contain spaces"
                )
                logger.error(exc)
                raise exc

        # validate email
        if payload.email != None:
            _user = self.user_repo.getByEmail(email=payload.email)
            if _user and _user.id != user.id:
                exc = CustomHttpException(
                    status_code=400, message="Email is already taken"
                )
                logger.error(exc)
                raise exc

            if "@" not in payload.email:
                exc = CustomHttpException(
                    status_code=400, message="Invalid email address"
                )
                logger.error(exc)
                raise exc

        # validate password
        if payload.password != None:
            if payload.confirm_password == None:
                exc = CustomHttpException(
                    status_code=400, message="Confirm password is required when changing password"
                )
                logger.error(exc)
                raise exc

            if payload.confirm_password != payload.password:
                exc = CustomHttpException(
                    status_code=400, message="Password and confirm password does not match"
                )
                logger.error(exc)
                raise exc

            if len(payload.password) < 7:
                exc = CustomHttpException(
                    status_code=400, message="Password must be at least 7 characters long"
                )
                logger.error(exc)
                raise exc

            if " " in payload.password:
                exc = CustomHttpException(
                    status_code=400, message="Password must not contain spaces"
                )
                logger.error(exc)
                raise exc

        # validate birth_date
        if payload.birth_date != None:
            try:
                datetime.strptime(payload.birth_date, "%d-%m-%Y")
            except Exception as e:
                exc = CustomHttpException(
                    status_code=400, message="Invalid birth date, format should be DD-MM-YYYY"
                )
                logger.error(exc)
                raise exc

        # update fields
        if payload.fullname != None:
            user.fullname = payload.fullname

        if payload.username != None:
            user.username = payload.username

        if payload.email != None:
            user.email = payload.email

        if payload.phone_number != None:
            user.phone_number = payload.phone_number

        if payload.gender != None:
            user.gender = payload.gender

        if payload.birth_date != None:
            user.birth_date = payload.birth_date

        if payload.profile_picture != None:
            user.profile_picture = payload.profile_picture

        if payload.password != None:
            user.password = bcrypt_utils.hashPassword(payload.password)

        # re-validate user
        user.model_validate() # dont need to raise exception because ValidationError automatically handled by exceptions handler

        # update user
        self.user_repo.update(id=user.id, data=user)

        return user_rest.UpdateMyProfileRespData(**user.model_dump())

