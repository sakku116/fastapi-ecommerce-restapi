from domain.model import base_model
from datetime import datetime
from domain.enum import wallet_enum
from typing import Optional

class WalletModel(base_model.MyBaseModel):
    """
    one user can have only one wallet
    """
    _coll_name = "wallets"

    id: str
    created_at: datetime
    updated_at: datetime

    user_id: str
    balance: float = 0
    currency: str = "USD"

class WalletTransactionModel(base_model.MyBaseModel):
    _coll_name = "wallet_transactions"

    id: str
    created_at: datetime
    updated_at: datetime

    wallet_id: str
    user_id: str

    current_balance: float
    amount: float
    balance_after: float
    type: wallet_enum.TransactionType
    reference_id: str
    reference_type: wallet_enum.TransactionReferenceType
    description: Optional[str] = None