from domain.dto import auth_dto
from pydantic import BaseModel
from domain.model import user_model
from fastapi import Form
from typing import Optional
from dataclasses import dataclass


class GetMeRespData(auth_dto.CurrentUser):
    pass


@dataclass
class UpdateMyProfileReq:
    fullname: Optional[str] = Form(None)
    username: Optional[str] = Form(None)
    email: Optional[str] = Form(None)
    phone_number: Optional[str] = Form(None)
    gender: Optional[str] = Form(None)
    birth_date: Optional[str] = Form(None, description="format: DD-MM-YYYY")
    profile_picture: Optional[str] = Form(None)
    password: Optional[str] = Form(None)
    confirm_password: Optional[str] = Form(None, description="Required if password is filled up")

class UpdateMyProfileRespData(user_model.PublicUserModel):
    pass