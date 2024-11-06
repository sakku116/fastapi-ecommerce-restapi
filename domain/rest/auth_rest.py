from pydantic import BaseModel, field_validator
from .generic_resp import RespData
from domain.dto import auth_dto
from dataclasses import dataclass
from fastapi import Form

@dataclass
class LoginReq:
    email_or_username: str = Form()
    password: str = Form()


class LoginResp(RespData):
    access_token: str
    refresh_token: str

@dataclass
class RefreshTokenReq:
    refresh_token: str = Form()

class RefreshTokenResp(RespData):
    access_token: str
    refresh_token: str

@dataclass
class RegisterReq:
    fullname: str = Form()
    username: str = Form()
    email: str = Form()
    password: str = Form()
    confirm_password: str = Form()

class RegisterResp(RespData):
    access_token: str
    refresh_token: str

@dataclass
class CheckTokenReq:
    access_token: str = Form()

class CheckTokenRespData(auth_dto.CurrentUser):
    pass