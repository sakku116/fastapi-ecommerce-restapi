import jwt

def decodeToken(token: str, secret: str):
    return jwt.decode(token, secret, algorithms="HS256")

def encodeToken(payload: dict, secret: str) -> str:
    return jwt.encode(payload, secret, algorithm="HS256")
