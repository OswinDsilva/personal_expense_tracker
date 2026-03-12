from datetime import date
from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import and_, or_, select
from sqlalchemy.orm import Session

from ..auth.jwt import get_current_user
from ..database import get_db
from ..models import Category, Transaction, User
from ..schema import (
    PaymentMethod,
    TransactionCreate,
    TransactionListResponse,
    TransactionResponse,
    TransactionType,
    TransactionUpdate,
    TransferCreate,
)

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if transaction.category_id is not None:
        cat = db.get(Category, transaction.category_id)
        if not cat:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Category does not exist"
            )

    transaction_to_add = Transaction(
        transaction_date=transaction.transaction_date,
        description=transaction.description,
        amount=transaction.amount,
        payment_method=transaction.payment_method,
        transaction_type=transaction.transaction_type,
        category_id=transaction.category_id,
    )

    db.add(transaction_to_add)
    db.commit()
    db.refresh(transaction_to_add)

    return transaction_to_add


@router.post(
    "/transfer", status_code=status.HTTP_201_CREATED, response_model=List[TransactionResponse]
)
def create_transfer_transaction(
    transaction: TransferCreate,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    source_transfer = Transaction(
        transaction_date=transaction.transaction_date,
        description=transaction.description,
        amount=transaction.amount,
        payment_method=transaction.source_method.value,
        transaction_type=TransactionType.TRANSFER.value,
        is_debit=True,
    )
    destination_transfer = Transaction(
        transaction_date=transaction.transaction_date,
        description=transaction.description,
        amount=transaction.amount,
        payment_method=transaction.destination_method.value,
        transaction_type=TransactionType.TRANSFER.value,
        is_debit=False,
    )

    db.add_all([source_transfer, destination_transfer])
    db.flush()

    source_transfer.linked_transfer_id = destination_transfer.id
    destination_transfer.linked_transfer_id = source_transfer.id
    db.commit()
    db.refresh(source_transfer)
    db.refresh(destination_transfer)

    return [source_transfer, destination_transfer]


@router.get("/", response_model=TransactionListResponse)
def get_all_transactions(
    start_date: date | None = None,
    end_date: date | None = None,
    category_id: int | None = None,
    transaction_type: str | None = None,
    payment_method: str | None = None,
    cursor: str | None = None,  # Format for the cursor is {cursor_date}_{id} , ex: 2026-02-01_123
    limit: int = Query(default=50, ge=1, le=100),
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = select(Transaction)

    if start_date is not None:
        query = query.where(Transaction.transaction_date >= start_date)

    if end_date is not None:
        query = query.where(Transaction.transaction_date <= end_date)

    if category_id is not None:
        query = query.where(Transaction.category_id == category_id)

    if transaction_type is not None:
        transaction_type_upper = transaction_type.upper()
        valid_types = [t.value for t in TransactionType]

        if transaction_type_upper not in valid_types:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Transaction type must be one of: {valid_types}",
            )

        query = query.where(Transaction.transaction_type == transaction_type_upper)

    if payment_method is not None:
        payment_method_upper = payment_method.upper()
        valid_methods = [t.value for t in PaymentMethod]

        if payment_method_upper not in valid_methods:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"Payment method must be one of: {valid_methods}",
            )

        query = query.where(Transaction.payment_method == payment_method_upper)

    if cursor:
        try:
            cursor_date_str, cursor_id_str = cursor.split("_")
            cursor_date = date.fromisoformat(cursor_date_str)
            cursor_id = int(cursor_id_str)
        except (ValueError, AttributeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Wrong cursor format, Expected: YYYY-MM-DD_ID",
            )
        query = query.where(
            or_(
                Transaction.transaction_date < cursor_date,
                and_(Transaction.transaction_date == cursor_date, Transaction.id < cursor_id),
            )
        )

    query = query.order_by(Transaction.transaction_date.desc(), Transaction.id.desc())

    query = query.limit(limit + 1)

    transactions = db.execute(query).scalars().all()

    next_cursor = None

    has_more = len(transactions) > limit

    if has_more:
        transactions = transactions[:limit]

    if has_more and transactions:
        last_transaction = transactions[-1]
        next_cursor = f"{last_transaction.transaction_date.isoformat()}_{last_transaction.id}"

    return {
        "data": transactions,
        "pagination": {"next_cursor": next_cursor, "has_more": has_more, "limit": limit},
    }


@router.get("/{id}", response_model=TransactionResponse)
def get_transaction_by_id(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    transaction = db.execute(select(Transaction).filter(Transaction.id == id)).scalars().first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    return transaction


@router.patch("/{id}", response_model=TransactionResponse)
def update_transaction_by_id(
    id: int,
    new_transaction: TransactionUpdate,
    curr_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    transaction = db.execute(select(Transaction).filter(Transaction.id == id)).scalars().first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if transaction.transaction_type == TransactionType.TRANSFER.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot alter transfer transactions"
        )

    data = new_transaction.model_dump(exclude_unset=True)

    if transaction.transaction_type == TransactionType.EXPENSE.value:
        if "category_id" in data and data["category_id"] is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="Cannot null expense category",
            )

    if "category_id" in data and data["category_id"] is not None:
        cat = (
            db.execute(select(Category).filter(Category.id == data["category_id"]))
            .scalars()
            .first()
        )
        if not cat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for field, value in data.items():
        setattr(transaction, field, value)

    db.commit()
    db.refresh(transaction)

    return transaction


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_transaction_by_id(
    id: int, curr_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    transaction = db.execute(select(Transaction).filter(Transaction.id == id)).scalars().first()

    if not transaction:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

    if transaction.linked_transfer_id is not None:
        linked_transaction = (
            db.execute(select(Transaction).filter(Transaction.id == transaction.linked_transfer_id))
            .scalars()
            .first()
        )

        transaction.linked_transfer_id = None
        if linked_transaction is not None:
            linked_transaction.linked_transfer_id = None

        db.flush()

        db.delete(transaction)
        if linked_transaction is not None:
            db.delete(linked_transaction)
    else:
        db.delete(transaction)

    db.commit()
    return None
