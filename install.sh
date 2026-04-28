#!/bin/bash

set -e

# Установка amneziawg для Arch

# Проверка yay
if ! command -v yay &> /dev/null
then
    echo "[!] yay не найден."

    read -p "Установить yay? (y/n): " choice
    if [[ "$choice" != "y" ]]; then
        echo "Установка прервана."
        exit 1
    fi

    echo "[*] Устанавливаем зависимости..."
    sudo pacman -S --needed git base-devel

    echo "[*] Клонируем yay..."
    git clone https://aur.archlinux.org/yay.git
    cd yay

    echo "[*] Сборка yay..."
    makepkg -si

    cd ..
    rm -rf yay
fi

echo "[*] Обновление базы пакетов..."
yay -Sy

echo "[*] Установка amneziawg..."
yay -S --needed amneziawg-dkms amneziawg-tools

echo "[+] Готово!"