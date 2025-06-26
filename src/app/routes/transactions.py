from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.controllers.database import get_session
from src.app.controllers.security import get_current_user
from src.app.models.models import Transaction, User
from src.app.models.schemas import (
    FilterTransaction,
    Message,
    TransactionList,
    TransactionPublic,
    TransactionSchema,
    TransactionUpdate,
)

router = APIRouter(prefix='/transactions', tags=['Tarefas'])
Session = Annotated[AsyncSession, Depends(get_session)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post('/', response_model=TransactionPublic)
async def crate_transaction(
    transaction: TransactionSchema,
    user: CurrentUser,
    session: Session,
):
    transaction_db = Transaction(
        title=transaction.title,
        description=transaction.description,
        state=transaction.state,
        user_id=user.id,
    )
    session.add(transaction_db)
    await session.commit()
    await session.refresh(transaction_db)

    return transaction_db


@router.get('/', response_model=TransactionList)
async def list_transactions(
    session: Session,
    user: CurrentUser,
    transaction_filter: Annotated[FilterTransaction, Query()],
):
    query = select(Transaction).where(Transaction.user_id == user.id)
    if transaction_filter.title:
        query = query.filter(Transaction.title.contains(transaction_filter.title))
    if transaction_filter.description:
        query = query.filter(
            Transaction.description.contains(transaction_filter.description)
        )
    if transaction_filter.state:
        query = query.filter(Transaction.state.contains(transaction_filter.state))

    transactions = await session.scalars(
        query.offset(transaction_filter.offset).limit(transaction_filter.limit)
    )

    return {'transactions': transactions.all()}


@router.patch('/{transaction_id}', response_model=TransactionPublic)
async def patch_transaction(
    transaction_id: int,
    session: Session,
    user: CurrentUser,
    transaction: TransactionUpdate,
):
    transaction_db = await session.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id and user.id == Transaction.user_id
        )
    )
    if not transaction_db:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='Not Found')
    for (
        key,
        value,
    ) in transaction.model_dump(exclude_unset=True).items():
        setattr(transaction_db, key, value)

    session.add(transaction_db)
    await session.commit()
    await session.refresh(transaction_db)

    return transaction_db


@router.delete('/{transaction_id}', response_model=Message)
async def delete_transaction(
    transaction_id: int,
    session: Session,
    user: CurrentUser,
):
    transaction = await session.scalar(
        select(Transaction).where(
            Transaction.id == transaction_id, Transaction.user_id == user.id
        )
    )
    if not transaction:
        raise HTTPException(detail='Not Found', status_code=HTTPStatus.NOT_FOUND)
    await session.delete(transaction)
    await session.commit()

    return {'message': 'Transaction has been delete successfully'}
