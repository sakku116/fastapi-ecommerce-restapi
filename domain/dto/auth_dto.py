from pydantic import BaseModel
from datetime import datetime
from domain.model import user_model

class CurrentUser(user_model.PublicUserModel):
    pass

class JwtPayload(CurrentUser):
    sub: str
    exp: datetime
