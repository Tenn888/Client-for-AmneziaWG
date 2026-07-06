<p align="center">
    <a href="README.ru.md">🇷🇺 Русский</a>
</p>

# 🔐 Client for AmneziaWG

A modern graphical client for **AmneziaWG**, built with **Python** and **PyQt6** for **Arch Linux** and **KDE Plasma**.

The application provides a convenient graphical interface for managing AmneziaWG VPN configurations, supports automatic startup, and integrates with the KDE system tray.

---

## ✨ Features

- 🖥️ Modern graphical interface built with PyQt6
- 🔐 Connect and disconnect AmneziaWG VPNs
- 📂 Import VPN configurations in `.conf` and `.zip` formats
- 📋 Automatic detection of installed VPN profiles
- 🟢 KDE Plasma system tray integration
- 🚀 Automatic startup on login
- ⚡ Quick VPN switching from the system tray menu
- 🔒 Automatic `sudoers` configuration for passwordless VPN management

---

## 📋 Requirements

- Arch Linux
- KDE Plasma 6
- Python 3
- PyQt6

The installation script automatically installs the required packages:

- `yay` (if not already installed)
- `amneziawg-dkms`
- `amneziawg-tools`
- `amneziawg-go`
- `unzip`

---

# 🚀 Installation

Place the following files **in the same directory**:

```text
amneziawg-client
amneziawg-client.desktop
install.sh
uninstall.sh
service.sh
```

Make the scripts executable:

```bash
chmod +x service.sh install.sh uninstall.sh
```

Run the application manager:

```bash
./service.sh
```

From the menu, select **"Install Application"**.

During installation, the following actions are performed automatically:

- installs all required dependencies;
- installs AmneziaWG;
- creates the `/etc/amnezia/amneziawg` directory;
- configures the required `sudoers` rules;
- installs the application to `/opt/amneziawg-client`;
- installs the desktop entry;
- enables autostart for the current user.

## 🔨 Build

Install PyInstaller if necessary:

```bash
pip install pyinstaller
```

Clone the repository:

```bash
git clone https://github.com/Tenn888/Client-for-AmneziaWG.git
cd Client-for-AmneziaWG
```

Build the executable:

```bash
pyinstaller \
    --onefile \
    --windowed \
    --name amneziawg-client \
    --add-data "Images:Images" \
    --hidden-import=PyQt6 \
    main.py
```

After the build is complete, the executable will be located at:

```text
dist/amneziawg-client
```

---

# ▶️ Usage

Run normally:

```bash
/opt/amneziawg-client/amneziawg-client
```

Run minimized to the system tray:

```bash
/opt/amneziawg-client/amneziawg-client --minimized
```

---

# 🖱️ System Tray

### Left Click

- Show or hide the main window.

### Right Click

- View available VPN configurations.
- Connect or disconnect a VPN.
- Exit the application.

---

# ⚙️ Application Management

The project includes a simple application management script.

Run:

```bash
./service.sh
```

Available options:

```text
1) Enable autostart
2) Disable autostart
3) Uninstall application
0) Exit
```

---

# 🔄 Updating

Build a new version of the application and replace the executable:

```bash
sudo cp dist/amneziawg-client /opt/amneziawg-client/
```

Then restart the application.

---

# 🗑️ Uninstallation

To completely remove the application:

```bash
./service.sh
```

or

```bash
sudo ./uninstall.sh
```

The following will be removed:

- application files;
- desktop entry;
- autostart configuration;
- `sudoers` configuration.