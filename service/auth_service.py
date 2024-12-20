from dataclasses import asdict

import jwt
from fastapi import BackgroundTasks, Depends
from pydantic import ValidationError

from config.env import Env
from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.dto import auth_dto
from domain.model import cart_model, otp_model, user_model, wallet_model
from domain.rest import auth_rest
from repository import cart_repo, otp_repo, refresh_token_repo, user_repo, wallet_repo
from utils import bcrypt as bcrypt_utils
from utils import helper
from utils import jwt as jwt_utils
from utils.service import auth_util, email_util


class AuthService:
    def __init__(
        self,
        user_repo: user_repo.UserRepo = Depends(),
        refresh_token_repo: refresh_token_repo.RefreshTokenRepo = Depends(),
        email_util: email_util.EmailUtil = Depends(),
        otp_repo: otp_repo.OtpRepo = Depends(),
        auth_util: auth_util.AuthUtil = Depends(),
        cart_repo: cart_repo.CartRepo = Depends(),
        wallet_repo: wallet_repo.WalletRepo = Depends(),
    ):
        self.user_repo = user_repo
        self.refresh_token_repo = refresh_token_repo
        self.email_util = email_util
        self.auth_util = auth_util
        self.otp_repo = otp_repo
        self.cart_repo = cart_repo
        self.wallet_repo = wallet_repo

    def login(self, payload: auth_rest.LoginReq) -> auth_rest.LoginResp:
        # check if input is email
        is_email = "@" in payload.username

        # check user if exist by email or username
        if is_email:
            user = self.user_repo.getByEmail(email=payload.username)
        else:
            user = self.user_repo.getByUsername(username=payload.username)

        if not user:
            exc = CustomHttpException(status_code=401, message="User not found")
            logger.error(exc)
            raise exc

        # check password
        is_pwd_match = bcrypt_utils.checkPassword(
            input_pw=payload.password, hashed_pw=user.password
        )
        if not is_pwd_match:
            exc = CustomHttpException(status_code=401, message="Invalid password")
            logger.error(exc)
            raise exc

        # generate access token and refresh token
        access_token, refresh_token = self.auth_util.generateAccessTokenAndRefreshToken(
            user=user
        )

        return auth_rest.LoginResp(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def refreshToken(
        self, payload: auth_rest.RefreshTokenReq
    ) -> auth_rest.RefreshTokenResp:
        # find refresh token
        refresh_token = self.refresh_token_repo.getById(id=payload.refresh_token)
        if not refresh_token:
            exc = CustomHttpException(
                status_code=401, message="Refresh token not found"
            )
            logger.error(exc)
            raise exc

        # check if expired
        if refresh_token.expired_at < helper.timeNow():
            exc = CustomHttpException(status_code=401, message="Refresh token expired")
            logger.error(exc)

        # get user
        user = self.user_repo.getById(id=refresh_token.created_by)
        if not user:
            exc = CustomHttpException(status_code=401, message="User not found")
            logger.error(exc)
            raise exc

        # login
        login_res = self.login(
            payload=auth_rest.LoginReq(
                username=user.username, password=payload.refresh_token
            )
        )

        # generate access token and refresh token
        access_token, refresh_token = self.auth_util.generateAccessTokenAndRefreshToken(
            user=user
        )

        return auth_rest.RefreshTokenResp(
            access_token=access_token,
            refresh_token=refresh_token,
        )

    def verifyToken(self, token: str) -> auth_dto.CurrentUser:
        # decode token
        claims = None
        try:
            claims = auth_dto.JwtPayload(
                **jwt_utils.decodeToken(token, Env.JWT_SECRET_KEY)
            )
        except jwt.ExpiredSignatureError as e:
            exc = CustomHttpException(
                status_code=401, message="Token expired", detail=str(e)
            )
            logger.error(exc)
            raise exc
        except jwt.InvalidTokenError as e:
            exc = CustomHttpException(
                status_code=401, message="Invalid token", detail=str(e)
            )
            logger.error(exc)
            raise exc
        except Exception as e:
            exc = CustomHttpException(
                status_code=401, message="Invalid token", detail=str(e)
            )
            logger.error(exc)
            raise exc

        # update last_active
        time_now = helper.timeNow()
        user = self.user_repo.updateLastActive(id=claims.sub, last_active=time_now)
        if not user:
            exc = CustomHttpException(status_code=401, message="User not found")
            logger.error(exc)
            raise exc

        result = auth_dto.CurrentUser(**user.model_dump())

        return result

    def checkToken(
        self, payload: auth_rest.CheckTokenReq
    ) -> auth_rest.CheckTokenRespData:
        data = self.verifyToken(token=payload.access_token.removeprefix("Bearer "))
        return auth_rest.CheckTokenRespData(**data.model_dump())

    def register(
        self, payload: auth_rest.RegisterReq, bt: BackgroundTasks
    ) -> auth_rest.RegisterResp:
        # validate password
        if len(payload.password) < 6:
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

        # validate password confirmation
        if payload.password != payload.confirm_password:
            exc = CustomHttpException(
                status_code=400, message="Password does not match"
            )
            logger.error(exc)
            raise exc

        # check if email already exist
        if self.user_repo.getByEmail(email=payload.email):
            exc = CustomHttpException(status_code=400, message="Email already exist")
            logger.error(exc)
            raise exc

        # check if username already exist
        if self.user_repo.getByUsername(username=payload.username):
            exc = CustomHttpException(status_code=400, message="Username already exist")
            logger.error(exc)
            raise exc

        # hash password
        hashed_pw = bcrypt_utils.hashPassword(payload.password)

        # create user
        time_now = helper.timeNow()
        try:
            new_user = user_model.UserModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                fullname=payload.fullname,
                username=payload.username,
                email=payload.email,
                password=hashed_pw,
                role="customer",
            )
        except ValidationError as e:
            for error in e.errors():
                exc = CustomHttpException(
                    status_code=400,
                    message=error.get("msg") or "Invalid value",
                    detail=e.json(),
                )
                logger.error(exc)
                raise exc

        self.user_repo.create(data=new_user)

        # create necessary user data in the backgrounds
        def initUserData(user_id: str):
            time_now = helper.timeNow()

            # cart
            logger.debug(f"creating wallet for user {user_id}")
            cart = cart_model.CartModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                user_id=user_id,
            )
            try:
                self.cart_repo.create(cart=cart)
            except Exception as e:
                logger.error(f"error creating cart for user {user_id}: {e}")

            # wallet
            logger.debug(f"creating wallet for user {user_id}")
            wallet = wallet_model.WalletModel(
                id=helper.generateUUID4(),
                created_at=time_now,
                updated_at=time_now,
                user_id=user_id,
                balance=0,
            )

            try:
                self.wallet_repo.create(wallet=wallet)
            except Exception as e:
                logger.error(f"error creating wallet for user {user_id}: {e}")

        bt.add_task(initUserData, user_id=new_user.id)

        # generate access token and refresh token
        access_token, refresh_token = self.auth_util.generateAccessTokenAndRefreshToken(
            user=new_user
        )

        result = auth_rest.RegisterResp(
            access_token=access_token,
            refresh_token=refresh_token,
        )
        return result

    async def sendVerifyEmailOTP(self, user_id):
        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(status_code=400, message="User not found")
            logger.error(exc)
            raise exc

        # check if email already verified
        if user.email_verified:
            exc = CustomHttpException(status_code=400, message="Email already verified")
            logger.error(exc)
            raise exc

        # check if any active otp exist
        otp = self.otp_repo.getUnverifiedByCreatedBy(created_by=user.id)
        if otp:
            # delete
            self.otp_repo.delete(id=otp.id)

        # create new otp
        time_now = helper.timeNow()
        new_otp = otp_model.OtpModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            updated_at=time_now,
            created_by=user.id,
            code=helper.generateRandomNumber(length=6),
        )

        self.otp_repo.create(data=new_otp)

        # check current user's email
        if not user.email:
            exc = CustomHttpException(
                status_code=400,
                message="User email not configured, please update your profile",
            )
            logger.error(exc)
            raise exc

        # send email
        try:
            await self.email_util.send_email(
                subject="Quickmart Email Verification",
                body=f"Your OTP is {new_otp.code}",
                recipient=user.email,
            )
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="Failed to send email", detail=str(e)
            )
            logger.error(exc)
            raise exc

    def verifyEmailOTP(self, user_id: str, payload: auth_rest.VerifyEmailOTPReq):
        _params = {
            "user_id": user_id,
            "payload": asdict(payload),
        }

        user = self.user_repo.getById(id=user_id)
        if not user:
            exc = CustomHttpException(
                status_code=400, message="User not found", context=_params
            )
            logger.error(exc)
            raise exc

        otp = self.otp_repo.getLatestByCreatedBy(created_by=user.id)
        if not otp:
            exc = CustomHttpException(
                status_code=400, message="OTP not found", context=_params
            )
            logger.error(exc)
            raise exc

        if helper.isExpired(otp.created_at, expr_seconds=Env.OTP_EXPIRES_SECONDS):
            exc = CustomHttpException(
                status_code=400, message="OTP expired", context=_params
            )
            logger.error(exc)
            raise exc

        if payload.otp_code != otp.code:
            exc = CustomHttpException(
                status_code=400, message="Invalid OTP", context=_params
            )
            logger.error(exc)
            raise exc

        # delete otp
        self.otp_repo.delete(id=otp.id)

        # update user's email verified
        user = self.user_repo.getById(id=user.id)
        if not user:
            exc = CustomHttpException(
                status_code=404, message="User not found", context=_params
            )
            logger.error(exc)
            raise exc

        user.email_verified = True
        user.updated_at = helper.timeNow()
        self.user_repo.update(id=user.id, data=user)

    async def sendEmailForgotPasswordOTP(
        self, payload: auth_rest.SendEmailForgotPasswordOTPReq
    ):
        # check if email is registered
        user = self.user_repo.getByEmail(email=payload.email)
        if not user:
            exc = CustomHttpException(status_code=400, message="Email not registered")
            logger.error(exc)
            raise exc

        # check if any unverified otp exist
        otp = self.otp_repo.getUnverifiedByCreatedBy(created_by=user.id)
        if otp:
            # delete
            self.otp_repo.delete(id=otp.id)

        # create new otp
        time_now = helper.timeNow()
        new_otp = otp_model.OtpModel(
            id=helper.generateUUID4(),
            created_at=time_now,
            updated_at=time_now,
            created_by=user.id,
            code=helper.generateRandomNumber(length=6),
        )

        self.otp_repo.create(data=new_otp)

        # send email
        try:
            await self.email_util.send_email(
                subject="Quickmart New Password Verification",
                body=f"Your OTP is {new_otp.code}",
                recipient=payload.email,
            )
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="Failed to send email", detail=str(e)
            )
            logger.error(exc)
            raise exc

    def verifyForgotPasswordOTP(
        self, payload: auth_rest.VerifyForgotPasswordOTPReq
    ) -> auth_rest.VerifyForgotPasswordOTPRespData:
        _params = {**asdict(payload)}
        # get users by email
        user = self.user_repo.getByEmail(email=payload.email)
        if not user:
            exc = CustomHttpException(status_code=400, message="Email not found")
            logger.error(exc)
            raise exc

        # get latest by created by
        otp = self.otp_repo.getLatestByCreatedBy(created_by=user.id)
        if not otp:
            exc = CustomHttpException(
                status_code=400, message="OTP not found", context=_params
            )
            logger.error(exc)
            raise exc

        # check if otp is expired
        if helper.isExpired(otp.created_at, expr_seconds=Env.OTP_EXPIRES_SECONDS):
            exc = CustomHttpException(
                status_code=400, message="OTP expired", context=_params
            )
            logger.error(exc)
            raise exc

        # check if otp is valid
        if payload.otp_code != otp.code:
            exc = CustomHttpException(
                status_code=400, message="Invalid OTP", context=_params
            )
            logger.error(exc)
            raise exc

        # mark as verified
        otp.verified = True
        otp.updated_at = helper.timeNow()
        self.otp_repo.update(id=otp.id, data=otp)

        return auth_rest.VerifyForgotPasswordOTPRespData(otp_id=otp.id)

    def changeForgottenPassword(self, payload: auth_rest.ChangeForgottenPasswordReq):
        otp = self.otp_repo.getById(id=payload.otp_id)
        if not otp:
            exc = CustomHttpException(status_code=400, message="OTP not found")
            logger.error(exc)
            raise exc

        # check if otp is expired
        if helper.isExpired(otp.created_at, expr_seconds=Env.OTP_EXPIRES_SECONDS):
            exc = CustomHttpException(status_code=400, message="OTP expired")
            logger.error(exc)
            raise exc

        # check if otp is verified
        if not otp.verified:
            exc = CustomHttpException(
                status_code=400, message="OTP not verified, verify first"
            )
            logger.error(exc)

        user = self.user_repo.getById(id=otp.created_by)
        if not user:
            exc = CustomHttpException(status_code=400, message="User not found")
            logger.error(exc)
            raise exc

        # validate password
        if len(payload.new_password) < 6:
            exc = CustomHttpException(
                status_code=400, message="Password must be at least 6 characters long"
            )
            logger.error(exc)
            raise exc

        if " " in payload.new_password:
            exc = CustomHttpException(
                status_code=400, message="Password must not contain spaces"
            )
            logger.error(exc)
            raise exc

        if payload.new_password != payload.confirm_password:
            exc = CustomHttpException(
                status_code=400, message="Password confirmation does not match"
            )
            logger.error(exc)
            raise exc

        # update password
        user.password = bcrypt_utils.hashPassword(payload.new_password)
        user.updated_by = user.id
        user.updated_at = helper.timeNow()
        user = self.user_repo.update(id=user.id, data=user)
        if not user:
            exc = CustomHttpException(
                status_code=500, message="Failed to update password, user not found"
            )
            logger.error(exc)
            raise exc
