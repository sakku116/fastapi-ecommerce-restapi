from pydantic import BaseModel
from datetime import datetime

class CurrentUser(BaseModel):
    id: str
    role: str = ""
    fullname: str = ""
    username: str = ""
    email: str = ""
    phone_number: str = ""
    gender: str = ""
    birth_date: str = "" # DD-MM-YYYY

class JwtPayload(CurrentUser):
    sub: str
    exp: datetime
