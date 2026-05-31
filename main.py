from PyQt6.QtCore import QSize, Qt
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, \
QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QPushButton, QGroupBox, \
QLabel, QFormLayout, QMessageBox
from PyQt6.QtGui import QIcon
from re import MULTILINE, search
from sys import argv
from subprocess import run
from os import path
from shutil import which
from tempfile import NamedTemporaryFile

import install_module, import_configs

# Константы для отображения статуса VPN и управления им
VPN_DIR = "/etc/amnezia/amneziawg"
VPN_ON = "Отключить VPN"
VPN_OFF = "Включить VPN"
VPN_STATUS = "Статус подключения: {}"
VPN_STATUS_ON = "Подключен к VPN"
VPN_STATUS_OFF = "Не подключен к VPN"
ENABLE_ANOTHER_VPN = "Включить другой VPN"

WORK_DIR = path.dirname(path.abspath(__file__))
BUTTON_WIDTH = 200
BUTTON_HEIGHT = 30

# Функция для проверки, установлен ли AmneziaWG, путем поиска его исполняемого файла в системе
def checking_installed_amneziawg():
    return which("awg") is not None


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Настройка окна приложения
        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(800,500))

        # Создание главного виджета и установка его в качестве центрального
        main_field = QWidget()
        self.setCentralWidget(main_field)

        # Создание кнопки для импорта vpn и привязывание к кнопке функции для импорта 
        #self.button_add_vpn = QPushButton("Импортировать VPN")
        self.button_add_vpn = QPushButton("")
        self.button_add_vpn.setFixedSize(BUTTON_WIDTH // 3, BUTTON_HEIGHT)
        self.button_add_vpn.setIcon(QIcon(path.join(WORK_DIR, "Images/Importing.png")))
        self.button_add_vpn.clicked.connect(self.import_vpn)

        self.button_edit_vpn = QPushButton("")
        self.button_edit_vpn.setFixedSize(BUTTON_WIDTH // 3, BUTTON_HEIGHT)
        self.button_edit_vpn.setIcon(QIcon(path.join(WORK_DIR, "Images/Editing.png")))
        self.button_edit_vpn.clicked.connect(self.edit_vpn)

        self.button_delete_vpn = QPushButton("")
        self.button_delete_vpn.setFixedSize(BUTTON_WIDTH // 3, BUTTON_HEIGHT)
        self.button_delete_vpn.setIcon(QIcon(path.join(WORK_DIR, "Images/Deletion.png")))
        self.button_delete_vpn.clicked.connect(self.import_vpn)

        # Создание виджета для отображения списка VPN и загрузка списка VPN из директории
        self.list_vpn = QListWidget()
        self.list_vpn.setFixedWidth(200)
        self.load_vpn_list()

        # Инициализация переменной для хранения имени активного VPN
        self.active_vpn_name = None

        # Создание виджета для отображения статуса VPN
        self.status_vpn = QTextEdit()
        self.status_vpn.setReadOnly(True)
        self.status_vpn.setFixedHeight(30)
        self.status_vpn.setText(f'{VPN_STATUS.format(self.check_status_vpn())}')

        # Создание кнопки для включения/отключения VPN и настройка ее начального состояния
        self.button_vpn = QPushButton("")
        self.button_vpn.setFixedSize(BUTTON_WIDTH, BUTTON_HEIGHT)
        self.button_vpn.setEnabled(False)
        self.button_vpn.clicked.connect(self.enable_and_disable_vpn)

        self.vpn_buttons_layout = QHBoxLayout()
        self.vpn_buttons_layout.addWidget(self.button_add_vpn)
        self.vpn_buttons_layout.addWidget(self.button_edit_vpn)
        self.vpn_buttons_layout.addWidget(self.button_delete_vpn)

        # Размещение виджетов в окне с помощью горизонтального и вертикального компоновщика
        # Левая панель со списком VPN и кнопкой добавления
        self.vpn_list_layout = QVBoxLayout()
        self.vpn_list_layout.addWidget(self.list_vpn)
        self.vpn_list_layout.addLayout(self.vpn_buttons_layout)

        self.layout = QHBoxLayout(main_field)
        self.layout.addLayout(self.vpn_list_layout)

        # Правая панель с информацией о VPN, статусом и кнопкой управления 
        self.info_layout = QVBoxLayout()
        self.info_widgets = []
        self.button_layout = QHBoxLayout()
        self.button_layout.addWidget(self.status_vpn)
        self.button_layout.addWidget(self.button_vpn)

        # Добавление компоновки кнопок в компоновку информации и добавление компоновки информации в главный компоновщик
        self.info_layout.addStretch()
        self.info_layout.addLayout(self.button_layout)
        self.layout.addLayout(self.info_layout)

        # Подключение сигнала клика по элементу списка VPN к функции загрузки информации о выбранном VPN
        self.list_vpn.itemClicked.connect(self.load_info_vpn)

    # Функция для импорта VPN из выбранного файла конфигурации и обновления списка VPN после импорта
    def import_vpn(self):
        try:
            iv = import_configs.ImportConfigs(self)
            file_path = iv.open_file_dialog()
            if not file_path:
                return

            # Получение расширения файла и выполнение соответствующих действий в зависимости от типа файла
            file_extension = path.splitext(file_path)[1].lower()

            if file_extension == ".conf":
                result = self.run_command(["sudo", "cp", "-f", file_path, VPN_DIR])
                self.load_vpn_list(path.basename(file_path))
                return

            elif file_extension == ".zip":
                result = self.run_command(["sudo", "unzip", "-o", file_path, "-d", VPN_DIR])
                self.load_vpn_list()
                return

            else:
                QMessageBox.warning(self, "Ошибка", "Можно импортировать только файлы .conf и .zip.")
                return
        except Exception as error:
            QMessageBox.critical(self, "Ошибка импорта", str(error))

    # Функция для редактирования VPN
    def edit_vpn(self):
        # Получение имени выбранного VPN из списка и проверка его наличия
        filename = self.selected_vpn_name()
        if filename is None:
            QMessageBox.warning(self, "Ошибка", "Выберите VPN для редактирования.")
            return
        
        config_path = path.join(VPN_DIR, filename)
        result = self.run_command(["sudo", "cat", config_path])
        
        with NamedTemporaryFile("w", encoding="utf-8") as temp_file:
            temp_file.write(result)
            self.run_command(["sudo", "cp", temp_file.name, config_path])


        if result.returncode != 0:
            QMessageBox.critical(self, "Ошибка сохранения", result.stderr)
            return

        QMessageBox.information(self, "Готово", "Конфигурация сохранена.")

    # Функция для выполнения команд в терминале и получения их вывода
    def run_command(self, command):
        if command and command[0] == "sudo":
            command = ["sudo", "-n", *command[1:]]

        return run(command, capture_output=True, text=True)

    # Функция для проверки наличия VPN в списке по его имени
    def list_has_vpn(self, filename):
        for i in range(self.list_vpn.count()):
            if self.list_vpn.item(i).text() == filename:
                return True
        return False

    # Функция для получения имени интерфейса из имени файла конфигурации VPN
    def interface_name_from_filename(self, filename):
        return filename.partition(".")[0]

    # Функция для получения имени выбранного VPN из списка
    def selected_vpn_name(self):
        item = self.list_vpn.currentItem()
        if item is None:
            return None
        return item.text()

    # Функция для обновления состояния кнопки и статуса VPN в зависимости от текущего состояния подключения и выбранного VPN
    def refresh_controls(self, selected_filename):
        status = self.check_status_vpn()
        active_interface = self.look_another_vpn()

        # Обновление текста статуса VPN в зависимости от наличия активного интерфейса
        if active_interface is None:
            self.status_vpn.setText(VPN_STATUS.format(VPN_STATUS_OFF))
        else:
            self.status_vpn.setText(VPN_STATUS.format(active_interface))

        self.button_vpn.setEnabled(True)
        selected_interface = self.interface_name_from_filename(selected_filename)

        # Обновление текста кнопки в зависимости от статуса подключения и выбранного VPN
        if status == VPN_STATUS_OFF:
            self.button_vpn.setText(VPN_OFF)
        elif active_interface == selected_interface:
            self.button_vpn.setText(VPN_ON)
        else:
            self.button_vpn.setText(ENABLE_ANOTHER_VPN)

    # Функция для проверки статуса VPN путем анализа вывода команды "awg show"
    def check_status_vpn(self):
        status = self.receiving_vpn()

        if "interface: " in status:
            status = VPN_STATUS_ON
        else:
            status = VPN_STATUS_OFF

        return status
    
    # Функция для получения имени активного интерфейса VPN из вывода команды "awg show"
    def look_another_vpn(self):
        status = self.receiving_vpn()

        for line in status.splitlines():
            line = line.strip()

            if line.startswith("interface:"):
                return line.split(":")[1].strip()

        return None
    
    # Функция для получения имени активного VPN из списка VPN
    def active_vpn(self):
        filename = self.list_vpn.currentItem().text()
        return filename

    # Функция для получения статуса VPN путем выполнения команды "awg show" и анализа ее вывода
    def receiving_vpn(self):
        status = self.run_command(["sudo", "awg", "show"])
        return status.stdout

    # Функция для загрузки списка VPN из директории и добавления их в виджет списка VPN
    def load_vpn_list(self, selected_filename=None):
        # Очистка текущего списка VPN перед загрузкой нового списка из директории
        self.list_vpn.clear()
        result = self.run_command(["sudo", "ls", VPN_DIR])

        # Сортировка списка файлов по алфавиту и добавление только файлов с расширением .conf в виджет списка VPN
        for filename in sorted(result.stdout.splitlines()):
            if filename.endswith(".conf"):
                self.list_vpn.addItem(filename)

        # Если указано имя файла, который должен быть выбран после загрузки списка,
        # проверяем его наличие в списке и устанавливаем его как текущий элемент, 
        # а затем загружаем информацию о нем
        if selected_filename and self.list_has_vpn(selected_filename):
            matching_items = self.list_vpn.findItems(selected_filename, Qt.MatchFlag.MatchExactly)
            if matching_items:
                self.list_vpn.setCurrentItem(matching_items[0])
                self.load_info_vpn()

    # Функция для загрузки информации о выбранном VPN из его конфигурационного файла и отображения ее в виджете информации о VPN
    def load_info_vpn(self):
        # Получение выбранного элемента из списка VPN и извлечение его имени для загрузки информации о нем
        item = self.list_vpn.currentItem()
        if item is not None:
            self.clear_info_vpn()
            filename = item.text()
            result = self.run_command(["sudo", "cat", f"{VPN_DIR}/{filename}"])

            # Извлечение необходимых параметров из конфигурационного файла VPN с помощью регулярных выражений
            private_key = self.config_value(result.stdout, "PrivateKey")
            mtu = self.config_value(result.stdout, "MTU")
            address = self.config_value(result.stdout, "Address")
            endpoint = self.config_value(result.stdout, "Endpoint")
            public_key = self.config_value(result.stdout, "PublicKey")
            dns = self.config_value(result.stdout, "DNS")
            allowed_ips = self.config_value(result.stdout, "AllowedIPs")

            # Проверка наличия всех необходимых параметров в конфигурационном файле VPN
            # и отображение предупреждения, если какой-либо параметр отсутствует
            if not all([private_key, mtu, address, endpoint, public_key, dns, allowed_ips]):
                return None
            
            # Создание групповых виджетов для отображения информации об интерфейсе и пире VPN, 
            # заполнение их данными из конфигурационного файла и добавление их в компоновку информации о VPN
            group_1 = QGroupBox(f"Интерфейс: {filename.partition('.')[0]}")
            group_1_layout = QFormLayout()
            group_1.setLayout(group_1_layout)
            group_2 = QGroupBox("Пир")
            group_2_layout = QFormLayout()
            group_2.setLayout(group_2_layout)

            # Добавление строк с параметрами интерфейса и пира в соответствующие групповые виджеты
            group_1_layout.addRow("Приватный ключ:", QLabel(private_key))
            group_1_layout.addRow("MTU:", QLabel(mtu))
            group_1_layout.addRow("IP-адрес:", QLabel(address))
            group_1_layout.addRow("DNS:", QLabel(dns))
            group_2_layout.addRow("Публичный ключ:", QLabel(public_key))
            group_2_layout.addRow("Разрешенные IP-адреса:", QLabel(allowed_ips))
            group_2_layout.addRow("IP-адреса сервера:", QLabel(endpoint))

            # Добавление групповых виджетов с информацией об интерфейсе и пире в компоновку информации о VPN
            self.info_layout.insertWidget(0, group_1)
            self.info_layout.insertWidget(1, group_2)
            self.info_widgets = [group_1, group_2]

            # Обновляем статус VPN и состояние кнопки для выбранной конфигурации
            self.refresh_controls(filename)

    # Функция для извлечения значения параметра из текста конфигурационного файла VPN с помощью регулярного выражения
    def config_value(self, config_text, key):
        value = search(rf'^{key}\s*=\s*(.+)$', config_text, flags=MULTILINE)
        if value is None:
            return None
        return value.group(1).strip()

    # Функция для очистки ранее отображенной информации о VPN
    def clear_info_vpn(self):
        for widget in self.info_widgets:
            self.info_layout.removeWidget(widget)
            widget.deleteLater()
        self.info_widgets = []

    # Функция для включения или отключения VPN в зависимости от текущего статуса подключения и выбранного VPN
    def enable_and_disable_vpn(self):
        # Получение имени выбранного VPN из списка и проверка его наличия
        filename = self.selected_vpn_name()
        if filename is None:
            return

        # Получение текущего статуса VPN, имени активного интерфейса и имени интерфейса из выбранного файла конфигурации VPN
        status = self.check_status_vpn()
        active_interface = self.look_another_vpn()
        selected_interface = self.interface_name_from_filename(filename)
        
        # В зависимости от текущего статуса подключения и выбранного VPN выполняем соответствующие команды для включения или отключения VPN,
        # а также обновляем имя активного VPN и состояние кнопки
        if status == VPN_STATUS_OFF:
            self.run_command(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
            self.active_vpn_name = filename

        elif status == VPN_STATUS_ON:
            if active_interface == selected_interface:
                self.run_command(["sudo", "awg-quick", "down", f"{VPN_DIR}/{filename}"])
                self.active_vpn_name = None

            elif active_interface is not None:
                self.run_command(["sudo", "awg-quick", "down", f"{VPN_DIR}/{active_interface}.conf"])

                self.run_command(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
                self.active_vpn_name = filename

        # Обновляем статус VPN и состояние кнопки для выбранной конфигурации
        self.refresh_controls(filename)


if __name__ == '__main__':
    app = QApplication(argv)
    app.setWindowIcon(QIcon(path.join(WORK_DIR, "Images/AmneziaWG.png")))

    if not checking_installed_amneziawg():
        ix = install_module.InstallWindow()
        ix.setWindowTitle("Установщик AmneziaWG")
        ix.show()
    else:
        ex = MainWindow()
        ex.setWindowTitle("AmneziaWG")
        ex.show()
    app.exec()
