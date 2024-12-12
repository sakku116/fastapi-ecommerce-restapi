from fastapi import Depends, File
from domain.model import user_model
from pydantic import ValidationError
from repository import user_repo, refresh_token_repo, otp_repo
import io
from domain.dto import auth_dto
from core.logging import logger
from domain.rest import user_rest
from core.exceptions.http import CustomHttpException
from utils import bcrypt as bcrypt_utils
from utils import helper
from config.minio import getMinioClient
from minio import Minio


class UserService:
    def __init__(
        self,
        user_repo: user_repo.UserRepo = Depends(),
        refresh_token_repo: refresh_token_repo.RefreshTokenRepo = Depends(),
        otp_repo: otp_repo.OtpRepo = Depends(),
        minio_client: Minio = Depends(getMinioClient),
    ) -> None:
        self.user_repo = user_repo
        self.otp_repo = otp_repo
        self.refresh_token_repo = refresh_token_repo
        self.minio_client = minio_client

    def getMe(self, current_user: auth_dto.CurrentUser) -> user_rest.GetMeRespData:
        result = user_rest.GetMeRespData(**current_user.model_dump())
        result.urlizeMinioFields(self.minio_client)
        return result

    def updateProfile(
        self, user_id: str, payload: user_rest.UpdateProfileReq
    ) -> user_rest.UpdateProfileRespData:
        logger.debug(f"payload: {payload}")
        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(status_code=404, message="User not found")
            logger.error(exc)
            raise exc

        # update fields
        if payload.fullname != None:
            user.fullname = payload.fullname

        if payload.username != None:
            user.username = payload.username

        if payload.email != None:
            # check if email already registered
            if self.user_repo.getByEmail(email=payload.email):
                exc = CustomHttpException(
                    status_code=400, message="Email already registered"
                )
                logger.error(exc)
                raise exc

            user.email = payload.email
            user.email_verified = False

        if payload.phone_number != None:
            user.phone_number = payload.phone_number

        if payload.gender != None:
            user.gender = payload.gender

        if payload.birth_date != None:
            user.birth_date = payload.birth_date

        if payload.language != None:
            user.language = payload.language

        if payload.currency != None:
            user.currency = payload.currency

        # re-validate user
        try:
            user.model_validate(user.model_dump())
        except ValidationError as e:
            logger.debug(f"validation error")
            for error in e.errors():
                exc = CustomHttpException(
                    status_code=400,
                    message=error.get("msg") or "Invalid value",
                    detail=e.json(),
                )
                logger.error(exc)
                raise exc
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="Failed to validate user"
            )
            logger.error(exc)
            raise exc

        # update user
        user.updated_at = helper.timeNow()
        user.updated_by = user_id
        user = self.user_repo.update(id=user.id, data=user)
        logger.debug(f"updated_user: {user}")
        if not user:
            exc = CustomHttpException(status_code=500, message="Failed to update user")
            logger.error(exc)
            raise exc

        user.urlizeMinioFields(self.minio_client)
        return user_rest.UpdateProfileRespData(**user.model_dump())

    def checkPassword(self, user_id: str, payload: user_rest.CheckPasswordReq) -> bool:
        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(status_code=404, message="User not found")
            logger.error(exc)
            raise exc

        is_pw_match = bcrypt_utils.checkPassword(payload.password, user.password)
        if not is_pw_match:
            exc = CustomHttpException(status_code=400, message="Invalid password")
            logger.error(exc)
            raise exc

        return True

    def updatePassword(
        self, user_id: str, payload: user_rest.UpdatePasswordReq
    ) -> user_rest.UpdatePasswordRespData:
        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(status_code=404, message="User not found")
            logger.error(exc)
            raise exc

        # validate
        if len(payload.new_password) < 7:
            exc = CustomHttpException(
                status_code=400,
                message="New password must be at least 7 characters long",
            )
            logger.error(exc)
            raise exc

        if " " in payload.new_password:
            exc = CustomHttpException(
                status_code=400, message="New password must not contain spaces"
            )
            logger.error(exc)
            raise exc

        if payload.new_password != payload.confirm_password:
            exc = CustomHttpException(
                status_code=400,
                message="New password and confirm password does not match",
            )
            logger.error(exc)
            raise exc

        # update user
        user.updated_at = helper.timeNow()
        user.updated_by = user_id
        user.password = bcrypt_utils.hashPassword(payload.new_password)
        self.user_repo.update(id=user.id, data=user)

        user.urlizeMinioFields(self.minio_client)
        return user_rest.UpdatePasswordRespData(**user.model_dump())

    def delete(self, user_id: str):
        _params = {"user_id": user_id}

        user = self.user_repo.delete(id=user_id)
        if not user:
            exc = CustomHttpException(
                status_code=404, message="User not found", context=_params
            )
            logger.error(exc)
            raise exc

        self.refresh_token_repo.deleteManyByCreatedBy(created_by=user_id)
        self.otp_repo.deleteManyByCreatedBy(created_by=user_id)

        return

    def updateProfilePict(
        self, user_id: str, payload: user_rest.UpdateProfilePictReq
    ) -> user_rest.UpdateProfilePictRespData:
        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(status_code=404, message="User not found")
            logger.error(exc)
            raise exc

        # validate image
        if not helper.isImage(payload.profile_picture.filename):
            exc = CustomHttpException(
                status_code=400,
                message="File is not an image",
            )
            logger.error(exc)
            raise exc

        # upload
        filename = f"{helper.generateUUID4()}-{payload.profile_picture.filename}"
        logger.debug(user_model.UserModel.getBucketName())
        try:
            self.minio_client.put_object(
                bucket_name=user_model.UserModel.getBucketName(),
                object_name=filename,
                data=payload.profile_picture.file,
                length=payload.profile_picture.size or 0,
                content_type=helper.getMimeType(payload.profile_picture.filename),
            )
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="Failed to store image", detail=str(e)
            )
            logger.error(exc)
            raise exc

        # update user object
        user.profile_picture = filename
        user.updated_at = helper.timeNow()
        user.updated_by = user_id
        user = self.user_repo.update(id=user.id, data=user)
        if not user:
            exc = CustomHttpException(status_code=500, message="Failed to update user")
            logger.error(exc)
            raise exc

        user.urlizeMinioFields(minio_client=self.minio_client)
        return user_rest.UpdateProfilePictRespData(**user.model_dump())