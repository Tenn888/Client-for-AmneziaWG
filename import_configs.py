from PyQt6.QtWidgets import QFileDialog
from os import path

# Определение директории для открытия диалогового окна выбора файла конфигурации VPN
if path.exists("/home/tenn888/Загрузки/"):
    DIR = path.expanduser("~/Загрузки/")
elif path.exists("/home/tenn888/Downloads/"):
    DIR = path.expanduser("~/Downloads/")

class ImportConfigs:
    def __init__(self, parent=None):
        self.parent = parent

    # Функция для открытия диалогового окна выбора файла конфигурации VPN и возвращения выбранного пути к файлу
    def open_file_dialog(self):
        # Создание и настройка диалогового окна выбора файла конфигурации VPN
        dialog = QFileDialog(parent=self.parent,directory=DIR)
        dialog.setWindowTitle("Выберите файл конфигурации VPN")
        dialog.setFileMode(QFileDialog.FileMode.ExistingFile)
        dialog.setNameFilters([
            "Все файлы (*)",
            "Конфигурация VPN (*.conf)",
            "ZIP-архив (*.zip)"
        ])
        dialog.setLabelText(QFileDialog.DialogLabel.Accept, "Открыть")
        dialog.setLabelText(QFileDialog.DialogLabel.Reject, "Отмена")
        dialog.setLabelText(QFileDialog.DialogLabel.FileName, "Имя файла:")
        dialog.setLabelText(QFileDialog.DialogLabel.FileType, "Тип файла:")
        dialog.setLabelText(QFileDialog.DialogLabel.LookIn, "Папка:")

        # Возвращаем путь к выбранному файлу
        if dialog.exec():
            return dialog.selectedFiles()[0]
        return ""
    