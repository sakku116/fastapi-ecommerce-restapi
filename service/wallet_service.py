from typing import Union

from fastapi import Depends

from core.exceptions.http import CustomHttpException
from core.logging import logger
from domain.model import user_model, wallet_model
from domain.rest import wallet_rest
from repository import user_repo, wallet_repo
from utils import helper


class WalletService:
    def __init__(
        self,
        wallet_repo: wallet_repo.WalletRepo = Depends(),
        user_repo: user_repo.UserRepo = Depends(),
    ):
        self.wallet_repo = wallet_repo
        self.user_repo = user_repo

    def topUpWallet(
        self,
        user: Union[user_model.UserModel, str],
        payload: wallet_rest.TopUpWalletRequest,
    ) -> wallet_rest.TopUpWalletRespData:
        # ensure user
        if isinstance(user, str):
            user = self.user_repo.getById(id=user)
            if not user:
                exc = CustomHttpException(
                    status_code=500,
                    message="internal service error",
                    detail="user not found",
                )
                logger.error(exc)
                raise exc

        # get wallet
        logger.debug(f"getting wallet of user {user.id}")
        wallet = self.wallet_repo.getByUserId(user_id=user.id)
        if not wallet:
            exc = CustomHttpException(status_code=404, message="wallet not found")
            logger.debug(f"failed to get wallet of user {user.id}: {exc}")
            raise exc

        """
        add topup method handling here if any
        """

        # add wallet balance
        wallet.balance += payload.amount
        wallet.updated_at = helper.timeNow()
        try:
            logger.debug(f"updating wallet of user {user.id}")
            self.wallet_repo.update(id=wallet.id, data=wallet)
        except Exception as e:
            exc = CustomHttpException(
                status_code=500, message="failed to update wallet", detail=str(e)
            )
            logger.debug(f"failed to update wallet of user {user.id}: {exc}")
            raise exc

        # resp data
        localized_balance = helper.localizePrice(
            price=wallet.balance,
            currency_code=user.currency,
            language_code=user.language,
        )
        resp_data = wallet_rest.TopUpWalletRespData(
            **wallet.model_dump(), localized_balance=localized_balance
        )

        return resp_data

    def getWallet(
        self, user: Union[user_model.UserModel, str]
    ) -> wallet_rest.GetWalletRespData:
        # ensure user
        if isinstance(user, str):
            user = self.user_repo.getById(id=user)
            if not user:
                exc = CustomHttpException(
                    status_code=500,
                    message="internal service error",
                    detail="user not found",
                )
                logger.error(exc)
                raise exc

        wallet = self.wallet_repo.getByUserId(user_id=user.id)
        if not wallet:
            # create new wallet
            wallet = wallet_model.WalletModel(
                id=helper.generateUUID4(),
                created_at=helper.timeNow(),
                updated_at=helper.timeNow(),
                user_id=user.id,
            )

            try:
                self.wallet_repo.create(wallet)
            except Exception as e:
                exc = CustomHttpException(
                    status_code=500, message="failed to create wallet", detail=str(e)
                )
                logger.debug(f"failed to create wallet of user {user.id}: {exc}")
                raise exc

        # resp data
        localized_balance = helper.localizePrice(
            price=wallet.balance,
            currency_code=user.currency,
            language_code=user.language,
        )
        resp_data = wallet_rest.GetWalletRespData(
            **wallet.model_dump(), localized_balance=localized_balance
        )
        return resp_data
