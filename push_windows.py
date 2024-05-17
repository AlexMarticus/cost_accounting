from PySide6.QtWidgets import QDialog, QVBoxLayout, QLabel


class ErrorDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('ОШИБКА')
        self.setFixedSize(210, 70)
        layout = QVBoxLayout()
        label = QLabel("Информация заполнена неверно!")
        layout.addWidget(label)
        self.setLayout(layout)


class CompleteDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('УСПЕШНО')
        self.setFixedSize(210, 70)
        layout = QVBoxLayout()
        label = QLabel("Транзакция успешно добавлена!")
        layout.addWidget(label)
        self.setLayout(layout)
