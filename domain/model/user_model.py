from .base_model import MyBaseModel, _MyBaseModel_Index, MinioUtil
from pydantic import field_validator, ValidationError, model_validator
from typing import Literal, Optional
from datetime import datetime
from pydantic import BaseModel
from utils import helper

USER_GENDER_ENUMS = Literal["male", "female"]
USER_GENDER_ENUMS_DEFAULT = "male"
USER_ROLE_ENUMS = Literal["seller", "customer", "admin"]
USER_ROLE_ENUMS_DEFAULT = "customer"

class PublicUserModel(MinioUtil):
    # WARNING: these private attr needed for response behavior usage
    _bucket_name = "users"
    _minio_fields = ["profile_picture"]

    id: str = ""
    created_at: datetime
    updated_at: datetime
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

    last_active: Optional[datetime] = None

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

    @model_validator(mode="before")
    def currency_validator(self, v):
        currency = self.get("currency")
        language = self.get("language") or "en"
        if not currency:
            self["currency"] = "USD"
        else:
            valid = helper.isCurrencyCodeValid(currency, locale=language)
            if not valid:
                raise ValueError("currency is not valid")

        return self

class UserModel(MyBaseModel, PublicUserModel):
    _bucket_name = "users"
    _minio_fields = ["profile_picture"]
    _coll_name = "users"
    _custom_indexes = [
        _MyBaseModel_Index(keys=[("username", -1)], unique=True),
        _MyBaseModel_Index(keys=[("email", -1)], unique=True),
        _MyBaseModel_Index(keys=[("created_at", -1)]),
        _MyBaseModel_Index(keys=[("updated_at", -1)]),
        _MyBaseModel_Index(keys=[("role", -1)]),
        _MyBaseModel_Index(keys=[("fullname", -1)]),
        _MyBaseModel_Index(keys=[("phone_number", -1)]),
    ]

    password: str = ""