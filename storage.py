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