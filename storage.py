import csv
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path
from models import Operation


class Storage:

    def __init__(self, source: str = "csv"):
        self.source = source
        self.data_dir = Path("data")
        self.data_dir.mkdir(exist_ok=True)

    def save_operation(self, operation: Operation) -> bool:
        pass

    def get_operations(self, filters: Optional[Dict] = None) -> List[Operation]:
        pass

    def delete_operation(self, operation_id: int) -> bool:
        pass


class CSVStorage(Storage):

    def __init__(self, filename: str = "operations.csv"):
        super().__init__("csv")
        self.filename = self.data_dir / filename
        self._init_csv_file()

    def _init_csv_file(self):
        if not self.filename.exists():
            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date',
                                 'description', 'type'])

    def save_operation(self, operation: Operation) -> bool:
        try:
            with open(self.filename, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    operation.id,
                    operation.amount,
                    operation.category,
                    operation.date.isoformat(),
                    operation.description or '',
                    operation.type
                ])
            return True
        except Exception as e:
            print(f"Ошибка сохранения: {e}")
            return False

    def get_operations(self, filters: Optional[Dict] = None) -> List[Operation]:
        operations = []
        try:
            with open(self.filename, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    op = Operation(
                        id=int(row['id']),
                        amount=float(row['amount']),
                        category=row['category'],
                        date=datetime.fromisoformat(row['date']),
                        description=row['description'] or None,
                        type=row['type']
                    )

                    if filters and not self._matches_filters(op, filters):
                        continue

                    operations.append(op)
        except FileNotFoundError:
            pass
        return operations

    def _matches_filters(self, operation: Operation, filters: Dict) -> bool:
        for key, value in filters.items():
            if key == 'category' and operation.category != value:
                return False
            if key == 'type' and operation.type != value:
                return False
            if key == 'date_from' and operation.date < value:
                return False
            if key == 'date_to' and operation.date > value:
                return False
        return True

    def delete_operation(self, operation_id: int) -> bool:
        try:
            operations = self.get_operations()

            operation_to_delete = None
            filtered_operations = []

            for op in operations:
                if op.id == operation_id:
                    operation_to_delete = op
                else:
                    filtered_operations.append(op)

            if operation_to_delete is None:
                print(f"Операция с ID {operation_id} не найдена")
                return False

            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date',
                                 'description', 'type'])

                for op in filtered_operations:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date.isoformat(),
                        op.description or '',
                        op.type
                    ])

            print(f"Операция {operation_id} удалена")
            return True

        except Exception as e:
            print(f"Ошибка при удалении операции: {e}")
            return False

    def update_operation(self, operation: Operation) -> bool:
        try:
            operations = self.get_operations()
            updated = False

            for i, op in enumerate(operations):
                if op.id == operation.id:
                    operations[i] = operation
                    updated = True
                    break

            if not updated:
                print(f"Операция с ID {operation.id} не найдена для обновления")
                return False

            with open(self.filename, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date',
                                 'description', 'type'])

                for op in operations:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date.isoformat(),
                        op.description or '',
                        op.type
                    ])

            print(f"Операция {operation.id} обновлена")
            return True

        except Exception as e:
            print(f"Ошибка при обновлении операции: {e}")
            return False


def export_to_csv(self, filename: str, operations: List[Operation] = None) -> bool:
    try:
        if operations is None:
            operations = self.get_operations()

        with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f, delimiter=';')

            writer.writerow([
                'ID', 'Дата', 'Тип', 'Категория', 'Сумма',
                'Описание', 'Год', 'Месяц', 'День недели'
            ])

            for op in operations:
                type_russian = 'Доход' if op.type == 'income' else 'Расход'

                weekdays = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
                day_of_week = weekdays[op.date.weekday()]

                writer.writerow([
                    op.id,
                    op.date.strftime("%d.%m.%Y"),
                    type_russian,
                    op.category,
                    f"{op.amount:.2f}".replace('.', ','),  # Запятая для десятичных
                    op.description or '',
                    op.date.year,
                    op.date.month,
                    day_of_week
                ])

        print(f"Экспортировано {len(operations)} операций в {filename}")
        return True

    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
        return False


def export_simple_csv(self, filename: str, operations: List[Operation] = None) -> bool:
    try:
        if operations is None:
            operations = self.get_operations()

        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'amount', 'category', 'date',
                             'description', 'type'])

            for op in operations:
                writer.writerow([
                    op.id,
                    op.amount,
                    op.category,
                    op.date.isoformat(),
                    op.description or '',
                    op.type
                ])

        return True
    except Exception as e:
        print(f"Ошибка при экспорте: {e}")
        return False
