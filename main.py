from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QHBoxLayout, QVBoxLayout, QWidget, QTextEdit, QPushButton
from re import search

import sys, subprocess

VPN_DIR = "/etc/amnezia/amneziawg"
VPN_ON = "Отключить VPN"
VPN_OFF = "Включить VPN"
VPN_STATUS = "Статус подключения: {}"
VPN_STATUS_ON = "Подключен к VPN"
VPN_STATUS_OFF = "Не подключен к VPN"

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(800,500))

        main_field = QWidget()
        self.setCentralWidget(main_field)

        self.list_vpn = QListWidget()
        self.list_vpn.setFixedWidth(200)
        self.load_vpn_list()

        self.info_vpn = QTextEdit()
        self.info_vpn.setReadOnly(True)

        self.status_vpn = QTextEdit()
        self.status_vpn.setReadOnly(True)
        self.status_vpn.setFixedHeight(30)
        self.status_vpn.setText(f'{VPN_STATUS.format(self.check_status_vpn())}')

        self.button_vpn = QPushButton("")
        self.button_vpn.setFixedWidth(150)
        self.button_vpn.clicked.connect(self.enable_and_disable_vpn)

        layout = QHBoxLayout(main_field)
        layout.addWidget(self.list_vpn)

        info_layout = QVBoxLayout()
        info_layout.addWidget(self.info_vpn)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.status_vpn)
        button_layout.addWidget(self.button_vpn)

        info_layout.addLayout(button_layout)
        layout.addLayout(info_layout)

        self.list_vpn.itemClicked.connect(self.load_info_vpn)

    def check_status_vpn(self):
        status = subprocess.check_output(["sudo", "awg", "show"], universal_newlines=True)

        if "interface: " in status:
            status = VPN_STATUS_ON
        else:
            status = VPN_STATUS_OFF

        return status

    def load_vpn_list(self):
        d = subprocess.run(
            ["sudo", "ls", "/etc/amnezia/amneziawg"], 
            capture_output=True, 
            text=True
        )
        for filename in d.stdout.strip().split('\n'):
            self.list_vpn.addItem(filename)

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

            status = self.check_status_vpn()
            self.status_vpn.setText(f'{VPN_STATUS.format(status)}')
            self.button_vpn.setText(VPN_OFF if status == VPN_STATUS_OFF else VPN_ON)

    def enable_and_disable_vpn(self):
        item = self.list_vpn.currentItem()
        if item is not None:
            filename = item.text()
            status = self.check_status_vpn()
            if status == VPN_STATUS_OFF:
                subprocess.run(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
                status = self.check_status_vpn()
                self.button_vpn.setText(VPN_ON)
                self.status_vpn.setText(VPN_STATUS.format(VPN_STATUS_ON))
            elif status == VPN_STATUS_ON:
                subprocess.run(["sudo", "awg-quick", "down", f"{VPN_DIR}/{filename}"])
                status = self.check_status_vpn()
                self.button_vpn.setText(VPN_OFF)
                self.status_vpn.setText(VPN_STATUS.format(VPN_STATUS_OFF))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec()
