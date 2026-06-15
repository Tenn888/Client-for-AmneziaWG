from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QWidget, QTextEdit, QMessageBox, QVBoxLayout, QPushButton, QHBoxLayout
from os import path, remove
from tempfile import NamedTemporaryFile
from subprocess import run

class EditWindow(QMainWindow):
    def __init__(self, config_path, parent=None):
        super().__init__()

        # Настройка окна приложения
        self.setWindowTitle("Редактирование конфигурационного файла")
        self.setMinimumSize(QSize(600,400))

        # Создание главного виджета и установка его в качестве центрального
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout()
        main_widget.setLayout(layout)

        # Создание виджета для отображения и редактирования конфигурации
        self.info_content = QTextEdit()
        self.info_content.setReadOnly(False)
        layout.addWidget(self.info_content)

        # Кнопки сохранения/закрытия
        buttons_layout = QHBoxLayout()
        self.save_button = QPushButton("Сохранить")
        self.save_button.clicked.connect(self.save_configuration)
        buttons_layout.addWidget(self.save_button)
        layout.addLayout(buttons_layout)

        self.config_path = config_path
        self.parent = parent
        self.edit_vpn_configuration(config_path)

    def run_command(self, command, input=None):
        if command and command[0] == "sudo":
            command = ["sudo", "-n", *command[1:]]

        return run(command, capture_output=True, text=True, input=input)

    def edit_vpn_configuration(self, config_path):
        # Чтение содержимого конфигурационного файла VPN с помощью команды sudo cat
        configuration = self.run_command(["sudo", "cat", config_path])
        if configuration.returncode != 0:
            QMessageBox.critical(self, "Ошибка чтения", configuration.stderr)
            return

        # Записанное содержимое показываем в виджете для редактирования
        with NamedTemporaryFile("w+", encoding="utf-8", delete=False) as temp_file:
            temp_file.write(configuration.stdout)
            temp_file.seek(0)
            edited_content = temp_file.read()

        self.info_content.setText(edited_content)

    def save_configuration(self):
        # Получаем текст из виджета и сохраняем во временный файл, затем копируем с sudo
        edited_text = self.info_content.toPlainText()
        try:
            with NamedTemporaryFile("w+", encoding="utf-8", delete=False) as temp_file:
                temp_file.write(edited_text)
                temp_name = temp_file.name

            save_result = self.run_command(["sudo", "cp", "-f", temp_name, self.config_path])
            if save_result.returncode != 0:
                QMessageBox.critical(self, "Ошибка сохранения", save_result.stderr)
                return

            QMessageBox.information(self, "Готово", "Конфигурация сохранена.")

            # Обновим информацию в родительском окне, если он передан
            try:
                if self.parent is not None:
                    basename = path.basename(self.config_path)
                    self.parent.load_vpn_list(basename)
                    # Если этот файл сейчас выбран, явно обновим информацию
                    if self.parent.selected_vpn_name() == basename:
                        self.parent.load_info_vpn()
            except Exception:
                pass
        finally:
            try:
                if temp_name:
                    remove(temp_name)
                self.close()
            except Exception:
                pass
