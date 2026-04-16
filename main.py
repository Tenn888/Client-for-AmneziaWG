from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QHBoxLayout, QWidget, QTextEdit, QPushButton
from re import search

import sys, subprocess

VPN_DIR = "/etc/amnezia/amneziawg"
VPN_ON = "Отключить VPN"
VPN_OFF = "Включить VPN"

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

        layout = QHBoxLayout(main_field)
        layout.addWidget(self.list_vpn)
        layout.addWidget(self.info_vpn)

        self.list_vpn.itemClicked.connect(lambda: self.load_info_vpn(layout))

    def check_status_vpn(self):
        status = subprocess.check_output(["sudo", "awg", "show"], universal_newlines=True)

        if "interface: " in status:
            status = VPN_ON
        else:
            status = VPN_OFF

        return status

    def load_vpn_list(self):
        d = subprocess.run(
            ["sudo", "ls", "/etc/amnezia/amneziawg"], 
            capture_output=True, 
            text=True
        )
        for filename in d.stdout.strip().split('\n'):
            self.list_vpn.addItem(filename)

    def load_info_vpn(self, layout):
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
            info += f"Статус подключения: {'Отключен'}\n"
            info += f"Приватный ключ: {private_key.group(1)}\n"
            info += f"MTU: {mtu.group(1)}\n"
            info += f"IP-адреса: {address.group(1)}\n"
            info += f"DNS: {dns.group(1)}\n"

            info += f"Публичный ключ: {public_key.group(1)}\n"
            info += f"Разрешенные IP-адреса: {allowed_ips.group(1)}\n"
            info += f"IP-адреса сервера: {endpoint.group(1)}\n"
            self.info_vpn.setText(info)

            status = self.check_status_vpn()
            self.button_vpn = QPushButton(status)
            self.button_vpn.setFixedWidth(150)
            layout.addWidget(self.button_vpn)
            self.button_vpn.clicked.connect(self.enable_and_disable_vpn)

    def enable_and_disable_vpn(self):
        item = self.list_vpn.currentItem()
        if item is not None:
            filename = item.text()
            status = self.check_status_vpn()
            if status == VPN_OFF:
                subprocess.run(["sudo", "awg-quick", "up", f"{VPN_DIR}/{filename}"])
                status = self.check_status_vpn()
                self.button_vpn.setText(status)
            elif status == VPN_ON:
                subprocess.run(["sudo", "awg-quick", "down", f"{VPN_DIR}/{filename}"])
                status = self.check_status_vpn()
                self.button_vpn.setText(status)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec()
