<p align="center">
  <img src="https://raw.githubusercontent.com/M4RC-XX/homeassistant_battery_sensor_for_ghub/main/images/logo.png" width="100" height="100" alt="G Hub Battery Sensor Logo">
</p>

# Battery Sensor for G Hub (Unofficial)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!TIP]
> **Deutschsprachige Anleitung:** Eine deutsche Version dieser Dokumentation findest du [weiter unten](#-deutsche-anleitung).

An unofficial but powerful Home Assistant integration for Logitech devices managed by G Hub. Monitor your peripherals' battery levels, estimated remaining runtimes, and charging states directly from your smart home dashboard.

## ✨ Features

* **Auto-Discovery:** Automatically finds, names, and registers all connected wireless peripherals (Mice, Keyboards, and Headsets).
* **Precise Battery Metrics:** Live updates for battery percentages (`%`) pulled directly from the device firmware.
* **Estimated Runtime Tracking:** Dynamic sensors displaying the estimated hours remaining based on your current power consumption.
* **Charging Status:** Native binary entity mapping (`battery_charging`) to show instantly when a charging cable is attached.
* **Clean Device Architecture:** Neatly groups all individual sensors under dedicated device cards (e.g., "Logitech G915") rather than a scattered list.
* **Local Push & Low Overhead:** Uses persistent WebSockets to instantly push state changes into Home Assistant the exact second they happen – no cloud required.

---

## 🛠️ Prerequisites

Because Home Assistant runs on your local network (e.g., in a virtual machine or dedicated host) and needs to access the G Hub API running on your Windows PC, Windows must be configured to allow and route incoming traffic on Port `9010`.

Open your Windows Terminal (PowerShell or Command Prompt) and execute the following commands to configure port proxying and your local firewall:

```powershell
# Redirect incoming network requests on Port 9010 to G Hub's local interface
sudo netsh interface portproxy add v4tov4 listenport=9010 listenaddress=0.0.0.0 connectport=9010 connectaddress=127.0.0.1

# Allow incoming TCP traffic on Port 9010 through the Windows Defender Firewall
sudo netsh advfirewall firewall add rule name="Logitech G Hub WebSocket Proxy" dir=in action=allow protocol=TCP localport=9010

## 📦 Installation

### Option 1: HACS (Recommended)
1. Open **HACS** in your Home Assistant dashboard.
2. Click the three dots in the top-right corner and select **Custom repositories**.
3. Paste the repository URL: `https://github.com/M4RC-XX/homeassistant_battery_sensor_for_ghub`
4. Choose **Integration** as the category and click **Add**.
5. Find **Battery Sensor for G Hub (Unofficial)** in HACS, click **Download**, and **Restart** Home Assistant.

### Option 2: Manual Installation
1. Download the latest release archive.
2. Extract the contents and copy the `ghub_battery` directory into your Home Assistant `<config_dir>/custom_components/` path.
3. **Restart** Home Assistant.

---

## ⚙️ Configuration

1. Go to **Settings -> Devices & Services**.
2. Click **Add Integration** in the bottom-right corner.
3. Search for **Battery for G Hub (Unofficial)**.
4. Enter the static IPv4 address of your Windows PC when prompted.
5. Click Submit. 
6. *Note:* Trigger your devices (e.g., turn your headset off/on or attach a charging cable) to fire the initial API events. Your devices will instantly build out their entities inside the dashboard.

---

## 🇩🇪 Deutsche Anleitung

### Installation
Füge dieses Repository als "Benutzerdefiniertes Repository" in HACS (Kategorie: Integration) mit der URL `https://github.com/M4RC-XX/homeassistant_battery_sensor_for_ghub` hinzu, lade es herunter und starte Home Assistant zwingend neu.

### Einrichtung
Gehe auf **Einstellungen -> Geräte & Dienste** und klicke auf **Integration hinzufügen**. Suche nach **Battery for G Hub (Unofficial)**. Trage dort die IP-Adresse deines Windows-PCs ein. 
*Hinweis:* Schalte deine Peripheriegeräte nach der Einrichtung kurz aus und wieder ein (oder stecke das Ladekabel an), um den initialen Datenstrom zu triggern. Die Geräte und Entitäten erscheinen sofort automatisch.

---

## 📝 License & Disclaimer

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

**Disclaimer:** This is an unofficial, community-driven project. It is not affiliated with, endorsed by, authorized by, or in any way officially connected to Logitech International S.A. or any of its subsidiaries. "Logitech" and "G Hub" are registered trademarks of their respective owners. Everything is provided as-is, without any guarantees.