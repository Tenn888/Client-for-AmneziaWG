#!/bin/bash

set -e

# Установка amneziawg для Arch

# Проверка yay
if ! command -v yay &> /dev/null
then
    echo "[!] yay не найден."
    echo "[*] Установка yay..."

    sudo pacman -S --needed base-devel git
    git clone https://aur.archlinux.org/yay-bin.git 
    cd yay-bin 
    makepkg -si
    echo "[*] yay установлен."
fi


echo "[*] Обновление базы пакетов..."
yay -Sy

echo "[*] Установка amneziawg..."
yay -S amneziawg-dkms amneziawg-tools
echo "[*] amneziawg установлен."
