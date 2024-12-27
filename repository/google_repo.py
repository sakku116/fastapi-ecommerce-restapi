from config.setting import Setting
from config.env import Env
import requests
from requests.exceptions import HTTPError, JSONDecodeError
from core.logging import logger


class GoogleRepo:
    def __init__(self):
        pass

    def reqExchangeOAuth2Token(self, payload):
        url = f"{Setting.OAUTH2_GOOGLE.token_url}"

        resp_json = None
        try:
            resp = requests.post(url=url, data=payload)
            resp.raise_for_status()
            return resp.json()
        except HTTPError as http_err:
            logger.error(f"HTTP error occurred: {http_err}")
            raise http_err
        except JSONDecodeError as json_err:
            logger.error(f"JSON decode error: {json_err}")
            raise json_err
        except Exception as err:
            logger.error(f"Other error occurred: {err}")

        # map resp data

        return resp_json