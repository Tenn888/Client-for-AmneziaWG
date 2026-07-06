#!/usr/bin/env bash

set -euo pipefail

# Скрипт удаления AmneziaWG Client

# Переменные
APP_DIR="/opt/amneziawg-client"
DESKTOP_FILE_SRC="./amneziawg-client.desktop"
DESKTOP_FILE_SYSTEM="/usr/share/applications/amneziawg-client.desktop"
SUDO_CMD=(sudo)


echo "Удаление AmneziaWG Client..."

# Определяем пользователя (должен быть запущен через sudo)
UNINSTALL_USER="${SUDO_USER}"
if [ -z "$UNINSTALL_USER" ]; then
    echo "[!] Скрипт должен быть запущен через sudo"
    exit 1
fi

# Получаем домашнюю директорию пользователя
UNINSTALL_USER_HOME=$(eval echo "~$UNINSTALL_USER")
AUTOSTART_DIR="$UNINSTALL_USER_HOME/.config/autostart"

# Команды для выполнения от имени пользователя
RUN_AS_UNINSTALL_USER=(sudo -u "$UNINSTALL_USER" -H)


# Проверка yay и установка, если надо yay
if ! command -v yay &> /dev/null
then
    echo "yay не найден. Устанавливаем yay..."
    "${SUDO_CMD[@]}" pacman -S --needed --noconfirm base-devel git
    YAY_BUILD_DIR="$("${RUN_AS_UNINSTALL_USER[@]}" mktemp -d)"
    "${RUN_AS_UNINSTALL_USER[@]}" git clone https://aur.archlinux.org/yay-bin.git "$YAY_BUILD_DIR"
    pushd "$YAY_BUILD_DIR" > /dev/null
    "${RUN_AS_UNINSTALL_USER[@]}" makepkg -f --noconfirm
    "${SUDO_CMD[@]}" pacman -U --noconfirm ./*.pkg.tar.zst
    popd > /dev/null
    rm -rf "$YAY_BUILD_DIR"
fi

# Удаление пакетов amneziawg
echo "Удаление пакетов amneziawg..."
"${RUN_AS_UNINSTALL_USER[@]}" yay -Rns amneziawg-dkms amneziawg-tools amneziawg-go

# Удаляем sudoers-файл для пользователя
echo "Удаление sudoers для пользователя $UNINSTALL_USER..."
"${SUDO_CMD[@]}" rm -rf /etc/sudoers.d/amnezia-client

# Удаление директории приложения
echo "Удаление директории приложения..."
"${SUDO_CMD[@]}" rm -rf "$APP_DIR"

# Удаление desktop файла для приложений
echo "Удаление desktop файла..."
"${SUDO_CMD[@]}" rm -f "$DESKTOP_FILE_SYSTEM"

# Обновление кэша desktop файлов
"${SUDO_CMD[@]}" update-desktop-database /usr/share/applications/

# Удаление автозапуска для текущего пользователя
"${RUN_AS_UNINSTALL_USER[@]}" rm -f "$AUTOSTART_DIR/amneziawg-client.desktop"

echo ""
echo "Удаление завершено!"