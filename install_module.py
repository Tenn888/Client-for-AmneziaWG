from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QMainWindow, QVBoxLayout, QWidget, QTextEdit, QPushButton
import os, sys, subprocess

# Получение директории, в которой находится текущий скрипт
WORK_DIR = os.path.dirname(os.path.abspath(__file__))

class InstallWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Настройка окна приложения
        self.setWindowTitle("Установка AmneziaWG")
        self.setMinimumSize(QSize(400,200))

        # Создание главного виджета и установка его в качестве центрального
        main_field = QWidget()
        self.setCentralWidget(main_field)

        # Создание виджета для отображения информации об установке и настройки его как только для чтения
        self.info_install = QTextEdit()
        self.info_install.setReadOnly(True)
        self.info_install.setText("Нажмите кнопку ниже, чтобы установить AmneziaWG (Откроется терминал)")

        # Создание кнопки для запуска установки и подключение ее к функции установки
        self.button_install = QPushButton("Установить")
        self.button_install.clicked.connect(self.install_amneziawg)

        # Размещение виджетов в окне с помощью вертикального компоновщика
        layout = QVBoxLayout(main_field)
        layout.addWidget(self.info_install)
        layout.addWidget(self.button_install)

    # Функция для запуска установки AmneziaWG и отображения результатов в виджете информации об установке
    def install_amneziawg(self):
        # Даем права на выполнение скрипта установки и запускаем его
        subprocess.run(["chmod", "+x", f"{WORK_DIR}/install.sh"])
        result = subprocess.run([f"{WORK_DIR}/install.sh"])
        if result.returncode == 0:
            self.info_install.setText("AmneziaWG успешно установлен!")
            
            # Изменяем текст кнопки и переназначаем ее на функцию перезагрузки программы
            self.button_install.setText("Перезагрузить программу")
            self.button_install.disconnect()
            self.button_install.clicked.connect(self.reboot)
        else:
            self.info_install.setText(f"Ошибка при установке AmneziaWG:\n{result.stderr}")
    
    # Функция для перезагрузки программы после успешной установки AmneziaWG
    def reboot(self):
        os.execv(sys.executable, [sys.executable] + sys.argv)