from dataclasses import dataclass

from fastapi import Form
from pydantic import BaseModel, field_validator

from domain.dto import auth_dto

from .generic_resp import RespData


class BaseTokenResp(BaseModel):
    """
    !!IMPORTANT!!
    fastapi oauth need `access_token` field in the root of the response,
    also my mobile client GUY need it inside of the `data` field.
    so this base token resp model need to be inherited to response model and passed in `data` field at the same time
    """
    access_token: str
    refresh_token: str


class LoginReq(BaseModel):
    username: str = Form()
    password: str = Form()


class LoginResp(RespData, BaseTokenResp):
    pass


class RefreshTokenReq(BaseModel):
    refresh_token: str = Form()


class RefreshTokenResp(RespData, BaseTokenResp):
    pass


class RegisterReq(BaseModel):
    fullname: str = Form()
    username: str = Form()
    email: str = Form()
    password: str = Form()
    confirm_password: str = Form()


class RegisterResp(RespData, BaseTokenResp):
    pass


class CheckTokenReq(BaseModel):
    access_token: str = Form()


class CheckTokenRespData(auth_dto.CurrentUser):
    pass

class VerifyEmailOTPReq(BaseModel):
    otp_code: str = Form()

class SendEmailForgotPasswordOTPReq(BaseModel):
    email: str = Form()

class VerifyForgotPasswordOTPReq(BaseModel):
    email: str = Form()
    otp_code: str = Form()

class VerifyForgotPasswordOTPRespData(BaseModel):
    otp_id: str = ""

class ChangeForgottenPasswordReq(BaseModel):
    otp_id: str = Form()
    new_password: str = Form()
    confirm_password: str = Form()
