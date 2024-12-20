from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.rest import wallet_rest
from repository import wallet_repo
from utils import helper


class WalletService:
    def __init__(
        self,
        wallet_repo: wallet_repo.WalletRepo = Depends(),
    ):
        self.wallet_repo = wallet_repo

    def topUpWallet(
        self, user_id: str, payload: wallet_rest.TopUpWalletReq
    ) -> wallet_rest.TopUpWalletRespData:
        # get wallet
        wallet = self.wallet_repo.getByUserId(user_id=user_id)
        if not wallet:
            exc = CustomHttpException(status_code=404, message="wallet not found")
            logger.debug(f"failed to get wallet of user {user_id}: {exc}")
            raise exc

        """
        add topup method handling here if any
        """

        # add wallet balance
        wallet.balance += payload.amount
        wallet.updated_at = helper.timeNow()
        try:
            self.wallet_repo.update(wallet, wallet)
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="failed to update wallet", detail=str(e)
            )
            logger.debug(f"failed to update wallet of user {user_id}: {exc}")
            raise exc

        # resp data
        resp_data = wallet_rest.TopUpWalletRespData(**wallet.model_dump())

        return resp_data

    def getWallet(self, user_id: str) -> wallet_rest.GetWalletRespData:
        wallet = self.wallet_repo.getByUserId(user_id=user_id)
        if not wallet:
            exc = CustomHttpException(status_code=404, message="wallet not found")
            logger.debug(f"failed to get wallet of user {user_id}: {exc}")
            raise exc

        # resp data
        resp_data = wallet_rest.GetWalletRespData(**wallet.model_dump())
        return resp_data
