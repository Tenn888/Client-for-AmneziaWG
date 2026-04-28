#!/bin/bash

set -e

# Установка amneziawg для Arch

# Проверка yay
if ! command -v yay &> /dev/null
then
    echo "[!] yay не найден."
    abort
fi


echo "[*] Обновление базы пакетов..."
yay -Sy

echo "[*] Установка amneziawg..."
yay -S amneziawg-dkms amneziawg-tools

echo "[+] Готово!"