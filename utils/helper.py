import time
import json
from uuid import uuid4


def parseBool(source: any) -> bool:
    if str(source).strip().lower() in ["none", 0, "", "false"]:
        return False
    return True


def generateSkip(page: int, limit: int) -> int:
    return (page - 1) * limit


def timeNowEpoch() -> int:
    return int(time.time())


def prettyJson(data: any) -> str:
    return json.dumps(data, indent=4)


def limitString(input: str, limit: int = 200) -> str:
    if len(input) > limit:
        return f"{input[:limit]}... ({len(input) - limit} chars left)"
    return input


def generateUUID4() -> str:
    return str(uuid4())