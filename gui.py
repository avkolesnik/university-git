import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
from models import Operation
from storage import CSVStorage
from validators import Validator
from analysis import FinancialAnalyzer
from visualization import FinancialVisualizer


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
        ttk.Button(btn_frame, text="Импорт из CSV",
                   command=self.import_csv).pack(side="left", padx=5)

        frame.rowconfigure(0, weight=1)
        frame.columnconfigure(0, weight=1)

    def refresh_operations_list(self):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for op in reversed(self.operations[-100:]):  # Показываем последние 100
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