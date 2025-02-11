from enum import Enum

class OAuth2Provider(str, Enum):
    GOOGLE = "google"

class OAuth2ClientType(str, Enum):
    WEB = "web"
    ANDROID = "android"
    IOS = "ios"