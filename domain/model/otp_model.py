from .base_model import MyBaseModel

class OtpModel(MyBaseModel):
    _coll_name = "otps"

    id: str = ""
    created_at: int = 0
    updated_at: int = 0
    created_by: str = ""

    verified: bool = False
    code: str = ""