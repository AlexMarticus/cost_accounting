from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QLineEdit, QPushButton
from DataBase import Database
from push_windows import ErrorDialog


class AddCategory(QDialog):
    def __init__(self):
        super().__init__()
        self.DB = Database()
        self.setWindowTitle('ДОБАВЛЕНИЕ КАТЕГОРИИ')
        self.setFixedSize(220, 120)
        layout = QVBoxLayout()
        label = QLabel("Введите новое название категории")
        layout.addWidget(label)
        self.ledit = QLineEdit()
        layout.addWidget(self.ledit)
        bt = QPushButton()
        bt.setText('Добавить')
        bt.clicked.connect(self.bt_clicked)
        layout.addWidget(bt)
        self.setLayout(layout)

    def bt_clicked(self):
        if not self.ledit.text().strip():
            dialog = ErrorDialog()
            dialog.exec()
        else:
            self.DB.add_category(self.ledit.text())
            self.close()
