from pydantic import BaseModel

from application.telegram.menu.base import ListRenderingInfo


class TransactionInfo(BaseModel):
    id: int


class TransactionsListRenderingInfo(ListRenderingInfo):
    callback_data: TransactionInfo
