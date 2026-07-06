#!/bin/bash

set -euo pipefail

# Скрипт для управления автозапуском AmneziaWG Client в KDE

# Константы
AUTOSTART_DIR="$HOME/.config/autostart"
AUTOSTART_FILE="$AUTOSTART_DIR/amneziawg-client.desktop"
SYSTEM_DESKTOP="/usr/share/applications/amneziawg-client.desktop"
APP_PATH="/opt/amneziawg-client/amneziawg-client"

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Функции
print_error() {
    echo -e "${RED}[!] Ошибка:${NC} $1" >&2
}

print_success() {
    echo -e "${GREEN}[+] Успешно:${NC} $1"
}

print_info() {
    echo -e "${BLUE}[ℹ] Информация:${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!] Предупреждение:${NC} $1"
}

# Проверка существования системного desktop-файла
check_system_desktop() {
    if [ ! -f "$SYSTEM_DESKTOP" ]; then
        print_error "[!] desktop файл не найден в $SYSTEM_DESKTOP"
        print_info "Приложение не установлено."
        exit 1
    fi
}

# Включить автозапуск
enable_autostart() {
    print_info "Включение автозапуска AmneziaWG Client..."
    check_system_desktop
    
    if [ -f "$AUTOSTART_FILE" ]; then
        print_warning "Файл автозапуска уже существует. Обновляю..."
    fi
    
    mkdir -p "$AUTOSTART_DIR"
    sed "s|Exec=.*|Exec=$APP_PATH --minimized|" "$SYSTEM_DESKTOP" > "$AUTOSTART_FILE"
    chmod 644 "$AUTOSTART_FILE"
    
    print_success "Автозапуск включен"
    print_info "Приложение будет запускаться при входе в систему"
}

# Отключить автозапуск
disable_autostart() {
    print_info "Отключение автозапуска AmneziaWG Client..."
    
    if [ ! -f "$AUTOSTART_FILE" ]; then
        print_warning "Автозапуск уже отключен"
        return 0
    fi
    
    rm -f "$AUTOSTART_FILE"
    print_success "Автозапуск отключен"
}

# Показ главного меню
show_menu() {
    while true; do
        clear
        show_status

        echo "Действия:"
        echo "1) Включить автозапуск"
        echo "2) Отключить автозапуск"
        echo "3) Установить программу"
        echo "4) Удалить программу"
        echo "0) Выход"
        echo

        read -rp "Выберите действие: " choice

        case "$choice" in
            1)
                enable_autostart
                ;;
            2)
                disable_autostart
                ;;
            3)
                install_program
                ;;
            4)
                uninstall_program
                ;;
            0)
                exit 0
                ;;
            *)
                print_error "Неверный выбор"
                ;;
        esac

        echo
        read -rp "Нажмите Enter..."
    done
}

# Показать статус автозапуска
show_status() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}   Статус автозапуска AmneziaWG Client${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    
    if [ -f "$SYSTEM_DESKTOP" ]; then
        echo -e "Установка:     ${GREEN}Обнаружена${NC}"
    else
        echo -e "Установка:     ${RED}Не найдена${NC}"
    fi

    if [ -f "$AUTOSTART_FILE" ]; then
        echo -e "Статус:        ${GREEN}ВКЛЮЧЕН${NC}"
        echo -e "Файл:          $AUTOSTART_FILE"
        echo -e "Приложение:    $APP_PATH --minimized"
    else
        echo -e "Статус:        ${RED}ОТКЛЮЧЕН${NC}"
        echo -e "Файл:          Не создан"
        echo -e "Приложение:    Не установлено"
    fi
    
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo ""
}

# Удаление amneziawg-client
uninstall_program() {
    echo
    print_warning "Программа будет полностью удалена."

    read -rp "Продолжить? [y/N]: " ans

    case "$ans" in
        y|Y)
            sudo ./uninstall.sh
            exit 0
            ;;
        *)
            print_info "Удаление отменено."
            return
            ;;
    esac
}

# Установка amneziawg-client
install_program() {
    echo
    print_warning "Программа будет установлена."

    read -rp "Продолжить? [y/N]: " ans

    case "$ans" in
        y|Y)
            sudo ./install.sh
            exit 0
            ;;
        *)
            print_info "Установка отменена."
            return
            ;;
    esac
}

# Основная логика
if [ $# -eq 0 ]; then
    show_menu
    exit 0
fi

case "$1" in
    enable)
        enable_autostart
        ;;
    disable)
        disable_autostart
        ;;
    install)
        install_program
        ;;
    uninstall)
        uninstall_program
        ;;
    *)
        print_error "Неизвестная команда: $1"
        exit 1
        ;;
esac