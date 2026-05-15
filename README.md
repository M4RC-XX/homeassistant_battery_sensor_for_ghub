<p align="center">
  <img src="https://raw.githubusercontent.com/M4RC-XX/homeassistant_battery_sensor_for_ghub/main/images/logo.png" width="100" height="100" alt="G Hub Battery Sensor Logo">
</p>

# Battery Sensor for G Hub (Unofficial)

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> [!TIP]
> **Deutschsprachige Anleitung:** Eine deutsche Version dieser Dokumentation findest du [weiter unten](#-deutsche-anleitung).

An unofficial but powerful Home Assistant local-push integration for Logitech devices managed by G Hub. This integration captures live peripheral data directly from your Windows PC via the G Hub background API, exposing battery levels, charge states, and runtime metrics without using heavy polling or external cloud services.

## ✨ Features

* **Auto-Discovery:** Automatically scans, names, and registers all connected wireless peripherals (Mice, Keyboards, and Headsets).
* **Precise Battery Metrics:** Tracks real-time battery percentages (`%`) directly from the device firmware state.
* **Estimated Runtime Tracking:** Extracts advanced telemetry to provide a dynamic sensor displaying estimated hours remaining based on your current power consumption.
* **Charging Binary Sensor:** Native binary entity mapping (`battery_charging`) to show instantly when a charging cable is attached.
* **Clean Device Architecture:** Neatly groups all individual diagnostic entities under clean, dedicated device cards rather than a scattered list.
* **Local Push & Low Overhead:** Uses persistent WebSockets to instantly push state changes into Home Assistant the exact second they happen.

---

## 🛠️ Prerequisites

Because Home Assistant runs on your local network (e.g., in a virtual machine or dedicated host) and needs to access the G Hub API running on your Windows PC, Windows must be configured to allow and route incoming traffic on Port `9010`.

Open your Windows Terminal (PowerShell or Command Prompt) and execute the following commands to configure port proxying and your local firewall:

```powershell
# Redirect incoming network requests on Port 9010 to G Hub's local interface
sudo netsh interface portproxy add v4tov4 listenport=9010 listenaddress=0.0.0.0 connectport=9010 connectaddress=127.0.0.1

# Allow incoming TCP traffic on Port 9010 through the Windows Defender Firewall
sudo netsh advfirewall firewall add rule name="Logitech G Hub WebSocket Proxy" dir=in action=allow protocol=TCP localport=9010