import csv
import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from typing import List
from models import Operation
from storage import CSVStorage
from validators import Validator
from analysis import FinancialAnalyzer
from visualization import FinancialVisualizer


def _export_to_json(filename: str, operations: List[Operation]):
    data = []
    for op in operations:
        data.append({
            'id': op.id,
            'amount': op.amount,
            'category': op.category,
            'date': op.date.isoformat(),
            'description': op.description,
            'type': op.type
        })

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    messagebox.showinfo("Успех", f"JSON файл сохранен:\n{filename}")


def _export_universal_csv(filename: str, operations: List[Operation], separate: bool = False):
    if separate:
        base_name = filename.rsplit('.', 1)[0]

        income_ops = [op for op in operations if op.type == 'income']
        if income_ops:
            income_file = f"{base_name}_income.csv"
            with open(income_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date', 'description'])
                for op in income_ops:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date.isoformat(),
                        op.description or ''
                    ])

        expense_ops = [op for op in operations if op.type == 'expense']
        if expense_ops:
            expense_file = f"{base_name}_expense.csv"
            with open(expense_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['id', 'amount', 'category', 'date', 'description'])
                for op in expense_ops:
                    writer.writerow([
                        op.id,
                        op.amount,
                        op.category,
                        op.date.isoformat(),
                        op.description or ''
                    ])

        messagebox.showinfo("Успех",
                            f"Созданы файлы:\n{income_file if income_ops else ''}\n{expense_file if expense_ops else ''}")
    else:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id', 'amount', 'category', 'date', 'description', 'type'])
            for op in operations:
                writer.writerow([
                    op.id,
                    op.amount,
                    op.category,
                    op.date.isoformat(),
                    op.description or '',
                    op.type
                ])
        messagebox.showinfo("Успех", f"Файл сохранен:\n{filename}")


def _write_excel_csv(filename: str, operations: List[Operation], title: str = ""):
    with open(filename, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')

        if title:
            writer.writerow([f"# {title}"])
            writer.writerow([f"# Дата экспорта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}"])
            writer.writerow([])

        writer.writerow([
            'ID', 'Дата', 'День недели', 'Тип операции',
            'Категория', 'Сумма (руб.)', 'Описание'
        ])

        for op in operations:
            type_russian = 'Доход' if op.type == 'income' else 'Расход'
            weekdays_rus = ['Понедельник', 'Вторник', 'Среда', 'Четверг',
                            'Пятница', 'Суббота', 'Воскресенье']
            day_of_week = weekdays_rus[op.date.weekday()]

            writer.writerow([
                op.id,
                op.date.strftime("%d.%m.%Y"),
                day_of_week,
                type_russian,
                op.category,
                f"{op.amount:.2f}".replace('.', ','),
                op.description or ''
            ])


class FinanceApp:

    def __init__(self, root):
        self.amount_entry = None
        self.root = root
        self.root.title("Финансовый трекер v1.0")
        self.root.geometry("1000x700")
        self.storage = CSVStorage()
        self.operations = self.storage.get_operations()
        self.next_id = max([op.id for op in self.operations], default=0) + 1
        self.setup_ui()
        self.refresh_operations_list()

    def setup_ui(self):
        self.create_input_panel()
        self.create_operations_list()
        self.create_analysis_panel()
        self.create_status_bar()

    def create_input_panel(self):
        frame = ttk.LabelFrame(self.root, text="Новая операция", padding=10)
        frame.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        ttk.Label(frame, text="Тип:").grid(row=0, column=0, sticky="w")
        self.type_var = tk.StringVar(value="expense")
        ttk.Combobox(frame, textvariable=self.type_var,
                     values=["expense", "income"], width=15,
                     state="readonly").grid(row=0, column=1, padx=5)

        ttk.Label(frame, text="Сумма:").grid(row=0, column=2, sticky="w", padx=(20, 0))
        self.amount_entry = ttk.Entry(frame, width=15)
        self.amount_entry.grid(row=0, column=3, padx=5)

        ttk.Label(frame, text="Категория:").grid(row=1, column=0, sticky="w", pady=(10, 0))
        self.category_entry = ttk.Entry(frame, width=15)
        self.category_entry.grid(row=1, column=1, pady=(10, 0), padx=5)

        ttk.Label(frame, text="Дата (ДД.ММ.ГГГГ):").grid(row=1, column=2, sticky="w",
                                                         pady=(10, 0), padx=(20, 0))
        self.date_entry = ttk.Entry(frame, width=15)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.date_entry.grid(row=1, column=3, pady=(10, 0), padx=5)

        ttk.Label(frame, text="Описание:").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.desc_entry = ttk.Entry(frame, width=50)
        self.desc_entry.grid(row=2, column=1, columnspan=3,
                             pady=(10, 0), padx=5, sticky="ew")

        ttk.Button(frame, text="Добавить операцию",
                   command=self.add_operation).grid(row=3, column=3,
                                                    pady=(10, 0), sticky="e")

    def add_operation(self):
        amount_valid, amount, amount_msg = Validator.validate_amount(
            self.amount_entry.get()
        )
        if not amount_valid:
            messagebox.showerror("Ошибка", amount_msg)
            return

        date_valid, date, date_msg = Validator.validate_date(
            self.date_entry.get()
        )
        if not date_valid:
            messagebox.showerror("Ошибка", date_msg)
            return

        category_valid, category_msg = Validator.validate_category(
            self.category_entry.get()
        )
        if not category_valid:
            messagebox.showerror("Ошибка", category_msg)
            return

        operation = Operation(
            id=self.next_id,
            amount=amount,
            category=self.category_entry.get(),
            date=date,
            description=self.desc_entry.get() or None,
            type=self.type_var.get()
        )

        if self.storage.save_operation(operation):
            self.operations.append(operation)
            self.next_id += 1
            self.refresh_operations_list()
            self.clear_input_fields()
            messagebox.showinfo("Успех", "Операция добавлена")
        else:
            messagebox.showerror("Ошибка", "Не удалось сохранить операцию")

    def clear_input_fields(self):
        self.amount_entry.delete(0, tk.END)
        self.category_entry.delete(0, tk.END)
        self.date_entry.delete(0, tk.END)
        self.date_entry.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.desc_entry.delete(0, tk.END)
        self.type_var.set("expense")

    def create_operations_list(self):
        frame = ttk.LabelFrame(self.root, text="История операций", padding=10)
        frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        columns = ("ID", "Дата", "Тип", "Категория", "Сумма", "Описание")
        self.tree = ttk.Treeview(frame, columns=columns, show="headings", height=15)

        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)

        self.tree.column("Описание", width=200)
        self.tree.column("Дата", width=100)

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

        btn_frame = ttk.Frame(frame)
        btn_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0), sticky="ew")

        ttk.Button(btn_frame, text="Удалить выбранное",
                   command=self.delete_selected).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Экспорт в CSV",
                   command=self.export_csv).pack(side="left", padx=5)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def refresh_operations_list(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for op in reversed(self.operations[-100:]):
            self.tree.insert("", "end", values=(
                op.id,
                op.date.strftime("%d.%m.%Y"),
                "Доход" if op.type == "income" else "Расход",
                op.category,
                f"{op.amount:.2f}",
                op.description or ""
            ))

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию для удаления")
            return

        if messagebox.askyesno("Подтверждение", "Удалить выбранную операцию?"):
            self.refresh_operations_list()

    def create_analysis_panel(self):
        frame = ttk.LabelFrame(self.root, text="Анализ и отчеты", padding=10)
        frame.grid(row=1, column=1, sticky="nsew", padx=10, pady=5)

        ttk.Button(frame, text="Баланс",
                   command=self.show_balance).pack(fill="x", pady=5)
        ttk.Button(frame, text="Расходы по категориям",
                   command=self.show_expenses_by_category).pack(fill="x", pady=5)
        ttk.Button(frame, text="График расходов",
                   command=self.show_expenses_chart).pack(fill="x", pady=5)
        ttk.Button(frame, text="Круговая диаграмма",
                   command=self.show_pie_chart).pack(fill="x", pady=5)
        ttk.Button(frame, text="Месячный отчет",
                   command=self.show_monthly_report).pack(fill="x", pady=5)

    def show_balance(self):
        analyzer = FinancialAnalyzer(self.operations)
        balance = analyzer.get_balance()

        messagebox.showinfo("Баланс",
                            f"Текущий баланс: {balance:.2f} руб.\n\n"
                            f"Доходы: {sum(op.amount for op in self.operations if op.type == 'income'):.2f} руб.\n"
                            f"Расходы: {sum(op.amount for op in self.operations if op.type == 'expense'):.2f} руб.")

    def show_expenses_by_category(self):
        analyzer = FinancialAnalyzer(self.operations)
        expenses = analyzer.get_expenses_by_category(period_days=30)

        if not expenses:
            messagebox.showinfo("Расходы", "Нет данных о расходах за последние 30 дней")
            return

        report = "Расходы за последние 30 дней:\n\n"
        for category, amount in sorted(expenses.items(), key=lambda x: x[1], reverse=True):
            report += f"{category}: {amount:.2f} руб.\n"

        messagebox.showinfo("Расходы по категориям", report)

    def show_expenses_chart(self):
        visualizer = FinancialVisualizer(self.operations)
        visualizer.plot_expenses_trend()

    def show_pie_chart(self):
        visualizer = FinancialVisualizer(self.operations)
        visualizer.plot_expenses_pie()

    def show_monthly_report(self):
        analyzer = FinancialAnalyzer(self.operations)
        summary = analyzer.get_monthly_summary()

        if summary.empty:
            messagebox.showinfo("Отчет", "Нет данных для отчета")
            return

        visualizer = FinancialVisualizer(self.operations)
        visualizer.plot_monthly_summary(summary)

    def export_csv(self):
        filename = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            pass

    def import_csv(self):
        filename = filedialog.askopenfilename(
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if filename:
            pass

    def create_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set(f"Операций: {len(self.operations)} | "
                            f"Используется: CSV хранилище")

        status_bar = ttk.Label(self.root, textvariable=self.status_var,
                               relief="sunken", anchor="w")
        status_bar.grid(row=2, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

    def delete_selected(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите операцию для удаления")
            return

        selected_item = self.tree.item(selection[0])
        operation_id = int(selected_item['values'][0])

        if not messagebox.askyesno("Подтверждение",
                                   f"Удалить операцию #{operation_id}?\n"
                                   f"{selected_item['values'][1]} - "
                                   f"{selected_item['values'][3]}: "
                                   f"{selected_item['values'][4]} руб."):
            return

        try:
            if self.storage.delete_operation(operation_id):
                self.operations = [op for op in self.operations if op.id != operation_id]
                self.refresh_operations_list()
                self.update_status_bar()
                messagebox.showinfo("Успех", f"Операция #{operation_id} удалена")
            else:
                messagebox.showerror("Ошибка", "Не удалось удалить операцию")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при удалении: {str(e)}")

    def update_status_bar(self):
        balance = self.calculate_balance()
        self.status_var.set(
            f"Операций: {len(self.operations)} | "
            f"Баланс: {balance:.2f} руб. | "
            f"Используется: CSV хранилище"
        )

    def calculate_balance(self) -> float:
        income = sum(op.amount for op in self.operations if op.type == 'income')
        expense = sum(op.amount for op in self.operations if op.type == 'expense')
        return income - expense


    def export_csv(self):

        format_dialog = tk.Toplevel(self.root)
        format_dialog.title("Выбор формата экспорта")
        format_dialog.geometry("500x350")
        format_dialog.transient(self.root)
        format_dialog.grab_set()

        tk.Label(format_dialog, text="Выберите формат экспорта:",
                 font=("Arial", 11, "bold")).pack(pady=10)

        format_var = tk.StringVar(value="excel")

        formats_info = {
            "excel": {
                "name": "Для Excel (Windows)",
                "description": "UTF-8 с BOM, разделитель ';', десятичная запятая",
                "ext": ".csv",
                "encoding": "utf-8-sig"
            },
            "universal": {
                "name": "Универсальный CSV",
                "description": "UTF-8, разделитель ',', десятичная точка",
                "ext": ".csv",
                "encoding": "utf-8"
            },
            "json": {
                "name": "JSON формат",
                "description": "Структурированные данные для других программ",
                "ext": ".json",
                "encoding": "utf-8"
            }
        }

        format_frame = ttk.Frame(format_dialog)
        format_frame.pack(fill="x", padx=20, pady=10)

        row = 0
        for format_key, format_info in formats_info.items():
            rb = tk.Radiobutton(
                format_frame,
                text=format_info["name"],
                variable=format_var,
                value=format_key,
                font=("Arial", 10)
            )
            rb.grid(row=row, column=0, sticky="w", pady=5)

            desc_label = tk.Label(
                format_frame,
                text=format_info["description"],
                font=("Arial", 9),
                fg="gray",
                justify="left"
            )
            desc_label.grid(row=row, column=1, sticky="w", padx=10, pady=5)

            row += 1

        options_frame = ttk.LabelFrame(format_dialog, text="Дополнительные опции")
        options_frame.pack(fill="x", padx=20, pady=10)

        date_filter_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Экспортировать только за последние 30 дней",
                       variable=date_filter_var).pack(anchor="w", padx=10, pady=5)

        separate_var = tk.BooleanVar(value=False)
        tk.Checkbutton(options_frame, text="Создать отдельные файлы для доходов и расходов",
                       variable=separate_var).pack(anchor="w", padx=10, pady=5)

        def perform_export():
            global datetime
            operations_to_export = self.operations.copy()

            if date_filter_var.get():
                from datetime import datetime, timedelta
                cutoff_date = datetime.now() - timedelta(days=30)
                operations_to_export = [
                    op for op in operations_to_export
                    if op.date >= cutoff_date
                ]

            if not operations_to_export:
                messagebox.showwarning("Нет данных", "Нет операций для экспорта")
                format_dialog.destroy()
                return

            selected_format = formats_info[format_var.get()]

            filename = filedialog.asksaveasfilename(
                defaultextension=selected_format["ext"],
                filetypes=[
                    (f"{selected_format['name']} (*{selected_format['ext']})",
                     f"*{selected_format['ext']}"),
                    ("Все файлы", "*.*")
                ],
                initialfile=f"finances_{datetime.now().strftime('%Y%m%d_%H%M%S')}{selected_format['ext']}"
            )

            if not filename:
                format_dialog.destroy()
                return

            try:
                if format_var.get() == "excel":
                    self._export_for_excel(filename, operations_to_export, separate_var.get())
                elif format_var.get() == "universal":
                    _export_universal_csv(filename, operations_to_export, separate_var.get())
                elif format_var.get() == "json":
                    _export_to_json(filename, operations_to_export)

            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка при экспорте: {str(e)}")

            format_dialog.destroy()

        btn_frame = tk.Frame(format_dialog)
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Экспорт", command=perform_export,
                  bg="green", fg="white", padx=20, font=("Arial", 10)).pack(side="left", padx=10)
        tk.Button(btn_frame, text="Отмена", command=format_dialog.destroy,
                  bg="gray", fg="white", padx=20, font=("Arial", 10)).pack(side="left", padx=10)

    def _export_for_excel(self, filename: str, operations: List[Operation], separate: bool = False):
        global income_file, expense_file

        if separate:
            income_ops = [op for op in operations if op.type == 'income']
            expense_ops = [op for op in operations if op.type == 'expense']

            base_name = filename.rsplit('.', 1)[0]

            if income_ops:
                income_file = f"{base_name}_доходы.csv"
                _write_excel_csv(income_file, income_ops, "Доходы")

            if expense_ops:
                expense_file = f"{base_name}_расходы.csv"
                _write_excel_csv(expense_file, expense_ops, "Расходы")

            messagebox.showinfo("Успех",
                                f"Созданы файлы:\n"
                                f"{income_file if income_ops else ''}\n"
                                f"{expense_file if expense_ops else ''}")
        else:
            _write_excel_csv(filename, operations, "Финансовые операции")
            messagebox.showinfo("Успех", f"Файл сохранен:\n{filename}")