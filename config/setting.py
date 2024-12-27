from dataclasses import dataclass
from pydantic import BaseModel

class OAuth2GenericConfig(BaseModel):
    auth_url: str
    token_url: str
    user_info_url: str
    callback_url_relative: str
    response_type: str
    scope: str


@dataclass(frozen=True)
class Setting:
    OAUTH2_GOOGLE = OAuth2GenericConfig(
        auth_url="https://accounts.google.com/o/oauth2/auth",
        token_url="https://oauth2.googleapis.com/token",
        user_info_url="https://www.googleapis.com/oauth2/v3/userinfo",
        callback_url_relative="auth/oauth2/google/callback",
        response_type="code",
        scope="openid profile email",
    )