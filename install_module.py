from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMainWindow, \
QVBoxLayout, QWidget, QTextEdit, QPushButton
from os import chmod, environ, execv, path, remove
from stat import S_IRUSR, S_IWUSR, S_IXUSR
from subprocess import run
from sys import executable, argv
from tempfile import mkstemp

# Получение директории, в которой находится текущий скрипт
WORK_DIR = path.dirname(path.abspath(__file__))

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
        self.info_install.setText("Нажмите кнопку ниже, чтобы установить AmneziaWG")

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
        install_script = f"{WORK_DIR}/install.sh"

        # Запрашиваем пароль sudo через Qt-диалог и проверяем его перед запуском установки
        password = self.request_sudo_password()
        if password is None:
            return

        sudo_wrapper = self.create_sudo_wrapper()

        # Отображаем сообщение о начале установки и отключаем кнопку, чтобы предотвратить повторные нажатия
        self.info_install.setText("Установка запущена.")
        self.button_install.setEnabled(False)
        QApplication.processEvents()

        # Устанавливаем переменную окружения, чтобы скрипт установки знал, что аутентификация sudo уже была выполнена через Qt-диалог
        env = environ.copy()
        env["AMNEZIA_CLIENT_SUDO_PASSWORD"] = password
        env["AMNEZIA_CLIENT_SUDO_WRAPPER"] = sudo_wrapper
        password = None

        # Запускаем скрипт установки и ждем его завершения
        try:
            result = run([install_script], capture_output=True, text=True, env=env)
        finally:
            self.remove_sudo_wrapper(sudo_wrapper)
            self.button_install.setEnabled(True)

        if result.returncode == 0:
            self.info_install.setText("AmneziaWG успешно установлен!")

            # Изменяем текст кнопки и переназначаем ее на функцию перезагрузки программы
            self.button_install.setText("Перезагрузить программу")
            self.button_install.disconnect()
            self.button_install.clicked.connect(self.reboot)
        else:
            # Если установка завершилась с ошибкой, отображаем сообщение об ошибке и вывод скрипта
            output = "\n".join(part for part in [result.stdout, result.stderr] if part)
            self.info_install.setText(
                f"Ошибка при установке AmneziaWG:\n{output}"
            )

    # Функция для запроса и проверки пароля sudo через Qt-диалог перед запуском установки
    def request_sudo_password(self):
        for attempt in range(3):
            password, ok = QInputDialog.getText(
                self,
                "Пароль sudo",
                "Введите пароль sudo:",
                QLineEdit.EchoMode.Password
            )
            if not ok:
                return None

            sudo_check = self.authenticate_sudo(password)
            if sudo_check.returncode == 0:
                return password

            password = None
            if attempt < 2:
                self.info_install.setText("Неверный пароль sudo. Попробуйте еще раз.")
                QApplication.processEvents()

        self.info_install.setText("Ошибка авторизации sudo:\nневерный пароль.")
        return None

    # Функция для проверки пароля sudo
    def authenticate_sudo(self, password):
        return run(
            ["sudo", "-k", "-S", "-p", "", "-v"],
            input=f"{password}\n",
            capture_output=True,
            text=True
        )

    # Функция для создания временного sudo-wrapper, который yay сможет использовать вместо обычного sudo
    def create_sudo_wrapper(self):
        fd, wrapper_path = mkstemp(prefix="amneziawg-client-sudo-", suffix=".sh")
        script = (
            "#!/usr/bin/env bash\n"
            "printf '%s\\n' \"$AMNEZIA_CLIENT_SUDO_PASSWORD\" | "
            "sudo -S -p '' \"$@\"\n"
        )

        with open(fd, "w", encoding="utf-8") as file:
            file.write(script)

        chmod(wrapper_path, S_IRUSR | S_IWUSR | S_IXUSR)
        return wrapper_path

    # Функция для удаления временного sudo-wrapper после завершения установки
    def remove_sudo_wrapper(self, wrapper_path):
        try:
            remove(wrapper_path)
        except OSError:
            pass
    
    # Функция для перезагрузки программы после успешной установки AmneziaWG
    def reboot(self):
        execv(executable, [executable] + argv)
