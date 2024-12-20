from enum import Enum

class TransactionType(str, Enum):
    CREDIT = "credit"
    DEBIT = "debit"

class TransactionReferenceType(str, Enum):
    ORDER = "order"
    TOP_UP = "top_up"
    TRANSFER = "transfer"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"