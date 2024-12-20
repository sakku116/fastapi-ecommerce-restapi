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
            wallet_rest.TopUpWalletRequest
        )
    },
)
def topup_wallet(
    payload=formOrJsonDependGenerator(wallet_rest.TopUpWalletRequest),
    wallet_service: wallet_service.WalletService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = wallet_service.topUpWallet(user=current_user, payload=payload)
    resp = generic_resp.RespData[wallet_rest.TopUpWalletRespData](data=data)
    resp.meta.message = "Wallet topped up successfully"
    return resp


@WalletRouter.get(
    "",
    response_model=generic_resp.RespData[wallet_rest.GetWalletRespData],
)
def get_current_user_wallet(
    wallet_service: wallet_service.WalletService = Depends(),
    current_user: auth_dto.CurrentUser = Depends(verifyToken),
):
    data = wallet_service.getWallet(user=current_user)
    return generic_resp.RespData[wallet_rest.GetWalletRespData](data=data)
