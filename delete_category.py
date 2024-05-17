from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel, QComboBox, QPushButton
from DataBase import Database


class DeleteCategory(QDialog):
    def __init__(self):
        super().__init__()
        self.DB = Database()
        self.setWindowTitle('УДАЛЕНИЕ КАТЕГОРИИ')
        self.setFixedSize(220, 120)
        layout = QVBoxLayout()
        label = QLabel("Выберите категорию для удаления")
        layout.addWidget(label)
        self.ledit = QComboBox()
        for i in self.DB.get_categories()[1:]:
            self.ledit.addItem(i.name_category, i.category_id)
        layout.addWidget(self.ledit)
        bt = QPushButton()
        bt.setText('Удалить')
        bt.clicked.connect(self.bt_clicked)
        layout.addWidget(bt)
        self.setLayout(layout)

    def bt_clicked(self):
        self.DB.delete_category(self.ledit.currentData())
        self.close()
