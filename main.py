from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QPushButton
from re import search

import sys, subprocess

# Константы для отображения статуса VPN и управления им
VPN_DIR = "/etc/amnezia/amneziawg"
VPN_ON = "Отключить VPN"
VPN_OFF = "Включить VPN"
VPN_STATUS = "Статус подключения: {}"
VPN_STATUS_ON = "Подключен к VPN"
VPN_STATUS_OFF = "Не подключен к VPN"
ENABLE_ANOTHER_VPN = "Включить другой VPN"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # Настройка окна приложения
        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(800,500))

        # Создание главного виджета и установка его в качестве центрального
        main_field = QWidget()
        self.setCentralWidget(main_field)

        # Создание виджета для отображения списка VPN и загрузка списка VPN из директории
        self.list_vpn = QListWidget()
        self.list_vpn.setFixedWidth(200)
        self.load_vpn_list()

        # Инициализация переменной для хранения имени активного VPN
        self.active_vpn_name = None

        # Создание виджета для отображения информации о VPN и настройки его как только для чтения
        self.info_vpn = QTextEdit()
        self.info_vpn.setReadOnly(True)

        # Создание виджета для отображения статуса VPN
        self.status_vpn = QTextEdit()
        self.status_vpn.setReadOnly(True)
        self.status_vpn.setFixedHeight(30)
        self.status_vpn.setText(f'{VPN_STATUS.format(self.check_status_vpn())}')

        # Создание кнопки для включения/отключения VPN и настройка ее начального состояния
        self.button_vpn = QPushButton("")
        self.button_vpn.setFixedWidth(150)
        self.button_vpn.setEnabled(False)
        self.button_vpn.clicked.connect(self.enable_and_disable_vpn)

        # Размещение виджетов в окне с помощью горизонтального и вертикального компоновщика
        layout = QHBoxLayout(main_field)
        layout.addWidget(self.list_vpn)
        info_layout = QVBoxLayout()
        info_layout.addWidget(self.info_vpn)
        button_layout = QHBoxLayout()
        button_layout.addWidget(self.status_vpn)
        button_layout.addWidget(self.button_vpn)

        # Добавление компоновки кнопок в компоновку информации и добавление компоновки информации в главный компоновщик
        info_layout.addLayout(button_layout)
        layout.addLayout(info_layout)

        # Подключение сигнала клика по элементу списка VPN к функции загрузки информации о выбранном VPN
        self.list_vpn.itemClicked.connect(self.load_info_vpn)

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
        status = subprocess.check_output(["sudo", "awg", "show"], universal_newlines=True)
        return status

    # Функция для загрузки списка VPN из директории и добавления их в виджет списка VPN
    def load_vpn_list(self):
        d = subprocess.run(
            ["sudo", "ls", "/etc/amnezia/amneziawg"], 
            capture_output=True, 
            text=True
        )
        for filename in d.stdout.strip().split('\n'):
            if filename:
                self.list_vpn.addItem(filename)

    # Функция для загрузки информации о выбранном VPN из его конфигурационного файла и отображения ее в виджете информации о VPN
    def load_info_vpn(self):
        item = self.list_vpn.currentItem()
        if item is not None:
            filename = item.text()
            d = subprocess.run(
                ["sudo", "cat", f"{VPN_DIR}/{filename}"],
                capture_output=True,
                text=True
            )

            private_key = search(r'PrivateKey\s*=\s*(\S+)', d.stdout)
            mtu = search(r'MTU\s*=\s*(\S+)', d.stdout)
            address = search(r'Address\s*=\s*(\S+)', d.stdout)
            endpoint = search(r'Endpoint\s*=\s*(\S+)', d.stdout)
            public_key = search(r'PublicKey\s*=\s*(\S+)', d.stdout)
            dns = search(r'DNS\s*=\s*(\S+)', d.stdout)
            allowed_ips = search(r'AllowedIPs\s*=\s*(\S+)', d.stdout)

            if not all([private_key, mtu, address, endpoint, public_key, dns, allowed_ips]):
                return None

            info = f"Интерфейс: {filename.partition('.')[0]}\n"
            info += f"Приватный ключ: {private_key.group(1)}\n"
            info += f"MTU: {mtu.group(1)}\n"
            info += f"IP-адреса: {address.group(1)}\n"
            info += f"DNS: {dns.group(1)}\n"

            info += f"Публичный ключ: {public_key.group(1)}\n"
            info += f"Разрешенные IP-адреса: {allowed_ips.group(1)}\n"
            info += f"IP-адреса сервера: {endpoint.group(1)}\n"
            self.info_vpn.setText(info)

            self.refresh_controls(filename)

    # Функция для включения или отключения VPN в зависимости от текущего статуса подключения и выбранного VPN
    def enable_and_disable_vpn(self):
        filename = self.selected_vpn_name()
        if filename is None:
            return

        status = self.check_status_vpn()
        active_interface = self.look_another_vpn()
        selected_interface = self.interface_name_from_filename(filename)
        
        if status == VPN_STATUS_OFF:
            subprocess.run(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
            self.active_vpn_name = filename

        elif status == VPN_STATUS_ON:
            if active_interface == selected_interface:
                subprocess.run(["sudo", "awg-quick", "down", f"{VPN_DIR}/{filename}"])
                self.active_vpn_name = None

            elif active_interface is not None:
                subprocess.run(["sudo", "awg-quick", "down", f"{VPN_DIR}/{active_interface}.conf"])
                subprocess.run(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
                self.active_vpn_name = filename

        self.refresh_controls(filename)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec()
