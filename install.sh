#!/usr/bin/env bash

set -euo pipefail

# Установка amneziawg для Arch

SUDOERS_TMP=""
YAY_BUILD_DIR=""

# Функция для очистки временных файлов при выходе
cleanup() {
    rm -f "$SUDOERS_TMP"
    if [ -n "$YAY_BUILD_DIR" ]; then
        rm -rf "$YAY_BUILD_DIR"
    fi
}
# Устанавливаем trap для вызова функции очистки при выходе из скрипта
trap cleanup EXIT

# Определение команд для sudo и yay в зависимости от наличия переменных окружения
if [ -n "${AMNEZIA_CLIENT_SUDO_WRAPPER:-}" ]; then
    SUDO_CMD=("$AMNEZIA_CLIENT_SUDO_WRAPPER")
    YAY_CMD=(yay --sudo "$AMNEZIA_CLIENT_SUDO_WRAPPER")
elif [ -n "${AMNEZIA_CLIENT_SUDO_PREAUTH:-}" ]; then
    SUDO_CMD=(sudo -n)
    YAY_CMD=(yay --sudoflags=-n)
elif [ -n "${SUDO_ASKPASS:-}" ]; then
    SUDO_CMD=(sudo -A)
    YAY_CMD=(yay --sudoflags=-A)
else
    SUDO_CMD=(sudo)
    YAY_CMD=(yay)
fi

# Проверка yay и установка,если надо yay
if ! command  -v yay &> /dev/null
then
    "${SUDO_CMD[@]}" pacman -S --needed --noconfirm base-devel git
    YAY_BUILD_DIR="$(mktemp -d)"
    git clone https://aur.archlinux.org/yay-bin.git "$YAY_BUILD_DIR"
    cd "$YAY_BUILD_DIR"
    makepkg -f --noconfirm
    "${SUDO_CMD[@]}" pacman -U --noconfirm ./*.pkg.tar.zst
fi

# Обновляем базу данных пакетов
"${YAY_CMD[@]}" -Sy --noconfirm

# Устанавливаем amneziawg и необходимые инструменты
"${YAY_CMD[@]}" -S --noconfirm amneziawg-dkms amneziawg-tools amneziawg-go unzip

echo "[*] Настройка каталога конфигураций..."
"${SUDO_CMD[@]}" mkdir -p /etc/amnezia/amneziawg

# Определяем основного пользователя для настройки sudoers
INSTALL_USER="${SUDO_USER:-${USER:-}}"
if [ -z "$INSTALL_USER" ] || [ "$INSTALL_USER" = "root" ]; then
    INSTALL_USER="$(logname 2>/dev/null || true)"
fi

# Если после всех попыток не удалось определить пользователя, выводим ошибку
if [ -z "$INSTALL_USER" ] || [ "$INSTALL_USER" = "root" ]; then
    echo "[!] Не удалось определить основного пользователя для sudoers."
    echo "[!] Запустите скрипт из-под обычного пользователя или через sudo."
    exit 1
fi

# Создаем sudoers-файл для пользователя, чтобы он мог управлять amneziawg без пароля
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
    echo "[*] sudoers-файл создан для пользователя $INSTALL_USER: $SUDOERS_FILE"
else
    echo "[!] Ошибка проверки sudoers. Файл не был создан."
    exit 1
fi
