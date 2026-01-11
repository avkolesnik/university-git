from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import re


@dataclass
class Category:
    id: int
    name: str
    type: str

    def __post_init__(self):
        if self.type not in ['income', 'expense']:
            raise ValueError("Тип категории должен быть 'income' или 'expense'")


@dataclass
class Operation:
    id: int
    amount: float
    category: str
    date: datetime
    description: Optional[str] = None
    type: str = "expense"

    def __post_init__(self):
        if self.amount <= 0:
            raise ValueError("Сумма должна быть положительной")
        if self.type not in ['income', 'expense']:
            raise ValueError("Тип операции должен быть 'income' или 'expense'")