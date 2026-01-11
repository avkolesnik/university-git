import unittest
from datetime import datetime
from models import Operation, Category


class TestModels(unittest.TestCase):

    def test_operation_creation(self):
        op = Operation(
            id=1,
            amount=100.50,
            category="Еда",
            date=datetime(2024, 1, 15),
            description="Обед в кафе",
            type="expense"
        )

        self.assertEqual(op.id, 1)
        self.assertEqual(op.amount, 100.50)
        self.assertEqual(op.category, "Еда")
        self.assertEqual(op.type, "expense")

    def test_operation_invalid_amount(self):
        with self.assertRaises(ValueError):
            Operation(
                id=1,
                amount=-100,
                category="Еда",
                date=datetime.now(),
                type="expense"
            )

    def test_category_creation(self):
        cat = Category(id=1, name="Зарплата", type="income")
        self.assertEqual(cat.name, "Зарплата")
        self.assertEqual(cat.type, "income")

    def test_category_invalid_type(self):
        with self.assertRaises(ValueError):
            Category(id=1, name="Тест", type="invalid")


if __name__ == '__main__':
    unittest.main()