from fastapi import APIRouter, Depends

from core.dependencies import formOrJsonDependGenerator, verifyToken
from domain.dto import auth_dto
from domain.rest import generic_resp, wallet_rest
from service import wallet_service
from utils import request as req_utils

WalletRouter = APIRouter(
    prefix="/wallet",
    tags=["Wallet"],
    dependencies=[Depends(verifyToken)],
)


@WalletRouter.post(
    "/topup",
    response_model=generic_resp.RespData[wallet_rest.TopUpWalletRespData],
    openapi_extra={
        "requestBody": req_utils.generateFormOrJsonOpenapiBody(
            wallet_rest.TopUpWalletReq
        )
    },
)
def topup_wallet(
    payload=formOrJsonDependGenerator(wallet_rest.TopUpWalletReq),
    wallet_service: wallet_service.WalletService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = wallet_service.topUpWallet(user_id=current_user, payload=payload)
    return generic_resp.RespData[wallet_rest.TopUpWalletRespData](data=data)


@WalletRouter.get(
    "",
    response_model=generic_resp.RespData[wallet_rest.GetWalletRespData],
)
def get_current_user_wallet(
    wallet_service: wallet_service.WalletService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = wallet_service.getWallet(user_id=current_user.id)
    return generic_resp.RespData[wallet_rest.GetWalletRespData](data=data)
