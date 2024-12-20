from pydantic import BaseModel
from domain.model import wallet_model

class TopUpWalletRequest(BaseModel):
    amount: float

class TopUpWalletRespData(wallet_model.WalletModel):
    localized_balance: str

class GetWalletRespData(wallet_model.WalletModel):
    localized_balance: str