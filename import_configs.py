from PyQt6.QtWidgets import QFileDialog
from os import path

# Определение директории для открытия диалогового окна выбора файла конфигурации VPN
HOME_DIR = path.expanduser("~")
DOWNLOADS_RU = path.join(HOME_DIR, "Загрузки")
DOWNLOADS_EN = path.join(HOME_DIR, "Downloads")

if path.exists(DOWNLOADS_RU):
    DIR = DOWNLOADS_RU
elif path.exists(DOWNLOADS_EN):
    DIR = DOWNLOADS_EN
else:
    DIR = HOME_DIR

class ImportConfigs:
    def __init__(self, parent=None):
        self.parent = parent

    # Функция для открытия диалогового окна выбора файла конфигурации VPN и возвращения выбранного пути к файлу
    def open_file_dialog(self):
        # Возвращаем путь к выбранному файлу
        file_path, _ = QFileDialog.getOpenFileName(
            self.parent,
            "Выберите файл конфигурации VPN",
            DIR,
            "Конфигурации VPN (*.conf *.zip);;Конфигурация VPN (*.conf);;ZIP-архив (*.zip);;Все файлы (*)"
        )
        return file_path
