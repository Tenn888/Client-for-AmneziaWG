from PyQt6.QtWidgets import QApplication, QMessageBox, QInputDialog, QLineEdit
from subprocess import run

def request_sudo_password(parent=None, info_widget=None):
    def authenticate_sudo(password):
        return run(
            ["sudo", "-k", "-S", "-p", "", "-v"],
            input=f"{password}\n",
            capture_output=True,
            text=True,
        )

    for attempt in range(3):
        password, ok = QInputDialog.getText(
            parent,
            "Пароль sudo",
            "Введите пароль sudo:",
            QLineEdit.EchoMode.Password,
        )
        if not ok:
            return None

        sudo_check = authenticate_sudo(password)
        if sudo_check.returncode == 0:
            return password

        if info_widget is not None:
            info_widget.setText("Неверный пароль sudo. Попробуйте еще раз.")
            QApplication.processEvents()
        elif parent is not None:
            QMessageBox.warning(parent, "Ошибка", "Неверный пароль sudo. Попробуйте еще раз.")

    if info_widget is not None:
        info_widget.setText("Ошибка авторизации sudo:\nневерный пароль.")
    elif parent is not None:
        QMessageBox.critical(parent, "Ошибка авторизации sudo", "неверный пароль.")
    return None
