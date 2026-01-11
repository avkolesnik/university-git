import re
from datetime import datetime
from typing import Optional, Tuple


class Validator:

    @staticmethod
    def validate_amount(amount_str: str) -> Tuple[bool, Optional[float], str]:
        if not re.match(r'^\d+(\.\d{1,2})?$', amount_str):
            return False, None, "Сумма должна быть числом (например: 100 или 100.50)"

        amount = float(amount_str)
        if amount <= 0:
            return False, None, "Сумма должна быть больше 0"

        return True, amount, ""

    @staticmethod
    def validate_date(date_str: str) -> Tuple[bool, Optional[datetime], str]:
        patterns = [
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{2}\.\d{2}\.\d{4}$',
            r'^\d{2}/\d{2}/\d{4}$'
        ]

        for pattern in patterns:
            if re.match(pattern, date_str):
                try:
                    if '-' in date_str:
                        date = datetime.strptime(date_str, '%Y-%m-%d')
                    elif '.' in date_str:
                        date = datetime.strptime(date_str, '%d.%m.%Y')
                    else:
                        date = datetime.strptime(date_str, '%d/%m/%Y')
                    return True, date, ""
                except ValueError:
                    pass

        return False, None, "Дата должна быть в формате ДД.ММ.ГГГГ"

    @staticmethod
    def validate_category(category: str) -> Tuple[bool, str]:
        if not category or len(category.strip()) == 0:
            return False, "Категория не может быть пустой"

        category = category.strip()

        if not re.match(r'^[a-zA-Zа-яА-Я0-9\s\-_]+$', category):
            return False, "Категория содержит недопустимые символы"

        return True, category
