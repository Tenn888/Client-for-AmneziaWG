from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit

import sys, os, subprocess

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

        self.list_vpn.itemClicked.connect(self.load_info_vpn)

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
                ["sudo", "cat", f"/etc/amnezia/amneziawg/{filename}"],
                capture_output=True,
                text=True
            )
            self.info_vpn.setText(d.stdout)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec()
