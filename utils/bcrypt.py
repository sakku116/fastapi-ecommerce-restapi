import bcrypt

def hashPassword(input: str) -> str:
    return bcrypt.hashpw(input.encode(), bcrypt.gensalt()).decode("utf-8")

def checkPassword(input_pw, hashed_pw):
    return bcrypt.checkpw(input_pw.encode(), hashed_pw.encode())