from .base_model import MyBaseModel

class RefreshTokenModel(MyBaseModel):
    _coll_name = "refresh_tokens"
    _custom_int64_fields = ["expired_at"]

    # use id for the token
    expired_at: int = 0