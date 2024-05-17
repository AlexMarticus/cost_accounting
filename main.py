import os
import sys
from datetime import datetime, timedelta, date
from PySide6 import QtGui
from PySide6.QtWidgets import QMainWindow, QApplication, QTableWidgetItem
from DataBase import Database
from add_category import AddCategory
from delete_category import DeleteCategory
from push_windows import CompleteDialog, ErrorDialog
from ui_main import Ui_MainWindow


basedir = os.path.dirname(__file__)

try:
    from ctypes import windll  # Only exists on Windows.
    myappid = 'mycompany.myproduct.subproduct.version'
    windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except ImportError:
    pass


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.stackedWidget.setCurrentIndex(1)
        self.DB = Database()
        if not self.DB.get_categories():
            self.DB.add_category('Разное')
        self.type_comboBox.addItem('Расход', 'outcome')
        self.type_comboBox.addItem('Доход', 'income')

        self.load_dates()
        self.load_categories()
        self.load_balance_labels()
        self.filter_date()
        self.filter_type()
        self.filter_categories()
        self.sort_type()
        self.load_TableWidget()

        self.commit_trans_bt.clicked.connect(self.commit_transaction)
        self.new_category_bt.clicked.connect(self.add_category)
        self.delete_category_bt.clicked.connect(self.delete_category)
        self.transactions_bt.clicked.connect(self.switch_window)
        self.back_to_MainMenu_bt.clicked.connect(self.switch_window)
        self.delete_trans_bt.clicked.connect(self.delete_transaction)

        self.type_comboBox.currentIndexChanged.connect(self.income_or_outcome)
        self.filter_date_comboBox.currentIndexChanged.connect(self.load_TableWidget)
        self.filter_type_comboBox.currentIndexChanged.connect(self.load_TableWidget)
        self.filter_categories_comboBox.currentIndexChanged.connect(self.load_TableWidget)
        self.sort_comboBox.currentIndexChanged.connect(self.load_TableWidget)

    def load_TableWidget(self):
        self.tableWidget.clear()
        date_ = self.filter_date_comboBox.currentData()
        type_ = self.filter_type_comboBox.currentData()
        category = self.filter_categories_comboBox.currentData()
        transactions = self.DB.get_transactions(date_transaction=date_, type_transaction=type_, category_id=category)
        transactions.sort(key=lambda x: x.price_transaction, reverse=self.sort_comboBox.currentData())
        self.tableWidget.setRowCount(len(transactions))
        self.tableWidget.setColumnCount(7)

        for row, transaction in enumerate(transactions):
            if transaction.type_transaction == 'income':
                type_ = 'Доход'
            else:
                type_ = 'Расход'
            self.tableWidget.setItem(row, 0, QTableWidgetItem(str(transaction.transaction_id)))
            self.tableWidget.setItem(row, 1, QTableWidgetItem(str(transaction.name_transaction)))
            self.tableWidget.setItem(row, 2, QTableWidgetItem(str(transaction.price_transaction)))
            self.tableWidget.setItem(row, 3, QTableWidgetItem(type_))
            self.tableWidget.setItem(row, 4, QTableWidgetItem(str(transaction.category.name_category)))
            self.tableWidget.setItem(row, 5, QTableWidgetItem(str(transaction.date_transaction.strftime('%d-%m-%Y'))))
            self.tableWidget.setItem(row, 6, QTableWidgetItem(str(transaction.comment_transaction)))

        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setHorizontalHeaderLabels(['id_hidden', 'Название', 'Цена', 'Тип', 'Категория', 'Дата',
                                                    'Комментарий'])

    def delete_transaction(self):
        if self.tableWidget.selectedItems():
            row = self.tableWidget.selectedItems()[0].row()
            id_ = self.tableWidget.takeItem(row, 0).text()
            self.DB.delete_transaction(id_)
            self.update_fields()

    def update_fields(self):
        self.product_name_lineEdit.clear()
        self.price_doubleSpinBox.setValue(0)
        self.load_dates()
        self.load_categories()
        self.comment_textEdit.clear()
        self.load_balance_labels()
        self.filter_categories()
        self.load_TableWidget()

    def filter_date(self):
        self.filter_date_comboBox.clear()
        date_today = datetime.combine(date.today(), datetime.min.time())
        self.filter_date_comboBox.addItem('За всё время', -1)
        self.filter_date_comboBox.addItem('За сегодня', date_today)
        self.filter_date_comboBox.addItem('За последние 7 дней', date_today - timedelta(6))
        self.filter_date_comboBox.addItem('За последние 30 дней', date_today - timedelta(29))

    def filter_type(self):
        self.filter_type_comboBox.clear()
        self.filter_type_comboBox.addItem('Доходы/Расходы', -1)
        self.filter_type_comboBox.addItem('Расходы', 'outcome')
        self.filter_type_comboBox.addItem('Доходы', 'income')

    def sort_type(self):
        self.sort_comboBox.clear()
        self.sort_comboBox.addItem('От min к max', False)
        self.sort_comboBox.addItem('От max к min', True)

    def filter_categories(self):
        self.filter_categories_comboBox.clear()
        self.filter_categories_comboBox.addItem('Все категории', -1)
        for i in self.DB.get_categories():
            self.filter_categories_comboBox.addItem(i.name_category, i.category_id)

    def switch_window(self):
        if self.stackedWidget.currentIndex() == 0:
            self.stackedWidget.setCurrentIndex(1)
        else:
            self.stackedWidget.setCurrentIndex(0)

    def delete_category(self):
        dialog = DeleteCategory()
        dialog.exec()
        self.update_fields()

    def add_category(self):
        dialog = AddCategory()
        dialog.exec()
        self.update_fields()

    def commit_transaction(self):
        name = self.product_name_lineEdit.text().strip()
        price = self.price_doubleSpinBox.value()
        type_ = self.type_comboBox.currentData()
        category = self.category_comboBox.currentData()
        date_ = self.date_comboBox.currentData()
        comment = self.comment_textEdit.toPlainText().strip()
        if name.strip() and price != 0:
            self.DB.add_transaction(name, price, type_, category, date_, comment)
            self.update_fields()
            dialog = CompleteDialog()
        else:
            dialog = ErrorDialog()
        dialog.exec()

    def load_balance_labels(self):
        from_date = datetime.combine(date.today(), datetime.min.time()) - timedelta(date.today().day - 1)
        incomes = sum([i.price_transaction for i in
                       self.DB.get_transactions(date_transaction=from_date, type_transaction='income')])
        outcomes = sum([i.price_transaction for i in
                        self.DB.get_transactions(date_transaction=from_date, type_transaction='outcome')])
        self.balance_value_label.setText(str(round(incomes - outcomes, 2)))
        self.income_value_label.setText(str(incomes))
        self.outcome_value_label.setText(str(outcomes))

    def income_or_outcome(self):  # деактивация полей при выборе "Доход"
        if self.type_comboBox.currentData() == 'income':
            self.categoty_label.hide()
            self.category_comboBox.hide()
        else:
            self.category_comboBox.show()
            self.categoty_label.show()

    def load_dates(self):
        self.date_comboBox.clear()
        date_today = datetime.combine(date.today(), datetime.min.time())
        for i in range(15):
            self.date_comboBox.addItem((date_today - timedelta(i)).strftime('%d.%m.%Y'), date_today - timedelta(i))

    def load_categories(self):
        self.category_comboBox.clear()
        for i in self.DB.get_categories():
            self.category_comboBox.addItem(i.name_category, i.category_id)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QtGui.QIcon('icon.ico'))
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
