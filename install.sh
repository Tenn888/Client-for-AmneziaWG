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
    if [ -d "yay" ]; then
        echo "[*] Репозиторий yay уже существует"
    else
        git clone https://aur.archlinux.org/yay.git
    fi

    cd yay

    echo "[*] Сборка yay..."
    makepkg -si

    cd ..
    rm -rf yay
fi
