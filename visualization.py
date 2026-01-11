import matplotlib.pyplot as plt
import pandas as pd
from typing import List
from models import Operation
from analysis import FinancialAnalyzer


class FinancialVisualizer:

    def __init__(self, operations: List[Operation]):
        self.operations = operations
        self.analyzer = FinancialAnalyzer(operations)

    def plot_expenses_trend(self):
        if not self.operations:
            print("Нет данных для визуализации")
            return

        df = self.analyzer.df
        expenses_df = df[df['type'] == 'expense'].copy()

        if expenses_df.empty:
            print("Нет данных о расходах")
            return

        expenses_df = expenses_df.sort_values('date')
        expenses_df['cumulative'] = expenses_df['amount'].cumsum()

        plt.figure(figsize=(10, 6))
        plt.plot(expenses_df['date'], expenses_df['cumulative'],
                 marker='o', linewidth=2)
        plt.title('Динамика расходов', fontsize=14)
        plt.xlabel('Дата')
        plt.ylabel('Накопленные расходы (руб.)')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.show()

    def plot_expenses_pie(self, period_days: int = 30):
        expenses = self.analyzer.get_expenses_by_category(period_days)

        if not expenses:
            print("Нет данных о расходах за указанный период")
            return

        sorted_expenses = sorted(expenses.items(), key=lambda x: x[1], reverse=True)

        if len(sorted_expenses) > 8:
            top_categories = dict(sorted_expenses[:7])
            other_sum = sum(amount for _, amount in sorted_expenses[7:])
            top_categories['Другие'] = other_sum
        else:
            top_categories = dict(sorted_expenses)

        plt.figure(figsize=(8, 8))
        plt.pie(top_categories.values(), labels=top_categories.keys(),
                autopct='%1.1f%%', startangle=90)
        plt.title(f'Расходы по категориям (последние {period_days} дней)',
                  fontsize=14)
        plt.tight_layout()
        plt.show()

    def plot_monthly_summary(self, summary: pd.DataFrame):
        if summary.empty:
            return

        summary = summary.tail(6)

        fig, ax = plt.subplots(figsize=(12, 6))

        x = range(len(summary))
        width = 0.35

        if 'income' in summary.columns:
            ax.bar([i - width / 2 for i in x], summary['income'],
                   width, label='Доходы', color='green')

        if 'expense' in summary.columns:
            ax.bar([i + width / 2 for i in x], summary['expense'],
                   width, label='Расходы', color='red')

        ax.set_xlabel('Месяц')
        ax.set_ylabel('Сумма (руб.)')
        ax.set_title('Доходы и расходы по месяцам')
        ax.set_xticks(x)
        ax.set_xticklabels([str(month) for month in summary.index])
        ax.legend()
        ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def save_chart_to_file(self, chart_type: str, filename: str):
        pass