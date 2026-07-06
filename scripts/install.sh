#!/usr/bin/env bash

set -euo pipefail

# Скрипт установки AmneziaWG Client с поддержкой автозапуска в KDE

# Переменные
APP_DIR="/opt/amneziawg-client"
DESKTOP_FILE_SRC="./amneziawg-client.desktop"
DESKTOP_FILE_SYSTEM="/usr/share/applications/amneziawg-client.desktop"
SUDO_CMD=(sudo)


echo "Установка AmneziaWG Client..."

# Определяем пользователя (должен быть запущен через sudo)
INSTALL_USER="${SUDO_USER}"
if [ -z "$INSTALL_USER" ]; then
    echo "[!] Скрипт должен быть запущен через sudo"
    exit 1
fi

# Получаем домашнюю директорию пользователя
INSTALL_USER_HOME=$(eval echo "~$INSTALL_USER")
AUTOSTART_DIR="$INSTALL_USER_HOME/.config/autostart"

# Команды для выполнения от имени пользователя
RUN_AS_INSTALL_USER=(sudo -u "$INSTALL_USER" -H)


# Проверка yay и установка, если надо yay
if ! command -v yay &> /dev/null
then
    echo "yay не найден. Устанавливаем yay..."
    "${SUDO_CMD[@]}" pacman -S --needed --noconfirm base-devel git
    YAY_BUILD_DIR="$("${RUN_AS_INSTALL_USER[@]}" mktemp -d)"
    "${RUN_AS_INSTALL_USER[@]}" git clone https://aur.archlinux.org/yay-bin.git "$YAY_BUILD_DIR"
    pushd "$YAY_BUILD_DIR" > /dev/null
    "${RUN_AS_INSTALL_USER[@]}" makepkg -f --noconfirm
    "${SUDO_CMD[@]}" pacman -U --noconfirm ./*.pkg.tar.zst
    popd > /dev/null
    rm -rf "$YAY_BUILD_DIR"
fi

# Обновляем базу данных пакетов
"${RUN_AS_INSTALL_USER[@]}" yay -Sy --noconfirm

# Устанавливаем amneziawg и необходимые инструменты
echo "Установка необходимых пакетов amneziawg..."
"${RUN_AS_INSTALL_USER[@]}" yay -S --noconfirm amneziawg-dkms amneziawg-tools amneziawg-go unzip

echo "Настройка каталога конфигураций..."
"${SUDO_CMD[@]}" mkdir -p /etc/amnezia/amneziawg

# Создаем sudoers-файл для пользователя, чтобы он мог управлять amneziawg без пароля
echo "Настройка sudoers для пользователя $INSTALL_USER..."
SUDOERS_FILE="/etc/sudoers.d/amnezia-client"
SUDOERS_TMP="$(mktemp)"

# Определяем команды, которые пользователь сможет выполнять без пароля
cat > "$SUDOERS_TMP" <<EOF
Cmnd_Alias AMNEZIA_CLIENT = \
    /usr/bin/awg show, \
    /usr/bin/awg-quick up /etc/amnezia/amneziawg/*.conf, \
    /usr/bin/awg-quick down /etc/amnezia/amneziawg/*.conf, \
    /usr/bin/ls /etc/amnezia/amneziawg, \
    /usr/bin/cat /etc/amnezia/amneziawg/*.conf, \
    /usr/bin/cp -f * /etc/amnezia/amneziawg, \
    /usr/bin/cp -f * /etc/amnezia/amneziawg/*.conf, \
    /usr/bin/unzip -o * -d /etc/amnezia/amneziawg, \
    /usr/bin/rm -f /etc/amnezia/amneziawg/*.conf

$INSTALL_USER ALL=(root) NOPASSWD: AMNEZIA_CLIENT
EOF

# Проверяем синтаксис sudoers-файла перед установкой
if "${SUDO_CMD[@]}" visudo -c -f "$SUDOERS_TMP"; then
    "${SUDO_CMD[@]}" install -o root -g root -m 0440 "$SUDOERS_TMP" "$SUDOERS_FILE"
    echo "sudoers-файл создан для пользователя $INSTALL_USER: $SUDOERS_FILE"
else
    echo "Ошибка проверки sudoers. Файл не был создан."
    rm -f "$SUDOERS_TMP"
    exit 1
fi
rm -f "$SUDOERS_TMP"


# Создание директории приложения
echo "Создание директории $APP_DIR..."
mkdir -p "$APP_DIR"

# Копирование собранного исполняемого файла
echo "Копирование приложения..."
if [ -f "./amneziawg-client" ]; then
    cp -v "./amneziawg-client" "$APP_DIR/"
    cp -v "./AmneziaWG.png" "$APP_DIR/"
    chmod +x "$APP_DIR/amneziawg-client"
else
    echo "Ошибка: файл ./amneziawg-client не найден!"
    exit 1
fi

# Установка desktop файла для приложений
echo "Установка desktop файла..."
"${SUDO_CMD[@]}" cp -v "$DESKTOP_FILE_SRC" "$DESKTOP_FILE_SYSTEM"
"${SUDO_CMD[@]}" chmod 644 "$DESKTOP_FILE_SYSTEM"

# Обновление кэша desktop файлов
"${SUDO_CMD[@]}" update-desktop-database /usr/share/applications/

# Создание автозапуска для текущего пользователя
"${RUN_AS_INSTALL_USER[@]}" mkdir -p "$AUTOSTART_DIR"
"${RUN_AS_INSTALL_USER[@]}" sed "s|Exec=.*|Exec=$APP_DIR/amneziawg-client --minimized|" "$DESKTOP_FILE_SRC" > "$AUTOSTART_DIR/amneziawg-client.desktop"
"${RUN_AS_INSTALL_USER[@]}" chmod 644 "$AUTOSTART_DIR/amneziawg-client.desktop"

echo ""
echo "Установка завершена!"
echo ""
echo "Приложение установлено в: $APP_DIR"
echo ""
echo "Автозапуск настроен для текущего пользователя"
echo "Файл автозапуска: $AUTOSTART_DIR/amneziawg-client.desktop"
echo ""
echo "Приложение будет запускаться в трее при входе в систему"
echo "Вы можете отключить автозапуск в KDE Параметры системы -> Запуск и завершение -> Автозагрузка"
