import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Tuple
from models import Operation


class FinancialAnalyzer:

    def __init__(self, operations: List[Operation]):
        self.operations = operations
        self.df = self._to_dataframe()

    def _to_dataframe(self) -> pd.DataFrame:
        data = []
        for op in self.operations:
            data.append({
                'id': op.id,
                'amount': op.amount,
                'category': op.category,
                'date': op.date,
                'type': op.type,
                'description': op.description
            })
        return pd.DataFrame(data)

    def get_balance(self) -> float:
        if self.df.empty:
            return 0.0

        income = self.df[self.df['type'] == 'income']['amount'].sum()
        expense = self.df[self.df['type'] == 'expense']['amount'].sum()
        return income - expense

    def get_expenses_by_category(self, period_days: int = None) -> Dict[str, float]:
        df = self.df[self.df['type'] == 'expense']

        if period_days:
            cutoff = datetime.now() - timedelta(days=period_days)
            df = df[df['date'] >= cutoff]

        return df.groupby('category')['amount'].sum().to_dict()

    def get_income_vs_expense(self, period_days: int = 30) -> Tuple[float, float]:
        cutoff = datetime.now() - timedelta(days=period_days)
        period_df = self.df[self.df['date'] >= cutoff]

        income = period_df[period_df['type'] == 'income']['amount'].sum()
        expense = period_df[period_df['type'] == 'expense']['amount'].sum()

        return income, expense

    def get_top_expenses(self, limit: int = 10) -> pd.DataFrame:
        return self.df[self.df['type'] == 'expense'].nlargest(limit, 'amount')

    def get_monthly_summary(self) -> pd.DataFrame:
        if self.df.empty:
            return pd.DataFrame()

        df = self.df.copy()
        df['month'] = df['date'].dt.to_period('M')

        summary = df.groupby(['month', 'type'])['amount'].sum().unstack(fill_value=0)
        summary['balance'] = summary.get('income', 0) - summary.get('expense', 0)

        return summary
