from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import QApplication, QMainWindow, QListWidget, QVBoxLayout, QWidget

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.setMinimumSize(QSize(800,500))

        main_field = QWidget()
        main_field.setMaximumWidth(200) 
        self.setCentralWidget(main_field)

        self.list_vpn = QListWidget()
        self.list_vpn.addItem("VPN 1")
        self.list_vpn.addItem("VPN 2")

        vbox = QVBoxLayout(main_field)
        vbox.addWidget(self.list_vpn)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    app.exec()
