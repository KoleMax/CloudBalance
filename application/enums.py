from enum import Enum


class UserRoles(Enum):
    CREATOR = 1
    ADMIN = 2
    USER = 3


class TransactionTypes(Enum):
    INCOME = "income"
    EXPENSE = "expense"
