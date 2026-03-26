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


def map_month(m_num: int) -> str:
    month_dict = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }

    return month_dict[m_num]