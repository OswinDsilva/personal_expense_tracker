from ..models import Transaction


def is_credit(t: Transaction) -> bool:
    if t.transaction_type in ["INCOME", "ADJUSTMENT_CREDIT"]:
        return True
    if t.transaction_type == "TRANSFER" and t.is_debit is False:
        return True
    return False


def is_debit(t: Transaction) -> bool:
    if t.transaction_type in ["EXPENSE", "ADJUSTMENT_DEBIT"]:
        return True
    if t.transaction_type == "TRANSFER" and t.is_debit is True:
        return True
    return False
