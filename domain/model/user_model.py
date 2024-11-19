from .base_model import MyBaseModel, _MyBaseModel_Index, MinioUtil
from pydantic import field_validator, ValidationError
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel
from utils import helper

USER_GENDER_ENUMS = Literal["male", "female"]
USER_GENDER_ENUMS_DEFAULT = "male"
USER_ROLE_ENUMS = Literal["seller", "customer", "admin"]
USER_ROLE_ENUMS_DEFAULT = "customer"

class PublicUserModel(MinioUtil):
    _bucket_name = "users"
    _minio_fields = ["profile_picture"]

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""
    updated_by: str = ""

    id: str
    role: Literal[USER_ROLE_ENUMS] = USER_GENDER_ENUMS_DEFAULT
    fullname: str = ""
    username: str = ""
    email: str = ""
    email_verified: bool = False
    phone_number: Optional[str] = None
    gender: Literal[USER_GENDER_ENUMS] = "male"
    birth_date: Optional[str] = None # DD-MM-YYYY
    profile_picture: Optional[str] = None # filename
    language: str = "en"
    currency: str = "USD"

    last_active: int = 0

    @field_validator("username", mode="before")
    def username_validator(cls, v):
        if " " in v:
            raise ValueError("username must not contain spaces")

        return v

    @field_validator("birth_date", mode="before")
    def birth_date_validator(cls, v):
        if not v:
            return v

        try:
            datetime.strptime(v, "%d-%m-%Y")
            return v
        except Exception as e:
            raise ValueError("birth_date is not valid")

    @field_validator("email", mode="before")
    def email_validator(cls, v):
        if "@" not in v or " " in v:
            raise ValueError("email is not valid")

        return v

    @field_validator("language", mode="before")
    def language_validator(cls, v):
        if not v:
            return "en"
        else:
            valid = helper.isLanguageCodeValid(v)
            if not valid:
                raise ValueError("language is not valid")

        return v

    @field_validator("currency", mode="before")
    def currency_validator(cls, v):
        if not v:
            return "USD"
        else:
            valid = helper.isCurrencyCodeValid(v)
            if not valid:
                raise ValueError("currency is not valid")

        return v

class UserModel(MyBaseModel, PublicUserModel):
    _coll_name = "users"
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("username", -1)], unique=True),
        _MyBaseModel_Index(keys=[("email", -1)], unique=True),
    ]
    _custom_int64_fields = ["last_active"]

    password: str = ""